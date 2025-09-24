# 🌊 AgentFlow 使用示例

这个目录包含了丰富的AgentFlow使用示例，从基础入门到高级应用，帮助您快速掌握多智能体编排框架的使用方法。

## 📋 示例分类

### 🎯 基础示例 (`basic/`)

适合刚开始使用AgentFlow的开发者：

| 示例文件 | 描述 | 关键概念 |
|---------|------|----------|
| `hello_agent.py` | 最简单的智能体示例 | 插件基础、多语言问候 |
| `task_scheduler_demo.py` | 任务调度和依赖管理 | 任务调度、依赖解析 |

**推荐学习顺序**：
1. 先运行 `hello_agent.py` 了解插件基础
2. 再运行 `task_scheduler_demo.py` 学习任务管理

### 🔌 插件开发 (`plugins/`)

学习如何创建自定义插件：

| 示例文件 | 描述 | 特性 |
|---------|------|------|
| `custom_plugin_example.py` | 完整的数据处理插件 | 生命周期管理、多种操作、缓存、统计 |

**学习要点**：
- 插件元数据定义
- 异步任务处理
- 错误处理和日志
- 性能监控

### 🚀 高级示例 (`advanced/`)

复杂场景和高级功能：

| 示例文件 | 描述 | 适用场景 |
|---------|------|----------|
| `multi_agent_collaboration.py` | 多智能体协作项目 | 团队开发、项目管理 |

**核心特性**：
- 6种不同角色的智能体协作
- 完整的项目开发流程模拟
- 事件驱动的实时通信
- 项目交付物生成

### 🌐 Web API集成 (`web_api/`)

将AgentFlow集成到Web应用：

| 示例文件 | 描述 | 技术栈 |
|---------|------|--------|
| `fastapi_integration.py` | RESTful API服务 | FastAPI + AgentFlow |

**API功能**：
- 智能体状态查询
- 项目创建和管理
- 任务执行接口
- 系统监控端点

### 🤖 聊天机器人 (`chatbot/`)

智能对话系统开发：

| 示例文件 | 描述 | 功能 |
|---------|------|------|
| `intelligent_assistant.py` | 多功能智能助手 | 对话、任务管理、计算器 |

**智能功能**：
- 自然语言理解
- 上下文记忆
- 多模态交互
- 个性化服务

## 🚀 快速开始

### 1. 环境准备

```bash
# 确保在项目根目录
cd /path/to/agentflow

# 安装基础依赖
pip install -e .
```

### 2. 运行第一个示例

```bash
# 最简单的入门示例
python3 examples/basic/hello_agent.py
```

预期输出：
```
🌊 AgentFlow 基础示例：Hello Agent
==================================================
🤖 Hello Agent 初始化完成！

🎯 开始执行 5 个问候任务：
------------------------------

1. 问候任务：
💬 你好，张三！
   结果：{'greeting': '你好，张三！', 'language': 'zh', ...}

...

📊 执行总结：
   总任务数：5
   成功率：100%
   支持语言：5 种
```

### 3. 探索任务调度

```bash
# 学习任务依赖和调度
python3 examples/basic/task_scheduler_demo.py
```

### 4. 尝试高级功能

```bash
# 多智能体协作
python3 examples/advanced/multi_agent_collaboration.py

# 智能助手对话
python3 examples/chatbot/intelligent_assistant.py
```

## 📚 详细说明

### 基础示例详解

#### `hello_agent.py` - 入门必读

**学习目标**：
- 理解插件的基本结构
- 掌握异步任务处理
- 学习元数据定义

**关键代码段**：
```python
class HelloAgent(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="hello_agent",
            version="1.0.0",
            description="最简单的问候智能体",
            tags=["basic", "example", "hello"]
        )
    
    async def execute_task(self, context: PluginContext) -> dict:
        # 处理任务逻辑
        name = context.data.get("name", "World")
        greeting = f"你好，{name}！"
        return {"greeting": greeting}
```

#### `task_scheduler_demo.py` - 核心概念

**学习目标**：
- 任务创建和配置
- 依赖关系管理
- 调度算法理解

**核心概念**：
- **依赖解析**：任务B依赖任务A，必须等A完成后才能执行B
- **优先级调度**：高优先级任务优先执行
- **并发控制**：限制同时执行的任务数量

### 插件开发指南

#### `custom_plugin_example.py` - 完整插件

这个示例展示了一个完整的数据处理插件，包含：

