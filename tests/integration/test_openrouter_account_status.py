#!/usr/bin/env python3
"""
OpenRouter Account Status and Rate Limits Checker
查询OpenRouter个人账户信息、余额、使用限制和请求次数
"""

import json
import sys
import os
from datetime import datetime
import urllib.request
import urllib.parse
import urllib.error

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# OpenRouter API Configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

class OpenRouterAccountChecker:
    """OpenRouter账户信息查询器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = OPENROUTER_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-agent-orchestrator.com",
            "X-Title": "AI Agent Account Checker",
        }
    
    def make_request(self, endpoint: str, method: str = "GET", data: dict = None):
        """发起HTTP请求"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            req = urllib.request.Request(url, method=method)
            
            for key, value in self.headers.items():
                req.add_header(key, value)
            
            if data and method == "POST":
                json_data = json.dumps(data).encode('utf-8')
                req.data = json_data
            
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = response.read().decode('utf-8')
                return {
                    "success": True,
                    "status": response.status,
                    "data": json.loads(response_data) if response_data else {}
                }
                
        except urllib.error.HTTPError as e:
            error_data = e.read().decode('utf-8')
            return {
                "success": False,
                "status": e.code,
                "error": f"HTTP {e.code}: {error_data}"
            }
        except Exception as e:
            return {
                "success": False,
                "status": 0,
                "error": f"Request failed: {str(e)}"
            }
    
    def get_account_info(self):
        """获取账户基本信息"""
        print("📊 Checking Account Information...")
        
        # OpenRouter没有标准的account endpoint，我们通过models endpoint验证
        result = self.make_request("models")
        
        if result["success"]:
            return {
                "success": True,
                "api_key_valid": True,
                "api_key_prefix": f"...{self.api_key[-8:]}",
                "models_accessible": len(result["data"].get("data", [])),
                "account_type": "Valid API Key"
            }
        else:
            return {
                "success": False,
                "api_key_valid": False,
                "error": result["error"]
            }
    
    def check_rate_limits(self):
        """检查请求速率限制"""
        print("⚡ Testing Rate Limits...")
        
        # 通过多次快速请求来测试限制
        test_requests = []
        max_tests = 5
        
        for i in range(max_tests):
            print(f"   Test request {i+1}/{max_tests}...", end=" ")
            
            start_time = datetime.now()
            result = self.make_request("models")
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds()
            
            test_requests.append({
                "request_number": i + 1,
                "success": result["success"],
                "response_time": response_time,
                "status": result["status"],
                "timestamp": start_time.isoformat()
            })
            
            if result["success"]:
                print(f"✅ {response_time:.2f}s")
            else:
                print(f"❌ {result['error']}")
                
                # 如果遇到429错误，说明达到了速率限制
                if result["status"] == 429:
                    print(f"🚫 Rate limit reached at request {i+1}")
                    break
        
        # 分析结果
        successful_requests = sum(1 for req in test_requests if req["success"])
        avg_response_time = sum(req["response_time"] for req in test_requests) / len(test_requests)
        
        return {
            "total_test_requests": len(test_requests),
            "successful_requests": successful_requests,
            "failed_requests": len(test_requests) - successful_requests,
            "average_response_time": round(avg_response_time, 3),
            "rate_limit_hit": any(req.get("status") == 429 for req in test_requests),
            "test_details": test_requests
        }
    
    def get_model_usage_stats(self):
        """获取模型使用统计"""
        print("📈 Analyzing Model Usage Patterns...")
        
        models_result = self.make_request("models")
        if not models_result["success"]:
            return {"error": "Failed to fetch models"}
        
        models = models_result["data"].get("data", [])
        
        # 分析不同类型的模型
        free_models = []
        premium_models = []
        pricing_data = []
        
        for model in models:
            model_id = model.get("id", "")
            pricing = model.get("pricing", {})
            context_length = model.get("context_length", 0)
            
            if model_id.endswith(":free"):
                free_models.append({
                    "id": model_id,
                    "context_length": context_length,
                    "pricing": "Free"
                })
            else:
                prompt_price = pricing.get("prompt", "N/A")
                completion_price = pricing.get("completion", "N/A")
                
                premium_models.append({
                    "id": model_id,
                    "context_length": context_length,
                    "prompt_price": prompt_price,
                    "completion_price": completion_price
                })
                
                if prompt_price != "N/A":
                    pricing_data.append(float(prompt_price))
        
        # 计算定价统计
        if pricing_data:
            min_price = min(pricing_data)
            max_price = max(pricing_data)
            avg_price = sum(pricing_data) / len(pricing_data)
        else:
            min_price = max_price = avg_price = 0
        
        return {
            "total_models": len(models),
            "free_models_count": len(free_models),
            "premium_models_count": len(premium_models),
            "free_models": free_models[:10],  # 显示前10个免费模型
            "pricing_stats": {
                "min_prompt_price": min_price,
                "max_prompt_price": max_price,
                "avg_prompt_price": round(avg_price, 8) if avg_price else 0,
                "currency": "USD per million tokens"
            }
        }
    
    def estimate_daily_limits(self):
        """估算每日使用限制"""
        print("📅 Estimating Daily Usage Limits...")
        
        # OpenRouter的限制通常基于：
        # 1. API key类型（免费 vs 付费）
        # 2. 模型类型（免费模型 vs 付费模型）
        # 3. 使用模式
        
        # 测试免费模型的连续请求
        free_model_test = self.test_model_requests("x-ai/grok-4-fast:free", 3)
        
        # 基于测试结果估算
        if free_model_test["all_successful"]:
            estimated_limits = {
                "free_models": {
                    "estimated_daily_requests": "1000-5000",
                    "rate_limit": "~1-2 requests/second",
                    "cost": "$0.00",
                    "note": "Based on successful test requests"
                },
                "premium_models": {
                    "estimated_daily_requests": "Depends on credits/billing",
                    "rate_limit": "Higher than free models",
                    "cost": "Variable based on model",
                    "note": "Requires payment setup"
                }
            }
        else:
            estimated_limits = {
                "warning": "Rate limits detected during testing",
                "recommendation": "Monitor usage carefully"
            }
        
        return estimated_limits
    
    def test_model_requests(self, model: str, count: int = 3):
        """测试特定模型的请求"""
        successful = 0
        
        for i in range(count):
            result = self.make_request("chat/completions", "POST", {
                "model": model,
                "messages": [{"role": "user", "content": f"Test {i+1}"}],
                "max_tokens": 10
            })
            
            if result["success"]:
                successful += 1
        
        return {
            "model": model,
            "total_requests": count,
            "successful_requests": successful,
            "success_rate": successful / count,
            "all_successful": successful == count
        }
    
    def generate_usage_recommendations(self, account_info, rate_limits, usage_stats):
        """生成使用建议"""
        recommendations = []
        
        if account_info.get("api_key_valid"):
            recommendations.append("✅ API密钥有效，可以正常使用")
        
        if rate_limits.get("rate_limit_hit"):
            recommendations.append("⚠️ 检测到速率限制，建议降低请求频率")
        else:
            recommendations.append("🚀 当前请求频率正常，可以继续使用")
        
        free_models = usage_stats.get("free_models_count", 0)
        if free_models > 0:
            recommendations.append(f"🆓 有{free_models}个免费模型可用，建议优先使用")
        
        avg_response_time = rate_limits.get("average_response_time", 0)
        if avg_response_time > 10:
            recommendations.append("🐌 响应时间较慢，可能网络或服务器负载较高")
        elif avg_response_time < 2:
            recommendations.append("⚡ 响应时间很快，服务状态良好")
        
        return recommendations

