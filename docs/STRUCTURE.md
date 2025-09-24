# 📁 AgentFlow 项目结构

```
agentflow/
├── 📋 项目配置
│   ├── pyproject.toml              # 项目配置和依赖
│   ├── requirements.txt            # 核心依赖包
│   ├── pytest.ini                 # 测试配置
│   ├── .gitignore                  # Git忽略文件
│   └── .env.example               # 环境变量模板
│
├── 🌊 AgentFlow 核心
│   └── agentflow/                 # 主要源码目录
│       ├── __init__.py            # 包初始化
│       ├── cli/                   # 命令行界面
│       │   ├── __init__.py
│       │   └── main.py           # CLI主要逻辑
│       ├── core/                  # 核心系统
│       │   ├── __init__.py
│       │   └── (核心模块)
│       ├── plugins/               # 插件系统
│       │   ├── __init__.py
│       │   ├── base.py           # 插件基类
│       │   ├── manager.py        # 插件管理器
│       │   ├── registry.py       # 插件注册表
│       │   └── discovery.py      # 插件发现
│       ├── integrations/          # 外部集成
│       ├── monitoring/            # 监控系统
│       ├── utils/                 # 工具函数
│       ├── config/                # 配置管理
│       ├── tools/                 # 开发工具
│       └── examples/              # 示例项目
│           ├── README.md          # 示例说明
│           ├── basic_agent/       # 基础智能体示例
│           ├── web_api/          # Web API示例
│           └── plugins/          # 插件示例
│               └── codegen/      # 代码生成插件
│
├── 🧪 测试
│   └── tests/                     # 测试文件
│       ├── unit/                 # 单元测试
│       ├── integration/          # 集成测试
│       └── fixtures/             # 测试数据
│
├── 📚 文档
│   ├── README.md                  # 英文说明文档
│   ├── README_CN.md              # 中文说明文档
│   ├── STRUCTURE.md              # 项目结构说明
│   ├── CLAUDE.md                 # 开发者说明
│   └── CHANGELOG.md              # 更新日志
│
├── 🐳 部署
│   ├── Dockerfile                # Docker镜像
│   ├── docker-compose.yml        # Docker编排
│   └── .dockerignore            # Docker忽略文件
│
└── 🛠️ 开发
    ├── .github/                  # GitHub配置
    │   └── workflows/           # CI/CD工作流
    └── agentflow.egg-info/       # 包构建信息
```

## 🎯 核心目录说明

### `agentflow/` - 主要源码
- **`cli/`** - 命令行界面实现，提供项目管理和插件管理功能
- **`plugins/`** - 插件系统核心，支持可扩展的功能模块
- **`core/`** - 框架核心逻辑，包括事件系统和任务管理
- **`examples/`** - 完整的示例项目，展示不同使用场景

### `tests/` - 测试套件
- **`unit/`** - 单元测试，测试独立组件功能
- **`integration/`** - 集成测试，测试组件间协作
- **`fixtures/`** - 测试数据和模拟对象

## 🔧 开发文件

- **`pyproject.toml`** - 现代Python项目配置，包含依赖、构建和工具设置
- **`pytest.ini`** - 测试框架配置，定义测试标记和覆盖率设置
- **`requirements.txt`** - 核心依赖列表，简化基础安装

## 📦 构建产物

- **`agentflow.egg-info/`** - pip安装时自动生成的包元数据
- **`__pycache__/`** - Python字节码缓存（已在.gitignore中忽略）

## 🚀 快速导航

- 查看示例: `agentflow/examples/`
- 开始开发: 阅读 `README.md` 或 `README_CN.md`
- 运行测试: `pytest`
- 安装框架: `pip install -e .`
- 创建项目: `agentflow create my-project --template basic`