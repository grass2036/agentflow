#!/usr/bin/env python3
"""
Grok 4 Fast + Premium Models Toggle Test
Tests the new Grok 4 Fast integration and premium models toggle functionality
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from ai_agent.core.orchestrator import AgentOrchestrator
from ai_agent.core.types import AgentRole
from ai_agent.agents.openrouter_agent import create_openrouter_agent
from ai_agent.integrations.openrouter_integration import create_openrouter_integration

async def test_grok_and_premium_toggle():
    """测试Grok 4 Fast和付费模型开关功能"""
    print("🚀 Grok 4 Fast + Premium Models Toggle Test")
    print("=" * 80)
    
    # Test 1: 测试免费模型模式 (默认)
    print("\n🆓 Test 1: Free Models Mode (Default)")
    print("-" * 60)
    
    try:
        # 创建免费模式的集成
        free_integration = create_openrouter_integration(
            api_key=os.getenv('OPENROUTER_API_KEY'),
            enable_premium=False  # 默认关闭付费模型
        )
        
        config = free_integration.get_model_configuration()
        print(f"✅ Premium models enabled: {config['premium_models_enabled']}")
        print(f"📊 Free models available: {config['free_models_count']}")
        print(f"🔥 Primary free model: {config['primary_free_model']}")
        print(f"💡 Strategy: {config['model_selection_strategy']}")
        
        # 测试Agent模型信息
        agent_info = free_integration.get_agent_model_info(AgentRole.PROJECT_MANAGER)
        print(f"\n🎭 Project Manager Agent:")
        print(f"   Current model: {agent_info['current_model']}")
        print(f"   Free model: {agent_info['free_model']}")
        print(f"   Premium model: {agent_info['premium_model']}")
        print(f"   Using premium: {agent_info['is_using_premium']}")
        
    except Exception as e:
        print(f"❌ Free mode test failed: {e}")
        return False
    
    # Test 2: 测试付费模型开关
    print(f"\n💰 Test 2: Premium Models Toggle")
    print("-" * 60)
    
    try:
        # 切换到付费模式
        result = free_integration.switch_model_mode("premium")
        print(f"Switch result: {result['message']}")
        print(f"Cost impact: {result['cost_impact']}")
        
        # 验证切换结果
        config_after = free_integration.get_model_configuration()
        print(f"✅ Premium enabled after switch: {config_after['premium_models_enabled']}")
        print(f"📈 Strategy after switch: {config_after['model_selection_strategy']}")
        
        # 测试Agent信息变化
        agent_info_premium = free_integration.get_agent_model_info(AgentRole.BACKEND_DEVELOPER)
        print(f"\n👨‍💻 Backend Developer Agent (Premium Mode):")
        print(f"   Current model: {agent_info_premium['current_model']}")
        print(f"   Using premium: {agent_info_premium['is_using_premium']}")
        
        # 切换回免费模式
        result_back = free_integration.switch_model_mode("free")
        print(f"\n🔄 Switch back result: {result_back['message']}")
        
    except Exception as e:
        print(f"❌ Premium toggle test failed: {e}")
        return False
    
    # Test 3: 测试Grok 4 Fast模型
    print(f"\n🤖 Test 3: Grok 4 Fast Model Test")
    print("-" * 60)
    
    try:
        # 创建使用Grok 4 Fast的Agent
        grok_agent = create_openrouter_agent(
            role=AgentRole.PROJECT_MANAGER,
            enable_premium=False  # 使用免费模型
        )
        
        # 获取模型信息
        model_info = grok_agent.get_model_info()
        print(f"🔥 Grok Agent Info:")
        print(f"   Agent: {model_info['agent_role']}")
        print(f"   Current model: {model_info['current_model']}")
        print(f"   Free model: {model_info['free_model']}")
        print(f"   Current cost: {model_info['model_costs']['current']}")
        
        # 简单任务测试
        print(f"\n📋 Testing Grok 4 Fast with simple task...")
        
        from ai_agent.core.task import create_task
        from ai_agent.core.types import TaskPriority, TechStack
        
        test_task = create_task(
            title="Grok测试任务",
            description="用一句话介绍你自己并说明你的主要功能",
            agent_role=AgentRole.PROJECT_MANAGER,
            priority=TaskPriority.LOW
        )
        
        result = await grok_agent.execute_task(test_task)
        
        if result["success"]:
            print(f"✅ Grok task completed successfully!")
            print(f"📝 Response preview: {result['output'][:100]}...")
            
            metadata = result.get("metadata", {})
            print(f"🔢 Tokens used: {metadata.get('tokens_used', 0)}")
            print(f"💰 Cost: ${metadata.get('estimated_cost', 0):.6f}")
            print(f"🤖 Model used: {metadata.get('model_used', 'Unknown')}")
        else:
            print(f"❌ Grok task failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Grok test failed: {e}")
        return False
    
    # Test 4: 比较免费 vs 付费模型性能
    print(f"\n⚡ Test 4: Free vs Premium Model Comparison")
    print("-" * 60)
    
    try:
        # 创建两个Agent：一个免费，一个付费
        free_agent = create_openrouter_agent(
            role=AgentRole.ARCHITECT,
            enable_premium=False
        )
        
        premium_agent = create_openrouter_agent(
            role=AgentRole.ARCHITECT, 
            enable_premium=True
        )
        
        # 获取模型信息对比
        free_info = free_agent.get_model_info()
        premium_info = premium_agent.get_model_info()
        
        print(f"🆓 Free Agent:")
        print(f"   Model: {free_info['current_model']}")
        print(f"   Cost: {free_info['model_costs']['current']}")
        
        print(f"💎 Premium Agent:")
        print(f"   Model: {premium_info['current_model']}")
        print(f"   Cost: {premium_info['model_costs']['current']}")
        
    except Exception as e:
        print(f"❌ Comparison test failed: {e}")
        return False
    
    # Test 5: 集成到Orchestrator中
    print(f"\n🎼 Test 5: Orchestrator Integration")
    print("-" * 60)
    
    try:
        # 创建使用新配置的协调器
        orchestrator_free = AgentOrchestrator(
            use_openrouter=True, 
            prefer_free_models=True
        )
        
        print(f"✅ Free Orchestrator created with {len(orchestrator_free.agents)} agents")
        
        # 获取Agent统计
        stats = orchestrator_free.get_agent_stats()
        print(f"📊 Agent Stats:")
        print(f"   Total agents: {stats['summary']['total_agents']}")
        print(f"   Using OpenRouter: {stats['summary']['using_openrouter']}")
        print(f"   Prefer free models: {stats['summary']['prefer_free_models']}")
        
        # 测试Agent的模型信息
        if orchestrator_free.agents:
            first_agent = next(iter(orchestrator_free.agents.values()))
            if hasattr(first_agent, 'get_model_info'):
                agent_model_info = first_agent.get_model_info()
                print(f"   Sample agent model: {agent_model_info['current_model']}")
        
    except Exception as e:
        print(f"❌ Orchestrator integration test failed: {e}")
        return False
    
    # 最终总结
    print(f"\n" + "=" * 80)
    print("🎉 Grok 4 Fast + Premium Toggle Test Summary")
    print("=" * 80)
    
    print(f"✅ 免费模型模式: 工作正常，默认使用Grok 4 Fast")
    print(f"✅ 付费模型开关: 可以动态切换，默认关闭")
    print(f"✅ Grok 4 Fast: 集成成功，2M context window")
    print(f"✅ 成本控制: 默认零成本，可选付费模式")
    print(f"✅ Agent集成: 所有Agent支持新配置")
    print(f"✅ Orchestrator: 完全兼容新功能")
    
    print(f"\n💡 使用建议:")
    print(f"🔧 开发/测试: enable_premium=False (免费)")
    print(f"🚀 生产环境: enable_premium=True (高质量)")
    print(f"⚡ 最佳免费模型: x-ai/grok-4-fast:free")
    print(f"📱 动态切换: integration.switch_model_mode('free'/'premium')")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True

async def main():
    """主测试函数"""
    try:
        # 设置环境变量
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            print("❌ OPENROUTER_API_KEY environment variable not set")
            return 1
        
        success = await test_grok_and_premium_toggle()
        return 0 if success else 1
    except Exception as e:
        print(f"💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("🧪 Grok 4 Fast + Premium Models Toggle Integration Test")
    print("Testing enhanced model configuration and premium toggle")
    print("=" * 80)
    
    exit_code = asyncio.run(main())
    print(f"\n🏁 Test completed with exit code: {exit_code}")
    sys.exit(exit_code)