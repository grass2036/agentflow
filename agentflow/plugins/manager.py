"""
Plugin Manager for AgentFlow
============================

High-level management of plugin lifecycle and execution.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from .base import BasePlugin, PluginContext, PluginConfig
from .registry import PluginRegistry, plugin_registry
from .discovery import PluginDiscovery

logger = logging.getLogger(__name__)


class PluginManager:
    """High-level plugin management."""
    
    def __init__(self, registry: PluginRegistry = None):
        self.registry = registry or plugin_registry
        self.discovery = PluginDiscovery(self.registry)
        self._initialized_plugins: set = set()
        self._lock = asyncio.Lock()
        
    async def initialize_all_plugins(self) -> None:
        """Initialize all registered plugins."""
        async with self._lock:
            plugins = self.registry.get_enabled_plugins()
            load_order = self.registry.get_load_order()
            
            # Initialize in dependency order
            for plugin_name in load_order:
                plugin = self.registry.get_plugin(plugin_name)
                if plugin and plugin.is_enabled and plugin_name not in self._initialized_plugins:
                    try:
                        await plugin.initialize()
                        self._initialized_plugins.add(plugin_name)
                        logger.info(f"Initialized plugin: {plugin_name}")
                    except Exception as e:
                        logger.error(f"Failed to initialize plugin {plugin_name}: {e}")
                        # Disable failed plugin
                        self.registry.disable_plugin(plugin_name)
                        
    async def cleanup_all_plugins(self) -> None:
        """Cleanup all plugins."""
        async with self._lock:
            # Cleanup in reverse order
            load_order = self.registry.get_load_order()
            for plugin_name in reversed(load_order):
                if plugin_name in self._initialized_plugins:
                    plugin = self.registry.get_plugin(plugin_name)
                    if plugin:
                        try:
                            await plugin.cleanup()
                            logger.info(f"Cleaned up plugin: {plugin_name}")
                        except Exception as e:
                            logger.error(f"Failed to cleanup plugin {plugin_name}: {e}")
                        finally:
                            self._initialized_plugins.discard(plugin_name)
                            
    async def install_plugin(self, plugin_name: str, config: PluginConfig = None) -> bool:
        """Install and initialize a plugin."""
        try:
            # Create instance
            plugin = self.registry.create_plugin_instance(plugin_name, config)
            
            # Validate dependencies
            missing_deps = self.registry.validate_dependencies(plugin_name)
            if missing_deps:
                logger.error(f"Missing dependencies for {plugin_name}: {missing_deps}")
                return False
                
            # Initialize
            if plugin.is_enabled:
                await plugin.initialize()
                self._initialized_plugins.add(plugin_name)
                
            logger.info(f"Successfully installed plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install plugin {plugin_name}: {e}")
            return False
            
    async def uninstall_plugin(self, plugin_name: str) -> bool:
        """Uninstall a plugin."""
        try:
            plugin = self.registry.get_plugin(plugin_name)
            if plugin and plugin_name in self._initialized_plugins:
                await plugin.cleanup()
                self._initialized_plugins.discard(plugin_name)
                
            self.registry.unregister_plugin(plugin_name)
            logger.info(f"Successfully uninstalled plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to uninstall plugin {plugin_name}: {e}")
            return False
            
    async def reload_plugin(self, plugin_name: str, config: PluginConfig = None) -> bool:
        """Reload a plugin with new configuration."""
        try:
            # Cleanup existing
            plugin = self.registry.get_plugin(plugin_name)
            if plugin and plugin_name in self._initialized_plugins:
                await plugin.cleanup()
                self._initialized_plugins.discard(plugin_name)
                
            # Recreate with new config
            plugin = self.registry.create_plugin_instance(plugin_name, config)
            
            # Initialize if enabled
            if plugin.is_enabled:
                await plugin.initialize()
                self._initialized_plugins.add(plugin_name)
                
            logger.info(f"Successfully reloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reload plugin {plugin_name}: {e}")
            return False
            
    async def discover_and_load_plugins(self, search_paths: List[str] = None) -> int:
        """Discover and load plugins from search paths."""
        return await self.discovery.discover_plugins(search_paths)
        
    async def execute_hook(self, hook_name: str, context: PluginContext, *args, **kwargs) -> List[Any]:
        """Execute a hook across all plugins that provide it."""
        plugins = self.registry.get_plugins_for_hook(hook_name)
        results = []
        
        for plugin in plugins:
            try:
                if hasattr(plugin, hook_name):
                    method = getattr(plugin, hook_name)
                    if asyncio.iscoroutinefunction(method):
                        result = await method(context, *args, **kwargs)
                    else:
                        result = method(context, *args, **kwargs)
                    results.append(result)
                    
            except Exception as e:
                logger.error(f"Plugin {plugin.metadata.name} failed on hook {hook_name}: {e}")
                
        return results
        
    async def pre_task_execution(self, context: PluginContext) -> PluginContext:
        """Execute pre-task hooks."""
        plugins = self.registry.get_enabled_plugins()
        
        for plugin in sorted(plugins, key=lambda p: p.priority, reverse=True):
            try:
                result = await plugin.pre_task_execution(context)
                if result and isinstance(result, dict):
                    context.data.update(result)
            except Exception as e:
                logger.error(f"Plugin {plugin.metadata.name} failed in pre_task_execution: {e}")
                
        return context
        
    async def post_task_execution(self, context: PluginContext, result: Any) -> Any:
        """Execute post-task hooks."""
        plugins = self.registry.get_enabled_plugins()
        
        for plugin in sorted(plugins, key=lambda p: p.priority, reverse=True):
            try:
                new_result = await plugin.post_task_execution(context, result)
                if new_result is not None:
                    result = new_result
            except Exception as e:
                logger.error(f"Plugin {plugin.metadata.name} failed in post_task_execution: {e}")
                
        return result
        
    @asynccontextmanager
    async def plugin_context(self, agent_id: str, task_id: str, session_id: str, data: Dict[str, Any] = None):
        """Context manager for plugin execution around a task."""
        context = PluginContext(agent_id, task_id, session_id, data)
        
        try:
            # Pre-execution
            context = await self.pre_task_execution(context)
            
            # Notify plugins that task started
            plugins = self.registry.get_enabled_plugins()
            for plugin in plugins:
                try:
                    await plugin.on_task_started(context)
                except Exception as e:
                    logger.error(f"Plugin {plugin.metadata.name} failed on_task_started: {e}")
                    
            yield context
            
        except Exception as e:
            # Notify plugins of failure
            plugins = self.registry.get_enabled_plugins()
            for plugin in plugins:
                try:
                    await plugin.on_task_failed(context, e)
                except Exception as plugin_error:
                    logger.error(f"Plugin {plugin.metadata.name} failed on_task_failed: {plugin_error}")
            raise
            
        finally:
            # Notify plugins that task completed
            plugins = self.registry.get_enabled_plugins()
            for plugin in plugins:
                try:
                    await plugin.on_task_completed(context, None)
                except Exception as e:
                    logger.error(f"Plugin {plugin.metadata.name} failed on_task_completed: {e}")
                    
    def get_plugin_status(self) -> Dict[str, Any]:
        """Get status of all plugins."""
        return {
            'total_plugins': len(self.registry.list_active_plugins()),
            'enabled_plugins': len(self.registry.list_enabled_plugins()),
            'initialized_plugins': len(self._initialized_plugins),
            'plugin_info': self.registry.get_plugin_info()
        }
        
    async def health_check(self) -> Dict[str, bool]:
        """Run health checks on all plugins."""
        results = {}
        plugins = self.registry.get_enabled_plugins()
        
        for plugin in plugins:
            try:
                if hasattr(plugin, 'health_check'):
                    result = await plugin.health_check()
                    results[plugin.metadata.name] = bool(result)
                else:
                    results[plugin.metadata.name] = True  # Assume healthy if no check
            except Exception as e:
                logger.error(f"Health check failed for {plugin.metadata.name}: {e}")
                results[plugin.metadata.name] = False
                
        return results


# Global plugin manager
plugin_manager = PluginManager()