**生命周期管理**：
```python
async def initialize(self) -> None:
    # 插件初始化逻辑
    self.register_hook("process_data")
    
async def cleanup(self) -> None:
    # 清理资源
    self.data_cache.clear()
```

**多种操作支持**：
- 数据计数、求和、过滤
- 数据分组、验证
- 缓存管理

**性能监控**：
```python
def get_statistics(self) -> Dict[str, Any]:
    return {
        "processed_count": self.processed_count,
        "success_rate": self.success_rate,
        "cache_size": len(self.data_cache)
    }
```

### 高级应用场景

#### `multi_agent_collaboration.py` - 企业级应用

**业务场景**：模拟真实的软件开发团队协作

**智能体角色**：
- 🎯 **项目经理**：需求分析、项目规划
- 🏗️ **架构师**：系统设计、技术选型
- ⚡ **后端开发**：API开发、数据库设计
- 🎨 **前端开发**：界面开发、用户体验
- 🧪 **测试工程师**：质量保证、测试用例
- 🚀 **DevOps工程师**：部署、运维

**工作流程**：
1. 项目经理分析需求
2. 架构师设计系统架构
3. 开发人员并行开发
4. 测试工程师进行测试
5. DevOps工程师负责部署

### Web API集成

#### `fastapi_integration.py` - 生产级API

**核心端点**：
- `GET /agents` - 查看智能体状态
- `POST /projects` - 创建项目
- `GET /projects/{session_id}` - 查看项目状态
- `POST /agents/{role}/task` - 为智能体分配任务

**使用方法**：
```bash
# 启动服务
python3 examples/web_api/fastapi_integration.py

# 访问API文档
open http://localhost:8000/docs

# 创建项目
curl -X POST "http://localhost:8000/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的项目",
    "description": "项目描述",
    "tech_stack": ["python_fastapi", "vue_js"],
    "complexity": "medium"
  }'
```

### 聊天机器人开发

#### `intelligent_assistant.py` - AI助手

**功能特点**：
- 🧠 **智能对话**：自然语言理解和生成
- 💭 **上下文记忆**：记住用户信息和对话历史
- 🛠️ **多功能工具**：任务管理、计算器、时间查询
- 📋 **命令系统**：支持快捷命令操作

**命令列表**：
- `/help` - 显示帮助
- `/task add <任务>` - 添加任务
- `/calc 2+3*4` - 计算表达式
- `/time` - 查看时间
- `/stats` - 会话统计

## 🔧 开发技巧

### 1. 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 在插件中添加调试输出
print(f"🐛 调试：{context.data}")
```

### 2. 性能优化

```python
# 异步处理大量任务
async def process_batch(self, tasks):
    semaphore = asyncio.Semaphore(5)  # 限制并发数
    
    async def process_single(task):
        async with semaphore:
            return await self.execute_task(task)
    
    results = await asyncio.gather(*[process_single(t) for t in tasks])
    return results
```

### 3. 错误处理

```python
try:
    result = await agent.execute_task(context)
except Exception as e:
    logger.error(f"任务执行失败：{e}")
    # 实现重试逻辑或错误恢复
```

### 4. 测试建议

```python
# 为插件编写测试
import pytest

@pytest.mark.asyncio
async def test_hello_agent():
    agent = HelloAgent()
    await agent.initialize()
    
    context = PluginContext(
        plugin_name="hello_agent",
        data={"name": "测试用户"}
    )
    
    result = await agent.execute_task(context)
    assert result["greeting"] == "你好，测试用户！"
```

## 🤝 贡献示例

我们欢迎您贡献新的示例！

### 贡献指南

1. **选择主题**：确定示例要解决的具体问题
2. **编写代码**：遵循现有示例的代码风格
3. **添加注释**：提供详细的中文注释
4. **测试验证**：确保示例能正常运行
5. **更新文档**：在此README中添加说明

### 示例模板

```python
#!/usr/bin/env python3
"""
示例名称：简短描述
=================

详细说明这个示例的用途和学习目标。

运行方式：
python3 examples/category/example_name.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# 导入AgentFlow模块
from agentflow.plugins.base import BasePlugin, PluginMetadata

# 示例实现...
```

## 📞 获取帮助

如果您在运行示例时遇到问题：

1. **检查依赖**：确保安装了所有必需的依赖
2. **查看日志**：注意控制台的错误信息
3. **参考文档**：阅读项目主要文档
4. **提交Issue**：在GitHub上提交问题报告

---

**开始探索AgentFlow的强大功能吧！** 🚀

每个示例都是独立的，您可以按兴趣选择学习顺序。建议从基础示例开始，逐步深入到高级应用。