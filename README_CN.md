# 🌊 AgentFlow

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.1.0-orange.svg)](https://github.com/grass2036/agentflow)
[![Tests](https://img.shields.io/badge/Tests-Passing-green.svg)](https://github.com/grass2036/agentflow)

**开源AI智能体编排框架，用于构建智能多智能体系统。**

AgentFlow 提供了强大而灵活的基础架构，用于创建复杂的AI工作流程，让多个专业智能体无缝协作。采用现代 Python async/await 架构，具备全面的插件系统和开发者友好的体验。

## ✨ 核心特性

### 🎯 框架核心
- **🤖 多智能体编排** - 智能任务分配，协调多个AI智能体
- **🔌 插件架构** - 可扩展插件系统，支持自定义集成和功能
- **⚡ 异步优先设计** - 为高性能并发处理而构建
- **🎛️ 事件驱动通信** - 通过事件总线实现实时智能体协作
- **📋 高级任务管理** - 支持依赖关系、优先级和生命周期管理的任务调度
- **🔒 类型安全** - 完整类型提示和 Pydantic 运行时验证

### 🛠️ 内置功能
- **🖥️ CLI工具** - 开发和部署的综合命令行界面
- **📊 监控与健康检查** - 内置指标、日志和系统健康监控
- **🔧 配置管理** - 支持JSON/YAML的灵活配置
- **📦 插件发现** - 自动插件发现和热加载
- **🧪 测试框架** - 智能体开发的内置测试工具

### 🚀 即用模板
- **基础智能体** - 入门的简单智能体模板
- **Web API智能体** - 基于 FastAPI 的 HTTP API 集成
- **聊天机器人智能体** - 多接口对话式AI
- **数据处理智能体** - 数据分析和转换工作流

## 🚀 快速开始

### 安装

```bash
# 从源码安装
git clone git@github.com:grass2036/agentflow.git
cd agentflow
pip install -e .
```

### 验证安装

```bash
# 检查版本和状态
python3 -m agentflow --version
python3 -m agentflow status
```

### 体验核心功能

```bash
# 运行快速示例（零依赖）
python3 simple_agent_example.py

# 验证系统健康状态
python3 run_basic_tests.py

# 查看可用插件
python3 -m agentflow plugins list --available
```

## 📝 使用说明

### 🚀 快速体验

最简单的开始方式是运行内置示例：

```bash
python3 simple_agent_example.py
```

这个示例将：
- ✅ 创建一个演示智能体
- ✅ 处理5个不同类型的任务
- ✅ 显示完整的执行结果
- ✅ 检查API密钥配置状态

### 🔑 配置API密钥

为了使用AI功能，需要配置API密钥：

1. **复制环境变量模板**：
   ```bash
   cp .env.example .env
   ```

2. **编辑 `.env` 文件**，添加你的API密钥：
   ```bash
   # OpenAI API Key (从 https://platform.openai.com/api-keys 获取)
   OPENAI_API_KEY=your-openai-key-here
   
   # OpenRouter API Key (从 https://openrouter.ai/ 获取，支持多种模型)
   OPENROUTER_API_KEY=your-openrouter-key-here
   
   # Google Gemini API Key (从 https://makersuite.google.com/app/apikey 获取)
   GEMINI_API_KEY=your-gemini-key-here
   
   # Claude API Key (从 https://console.anthropic.com/ 获取)
   CLAUDE_API_KEY=your-claude-key-here
   ```

3. **重新运行示例**验证配置：
   ```bash
   python3 simple_agent_example.py
   ```

### 📦 插件系统

查看和管理插件：

```bash
# 查看所有可用插件
python3 -m agentflow plugins list --available

# 查看特定插件信息
python3 -m agentflow plugins info hello_world
```

内置插件包括：
- **hello_world** - 基础演示插件
- **openai** - OpenAI API集成
- **openrouter** - OpenRouter多模型API集成

### 🧪 测试系统健康

```bash
# 运行核心功能测试
python3 run_basic_tests.py

# 如果安装了pytest，可以运行完整测试套件
pytest tests/unit/
pytest tests/integration/
```

### 🎯 创建新项目

```bash
# 创建基础项目
python3 -m agentflow create my-agent --template basic

# 创建Web API项目
python3 -m agentflow create my-web-agent --template web

# 在当前目录初始化项目
python3 -m agentflow init --template basic
```

## 🏗️ 高级使用

### 自定义智能体示例

```python
#!/usr/bin/env python3
import asyncio
from agentflow.plugins.base import BasePlugin, PluginMetadata

class MyCustomPlugin(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my_plugin",
            version="1.0.0",
            description="我的自定义智能体插件",
            author="你的名字"
        )
    
    async def initialize(self) -> None:
        print("🚀 插件初始化成功！")
    
    async def execute_task(self, context):
        return {"result": "任务执行成功！"}

async def main():
    plugin = MyCustomPlugin()
    await plugin.initialize()
    result = await plugin.execute_task({})
    print(f"执行结果: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 多智能体协作

```python
from agentflow.core.orchestrator import AgentOrchestrator
from agentflow.agents.base import create_mock_agent
from agentflow.core.types import AgentRole

async def multi_agent_example():
    # 创建协调器
    orchestrator = AgentOrchestrator()
    
    # 注册多个智能体
    roles = [
        AgentRole.PROJECT_MANAGER,
        AgentRole.BACKEND_DEVELOPER,
        AgentRole.FRONTEND_DEVELOPER
    ]
    
    for role in roles:
        agent = create_mock_agent(role)
        orchestrator.register_agent(agent)
    
    # 获取协调器状态
    status = orchestrator.get_orchestrator_status()
    print(f"已注册智能体: {status['registered_agents']}")

# 运行示例
asyncio.run(multi_agent_example())
```

## 🔧 开发指南

### 目录结构

```
agentflow/
├── agentflow/              # 核心Python包
│   ├── core/              # 核心功能模块
│   ├── agents/            # AI智能体模块
│   ├── plugins/           # 插件系统
│   ├── cli/               # 命令行接口
│   └── tools/             # 实用工具
├── tests/                 # 测试文件
├── docs/                  # 文档目录
├── docker/                # Docker配置
├── simple_agent_example.py # 快速示例
├── run_basic_tests.py     # 核心测试
└── pyproject.toml         # 项目配置
```

### 开发环境设置

```bash
# 克隆仓库
git clone git@github.com:grass2036/agentflow.git
cd agentflow

# 安装开发依赖
pip install -e .[dev]

# 安装代码质量工具
pip install black isort mypy flake8 pytest

# 设置预提交钩子
pre-commit install
```

### 代码质量

```bash
# 代码格式化
black .
isort .

# 类型检查
mypy agentflow/

# 代码检查
flake8

# 运行测试
pytest
```

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 如何贡献

1. **Fork 仓库**
2. **创建功能分支** (`git checkout -b feature/amazing-feature`)
3. **提交更改** (`git commit -m 'Add amazing feature'`)
4. **推送分支** (`git push origin feature/amazing-feature`)
5. **创建 Pull Request**

### 开发流程

1. **报告问题** - 在 GitHub Issues 中报告bug或请求功能
2. **讨论方案** - 与维护者讨论实现方案
3. **编写代码** - 遵循项目代码风格
4. **添加测试** - 为新功能编写测试
5. **更新文档** - 更新相关文档
6. **代码审查** - 提交PR并参与代码审查

## 📚 文档

- **[安装指南](docs/INSTALLATION.md)** - 详细安装说明
- **[API文档](docs/API.md)** - 完整API参考
- **[插件开发](docs/PLUGIN_DEVELOPMENT.md)** - 插件开发指南
- **[架构设计](docs/ARCHITECTURE.md)** - 系统架构说明
- **[示例项目](examples/)** - 更多示例代码

## 🆘 获取帮助

- **GitHub Issues** - 报告bug和功能请求
- **GitHub Discussions** - 社区讨论和问答
- **文档** - 查看 `docs/` 目录中的详细文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有贡献者和支持者！

---

**开始使用 AgentFlow 构建你的智能体系统！** 🚀

如有任何问题或建议，欢迎通过 GitHub Issues 联系我们。