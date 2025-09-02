#!/usr/bin/env python3
"""
启动所有LifeTrace服务
不依赖lifetrace命令行工具
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path
import json
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.config import config


class ServiceManager:
    def __init__(self):
        self.processes = {}
        self.running = True
        
        # 从配置文件读取心跳参数
        self.heartbeat_dir = config.heartbeat_log_dir
        self.heartbeat_timeout = config.heartbeat_timeout
        self.heartbeat_check_interval = config.heartbeat_check_interval
        self.max_restart_attempts = config.heartbeat_max_restart_attempts
        self.restart_delay = config.heartbeat_restart_delay
        
        self.last_heartbeat_check = {}
        self.restart_count = {}  # 记录每个服务的重启次数
    
    def start_service(self, name, module):
        """启动单个服务"""
        try:
            print(f"🚀 启动 {name} 服务...")
            
            cmd = [sys.executable, '-m', module]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[name] = process
            self.restart_count[name] = 0  # 重置重启计数
            print(f"✅ {name} 服务已启动 (PID: {process.pid})")
            
            return True
            
        except Exception as e:
            print(f"❌ 启动 {name} 服务失败: {e}")
            return False
    
    def stop_all_services(self):
        """停止所有服务"""
        print(f"\n🛑 正在停止所有服务...")
        
        for name, process in self.processes.items():
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    print(f"✅ {name} 服务已停止")
                except subprocess.TimeoutExpired:
                    process.kill()
                    print(f"⚡ 强制停止 {name} 服务")
                except Exception as e:
                    print(f"❌ 停止 {name} 服务失败: {e}")
    
    def check_services(self):
        """检查服务状态"""
        running_services = []
        
        for name, process in self.processes.items():
            if process and process.poll() is None:
                running_services.append(f"{name} (PID: {process.pid})")
            else:
                print(f"❌ {name} 服务已停止")
        
        if running_services:
            print(f"✅ 运行中的服务: {', '.join(running_services)}")
        
        return len(running_services)
    
    def show_service_output(self):
        """显示服务输出"""
        for name, process in self.processes.items():
            if process and process.poll() is None:
                try:
                    # 非阻塞读取输出
                    stdout_data = process.stdout.read()
                    stderr_data = process.stderr.read()
                    
                    if stdout_data:
                        print(f"[{name} STDOUT] {stdout_data}")
                    if stderr_data:
                        print(f"[{name} STDERR] {stderr_data}")
                        
                except Exception:
                    pass
    
    def get_service_heartbeat(self, service_name):
        """获取服务的最新心跳信息"""
        # 根据服务名映射到心跳文件名
        heartbeat_mapping = {
            "录制器": "recorder",
            "处理器": "processor", 
            "OCR服务": "ocr",
            "Web服务": "server"
        }
        
        heartbeat_file_name = heartbeat_mapping.get(service_name, service_name.lower())
        heartbeat_file = os.path.join(self.heartbeat_dir, f"{heartbeat_file_name}_heartbeat.log")
        
        if not os.path.exists(heartbeat_file):
            return None
            
        try:
            with open(heartbeat_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    # 读取最后一行心跳记录
                    last_line = lines[-1].strip()
                    if last_line:
                        return json.loads(last_line)
        except Exception as e:
            print(f"❌ 读取 {service_name} 心跳文件失败: {e}")
            
        return None
    
    def check_service_heartbeat(self, service_name):
        """检查服务心跳是否正常"""
        heartbeat = self.get_service_heartbeat(service_name)
        
        if not heartbeat:
            return False
            
        try:
            heartbeat_time = datetime.fromisoformat(heartbeat['timestamp'])
            current_time = datetime.now()
            time_diff = (current_time - heartbeat_time).total_seconds()
            
            # 如果心跳超时，认为服务异常
            if time_diff > self.heartbeat_timeout:
                print(f"⚠️  {service_name} 心跳超时 ({time_diff:.1f}秒)")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ 解析 {service_name} 心跳时间失败: {e}")
            return False
    
    def restart_service(self, name, module):
        """重启单个服务"""
        print(f"🔄 正在重启 {name} 服务...")
        
        # 检查重启次数
        if self.restart_count.get(name, 0) >= self.max_restart_attempts:
            print(f"❌ {name} 服务重启次数已达上限 ({self.max_restart_attempts})，停止重启")
            return False
        
        # 停止现有进程
        if name in self.processes:
            process = self.processes[name]
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except Exception as e:
                    print(f"❌ 停止 {name} 服务失败: {e}")
        
        # 等待一段时间后重启
        time.sleep(2)
        
        # 重新启动服务
        success = self.start_service(name, module)
        if success:
            self.restart_count[name] = self.restart_count.get(name, 0) + 1
            print(f"✅ {name} 服务重启成功 (第{self.restart_count[name]}次重启)")
        else:
            print(f"❌ {name} 服务重启失败")
            
        return success


def check_dependencies():
    """检查依赖"""
    print("🔍 检查依赖...")
    
    missing_deps = []
    
    try:
        import mss
        print("✅ mss (截图)")
    except ImportError:
        missing_deps.append("mss")
    
    try:
        import fastapi
        print("✅ fastapi (Web服务)")
    except ImportError:
        missing_deps.append("fastapi")
    
    try:
        import rapidocr_onnxruntime
        print("✅ rapidocr-onnxruntime (OCR)")
    except ImportError:
        missing_deps.append("rapidocr-onnxruntime")
    
    try:
        import sqlalchemy
        print("✅ sqlalchemy (数据库)")
    except ImportError:
        missing_deps.append("sqlalchemy")
    
    if missing_deps:
        print(f"❌ 缺少依赖: {', '.join(missing_deps)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True


def check_database():
    """检查数据库"""
    print(f"\n🗄️ 检查数据库...")
    
    db_path = config.database_path
    if os.path.exists(db_path):
        print(f"✅ 数据库存在: {db_path}")
        return True
    else:
        print(f"❌ 数据库不存在: {db_path}")
        print("请先运行: python manual_reset.py")
        return False


def main():
    """主函数"""
    print("🚀 LifeTrace 服务启动器")
    print("=" * 40)
    
    # 检查依赖和数据库
    if not check_dependencies():
        return
    
    if not check_database():
        return
    
    # 创建服务管理器
    manager = ServiceManager()
    
    # 设置信号处理
    def signal_handler(signum, frame):
        print(f"\n⚠️  收到停止信号 ({signum})")
        manager.running = False
        manager.stop_all_services()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动服务
    services = [
        ("录制器", "lifetrace_backend.recorder"),
        ("处理器", "lifetrace_backend.processor"),
        ("OCR服务", "lifetrace_backend.simple_ocr"),
        ("Web服务", "lifetrace_backend.server")
    ]
    
    success_count = 0
    for name, module in services:
        if manager.start_service(name, module):
            success_count += 1
            time.sleep(2)  # 给服务启动时间
    
    if success_count == 0:
        print("❌ 没有服务启动成功")
        return
    
    print(f"\n✅ 成功启动 {success_count}/{len(services)} 个服务")
    
    print(f"\n📱 Web界面: http://localhost:8840")
    print(f"💡 按 Ctrl+C 停止所有服务")
    
    # 监控服务
    try:
        heartbeat_check_interval = manager.heartbeat_check_interval  # 从配置读取心跳检查间隔
        last_heartbeat_check = 0
        
        while manager.running:
            time.sleep(10)
            current_time = time.time()
            
            # 检查进程状态
            running_count = manager.check_services()
            
            # 定期检查心跳并自动重启异常服务
            if current_time - last_heartbeat_check >= heartbeat_check_interval:
                print("\n🔍 检查服务心跳状态...")
                
                for name, module in services:
                    if name in manager.processes:
                        process = manager.processes[name]
                        
                        # 如果进程还在运行，检查心跳
                        if process and process.poll() is None:
                            if not manager.check_service_heartbeat(name):
                                print(f"💔 {name} 心跳异常，尝试重启...")
                                manager.restart_service(name, module)
                        # 如果进程已停止，尝试重启
                        elif manager.restart_count.get(name, 0) < manager.max_restart_attempts:
                            print(f"💀 {name} 进程已停止，尝试重启...")
                            manager.restart_service(name, module)
                
                last_heartbeat_check = current_time
                print("✅ 心跳检查完成\n")
            
            if running_count == 0:
                print("❌ 所有服务都已停止")
                break
                
    except KeyboardInterrupt:
        print(f"\n⚠️  用户中断")
    finally:
        manager.stop_all_services()
        print(f"\n👋 所有服务已停止")


if __name__ == '__main__':
    main()