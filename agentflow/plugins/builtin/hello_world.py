"""
Hello World Plugin
==================

A simple example plugin to demonstrate basic plugin functionality.
"""

import asyncio
import logging
from typing import Dict, Any

from agentflow.plugins.base import BasePlugin, PluginMetadata, PluginContext

logger = logging.getLogger(__name__)


class HelloWorldPlugin(BasePlugin):
    """Simple hello world plugin for demonstration."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="hello_world",
            version="1.0.0",
            description="Simple hello world plugin for testing",
            author="AgentFlow Team",
            homepage="https://github.com/agentflow/agentflow",
            tags=["example", "demo", "builtin"],
            supports_async=True
        )
    
    async def initialize(self) -> None:
        """Initialize the hello world plugin."""
        logger.info("🌊 Hello World plugin initialized!")
        self.message_count = 0
        self.register_hook("say_hello")
        
    async def cleanup(self) -> None:
        """Cleanup the hello world plugin."""
        logger.info(f"👋 Hello World plugin cleaned up! Processed {self.message_count} messages")
        
    async def say_hello(self, context: PluginContext, name: str = "World") -> str:
        """Say hello to someone."""
        self.message_count += 1
        message = f"Hello, {name}! This is message #{self.message_count} from AgentFlow"
        logger.info(f"📝 {message}")
        return message
        
    async def pre_task_execution(self, context: PluginContext) -> Dict[str, Any]:
        """Called before task execution."""
        logger.info(f"🚀 Starting task {context.task_id}")
        return {"hello_world_active": True, "start_time": asyncio.get_event_loop().time()}
        
    async def post_task_execution(self, context: PluginContext, result: Any) -> Any:
        """Called after task execution."""
        logger.info(f"✅ Completed task {context.task_id}")
        return result
        
    async def health_check(self) -> bool:
        """Check if the plugin is healthy."""
        return True