"""
核心类型定义
定义AI Agent系统中使用的所有枚举类型和数据结构
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime

class AgentRole(Enum):
    """Agent角色定义"""
    PROJECT_MANAGER = "project_manager"
    ARCHITECT = "architect"
    BACKEND_DEVELOPER = "backend_developer"
    FRONTEND_DEVELOPER = "frontend_developer"
    QA_ENGINEER = "qa_engineer"
    DEVOPS_ENGINEER = "devops_engineer"
    UI_UX_DESIGNER = "ui_ux_designer"
    DATA_ENGINEER = "data_engineer"
    SECURITY_ENGINEER = "security_engineer"

class TechStack(Enum):
    """技术栈定义"""
    # 后端技术
    PYTHON_FASTAPI = "python_fastapi"
    PYTHON_DJANGO = "python_django"
    PYTHON_FLASK = "python_flask"
    NODEJS_EXPRESS = "nodejs_express"
    NODEJS_NESTJS = "nodejs_nestjs"
    JAVA_SPRING = "java_spring"
    GO_GIN = "go_gin"
    CSHARP_DOTNET = "csharp_dotnet"
    PHP_LARAVEL = "php_laravel"
    RUST_ACTIX = "rust_actix"
    
    # 前端技术
    VUE_JS = "vue_js"
    REACT_JS = "react_js"
    ANGULAR = "angular"
    SVELTE = "svelte"
    NEXTJS = "nextjs"
    NUXTJS = "nuxtjs"
    
    # 移动端技术
    FLUTTER = "flutter"
    REACT_NATIVE = "react_native"
    IONIC = "ionic"
    
    # 数据库
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"
    SQLITE = "sqlite"
    
    # 云平台和工具
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"

class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

class ProjectComplexity(Enum):
    """项目复杂度"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"

class PlatformType(Enum):
    """目标平台类型"""
    WEB = "web"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    API = "api"
    MICROSERVICE = "microservice"
    FULLSTACK = "fullstack"

class EventType(Enum):
    """事件类型"""
    # 任务事件
    TASK_CREATED = "task_created"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_BLOCKED = "task_blocked"
    
    # Agent事件
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    AGENT_ERROR = "agent_error"
    AGENT_REQUEST_HELP = "agent_request_help"
    
    # 协作事件
    COLLABORATION_STARTED = "collaboration_started"
    COLLABORATION_COMPLETED = "collaboration_completed"
    COLLABORATION_CONFLICT = "collaboration_conflict"
    
    # 系统事件
    PROJECT_STARTED = "project_started"
    PROJECT_COMPLETED = "project_completed"
    SYSTEM_ALERT = "system_alert"
    PERFORMANCE_WARNING = "performance_warning"

@dataclass
class AgentCapability:
    """Agent能力定义"""
    agent_role: AgentRole
    supported_tech_stacks: List[TechStack]
    specialties: List[str]
    tools: List[str]
    max_concurrent_tasks: int = 3
    performance_score: float = 1.0

@dataclass
class ProjectConfig:
    """项目配置"""
    name: str
    description: str
    tech_stack: List[TechStack]
    target_platform: PlatformType
    complexity: ProjectComplexity
    requirements: List[str]
    timeline: Optional[str] = None
    team_size: Optional[int] = None
    budget: Optional[float] = None
    priority: TaskPriority = TaskPriority.MEDIUM

@dataclass
class TaskDependency:
    """任务依赖关系"""
    task_id: str
    depends_on: List[str]
    dependency_type: str = "finish_to_start"  # finish_to_start, start_to_start, etc.

@dataclass
class PerformanceMetrics:
    """性能指标"""
    tasks_completed: int = 0
    tasks_failed: int = 0
    average_completion_time: float = 0.0
    success_rate: float = 1.0
    efficiency_score: float = 1.0
    collaboration_events: int = 0

@dataclass
class AgentEvent:
    """Agent事件"""
    event_type: EventType
    source_agent: AgentRole
    target_agent: Optional[AgentRole] = None
    data: Dict[str, Any] = None
    session_id: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.data is None:
            self.data = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "event_type": self.event_type.value,
            "source_agent": self.source_agent.value,
            "target_agent": self.target_agent.value if self.target_agent else None,
            "data": self.data,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat()
        }

# 类型别名
AgentID = str
TaskID = str
SessionID = str
ConfigDict = Dict[str, Any]

