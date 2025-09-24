"""
OpenAI Integration
Integration with OpenAI GPT models for AI Agent tasks
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from ..core.types import AgentRole, TaskStatus


class OpenAIIntegration:
    """OpenAI API integration for AI agents"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.base_url = "https://api.openai.com/v1"
        self.default_model = "gpt-4"
        
        # Agent-specific model preferences
        self.agent_models = {
            AgentRole.PROJECT_MANAGER: "gpt-4",
            AgentRole.ARCHITECT: "gpt-4",
            AgentRole.BACKEND_DEVELOPER: "gpt-3.5-turbo",
            AgentRole.FRONTEND_DEVELOPER: "gpt-3.5-turbo",
            AgentRole.QA_ENGINEER: "gpt-3.5-turbo",
            AgentRole.DEVOPS_ENGINEER: "gpt-4",
            AgentRole.UI_UX_DESIGNER: "gpt-4",
            AgentRole.DATA_ENGINEER: "gpt-4",
            AgentRole.SECURITY_ENGINEER: "gpt-4"
        }
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        agent_role: AgentRole,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """Send chat completion request to OpenAI API"""
        
        selected_model = model or self.agent_models.get(agent_role, self.default_model)
        
        payload = {
            'model': selected_model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens
        }
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'success': True,
                            'content': data['choices'][0]['message']['content'],
                            'model': selected_model,
                            'usage': data.get('usage', {}),
                            'agent_role': agent_role.value
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f"HTTP {response.status}: {error_text}",
                            'agent_role': agent_role.value
                        }
                        
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'agent_role': agent_role.value
                }
    
    async def execute_agent_task(
        self, 
        task_description: str, 
        agent_role: AgentRole,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute a specific task using OpenAI models"""
        
        context = context or {}
        
        context_info = ""
        if context:
            context_info = f"\n\nContext:\n{json.dumps(context, indent=2)}"
        
        messages = [
            {
                'role': 'system',
                'content': f"You are a {agent_role.value.replace('_', ' ').title()} AI agent."
            },
            {
                'role': 'user',
                'content': f"Task: {task_description}{context_info}"
            }
        ]
        
        result = await self.chat_completion(messages, agent_role)
        
        if result['success']:
            return {
                'status': TaskStatus.COMPLETED,
                'output': result['content'],
                'model_used': result['model'],
                'agent_role': agent_role.value,
                'execution_info': {
                    'api_provider': 'openai',
                    'model': result['model'],
                    'usage': result.get('usage', {})
                }
            }
        else:
            return {
                'status': TaskStatus.FAILED,
                'error': result['error'],
                'agent_role': agent_role.value,
                'execution_info': {
                    'api_provider': 'openai',
                    'error_details': result['error']
                }
            }
    
    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models"""
        return ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo-preview"]
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test OpenAI API connection"""
        test_messages = [
            {'role': 'user', 'content': 'Hello, please respond with "Connection successful".'}
        ]
        
        result = await self.chat_completion(test_messages, AgentRole.PROJECT_MANAGER)
        
        return {
            'connected': result['success'],
            'model': result.get('model', 'unknown'),
            'response': result.get('content', result.get('error', 'No response')),
            'api_provider': 'openai'
        }