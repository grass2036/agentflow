#!/usr/bin/env python3
"""
简化的 Gemini API 测试
直接使用 REST API 请求测试连接
"""

import os
import json
import urllib.request
import urllib.parse

def test_gemini_rest_api():
    """使用 REST API 测试 Gemini"""
    
    # 从 .env 文件读取 API 密钥
    api_key = None
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('GEMINI_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    break
    
    if not api_key:
        print("❌ 未找到 GEMINI_API_KEY")
        return False
    
    print(f"✅ 找到 API 密钥: {api_key[:20]}...")
    
    # Gemini API 端点 (使用 v1 版本和正确的模型名称)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    # 请求数据
    data = {
        "contents": [{
            "parts": [{
                "text": "你好，请简单介绍一下你自己。用中文回答。"
            }]
        }]
    }
    
    try:
        # 发送请求
        print("🔄 发送 API 请求...")
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        # 检查响应
        if 'candidates' in result and len(result['candidates']) > 0:
            text = result['candidates'][0]['content']['parts'][0]['text']
            print(f"✅ API 测试成功!")
            print(f"📝 Gemini 回复: {text}")
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

def test_api_key_format():
    """检查 API 密钥格式"""
    api_key = None
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('GEMINI_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    break
    
    if not api_key:
        print("❌ 未找到 GEMINI_API_KEY")
        return False
    
    # Google API 密钥通常以 AIza 开头
    if api_key.startswith('AIza'):
        print("✅ API 密钥格式正确")
        return True
    else:
        print(f"⚠️  API 密钥格式可能有误: {api_key[:10]}...")
        return False

def main():
    print("🚀 Gemini API 简单测试")
    print("=" * 40)
    
    # 检查 API 密钥格式
    print("\n1. 检查 API 密钥...")
    key_ok = test_api_key_format()
    
    if key_ok:
        # 测试 API 连接
        print("\n2. 测试 API 连接...")
        api_ok = test_gemini_rest_api()
        
        if api_ok:
            print("\n🎉 Gemini API 测试成功！")
        else:
            print("\n❌ API 测试失败")
    else:
        print("\n❌ 请检查 API 密钥配置")

if __name__ == "__main__":
    main()