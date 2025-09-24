"""
AI Agent Integrations
Third-party service integrations for AI Agent Orchestrator
"""

# Conditional imports to avoid aiohttp dependency issues
try:
    from .xai_integration import XAIIntegration
    _HAS_XAI = True
except ImportError:
    _HAS_XAI = False

try:
    from .openai_integration import OpenAIIntegration
    _HAS_OPENAI = True
except ImportError:
    _HAS_OPENAI = False

try:
    from .deepseek_integration import DeepSeekIntegration
    _HAS_DEEPSEEK = True
except ImportError:
    _HAS_DEEPSEEK = False

from .openrouter_integration import OpenRouterIntegration

__all__ = ['OpenRouterIntegration']

if _HAS_XAI:
    __all__.append('XAIIntegration')
if _HAS_OPENAI:
    __all__.append('OpenAIIntegration')
if _HAS_DEEPSEEK:
    __all__.append('DeepSeekIntegration')