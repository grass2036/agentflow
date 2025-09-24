"""
Base Plugin Architecture for AgentFlow
=====================================

This module provides the foundation for AgentFlow's plugin system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from pydantic import BaseModel
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class PluginMetadata:
    """Plugin metadata and configuration."""
    name: str
    version: str
    description: str
    author: str
    homepage: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    min_agentflow_version: str = "0.1.0"
    max_agentflow_version: Optional[str] = None
    supports_async: bool = True
    config_schema: Optional[Dict[str, Any]] = None


class PluginConfig(BaseModel):
    """Base configuration model for plugins."""
    enabled: bool = True
    priority: int = 50  # 0-100, higher = more priority
    config: Dict[str, Any] = {}


class PluginContext:
    """Context passed to plugins during execution."""
    
    def __init__(self, agent_id: str, task_id: str, session_id: str, data: Dict[str, Any] = None):
        self.agent_id = agent_id
        self.task_id = task_id 
        self.session_id = session_id
        self.data = data or {}
        self.shared_state: Dict[str, Any] = {}
        
    def get_shared(self, key: str, default: Any = None) -> Any:
        """Get value from shared state."""
        return self.shared_state.get(key, default)
        
    def set_shared(self, key: str, value: Any) -> None:
        """Set value in shared state."""
        self.shared_state[key] = value


class BasePlugin(ABC):
    """Base class for all AgentFlow plugins."""
    
    def __init__(self, config: PluginConfig = None):
        self.config = config or PluginConfig()
        self.is_enabled = self.config.enabled
        self.priority = self.config.priority
        self._hooks: Set[str] = set()
        
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass
        
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the plugin."""
        pass
        
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up resources when plugin is disabled."""
        pass
        
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration."""
        return True
        
    def register_hook(self, hook_name: str) -> None:
        """Register a hook that this plugin provides."""
        self._hooks.add(hook_name)
        
    def get_hooks(self) -> Set[str]:
        """Get list of hooks this plugin provides."""
        return self._hooks.copy()
        
    async def pre_task_execution(self, context: PluginContext) -> Optional[Dict[str, Any]]:
        """Called before task execution. Can modify context."""
        return None
        
    async def post_task_execution(self, context: PluginContext, result: Any) -> Optional[Any]:
        """Called after task execution. Can modify result."""
        return result
        
    async def on_agent_created(self, agent_id: str, agent_type: str) -> None:
        """Called when an agent is created."""
        pass
        
    async def on_agent_destroyed(self, agent_id: str) -> None:
        """Called when an agent is destroyed."""
        pass
        
    async def on_task_started(self, context: PluginContext) -> None:
        """Called when a task starts."""
        pass
        
    async def on_task_completed(self, context: PluginContext, result: Any) -> None:
        """Called when a task completes."""
        pass
        
    async def on_task_failed(self, context: PluginContext, error: Exception) -> None:
        """Called when a task fails."""
        pass
        
    async def on_session_started(self, session_id: str) -> None:
        """Called when a session starts."""
        pass
        
    async def on_session_ended(self, session_id: str) -> None:
        """Called when a session ends."""
        pass


class AgentPlugin(BasePlugin):
    """Base class for agent-specific plugins."""
    
    @abstractmethod
    async def enhance_agent(self, agent_instance: Any) -> Any:
        """Enhance an agent instance with plugin functionality."""
        pass


class TaskPlugin(BasePlugin):
    """Base class for task-specific plugins."""
    
    @abstractmethod
    async def process_task(self, context: PluginContext) -> Any:
        """Process a task with plugin logic."""
        pass


class IntegrationPlugin(BasePlugin):
    """Base class for external integration plugins."""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to external service."""
        pass
        
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from external service."""
        pass
        
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if external service is healthy."""
        pass


class DataPlugin(BasePlugin):
    """Base class for data processing plugins."""
    
    @abstractmethod
    async def process_data(self, data: Any, context: PluginContext) -> Any:
        """Process data with plugin logic."""
        pass


class MonitoringPlugin(BasePlugin):
    """Base class for monitoring and observability plugins."""
    
    @abstractmethod
    async def collect_metrics(self, context: PluginContext) -> Dict[str, Any]:
        """Collect metrics from the system."""
        pass
        
    @abstractmethod
    async def send_logs(self, level: str, message: str, context: PluginContext) -> None:
        """Send logs to monitoring system."""
        pass