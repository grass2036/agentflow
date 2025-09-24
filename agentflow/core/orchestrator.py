"""
AI Agent协调器核心
负责管理多个AI Agent的协作，任务分解，调度和监控
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from collections import defaultdict
import uuid

from .types import (
    AgentRole, TechStack, TaskPriority, TaskStatus, ProjectConfig, 
    AgentEvent, EventType, PerformanceMetrics, PlatformType, ProjectComplexity
)
from .task import Task, TaskBuilder, TaskQuery, create_task

logger = logging.getLogger(__name__)

class TaskScheduler:
    """智能任务调度器"""
    
    def __init__(self):
        self.task_queue: List[Task] = []
        self.agent_loads: Dict[AgentRole, int] = defaultdict(int)
        self.max_concurrent_tasks = 3
    
    def add_task(self, task: Task) -> bool:
        """添加任务到调度队列"""
        if task not in self.task_queue:
            self.task_queue.append(task)
            logger.info(f"任务已添加到调度队列: {task.title}")
            return True
        return False
    
    def get_ready_tasks(self, completed_task_ids: set = None) -> List[Task]:
        """获取可执行的任务"""
        completed_task_ids = completed_task_ids or set()
        ready_tasks = []
        
        for task in self.task_queue:
            if task.status == TaskStatus.PENDING:
                # 检查依赖是否完成
                dependencies_met = all(
                    dep_id in completed_task_ids 
                    for dep_id in task.dependencies
                )
                
                # 检查Agent负载
                agent_available = (
                    self.agent_loads[task.agent_role] < self.max_concurrent_tasks
                )
                
                if dependencies_met and agent_available:
                    task.status = TaskStatus.READY
                    ready_tasks.append(task)
        
        # 按优先级排序
        ready_tasks.sort(key=lambda t: t.priority.value, reverse=True)
        return ready_tasks
    
    def assign_task(self, task: Task, agent_id: str = None) -> bool:
        """分配任务给Agent"""
        if task.start(agent_id):
            self.agent_loads[task.agent_role] += 1
            logger.info(f"任务已分配: {task.title} -> {task.agent_role.value}")
            return True
        return False
    
    def complete_task(self, task: Task, result: Dict[str, Any] = None) -> bool:
        """标记任务完成"""
        if task.complete(result):
            self.agent_loads[task.agent_role] = max(0, self.agent_loads[task.agent_role] - 1)
            logger.info(f"任务已完成: {task.title}")
            return True
        return False
    
    def get_schedule_stats(self) -> Dict[str, Any]:
        """获取调度统计信息"""
        status_counts = defaultdict(int)
        for task in self.task_queue:
            status_counts[task.status.value] += 1
        
        return {
            "total_tasks": len(self.task_queue),
            "status_distribution": dict(status_counts),
            "agent_loads": dict(self.agent_loads),
            "ready_tasks": len([t for t in self.task_queue if t.status == TaskStatus.READY])
        }

class EventBus:
    """事件总线"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.event_history: List[AgentEvent] = []
        self.max_history = 1000
    
    def subscribe(self, event_pattern: str, callback: Callable):
        """订阅事件"""
        self.subscribers[event_pattern].append(callback)
        logger.info(f"事件订阅: {event_pattern}")
    
    async def publish(self, event: AgentEvent):
        """发布事件"""
        self.event_history.append(event)
        
        # 保持历史记录大小
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
        
        # 通知订阅者
        patterns_to_notify = []
        
        # 检查精确匹配
        event_type = event.event_type.value
        if event_type in self.subscribers:
            patterns_to_notify.append(event_type)
        
        # 检查通配符匹配
        if "*" in self.subscribers:
            patterns_to_notify.append("*")
        
        # 检查前缀匹配 (如 "task_*")
        for pattern in self.subscribers.keys():
            if pattern.endswith("*") and event_type.startswith(pattern[:-1]):
                patterns_to_notify.append(pattern)
        
        # 异步通知所有匹配的订阅者
        for pattern in patterns_to_notify:
            for callback in self.subscribers[pattern]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    logger.error(f"事件处理失败 {pattern}: {e}")
    
    def get_recent_events(self, count: int = 10) -> List[AgentEvent]:
        """获取最近的事件"""
        return self.event_history[-count:]

