#!/usr/bin/env python3
"""
OpenRouter 付费模型测试脚本
测试付费模型扣费情况，使用最小token请求
"""

import os
import json
import urllib.request
import urllib.parse

def load_env():
    """加载环境变量"""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

def check_balance():
    """检查当前账户余额"""
    load_env()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None
    
    url = "https://openrouter.ai/api/v1/auth/key"
    
    try:
        req = urllib.request.Request(
            url,
            headers={'Authorization': f'Bearer {api_key}'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        if 'data' in result:
            balance = result['data'].get('credit_balance', 0)
            usage = result['data'].get('usage', 0)
            return {'balance': balance, 'usage': usage}
        
    except Exception as e:
        print(f"❌ 余额查询失败: {str(e)}")
    
    return None

def test_cheap_paid_model():
    """测试最便宜的付费模型"""
    
    load_env()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ 未找到 OPENROUTER_API_KEY")
        return False
    
    # 使用比较便宜的模型进行测试
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # 选择一个相对便宜的模型，使用最少的token
    data = {
        "model": "microsoft/phi-4",  # 相对便宜的模型
        "messages": [
            {
                "role": "user",
                "content": "Hi"  # 最短的请求
            }
        ],
        "max_tokens": 5,  # 限制最大输出token
        "temperature": 0
    }
    
    try:
        print("🔄 测试付费模型 (microsoft/phi-4)...")
        print("💡 使用最小token请求以降低成本")
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}',
                'HTTP-Referer': 'https://github.com/ai-agent-test',
                'X-Title': 'AI Agent Billing Test'
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        if 'choices' in result and len(result['choices']) > 0:
            message = result['choices'][0]['message']['content']
            print(f"✅ 付费模型测试成功!")
            print(f"📝 回复: {message}")
            
            # 显示使用统计和费用
            if 'usage' in result:
                usage = result['usage']
                prompt_tokens = usage.get('prompt_tokens', 0)
                completion_tokens = usage.get('completion_tokens', 0)
                total_tokens = usage.get('total_tokens', 0)
                
                print(f"📊 Token 使用:")
                print(f"   输入: {prompt_tokens} tokens")
                print(f"   输出: {completion_tokens} tokens") 
                print(f"   总计: {total_tokens} tokens")
                
                # 估算费用 (microsoft/phi-4 大约 $0.00014 per 1k tokens)
                estimated_cost = (total_tokens / 1000) * 0.00014
                print(f"💰 预估费用: ${estimated_cost:.6f}")
            
            return True
        else:
            print(f"❌ 付费模型响应异常: {result}")
            return False
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"❌ HTTP 错误 {e.code}: {error_body}")
        
        # 如果是余额不足错误
        if e.code == 402:
            print("💡 这确认了计费系统正常工作 - 余额不足无法调用付费模型")
            return True  # 这实际上是我们想要的结果
        
        return False
    except Exception as e:
        print(f"❌ 付费模型测试失败: {str(e)}")
        return False

def main():
    print("🚀 OpenRouter 付费模型扣费测试")
    print("=" * 45)
    
    # 检查测试前余额
    print("📊 测试前余额检查:")
    balance_before = check_balance()
    if balance_before:
        print(f"💰 余额: ${balance_before['balance']:.4f}")
        print(f"📈 已用: ${balance_before['usage']:.4f}")
    else:
        print("❌ 无法获取余额信息")
        return
    
    # 测试付费模型
    print(f"\n🔄 付费模型测试:")
    success = test_cheap_paid_model()
    
    # 检查测试后余额
    print(f"\n📊 测试后余额检查:")
    balance_after = check_balance()
    if balance_after:
        print(f"💰 余额: ${balance_after['balance']:.4f}")
        print(f"📈 已用: ${balance_after['usage']:.4f}")
        
        # 计算变化
        if balance_before:
            balance_change = balance_before['balance'] - balance_after['balance']
            usage_change = balance_after['usage'] - balance_before['usage']
            
            if balance_change > 0 or usage_change > 0:
                print(f"\n💸 检测到扣费:")
                print(f"   余额减少: ${balance_change:.6f}")
                print(f"   使用增加: ${usage_change:.6f}")
                print("✅ 计费系统正常工作!")
            elif success:
                print(f"\n🔍 未检测到余额变化")
                print("可能原因: 费用太小或系统延迟")
            else:
                print(f"\n📝 测试结果: 无扣费发生")
    
    print(f"\n🎯 测试结论:")
    if balance_before and balance_before['balance'] <= 0:
        print("⚠️  账户余额为0，无法调用付费模型")
        print("💡 这证明了计费保护机制正常工作")
    elif success:
        print("✅ 付费模型可以正常调用和计费")
    else:
        print("❌ 付费模型调用失败")

if __name__ == "__main__":
    main()