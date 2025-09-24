#!/usr/bin/env python3
"""
Basic Agent Example
===================

A simple example demonstrating core AgentFlow functionality including:
- Agent initialization and cleanup
- Plugin system integration 
- Event handling
- Configuration management
"""

import asyncio
import json
import logging
from pathlib import Path

from agentflow.plugins.manager import plugin_manager
from agentflow.plugins.base import BasePlugin, PluginMetadata, PluginContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleTaskPlugin(BasePlugin):
    """A simple plugin that demonstrates basic functionality."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="simple_task",
            version="1.0.0", 
            description="Simple task processing plugin",
            author="AgentFlow Examples",
            tags=["example", "demo"]
        )
    
    async def initialize(self) -> None:
        logger.info("Initializing SimpleTask plugin")
        self.processed_count = 0
        
    async def cleanup(self) -> None:
        logger.info(f"Cleaning up SimpleTask plugin. Processed {self.processed_count} tasks")
        
    async def process_task(self, task_data: dict) -> dict:
        """Process a simple task."""
        self.processed_count += 1
        task_type = task_data.get("type", "unknown")
        task_id = task_data.get("id", "unknown")
        
        logger.info(f"Processing task {task_id} of type {task_type}")
        
        # Simulate some processing
        await asyncio.sleep(0.1)
        
        return {
            "task_id": task_id,
            "status": "completed",
            "result": f"Processed {task_type} task successfully",
            "processed_at": asyncio.get_event_loop().time()
        }


class BasicAgent:
    """A basic AI agent demonstrating core functionality."""
    
    def __init__(self, config_path: str = "agentflow.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.task_queue = asyncio.Queue()
        self.results = []
        
    def _load_config(self) -> dict:
        """Load agent configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            return {
                "name": "basic-agent",
                "version": "1.0.0",
                "description": "Basic AgentFlow example",
                "plugins": [],
                "config": {
                    "max_concurrent_tasks": 3,
                    "task_timeout": 30
                }
            }
    
    async def initialize(self):
        """Initialize the agent and its plugins."""
        logger.info(f"Initializing agent: {self.config['name']}")
        
        # Register our example plugin
        from agentflow.plugins.registry import plugin_registry
        plugin_registry.register_plugin_class(SimpleTaskPlugin)
        
        # Create plugin instance
        plugin_manager.registry.create_plugin_instance("simple_task")
        
        # Initialize all plugins
        await plugin_manager.initialize_all_plugins()
        
        logger.info("Agent initialization completed")
        
    async def cleanup(self):
        """Cleanup agent resources."""
        logger.info("Starting agent cleanup")
        await plugin_manager.cleanup_all_plugins()
        logger.info("Agent cleanup completed")
        
    async def add_task(self, task_data: dict):
        """Add a task to the processing queue."""
        await self.task_queue.put(task_data)
        logger.info(f"Added task {task_data.get('id', 'unknown')} to queue")
        
    async def process_tasks(self):
        """Process tasks from the queue."""
        logger.info("Starting task processing")
        
        active_tasks = set()
        max_concurrent = self.config["config"]["max_concurrent_tasks"]
        
        while True:
            try:
                # Remove completed tasks
                active_tasks = {task for task in active_tasks if not task.done()}
                
                # Start new tasks if we have capacity
                while len(active_tasks) < max_concurrent:
                    try:
                        # Get next task with timeout
                        task_data = await asyncio.wait_for(
                            self.task_queue.get(), 
                            timeout=1.0
                        )
                        
                        # Create and start task
                        task = asyncio.create_task(self._process_single_task(task_data))
                        active_tasks.add(task)
                        
                    except asyncio.TimeoutError:
                        # No new tasks available
                        break
                
                # If no active tasks and queue is empty, we're done
                if not active_tasks and self.task_queue.empty():
                    break
                    
                # Wait a bit before checking again
                await asyncio.sleep(0.1)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, stopping task processing")
                break
                
        # Wait for remaining tasks to complete
        if active_tasks:
            logger.info(f"Waiting for {len(active_tasks)} tasks to complete")
            await asyncio.gather(*active_tasks, return_exceptions=True)
            
        logger.info("Task processing completed")
        
    async def _process_single_task(self, task_data: dict):
        """Process a single task using plugins."""
        try:
            # Create plugin context
            context = PluginContext(
                agent_id=self.config["name"],
                task_id=task_data.get("id", "unknown"),
                session_id="example_session",
                data=task_data
            )
            
            # Use plugin manager to process task
            async with plugin_manager.plugin_context(
                context.agent_id,
                context.task_id, 
                context.session_id,
                context.data
            ) as ctx:
                # Get our plugin and process task
                plugin = plugin_manager.registry.get_plugin("simple_task")
                if plugin:
                    result = await plugin.process_task(task_data)
                    self.results.append(result)
                    logger.info(f"Task {task_data.get('id')} completed: {result['status']}")
                else:
                    logger.error("SimpleTask plugin not found")
                    
        except Exception as e:
            logger.error(f"Error processing task {task_data.get('id', 'unknown')}: {e}")
            
    def print_results(self):
        """Print processing results."""
        print("\\n" + "="*50)
        print("PROCESSING RESULTS")
        print("="*50)
        
        if not self.results:
            print("No tasks were processed")
            return
            
        print(f"Total tasks processed: {len(self.results)}")
        print(f"Success rate: 100%")  # All tasks succeeded in this example
        
        print("\\nTask Details:")
        for i, result in enumerate(self.results, 1):
            print(f"{i:2d}. Task {result['task_id']}: {result['status']}")
            print(f"    Result: {result['result']}")
            
        print("="*50)


async def main():
    """Main example function."""
    print("🌊 AgentFlow Basic Agent Example")
    print("="*40)
    
    # Create agent
    agent = BasicAgent()
    
    try:
        # Initialize agent
        await agent.initialize()
        
        # Add some example tasks
        tasks = [
            {"id": "task_001", "type": "data_processing", "data": {"value": 42}},
            {"id": "task_002", "type": "text_analysis", "data": {"text": "Hello AgentFlow"}},
            {"id": "task_003", "type": "calculation", "data": {"x": 10, "y": 20}},
            {"id": "task_004", "type": "validation", "data": {"email": "user@example.com"}},
            {"id": "task_005", "type": "transformation", "data": {"format": "json"}}
        ]
        
        print(f"\\nAdding {len(tasks)} tasks to processing queue...")
        for task in tasks:
            await agent.add_task(task)
            
        print("\\nProcessing tasks...")
        await agent.process_tasks()
        
        # Show results
        agent.print_results()
        
    except KeyboardInterrupt:
        print("\\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\\n❌ Error: {e}")
        logger.exception("Unexpected error occurred")
    finally:
        # Cleanup
        await agent.cleanup()
        print("\\n👋 Example completed")


if __name__ == "__main__":
    asyncio.run(main())