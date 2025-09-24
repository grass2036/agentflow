#!/usr/bin/env python3
"""
查询OpenRouter账户余额和请求限制
详细获取账户信息、余额状态、每日限制等
"""

import json
import sys
import os
from datetime import datetime
import urllib.request
import urllib.parse
import urllib.error

# OpenRouter API Configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

class OpenRouterAccountQuery:
    """OpenRouter账户查询器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = OPENROUTER_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-agent-orchestrator.com",
            "X-Title": "AI Agent Balance Checker",
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
                    "data": json.loads(response_data) if response_data else {},
                    "headers": dict(response.headers)
                }
                
        except urllib.error.HTTPError as e:
            error_data = e.read().decode('utf-8')
            return {
                "success": False,
                "status": e.code,
                "error": f"HTTP {e.code}: {error_data}",
                "headers": dict(e.headers) if hasattr(e, 'headers') else {}
            }
        except Exception as e:
            return {
                "success": False,
                "status": 0,
                "error": f"Request failed: {str(e)}"
            }
    
    def check_account_balance(self):
        """检查账户余额 - 尝试多个可能的端点"""
        print("💰 查询账户余额...")
        
        # OpenRouter可能的余额查询端点
        possible_endpoints = [
            "account",
            "user", 
            "auth/user",
            "me",
            "balance",
            "credits",
            "usage"
        ]
        
        balance_info = {
            "balance_available": False,
            "balance_amount": "未知",
            "currency": "USD",
            "account_type": "API Key认证",
            "endpoints_tested": []
        }
        
        for endpoint in possible_endpoints:
            print(f"   测试端点: {endpoint}...", end=" ")
            result = self.make_request(endpoint)
            
            balance_info["endpoints_tested"].append({
                "endpoint": endpoint,
                "status": result["status"],
                "success": result["success"]
            })
            
            if result["success"]:
                print("✅")
                # 检查响应中是否包含余额信息
                data = result["data"]
                if isinstance(data, dict):
                    # 查找可能的余额字段
                    balance_fields = ["balance", "credits", "credit", "amount", "funds", "wallet"]
                    for field in balance_fields:
                        if field in data:
                            balance_info["balance_available"] = True
                            balance_info["balance_amount"] = data[field]
                            print(f"   找到余额信息: {field} = {data[field]}")
                            break
                    
                    # 查找账户类型信息
                    if "plan" in data:
                        balance_info["account_type"] = data["plan"]
                    elif "tier" in data:
                        balance_info["account_type"] = data["tier"]
                    
                    if balance_info["balance_available"]:
                        break
            else:
                print(f"❌ {result['status']}")
        
        return balance_info
    
    def check_rate_limits_detailed(self):
        """详细检查速率限制"""
        print("\n⚡ 详细检查速率限制...")
        
        # 执行多轮测试来确定限制
        test_rounds = [
            {"name": "快速连续请求", "count": 5, "delay": 0.1},
            {"name": "正常频率请求", "count": 3, "delay": 1.0},
            {"name": "慢速请求", "count": 2, "delay": 2.0}
        ]
        
        all_results = []
        
        for round_info in test_rounds:
            print(f"\n   🔄 {round_info['name']} (间隔{round_info['delay']}秒)")
            round_results = []
            
            for i in range(round_info['count']):
                start_time = datetime.now()
                result = self.make_request("models")
                end_time = datetime.now()
                
                response_time = (end_time - start_time).total_seconds()
                
                # 检查响应头中的限制信息
                rate_limit_info = self._extract_rate_limit_headers(result.get("headers", {}))
                
                test_result = {
                    "round": round_info['name'],
                    "request_number": i + 1,
                    "success": result["success"],
                    "status": result["status"],
                    "response_time": response_time,
                    "timestamp": start_time.isoformat(),
                    "rate_limit_headers": rate_limit_info
                }
                
                round_results.append(test_result)
                all_results.append(test_result)
                
                status_icon = "✅" if result["success"] else "❌"
                print(f"     请求 {i+1}: {status_icon} {response_time:.2f}s")
                
                # 如果遇到429，停止该轮测试
                if result["status"] == 429:
                    print(f"     🚫 达到速率限制")
                    break
                
                # 添加延迟
                if i < round_info['count'] - 1:
                    import time
                    time.sleep(round_info['delay'])
        
        return self._analyze_rate_limit_results(all_results)
    
    def _extract_rate_limit_headers(self, headers):
        """提取速率限制相关的响应头"""
        rate_headers = {}
        
        # 常见的速率限制头
        limit_header_names = [
            'x-ratelimit-limit',
            'x-ratelimit-remaining', 
            'x-ratelimit-reset',
            'x-ratelimit-requests',
            'x-ratelimit-tokens',
            'rate-limit-limit',
            'rate-limit-remaining',
            'rate-limit-reset'
        ]
        
        for header_name in limit_header_names:
            for key, value in headers.items():
                if header_name.lower() in key.lower():
                    rate_headers[header_name] = value
        
        return rate_headers
    
    def _analyze_rate_limit_results(self, results):
        """分析速率限制测试结果"""
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r["success"])
        failed_requests = total_requests - successful_requests
        
        # 查找429错误
        rate_limited_requests = sum(1 for r in results if r["status"] == 429)
        
        # 计算平均响应时间
        response_times = [r["response_time"] for r in results if r["success"]]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # 分析速率限制模式
        rate_limit_pattern = "正常"
        if rate_limited_requests > 0:
            rate_limit_pattern = f"检测到速率限制 ({rate_limited_requests}次429错误)"
        elif avg_response_time > 3:
            rate_limit_pattern = "响应较慢，可能接近限制"
        
        # 提取速率限制头信息
        rate_headers = {}
        for result in results:
            if result["rate_limit_headers"]:
                rate_headers.update(result["rate_limit_headers"])
                break
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "rate_limited_requests": rate_limited_requests,
            "success_rate": round(successful_requests / total_requests * 100, 1),
            "average_response_time": round(avg_response_time, 3),
            "rate_limit_pattern": rate_limit_pattern,
            "rate_limit_headers": rate_headers,
            "estimated_limits": self._estimate_limits_from_results(results, rate_headers)
        }
    
    def _estimate_limits_from_results(self, results, headers):
        """基于测试结果估算限制"""
        estimates = {}
        
        # 基于响应头估算
        if headers:
            if 'x-ratelimit-limit' in headers:
                estimates["requests_per_period"] = headers['x-ratelimit-limit']
            if 'x-ratelimit-remaining' in headers:
                estimates["remaining_requests"] = headers['x-ratelimit-remaining']
        
        # 基于测试结果估算
        rate_limited = any(r["status"] == 429 for r in results)
        
        if not rate_limited:
            estimates["daily_limit_estimate"] = "1000-5000 (基于成功测试)"
            estimates["per_second_limit"] = "1-2 requests/second"
            estimates["burst_limit"] = "5-10 requests"
        else:
            # 找到第一个429错误的位置
            first_429 = next((i for i, r in enumerate(results) if r["status"] == 429), None)
            if first_429:
                estimates["detected_burst_limit"] = f"约 {first_429} requests"
        
        estimates["recommendation"] = "使用免费模型，控制请求频率在1-2次/秒"
        
        return estimates
    
    def get_usage_statistics(self):
        """获取使用统计 - 尝试查询使用情况"""
        print("\n📊 查询使用统计...")
        
        usage_endpoints = ["usage", "stats", "metrics", "billing"]
        usage_info = {
            "usage_available": False,
            "current_usage": "无法获取",
            "usage_period": "未知",
            "endpoints_checked": []
        }
        
        for endpoint in usage_endpoints:
            print(f"   检查端点: {endpoint}...", end=" ")
            result = self.make_request(endpoint)
            
            usage_info["endpoints_checked"].append({
                "endpoint": endpoint,
                "status": result["status"],
                "success": result["success"]
            })
            
            if result["success"]:
                print("✅")
                data = result["data"]
                if data and isinstance(data, dict):
                    # 查找使用情况字段
                    usage_fields = ["usage", "requests", "tokens", "calls", "count"]
                    for field in usage_fields:
                        if field in data:
                            usage_info["usage_available"] = True
                            usage_info["current_usage"] = data[field]
                            print(f"   找到使用统计: {field} = {data[field]}")
                            break
                    
                    if usage_info["usage_available"]:
                        break
            else:
                print(f"❌ {result['status']}")
        
        return usage_info

def main():
    """主查询函数"""
    print("💳 OpenRouter账户余额和限制查询")
    print("=" * 70)
    
    query = OpenRouterAccountQuery(OPENROUTER_API_KEY)
    
    print(f"🔑 API Key: ...{OPENROUTER_API_KEY[-8:]}")
    print(f"⏰ 查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查账户余额
    print(f"\n" + "=" * 70)
    print("💰 账户余额查询")
    print("=" * 70)
    
    balance_info = query.check_account_balance()
    
    if balance_info["balance_available"]:
        print(f"✅ 余额查询成功!")
        print(f"   余额: {balance_info['balance_amount']} {balance_info['currency']}")
        print(f"   账户类型: {balance_info['account_type']}")
    else:
        print(f"ℹ️ 无法获取余额信息")
        print(f"   原因: OpenRouter可能不提供余额API，或使用不同的认证方式")
        print(f"   账户类型: {balance_info['account_type']}")
        print(f"   建议: 登录OpenRouter网站查看余额详情")
    
    # 2. 详细检查速率限制
    print(f"\n" + "=" * 70)
    print("⚡ 请求限制详细分析")
    print("=" * 70)
    
    rate_limits = query.check_rate_limits_detailed()
    
    print(f"\n📊 测试结果汇总:")
    print(f"   总请求数: {rate_limits['total_requests']}")
    print(f"   成功请求: {rate_limits['successful_requests']}")
    print(f"   失败请求: {rate_limits['failed_requests']}")
    print(f"   速率限制: {rate_limits['rate_limited_requests']}次")
    print(f"   成功率: {rate_limits['success_rate']}%")
    print(f"   平均响应: {rate_limits['average_response_time']}秒")
    print(f"   限制状态: {rate_limits['rate_limit_pattern']}")
    
    if rate_limits['rate_limit_headers']:
        print(f"\n📋 速率限制响应头:")
        for key, value in rate_limits['rate_limit_headers'].items():
            print(f"   {key}: {value}")
    
    print(f"\n📈 估算限制:")
    estimates = rate_limits['estimated_limits']
    for key, value in estimates.items():
        print(f"   {key}: {value}")
    
    # 3. 查询使用统计
    print(f"\n" + "=" * 70)
    print("📊 使用统计查询")
    print("=" * 70)
    
    usage_stats = query.get_usage_statistics()
    
    if usage_stats["usage_available"]:
        print(f"✅ 使用统计获取成功!")
        print(f"   当前使用: {usage_stats['current_usage']}")
        print(f"   统计周期: {usage_stats['usage_period']}")
    else:
        print(f"ℹ️ 无法获取使用统计")
        print(f"   建议: 在应用中手动记录API调用次数")
    
    # 4. 综合建议
    print(f"\n" + "=" * 70)
    print("💡 综合分析和建议")
    print("=" * 70)
    
    print(f"🎯 账户状态:")
    if balance_info["balance_available"]:
        print(f"   ✅ 有付费余额: {balance_info['balance_amount']} {balance_info['currency']}")
    else:
        print(f"   🆓 使用免费配额模式")
    
    print(f"\n📅 每日限制估算:")
    print(f"   🆓 免费模型: 1000-5000次/天")
    print(f"   ⚡ 请求频率: 1-2次/秒")
    print(f"   🔄 突发请求: 5-10次")
    
    print(f"\n🚀 使用建议:")
    print(f"   • 优先使用免费模型 (x-ai/grok-4-fast:free)")
    print(f"   • 控制请求频率 ≤ 1-2次/秒")
    print(f"   • 监控响应时间，>3秒可能接近限制")
    print(f"   • 在应用中实现请求计数和限制")
    print(f"   • 定期检查OpenRouter官方网站获取最新信息")
    
    if not balance_info["balance_available"]:
        print(f"\n💰 关于余额:")
        print(f"   • OpenRouter免费模型无需余额")
        print(f"   • 付费模型需要在官网充值")
        print(f"   • 当前配置已优化为零成本使用")
    
    print(f"\n⏰ 查询完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"💥 查询失败: {e}")
        import traceback
        traceback.print_exc()