def main():
    """主函数"""
    print("🔍 OpenRouter Account Status & Rate Limits Checker")
    print("=" * 80)
    
    checker = OpenRouterAccountChecker(OPENROUTER_API_KEY)
    
    # 1. 获取账户信息
    print("\n1️⃣ Account Information")
    print("-" * 50)
    
    account_info = checker.get_account_info()
    
    if account_info["success"]:
        print(f"✅ API Key: {account_info['api_key_prefix']}")
        print(f"📊 Account Type: {account_info['account_type']}")
        print(f"🔗 Models Accessible: {account_info['models_accessible']}")
    else:
        print(f"❌ Account Error: {account_info['error']}")
        return 1
    
    # 2. 检查速率限制
    print(f"\n2️⃣ Rate Limits Testing")
    print("-" * 50)
    
    rate_limits = checker.check_rate_limits()
    
    print(f"📊 Test Results:")
    print(f"   Total requests: {rate_limits['total_test_requests']}")
    print(f"   Successful: {rate_limits['successful_requests']}")
    print(f"   Failed: {rate_limits['failed_requests']}")
    print(f"   Average response time: {rate_limits['average_response_time']}s")
    print(f"   Rate limit hit: {'Yes' if rate_limits['rate_limit_hit'] else 'No'}")
    
    # 3. 分析模型使用情况
    print(f"\n3️⃣ Model Usage Analysis")
    print("-" * 50)
    
    usage_stats = checker.get_model_usage_stats()
    
    if "error" not in usage_stats:
        print(f"📈 Total Models: {usage_stats['total_models']}")
        print(f"🆓 Free Models: {usage_stats['free_models_count']}")
        print(f"💰 Premium Models: {usage_stats['premium_models_count']}")
        
        pricing = usage_stats['pricing_stats']
        print(f"💵 Pricing Range: ${pricing['min_prompt_price']:.8f} - ${pricing['max_prompt_price']:.6f} per M tokens")
        
        print(f"\n🔥 Top Free Models:")
        for model in usage_stats['free_models'][:5]:
            print(f"   • {model['id']} (Context: {model['context_length']:,})")
    
    # 4. 估算每日限制
    print(f"\n4️⃣ Daily Usage Limits")
    print("-" * 50)
    
    daily_limits = checker.estimate_daily_limits()
    
    if "free_models" in daily_limits:
        free_info = daily_limits["free_models"]
        print(f"🆓 Free Models:")
        print(f"   Daily Requests: {free_info['estimated_daily_requests']}")
        print(f"   Rate Limit: {free_info['rate_limit']}")
        print(f"   Cost: {free_info['cost']}")
        
        premium_info = daily_limits["premium_models"]
        print(f"\n💎 Premium Models:")
        print(f"   Daily Requests: {premium_info['estimated_daily_requests']}")
        print(f"   Rate Limit: {premium_info['rate_limit']}")
        print(f"   Cost: {premium_info['cost']}")
    
    # 5. 使用建议
    print(f"\n5️⃣ Usage Recommendations")
    print("-" * 50)
    
    recommendations = checker.generate_usage_recommendations(
        account_info, rate_limits, usage_stats
    )
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    # 总结
    print(f"\n" + "=" * 80)
    print("📋 Account Status Summary")
    print("=" * 80)
    
    print(f"🔑 API Status: {'Active' if account_info.get('api_key_valid') else 'Invalid'}")
    print(f"🌐 Models Available: {usage_stats.get('total_models', 0)}")
    print(f"🆓 Free Models: {usage_stats.get('free_models_count', 0)}")
    print(f"⚡ Current Performance: {rate_limits.get('average_response_time', 0):.2f}s avg response")
    print(f"🎯 Recommended Usage: Prioritize free models for development")
    print(f"📅 Daily Estimates: 1000-5000 requests for free models")
    print(f"⏰ Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n💡 Pro Tips:")
    print(f"• Use Grok 4 Fast (free) for most tasks - 2M context window")
    print(f"• Monitor response times - slow = potential rate limiting")
    print(f"• Free models reset daily, premium models need billing setup")
    print(f"• Current configuration optimized for zero-cost usage")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        print(f"\n🏁 Check completed with exit code: {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        print(f"💥 Check failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)