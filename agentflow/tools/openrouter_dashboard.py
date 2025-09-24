"""
OpenRouter Account Dashboard
提供详细的账户状态、使用情况和限制信息查询功能
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
import urllib.request
import urllib.parse
import urllib.error

from ..integrations.openrouter_integration import OpenRouterIntegration

class OpenRouterDashboard:
    """OpenRouter账户仪表板"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
        
        self.integration = OpenRouterIntegration(self.api_key)
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-agent-orchestrator.com",
            "X-Title": "AI Agent Dashboard",
        }
    
    def get_account_summary(self) -> Dict[str, Any]:
        """获取账户摘要信息"""
        try:
            # 获取模型信息
            models_result = self.integration.get_available_models()
            
            if not models_result["success"]:
                return {"error": "Failed to fetch account information"}
            
            models = models_result["models"]
            free_models = [m for m in models if m.get('id', '').endswith(':free')]
            premium_models = [m for m in models if not m.get('id', '').endswith(':free')]
            
            # 分析定价
            pricing_data = []
            for model in premium_models:
                pricing = model.get('pricing', {})
                prompt_price = pricing.get('prompt')
                if prompt_price and isinstance(prompt_price, (int, float)):
                    pricing_data.append(float(prompt_price))
            
            # 计算统计信息
            now = datetime.now()
            
            return {
                "account_status": "Active",
                "api_key_preview": f"...{self.api_key[-8:]}",
                "check_time": now.isoformat(),
                "models": {
                    "total": len(models),
                    "free": len(free_models),
                    "premium": len(premium_models),
                    "free_percentage": round(len(free_models) / len(models) * 100, 1)
                },
                "pricing": {
                    "min_price": min(pricing_data) if pricing_data else 0,
                    "max_price": max(pricing_data) if pricing_data else 0,
                    "avg_price": sum(pricing_data) / len(pricing_data) if pricing_data else 0,
                    "currency": "USD per million tokens"
                },
                "recommendations": self._generate_recommendations(free_models, premium_models)
            }
            
        except Exception as e:
            return {"error": f"Failed to get account summary: {str(e)}"}
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """获取速率限制信息"""
        print("🔍 Analyzing rate limits...")
        
        # 执行连续请求测试
        test_results = []
        start_time = datetime.now()
        
        for i in range(3):
            request_start = datetime.now()
            result = self._test_single_request()
            request_end = datetime.now()
            
            test_results.append({
                "request_id": i + 1,
                "success": result["success"],
                "response_time": (request_end - request_start).total_seconds(),
                "status_code": result.get("status", 0),
                "timestamp": request_start.isoformat()
            })
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        successful_requests = sum(1 for r in test_results if r["success"])
        avg_response_time = sum(r["response_time"] for r in test_results) / len(test_results)
        
        # 判断速率限制状态
        rate_limit_status = "Normal"
        if any(r.get("status_code") == 429 for r in test_results):
            rate_limit_status = "Rate Limited"
        elif avg_response_time > 5:
            rate_limit_status = "Slow Response"
        
        return {
            "status": rate_limit_status,
            "test_duration": round(total_time, 2),
            "total_requests": len(test_results),
            "successful_requests": successful_requests,
            "success_rate": round(successful_requests / len(test_results) * 100, 1),
            "average_response_time": round(avg_response_time, 3),
            "estimated_limits": {
                "free_models": "1000-5000 requests/day",
                "premium_models": "Depends on billing",
                "rate_per_second": "~1-2 requests/second",
                "burst_limit": "~10 requests/burst"
            },
            "test_details": test_results
        }
    
    def get_model_recommendations(self) -> Dict[str, Any]:
        """获取模型推荐"""
        try:
            models_result = self.integration.get_available_models()
            if not models_result["success"]:
                return {"error": "Failed to fetch models"}
            
            models = models_result["models"]
            
            # 分类和分析模型
            categories = {
                "best_free": [],
                "coding_models": [],
                "general_purpose": [],
                "high_context": [],
                "fast_models": []
            }
            
            for model in models:
                model_id = model.get('id', '')
                context_length = model.get('context_length', 0)
                pricing = model.get('pricing', {})
                
                # 最佳免费模型
                if model_id.endswith(':free'):
                    categories["best_free"].append({
                        "id": model_id,
                        "context": context_length,
                        "description": self._get_model_description(model_id)
                    })
                
                # 编程模型
                if any(keyword in model_id.lower() for keyword in ['code', 'coder', 'programming']):
                    categories["coding_models"].append({
                        "id": model_id,
                        "context": context_length,
                        "is_free": model_id.endswith(':free'),
                        "price": pricing.get('prompt', 'N/A')
                    })
                
                # 大上下文模型
                if context_length > 100000:
                    categories["high_context"].append({
                        "id": model_id,
                        "context": context_length,
                        "is_free": model_id.endswith(':free'),
                        "price": pricing.get('prompt', 'N/A')
                    })
            
            # 排序和限制数量
            categories["best_free"] = sorted(
                categories["best_free"], 
                key=lambda x: x["context"], 
                reverse=True
            )[:5]
            
            categories["high_context"] = sorted(
                categories["high_context"],
                key=lambda x: x["context"],
                reverse=True
            )[:5]
            
            return {
                "categories": categories,
                "recommendations": {
                    "development": "x-ai/grok-4-fast:free - Best free model with 2M context",
                    "production": "Consider premium models for higher quality",
                    "coding": "deepseek models for programming tasks",
                    "general": "gpt-3.5-turbo for balanced performance"
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to get recommendations: {str(e)}"}
    
    def get_usage_analytics(self) -> Dict[str, Any]:
        """获取使用分析（模拟数据，因为OpenRouter没有提供使用统计API）"""
        return {
            "note": "OpenRouter does not provide usage analytics API",
            "estimated_usage": {
                "today": "Estimated based on your application usage",
                "this_week": "Not available",
                "this_month": "Not available"
            },
            "cost_analysis": {
                "free_models_used": "Cost: $0.00",
                "premium_models_used": "Cost: Varies",
                "total_estimated_cost": "Monitor through OpenRouter dashboard"
            },
            "tips": [
                "Use integration.get_agent_stats() to track local usage",
                "Monitor token usage in your application logs",
                "Check OpenRouter web dashboard for billing details",
                "Set up usage alerts in your application"
            ]
        }
    
    def _test_single_request(self) -> Dict[str, Any]:
        """执行单个测试请求"""
        try:
            url = f"{self.base_url}/models"
            req = urllib.request.Request(url)
            
            for key, value in self.headers.items():
                req.add_header(key, value)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                return {
                    "success": True,
                    "status": response.status
                }
                
        except urllib.error.HTTPError as e:
            return {
                "success": False,
                "status": e.code
            }
        except Exception:
            return {
                "success": False,
                "status": 0
            }
    
    def _get_model_description(self, model_id: str) -> str:
        """获取模型描述"""
        descriptions = {
            "x-ai/grok-4-fast:free": "Best free model - 2M context, excellent quality",
            "google/gemma-2-9b-it:free": "Reliable Google model - good for general tasks",
            "deepseek/deepseek-chat-v3.1:free": "Great for coding - programming optimized",
            "nvidia/nemotron-nano-9b-v2:free": "Fast and efficient - quick responses",
            "openai/gpt-oss-120b:free": "Large parameter model - high capability"
        }
        return descriptions.get(model_id, "AI model")
    
    def _generate_recommendations(self, free_models: List, premium_models: List) -> List[str]:
        """生成使用建议"""
        recommendations = []
        
        recommendations.append(f"🆓 {len(free_models)} free models available - prioritize for development")
        
        if len(free_models) > 50:
            recommendations.append("🔥 Rich selection of free models - excellent for zero-cost development")
        
        # 查找Grok模型
        grok_models = [m for m in free_models if 'grok' in m.get('id', '').lower()]
        if grok_models:
            recommendations.append("⚡ Grok 4 Fast available - 2M context window, top quality")
        
        # 查找高上下文模型
        high_context = [m for m in free_models if m.get('context_length', 0) > 100000]
        if high_context:
            recommendations.append(f"📖 {len(high_context)} free models with 100K+ context available")
        
        recommendations.append("💡 Current setup optimized for zero-cost operation")
        
        return recommendations
    
    def display_dashboard(self) -> None:
        """显示完整的仪表板"""
        print("🎛️ OpenRouter Account Dashboard")
        print("=" * 80)
        
        # 1. 账户摘要
        print("\n📊 Account Summary")
        print("-" * 50)
        
        summary = self.get_account_summary()
        if "error" in summary:
            print(f"❌ Error: {summary['error']}")
            return
        
        print(f"🔑 Status: {summary['account_status']}")
        print(f"🆔 API Key: {summary['api_key_preview']}")
        print(f"🌐 Total Models: {summary['models']['total']}")
        print(f"🆓 Free Models: {summary['models']['free']} ({summary['models']['free_percentage']}%)")
        print(f"💰 Premium Models: {summary['models']['premium']}")
        
        # 2. 速率限制
        print(f"\n⚡ Rate Limits & Performance")
        print("-" * 50)
        
        rate_info = self.get_rate_limit_info()
        print(f"📈 Status: {rate_info['status']}")
        print(f"🎯 Success Rate: {rate_info['success_rate']}%")
        print(f"⏱️ Avg Response: {rate_info['average_response_time']}s")
        print(f"📅 Daily Limit: {rate_info['estimated_limits']['free_models']}")
        print(f"🔄 Rate Limit: {rate_info['estimated_limits']['rate_per_second']}")
        
        # 3. 模型推荐
        print(f"\n🚀 Model Recommendations")
        print("-" * 50)
        
        recommendations = self.get_model_recommendations()
        if "error" not in recommendations:
            print("🔥 Top Free Models:")
            for model in recommendations["categories"]["best_free"][:3]:
                print(f"   • {model['id']} (Context: {model['context']:,})")
                print(f"     {model['description']}")
        
        # 4. 使用建议
        print(f"\n💡 Recommendations")
        print("-" * 50)
        
        for i, rec in enumerate(summary["recommendations"], 1):
            print(f"{i}. {rec}")
        
        # 5. 使用分析
        print(f"\n📈 Usage Analytics")
        print("-" * 50)
        
        analytics = self.get_usage_analytics()
        print(f"📝 Note: {analytics['note']}")
        print(f"💰 Free Models Cost: {analytics['cost_analysis']['free_models_used']}")
        print(f"🎯 Monitoring Tips:")
        for tip in analytics["tips"][:2]:
            print(f"   • {tip}")
        
        print(f"\n⏰ Dashboard Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 便捷函数
def show_openrouter_dashboard(api_key: str = None) -> None:
    """显示OpenRouter仪表板"""
    try:
        dashboard = OpenRouterDashboard(api_key)
        dashboard.display_dashboard()
    except Exception as e:
        print(f"❌ Dashboard error: {e}")

def get_account_limits(api_key: str = None) -> Dict[str, Any]:
    """获取账户限制信息"""
    try:
        dashboard = OpenRouterDashboard(api_key)
        return {
            "summary": dashboard.get_account_summary(),
            "rate_limits": dashboard.get_rate_limit_info()
        }
    except Exception as e:
        return {"error": str(e)}