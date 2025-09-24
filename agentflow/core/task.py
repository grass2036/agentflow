"""
任务核心类
定义AI Agent系统中的任务对象和相关操作
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field

from .types import (
    AgentRole, TechStack, TaskPriority, TaskStatus, 
    TaskDependency, PerformanceMetrics
)

@dataclass
class Task:
    """任务定义"""
    # 基本信息
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    
    # 分配信息
    agent_role: AgentRole = AgentRole.PROJECT_MANAGER
    assigned_agent_id: Optional[str] = None
    
    # 技术要求
    tech_requirements: List[TechStack] = field(default_factory=list)
    
    # 优先级和状态
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    
    # 依赖关系
    dependencies: List[str] = field(default_factory=list)
    blocks: List[str] = field(default_factory=list)  # 此任务阻塞的其他任务
    
    # 时间信息
    estimated_hours: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    
    # 执行信息
    context: Dict[str, Any] = field(default_factory=dict)
    result: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    # 元数据
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.title:
            self.title = f"Task {self.task_id[:8]}"
        
        # 设置默认截止时间（创建后24小时）
        if not self.deadline:
            self.deadline = self.created_at + timedelta(hours=24)
    
    @property
    def is_ready(self) -> bool:
        """检查任务是否可以开始执行"""
        return (
            self.status == TaskStatus.PENDING and
            all(dep in self._completed_dependencies for dep in self.dependencies)
        )
    
    @property
    def is_overdue(self) -> bool:
        """检查任务是否过期"""
        if self.deadline and self.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            return datetime.now() > self.deadline
        return False
    
    @property
    def duration(self) -> Optional[timedelta]:
        """获取任务执行时长"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return datetime.now() - self.started_at
        return None
    
    @property
    def progress(self) -> float:
        """获取任务进度 (0.0 - 1.0)"""
        status_progress = {
            TaskStatus.PENDING: 0.0,
            TaskStatus.READY: 0.1,
            TaskStatus.IN_PROGRESS: 0.5,
            TaskStatus.COMPLETED: 1.0,
            TaskStatus.FAILED: 0.0,
            TaskStatus.BLOCKED: 0.2,
            TaskStatus.CANCELLED: 0.0
        }
        return status_progress.get(self.status, 0.0)
    
    def start(self, agent_id: Optional[str] = None) -> bool:
        """开始执行任务"""
        if self.status != TaskStatus.PENDING:
            return False
        
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()
        
        if agent_id:
            self.assigned_agent_id = agent_id
        
        return True
    
    def complete(self, result: Optional[Dict[str, Any]] = None) -> bool:
        """完成任务"""
        if self.status != TaskStatus.IN_PROGRESS:
            return False
        
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        
        if result:
            self.result.update(result)
        
        return True
    
    def fail(self, error_message: str) -> bool:
        """任务失败"""
        if self.status not in [TaskStatus.IN_PROGRESS, TaskStatus.READY]:
            return False
        
        self.status = TaskStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.now()
        
        return True
    
    def block(self, reason: str) -> bool:
        """阻塞任务"""
        if self.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED, TaskStatus.FAILED]:
            return False
        
        self.status = TaskStatus.BLOCKED
        self.context["block_reason"] = reason
        
        return True
    
    def unblock(self) -> bool:
        """解除阻塞"""
        if self.status != TaskStatus.BLOCKED:
            return False
        
        self.status = TaskStatus.READY if self.is_ready else TaskStatus.PENDING
        self.context.pop("block_reason", None)
        
        return True
    
    def cancel(self, reason: str = "") -> bool:
        """取消任务"""
        if self.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            return False
        
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now()
        
        if reason:
            self.context["cancel_reason"] = reason
        
        return True
    
    def add_dependency(self, task_id: str) -> bool:
        """添加依赖任务"""
        if task_id not in self.dependencies and task_id != self.task_id:
            self.dependencies.append(task_id)
            return True
        return False
    
    def remove_dependency(self, task_id: str) -> bool:
        """移除依赖任务"""
        if task_id in self.dependencies:
            self.dependencies.remove(task_id)
            return True
        return False
    
    def add_tag(self, tag: str) -> bool:
        """添加标签"""
        if tag not in self.tags:
            self.tags.add(tag)
            return True
        return False
    
    def remove_tag(self, tag: str) -> bool:
        """移除标签"""
        if tag in self.tags:
            self.tags.remove(tag)
            return True
        return False
    
    def update_context(self, **kwargs) -> None:
        """更新上下文信息"""
        self.context.update(kwargs)
    
    def update_result(self, **kwargs) -> None:
        """更新结果信息"""
        self.result.update(kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "agent_role": self.agent_role.value,
            "assigned_agent_id": self.assigned_agent_id,
            "tech_requirements": [tech.value for tech in self.tech_requirements],
            "priority": self.priority.value,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "blocks": self.blocks,
            "estimated_hours": self.estimated_hours,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "context": self.context,
            "result": self.result,
            "error_message": self.error_message,
            "tags": list(self.tags),
            "metadata": self.metadata,
            "progress": self.progress,
            "is_ready": self.is_ready,
            "is_overdue": self.is_overdue,
            "duration": str(self.duration) if self.duration else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """从字典创建Task对象"""
        task = cls(
            task_id=data.get("task_id", str(uuid.uuid4())),
            title=data.get("title", ""),
            description=data.get("description", ""),
            agent_role=AgentRole(data.get("agent_role", AgentRole.PROJECT_MANAGER.value)),
            assigned_agent_id=data.get("assigned_agent_id"),
            tech_requirements=[TechStack(tech) for tech in data.get("tech_requirements", [])],
            priority=TaskPriority(data.get("priority", TaskPriority.MEDIUM.value)),
            status=TaskStatus(data.get("status", TaskStatus.PENDING.value)),
            dependencies=data.get("dependencies", []),
            blocks=data.get("blocks", []),
            estimated_hours=data.get("estimated_hours", 1),
            context=data.get("context", {}),
            result=data.get("result", {}),
            error_message=data.get("error_message"),
            tags=set(data.get("tags", [])),
            metadata=data.get("metadata", {})
        )
        
        # 处理时间字段
        if data.get("created_at"):
            task.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("started_at"):
            task.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            task.completed_at = datetime.fromisoformat(data["completed_at"])
        if data.get("deadline"):
            task.deadline = datetime.fromisoformat(data["deadline"])
        
        return task

class TaskBuilder:
    """任务构建器"""
    
    def __init__(self):
        self.task_data = {}
    
    def with_title(self, title: str) -> 'TaskBuilder':
        self.task_data["title"] = title
        return self
    
    def with_description(self, description: str) -> 'TaskBuilder':
        self.task_data["description"] = description
        return self
    
    def with_agent(self, agent_role: AgentRole) -> 'TaskBuilder':
        self.task_data["agent_role"] = agent_role
        return self
    
    def with_tech(self, *tech_stacks: TechStack) -> 'TaskBuilder':
        self.task_data["tech_requirements"] = list(tech_stacks)
        return self
    
    def with_priority(self, priority: TaskPriority) -> 'TaskBuilder':
        self.task_data["priority"] = priority
        return self
    
    def with_dependencies(self, *task_ids: str) -> 'TaskBuilder':
        self.task_data["dependencies"] = list(task_ids)
        return self
    
    def with_estimated_hours(self, hours: int) -> 'TaskBuilder':
        self.task_data["estimated_hours"] = hours
        return self
    
    def with_deadline(self, deadline: datetime) -> 'TaskBuilder':
        self.task_data["deadline"] = deadline
        return self
    
    def with_context(self, **context) -> 'TaskBuilder':
        self.task_data["context"] = context
        return self
    
    def with_tags(self, *tags: str) -> 'TaskBuilder':
        self.task_data["tags"] = set(tags)
        return self
    
    def build(self) -> Task:
        """构建Task对象"""
        return Task(**self.task_data)

class TaskQuery:
    """任务查询器"""
    
    def __init__(self, tasks: List[Task]):
        self.tasks = tasks
    
    def by_status(self, status: TaskStatus) -> 'TaskQuery':
        """按状态筛选"""
        self.tasks = [task for task in self.tasks if task.status == status]
        return self
    
    def by_agent(self, agent_role: AgentRole) -> 'TaskQuery':
        """按Agent角色筛选"""
        self.tasks = [task for task in self.tasks if task.agent_role == agent_role]
        return self
    
    def by_priority(self, priority: TaskPriority) -> 'TaskQuery':
        """按优先级筛选"""
        self.tasks = [task for task in self.tasks if task.priority == priority]
        return self
    
    def by_tech(self, tech_stack: TechStack) -> 'TaskQuery':
        """按技术栈筛选"""
        self.tasks = [task for task in self.tasks if tech_stack in task.tech_requirements]
        return self
    
    def by_tag(self, tag: str) -> 'TaskQuery':
        """按标签筛选"""
        self.tasks = [task for task in self.tasks if tag in task.tags]
        return self
    
    def ready_to_execute(self) -> 'TaskQuery':
        """获取可执行的任务"""
        self.tasks = [task for task in self.tasks if task.is_ready]
        return self
    
    def overdue(self) -> 'TaskQuery':
        """获取过期任务"""
        self.tasks = [task for task in self.tasks if task.is_overdue]
        return self
    
    def sort_by_priority(self, reverse: bool = True) -> 'TaskQuery':
        """按优先级排序"""
        self.tasks.sort(key=lambda t: t.priority.value, reverse=reverse)
        return self
    
    def sort_by_created(self, reverse: bool = False) -> 'TaskQuery':
        """按创建时间排序"""
        self.tasks.sort(key=lambda t: t.created_at, reverse=reverse)
        return self
    
    def limit(self, count: int) -> 'TaskQuery':
        """限制返回数量"""
        self.tasks = self.tasks[:count]
        return self
    
    def all(self) -> List[Task]:
        """返回所有任务"""
        return self.tasks
    
    def first(self) -> Optional[Task]:
        """返回第一个任务"""
        return self.tasks[0] if self.tasks else None
    
    def count(self) -> int:
        """返回任务数量"""
        return len(self.tasks)

# 便捷函数
def create_task(
    title: str,
    description: str = "",
    agent_role: AgentRole = AgentRole.PROJECT_MANAGER,
    tech_requirements: Optional[List[TechStack]] = None,
    priority: TaskPriority = TaskPriority.MEDIUM,
    estimated_hours: int = 1,
    dependencies: Optional[List[str]] = None
) -> Task:
    """创建任务的便捷函数"""
    return TaskBuilder() \
        .with_title(title) \
        .with_description(description) \
        .with_agent(agent_role) \
        .with_tech(*(tech_requirements or [])) \
        .with_priority(priority) \
        .with_estimated_hours(estimated_hours) \
        .with_dependencies(*(dependencies or [])) \
        .build()

def query_tasks(tasks: List[Task]) -> TaskQuery:
    """创建任务查询器"""
    return TaskQuery(tasks)