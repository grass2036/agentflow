# 🧪 AI Agent Testing Environment

完整的AI Agent测试环境，包含Docker容器化支持和结构化测试框架。

## 📁 测试结构

```
tests/
├── 📄 README.md              # 此文件 - 测试文档
├── 🎭 demos/                 # 系统演示
│   └── demo_ai_agents.py     # 多Agent协调演示
├── 🔗 integration/           # 集成测试
│   ├── basic_xai_test.py     # XAI API基础测试
│   ├── test_openrouter_*.py  # OpenRouter相关测试
│   ├── test_grok_*.py        # Grok模型测试
│   └── test_dashboard.py     # 仪表板测试
├── 🧪 unit/                  # 单元测试
│   └── test_orchestrator.py  # 协调器单元测试
├── 🛠️ tools/                 # 账户工具
│   ├── check_limits.py       # 检查账户限制
│   ├── detailed_limits_check.py # 详细限制分析
│   └── query_balance_limits.py  # 余额查询
├── 📦 generated/             # AI生成代码示例
│   └── grok_generated_email_sender.py # 生成的邮件系统
├── 🏃 run_tests.py           # 主测试运行器
└── 📋 fixtures/              # 测试数据和Mock
```

## 🚀 快速开始

### 1. 本地测试

```bash
# 运行所有测试
python tests/run_tests.py

# 运行特定类型测试
python tests/run_tests.py integration  # 集成测试
python tests/run_tests.py tools        # 账户工具
python tests/run_tests.py demos        # 系统演示
python tests/run_tests.py unit         # 单元测试
```

### 2. Docker容器测试

```bash
# 构建测试镜像
docker-compose build ai-agent-test

# 运行容器化测试
docker-compose run --rm ai-agent-test

# 运行完整环境测试 (包含Redis, PostgreSQL)
docker-compose --profile full run --rm ai-agent-test
```

### 3. Make命令 (便捷方式)

```bash
make help           # 显示所有命令
make test           # 运行所有测试
make test-integration # 集成测试
make test-tools     # 账户工具
make docker-test    # Docker测试
make clean          # 清理测试结果
```

## ⚙️ 环境配置

### API密钥配置

编辑 `.env` 文件：

```bash
# OpenRouter API (推荐 - 325个模型)
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# XAI API (可选)
XAI_API_KEY=xai-your-key-here

# Gemini API (可选)
GEMINI_API_KEY=your-gemini-key-here
```

### 测试依赖安装

```bash
# 安装测试依赖
pip install -r requirements-test.txt

# 或者安装完整开发环境
pip install -e .[dev]
```

## 🧪 测试类型说明

### 🎭 Demos (演示)
- **目的**: 展示系统完整功能
- **内容**: 端到端场景演示
- **运行**: `python tests/run_tests.py demos`

**示例:**
```bash
python tests/demos/demo_ai_agents.py
# 展示9个AI Agent协作开发邮件系统
```

### 🔗 Integration (集成测试)
- **目的**: 测试API集成和外部服务
- **要求**: 需要真实API密钥
- **内容**: 真实API调用验证

**示例:**
```bash
python tests/integration/test_openrouter_basic.py
# 测试OpenRouter API连接和模型可用性

python tests/integration/test_grok_premium_toggle.py
# 测试Grok模型和付费开关功能
```

### 🛠️ Tools (账户工具)
- **目的**: 账户管理和监控
- **功能**: 余额查询、限制检查、使用统计

**示例:**
```bash
python tests/tools/check_limits.py
# 快速检查账户限制

python tests/tools/detailed_limits_check.py
# 详细分析账户状态和限制
```

### 🧪 Unit (单元测试)
- **目的**: 测试独立组件功能
- **要求**: 无外部依赖
- **框架**: pytest

**示例:**
```bash
pytest tests/unit/ -v
# 运行所有单元测试
```

## 📊 测试结果

所有测试结果保存在 `test_results/` 目录：

```
test_results/
├── integration/    # 集成测试输出
├── unit/          # 单元测试报告
├── tools/         # 工具执行日志
└── demos/         # 演示运行结果
```

## 🐳 Docker环境

### 基础测试容器
```yaml
# docker-compose.yml
services:
  ai-agent-test:
    build: .
    volumes:
      - ./tests:/app/tests
      - ./test_results:/app/test_results
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
```

### 完整测试环境
```bash
# 包含Redis和PostgreSQL
docker-compose --profile full up
```

## 🔧 高级配置

### pytest配置
```ini
# pytest.ini
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "unit: Unit tests",
    "integration: Integration tests", 
    "tools: Account tools",
    "slow: Slow tests",
]
```

### 覆盖率测试
```bash
pytest --cov=ai_agent --cov-report=html tests/unit/
# 生成HTML覆盖率报告
```

### 性能测试
```bash
pytest --benchmark-only tests/
# 运行性能基准测试
```

## 🚨 故障排除

### 常见问题

**1. API连接失败**
```bash
# 检查API密钥
python tests/tools/check_limits.py

# 解决方案
- 验证.env文件中的API密钥
- 检查网络连接
- 确认API配额未超限
```

**2. 导入错误**
```bash
# 确保项目已安装
pip install -e .

# 检查Python路径
export PYTHONPATH=/path/to/ai-agent
```

**3. Docker构建失败**
```bash
# 清理Docker缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache ai-agent-test
```

## 📈 性能基准

| 测试类型 | 平均耗时 | 最大可接受时间 | 说明 |
|---------|----------|----------------|------|
| 单元测试 | <1秒 | 2秒 | 快速验证 |
| 集成测试 | 5-30秒 | 60秒 | API调用 |
| 演示场景 | 30-120秒 | 300秒 | 完整流程 |
| 账户工具 | 2-10秒 | 30秒 | API查询 |

## 🎯 最佳实践

### 测试编写
1. **隔离性**: 每个测试独立运行
2. **清晰性**: 测试名称描述功能
3. **速度**: 单元测试快速(<1秒)
4. **可靠性**: 不依赖外部状态
5. **文档**: 复杂测试添加注释

### CI/CD集成
```yaml
# GitHub Actions 示例
name: AI Agent Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          docker-compose run --rm ai-agent-test
```

## 🤝 贡献指南

添加新测试时：
1. 选择合适目录 (`unit/`, `integration/`, etc.)
2. 遵循命名约定 (`test_*.py`)
3. 添加适当文档
4. 更新此README
5. 确保测试在CI/CD中通过

## 📞 支持

如有问题，请：
1. 检查此文档
2. 运行 `make help` 查看可用命令
3. 查看 `test_results/` 目录的错误日志
4. 提交Issue到项目仓库