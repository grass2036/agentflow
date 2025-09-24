"""
AgentFlow Plugin System
======================

A powerful plugin architecture for extending AgentFlow with custom functionality.
"""

from .base import BasePlugin, PluginMetadata
from .manager import plugin_manager
from .registry import plugin_registry

__all__ = [
    'BasePlugin',
    'PluginMetadata', 
    'plugin_manager',
    'plugin_registry'
]