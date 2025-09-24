"""
OpenRouter Agent Implementation
Specialized agent that uses OpenRouter's multi-model API for task execution
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..core.types import AgentRole
from ..core.task import Task
from ..integrations.openrouter_integration import OpenRouterIntegration

logger = logging.getLogger(__name__)

class OpenRouterAgent:
    """使用OpenRouter API的智能Agent"""
    
    def __init__(self, role: AgentRole, api_key: str = None, prefer_free_models: bool = False, 
                 enable_premium_models: bool = False):
        self.role = role
        self.prefer_free_models = prefer_free_models
        
        # 从环境变量获取API密钥
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")
        
        # 初始化OpenRouter集成
        self.openrouter = OpenRouterIntegration(
            self.api_key, 
            enable_premium_models=enable_premium_models
        )
        
        # Agent状态
        self.tasks_completed = 0
        self.total_tokens_used = 0
        self.total_cost = 0.0
        
        logger.info(f"OpenRouter Agent initialized for role: {role.value}")
    
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """执行任务"""
        logger.info(f"OpenRouter Agent {self.role.value} executing task: {task.title}")
        
        try:
            # 构建任务描述
            task_description = self._build_task_description(task)
            
            # 执行任务
            result = self.openrouter.execute_agent_task(
                agent_role=self.role,
                task_description=task_description,
                context=task.context,
                prefer_free=self.prefer_free_models
            )
            
            if result["status"] == "completed":
                # 更新统计信息
                self.tasks_completed += 1
                usage = result["execution_info"].get("tokens_used", {})
                total_tokens = usage.get("total_tokens", 0)
                self.total_tokens_used += total_tokens
                
                # 估算成本
                model_used = result["model_used"]
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                
                cost_estimate = self.openrouter.estimate_cost(
                    prompt_tokens, completion_tokens, model_used
                )
                if cost_estimate["success"]:
                    self.total_cost += cost_estimate["total_cost"]
                
                logger.info(f"Task completed successfully. Tokens used: {total_tokens}, Cost: ${cost_estimate.get('total_cost', 0):.6f}")
                
                return {
                    "success": True,
                    "output": result["output"],
                    "metadata": {
                        "agent_role": self.role.value,
                        "model_used": result["model_used"],
                        "execution_time": result["execution_info"]["execution_time"],
                        "tokens_used": total_tokens,
                        "estimated_cost": cost_estimate.get("total_cost", 0),
                        "api_provider": "openrouter"
                    }
                }
            else:
                logger.error(f"Task execution failed: {result.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "metadata": {
                        "agent_role": self.role.value,
                        "api_provider": "openrouter"
                    }
                }
                
        except Exception as e:
            logger.error(f"Exception during task execution: {str(e)}")
            return {
                "success": False,
                "error": f"Agent execution failed: {str(e)}",
                "metadata": {
                    "agent_role": self.role.value,
                    "api_provider": "openrouter"
                }
            }
    
    def _build_task_description(self, task: Task) -> str:
        """构建任务描述"""
        description = f"""
# 任务：{task.title}

## 任务描述
{task.description}

## 技术要求
{', '.join([tech.value for tech in task.tech_requirements]) if task.tech_requirements else '无特定技术要求'}

## 优先级
{task.priority.value}

## 预计工作量
{task.estimated_hours} 小时

## 依赖任务
{', '.join(task.dependencies) if task.dependencies else '无依赖'}

## 具体要求
请根据你的专业角色（{self.role.value}）提供详细、专业的解决方案。
包含具体的实施步骤、代码示例（如适用）、最佳实践建议。

## 输出格式要求
- 使用Markdown格式
- 包含清晰的章节结构
- 提供可执行的代码或配置
- 说明关键决策的理由
- 考虑可扩展性和维护性
"""
        return description.strip()
    
    def get_recommended_models(self) -> List[str]:
        """获取推荐模型"""
        return self.openrouter.get_recommended_models(
            agent_role=self.role,
            prefer_free=self.prefer_free_models
        )
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """获取Agent统计信息"""
        return {
            "role": self.role.value,
            "tasks_completed": self.tasks_completed,
            "total_tokens_used": self.total_tokens_used,
            "total_cost_usd": round(self.total_cost, 6),
            "average_tokens_per_task": round(self.total_tokens_used / max(1, self.tasks_completed), 2),
            "average_cost_per_task": round(self.total_cost / max(1, self.tasks_completed), 6),
            "recommended_models": self.get_recommended_models(),
            "prefer_free_models": self.prefer_free_models,
            "api_provider": "openrouter"
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """测试与OpenRouter的连接"""
        return self.openrouter.test_connection()
    
    def switch_to_free_models(self, enable: bool = True):
        """切换到免费模型模式"""
        self.prefer_free_models = enable
        logger.info(f"Free models preference set to: {enable}")
    
    def enable_premium_models(self, enable: bool = True):
        """启用或禁用付费模型"""
        self.openrouter.enable_premium_models(enable)
        logger.info(f"Premium models {'enabled' if enable else 'disabled'} for agent {self.role.value}")
    
    def switch_model_mode(self, mode: str) -> Dict[str, Any]:
        """切换模型模式"""
        result = self.openrouter.switch_model_mode(mode)
        if result["success"]:
            logger.info(f"Agent {self.role.value} switched to {result['mode']} mode")
        return result
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取当前Agent的模型信息"""
        return self.openrouter.get_agent_model_info(self.role)
    
    def get_model_pricing(self, model_id: str) -> Dict[str, Any]:
        """获取特定模型的定价信息"""
        return self.openrouter.get_model_pricing(model_id)

class OpenRouterAgentFactory:
    """OpenRouter Agent工厂类"""
    
    def __init__(self, api_key: str = None, prefer_free_models: bool = False, 
                 enable_premium_models: bool = False):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.prefer_free_models = prefer_free_models
        self.enable_premium_models = enable_premium_models
        
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
    
    def create_agent(self, role: AgentRole) -> OpenRouterAgent:
        """创建指定角色的Agent"""
        return OpenRouterAgent(
            role=role,
            api_key=self.api_key,
            prefer_free_models=self.prefer_free_models,
            enable_premium_models=self.enable_premium_models
        )
    
    def create_all_agents(self) -> Dict[AgentRole, OpenRouterAgent]:
        """创建所有角色的Agent"""
        agents = {}
        for role in AgentRole:
            agents[role] = self.create_agent(role)
        return agents
    
    def test_all_connections(self) -> Dict[str, Any]:
        """测试所有Agent的连接"""
        test_agent = self.create_agent(AgentRole.PROJECT_MANAGER)
        return test_agent.test_connection()

# 便捷函数
def create_openrouter_agent(role: AgentRole, api_key: str = None, prefer_free: bool = False, 
                           enable_premium: bool = False) -> OpenRouterAgent:
    """创建OpenRouter Agent实例"""
    return OpenRouterAgent(
        role=role, 
        api_key=api_key, 
        prefer_free_models=prefer_free,
        enable_premium_models=enable_premium
    )

def create_openrouter_agent_team(api_key: str = None, prefer_free: bool = False, 
                                enable_premium: bool = False) -> Dict[AgentRole, OpenRouterAgent]:
    """创建完整的OpenRouter Agent团队"""
    factory = OpenRouterAgentFactory(
        api_key=api_key, 
        prefer_free_models=prefer_free,
        enable_premium_models=enable_premium
    )
    return factory.create_all_agents()