class AgentOrchestrator:
    """AI Agent协调器主类"""
    
    def __init__(self, use_openrouter: bool = False, prefer_free_models: bool = False):
        self.agents: Dict[AgentRole, Any] = {}
        self.scheduler = TaskScheduler()
        self.event_bus = EventBus()
        
        # AI Provider配置
        self.use_openrouter = use_openrouter
        self.prefer_free_models = prefer_free_models
        
        # 会话管理
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.active_sessions: set = set()
        
        # 性能指标
        self.metrics = PerformanceMetrics()
        
        # 项目模板
        self.project_templates = self._init_project_templates()
        
        # 初始化Agent团队
        if use_openrouter:
            self._init_openrouter_agents()
        
        logger.info(f"AI Agent协调器已初始化 (OpenRouter: {use_openrouter}, Free Models: {prefer_free_models})")
    
    def _init_openrouter_agents(self):
        """初始化OpenRouter Agent团队"""
        try:
            from ..agents.openrouter_agent import create_openrouter_agent_team
            
            openrouter_agents = create_openrouter_agent_team(prefer_free=self.prefer_free_models)
            
            for role, agent in openrouter_agents.items():
                self.agents[role] = agent
            
            logger.info(f"已初始化 {len(openrouter_agents)} 个OpenRouter Agents")
        except Exception as e:
            logger.error(f"OpenRouter Agents初始化失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _init_project_templates(self) -> Dict[str, Dict[str, Any]]:
        """初始化项目模板"""
        return {
            "web_app": {
                "name": "Web应用",
                "tech_stack": [TechStack.PYTHON_FASTAPI, TechStack.VUE_JS, TechStack.POSTGRESQL],
                "tasks": [
                    "需求分析和规划",
                    "系统架构设计",
                    "数据库设计", 
                    "后端API开发",
                    "前端界面开发",
                    "集成测试",
                    "部署配置"
                ]
            },
            "mobile_app": {
                "name": "移动应用",
                "tech_stack": [TechStack.FLUTTER, TechStack.PYTHON_FASTAPI],
                "tasks": [
                    "需求分析和规划",
                    "UI/UX设计",
                    "后端API开发",
                    "移动端开发",
                    "测试和调试",
                    "发布准备"
                ]
            },
            "microservice": {
                "name": "微服务架构",
                "tech_stack": [TechStack.NODEJS_EXPRESS, TechStack.DOCKER, TechStack.KUBERNETES],
                "tasks": [
                    "架构设计",
                    "服务拆分",
                    "API网关开发",
                    "服务间通信",
                    "数据一致性",
                    "监控和日志",
                    "容器化部署"
                ]
            }
        }
    
    def register_agent(self, agent: Any) -> bool:
        """注册Agent"""
        if hasattr(agent, 'role') and isinstance(agent.role, AgentRole):
            self.agents[agent.role] = agent
            logger.info(f"Agent已注册: {agent.role.value}")
            return True
        return False
    
    def decompose_project(self, config: ProjectConfig) -> List[Task]:
        """智能项目分解"""
        tasks = []
        task_counter = 1
        
        # 基于项目配置生成基础任务
        base_tasks = [
            ("项目需求分析", AgentRole.PROJECT_MANAGER, 4, TaskPriority.HIGH),
            ("系统架构设计", AgentRole.ARCHITECT, 8, TaskPriority.HIGH),
        ]
        
        # 根据技术栈添加开发任务
        backend_techs = [tech for tech in config.tech_stack 
                        if any(x in tech.value for x in ["python", "nodejs", "java", "go", "csharp", "php"])]
        if backend_techs:
            base_tasks.extend([
                ("后端服务开发", AgentRole.BACKEND_DEVELOPER, 16, TaskPriority.MEDIUM),
                ("数据库设计实现", AgentRole.BACKEND_DEVELOPER, 8, TaskPriority.MEDIUM),
                ("API接口开发", AgentRole.BACKEND_DEVELOPER, 12, TaskPriority.MEDIUM),
            ])
        
        frontend_techs = [tech for tech in config.tech_stack 
                         if any(x in tech.value for x in ["vue", "react", "angular", "svelte"])]
        if frontend_techs:
            base_tasks.extend([
                ("前端界面开发", AgentRole.FRONTEND_DEVELOPER, 12, TaskPriority.MEDIUM),
                ("用户交互实现", AgentRole.FRONTEND_DEVELOPER, 8, TaskPriority.MEDIUM),
            ])
        
        mobile_techs = [tech for tech in config.tech_stack 
                       if any(x in tech.value for x in ["flutter", "react_native"])]
        if mobile_techs:
            base_tasks.append(("移动端开发", AgentRole.FRONTEND_DEVELOPER, 20, TaskPriority.MEDIUM))
        
        # 添加QA和DevOps任务
        base_tasks.extend([
            ("测试方案设计", AgentRole.QA_ENGINEER, 6, TaskPriority.LOW),
            ("自动化测试", AgentRole.QA_ENGINEER, 8, TaskPriority.LOW),
        ])
        
        # 根据复杂度调整
        complexity_multiplier = {
            ProjectComplexity.SIMPLE: 0.8,
            ProjectComplexity.MEDIUM: 1.0,
            ProjectComplexity.COMPLEX: 1.5,
            ProjectComplexity.ENTERPRISE: 2.0
        }.get(config.complexity, 1.0)
        
        # 生成Task对象
        for title, role, base_hours, priority in base_tasks:
            estimated_hours = max(1, int(base_hours * complexity_multiplier))
            
            task = create_task(
                title=f"{config.name} - {title}",
                description=f"为项目 '{config.name}' 执行 {title}",
                agent_role=role,
                tech_requirements=config.tech_stack,
                priority=priority,
                estimated_hours=estimated_hours
            )
            
            task.context.update({
                "project_name": config.name,
                "project_description": config.description,
                "target_platform": config.target_platform.value,
                "complexity": config.complexity.value,
                "requirements": config.requirements
            })
            
            tasks.append(task)
            task_counter += 1
        
        # 设置任务依赖关系
        if len(tasks) >= 2:
            # 架构设计依赖需求分析
            tasks[1].add_dependency(tasks[0].task_id)
            
            # 开发任务依赖架构设计
            for i in range(2, len(tasks) - 2):  # 排除测试任务
                tasks[i].add_dependency(tasks[1].task_id)
            
            # 测试任务依赖开发任务
            for i in range(len(tasks) - 2, len(tasks)):
                for j in range(2, len(tasks) - 2):
                    tasks[i].add_dependency(tasks[j].task_id)
        
        return tasks
    
    async def execute_project(self, config: ProjectConfig) -> Dict[str, Any]:
        """执行项目"""
        logger.info(f"开始执行项目: {config.name}")
        
        # 创建会话
        session_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        session_info = {
            "session_id": session_id,
            "project_config": config,
            "start_time": start_time,
            "status": "executing",
            "tasks": [],
            "results": {}
        }
        
        self.sessions[session_id] = session_info
        self.active_sessions.add(session_id)
        
        # 发布项目开始事件
        await self.event_bus.publish(AgentEvent(
            event_type=EventType.PROJECT_STARTED,
            source_agent=AgentRole.PROJECT_MANAGER,
            data={"project_name": config.name, "session_id": session_id},
            session_id=session_id
        ))
        
        try:
            # 分解项目任务
            tasks = self.decompose_project(config)
            session_info["tasks"] = [task.task_id for task in tasks]
            
            # 添加任务到调度器
            for task in tasks:
                self.scheduler.add_task(task)
            
            # 执行任务
            completed_tasks = []
            max_iterations = 20  # 防止无限循环
            
            for iteration in range(max_iterations):
                # 获取可执行任务
                completed_task_ids = {task.task_id for task in completed_tasks}
                ready_tasks = self.scheduler.get_ready_tasks(completed_task_ids)
                
                if not ready_tasks:
                    logger.info("没有更多可执行任务")
                    break
                
                logger.info(f"第 {iteration + 1} 轮执行，{len(ready_tasks)} 个任务可执行")
                
                # 并行执行任务
                execution_results = await self._execute_tasks_parallel(ready_tasks)
                
                # 处理执行结果
                for task, success, result in execution_results:
                    if success:
                        self.scheduler.complete_task(task, result)
                        completed_tasks.append(task)
                        
                        # 发布任务完成事件
                        await self.event_bus.publish(AgentEvent(
                            event_type=EventType.TASK_COMPLETED,
                            source_agent=task.agent_role,
                            data={"task_id": task.task_id, "result": result},
                            session_id=session_id
                        ))
                    else:
                        task.fail(result.get("error", "执行失败"))
                        logger.error(f"任务执行失败: {task.title}")
                
                # 检查是否所有任务都完成
                if len(completed_tasks) >= len([t for t in tasks if t.status != TaskStatus.CANCELLED]):
                    break
            
            # 项目完成
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            session_info.update({
                "status": "completed",
                "end_time": end_time,
                "execution_time": execution_time,
                "completed_tasks": len(completed_tasks),
                "total_tasks": len(tasks)
            })
            
            self.active_sessions.discard(session_id)
            
            # 更新指标
            self.metrics.tasks_completed += len(completed_tasks)
            success_rate = len(completed_tasks) / len(tasks) if tasks else 0
            
            # 发布项目完成事件
            await self.event_bus.publish(AgentEvent(
                event_type=EventType.PROJECT_COMPLETED,
                source_agent=AgentRole.PROJECT_MANAGER,
                data={
                    "project_name": config.name,
                    "success_rate": success_rate,
                    "execution_time": execution_time
                },
                session_id=session_id
            ))
            
            return {
                "success": True,
                "session_id": session_id,
                "project_name": config.name,
                "execution_time": f"{execution_time:.2f}秒",
                "tasks_completed": len(completed_tasks),
                "total_tasks": len(tasks),
                "success_rate": f"{success_rate:.1%}",
                "deliverables": self._generate_deliverables(completed_tasks)
            }
            
        except Exception as e:
            logger.error(f"项目执行失败: {e}")
            session_info.update({
                "status": "failed",
                "error": str(e),
                "end_time": datetime.now()
            })
            self.active_sessions.discard(session_id)
            
            return {
                "success": False,
                "session_id": session_id,
                "error": str(e)
            }
    
    async def _execute_tasks_parallel(self, tasks: List[Task]) -> List[tuple]:
        """并行执行任务"""
        results = []
        
        # 限制并发数量
        max_concurrent = min(len(tasks), 5)
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_single_task(task: Task):
            async with semaphore:
                try:
                    # 分配任务
                    self.scheduler.assign_task(task)
                    
                    # 模拟任务执行（实际应该调用对应的Agent）
                    agent = self.agents.get(task.agent_role)
                    if agent and hasattr(agent, 'execute_task'):
                        result = await agent.execute_task(task)
                    else:
                        # 模拟执行
                        await asyncio.sleep(0.1)
                        result = {"status": "completed", "output": f"模拟完成 {task.title}"}
                    
                    return (task, True, result)
                
                except Exception as e:
                    logger.error(f"任务执行异常 {task.title}: {e}")
                    return (task, False, {"error": str(e)})
        
        # 并行执行所有任务
        task_coroutines = [execute_single_task(task) for task in tasks]
        results = await asyncio.gather(*task_coroutines)
        
        return results
    
    def _generate_deliverables(self, completed_tasks: List[Task]) -> Dict[str, Any]:
        """生成项目交付物"""
        deliverables = {
            "documents": [],
            "code_artifacts": [],
            "test_reports": [],
            "deployment_configs": []
        }
        
        for task in completed_tasks:
            result = task.result
            
            if task.agent_role == AgentRole.PROJECT_MANAGER:
                deliverables["documents"].append({
                    "type": "项目规划文档",
                    "task_id": task.task_id,
                    "content": result
                })
            
            elif task.agent_role == AgentRole.ARCHITECT:
                deliverables["documents"].append({
                    "type": "系统架构文档",
                    "task_id": task.task_id,
                    "content": result
                })
            
            elif task.agent_role in [AgentRole.BACKEND_DEVELOPER, AgentRole.FRONTEND_DEVELOPER]:
                deliverables["code_artifacts"].append({
                    "type": f"{task.agent_role.value}代码",
                    "task_id": task.task_id,
                    "content": result
                })
            
            elif task.agent_role == AgentRole.QA_ENGINEER:
                deliverables["test_reports"].append({
                    "type": "测试报告",
                    "task_id": task.task_id,
                    "content": result
                })
        
        return deliverables
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """获取会话状态"""
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "会话不存在"}
        
        # 获取任务状态统计
        task_stats = self.scheduler.get_schedule_stats()
        
        return {
            "session_id": session_id,
            "status": session["status"],
            "project_name": session["project_config"].name,
            "start_time": session["start_time"].isoformat(),
            "task_statistics": task_stats,
            "recent_events": [event.to_dict() for event in self.event_bus.get_recent_events(5)]
        }
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """获取协调器状态"""
        return {
            "active_sessions": len(self.active_sessions),
            "total_sessions": len(self.sessions),
            "registered_agents": len(self.agents),
            "metrics": {
                "tasks_completed": self.metrics.tasks_completed,
                "tasks_failed": self.metrics.tasks_failed,
                "success_rate": self.metrics.success_rate,
                "average_completion_time": self.metrics.average_completion_time
            },
            "scheduler_stats": self.scheduler.get_schedule_stats(),
            "recent_events": len(self.event_bus.event_history)
        }
    
    def list_project_templates(self) -> Dict[str, Any]:
        """列出可用的项目模板"""
        return {
            template_id: {
                "name": template["name"],
                "tech_stack": [tech.value for tech in template["tech_stack"]],
                "estimated_tasks": len(template["tasks"])
            }
            for template_id, template in self.project_templates.items()
        }
    
    async def stop_session(self, session_id: str) -> bool:
        """停止会话"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session["status"] = "stopped"
            session["end_time"] = datetime.now()
            self.active_sessions.discard(session_id)
            
            await self.event_bus.publish(AgentEvent(
                event_type=EventType.SYSTEM_ALERT,
                source_agent=AgentRole.PROJECT_MANAGER,
                data={"message": f"会话 {session_id} 已停止"},
                session_id=session_id
            ))
            
            return True
        return False
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """获取所有Agent的统计信息"""
        stats = {}
        total_cost = 0.0
        total_tokens = 0
        
        for role, agent in self.agents.items():
            if hasattr(agent, 'get_agent_stats'):
                agent_stats = agent.get_agent_stats()
                stats[role.value] = agent_stats
                total_cost += agent_stats.get('total_cost_usd', 0)
                total_tokens += agent_stats.get('total_tokens_used', 0)
        
        return {
            "individual_agents": stats,
            "summary": {
                "total_agents": len(self.agents),
                "total_cost_usd": round(total_cost, 6),
                "total_tokens_used": total_tokens,
                "using_openrouter": self.use_openrouter,
                "prefer_free_models": self.prefer_free_models
            }
        }
    
    def switch_to_free_models(self, enable: bool = True):
        """切换所有Agent到免费模型模式"""
        self.prefer_free_models = enable
        
        for agent in self.agents.values():
            if hasattr(agent, 'switch_to_free_models'):
                agent.switch_to_free_models(enable)
        
        logger.info(f"All agents switched to free models: {enable}")
    
    def test_all_agent_connections(self) -> Dict[str, Any]:
        """测试所有Agent的连接"""
        results = {}
        
        for role, agent in self.agents.items():
            if hasattr(agent, 'test_connection'):
                try:
                    result = agent.test_connection()
                    results[role.value] = result
                except Exception as e:
                    results[role.value] = {
                        "success": False,
                        "error": str(e)
                    }
            else:
                results[role.value] = {
                    "success": False,
                    "error": "Agent does not support connection testing"
                }
        
        return results