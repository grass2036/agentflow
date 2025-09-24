"""
协调器单元测试
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

import sys
from pathlib import Path

# 添加项目根路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentflow.core.orchestrator import AgentOrchestrator, TaskScheduler, EventBus
from agentflow.core.types import (
    AgentRole, TechStack, ProjectConfig, PlatformType, 
    ProjectComplexity, TaskPriority, TaskStatus
)
from agentflow.core.task import Task, create_task
from agentflow.agents.base import create_mock_agent

class TestTaskScheduler:
    """任务调度器测试"""
    
    def test_scheduler_initialization(self):
        """测试调度器初始化"""
        scheduler = TaskScheduler()
        
        assert scheduler.task_queue == []
        assert scheduler.max_concurrent_tasks == 3
        assert len(scheduler.agent_loads) == 0
    
    def test_add_task(self):
        """测试添加任务"""
        scheduler = TaskScheduler()
        task = create_task(
            title="测试任务",
            agent_role=AgentRole.PROJECT_MANAGER
        )
        
        result = scheduler.add_task(task)
        
        assert result is True
        assert len(scheduler.task_queue) == 1
        assert scheduler.task_queue[0] == task
    
    def test_add_duplicate_task(self):
        """测试添加重复任务"""
        scheduler = TaskScheduler()
        task = create_task(
            title="测试任务",
            agent_role=AgentRole.PROJECT_MANAGER
        )
        
        scheduler.add_task(task)
        result = scheduler.add_task(task)  # 重复添加
        
        assert result is False
        assert len(scheduler.task_queue) == 1
    
    def test_get_ready_tasks_no_dependencies(self):
        """测试获取无依赖的就绪任务"""
        scheduler = TaskScheduler()
        
        task1 = create_task("任务1", agent_role=AgentRole.PROJECT_MANAGER, priority=TaskPriority.HIGH)
        task2 = create_task("任务2", agent_role=AgentRole.ARCHITECT, priority=TaskPriority.MEDIUM)
        
        scheduler.add_task(task1)
        scheduler.add_task(task2)
        
        ready_tasks = scheduler.get_ready_tasks()
        
        assert len(ready_tasks) == 2
        assert ready_tasks[0].priority.value > ready_tasks[1].priority.value  # 按优先级排序
    
    def test_get_ready_tasks_with_dependencies(self):
        """测试获取有依赖的就绪任务"""
        scheduler = TaskScheduler()
        
        task1 = create_task("任务1", agent_role=AgentRole.PROJECT_MANAGER)
        task2 = create_task("任务2", agent_role=AgentRole.ARCHITECT, dependencies=[task1.task_id])
        
        scheduler.add_task(task1)
        scheduler.add_task(task2)
        
        # 没有完成任务时，只有task1可执行
        ready_tasks = scheduler.get_ready_tasks()
        assert len(ready_tasks) == 1
        assert ready_tasks[0] == task1
        
        # task1完成后，task2变为可执行
        completed_task_ids = {task1.task_id}
        ready_tasks = scheduler.get_ready_tasks(completed_task_ids)
        assert len(ready_tasks) == 1
        assert ready_tasks[0] == task2
    
    def test_assign_and_complete_task(self):
        """测试任务分配和完成"""
        scheduler = TaskScheduler()
        task = create_task("测试任务", agent_role=AgentRole.PROJECT_MANAGER)
        
        scheduler.add_task(task)
        
        # 分配任务
        result = scheduler.assign_task(task, "agent_001")
        assert result is True
        assert task.status == TaskStatus.IN_PROGRESS
        assert scheduler.agent_loads[AgentRole.PROJECT_MANAGER] == 1
        
        # 完成任务
        result = scheduler.complete_task(task, {"output": "完成"})
        assert result is True
        assert task.status == TaskStatus.COMPLETED
        assert scheduler.agent_loads[AgentRole.PROJECT_MANAGER] == 0
    
    def test_get_schedule_stats(self):
        """测试获取调度统计"""
        scheduler = TaskScheduler()
        
        task1 = create_task("任务1", agent_role=AgentRole.PROJECT_MANAGER)
        task2 = create_task("任务2", agent_role=AgentRole.ARCHITECT)
        
        scheduler.add_task(task1)
        scheduler.add_task(task2)
        scheduler.assign_task(task1)
        
        stats = scheduler.get_schedule_stats()
        
        assert stats["total_tasks"] == 2
        assert stats["status_distribution"]["pending"] == 1
        assert stats["status_distribution"]["in_progress"] == 1
        assert stats["agent_loads"][AgentRole.PROJECT_MANAGER.value] == 1

class TestEventBus:
    """事件总线测试"""
    
    def test_event_bus_initialization(self):
        """测试事件总线初始化"""
        event_bus = EventBus()
        
        assert len(event_bus.subscribers) == 0
        assert len(event_bus.event_history) == 0
        assert event_bus.max_history == 1000
    
    def test_subscribe(self):
        """测试事件订阅"""
        event_bus = EventBus()
        callback = Mock()
        
        event_bus.subscribe("test_event", callback)
        
        assert "test_event" in event_bus.subscribers
        assert callback in event_bus.subscribers["test_event"]
    
    @pytest.mark.asyncio
    async def test_publish_and_subscribe(self):
        """测试事件发布和订阅"""
        from agentflow.core.types import AgentEvent, EventType
        
        event_bus = EventBus()
        received_events = []
        
        async def callback(event):
            received_events.append(event)
        
        event_bus.subscribe("task_completed", callback)
        
        # 发布事件
        test_event = AgentEvent(
            event_type=EventType.TASK_COMPLETED,
            source_agent=AgentRole.PROJECT_MANAGER,
            data={"task_id": "test_001"}
        )
        
        await event_bus.publish(test_event)
        
        assert len(received_events) == 1
        assert received_events[0] == test_event
        assert len(event_bus.event_history) == 1
    
    @pytest.mark.asyncio 
    async def test_wildcard_subscription(self):
        """测试通配符订阅"""
        from agentflow.core.types import AgentEvent, EventType
        
        event_bus = EventBus()
        received_events = []
        
        def callback(event):
            received_events.append(event)
        
        event_bus.subscribe("*", callback)
        
        # 发布不同类型的事件
        events = [
            AgentEvent(EventType.TASK_STARTED, AgentRole.PROJECT_MANAGER),
            AgentEvent(EventType.TASK_COMPLETED, AgentRole.ARCHITECT),
        ]
        
        for event in events:
            await event_bus.publish(event)
        
        assert len(received_events) == 2
    
    def test_get_recent_events(self):
        """测试获取最近事件"""
        from agentflow.core.types import AgentEvent, EventType
        
        event_bus = EventBus()
        
        # 添加多个事件到历史
        for i in range(5):
            event = AgentEvent(
                EventType.TASK_COMPLETED,
                AgentRole.PROJECT_MANAGER,
                data={"index": i}
            )
            event_bus.event_history.append(event)
        
        recent = event_bus.get_recent_events(3)
        
        assert len(recent) == 3
        assert recent[-1].data["index"] == 4  # 最新的事件

class TestAgentOrchestrator:
    """协调器测试"""
    
    def test_orchestrator_initialization(self):
        """测试协调器初始化"""
        orchestrator = AgentOrchestrator()
        
        assert len(orchestrator.agents) == 0
        assert isinstance(orchestrator.scheduler, TaskScheduler)
        assert isinstance(orchestrator.event_bus, EventBus)
        assert len(orchestrator.sessions) == 0
        assert len(orchestrator.project_templates) > 0
    
    def test_register_agent(self):
        """测试注册Agent"""
        orchestrator = AgentOrchestrator()
        agent = create_mock_agent(AgentRole.PROJECT_MANAGER)
        
        result = orchestrator.register_agent(agent)
        
        assert result is True
        assert AgentRole.PROJECT_MANAGER in orchestrator.agents
        assert orchestrator.agents[AgentRole.PROJECT_MANAGER] == agent
    
    def test_register_invalid_agent(self):
        """测试注册无效Agent"""
        orchestrator = AgentOrchestrator()
        invalid_agent = "not_an_agent"
        
        result = orchestrator.register_agent(invalid_agent)
        
        assert result is False
        assert len(orchestrator.agents) == 0
    
    def test_decompose_project(self):
        """测试项目分解"""
        orchestrator = AgentOrchestrator()
        
        config = ProjectConfig(
            name="测试项目",
            description="测试项目描述",
            tech_stack=[TechStack.PYTHON_FASTAPI, TechStack.VUE_JS],
            target_platform=PlatformType.WEB,
            complexity=ProjectComplexity.MEDIUM,
            requirements=["需求1", "需求2", "需求3"]
        )
        
        tasks = orchestrator.decompose_project(config)
        
        assert len(tasks) > 0
        assert all(isinstance(task, Task) for task in tasks)
        assert any(task.agent_role == AgentRole.PROJECT_MANAGER for task in tasks)
        assert any(task.agent_role == AgentRole.ARCHITECT for task in tasks)
        
        # 检查任务依赖关系
        pm_tasks = [t for t in tasks if t.agent_role == AgentRole.PROJECT_MANAGER]
        arch_tasks = [t for t in tasks if t.agent_role == AgentRole.ARCHITECT]
        
        if pm_tasks and arch_tasks:
            # 架构任务应该依赖项目管理任务
            assert pm_tasks[0].task_id in arch_tasks[0].dependencies
    
    @pytest.mark.asyncio
    async def test_execute_project_basic(self):
        """测试基础项目执行"""
        orchestrator = AgentOrchestrator()
        
        # 注册mock agents
        for role in [AgentRole.PROJECT_MANAGER, AgentRole.ARCHITECT]:
            agent = create_mock_agent(role)
            orchestrator.register_agent(agent)
        
        config = ProjectConfig(
            name="简单项目",
            description="简单测试项目",
            tech_stack=[TechStack.PYTHON_FASTAPI],
            target_platform=PlatformType.API,
            complexity=ProjectComplexity.SIMPLE,
            requirements=["基础功能"]
        )
        
        result = await orchestrator.execute_project(config)
        
        assert result["success"] is True
        assert "session_id" in result
        assert "execution_time" in result
        assert result["tasks_completed"] >= 0
        assert result["total_tasks"] > 0
    
    def test_get_orchestrator_status(self):
        """测试获取协调器状态"""
        orchestrator = AgentOrchestrator()
        
        # 注册一些agents
        for role in [AgentRole.PROJECT_MANAGER, AgentRole.ARCHITECT]:
            agent = create_mock_agent(role)
            orchestrator.register_agent(agent)
        
        status = orchestrator.get_orchestrator_status()
        
        assert "active_sessions" in status
        assert "total_sessions" in status
        assert "registered_agents" in status
        assert "metrics" in status
        assert "scheduler_stats" in status
        
        assert status["registered_agents"] == 2
    
    def test_list_project_templates(self):
        """测试列出项目模板"""
        orchestrator = AgentOrchestrator()
        
        templates = orchestrator.list_project_templates()
        
        assert isinstance(templates, dict)
        assert len(templates) > 0
        
        # 检查模板结构
        for template_id, template_info in templates.items():
            assert "name" in template_info
            assert "tech_stack" in template_info
            assert "estimated_tasks" in template_info
            assert isinstance(template_info["tech_stack"], list)

@pytest.mark.asyncio
class TestAgentOrchestratorIntegration:
    """协调器集成测试"""
    
    async def test_full_project_workflow(self):
        """测试完整项目工作流"""
        orchestrator = AgentOrchestrator()
        
        # 注册所有需要的agents
        roles = [
            AgentRole.PROJECT_MANAGER,
            AgentRole.ARCHITECT,
            AgentRole.BACKEND_DEVELOPER,
            AgentRole.FRONTEND_DEVELOPER
        ]
        
        for role in roles:
            agent = create_mock_agent(role)
            orchestrator.register_agent(agent)
        
        # 配置项目
        config = ProjectConfig(
            name="集成测试项目",
            description="完整工作流测试",
            tech_stack=[TechStack.PYTHON_FASTAPI, TechStack.VUE_JS, TechStack.POSTGRESQL],
            target_platform=PlatformType.WEB,
            complexity=ProjectComplexity.MEDIUM,
            requirements=[
                "用户管理",
                "数据展示", 
                "API接口",
                "前端界面"
            ]
        )
        
        # 执行项目
        result = await orchestrator.execute_project(config)
        
        # 验证结果
        assert result["success"] is True
        assert result["tasks_completed"] > 0
        assert result["total_tasks"] >= result["tasks_completed"]
        
        # 验证会话状态
        session_id = result["session_id"]
        session_status = orchestrator.get_session_status(session_id)
        
        assert session_status["session_id"] == session_id
        assert "project_name" in session_status
        assert "task_statistics" in session_status
    
    async def test_agent_collaboration(self):
        """测试Agent协作"""
        orchestrator = AgentOrchestrator()
        
        # 注册agents并跟踪它们的活动
        agents = {}
        for role in [AgentRole.PROJECT_MANAGER, AgentRole.ARCHITECT, AgentRole.BACKEND_DEVELOPER]:
            agent = create_mock_agent(role)
            orchestrator.register_agent(agent)
            agents[role] = agent
        
        config = ProjectConfig(
            name="协作测试",
            description="测试Agent间协作",
            tech_stack=[TechStack.PYTHON_FASTAPI],
            target_platform=PlatformType.API,
            complexity=ProjectComplexity.SIMPLE,
            requirements=["基础API", "数据处理"]
        )
        
        # 执行前检查agent状态
        initial_tasks = {role: len(agent.current_tasks) for role, agent in agents.items()}
        
        result = await orchestrator.execute_project(config)
        
        # 执行后检查agent状态
        final_tasks = {role: len(agent.current_tasks) for role, agent in agents.items()}
        completed_tasks = {role: len(agent.completed_tasks) for role, agent in agents.items()}
        
        # 验证agents确实执行了任务
        assert result["success"] is True
        assert sum(completed_tasks.values()) > 0
        
        # 验证任务分配合理
        assert completed_tasks[AgentRole.PROJECT_MANAGER] > 0  # 项目经理应该有任务

# 测试运行入口
if __name__ == "__main__":
    pytest.main([__file__, "-v"])