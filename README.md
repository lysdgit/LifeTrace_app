![LifeTrace Logo](assets/rhn8yu8l.png)

![GitHub stars](https://img.shields.io/github/stars/lifetrace/lifetrace?style=social) ![GitHub forks](https://img.shields.io/github/forks/lifetrace/lifetrace?style=social) ![GitHub issues](https://img.shields.io/github/issues/lifetrace/lifetrace) ![GitHub license](https://img.shields.io/github/license/lifetrace/lifetrace) ![Python version](https://img.shields.io/badge/python-3.8+-blue.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)

[📖 Documentation](doc/README.md) • [🚀 Quick Start](#quick-start) • [💡 Features](#core-features) • [🔧 API Reference](#web-api-service) • [🤝 Contributing](#contributing)

# LifeTrace - Intelligent Life Recording System

## Project Overview

LifeTrace is an AI-powered intelligent life recording system that helps users record and retrieve daily activities through automatic screenshot capture, OCR text recognition, and multimodal search technologies. The system supports traditional keyword search, semantic search, and multimodal search, providing powerful life trajectory tracking capabilities.

## Core Features

- **Automatic Screenshot Recording**: Timed automatic screen capture to record user activities
- **Intelligent OCR Recognition**: Uses RapidOCR to extract text content from screenshots
- **Multimodal Search**: Supports text, image, and semantic search
- **Vector Database**: Efficient vector storage and retrieval based on ChromaDB
- **Web API Service**: Provides complete RESTful API interfaces
- **Frontend Integration**: Supports integration with various frontend frameworks


## Deployment and Configuration

### Environment Requirements
- Python 3.8+
- Supported OS: Windows, macOS, Linux
- Optional: CUDA support (for GPU acceleration)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Configuration File
Main configuration file: `config/default_config.yaml`

```yaml
server:
  host: 127.0.0.1
  port: 8840
  debug: false

vector_db:
  enabled: true
  collection_name: "lifetrace_ocr"
  embedding_model: "shibing624/text2vec-base-chinese"
  rerank_model: "BAAI/bge-reranker-base"
  persist_directory: "vector_db"

multimodal:
  enabled: true
  text_weight: 0.6
  image_weight: 0.4
```

### Starting Services

#### Start All Services
```bash
python start_all_services.py
```

#### Start Web Service Only
```bash
python -m lifetrace_backend.server --port 8840
```

#### Start Individual Services
```bash
# Start recorder
python -m lifetrace_backend.recorder

# Start processor
python -m lifetrace_backend.processor

# Start OCR service
python -m lifetrace_backend.simple_ocr
```

## API Documentation

After starting the service, access API documentation at:
- Swagger UI: http://localhost:8840/docs
- ReDoc: http://localhost:8840/redoc

## Development Guide

### Project Structure
```
LifeTrace/
├── lifetrace_backend/      # Core modules
│   ├── server.py           # Web API service
│   ├── models.py           # Data models
│   ├── config.py           # Configuration management
│   ├── storage.py          # Storage management
│   ├── simple_ocr.py       # OCR processing
│   ├── vector_service.py   # Vector service
│   ├── multimodal_*.py     # Multimodal services
│   ├── processor.py        # File processing
│   ├── recorder.py         # Screen recording
│   └── utils.py            # Utility functions
├── config/                 # Configuration files
├── doc/                    # Documentation
├── data/                   # Data directory
├── logs/                   # Log directory
└── requirements.txt        # Dependencies
```



## Contributing

The LifeTrace community is possible thanks to thousands of kind volunteers like you. We welcome all contributions to the community and are excited to welcome you aboard.

> Please follow these steps to contribute.

**Recent Contributions:**

![GitHub contributors](https://img.shields.io/github/contributors/tangyuanbo1/LifeTrace_app) ![GitHub commit activity](https://img.shields.io/github/commit-activity/m/tangyuanbo1/LifeTrace_app) ![GitHub last commit](https://img.shields.io/github/last-commit/tangyuanbo1/LifeTrace_app)

**How to contribute:**

1. **🍴 Fork the project** - Create your own copy of the repository
2. **🌿 Create a feature branch** - `git checkout -b feature/amazing-feature`
3. **💾 Commit your changes** - `git commit -m 'Add some amazing feature'`
4. **📤 Push to the branch** - `git push origin feature/amazing-feature`
5. **🔄 Create a Pull Request** - Submit your changes for review

**Areas where you can contribute:**

- 🐛 **Bug Reports** - Help us identify and fix issues
- 💡 **Feature Requests** - Suggest new functionality
- 📝 **Documentation** - Improve guides and tutorials
- 🧪 **Testing** - Write tests and improve coverage
- 🎨 **UI/UX** - Enhance the user interface
- 🔧 **Code** - Implement new features and improvements

**Getting Started:**

- Check out our [Contributing Guidelines](CONTRIBUTING.md)
- Look for issues labeled `good first issue` or `help wanted`
- Join our community discussions in Issues and Pull Requests

We appreciate all contributions, no matter how small! 🙏



## Documentation

For detailed documentation, please refer to the `doc/` directory:
- [OCR Optimization Guide](doc/OCR_优化说明.md)
- [RapidOCR Integration Guide](doc/RapidOCR集成说明.md)
- [Multimodal Search Guide](doc/multimodal_search_guide.md)
- [Vector Database Usage Guide](doc/vector_db_usage.md)
- [Frontend Integration Guide](doc/前端集成说明.md)
- [Documentation Center](doc/README.md)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=tangyuanbo1/LifeTrace_app&type=Timeline)](https://www.star-history.com/#tangyuanbo1/LifeTrace_app&Timeline)


## License

Copyright © 2024 LifeTrace.org

The content of this repository is bound by the following licenses:

• The computer software is licensed under the [MIT](LICENSE) license.
• The learning resources in the `/doc` directory including their subdirectories thereon are copyright © 2024 LifeTrace.org
