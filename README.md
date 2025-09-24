# 🌊 AgentFlow

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.1.0-orange.svg)](https://github.com/agentflow/agentflow)
[![Tests](https://img.shields.io/badge/Tests-Passing-green.svg)](https://github.com/agentflow/agentflow)

**Open-source AI Agent orchestration framework for building intelligent multi-agent systems.**

AgentFlow provides a powerful, flexible foundation for creating complex AI workflows with multiple specialized agents working together seamlessly. Built with modern Python async/await, comprehensive plugin architecture, and developer-first experience.

## ✨ Features

### 🎯 Core Framework
- **🤖 Multi-Agent Orchestration** - Coordinate multiple AI agents with intelligent task distribution
- **🔌 Plugin Architecture** - Extensible plugin system for custom integrations and capabilities
- **⚡ Async-First Design** - Built for high-performance concurrent processing
- **🎛️ Event-Driven Communication** - Real-time agent collaboration through event bus
- **📋 Advanced Task Management** - Task scheduling with dependencies, priorities, and lifecycle management
- **🔒 Type-Safe** - Full type hints and runtime validation with Pydantic

### 🛠️ Built-in Capabilities
- **🖥️ CLI Tools** - Comprehensive command-line interface for development and deployment
- **📊 Monitoring & Health Checks** - Built-in metrics, logging, and system health monitoring
- **🔧 Configuration Management** - Flexible configuration with JSON/YAML support
- **🌐 Web API Support** - RESTful API integration with FastAPI
- **📦 Plugin Discovery** - Automatic plugin discovery and hot-loading
- **🧪 Testing Framework** - Built-in testing utilities for agent development

### 🚀 Ready-to-Use Templates
- **Basic Agent** - Simple agent template for getting started
- **Web API Agent** - HTTP API integration with FastAPI
- **Chatbot Agent** - Conversational AI with multiple interfaces
- **Data Processing Agent** - Data analysis and transformation workflows
- **Multi-Agent System** - Complex coordination between multiple agents

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (coming soon)
pip install agentflow

# Or install from source
git clone https://github.com/agentflow/agentflow.git
cd agentflow
pip install -e .
```

### Verify Installation

```bash
# Check version and status
agentflow --version
agentflow status
```

### Create Your First Agent

```bash
# Create a new project with basic template
agentflow create my-first-agent --template basic

# Navigate and run
cd my-first-agent
python main.py
```

### Using Templates

```bash
# Available templates
agentflow create my-web-agent --template web      # Web API agent
agentflow create my-chatbot --template chatbot    # Conversational agent  
agentflow create my-data-agent --template data    # Data processing agent
agentflow create my-api --template api            # REST API agent

# Initialize in existing directory
agentflow init --template basic
```

## 📝 Basic Usage

### Simple Agent Example

```python
#!/usr/bin/env python3
import asyncio
from agentflow.plugins.manager import plugin_manager
from agentflow.plugins.base import BasePlugin, PluginMetadata

class MyCustomPlugin(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my_plugin",
            version="1.0.0",
            description="My custom agent plugin",
            author="Your Name"
        )
    
    async def initialize(self) -> None:
        print("🚀 Plugin initialized!")
    
    async def cleanup(self) -> None:
        print("🧹 Plugin cleaned up!")
    
    async def process_task(self, task_data: dict) -> dict:
        return {"result": f"Processed: {task_data}"}

async def main():
    # Register and initialize plugins
    from agentflow.plugins.registry import plugin_registry
    plugin_registry.register_plugin_class(MyCustomPlugin)
    plugin_manager.registry.create_plugin_instance("my_plugin")
    
    await plugin_manager.initialize_all_plugins()
    
    try:
        print("🌊 Agent is running...")
        # Your agent logic here
        
    finally:
        await plugin_manager.cleanup_all_plugins()

if __name__ == '__main__':
    asyncio.run(main())
```

### Web API Agent Example

```python
from fastapi import FastAPI
from agentflow.plugins.manager import plugin_manager

app = FastAPI(title="My AgentFlow API")

@app.get("/")
async def root():
    return {"message": "AgentFlow Agent is running!"}

@app.get("/health")
async def health():
    health_status = await plugin_manager.health_check()
    return {"status": "healthy", "plugins": health_status}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 🔧 CLI Reference

### Project Management

```bash
# Create new projects
agentflow create <name> --template <template>     # Create new project
agentflow init --template <template>              # Initialize current directory

# Available templates: basic, web, api, chatbot, data
```

### Plugin Management

```bash
# Plugin operations
agentflow plugins list                            # List installed plugins
agentflow plugins list --available               # Show available plugins
agentflow plugins install <plugin-name>          # Install a plugin
agentflow plugins remove <plugin-name>           # Remove a plugin
agentflow plugins info <plugin-name>             # Show plugin details
```

### Development Tools

```bash
# Development and monitoring
agentflow status                                  # Show system status
agentflow dev serve --port 8000                  # Start development server
agentflow dev serve --host 0.0.0.0 --port 8080  # Custom host/port
```

### Help and Information

```bash
agentflow --help                                  # Show main help
agentflow <command> --help                       # Show command-specific help
agentflow --version                               # Show version information
```

## 🏗️ Architecture Overview

```
AgentFlow Framework
├── 🎯 Core System
│   ├── Plugin Manager         # Plugin lifecycle and orchestration
│   ├── Plugin Registry        # Plugin registration and discovery  
│   ├── Event System          # Inter-plugin communication
│   └── Configuration         # Settings and environment management
│
├── 🔌 Plugin Types
│   ├── BasePlugin            # Foundation for all plugins
│   ├── AgentPlugin           # Agent-specific functionality
│   ├── TaskPlugin            # Task processing plugins
│   ├── IntegrationPlugin     # External service integrations
│   ├── DataPlugin            # Data processing capabilities
│   └── MonitoringPlugin      # Observability and metrics
│
├── 🛠️ Developer Tools
│   ├── CLI Interface         # Command-line tools
│   ├── Project Templates     # Quick-start templates
│   ├── Development Server    # Local development environment
│   └── Testing Utilities     # Plugin and agent testing
│
└── 📦 Examples & Templates
    ├── Basic Agent           # Simple agent implementation
    ├── Web API Agent         # HTTP API integration
    ├── Chatbot Agent         # Conversational interfaces
    ├── Data Processing       # Data analysis workflows
    └── Multi-Agent Systems   # Complex agent coordination
```

## 🔌 Plugin Development

### Creating a Custom Plugin

```python
from agentflow.plugins.base import BasePlugin, PluginMetadata

class MyPlugin(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my_plugin",
            version="1.0.0",
            description="Description of what this plugin does",
            author="Your Name",
            homepage="https://github.com/yourusername/my-plugin",
            tags=["category", "feature"],
            dependencies=["other_plugin"],  # Optional dependencies
        )
    
    async def initialize(self) -> None:
        """Plugin initialization code"""
        pass
    
    async def cleanup(self) -> None:
        """Plugin cleanup code"""
        pass
    
    # Implement your plugin-specific methods here
```

### Plugin Lifecycle Hooks

```python
# Available lifecycle hooks
async def pre_task_execution(self, context: PluginContext) -> dict:
    """Called before task execution"""
    
async def post_task_execution(self, context: PluginContext, result: Any) -> Any:
    """Called after task execution"""
    
async def on_agent_created(self, agent_id: str, agent_type: str) -> None:
    """Called when an agent is created"""
    
async def on_task_started(self, context: PluginContext) -> None:
    """Called when a task starts"""
    
async def health_check(self) -> bool:
    """Health check for monitoring"""
    return True
```

## 📚 Examples & Use Cases

### 🤖 Chatbot Agent
Perfect for customer service, personal assistants, or interactive applications.

```bash
agentflow create my-chatbot --template chatbot
cd my-chatbot
python main.py
# Interactive chat interface starts
```

### 🌐 Web API Service
Build scalable API services with built-in monitoring and plugin support.

```bash
agentflow create my-api --template api
cd my-api
pip install -r requirements.txt
python main.py
# API server starts on http://localhost:8000
```

### 📊 Data Processing Pipeline
Analyze and transform data with specialized processing agents.

```bash
agentflow create data-pipeline --template data
cd data-pipeline
python main.py
# Data processing workflow starts
```

### 🏢 Enterprise Integration
Build complex multi-agent systems for enterprise workflows.

```bash
agentflow create enterprise-system --template basic
# Then customize with multiple plugins and agents
```

## 🧪 Development & Testing

### Development Setup

```bash
# Clone repository
git clone https://github.com/agentflow/agentflow.git
cd agentflow

# Install in development mode
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agentflow --cov-report=html

# Run specific test categories
pytest -m unit                    # Unit tests only
pytest -m integration            # Integration tests only
```

### Code Quality

```bash
# Format code
black .
isort .

# Type checking
mypy src/

# Linting
flake8
```

## 📊 Configuration

### Project Configuration (`agentflow.json`)

```json
{
  "name": "my-agent",
  "version": "1.0.0",
  "description": "My AgentFlow project",
  "plugins": [
    "web_processing",
    "data_analysis"
  ],
  "config": {
    "max_concurrent_tasks": 5,
    "task_timeout": 30,
    "logging": {
      "level": "INFO"
    }
  }
}
```

### Environment Variables

```bash
# Optional environment configuration
AGENTFLOW_LOG_LEVEL=INFO
AGENTFLOW_PLUGIN_PATH=/path/to/custom/plugins
AGENTFLOW_CONFIG_PATH=/path/to/config
```

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

### Production Considerations

- Use environment variables for sensitive configuration
- Implement proper logging and monitoring
- Set up health checks for plugin dependencies
- Consider using async-compatible databases
- Monitor plugin performance and memory usage

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run the test suite**: `pytest`
5. **Submit a pull request**

### Contribution Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all new code
- Include tests for new functionality
- Update documentation as needed
- Add examples for new features

## 📖 Documentation

- [📘 User Guide](https://agentflow.readthedocs.io/guide/) - Comprehensive usage guide
- [📗 API Reference](https://agentflow.readthedocs.io/api/) - Complete API documentation
- [📙 Plugin Development](https://agentflow.readthedocs.io/plugins/) - Plugin creation guide
- [📕 Examples Gallery](https://agentflow.readthedocs.io/examples/) - Real-world examples

## 💬 Community & Support

- **📢 GitHub Discussions** - Ask questions and share ideas
- **🐛 GitHub Issues** - Report bugs and request features
- **📧 Email** - contact@agentflow.dev
- **📖 Documentation** - Comprehensive guides and API reference

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the growing AI agent ecosystem
- Built with modern Python async/await patterns
- Thanks to all contributors and early adopters
- Special recognition to the open-source community

---

⭐ **Star this repository if AgentFlow helps you build amazing AI applications!** ⭐

**Ready to build your first AI agent? Start with `agentflow create my-agent --template basic`** 🚀