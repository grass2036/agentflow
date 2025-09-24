#!/usr/bin/env python3
"""
基础示例：Hello Agent
=====================

这个示例展示了如何创建一个最简单的AgentFlow智能体。

运行方式：
python3 examples/basic/hello_agent.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentflow.plugins.base import BasePlugin, PluginMetadata, PluginContext


class HelloAgent(BasePlugin):
    """最简单的Hello智能体示例"""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="hello_agent",
            version="1.0.0",
            description="最简单的问候智能体",
            author="AgentFlow Examples",
            tags=["basic", "example", "hello"]
        )
    
    async def initialize(self) -> None:
        """初始化智能体"""
        print("🤖 Hello Agent 初始化完成！")
        self.greeting_count = 0
    
    async def execute_task(self, context: PluginContext) -> dict:
        """执行问候任务"""
        name = context.data.get("name", "World")
        language = context.data.get("language", "zh")
        
        greetings = {
            "zh": f"你好，{name}！",
            "en": f"Hello, {name}!",
            "es": f"¡Hola, {name}!",
            "fr": f"Bonjour, {name}!",
            "ja": f"こんにちは、{name}！"
        }
        
        greeting = greetings.get(language, greetings["en"])
        self.greeting_count += 1
        
        print(f"💬 {greeting}")
        
        return {
            "greeting": greeting,
            "language": language,
            "count": self.greeting_count,
            "timestamp": None  # 简化示例，不使用时间戳
        }
    
    async def cleanup(self) -> None:
        """清理资源"""
        print(f"👋 Hello Agent 结束，共问候了 {self.greeting_count} 次")


async def main():
    """主函数演示"""
    print("🌊 AgentFlow 基础示例：Hello Agent")
    print("=" * 50)
    
    # 创建智能体
    agent = HelloAgent()
    
    try:
        # 初始化
        await agent.initialize()
        
        # 创建测试上下文
        test_cases = [
            {"name": "张三", "language": "zh"},
            {"name": "Alice", "language": "en"},
            {"name": "José", "language": "es"},
            {"name": "Marie", "language": "fr"},
            {"name": "田中", "language": "ja"},
        ]
        
        print(f"\n🎯 开始执行 {len(test_cases)} 个问候任务：")
        print("-" * 30)
        
        # 执行任务
        results = []
        for i, test_data in enumerate(test_cases, 1):
            context = PluginContext(
                agent_id="hello_agent",
                task_id=f"task_{i}",
                session_id="demo_session",
                data=test_data
            )
            
            print(f"\n{i}. 问候任务：")
            result = await agent.execute_task(context)
            results.append(result)
            
            print(f"   结果：{result}")
        
        # 显示总结
        print("\n" + "=" * 50)
        print("📊 执行总结：")
        print(f"   总任务数：{len(results)}")
        print(f"   成功率：100%")
        print(f"   支持语言：{len(set(r['language'] for r in results))} 种")
        
    finally:
        # 清理
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())