# 常量定义
DEFAULT_TASK_TIMEOUT = 3600  # 1小时
MAX_CONCURRENT_TASKS = 10
DEFAULT_AGENT_CAPACITY = 3
MIN_SUCCESS_RATE = 0.8

# 技术栈兼容性映射
TECH_STACK_COMPATIBILITY = {
    TechStack.PYTHON_FASTAPI: [TechStack.VUE_JS, TechStack.REACT_JS, TechStack.POSTGRESQL, TechStack.REDIS],
    TechStack.NODEJS_EXPRESS: [TechStack.REACT_JS, TechStack.VUE_JS, TechStack.MONGODB, TechStack.POSTGRESQL],
    TechStack.VUE_JS: [TechStack.PYTHON_FASTAPI, TechStack.NODEJS_EXPRESS, TechStack.DOCKER],
    TechStack.REACT_JS: [TechStack.NODEJS_EXPRESS, TechStack.PYTHON_DJANGO, TechStack.DOCKER],
}

# Agent能力映射
AGENT_CAPABILITIES = {
    AgentRole.PROJECT_MANAGER: AgentCapability(
        agent_role=AgentRole.PROJECT_MANAGER,
        supported_tech_stacks=list(TechStack),  # 支持所有技术栈
        specialties=["需求分析", "项目规划", "进度管理", "风险控制", "团队协调"],
        tools=["甘特图生成", "需求追踪", "风险矩阵", "进度报告", "资源分配"]
    ),
    AgentRole.ARCHITECT: AgentCapability(
        agent_role=AgentRole.ARCHITECT,
        supported_tech_stacks=list(TechStack),
        specialties=["系统设计", "技术选型", "架构模式", "性能优化", "扩展性设计"],
        tools=["架构图生成", "技术评估", "性能分析", "模式推荐", "容量规划"]
    ),
    AgentRole.BACKEND_DEVELOPER: AgentCapability(
        agent_role=AgentRole.BACKEND_DEVELOPER,
        supported_tech_stacks=[
            TechStack.PYTHON_FASTAPI, TechStack.PYTHON_DJANGO, TechStack.PYTHON_FLASK,
            TechStack.NODEJS_EXPRESS, TechStack.NODEJS_NESTJS, TechStack.JAVA_SPRING,
            TechStack.GO_GIN, TechStack.CSHARP_DOTNET, TechStack.POSTGRESQL, 
            TechStack.MYSQL, TechStack.MONGODB, TechStack.REDIS
        ],
        specialties=["API开发", "数据库设计", "业务逻辑", "性能优化", "安全实现"],
        tools=["代码生成", "API文档", "数据库迁移", "单元测试", "性能监控"]
    ),
    AgentRole.FRONTEND_DEVELOPER: AgentCapability(
        agent_role=AgentRole.FRONTEND_DEVELOPER,
        supported_tech_stacks=[
            TechStack.VUE_JS, TechStack.REACT_JS, TechStack.ANGULAR, TechStack.SVELTE,
            TechStack.NEXTJS, TechStack.NUXTJS, TechStack.FLUTTER, TechStack.REACT_NATIVE
        ],
        specialties=["UI组件", "用户体验", "状态管理", "响应式设计", "性能优化"],
        tools=["组件库", "样式框架", "构建工具", "测试框架", "性能分析"]
    ),
    AgentRole.QA_ENGINEER: AgentCapability(
        agent_role=AgentRole.QA_ENGINEER,
        supported_tech_stacks=list(TechStack),
        specialties=["测试策略", "质量保证", "自动化测试", "性能测试", "安全测试"],
        tools=["测试框架", "自动化工具", "性能测试", "安全扫描", "质量报告"]
    ),
}

def get_compatible_tech_stacks(tech: TechStack) -> List[TechStack]:
    """获取兼容的技术栈"""
    return TECH_STACK_COMPATIBILITY.get(tech, [])

def get_agent_capability(role: AgentRole) -> AgentCapability:
    """获取Agent能力信息"""
    return AGENT_CAPABILITIES.get(role, AgentCapability(
        agent_role=role,
        supported_tech_stacks=[],
        specialties=[],
        tools=[]
    ))

def is_tech_stack_compatible(tech1: TechStack, tech2: TechStack) -> bool:
    """检查两个技术栈是否兼容"""
    return tech2 in get_compatible_tech_stacks(tech1) or tech1 in get_compatible_tech_stacks(tech2)