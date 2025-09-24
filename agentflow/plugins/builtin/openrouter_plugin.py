"""
OpenRouter Plugin
=================

Plugin for integrating with OpenRouter API (access to multiple LLMs).
"""

import os
import logging
from typing import Dict, Any, Optional
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None

from agentflow.plugins.base import IntegrationPlugin, PluginMetadata, PluginContext

logger = logging.getLogger(__name__)


class OpenRouterPlugin(IntegrationPlugin):
    """OpenRouter API integration plugin."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = None
        self.base_url = "https://openrouter.ai/api/v1"
        self.session = None
        
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="openrouter",
            version="1.0.0",
            description="OpenRouter API integration - access multiple LLMs",
            author="AgentFlow Team",
            homepage="https://github.com/agentflow/agentflow",
            tags=["ai", "llm", "openrouter", "integration", "multi-model"],
            dependencies=[],
            supports_async=True
        )
    
    async def initialize(self) -> None:
        """Initialize OpenRouter plugin."""
        logger.info("🚀 Initializing OpenRouter plugin")
        
        if not AIOHTTP_AVAILABLE:
            logger.warning("⚠️  aiohttp not available. Run: pip install aiohttp")
            return
        
        # Get API key from environment
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            logger.warning("⚠️  OPENROUTER_API_KEY not found in environment variables")
            return
            
        # Create aiohttp session
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/agentflow/agentflow",
                "X-Title": "AgentFlow"
            }
        )
        
        logger.info("✅ OpenRouter client initialized successfully")
        self.register_hook("chat_completion")
        self.register_hook("list_models")
        
    async def cleanup(self) -> None:
        """Cleanup OpenRouter plugin."""
        logger.info("🧹 Cleaning up OpenRouter plugin")
        if self.session:
            await self.session.close()
            self.session = None
            
    async def connect(self) -> bool:
        """Connect to OpenRouter service."""
        if not self.api_key or not self.session:
            return False
            
        try:
            # Test connection by getting models list
            async with self.session.get(f"{self.base_url}/models") as response:
                if response.status == 200:
                    models = await response.json()
                    model_count = len(models.get('data', []))
                    logger.info(f"✅ Connected to OpenRouter API, {model_count} models available")
                    return True
                else:
                    logger.error(f"❌ Failed to connect to OpenRouter: HTTP {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Failed to connect to OpenRouter API: {e}")
            return False
            
    async def disconnect(self) -> None:
        """Disconnect from OpenRouter service."""
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("🔌 Disconnected from OpenRouter API")
        
    async def health_check(self) -> bool:
        """Check if OpenRouter service is healthy."""
        if not self.session:
            return False
            
        try:
            async with self.session.get(f"{self.base_url}/models") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"❌ OpenRouter health check failed: {e}")
            return False
            
    async def list_models(self, context: PluginContext) -> Optional[list]:
        """Get list of available models."""
        if not self.session:
            logger.error("❌ OpenRouter session not initialized")
            return None
            
        try:
            async with self.session.get(f"{self.base_url}/models") as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get('data', [])
                    logger.info(f"✅ Retrieved {len(models)} available models")
                    return models
                else:
                    logger.error(f"❌ Failed to get models: HTTP {response.status}")
                    return None
        except Exception as e:
            logger.error(f"❌ Failed to list models: {e}")
            return None
            
    async def chat_completion(self, context: PluginContext, 
                             messages: list, 
                             model: str = "openai/gpt-3.5-turbo",
                             **kwargs) -> Optional[str]:
        """Generate chat completion."""
        if not self.session:
            logger.error("❌ OpenRouter session not initialized")
            return None
            
        payload = {
            "model": model,
            "messages": messages,
            **kwargs
        }
        
        try:
            async with self.session.post(f"{self.base_url}/chat/completions", 
                                       json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data['choices'][0]['message']['content']
                    logger.info(f"✅ Generated chat completion with {model} ({len(content)} characters)")
                    return content
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Chat completion failed: HTTP {response.status}, {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Chat completion failed: {e}")
            return None