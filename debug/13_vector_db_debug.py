#!/usr/bin/env python3
"""
向量数据库独立调试脚�?用于单独测试和调试语义搜索功�?"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.config import config
from lifetrace_backend.storage import db_manager
from lifetrace_backend.vector_service import create_vector_service


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('debug_vector_db.log', encoding='utf-8')
        ]
    )


def check_dependencies():
    """检查依赖是否安�?""
    print("🔍 检查依�?..")
    
    missing_deps = []
    
    try:
        import sentence_transformers
        print("�?sentence-transformers 已安�?)
    except ImportError:
        missing_deps.append("sentence-transformers")
    
    try:
        import chromadb
        print("�?chromadb 已安�?)
    except ImportError:
        missing_deps.append("chromadb")
    
    try:
        import numpy
        print("�?numpy 已安�?)
    except ImportError:
        missing_deps.append("numpy")
    
    if missing_deps:
        print(f"�?缺少依赖: {', '.join(missing_deps)}")
        print("请运�? pip install -r requirements_vector.txt")
        return False
    
    print("�?所有依赖已安装")
    return True


def test_vector_service():
    """测试向量服务"""
    print("\n🚀 初始化向量服�?..")
    
    # 检查配�?    print(f"向量数据库是否启�? {config.vector_db_enabled}")
    print(f"嵌入模型: {config.vector_db_embedding_model}")
    print(f"重排序模�? {config.vector_db_rerank_model}")
    print(f"向量数据库路�? {config.vector_db_persist_directory}")
    
    # 创建向量服务
    vector_service = create_vector_service(config, db_manager)
    
    if not vector_service.is_enabled():
        print("�?向量服务不可�?)
        return None
    
    print("�?向量服务初始化成�?)
    return vector_service


def test_basic_operations(vector_service):
    """测试基本操作"""
    print("\n🔧 测试基本操作...")
    
    # 测试添加文档
    test_documents = [
        {
            "id": "test_1",
            "text": "今天天气很好，适合出门散步",
            "metadata": {"type": "test", "category": "weather"}
        },
        {
            "id": "test_2", 
            "text": "我正在学习Python编程",
            "metadata": {"type": "test", "category": "programming"}
        },
        {
            "id": "test_3",
            "text": "明天要去超市买菜",
            "metadata": {"type": "test", "category": "shopping"}
        }
    ]
    
    # 添加测试文档
    for doc in test_documents:
        success = vector_service.vector_db.add_document(
            doc_id=doc["id"],
            text=doc["text"],
            metadata=doc["metadata"]
        )
        if success:
            print(f"�?添加文档: {doc['id']}")
        else:
            print(f"�?添加文档失败: {doc['id']}")
    
    # 测试搜索
    test_queries = [
        "天气如何",
        "编程学习",
        "购物清单",
        "出去�?
    ]
    
    print("\n🔍 测试语义搜索...")
    for query in test_queries:
        print(f"\n查询: '{query}'")
        
        # 普通搜�?        results = vector_service.vector_db.search(query, top_k=3)
        print(f"普通搜索结果数: {len(results)}")
        for i, result in enumerate(results):
            print(f"  {i+1}. {result['document'][:50]}... (距离: {result.get('distance', 'N/A')})")
        
        # 重排序搜�?        rerank_results = vector_service.vector_db.search_and_rerank(
            query, retrieve_k=3, rerank_k=2
        )
        print(f"重排序搜索结果数: {len(rerank_results)}")
        for i, result in enumerate(rerank_results):
            print(f"  {i+1}. {result['document'][:50]}... (重排序分�? {result.get('rerank_score', 'N/A')})")


def test_database_sync(vector_service):
    """测试数据库同�?""
    print("\n🔄 测试数据库同�?..")
    
    # 获取统计信息
    stats = vector_service.get_stats()
    print(f"同步前向量数据库文档�? {stats.get('document_count', 0)}")
    
    # 执行同步
    synced_count = vector_service.sync_from_database(limit=10)
    print(f"同步�?{synced_count} 条记�?)
    
    # 再次获取统计信息
    stats = vector_service.get_stats()
    print(f"同步后向量数据库文档�? {stats.get('document_count', 0)}")


def test_semantic_search(vector_service):
    """测试语义搜索功能"""
    print("\n🎯 测试语义搜索功能...")
    
    # 确保有数�?    stats = vector_service.get_stats()
    doc_count = stats.get('document_count', 0)
    
    if doc_count == 0:
        print("⚠️  向量数据库中没有数据，先执行同步...")
        vector_service.sync_from_database(limit=50)
        stats = vector_service.get_stats()
        doc_count = stats.get('document_count', 0)
    
    print(f"向量数据库中�?{doc_count} 条记�?)
    
    if doc_count == 0:
        print("�?没有数据可供搜索")
        return
    
    # 测试不同的搜索查�?    test_queries = [
        "代码",
        "文件",
        "浏览�?,
        "编程",
        "设置",
        "下载",
        "音乐",
        "视频"
    ]
    
    for query in test_queries:
        print(f"\n🔍 搜索: '{query}'")
        
        # 使用向量服务的语义搜�?        results = vector_service.semantic_search(
            query=query,
            top_k=5,
            use_rerank=True
        )
        
        print(f"找到 {len(results)} 个结�?")
        for i, result in enumerate(results[:3]):  # 只显示前3�?            text = result.get('text', '')[:100]
            score = result.get('rerank_score', result.get('score', 0))
            metadata = result.get('metadata', {})
            app_name = metadata.get('application', 'Unknown')
            
            print(f"  {i+1}. [{app_name}] {text}... (分数: {score:.3f})")


def interactive_search(vector_service):
    """交互式搜�?""
    print("\n💬 进入交互式搜索模�?(输入 'quit' 退�?")
    
    while True:
        try:
            query = input("\n请输入搜索查�? ").strip()
            if query.lower() in ['quit', 'exit', '退�?]:
                break
            
            if not query:
                continue
            
            # 执行搜索
            results = vector_service.semantic_search(
                query=query,
                top_k=10,
                use_rerank=True
            )
            
            if not results:
                print("�?没有找到相关结果")
                continue
            
            print(f"\n找到 {len(results)} 个相关结�?")
            for i, result in enumerate(results):
                text = result.get('text', '')
                score = result.get('rerank_score', result.get('score', 0))
                metadata = result.get('metadata', {})
                
                app_name = metadata.get('application', 'Unknown')
                timestamp = metadata.get('screenshot_timestamp', 'Unknown')
                
                print(f"\n{i+1}. [{app_name}] 分数: {score:.3f}")
                print(f"   时间: {timestamp}")
                print(f"   内容: {text[:200]}...")
                
                if i >= 4:  # 只显示前5个详细结�?                    remaining = len(results) - 5
                    if remaining > 0:
                        print(f"   ... 还有 {remaining} 个结�?)
                    break
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"搜索出错: {e}")
    
    print("退出交互式搜索")


def main():
    """主函�?""
    print("🚀 LifeTrace 向量数据库调试工�?)
    print("=" * 50)
    
    # 设置日志
    setup_logging()
    
    # 检查依�?    if not check_dependencies():
        return
    
    # 检查数据库是否初始�?    if not os.path.exists(config.database_path):
        print("�?LifeTrace 数据库未初始化，请先运行: lifetrace init")
        return
    
    # 测试向量服务
    vector_service = test_vector_service()
    if not vector_service:
        return
    
    # 显示统计信息
    stats = vector_service.get_stats()
    print(f"\n📊 向量数据库统�?")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 选择操作
    while True:
        print("\n" + "=" * 50)
        print("请选择操作:")
        print("1. 测试基本操作 (添加测试文档和搜�?")
        print("2. 同步数据�?(从SQLite同步OCR结果)")
        print("3. 测试语义搜索")
        print("4. 交互式搜�?)
        print("5. 重置向量数据�?)
        print("6. 查看统计信息")
        print("0. 退�?)
        
        try:
            choice = input("\n请输入选择 (0-6): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                test_basic_operations(vector_service)
            elif choice == '2':
                test_database_sync(vector_service)
            elif choice == '3':
                test_semantic_search(vector_service)
            elif choice == '4':
                interactive_search(vector_service)
            elif choice == '5':
                confirm = input("⚠️  确定要重置向量数据库�? (y/N): ").strip().lower()
                if confirm == 'y':
                    if vector_service.reset():
                        print("�?向量数据库已重置")
                    else:
                        print("�?重置失败")
            elif choice == '6':
                stats = vector_service.get_stats()
                print(f"\n📊 向量数据库统�?")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
            else:
                print("�?无效选择")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"操作出错: {e}")
    
    print("\n👋 调试结束")


if __name__ == '__main__':
    main()
