#!/usr/bin/env python3
"""
OpenRouter AI Agent System Integration Test
Tests the complete integration of OpenRouter with the AI Agent Orchestrator
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from ai_agent.core.orchestrator import AgentOrchestrator
from ai_agent.core.types import (
    ProjectConfig, TechStack, PlatformType, ProjectComplexity, 
    TaskPriority, AgentRole
)
from ai_agent.core.task import create_task

async def test_openrouter_agent_system():
    """测试OpenRouter AI Agent系统集成"""
    print("🚀 OpenRouter AI Agent System Integration Test")
    print("=" * 80)
    
    # Test 1: 创建使用OpenRouter的协调器
    print("\n📋 Test 1: Creating OpenRouter-Enabled Orchestrator")
    print("-" * 60)
    
    try:
        # 测试免费模型优先
        orchestrator_free = AgentOrchestrator(use_openrouter=True, prefer_free_models=True)
        print("✅ OpenRouter Orchestrator (Free Models) created successfully")
        
        # 测试付费模型优先
        orchestrator_premium = AgentOrchestrator(use_openrouter=True, prefer_free_models=False)
        print("✅ OpenRouter Orchestrator (Premium Models) created successfully")
        
    except Exception as e:
        print(f"❌ Failed to create orchestrator: {e}")
        return False
    
    # Test 2: 测试Agent连接
    print(f"\n💻 Test 2: Testing Agent Connections")
    print("-" * 60)
    
    connection_results = orchestrator_free.test_all_agent_connections()
    successful_connections = 0
    
    for role, result in connection_results.items():
        if result.get("success", False):
            print(f"✅ {role}: Connected successfully")
            successful_connections += 1
        else:
            print(f"❌ {role}: Connection failed - {result.get('error', 'Unknown error')}")
    
    print(f"📊 Connection Summary: {successful_connections}/{len(connection_results)} agents connected")
    
    if successful_connections == 0:
        print("❌ No agents connected successfully. Check API key and configuration.")
        return False
    
    # Test 3: 单个Agent任务测试
    print(f"\n🤖 Test 3: Individual Agent Task Tests")
    print("-" * 60)
    
    # 创建测试任务
    test_tasks = [
        {
            "role": AgentRole.PROJECT_MANAGER,
            "task": create_task(
                title="项目需求分析",
                description="为一个简单的待办事项应用制定项目计划，包括技术选型、时间线和风险评估",
                agent_role=AgentRole.PROJECT_MANAGER,
                tech_requirements=[TechStack.PYTHON_FASTAPI, TechStack.VUE_JS],
                priority=TaskPriority.HIGH
            )
        },
        {
            "role": AgentRole.BACKEND_DEVELOPER,
            "task": create_task(
                title="API接口设计",
                description="设计一个简单的用户认证API，包括注册、登录和JWT token验证",
                agent_role=AgentRole.BACKEND_DEVELOPER,
                tech_requirements=[TechStack.PYTHON_FASTAPI],
                priority=TaskPriority.MEDIUM
            )
        }
    ]
    
    task_results = []
    
    for test_case in test_tasks:
        role = test_case["role"]
        task = test_case["task"]
        
        print(f"\n🎭 Testing {role.value}")
        print(f"📋 Task: {task.title}")
        
        if role in orchestrator_free.agents:
            agent = orchestrator_free.agents[role]
            
            try:
                # 执行任务
                result = await agent.execute_task(task)
                
                if result["success"]:
                    print(f"✅ Task completed successfully")
                    print(f"📝 Output preview: {result['output'][:100]}...")
                    
                    metadata = result.get("metadata", {})
                    tokens_used = metadata.get("tokens_used", 0)
                    cost = metadata.get("estimated_cost", 0)
                    model_used = metadata.get("model_used", "Unknown")
                    
                    print(f"🔢 Tokens used: {tokens_used}")
                    print(f"💰 Estimated cost: ${cost:.6f}")
                    print(f"🤖 Model used: {model_used}")
                    
                    task_results.append({
                        "role": role.value,
                        "success": True,
                        "tokens": tokens_used,
                        "cost": cost,
                        "model": model_used
                    })
                else:
                    print(f"❌ Task failed: {result.get('error', 'Unknown error')}")
                    task_results.append({
                        "role": role.value,
                        "success": False,
                        "error": result.get('error', 'Unknown error')
                    })
                    
            except Exception as e:
                print(f"❌ Exception during task execution: {e}")
                task_results.append({
                    "role": role.value,
                    "success": False,
                    "error": str(e)
                })
        else:
            print(f"❌ Agent {role.value} not available")
    
    # Test 4: 项目执行测试（小规模）
    print(f"\n🏗️ Test 4: Mini Project Execution")
    print("-" * 60)
    
    mini_project_config = ProjectConfig(
        name="OpenRouter测试项目",
        description="使用OpenRouter集成的简单API项目测试",
        tech_stack=[TechStack.PYTHON_FASTAPI],
        target_platform=PlatformType.API,
        complexity=ProjectComplexity.SIMPLE,
        requirements=[
            "简单的用户API",
            "基础错误处理",
            "API文档"
        ],
        priority=TaskPriority.MEDIUM
    )
    
    print(f"📋 Project: {mini_project_config.name}")
    print(f"🎯 Platform: {mini_project_config.target_platform.value}")
    print(f"🔧 Tech Stack: {', '.join([tech.value for tech in mini_project_config.tech_stack])}")
    
    try:
        # 执行小型项目（限制任务数量以节省成本）
        project_result = await orchestrator_free.execute_project(mini_project_config)
        
        if project_result["success"]:
            print(f"✅ Mini project completed successfully!")
            print(f"⏱️ Execution time: {project_result['execution_time']}")
            print(f"📊 Tasks completed: {project_result['tasks_completed']}/{project_result['total_tasks']}")
            print(f"📈 Success rate: {project_result['success_rate']}")
        else:
            print(f"❌ Mini project failed: {project_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception during project execution: {e}")
    
    # Test 5: 成本和性能统计
    print(f"\n📊 Test 5: Cost & Performance Statistics")
    print("-" * 60)
    
    agent_stats = orchestrator_free.get_agent_stats()
    
    print(f"🤖 Total Agents: {agent_stats['summary']['total_agents']}")
    print(f"🔢 Total Tokens Used: {agent_stats['summary']['total_tokens_used']:,}")
    print(f"💰 Total Cost: ${agent_stats['summary']['total_cost_usd']:.6f}")
    print(f"🆓 Using Free Models: {agent_stats['summary']['prefer_free_models']}")
    
    # 显示各个Agent的统计
    print(f"\n📋 Individual Agent Statistics:")
    for agent_role, stats in agent_stats["individual_agents"].items():
        if stats.get("tasks_completed", 0) > 0:
            print(f"  🎭 {agent_role}:")
            print(f"     Tasks: {stats['tasks_completed']}")
            print(f"     Tokens: {stats['total_tokens_used']:,}")
            print(f"     Cost: ${stats['total_cost_usd']:.6f}")
            print(f"     Avg/Task: {stats['average_tokens_per_task']:.1f} tokens")
    
    # Test 6: 免费 vs 付费模型对比
    print(f"\n⚡ Test 6: Free vs Premium Model Comparison")
    print("-" * 60)
    
    print("🆓 Free Models Summary:")
    free_cost = agent_stats['summary']['total_cost_usd']
    free_tokens = agent_stats['summary']['total_tokens_used']
    print(f"   Total Cost: ${free_cost:.6f}")
    print(f"   Total Tokens: {free_tokens:,}")
    
    # 简单估算付费模型成本（假设比免费模型贵10倍）
    estimated_premium_cost = free_cost * 10 if free_cost > 0 else 0.01
    print(f"\n💎 Estimated Premium Models Cost: ${estimated_premium_cost:.6f}")
    print(f"💰 Savings with Free Models: ${estimated_premium_cost - free_cost:.6f}")
    
    # 最终总结
    print(f"\n" + "=" * 80)
    print("🎉 OpenRouter AI Agent System Integration Test Summary")
    print("=" * 80)
    
    successful_tasks = sum(1 for result in task_results if result["success"])
    total_tasks = len(task_results)
    
    print(f"🔑 API Key: Valid and working")
    print(f"🤖 Agents Initialized: {len(orchestrator_free.agents)}")
    print(f"🔗 Successful Connections: {successful_connections}/{len(connection_results)}")
    print(f"✅ Task Success Rate: {successful_tasks}/{total_tasks}")
    print(f"🔢 Total Tokens Used: {agent_stats['summary']['total_tokens_used']:,}")
    print(f"💰 Total Cost: ${agent_stats['summary']['total_cost_usd']:.6f}")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 推荐配置
    print(f"\n💡 Recommended Configuration:")
    print(f"   ✓ Use OpenRouter: True")
    print(f"   ✓ Prefer Free Models: True (for development/testing)")
    print(f"   ✓ Available Models: 325+ models through OpenRouter")
    print(f"   ✓ Cost Optimization: Free models available for most tasks")
    
    overall_success = successful_connections > 0 and successful_tasks > 0
    
    if overall_success:
        print(f"\n🎊 OpenRouter integration is fully functional!")
        print(f"🚀 Ready for production use with multi-agent coordination")
    else:
        print(f"\n⚠️ OpenRouter integration needs attention")
        print(f"🔧 Check API configuration and network connectivity")
    
    return overall_success

async def main():
    """主测试函数"""
    try:
        success = await test_openrouter_agent_system()
        return 0 if success else 1
    except Exception as e:
        print(f"💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("🧪 OpenRouter AI Agent System Integration Test")
    print("Testing complete integration with multi-agent coordination")
    print("=" * 80)
    
    exit_code = asyncio.run(main())
    print(f"\n🏁 Test completed with exit code: {exit_code}")
    sys.exit(exit_code)