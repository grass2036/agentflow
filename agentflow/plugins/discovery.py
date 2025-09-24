"""
Plugin Discovery for AgentFlow
==============================

Automatically discover and load plugins from various sources.
"""

import os
import sys
import importlib
import importlib.util
import inspect
import logging
from pathlib import Path
from typing import List, Type, Optional, Dict, Set
import pkg_resources

from .base import BasePlugin
from .registry import PluginRegistry

logger = logging.getLogger(__name__)


class PluginDiscovery:
    """Discover and load plugins from various sources."""
    
    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self._loaded_modules: Set[str] = set()
        
    async def discover_plugins(self, search_paths: List[str] = None) -> int:
        """Discover plugins from multiple sources."""
        total_discovered = 0
        
        # 1. Discover from entry points
        total_discovered += self._discover_from_entry_points()
        
        # 2. Discover from search paths
        if search_paths:
            for path in search_paths:
                total_discovered += await self._discover_from_path(path)
                
        # 3. Discover from default locations
        default_paths = self._get_default_search_paths()
        for path in default_paths:
            if os.path.exists(path):
                total_discovered += await self._discover_from_path(path)
                
        logger.info(f"Discovered {total_discovered} plugins total")
        return total_discovered
        
    def _discover_from_entry_points(self) -> int:
        """Discover plugins from setuptools entry points."""
        discovered = 0
        
        try:
            # Look for agentflow.plugins entry point group
            for entry_point in pkg_resources.iter_entry_points('agentflow.plugins'):
                try:
                    plugin_class = entry_point.load()
                    if self._is_valid_plugin_class(plugin_class):
                        self.registry.register_plugin_class(plugin_class)
                        discovered += 1
                        logger.info(f"Discovered plugin from entry point: {entry_point.name}")
                except Exception as e:
                    logger.error(f"Failed to load plugin from entry point {entry_point.name}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to discover plugins from entry points: {e}")
            
        return discovered
        
    async def _discover_from_path(self, search_path: str) -> int:
        """Discover plugins from a file system path."""
        discovered = 0
        path = Path(search_path)
        
        if not path.exists():
            logger.warning(f"Plugin search path does not exist: {search_path}")
            return 0
            
        logger.info(f"Searching for plugins in: {search_path}")
        
        # Look for Python files and packages
        for item in path.rglob("*.py"):
            if item.name.startswith("__"):
                continue
                
            try:
                discovered += await self._load_plugin_from_file(item)
            except Exception as e:
                logger.error(f"Failed to load plugin from {item}: {e}")
                
        # Look for plugin packages (directories with __init__.py)
        for item in path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                try:
                    discovered += await self._load_plugin_from_package(item)
                except Exception as e:
                    logger.error(f"Failed to load plugin package from {item}: {e}")
                    
        return discovered
        
    async def _load_plugin_from_file(self, file_path: Path) -> int:
        """Load plugin from a single Python file."""
        discovered = 0
        
        # Create module name from file path
        module_name = f"agentflow_plugin_{file_path.stem}_{id(file_path)}"
        
        if module_name in self._loaded_modules:
            return 0
            
        try:
            # Load module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                self._loaded_modules.add(module_name)
                
                # Find plugin classes in module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if self._is_valid_plugin_class(obj) and obj.__module__ == module_name:
                        self.registry.register_plugin_class(obj)
                        discovered += 1
                        logger.info(f"Discovered plugin class: {name} from {file_path}")
                        
        except Exception as e:
            logger.error(f"Failed to load plugin from file {file_path}: {e}")
            
        return discovered
        
    async def _load_plugin_from_package(self, package_path: Path) -> int:
        """Load plugin from a Python package directory."""
        discovered = 0
        
        # Create module name
        module_name = f"agentflow_plugin_pkg_{package_path.name}_{id(package_path)}"
        
        if module_name in self._loaded_modules:
            return 0
            
        try:
            # Add package parent to sys.path temporarily
            parent_path = str(package_path.parent)
            if parent_path not in sys.path:
                sys.path.insert(0, parent_path)
                
            try:
                # Import the package
                spec = importlib.util.spec_from_file_location(
                    module_name, 
                    package_path / "__init__.py"
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    self._loaded_modules.add(module_name)
                    
                    # Find plugin classes
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if self._is_valid_plugin_class(obj):
                            self.registry.register_plugin_class(obj)
                            discovered += 1
                            logger.info(f"Discovered plugin class: {name} from package {package_path}")
                            
            finally:
                # Remove from sys.path
                if parent_path in sys.path:
                    sys.path.remove(parent_path)
                    
        except Exception as e:
            logger.error(f"Failed to load plugin package from {package_path}: {e}")
            
        return discovered
        
    def _is_valid_plugin_class(self, cls) -> bool:
        """Check if a class is a valid plugin class."""
        try:
            return (
                inspect.isclass(cls) and 
                issubclass(cls, BasePlugin) and 
                cls != BasePlugin and
                not inspect.isabstract(cls)
            )
        except Exception:
            return False
            
    def _get_default_search_paths(self) -> List[str]:
        """Get default plugin search paths."""
        paths = []
        
        # 1. User plugins directory
        home_plugins = os.path.expanduser("~/.agentflow/plugins")
        paths.append(home_plugins)
        
        # 2. System plugins directory  
        if sys.platform.startswith('win'):
            system_plugins = os.path.join(os.environ.get('PROGRAMDATA', ''), 'AgentFlow', 'plugins')
        else:
            system_plugins = '/usr/local/share/agentflow/plugins'
        paths.append(system_plugins)
        
        # 3. Current working directory plugins
        cwd_plugins = os.path.join(os.getcwd(), 'plugins')
        paths.append(cwd_plugins)
        
        # 4. AgentFlow package plugins
        try:
            import agentflow
            package_dir = os.path.dirname(agentflow.__file__)
            package_plugins = os.path.join(package_dir, 'plugins', 'builtin')
            paths.append(package_plugins)
        except Exception:
            pass
            
        return paths
        
    def load_plugin_from_module(self, module_name: str, class_name: str = None) -> int:
        """Load plugin from a specific module."""
        discovered = 0
        
        try:
            # Import the module
            module = importlib.import_module(module_name)
            
            if class_name:
                # Load specific class
                if hasattr(module, class_name):
                    cls = getattr(module, class_name)
                    if self._is_valid_plugin_class(cls):
                        self.registry.register_plugin_class(cls)
                        discovered = 1
                        logger.info(f"Loaded plugin class: {class_name} from {module_name}")
            else:
                # Find all plugin classes in module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if self._is_valid_plugin_class(obj) and obj.__module__ == module_name:
                        self.registry.register_plugin_class(obj)
                        discovered += 1
                        logger.info(f"Loaded plugin class: {name} from {module_name}")
                        
        except Exception as e:
            logger.error(f"Failed to load plugin from module {module_name}: {e}")
            
        return discovered
        
    def get_discovered_plugins(self) -> List[str]:
        """Get list of discovered plugin names."""
        return self.registry.list_available_plugins()
        
    def get_plugin_metadata_by_file(self, file_path: str) -> Optional[Dict]:
        """Get plugin metadata from a file without loading it."""
        try:
            # This is a simplified version - you might want to parse
            # the file more carefully to extract metadata
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Look for metadata patterns
            metadata = {}
            
            # This is a basic implementation - enhance as needed
            if 'class' in content and 'BasePlugin' in content:
                metadata['has_plugin'] = True
                
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to get metadata from {file_path}: {e}")
            return None