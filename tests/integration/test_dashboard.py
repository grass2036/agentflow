#!/usr/bin/env python3
"""
OpenRouter Dashboard Test
测试OpenRouter账户仪表板功能
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from ai_agent.tools.openrouter_dashboard import show_openrouter_dashboard, get_account_limits

def main():
    """主函数"""
    print("🎛️ Testing OpenRouter Dashboard")
    print("=" * 80)
    
    # 显示完整仪表板
    show_openrouter_dashboard()
    
    print(f"\n" + "=" * 80)
    print("✅ Dashboard test completed")

if __name__ == "__main__":
    main()