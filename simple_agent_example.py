#!/usr/bin/env python3
"""
简单的AgentFlow示例
=================

这个示例展示了AgentFlow的基本使用方法，不依赖复杂的插件系统。
"""

import asyncio
import logging
import os
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleAgent:
    """简单的AI智能体示例"""
    
    def __init__(self, name: str):
        self.name = name
        self.tasks_completed = 0
        self.api_keys = self._load_api_keys()
        
    def _load_api_keys(self) -> Dict[str, str]:
        """从环境变量加载API keys"""
        keys = {}
        
        # 检查各种API keys
        api_vars = [
            'OPENAI_API_KEY',
            'OPENROUTER_API_KEY', 
            'GEMINI_API_KEY',
            'CLAUDE_API_KEY'
        ]
        
        for var in api_vars:
            value = os.getenv(var)
            if value:
                keys[var] = value
                logger.info(f"✅ Loaded {var}")
            else:
                logger.warning(f"⚠️  {var} not found in environment")
                
        return keys
        
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理一个任务"""
        task_id = task.get("id", "unknown")
        task_type = task.get("type", "generic")
        
        logger.info(f"🔄 Processing task {task_id} ({task_type})")
        
        # 模拟任务处理
        await asyncio.sleep(0.1)
        
        self.tasks_completed += 1
        
        result = {
            "task_id": task_id,
            "status": "completed",
            "result": f"Task {task_id} completed successfully by {self.name}",
            "agent": self.name,
            "processed_at": asyncio.get_event_loop().time()
        }
        
        logger.info(f"✅ Completed task {task_id}")
        return result
        
    async def run_demo(self):
        """运行演示"""
        logger.info(f"🌊 Starting {self.name} agent demo")
        
        # 示例任务列表
        tasks = [
            {"id": "task_001", "type": "text_processing", "data": {"text": "Hello AgentFlow"}},
            {"id": "task_002", "type": "data_analysis", "data": {"numbers": [1, 2, 3, 4, 5]}},
            {"id": "task_003", "type": "api_call", "data": {"endpoint": "/test"}},
            {"id": "task_004", "type": "file_processing", "data": {"filename": "example.txt"}},
            {"id": "task_005", "type": "validation", "data": {"email": "user@example.com"}}
        ]
        
        logger.info(f"📋 Processing {len(tasks)} tasks...")
        
        results = []
        for task in tasks:
            result = await self.process_task(task)
            results.append(result)
            
        # 显示结果
        print("\n" + "="*60)
        print("🎉 AgentFlow 演示结果")
        print("="*60)
        print(f"智能体名称: {self.name}")
        print(f"任务完成数: {self.tasks_completed}")
        print(f"成功率: 100%")
        print(f"配置的API Keys: {len(self.api_keys)}")
        
        print("\n📊 任务详情:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['task_id']}: {result['status']}")
            
        print("\n🔑 API配置状态:")
        if self.api_keys:
            for key in self.api_keys:
                print(f"  ✅ {key}: 已配置")
        else:
            print("  ⚠️  没有找到API keys，请检查.env文件")
            
        print("="*60)


async def main():
    """主函数"""
    print("🌊 AgentFlow 简单示例")
    print("============================")
    print()
    
    # 创建智能体
    agent = SimpleAgent("DemoAgent")
    
    try:
        # 运行演示
        await agent.run_demo()
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
    except Exception as e:
        logger.error(f"❌ 发生错误: {e}")
        print(f"❌ 发生错误: {e}")
    finally:
        print("\n👋 演示结束")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())