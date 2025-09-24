"""
OpenAI Plugin
=============

Plugin for integrating with OpenAI API services.
"""

import os
import logging
from typing import Dict, Any, Optional

from agentflow.plugins.base import IntegrationPlugin, PluginMetadata, PluginContext

logger = logging.getLogger(__name__)


class OpenAIPlugin(IntegrationPlugin):
    """OpenAI API integration plugin."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = None
        self.client = None
        
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="openai",
            version="1.0.0",
            description="OpenAI API integration plugin",
            author="AgentFlow Team",
            homepage="https://github.com/agentflow/agentflow",
            tags=["ai", "llm", "openai", "integration"],
            dependencies=[],
            supports_async=True
        )
    
    async def initialize(self) -> None:
        """Initialize OpenAI plugin."""
        logger.info("🤖 Initializing OpenAI plugin")
        
        # Get API key from environment
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("⚠️  OPENAI_API_KEY not found in environment variables")
            return
            
        try:
            # Try to import openai - this is optional
            import openai
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
            logger.info("✅ OpenAI client initialized successfully")
        except ImportError:
            logger.warning("⚠️  OpenAI library not installed. Run: pip install openai")
            self.client = None
        
        self.register_hook("chat_completion")
        self.register_hook("generate_text")
        
    async def cleanup(self) -> None:
        """Cleanup OpenAI plugin."""
        logger.info("🧹 Cleaning up OpenAI plugin")
        self.client = None
        
    async def connect(self) -> bool:
        """Connect to OpenAI service."""
        if not self.api_key:
            return False
            
        if not self.client:
            return False
            
        try:
            # Test connection by making a simple API call
            models = await self.client.models.list()
            logger.info(f"✅ Connected to OpenAI API, {len(models.data)} models available")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to OpenAI API: {e}")
            return False
            
    async def disconnect(self) -> None:
        """Disconnect from OpenAI service."""
        logger.info("🔌 Disconnected from OpenAI API")
        
    async def health_check(self) -> bool:
        """Check if OpenAI service is healthy."""
        if not self.client:
            return False
            
        try:
            # Simple health check - list models
            await self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"❌ OpenAI health check failed: {e}")
            return False
            
    async def chat_completion(self, context: PluginContext, 
                             messages: list, 
                             model: str = "gpt-3.5-turbo",
                             **kwargs) -> Optional[str]:
        """Generate chat completion."""
        if not self.client:
            logger.error("❌ OpenAI client not initialized")
            return None
            
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            
            content = response.choices[0].message.content
            logger.info(f"✅ Generated chat completion ({len(content)} characters)")
            return content
            
        except Exception as e:
            logger.error(f"❌ Chat completion failed: {e}")
            return None
            
    async def generate_text(self, context: PluginContext, 
                           prompt: str, 
                           model: str = "gpt-3.5-turbo",
                           **kwargs) -> Optional[str]:
        """Generate text from prompt."""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(context, messages, model, **kwargs)