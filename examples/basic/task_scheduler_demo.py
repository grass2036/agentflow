#!/usr/bin/env python3
"""
基础示例：任务调度器演示
========================

这个示例展示了AgentFlow的任务调度和依赖管理功能。

运行方式：
python3 examples/basic/task_scheduler_demo.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentflow.core.orchestrator import TaskScheduler
from agentflow.core.task import create_task
from agentflow.core.types import AgentRole, TaskPriority


async def main():
    """任务调度演示"""
    print("🌊 AgentFlow 任务调度器演示")
    print("=" * 50)
    
    # 创建任务调度器
    scheduler = TaskScheduler()
    
    # 创建一系列相关任务
    tasks = []
    
    # 1. 需求分析任务（最高优先级，无依赖）
    task1 = create_task(
        title="项目需求分析",
        description="分析项目需求和目标",
        agent_role=AgentRole.PROJECT_MANAGER,
        priority=TaskPriority.CRITICAL,
        estimated_hours=4
    )
    tasks.append(task1)
    
    # 2. 架构设计任务（依赖需求分析）
    task2 = create_task(
        title="系统架构设计",
        description="设计系统整体架构",
        agent_role=AgentRole.ARCHITECT,
        priority=TaskPriority.HIGH,
        dependencies=[task1.task_id],
        estimated_hours=8
    )
    tasks.append(task2)
    
    # 3. 数据库设计任务（依赖架构设计）
    task3 = create_task(
        title="数据库设计",
        description="设计数据库结构",
        agent_role=AgentRole.BACKEND_DEVELOPER,
        priority=TaskPriority.HIGH,
        dependencies=[task2.task_id],
        estimated_hours=6
    )
    tasks.append(task3)
    
    # 4. 前端界面设计（依赖架构设计）
    task4 = create_task(
        title="前端界面设计",
        description="设计用户界面",
        agent_role=AgentRole.FRONTEND_DEVELOPER,
        priority=TaskPriority.MEDIUM,
        dependencies=[task2.task_id],
        estimated_hours=10
    )
    tasks.append(task4)
    
    # 5. 后端API开发（依赖数据库设计）
    task5 = create_task(
        title="后端API开发",
        description="开发后端API接口",
        agent_role=AgentRole.BACKEND_DEVELOPER,
        priority=TaskPriority.HIGH,
        dependencies=[task3.task_id],
        estimated_hours=16
    )
    tasks.append(task5)
    
    # 6. 前端功能开发（依赖界面设计和API开发）
    task6 = create_task(
        title="前端功能开发",
        description="实现前端功能",
        agent_role=AgentRole.FRONTEND_DEVELOPER,
        priority=TaskPriority.MEDIUM,
        dependencies=[task4.task_id, task5.task_id],
        estimated_hours=12
    )
    tasks.append(task6)
    
    # 7. 测试任务（依赖所有开发任务）
    task7 = create_task(
        title="系统测试",
        description="进行系统集成测试",
        agent_role=AgentRole.QA_ENGINEER,
        priority=TaskPriority.MEDIUM,
        dependencies=[task5.task_id, task6.task_id],
        estimated_hours=8
    )
    tasks.append(task7)
    
    # 将所有任务添加到调度器
    print("📋 添加任务到调度器：")
    for i, task in enumerate(tasks, 1):
        scheduler.add_task(task)
        deps = f"依赖：{task.dependencies}" if task.dependencies else "无依赖"
        print(f"   {i}. {task.title} ({task.priority.name}优先级, {deps})")
    
    print(f"\n📊 初始调度统计：")
    stats = scheduler.get_schedule_stats()
    print(f"   总任务数：{stats['total_tasks']}")
    print(f"   状态分布：{stats['status_distribution']}")
    
    # 模拟任务执行过程
    print("\n🚀 开始模拟任务执行：")
    print("-" * 30)
    
    completed_tasks = set()
    round_number = 1
    
    while completed_tasks != {t.task_id for t in tasks}:
        print(f"\n第 {round_number} 轮执行：")
        
        # 获取可执行的任务
        ready_tasks = scheduler.get_ready_tasks(completed_tasks)
        
        if not ready_tasks:
            print("   没有可执行的任务")
            break
        
        print(f"   可执行任务：{len(ready_tasks)} 个")
        
        # 模拟执行每个可执行任务
        for task in ready_tasks:
            # 分配任务
            scheduler.assign_task(task, f"agent_{task.agent_role.value}")
            print(f"   ✓ 开始执行：{task.title} (分配给 {task.agent_role.value})")
            
            # 模拟任务完成
            result = {
                "status": "completed",
                "output": f"{task.title} 执行完成",
                "duration": f"{task.estimated_hours}小时"
            }
            
            scheduler.complete_task(task, result)
            completed_tasks.add(task.task_id)
            print(f"   ✅ 完成：{task.title}")
        
        round_number += 1
    
    # 显示最终统计
    print("\n" + "=" * 50)
    print("🎯 执行完成！最终统计：")
    final_stats = scheduler.get_schedule_stats()
    print(f"   总任务数：{final_stats['total_tasks']}")
    print(f"   已完成：{final_stats['status_distribution'].get('completed', 0)}")
    print(f"   执行轮数：{round_number - 1}")
    print(f"   成功率：100%")
    
    # 显示任务执行顺序
    print("\n📋 任务执行顺序：")
    for i, task in enumerate(tasks, 1):
        deps_info = ""
        if task.dependencies:
            dep_titles = [t.title for t in tasks if t.task_id in task.dependencies]
            deps_info = f" (等待：{', '.join(dep_titles)})"
        print(f"   {i}. {task.title}{deps_info}")


if __name__ == "__main__":
    asyncio.run(main())