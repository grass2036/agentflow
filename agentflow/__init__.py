"""
AgentFlow - Open-source AI Agent orchestration framework
========================================================

A powerful, flexible foundation for creating complex AI workflows 
with multiple specialized agents working together seamlessly.
"""

__version__ = "0.1.0"
__author__ = "AgentFlow Team"
__license__ = "MIT"

def get_version():
    """Get the current version of AgentFlow."""
    return __version__

def get_info():
    """Get information about AgentFlow."""
    return {
        "name": "AgentFlow",
        "version": __version__,
        "description": "Open-source AI Agent orchestration framework",
        "author": __author__,
        "license": __license__,
        "homepage": "https://github.com/agentflow/agentflow",
        "documentation": "https://agentflow.readthedocs.io"
    }

# Welcome message
print(f"🌊 AgentFlow v{__version__} - AI Agent Orchestration Framework")
print("📖 Documentation: https://agentflow.readthedocs.io")