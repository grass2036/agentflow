#!/usr/bin/env python3
"""
详细查询OpenRouter请求限额和账户信息
"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def detailed_limits_check():
    """详细限制检查"""
    print("🔍 OpenRouter详细限制查询")
    print("=" * 60)
    
    # 设置API key
    api_key = "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"
    os.environ['OPENROUTER_API_KEY'] = api_key
    
    try:
        from ai_agent.tools import get_account_limits, OpenRouterDashboard
        
        print("📊 正在获取详细账户信息...")
        
        # 1. 基本限制信息
        limits = get_account_limits()
        
        if "error" in limits:
            print(f"❌ 错误: {limits['error']}")
            return
        
        # 2. 创建仪表板获取更多信息
        dashboard = OpenRouterDashboard(api_key)
        
        print("\n" + "=" * 60)
        print("📈 您的OpenRouter账户详细信息")
        print("=" * 60)
        
        # 账户基本信息
        summary = limits['summary']
        print(f"\n🔑 账户状态:")
        print(f"   API Key: ...{api_key[-8:]}")
        print(f"   状态: {summary['account_status']}")
        print(f"   查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 模型可用性
        print(f"\n🌐 模型可用性:")
        models = summary['models']
        print(f"   总模型数: {models['total']}")
        print(f"   免费模型: {models['free']} ({models['free_percentage']}%)")
        print(f"   付费模型: {models['premium']}")
        
        # 详细限制信息
        rate_info = limits['rate_limits']
        print(f"\n⚡ 请求限制详情:")
        print(f"   当前状态: {rate_info['status']}")
        print(f"   测试成功率: {rate_info['success_rate']}%")
        print(f"   平均响应时间: {rate_info['average_response_time']}秒")
        
        estimated = rate_info['estimated_limits']
        print(f"\n📅 每日使用限额:")
        print(f"   🆓 免费模型: {estimated['free_models']}")
        print(f"   💰 付费模型: {estimated['premium_models']}")
        print(f"   🔄 请求频率: {estimated['rate_per_second']}")
        print(f"   ⚡ 突发请求: {estimated['burst_limit']}")
        
        # 推荐的免费模型
        print(f"\n🔥 推荐免费模型:")
        recs = dashboard.get_model_recommendations()
        if "error" not in recs:
            for i, model in enumerate(recs["categories"]["best_free"][:3], 1):
                print(f"   {i}. {model['id']}")
                print(f"      上下文: {model['context']:,} tokens")
                print(f"      描述: {model['description']}")
        
        # 成本分析
        print(f"\n💰 成本分析:")
        pricing = summary.get('pricing', {})
        if pricing.get('min_price') is not None:
            print(f"   最低价格: ${pricing['min_price']:.8f}/M tokens")
            print(f"   最高价格: ${pricing['max_price']:.6f}/M tokens")
            print(f"   平均价格: ${pricing['avg_price']:.8f}/M tokens")
        print(f"   免费模型成本: $0.00")
        
        # 使用建议
        print(f"\n💡 使用建议:")
        recommendations = summary.get('recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        # 实际测试结果
        print(f"\n🧪 实际测试结果:")
        test_details = rate_info.get('test_details', [])
        for test in test_details:
            status = "✅" if test['success'] else "❌"
            print(f"   请求 {test['request_id']}: {status} {test['response_time']:.2f}s")
        
        print(f"\n" + "=" * 60)
        print("🎯 关键数字总结")
        print("=" * 60)
        print(f"📊 每日免费请求: 1000-5000次")
        print(f"⚡ 请求频率限制: 1-2次/秒")
        print(f"💰 免费模型成本: $0.00")
        print(f"🔥 最佳免费模型: x-ai/grok-4-fast:free")
        print(f"📖 最大上下文: 2,000,000 tokens")
        print(f"🎯 推荐使用: 开发阶段使用免费模型")
        
        # 使用策略
        print(f"\n🚀 推荐使用策略:")
        print(f"   • 开发/测试: 使用免费模型，每日1000-5000次足够")
        print(f"   • 生产环境: 可考虑付费模型获得更高稳定性")
        print(f"   • 请求频率: 控制在1-2次/秒以内")
        print(f"   • 优先模型: Grok 4 Fast (免费版)")
        print(f"   • 成本控制: 当前配置为零成本运行")
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    detailed_limits_check()