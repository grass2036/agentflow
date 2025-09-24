"""
Agent基类
定义所有AI Agent的基础接口和通用功能
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict

from ..core.types import AgentRole, AgentCapability, TechStack, PerformanceMetrics
from ..core.task import Task

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """AI Agent基类"""
    
    def __init__(self, role: AgentRole, capabilities: AgentCapability):
        self.role = role
        self.capabilities = capabilities
        self.agent_id = f"{role.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 任务管理
        self.current_tasks: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.failed_tasks: List[Task] = []
        
        # 性能指标
        self.metrics = PerformanceMetrics()
        
        # 工具和配置
        self.tools: Dict[str, Any] = {}
        self.config: Dict[str, Any] = {}
        
        # 状态管理
        self.is_active = True
        self.last_activity = datetime.now()
        
        logger.info(f"Agent已初始化: {self.role.value} ({self.agent_id})")
    
    @property
    def is_available(self) -> bool:
        """检查Agent是否可用"""
        return (
            self.is_active and
            len(self.current_tasks) < self.capabilities.max_concurrent_tasks
        )
    
    @property
    def current_load(self) -> float:
        """获取当前负载率 (0.0 - 1.0)"""
        if self.capabilities.max_concurrent_tasks == 0:
            return 1.0
        return len(self.current_tasks) / self.capabilities.max_concurrent_tasks
    
    @property
    def success_rate(self) -> float:
        """获取成功率"""
        total_tasks = len(self.completed_tasks) + len(self.failed_tasks)
        if total_tasks == 0:
            return 1.0
        return len(self.completed_tasks) / total_tasks
    
    def can_handle_task(self, task: Task) -> bool:
        """检查是否能处理特定任务"""
        # 检查角色匹配
        if task.agent_role != self.role:
            return False
        
        # 检查是否可用
        if not self.is_available:
            return False
        
        # 检查技术栈支持
        for tech in task.tech_requirements:
            if tech not in self.capabilities.supported_tech_stacks:
                logger.warning(f"Agent {self.role.value} 不支持技术栈: {tech.value}")
                return False
        
        return True
    
    @abstractmethod
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """
        执行任务的抽象方法
        子类必须实现此方法来定义具体的任务执行逻辑
        
        Args:
            task: 要执行的任务
            
        Returns:
            包含执行结果的字典
        """
        pass
    
    async def start_task(self, task: Task) -> bool:
        """开始执行任务"""
        if not self.can_handle_task(task):
            return False
        
        if task.start(self.agent_id):
            self.current_tasks.append(task)
            self.last_activity = datetime.now()
            
            logger.info(f"Agent {self.role.value} 开始执行任务: {task.title}")
            return True
        
        return False
    
    async def complete_task(self, task: Task, result: Dict[str, Any]) -> bool:
        """完成任务"""
        if task in self.current_tasks:
            if task.complete(result):
                self.current_tasks.remove(task)
                self.completed_tasks.append(task)
                
                # 更新性能指标
                self.metrics.tasks_completed += 1
                self._update_performance_metrics(task, True)
                
                logger.info(f"Agent {self.role.value} 完成任务: {task.title}")
                return True
        
        return False
    
    async def fail_task(self, task: Task, error_message: str) -> bool:
        """任务失败"""
        if task in self.current_tasks:
            if task.fail(error_message):
                self.current_tasks.remove(task)
                self.failed_tasks.append(task)
                
                # 更新性能指标
                self.metrics.tasks_failed += 1
                self._update_performance_metrics(task, False)
                
                logger.error(f"Agent {self.role.value} 任务失败: {task.title} - {error_message}")
                return True
        
        return False
    
    def _update_performance_metrics(self, task: Task, success: bool):
        """更新性能指标"""
        if task.duration:
            duration_hours = task.duration.total_seconds() / 3600
            
            # 更新平均完成时间
            total_completed = self.metrics.tasks_completed
            if total_completed > 0:
                current_avg = self.metrics.average_completion_time
                self.metrics.average_completion_time = (
                    (current_avg * (total_completed - 1) + duration_hours) / total_completed
                )
            else:
                self.metrics.average_completion_time = duration_hours
        
        # 更新成功率
        total_tasks = self.metrics.tasks_completed + self.metrics.tasks_failed
        if total_tasks > 0:
            self.metrics.success_rate = self.metrics.tasks_completed / total_tasks
        
        # 更新效率评分
        self._calculate_efficiency_score()
    
    def _calculate_efficiency_score(self):
        """计算效率评分"""
        # 基于成功率和完成时间的综合评分
        success_factor = self.metrics.success_rate
        
        # 时间效率因子（假设目标是每个任务2小时）
        target_time_per_task = 2.0
        time_factor = 1.0
        if self.metrics.average_completion_time > 0:
            time_factor = min(1.0, target_time_per_task / self.metrics.average_completion_time)
        
        # 综合效率评分
        self.metrics.efficiency_score = (success_factor * 0.7 + time_factor * 0.3)
    
    def add_tool(self, tool_name: str, tool: Any) -> bool:
        """添加工具"""
        if tool_name not in self.tools:
            self.tools[tool_name] = tool
            logger.info(f"Agent {self.role.value} 添加工具: {tool_name}")
            return True
        return False
    
    def remove_tool(self, tool_name: str) -> bool:
        """移除工具"""
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"Agent {self.role.value} 移除工具: {tool_name}")
            return True
        return False
    
    def get_tool(self, tool_name: str) -> Optional[Any]:
        """获取工具"""
        return self.tools.get(tool_name)
    
    def configure(self, **config) -> None:
        """配置Agent"""
        self.config.update(config)
        logger.info(f"Agent {self.role.value} 配置已更新")
    
    def get_status(self) -> Dict[str, Any]:
        """获取Agent状态"""
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "is_active": self.is_active,
            "is_available": self.is_available,
            "current_load": self.current_load,
            "current_tasks": len(self.current_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "success_rate": self.success_rate,
            "last_activity": self.last_activity.isoformat(),
            "capabilities": {
                "supported_tech_stacks": [tech.value for tech in self.capabilities.supported_tech_stacks],
                "specialties": self.capabilities.specialties,
                "tools": self.capabilities.tools,
                "max_concurrent_tasks": self.capabilities.max_concurrent_tasks
            },
            "metrics": {
                "tasks_completed": self.metrics.tasks_completed,
                "tasks_failed": self.metrics.tasks_failed,
                "average_completion_time": self.metrics.average_completion_time,
                "success_rate": self.metrics.success_rate,
                "efficiency_score": self.metrics.efficiency_score
            },
            "available_tools": list(self.tools.keys())
        }
    
    def get_task_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取任务历史"""
        all_tasks = self.completed_tasks + self.failed_tasks
        recent_tasks = sorted(all_tasks, key=lambda t: t.created_at, reverse=True)[:limit]
        
        return [
            {
                "task_id": task.task_id,
                "title": task.title,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "duration": str(task.duration) if task.duration else None,
                "tech_requirements": [tech.value for tech in task.tech_requirements]
            }
            for task in recent_tasks
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 检查基本状态
            health_status = "healthy"
            issues = []
            
            # 检查负载
            if self.current_load > 0.9:
                issues.append("高负载")
                health_status = "warning"
            
            # 检查成功率
            if self.success_rate < 0.8:
                issues.append("成功率偏低")
                health_status = "warning"
            
            # 检查最后活动时间
            inactive_hours = (datetime.now() - self.last_activity).total_seconds() / 3600
            if inactive_hours > 24:
                issues.append("长时间无活动")
                health_status = "warning"
            
            return {
                "status": health_status,
                "issues": issues,
                "current_load": self.current_load,
                "success_rate": self.success_rate,
                "inactive_hours": inactive_hours,
                "check_time": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "check_time": datetime.now().isoformat()
            }
    
    def pause(self) -> bool:
        """暂停Agent"""
        if self.is_active:
            self.is_active = False
            logger.info(f"Agent {self.role.value} 已暂停")
            return True
        return False
    
    def resume(self) -> bool:
        """恢复Agent"""
        if not self.is_active:
            self.is_active = True
            self.last_activity = datetime.now()
            logger.info(f"Agent {self.role.value} 已恢复")
            return True
        return False
    
    async def shutdown(self) -> bool:
        """关闭Agent"""
        try:
            # 等待当前任务完成或超时
            if self.current_tasks:
                logger.info(f"Agent {self.role.value} 等待 {len(self.current_tasks)} 个任务完成...")
                timeout = 30  # 30秒超时
                start_time = datetime.now()
                
                while self.current_tasks and (datetime.now() - start_time).total_seconds() < timeout:
                    await asyncio.sleep(1)
                
                # 如果仍有任务在执行，强制失败
                for task in self.current_tasks[:]:
                    await self.fail_task(task, "Agent关闭")
            
            self.is_active = False
            logger.info(f"Agent {self.role.value} 已关闭")
            return True
            
        except Exception as e:
            logger.error(f"Agent {self.role.value} 关闭失败: {e}")
            return False
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(role={self.role.value}, id={self.agent_id})>"

class MockAgent(BaseAgent):
    """模拟Agent，用于测试"""
    
    def __init__(self, role: AgentRole, capabilities: AgentCapability):
        super().__init__(role, capabilities)
        self.execution_delay = 0.1  # 模拟执行时间
    
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """模拟执行任务"""
        logger.info(f"MockAgent {self.role.value} 执行任务: {task.title}")
        
        # 模拟执行时间
        await asyncio.sleep(self.execution_delay)
        
        # 生成模拟结果
        result = {
            "status": "completed",
            "agent_role": self.role.value,
            "task_id": task.task_id,
            "execution_time": self.execution_delay,
            "output": f"模拟完成任务: {task.title}",
            "mock": True,
            "tech_used": [tech.value for tech in task.tech_requirements],
            "timestamp": datetime.now().isoformat()
        }
        
        # 根据Agent角色生成特定内容
        if self.role == AgentRole.PROJECT_MANAGER:
            result["deliverables"] = {
                "project_plan": "详细项目计划",
                "timeline": "4周开发周期",
                "risk_assessment": "中等风险"
            }
        
        elif self.role == AgentRole.ARCHITECT:
            result["deliverables"] = {
                "architecture_design": "微服务架构",
                "tech_stack_recommendations": task.tech_requirements,
                "scalability_plan": "水平扩展方案"
            }
        
        elif self.role == AgentRole.BACKEND_DEVELOPER:
            result["deliverables"] = {
                "api_endpoints": ["/api/users", "/api/auth"],
                "database_schema": "用户表设计",
                "code_files": ["main.py", "models.py", "routes.py"]
            }
        
        elif self.role == AgentRole.FRONTEND_DEVELOPER:
            result["deliverables"] = {
                "components": ["UserCard.vue", "Dashboard.vue"],
                "pages": ["Home", "Profile", "Settings"],
                "styling": "Vuetify主题"
            }
        
        elif self.role == AgentRole.QA_ENGINEER:
            result["deliverables"] = {
                "test_cases": 25,
                "coverage": "92%",
                "test_reports": "所有测试通过"
            }
        
        return result

# 便捷函数
def create_mock_agent(role: AgentRole, max_concurrent_tasks: int = 3) -> MockAgent:
    """创建模拟Agent"""
    from ..core.types import get_agent_capability
    
    capability = get_agent_capability(role)
    capability.max_concurrent_tasks = max_concurrent_tasks
    
    return MockAgent(role, capability)