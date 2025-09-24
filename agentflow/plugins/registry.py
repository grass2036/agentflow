"""
Plugin Registry for AgentFlow
============================

Centralized registry for managing plugin instances and metadata.
"""

from typing import Dict, List, Optional, Set, Type, Any
from collections import defaultdict
import logging
from .base import BasePlugin, PluginMetadata, PluginConfig

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Central registry for all plugins."""
    
    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        self._plugin_classes: Dict[str, Type[BasePlugin]] = {}
        self._hooks: Dict[str, List[str]] = defaultdict(list)  # hook_name -> [plugin_names]
        self._categories: Dict[str, Set[str]] = defaultdict(set)  # category -> {plugin_names}
        self._enabled_plugins: Set[str] = set()
        
    def register_plugin_class(self, plugin_class: Type[BasePlugin]) -> None:
        """Register a plugin class (not instance)."""
        # Get metadata from a temporary instance
        temp_instance = plugin_class()
        metadata = temp_instance.metadata
        
        if metadata.name in self._plugin_classes:
            logger.warning(f"Plugin {metadata.name} already registered, overwriting")
            
        self._plugin_classes[metadata.name] = plugin_class
        logger.info(f"Registered plugin class: {metadata.name} v{metadata.version}")
        
    def create_plugin_instance(self, plugin_name: str, config: PluginConfig = None) -> BasePlugin:
        """Create an instance of a registered plugin."""
        if plugin_name not in self._plugin_classes:
            raise ValueError(f"Plugin {plugin_name} not found in registry")
            
        plugin_class = self._plugin_classes[plugin_name]
        instance = plugin_class(config)
        
        self._plugins[plugin_name] = instance
        
        # Register hooks
        for hook in instance.get_hooks():
            self._hooks[hook].append(plugin_name)
            
        # Add to categories based on metadata tags
        for tag in instance.metadata.tags:
            self._categories[tag].add(plugin_name)
            
        if instance.is_enabled:
            self._enabled_plugins.add(plugin_name)
            
        logger.info(f"Created plugin instance: {plugin_name}")
        return instance
        
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get a plugin instance by name."""
        return self._plugins.get(name)
        
    def get_enabled_plugins(self) -> List[BasePlugin]:
        """Get all enabled plugin instances."""
        return [
            self._plugins[name] 
            for name in self._enabled_plugins 
            if name in self._plugins
        ]
        
    def get_plugins_by_category(self, category: str) -> List[BasePlugin]:
        """Get plugins by category/tag."""
        plugin_names = self._categories.get(category, set())
        return [
            self._plugins[name] 
            for name in plugin_names 
            if name in self._plugins and name in self._enabled_plugins
        ]
        
    def get_plugins_for_hook(self, hook_name: str) -> List[BasePlugin]:
        """Get plugins that provide a specific hook."""
        plugin_names = self._hooks.get(hook_name, [])
        return [
            self._plugins[name] 
            for name in plugin_names 
            if name in self._plugins and name in self._enabled_plugins
        ]
        
    def enable_plugin(self, name: str) -> bool:
        """Enable a plugin."""
        if name not in self._plugins:
            logger.error(f"Plugin {name} not found")
            return False
            
        plugin = self._plugins[name]
        plugin.is_enabled = True
        self._enabled_plugins.add(name)
        logger.info(f"Enabled plugin: {name}")
        return True
        
    def disable_plugin(self, name: str) -> bool:
        """Disable a plugin."""
        if name not in self._plugins:
            logger.error(f"Plugin {name} not found")
            return False
            
        plugin = self._plugins[name]
        plugin.is_enabled = False
        self._enabled_plugins.discard(name)
        logger.info(f"Disabled plugin: {name}")
        return True
        
    def unregister_plugin(self, name: str) -> bool:
        """Unregister a plugin completely."""
        if name not in self._plugins:
            return False
            
        # Remove from enabled set
        self._enabled_plugins.discard(name)
        
        # Remove from hooks
        for hook_plugins in self._hooks.values():
            if name in hook_plugins:
                hook_plugins.remove(name)
                
        # Remove from categories
        for category_plugins in self._categories.values():
            category_plugins.discard(name)
            
        # Remove instance and class
        del self._plugins[name]
        if name in self._plugin_classes:
            del self._plugin_classes[name]
            
        logger.info(f"Unregistered plugin: {name}")
        return True
        
    def list_available_plugins(self) -> List[str]:
        """List all available plugin classes."""
        return list(self._plugin_classes.keys())
        
    def list_active_plugins(self) -> List[str]:
        """List all active plugin instances."""
        return list(self._plugins.keys())
        
    def list_enabled_plugins(self) -> List[str]:
        """List all enabled plugins."""
        return list(self._enabled_plugins)
        
    def get_plugin_metadata(self, name: str) -> Optional[PluginMetadata]:
        """Get metadata for a plugin."""
        # First try to get from instance
        plugin = self._plugins.get(name)
        if plugin:
            return plugin.metadata
            
        # If no instance, try to get from registered class
        plugin_class = self._plugin_classes.get(name)
        if plugin_class:
            # Create temporary instance to get metadata
            temp_instance = plugin_class()
            return temp_instance.metadata
            
        return None
        
    def get_plugin_info(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive info about all plugins."""
        info = {}
        
        for name, plugin in self._plugins.items():
            metadata = plugin.metadata
            info[name] = {
                'metadata': {
                    'name': metadata.name,
                    'version': metadata.version,
                    'description': metadata.description,
                    'author': metadata.author,
                    'homepage': metadata.homepage,
                    'tags': metadata.tags,
                },
                'status': {
                    'enabled': plugin.is_enabled,
                    'priority': plugin.priority,
                },
                'hooks': list(plugin.get_hooks()),
                'config': plugin.config.dict() if plugin.config else None
            }
            
        return info
        
    def validate_dependencies(self, plugin_name: str) -> List[str]:
        """Check if plugin dependencies are satisfied."""
        plugin = self._plugins.get(plugin_name)
        if not plugin:
            return [f"Plugin {plugin_name} not found"]
            
        missing_deps = []
        for dep in plugin.metadata.dependencies:
            if dep not in self._plugins:
                missing_deps.append(dep)
                
        return missing_deps
        
    def get_load_order(self) -> List[str]:
        """Get plugins in load order based on dependencies and priority."""
        # Simple topological sort based on dependencies
        # Then sort by priority within each level
        
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(plugin_name: str):
            if plugin_name in temp_visited:
                raise ValueError(f"Circular dependency detected involving {plugin_name}")
            if plugin_name in visited:
                return
                
            temp_visited.add(plugin_name)
            
            plugin = self._plugins.get(plugin_name)
            if plugin:
                for dep in plugin.metadata.dependencies:
                    if dep in self._plugins:
                        visit(dep)
                        
            temp_visited.remove(plugin_name)
            visited.add(plugin_name)
            result.append(plugin_name)
            
        # Visit all plugins
        for plugin_name in self._plugins:
            if plugin_name not in visited:
                visit(plugin_name)
                
        # Sort by priority within load order
        def priority_key(name: str) -> int:
            plugin = self._plugins.get(name)
            return plugin.priority if plugin else 0
            
        result.sort(key=priority_key, reverse=True)
        return result
        
    def clear(self) -> None:
        """Clear all plugins from registry."""
        self._plugins.clear()
        self._plugin_classes.clear()
        self._hooks.clear()
        self._categories.clear()
        self._enabled_plugins.clear()
        logger.info("Cleared plugin registry")


# Global registry instance
plugin_registry = PluginRegistry()