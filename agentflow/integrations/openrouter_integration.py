"""
OpenRouter API Integration
Provides access to 325+ AI models through OpenRouter's unified API
"""

import json
import logging
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..core.types import AgentRole

logger = logging.getLogger(__name__)

class OpenRouterIntegration:
    """OpenRouter API集成类"""
    
    def __init__(self, api_key: str, app_name: str = "AI Agent Orchestrator", 
                 enable_premium_models: bool = False):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.app_name = app_name
        self.enable_premium_models = enable_premium_models
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-agent-orchestrator.com",
            "X-Title": app_name,
        }
        
        # Model preferences for different agent roles
        self.agent_model_preferences = {
            AgentRole.PROJECT_MANAGER: {
                "premium": "gpt-3.5-turbo",
                "free": "x-ai/grok-4-fast:free",
                "fallback": "google/gemma-2-9b-it:free", 
                "system_prompt": """你是一位经验丰富的项目经理。你的职责是：
- 分析项目需求和复杂度
- 制定详细的项目计划和时间线
- 识别潜在风险和依赖关系
- 分配资源和协调团队
- 监控项目进度和质量

请用专业、结构化的方式回应，包含具体的行动计划和里程碑。"""
            },
            
            AgentRole.ARCHITECT: {
                "premium": "deepseek/deepseek-v3.1-terminus",
                "free": "x-ai/grok-4-fast:free",
                "fallback": "qwen/qwen3-coder-flash", 
                "system_prompt": """你是一位资深的系统架构师。你的专长包括：
- 设计可扩展的系统架构
- 选择合适的技术栈和设计模式
- 定义API接口和数据模型
- 考虑性能、安全性和可维护性
- 制定技术规范和最佳实践

请提供详细的架构设计，包含图表、技术选型理由和实施建议。"""
            },
            
            AgentRole.BACKEND_DEVELOPER: {
                "premium": "qwen/qwen3-coder-plus",
                "free": "x-ai/grok-4-fast:free",
                "fallback": "deepseek/deepseek-chat-v3.1:free",
                "system_prompt": """你是一位专业的后端开发工程师。你的技能包括：
- 编写高质量的后端代码
- 设计和实现API接口
- 数据库设计和优化
- 处理并发、缓存和性能优化
- 实现安全认证和授权

请提供完整、可运行的代码实现，包含错误处理、类型注解和文档。"""
            },
            
            AgentRole.FRONTEND_DEVELOPER: {
                "premium": "gpt-3.5-turbo",
                "free": "x-ai/grok-4-fast:free",
                "fallback": "google/gemma-2-9b-it:free",
                "system_prompt": """你是一位专业的前端开发工程师。你的专长是：
- 构建响应式用户界面
- 实现现代前端框架(React, Vue, Angular)
- 用户体验设计和交互优化
- 前端性能优化和SEO
- 移动端适配和PWA开发

请提供完整的前端实现，包含组件化设计和最佳实践。"""
            },
            
            AgentRole.QA_ENGINEER: {
                "premium": "gpt-3.5-turbo",
                "free": "x-ai/grok-4-fast:free",
                "fallback": "nvidia/nemotron-nano-9b-v2:free",
                "system_prompt": """你是一位专业的QA测试工程师。你的职责包括：
- 设计全面的测试策略和测试用例
- 实施自动化测试框架
- 执行功能、性能和安全测试
- 缺陷跟踪和质量评估
- 测试数据管理和环境配置

请提供详细的测试计划、测试脚本和质量保证建议。"""
            },
            
            AgentRole.DEVOPS_ENGINEER: {
                "premium": "deepseek/deepseek-v3.1-terminus",
                "free": "x-ai/grok-4-fast:free",
                "fallback": "qwen/qwen3-coder-flash",
                "system_prompt": """你是一位专业的DevOps工程师。你的专业领域包括：
- CI/CD流水线设计和实施
- 容器化和微服务部署
- 云平台架构和基础设施即代码
- 监控、日志和告警系统
- 安全扫描和合规性检查

请提供完整的部署方案，包含配置文件、脚本和运维建议。"""
            },
            
            AgentRole.UI_UX_DESIGNER: {
                "premium": "gpt-3.5-turbo",
                "free": "x-ai/grok-4-fast:free",
                "fallback": "google/gemma-2-9b-it:free",
                "system_prompt": """你是一位专业的UI/UX设计师。你的设计理念包括：
- 用户体验研究和设计思维
- 界面设计和交互原型
- 可用性测试和用户反馈收集
- 设计系统和组件库构建
- 响应式设计和无障碍访问

请提供详细的设计方案，包含用户流程、界面模型和设计规范。"""
            },
            
            AgentRole.DATA_ENGINEER: {
                "premium": "qwen/qwen3-coder-plus",
                "free": "x-ai/grok-4-fast:free",
                "fallback": "deepseek/deepseek-chat-v3.1:free",
                "system_prompt": """你是一位专业的数据工程师。你的技术栈包括：
- 数据管道设计和ETL流程
- 大数据处理和数据仓库构建
- 数据质量监控和治理
- 实时数据流处理
- 数据安全和隐私保护

请提供完整的数据解决方案，包含架构设计、代码实现和数据治理策略。"""
            },
            
            AgentRole.SECURITY_ENGINEER: {
                "premium": "gpt-3.5-turbo",
                "free": "x-ai/grok-4-fast:free",
                "fallback": "deepseek/deepseek-v3.1-terminus",
                "system_prompt": """你是一位专业的安全工程师。你的安全专长包括：
- 安全威胁建模和风险评估
- 安全代码审查和漏洞扫描
- 身份认证和访问控制
- 安全监控和事件响应
- 合规性检查和安全培训

请提供全面的安全方案，包含威胁分析、防护措施和应急预案。"""
            }
        }
        
        # Free models for cost optimization (ordered by priority)
        self.free_models = [
            "x-ai/grok-4-fast:free",          # 🔥 Best free model - 2M context
            "google/gemma-2-9b-it:free",      # ✅ Reliable Google model
            "deepseek/deepseek-chat-v3.1:free", # 🚀 Good for coding tasks
            "nvidia/nemotron-nano-9b-v2:free",  # ⚡ Fast and efficient
            "openai/gpt-oss-120b:free"        # 🧠 Large parameter model
        ]
        
        # Premium models (disabled by default)
        self.premium_models = [
            "gpt-4",
            "gpt-3.5-turbo", 
            "claude-3-opus",
            "claude-3-sonnet",
            "deepseek/deepseek-v3.1-terminus",
            "qwen/qwen3-coder-plus"
        ]
        
        logger.info(f"OpenRouter integration initialized with {len(self.agent_model_preferences)} agent configurations")
    
    def make_request(self, endpoint: str, method: str = "GET", data: dict = None) -> Dict[str, Any]:
        """发起HTTP请求"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            req = urllib.request.Request(url, method=method)
            
            for key, value in self.headers.items():
                req.add_header(key, value)
            
            if data and method == "POST":
                json_data = json.dumps(data).encode('utf-8')
                req.data = json_data
            
            with urllib.request.urlopen(req, timeout=60) as response:
                response_data = response.read().decode('utf-8')
                return {
                    "success": True,
                    "status": response.status,
                    "data": json.loads(response_data)
                }
                
        except urllib.error.HTTPError as e:
            error_data = e.read().decode('utf-8')
            logger.error(f"OpenRouter HTTP error {e.code}: {error_data}")
            return {
                "success": False,
                "status": e.code,
                "error": f"HTTP {e.code}: {error_data}"
            }
        except Exception as e:
            logger.error(f"OpenRouter request failed: {str(e)}")
            return {
                "success": False,
                "status": 0,
                "error": f"Request failed: {str(e)}"
            }
    
    def get_available_models(self) -> Dict[str, Any]:
        """获取可用模型列表"""
        logger.info("Fetching available models from OpenRouter")
        result = self.make_request("models")
        
        if result["success"]:
            models = result["data"].get("data", [])
            logger.info(f"Retrieved {len(models)} models from OpenRouter")
            return {
                "success": True,
                "models": models,
                "free_models": [m for m in models if m.get('id', '').endswith(':free')],
                "total_count": len(models)
            }
        else:
            return {
                "success": False,
                "error": result["error"]
            }
    
    def chat_completion(self, messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo", 
                       max_tokens: int = 2000, temperature: float = 0.7, **kwargs) -> Dict[str, Any]:
        """执行聊天完成"""
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        logger.info(f"Making chat completion request with model: {model}")
        result = self.make_request("chat/completions", method="POST", data=payload)
        
        if result["success"]:
            response_data = result["data"]
            usage = response_data.get("usage", {})
            
            logger.info(f"Chat completion successful. Tokens used: {usage.get('total_tokens', 0)}")
            return {
                "success": True,
                "response": response_data,
                "content": response_data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                "usage": usage,
                "model_used": model
            }
        else:
            logger.error(f"Chat completion failed: {result['error']}")
            return {
                "success": False,
                "error": result["error"]
            }
    
    def execute_agent_task(self, agent_role: AgentRole, task_description: str, 
                          context: Dict[str, Any] = None, prefer_free: bool = False) -> Dict[str, Any]:
        """执行特定角色的Agent任务"""
        logger.info(f"Executing agent task for {agent_role.value}: {task_description[:100]}")
        
        # 获取该角色的模型配置
        agent_config = self.agent_model_preferences.get(agent_role)
        if not agent_config:
            logger.warning(f"No configuration found for agent role: {agent_role.value}")
            model = "x-ai/grok-4-fast:free"  # Default to best free model
            system_prompt = "你是一个专业的AI助手，请根据要求完成任务。"
        else:
            # 智能模型选择逻辑
            if prefer_free or not self.enable_premium_models:
                # 优先使用免费模型
                model = agent_config["free"]
                logger.info(f"Using FREE model for {agent_role.value}: {model}")
            else:
                # 使用付费模型
                model = agent_config["premium"] 
                logger.info(f"Using PREMIUM model for {agent_role.value}: {model}")
            
            system_prompt = agent_config["system_prompt"]
        
        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # 添加上下文信息
        if context:
            context_str = f"项目上下文：\n{json.dumps(context, ensure_ascii=False, indent=2)}\n\n"
            task_description = context_str + task_description
        
        messages.append({"role": "user", "content": task_description})
        
        # 执行请求
        start_time = datetime.now()
        result = self.chat_completion(
            messages=messages,
            model=model,
            max_tokens=3000,
            temperature=0.7
        )
        execution_time = (datetime.now() - start_time).total_seconds()
        
        if result["success"]:
            logger.info(f"Agent task completed successfully in {execution_time:.2f}s")
            return {
                "status": "completed",
                "output": result["content"],
                "model_used": result["model_used"],
                "agent_role": agent_role.value,
                "execution_info": {
                    "api_provider": "openrouter",
                    "model": result["model_used"],
                    "execution_time": execution_time,
                    "tokens_used": result["usage"],
                    "timestamp": datetime.now().isoformat()
                }
            }
        else:
            logger.error(f"Agent task failed: {result['error']}")
            
            # 智能备用模型重试逻辑
            fallback_model = None
            if agent_config:
                if model == agent_config.get("premium") and agent_config.get("free"):
                    # 付费模型失败，尝试免费模型
                    fallback_model = agent_config["free"]
                elif model == agent_config.get("free") and agent_config.get("fallback"):
                    # 主要免费模型失败，尝试备用免费模型
                    fallback_model = agent_config["fallback"]
                
                if fallback_model and fallback_model != model:
                    logger.info(f"Retrying with fallback model: {fallback_model}")
                    retry_result = self.chat_completion(
                        messages=messages,
                        model=fallback_model,
                        max_tokens=3000,
                        temperature=0.7
                    )
                
                if retry_result["success"]:
                    return {
                        "status": "completed",
                        "output": retry_result["content"],
                        "model_used": retry_result["model_used"],
                        "agent_role": agent_role.value,
                        "execution_info": {
                            "api_provider": "openrouter",
                            "model": retry_result["model_used"],
                            "execution_time": execution_time,
                            "tokens_used": retry_result["usage"],
                            "timestamp": datetime.now().isoformat(),
                            "fallback_used": True
                        }
                    }
            
            return {
                "status": "failed",
                "error": result["error"],
                "agent_role": agent_role.value,
                "execution_info": {
                    "api_provider": "openrouter",
                    "model": model,
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat()
                }
            }
    
    def get_model_pricing(self, model_id: str) -> Dict[str, Any]:
        """获取模型定价信息"""
        models_result = self.get_available_models()
        if not models_result["success"]:
            return {"success": False, "error": "Failed to fetch models"}
        
        for model in models_result["models"]:
            if model.get("id") == model_id:
                pricing = model.get("pricing", {})
                return {
                    "success": True,
                    "model_id": model_id,
                    "prompt_price": pricing.get("prompt", "N/A"),
                    "completion_price": pricing.get("completion", "N/A"),
                    "context_length": model.get("context_length", "N/A"),
                    "is_free": model_id.endswith(":free")
                }
        
        return {"success": False, "error": f"Model {model_id} not found"}
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model_id: str) -> Dict[str, Any]:
        """估算API调用成本"""
        pricing = self.get_model_pricing(model_id)
        if not pricing["success"]:
            return pricing
        
        if pricing["is_free"]:
            return {
                "success": True,
                "total_cost": 0.0,
                "prompt_cost": 0.0,
                "completion_cost": 0.0,
                "currency": "USD",
                "is_free": True
            }
        
        try:
            prompt_price = float(pricing["prompt_price"])
            completion_price = float(pricing["completion_price"])
            
            prompt_cost = (prompt_tokens / 1_000_000) * prompt_price
            completion_cost = (completion_tokens / 1_000_000) * completion_price
            total_cost = prompt_cost + completion_cost
            
            return {
                "success": True,
                "total_cost": round(total_cost, 6),
                "prompt_cost": round(prompt_cost, 6),
                "completion_cost": round(completion_cost, 6),
                "currency": "USD",
                "is_free": False
            }
        except (ValueError, TypeError):
            return {"success": False, "error": "Invalid pricing data"}
    
    def get_recommended_models(self, agent_role: AgentRole = None, prefer_free: bool = False) -> List[str]:
        """获取推荐模型列表"""
        if agent_role and agent_role in self.agent_model_preferences:
            config = self.agent_model_preferences[agent_role]
            if prefer_free:
                return [config["fallback"], config["primary"]]
            else:
                return [config["primary"], config["fallback"]]
        
        if prefer_free:
            return self.free_models[:5]
        else:
            return ["gpt-3.5-turbo", "deepseek/deepseek-v3.1-terminus", "qwen/qwen3-coder-plus"]
    
    def test_connection(self) -> Dict[str, Any]:
        """测试API连接"""
        logger.info("Testing OpenRouter API connection")
        
        test_result = self.chat_completion(
            messages=[{"role": "user", "content": "Hello! Please respond with 'Connection successful' if you receive this message."}],
            model="google/gemma-2-9b-it:free",
            max_tokens=50
        )
        
        if test_result["success"]:
            logger.info("OpenRouter API connection test successful")
            return {
                "success": True,
                "message": "OpenRouter API connection successful",
                "response": test_result["content"],
                "model_tested": test_result["model_used"],
                "tokens_used": test_result["usage"]
            }
        else:
            logger.error(f"OpenRouter API connection test failed: {test_result['error']}")
            return {
                "success": False,
                "message": "OpenRouter API connection failed",
                "error": test_result["error"]
            }
    
    def enable_premium_models(self, enable: bool = True) -> None:
        """启用或禁用付费模型"""
        self.enable_premium_models = enable
        status = "enabled" if enable else "disabled"
        logger.info(f"Premium models {status}")
    
    def is_premium_enabled(self) -> bool:
        """检查是否启用了付费模型"""
        return self.enable_premium_models
    
    def get_model_configuration(self) -> Dict[str, Any]:
        """获取当前模型配置信息"""
        return {
            "premium_models_enabled": self.enable_premium_models,
            "free_models_count": len(self.free_models),
            "premium_models_count": len(self.premium_models),
            "agents_configured": len(self.agent_model_preferences),
            "primary_free_model": self.free_models[0] if self.free_models else None,
            "model_selection_strategy": "premium" if self.enable_premium_models else "free",
            "available_free_models": self.free_models,
            "available_premium_models": self.premium_models if self.enable_premium_models else []
        }
    
    def get_agent_model_info(self, agent_role: AgentRole) -> Dict[str, Any]:
        """获取特定Agent的模型信息"""
        agent_config = self.agent_model_preferences.get(agent_role)
        if not agent_config:
            return {"error": f"No configuration found for {agent_role.value}"}
        
        current_model = agent_config["premium"] if self.enable_premium_models else agent_config["free"]
        
        return {
            "agent_role": agent_role.value,
            "current_model": current_model,
            "premium_model": agent_config["premium"],
            "free_model": agent_config["free"],
            "fallback_model": agent_config["fallback"],
            "is_using_premium": self.enable_premium_models,
            "model_costs": {
                "current": "varies" if self.enable_premium_models else "$0.00",
                "premium": "varies",
                "free": "$0.00"
            }
        }
    
    def switch_model_mode(self, mode: str) -> Dict[str, Any]:
        """切换模型模式"""
        if mode.lower() in ["free", "免费"]:
            self.enable_premium_models = False
            return {
                "success": True,
                "mode": "free",
                "message": "Switched to FREE models mode - all agents will use free models",
                "cost_impact": "Zero cost operation"
            }
        elif mode.lower() in ["premium", "付费", "paid"]:
            self.enable_premium_models = True
            return {
                "success": True,
                "mode": "premium", 
                "message": "Switched to PREMIUM models mode - agents will use paid models for better quality",
                "cost_impact": "Charges will apply based on usage"
            }
        else:
            return {
                "success": False,
                "error": f"Invalid mode: {mode}. Use 'free' or 'premium'",
                "current_mode": "premium" if self.enable_premium_models else "free"
            }

# Factory function for easy instantiation
def create_openrouter_integration(api_key: str, enable_premium: bool = False) -> OpenRouterIntegration:
    """创建OpenRouter集成实例"""
    return OpenRouterIntegration(api_key, enable_premium_models=enable_premium)