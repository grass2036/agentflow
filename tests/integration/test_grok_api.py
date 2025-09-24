#!/usr/bin/env python3
"""
Grok API (XAI) 测试脚本
测试 X.AI Grok API 的基本功能
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

def test_grok_api():
    """测试 Grok API 基本功能"""
    
    # 加载环境变量
    load_env()
    
    # 获取 API 密钥
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("❌ 未找到 XAI_API_KEY")
        return False
    
    print(f"✅ 找到 XAI API 密钥: {api_key[:20]}...")
    
    # Grok API 端点 (使用正确的基础URL)
    url = "https://api.x.ai/v1/chat/completions"
    
    # 请求数据
    data = {
        "messages": [
            {
                "role": "system",
                "content": "你是Grok，一个由xAI开发的AI助手。请用中文回答。"
            },
            {
                "role": "user", 
                "content": "你好，请简单介绍一下你自己，你是什么模型？"
            }
        ],
        "model": "grok-2-1212",
        "stream": False,
        "temperature": 0.7
    }
    
    try:
        # 发送请求
        print("🔄 发送 Grok API 请求...")
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        # 检查响应
        if 'choices' in result and len(result['choices']) > 0:
            message = result['choices'][0]['message']['content']
            print(f"✅ Grok API 测试成功!")
            print(f"📝 Grok 回复: {message}")
            
            # 显示使用统计
            if 'usage' in result:
                usage = result['usage']
                print(f"📊 Token 使用: 输入={usage.get('prompt_tokens', 0)}, 输出={usage.get('completion_tokens', 0)}, 总计={usage.get('total_tokens', 0)}")
            
            return True
        else:
            print(f"❌ API 响应格式异常: {result}")
            return False
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"❌ HTTP 错误 {e.code}: {error_body}")
        return False
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return False

def test_grok_models():
    """测试获取可用模型列表"""
    
    load_env()
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("❌ 未找到 XAI_API_KEY")
        return False
    
    url = "https://api.x.ai/v1/models"
    
    try:
        print("🔄 获取 Grok 模型列表...")
        
        req = urllib.request.Request(
            url,
            headers={'Authorization': f'Bearer {api_key}'}
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        if 'data' in result:
            print("✅ 可用模型:")
            for model in result['data']:
                model_id = model.get('id', 'unknown')
                created = model.get('created', 0)
                print(f"  - {model_id} (创建时间: {created})")
            return True
        else:
            print(f"❌ 模型列表响应异常: {result}")
            return False
            
    except Exception as e:
        print(f"❌ 获取模型列表失败: {str(e)}")
        return False

def test_grok_code_generation():
    """测试 Grok 代码生成能力"""
    
    load_env()
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        return False
    
    url = "https://api.x.ai/v1/chat/completions"
    
    data = {
        "messages": [
            {
                "role": "user",
                "content": "请用Python写一个简单的计算器类，支持加减乘除四则运算。代码要简洁清晰。"
            }
        ],
        "model": "grok-2-1212",
        "stream": False,
        "temperature": 0.3
    }
    
    try:
        print("🔄 测试 Grok 代码生成...")
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
        )
        
        with urllib.request.urlopen(req, timeout=45) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        if 'choices' in result and len(result['choices']) > 0:
            code = result['choices'][0]['message']['content']
            print("✅ 代码生成成功!")
            print(f"📝 生成的代码:\n{code[:300]}...")
            return True
        else:
            print(f"❌ 代码生成失败: {result}")
            return False
            
    except Exception as e:
        print(f"❌ 代码生成测试失败: {str(e)}")
        return False

def test_api_key_format():
    """检查 XAI API 密钥格式"""
    load_env()
    api_key = os.getenv("XAI_API_KEY")
    
    if not api_key:
        print("❌ 未找到 XAI_API_KEY")
        return False
    
    # XAI API 密钥通常以 xai- 开头
    if api_key.startswith('xai-'):
        print("✅ XAI API 密钥格式正确")
        return True
    else:
        print(f"⚠️  XAI API 密钥格式可能有误: {api_key[:10]}...")
        return False

def main():
    print("🚀 Grok API (XAI) 测试")
    print("=" * 40)
    
    # 测试列表
    tests = [
        ("API 密钥格式检查", test_api_key_format),
        ("模型列表获取", test_grok_models),
        ("基本对话测试", test_grok_api),
        ("代码生成测试", test_grok_code_generation),
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
    
    if success_count == total_count:
        print("🎉 所有测试通过！Grok API 工作正常")
    elif success_count > 0:
        print("⚠️  部分测试通过，Grok API 基本可用")
    else:
        print("❌ 所有测试失败，请检查配置和网络连接")

if __name__ == "__main__":
    main()