#!/usr/bin/env python3
"""
简单的测试运行器
用于运行基础的AgentFlow核心功能测试
"""

import sys
import asyncio
import traceback
from pathlib import Path

# 添加项目根路径
sys.path.insert(0, str(Path(__file__).parent))

def test_basic_imports():
    """测试基础导入"""
    print("🔍 测试基础导入...")
    try:
        from agentflow.core.orchestrator import AgentOrchestrator, TaskScheduler, EventBus
        from agentflow.core.types import AgentRole, TechStack, ProjectConfig, PlatformType, ProjectComplexity
        from agentflow.core.task import Task, create_task
        from agentflow.agents.base import create_mock_agent
        print("✅ 基础导入成功")
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        traceback.print_exc()
        return False

def test_task_creation():
    """测试任务创建"""
    print("🔍 测试任务创建...")
    try:
        from agentflow.core.task import create_task
        from agentflow.core.types import AgentRole, TaskPriority
        
        task = create_task(
            title="测试任务",
            description="这是一个测试任务",
            agent_role=AgentRole.PROJECT_MANAGER,
            priority=TaskPriority.HIGH
        )
        
        assert task.title == "测试任务"
        assert task.agent_role == AgentRole.PROJECT_MANAGER
        assert task.priority == TaskPriority.HIGH
        print("✅ 任务创建成功")
        return True
    except Exception as e:
        print(f"❌ 任务创建失败: {e}")
        traceback.print_exc()
        return False

def test_task_scheduler():
    """测试任务调度器"""
    print("🔍 测试任务调度器...")
    try:
        from agentflow.core.orchestrator import TaskScheduler
        from agentflow.core.task import create_task
        from agentflow.core.types import AgentRole, TaskPriority
        
        scheduler = TaskScheduler()
        task = create_task("调度测试任务", agent_role=AgentRole.PROJECT_MANAGER)
        
        # 测试添加任务
        result = scheduler.add_task(task)
        assert result is True
        assert len(scheduler.task_queue) == 1
        
        # 测试获取就绪任务
        ready_tasks = scheduler.get_ready_tasks()
        assert len(ready_tasks) == 1
        
        print("✅ 任务调度器测试成功")
        return True
    except Exception as e:
        print(f"❌ 任务调度器测试失败: {e}")
        traceback.print_exc()
        return False

async def test_event_bus():
    """测试事件总线"""
    print("🔍 测试事件总线...")
    try:
        from agentflow.core.orchestrator import EventBus
        from agentflow.core.types import AgentEvent, EventType, AgentRole
        
        event_bus = EventBus()
        received_events = []
        
        # 订阅事件
        def callback(event):
            received_events.append(event)
        
        event_bus.subscribe("task_completed", callback)
        
        # 发布事件
        test_event = AgentEvent(
            event_type=EventType.TASK_COMPLETED,
            source_agent=AgentRole.PROJECT_MANAGER,
            data={"test": "data"}
        )
        
        await event_bus.publish(test_event)
        
        assert len(received_events) == 1
        assert len(event_bus.event_history) == 1
        
        print("✅ 事件总线测试成功")
        return True
    except Exception as e:
        print(f"❌ 事件总线测试失败: {e}")
        traceback.print_exc()
        return False

def test_mock_agent():
    """测试模拟Agent"""
    print("🔍 测试模拟Agent...")
    try:
        from agentflow.agents.base import create_mock_agent
        from agentflow.core.types import AgentRole
        
        agent = create_mock_agent(AgentRole.PROJECT_MANAGER)
        
        assert agent.role == AgentRole.PROJECT_MANAGER
        assert agent.is_available is True
        assert len(agent.current_tasks) == 0
        
        print("✅ 模拟Agent测试成功")
        return True
    except Exception as e:
        print(f"❌ 模拟Agent测试失败: {e}")
        traceback.print_exc()
        return False

def test_orchestrator_basic():
    """测试协调器基础功能"""
    print("🔍 测试协调器基础功能...")
    try:
        from agentflow.core.orchestrator import AgentOrchestrator
        from agentflow.agents.base import create_mock_agent
        from agentflow.core.types import AgentRole, TechStack, ProjectConfig, PlatformType, ProjectComplexity
        
        orchestrator = AgentOrchestrator()
        
        # 注册Agent
        agent = create_mock_agent(AgentRole.PROJECT_MANAGER)
        result = orchestrator.register_agent(agent)
        assert result is True
        assert len(orchestrator.agents) == 1
        
        # 测试项目分解
        config = ProjectConfig(
            name="测试项目",
            description="一个测试项目",
            tech_stack=[TechStack.PYTHON_FASTAPI],
            target_platform=PlatformType.API,
            complexity=ProjectComplexity.SIMPLE,
            requirements=["基础功能"]
        )
        
        tasks = orchestrator.decompose_project(config)
        assert len(tasks) > 0
        
        print("✅ 协调器基础功能测试成功")
        return True
    except Exception as e:
        print(f"❌ 协调器基础功能测试失败: {e}")
        traceback.print_exc()
        return False

async def test_project_execution():
    """测试项目执行"""
    print("🔍 测试项目执行...")
    try:
        from agentflow.core.orchestrator import AgentOrchestrator
        from agentflow.agents.base import create_mock_agent
        from agentflow.core.types import AgentRole, TechStack, ProjectConfig, PlatformType, ProjectComplexity
        
        orchestrator = AgentOrchestrator()
        
        # 注册多个Agent
        for role in [AgentRole.PROJECT_MANAGER, AgentRole.ARCHITECT, AgentRole.BACKEND_DEVELOPER]:
            agent = create_mock_agent(role)
            orchestrator.register_agent(agent)
        
        config = ProjectConfig(
            name="执行测试项目",
            description="测试项目执行流程",
            tech_stack=[TechStack.PYTHON_FASTAPI],
            target_platform=PlatformType.API,
            complexity=ProjectComplexity.SIMPLE,
            requirements=["API开发", "数据库设计"]
        )
        
        result = await orchestrator.execute_project(config)
        
        assert result["success"] is True
        assert "session_id" in result
        assert result["tasks_completed"] >= 0
        
        print("✅ 项目执行测试成功")
        return True
    except Exception as e:
        print(f"❌ 项目执行测试失败: {e}")
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🌊 AgentFlow 核心功能基础测试")
    print("=" * 50)
    
    tests = [
        ("基础导入", test_basic_imports),
        ("任务创建", test_task_creation),
        ("任务调度器", test_task_scheduler),
        ("事件总线", test_event_bus),
        ("模拟Agent", test_mock_agent),
        ("协调器基础功能", test_orchestrator_basic),
        ("项目执行", test_project_execution),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 运行测试: {test_name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"🎯 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！AgentFlow核心功能正常工作")
        return True
    else:
        print(f"⚠️  有 {total - passed} 个测试失败")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)