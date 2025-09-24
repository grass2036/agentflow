#!/usr/bin/env python3
"""
快速查询OpenRouter每日请求限额
"""

import sys
import os

# Add AI agent path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def main():
    """查询限制信息"""
    print("🔍 查询OpenRouter每日请求限额")
    print("=" * 50)
    
    try:
        from ai_agent.tools import get_account_limits
        
        # 设置API key
        os.environ['OPENROUTER_API_KEY'] = "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"
        
        # 获取限制信息
        print("📊 正在查询账户限制...")
        limits = get_account_limits()
        
        if "error" in limits:
            print(f"❌ 查询失败: {limits['error']}")
            return
        
        # 显示详细信息
        print("\n📈 账户状态:")
        summary = limits['summary']
        print(f"   🔑 API状态: {summary['account_status']}")
        print(f"   🌐 总模型数: {summary['models']['total']}")
        print(f"   🆓 免费模型: {summary['models']['free']}")
        
        print("\n⚡ 速率限制信息:")
        rate_limits = limits['rate_limits']
        print(f"   📊 当前状态: {rate_limits['status']}")
        print(f"   🎯 成功率: {rate_limits['success_rate']}%")
        print(f"   ⏱️ 平均响应: {rate_limits['average_response_time']}秒")
        
        print("\n📅 每日请求限额:")
        estimated = rate_limits['estimated_limits']
        print(f"   🆓 免费模型: {estimated['free_models']}")
        print(f"   💰 付费模型: {estimated['premium_models']}")
        print(f"   🔄 请求频率: {estimated['rate_per_second']}")
        print(f"   ⚡ 突发限制: {estimated['burst_limit']}")
        
        # 重点信息
        print("\n" + "=" * 50)
        print("🎯 关键限制信息:")
        print(f"每日限制: {estimated['free_models']}")
        print(f"请求频率: {estimated['rate_per_second']}")
        print("=" * 50)
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已正确安装AI Agent模块")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()