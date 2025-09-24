"""
X.AI (Grok) Integration
Integration with X.AI's Grok models for AI Agent tasks
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from ..core.types import AgentRole, TaskStatus


class XAIIntegration:
    """X.AI Grok API integration for AI agents"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('XAI_API_KEY')
        if not self.api_key:
            raise ValueError("XAI_API_KEY environment variable is required")
        
        self.base_url = "https://api.x.ai/v1"
        self.default_model = "grok-3-mini"
        
        # Agent-specific model preferences
        self.agent_models = {
            AgentRole.PROJECT_MANAGER: "grok-3",
            AgentRole.ARCHITECT: "grok-3",
            AgentRole.BACKEND_DEVELOPER: "grok-3-mini",
            AgentRole.FRONTEND_DEVELOPER: "grok-3-mini", 
            AgentRole.QA_ENGINEER: "grok-3-mini",
            AgentRole.DEVOPS_ENGINEER: "grok-3-mini",
            AgentRole.UI_UX_DESIGNER: "grok-3",
            AgentRole.DATA_ENGINEER: "grok-3",
            AgentRole.SECURITY_ENGINEER: "grok-3"
        }
        
        # Agent-specific system prompts
        self.agent_prompts = {
            AgentRole.PROJECT_MANAGER: """You are an expert Project Manager AI agent. You excel at:
- Requirements analysis and project planning
- Risk assessment and mitigation strategies
- Resource allocation and timeline management
- Stakeholder communication and coordination
- Quality assurance and delivery oversight

Provide clear, actionable project management deliverables.""",

            AgentRole.ARCHITECT: """You are an expert Software Architect AI agent. You excel at:
- System design and architecture patterns
- Technology stack evaluation and selection
- Scalability and performance optimization
- Integration design and API architecture
- Security and compliance considerations

Design robust, scalable, and maintainable system architectures.""",

            AgentRole.BACKEND_DEVELOPER: """You are an expert Backend Developer AI agent. You excel at:
- API development and microservices architecture
- Database design and optimization
- Server-side business logic implementation
- Security best practices and authentication
- Performance optimization and caching

Write clean, efficient, and secure backend code with proper error handling.""",

            AgentRole.FRONTEND_DEVELOPER: """You are an expert Frontend Developer AI agent. You excel at:
- Modern UI/UX implementation
- Component-based architecture
- State management and data flow
- Performance optimization and accessibility
- Cross-platform compatibility

Create responsive, user-friendly interfaces with modern frameworks.""",

            AgentRole.QA_ENGINEER: """You are an expert QA Engineer AI agent. You excel at:
- Test strategy and test case design
- Automated testing frameworks and CI/CD
- Quality assurance processes
- Bug detection and regression testing
- Performance and security testing

Ensure high-quality software through comprehensive testing strategies.""",

            AgentRole.DEVOPS_ENGINEER: """You are an expert DevOps Engineer AI agent. You excel at:
- Infrastructure as Code and automation
- CI/CD pipeline design and implementation
- Containerization and orchestration
- Monitoring, logging, and observability
- Cloud platform optimization

Build reliable, scalable, and automated deployment infrastructure.""",

            AgentRole.UI_UX_DESIGNER: """You are an expert UI/UX Designer AI agent. You excel at:
- User experience research and design
- Interface design and prototyping
- Design systems and style guides
- Accessibility and usability testing
- Cross-platform design consistency

Create intuitive, accessible, and visually appealing user experiences.""",

            AgentRole.DATA_ENGINEER: """You are an expert Data Engineer AI agent. You excel at:
- Data pipeline architecture and ETL processes
- Data modeling and warehouse design
- Big data technologies and analytics
- Data quality and governance
- Machine learning infrastructure

Build robust, scalable data infrastructure and analytics solutions.""",

            AgentRole.SECURITY_ENGINEER: """You are an expert Security Engineer AI agent. You excel at:
- Security architecture and threat modeling
- Vulnerability assessment and penetration testing
- Compliance and regulatory requirements
- Security automation and monitoring
- Incident response and forensics

Implement comprehensive security measures and protect against threats."""
        }
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        agent_role: AgentRole,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """Send chat completion request to X.AI API"""
        
        # Select appropriate model for agent
        selected_model = model or self.agent_models.get(agent_role, self.default_model)
        
        # Add agent-specific system prompt if not provided
        if not messages or messages[0].get('role') != 'system':
            system_prompt = self.agent_prompts.get(agent_role, "You are a helpful AI assistant.")
            messages.insert(0, {'role': 'system', 'content': system_prompt})
        
        payload = {
            'model': selected_model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'stream': False
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
                        
            except asyncio.TimeoutError:
                return {
                    'success': False,
                    'error': "Request timeout",
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
        """Execute a specific task using appropriate X.AI model for the agent"""
        
        context = context or {}
        
        # Build context-aware prompt
        context_info = ""
        if context:
            context_info = f"\n\nContext:\n{json.dumps(context, indent=2)}"
        
        messages = [
            {
                'role': 'user',
                'content': f"""Task: {task_description}{context_info}

Please provide a comprehensive response including:
1. Analysis of the task requirements
2. Recommended approach or solution
3. Key deliverables or outputs
4. Potential challenges and mitigation strategies
5. Next steps or follow-up actions

Format your response as structured output that can be used by other agents."""
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
                    'api_provider': 'xai',
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
                    'api_provider': 'xai',
                    'error_details': result['error']
                }
            }
    
    async def get_agent_recommendation(
        self, 
        project_description: str, 
        tech_stack: List[str],
        requirements: List[str]
    ) -> Dict[str, Any]:
        """Get AI recommendation for project approach"""
        
        messages = [
            {
                'role': 'user',
                'content': f"""Project Analysis Request:

Description: {project_description}
Technology Stack: {', '.join(tech_stack)}
Requirements: {', '.join(requirements)}

Please provide:
1. Project complexity assessment
2. Recommended development approach
3. Key technical challenges
4. Suggested agent coordination strategy
5. Estimated timeline and milestones

Provide a structured analysis that can guide the multi-agent development process."""
            }
        ]
        
        result = await self.chat_completion(messages, AgentRole.ARCHITECT)
        return result
    
    def get_available_models(self) -> List[str]:
        """Get list of available X.AI models"""
        return ["grok-3", "grok-3-mini", "grok-vision"]
    
    def get_agent_model_preference(self, agent_role: AgentRole) -> str:
        """Get preferred model for specific agent role"""
        return self.agent_models.get(agent_role, self.default_model)
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test X.AI API connection"""
        test_messages = [
            {'role': 'user', 'content': 'Hello, please respond with "Connection successful" if you can hear me.'}
        ]
        
        result = await self.chat_completion(test_messages, AgentRole.PROJECT_MANAGER)
        
        return {
            'connected': result['success'],
            'model': result.get('model', 'unknown'),
            'response': result.get('content', result.get('error', 'No response')),
            'api_provider': 'xai'
        }