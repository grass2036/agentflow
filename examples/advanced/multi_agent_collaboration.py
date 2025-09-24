#!/usr/bin/env python3
"""
高级示例：多智能体协作系统
==========================

这个示例展示了完整的多智能体协作场景，包括项目管理、开发和测试流程。

运行方式：
python3 examples/advanced/multi_agent_collaboration.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentflow.core.orchestrator import AgentOrchestrator
from agentflow.core.types import (
    AgentRole, TechStack, ProjectConfig, PlatformType, 
    ProjectComplexity, TaskPriority
)
from agentflow.agents.base import create_mock_agent


async def create_web_project_example():
    """创建Web项目开发示例"""
    print("🌊 AgentFlow 多智能体协作示例")
    print("📋 项目：在线任务管理系统")
    print("=" * 60)
    
    # 创建协调器
    orchestrator = AgentOrchestrator(use_openrouter=False, prefer_free_models=True)
    
    # 创建多个专业智能体团队
    agent_team = {
        AgentRole.PROJECT_MANAGER: "项目经理 - Alice",
        AgentRole.ARCHITECT: "架构师 - Bob", 
        AgentRole.BACKEND_DEVELOPER: "后端开发 - Charlie",
        AgentRole.FRONTEND_DEVELOPER: "前端开发 - Diana",
        AgentRole.QA_ENGINEER: "测试工程师 - Eve",
        AgentRole.DEVOPS_ENGINEER: "DevOps工程师 - Frank"
    }
    
    print(f"👥 组建开发团队：")
    for role, name in agent_team.items():
        agent = create_mock_agent(role, max_concurrent_tasks=2)
        orchestrator.register_agent(agent)
        print(f"   ✓ {name} ({role.value})")
    
    # 配置项目
    project_config = ProjectConfig(
        name="TaskMaster - 在线任务管理系统",
        description="""
        一个功能完整的在线任务管理系统，支持：
        - 用户注册和认证
        - 任务创建、分配和跟踪
        - 团队协作和权限管理
        - 实时通知和报告
        - 移动端和桌面端支持
        """,
        tech_stack=[
            TechStack.PYTHON_FASTAPI,    # 后端框架
            TechStack.VUE_JS,            # 前端框架
            TechStack.POSTGRESQL,        # 数据库
            TechStack.REDIS,             # 缓存
            TechStack.DOCKER,            # 容器化
            TechStack.AWS                # 云平台
        ],
        target_platform=PlatformType.WEB,
        complexity=ProjectComplexity.MEDIUM,
        requirements=[
            "用户管理：注册、登录、个人资料",
            "任务管理：创建、编辑、删除、状态更新",
            "团队协作：任务分配、评论、文件共享",
            "通知系统：邮件通知、实时推送",
            "数据分析：任务统计、进度报告",
            "移动适配：响应式设计，PWA支持",
            "安全性：JWT认证、权限控制、数据加密",
            "性能优化：缓存策略、数据库优化"
        ]
    )
    
    print(f"\n📋 项目配置：")
    print(f"   名称：{project_config.name}")
    print(f"   复杂度：{project_config.complexity.value}")
    print(f"   技术栈：{', '.join([tech.value for tech in project_config.tech_stack])}")
    print(f"   需求数量：{len(project_config.requirements)}")
    
    # 获取初始状态
    initial_status = orchestrator.get_orchestrator_status()
    print(f"\n🎯 协调器初始状态：")
    print(f"   注册智能体：{initial_status['registered_agents']}")
    print(f"   活跃会话：{initial_status['active_sessions']}")
    
    # 订阅事件以监控进度
    event_log = []
    
    def event_logger(event):
        event_log.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "type": event.event_type.value,
            "agent": event.source_agent.value,
            "data": event.data
        })
        print(f"📢 [{datetime.now().strftime('%H:%M:%S')}] {event.event_type.value}: {event.source_agent.value}")
    
    # 订阅所有事件
    orchestrator.event_bus.subscribe("*", event_logger)
    
    try:
        print(f"\n🚀 开始项目执行...")
        print("=" * 40)
        
        # 执行项目
        result = await orchestrator.execute_project(project_config)
        
        print(f"\n" + "=" * 60)
        print(f"🎯 项目执行结果：")
        print(f"=" * 60)
        
        if result["success"]:
            print(f"✅ 项目执行成功！")
            print(f"   会话ID：{result['session_id']}")
            print(f"   执行时间：{result['execution_time']}")
            print(f"   完成任务：{result['tasks_completed']}/{result['total_tasks']}")
            print(f"   成功率：{result['success_rate']}")
            
            # 显示交付物
            deliverables = result.get('deliverables', {})
            print(f"\n📦 项目交付物：")
            
            for category, items in deliverables.items():
                if items:
                    print(f"   {category.replace('_', ' ').title()}：")
                    for item in items:
                        print(f"      - {item.get('type', 'Unknown')}")
            
        else:
            print(f"❌ 项目执行失败：{result.get('error', '未知错误')}")
        
        # 获取最终状态
        final_status = orchestrator.get_orchestrator_status()
        print(f"\n📊 最终统计：")
        print(f"   总会话数：{final_status['total_sessions']}")
        print(f"   任务完成：{final_status['metrics']['tasks_completed']}")
        print(f"   任务失败：{final_status['metrics']['tasks_failed']}")
        print(f"   总成功率：{final_status['metrics']['success_rate']:.1%}")
        
        # 显示智能体表现
        print(f"\n👥 智能体表现分析：")
        for role in agent_team.keys():
            agent = orchestrator.agents.get(role)
            if agent:
                print(f"   {role.value}：")
                print(f"      - 当前任务：{len(agent.current_tasks)}")
                print(f"      - 已完成：{len(agent.completed_tasks)}")
                print(f"      - 失败任务：{len(agent.failed_tasks)}")
                print(f"      - 成功率：{agent.success_rate:.1%}")
        
        # 显示关键事件
        print(f"\n📝 关键事件日志（最近10个）：")
        for event in event_log[-10:]:
            print(f"   [{event['time']}] {event['type']} - {event['agent']}")
        
        # 获取会话详情
        if result.get("success") and "session_id" in result:
            session_status = orchestrator.get_session_status(result["session_id"])
            print(f"\n🔍 会话详情：")
            print(f"   项目名称：{session_status.get('project_name', 'Unknown')}")
            print(f"   开始时间：{session_status.get('start_time', 'Unknown')}")
            
            task_stats = session_status.get('task_statistics', {})
            if task_stats:
                print(f"   任务统计：{task_stats}")
        
    except Exception as e:
        print(f"💥 执行过程中发生错误：{e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "=" * 60)
    print(f"🎉 多智能体协作演示完成！")
    print(f"   事件总数：{len(event_log)}")
    print(f"   参与智能体：{len(agent_team)}")
    print(f"   技术栈：{len(project_config.tech_stack)} 种")


async def demonstrate_agent_communication():
    """演示智能体间通信"""
    print(f"\n" + "🔄" * 20)
    print(f"🗣️  智能体通信演示")
    print(f"🔄" * 20)
    
    # 创建简化的协调器
    orchestrator = AgentOrchestrator()
    
    # 注册几个智能体
    pm_agent = create_mock_agent(AgentRole.PROJECT_MANAGER)
    dev_agent = create_mock_agent(AgentRole.BACKEND_DEVELOPER)
    
    orchestrator.register_agent(pm_agent)
    orchestrator.register_agent(dev_agent)
    
    # 通信日志
    communications = []
    
    async def communication_handler(event):
        communications.append({
            "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "from": event.source_agent.value,
            "type": event.event_type.value,
            "message": event.data.get("message", ""),
            "data": event.data
        })
    
    # 订阅通信事件
    orchestrator.event_bus.subscribe("*", communication_handler)
    
    # 模拟智能体间通信
    from agentflow.core.types import AgentEvent, EventType
    
    communications_sequence = [
        {
            "event": AgentEvent(
                event_type=EventType.AGENT_STARTED,
                source_agent=AgentRole.PROJECT_MANAGER,
                data={"message": "项目启动，开始需求分析"}
            ),
            "description": "项目经理启动项目"
        },
        {
            "event": AgentEvent(
                event_type=EventType.TASK_STARTED,
                source_agent=AgentRole.PROJECT_MANAGER,
                data={"task_id": "req_001", "message": "开始需求收集和分析"}
            ),
            "description": "开始需求分析任务"
        },
        {
            "event": AgentEvent(
                event_type=EventType.TASK_COMPLETED,
                source_agent=AgentRole.PROJECT_MANAGER,
                data={"task_id": "req_001", "message": "需求分析完成，准备技术规划"}
            ),
            "description": "需求分析完成"
        },
        {
            "event": AgentEvent(
                event_type=EventType.TASK_STARTED,
                source_agent=AgentRole.BACKEND_DEVELOPER,
                data={"task_id": "dev_001", "message": "收到需求，开始技术评估"}
            ),
            "description": "后端开发者开始技术评估"
        },
        {
            "event": AgentEvent(
                event_type=EventType.AGENT_COMMUNICATION,
                source_agent=AgentRole.BACKEND_DEVELOPER,
                data={
                    "target_agent": "project_manager",
                    "message": "技术评估完成，建议使用FastAPI+PostgreSQL架构",
                    "estimated_time": "2周"
                }
            ),
            "description": "技术方案反馈"
        }
    ]
    
    print(f"📡 模拟智能体通信序列：")
    
    for i, comm in enumerate(communications_sequence, 1):
        print(f"\n{i}. {comm['description']}")
        await orchestrator.event_bus.publish(comm["event"])
        await asyncio.sleep(0.1)  # 模拟处理时间
    
    # 显示通信历史
    print(f"\n📋 通信历史记录：")
    print("-" * 50)
    for comm in communications:
        print(f"[{comm['timestamp']}] {comm['from']}: {comm['message']}")
        if comm.get('data') and len(str(comm['data'])) < 100:
            extra_info = {k: v for k, v in comm['data'].items() if k != 'message'}
            if extra_info:
                print(f"    详情: {extra_info}")
    
    print(f"\n📊 通信统计：")
    print(f"   总通信次数：{len(communications)}")
    print(f"   参与智能体：{len(set(c['from'] for c in communications))}")
    print(f"   事件类型：{len(set(c['type'] for c in communications))}")


if __name__ == "__main__":
    async def main():
        await create_web_project_example()
        await demonstrate_agent_communication()
    
    asyncio.run(main())