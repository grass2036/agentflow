#!/usr/bin/env python3
"""
OpenRouter API 测试脚本
测试账户余额、每日额度和API功能
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

def check_account_balance():
    """检查账户余额和配额信息"""
    
    load_env()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ 未找到 OPENROUTER_API_KEY")
        return False
    
    print(f"✅ 找到 OpenRouter API 密钥: {api_key[:20]}...")
    
    # OpenRouter 账户信息端点
    url = "https://openrouter.ai/api/v1/auth/key"
    
    try:
        print("🔄 查询账户余额和配额...")
        
        req = urllib.request.Request(
            url,
            headers={'Authorization': f'Bearer {api_key}'}
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        if 'data' in result:
            data = result['data']
            
            # 账户余额
            balance = data.get('credit_balance', 0)
            print(f"💰 账户余额: ${balance:.2f}")
            
            # 使用统计
            usage = data.get('usage', 0)
            print(f"📊 已使用额度: ${usage:.4f}")
            
            # 速率限制信息
            rate_limit = data.get('rate_limit', {})
            if rate_limit:
                print(f"⏱️  速率限制: {rate_limit}")
            
            # 判断每日免费额度
            if balance >= 10.0:
                print("🎉 账户余额 ≥ $10，每日免费模型额度: 1000次")
            else:
                print("⚠️  账户余额 < $10，每日免费模型额度: 50次")
                print(f"💡 建议充值 ${10.0 - balance:.2f} 获得 1000次/天 额度")
            
            return True
        else:
            print(f"❌ 账户信息响应异常: {result}")
            return False
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"❌ HTTP 错误 {e.code}: {error_body}")
        return False
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
        return False

def test_free_model():
    """测试免费模型"""
    
    load_env()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return False
    
    # 使用免费模型
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    data = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [
            {
                "role": "user",
                "content": "你好，请简单介绍一下你自己。用中文回答。"
            }
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        print("🔄 测试免费模型 (DeepSeek R1:free)...")
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}',
                'HTTP-Referer': 'https://github.com/ai-agent-test',
                'X-Title': 'AI Agent Test'
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        if 'choices' in result and len(result['choices']) > 0:
            message = result['choices'][0]['message']['content']
            print(f"✅ 免费模型测试成功!")
            print(f"📝 DeepSeek R1 回复: {message}")
            
            # 显示使用统计
            if 'usage' in result:
                usage = result['usage']
                print(f"📊 Token 使用: 输入={usage.get('prompt_tokens', 0)}, 输出={usage.get('completion_tokens', 0)}")
            
            return True
        else:
            print(f"❌ 免费模型响应异常: {result}")
            return False
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"❌ HTTP 错误 {e.code}: {error_body}")
        return False
    except Exception as e:
        print(f"❌ 免费模型测试失败: {str(e)}")
        return False

def list_available_models():
    """列出可用模型"""
    
    load_env()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return False
    
    url = "https://openrouter.ai/api/v1/models"
    
    try:
        print("🔄 获取可用模型列表...")
        
        req = urllib.request.Request(
            url,
            headers={'Authorization': f'Bearer {api_key}'}
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        if 'data' in result:
            models = result['data']
            free_models = []
            paid_models = []
            
            for model in models:
                model_id = model.get('id', '')
                pricing = model.get('pricing', {})
                
                if ':free' in model_id:
                    free_models.append(model_id)
                elif pricing.get('prompt', '0') != '0':
                    paid_models.append(model_id)
            
            print(f"✅ 找到 {len(free_models)} 个免费模型:")
            for model in free_models[:10]:  # 显示前10个
                print(f"  - {model}")
            if len(free_models) > 10:
                print(f"  ... 还有 {len(free_models) - 10} 个免费模型")
            
            print(f"\n📊 付费模型总数: {len(paid_models)}")
            
            return True
        else:
            print(f"❌ 模型列表响应异常: {result}")
            return False
            
    except Exception as e:
        print(f"❌ 获取模型列表失败: {str(e)}")
        return False

def main():
    print("🚀 OpenRouter API 测试")
    print("=" * 40)
    
    tests = [
        ("账户余额查询", check_account_balance),
        ("可用模型列表", list_available_models),
        ("免费模型测试", test_free_model),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔄 {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print("\n⏹️ 测试被用户中断")
            break
        except Exception as e:
            print(f"❌ {test_name} 出现异常: {str(e)}")
            results.append((test_name, False))
    
    # 显示测试结果
    print("\n" + "=" * 40)
    print("📋 测试结果汇总:")
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    print(f"\n🎯 总体结果: {success_count}/{total_count} 测试通过")

if __name__ == "__main__":
    main()