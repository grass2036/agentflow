#!/usr/bin/env python3
"""
Gemini API 测试脚本
测试 Google Gemini API 的基本功能
"""

import os
import sys

# 尝试加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv 未安装，直接从环境变量读取...")
    # 如果没有 .env 文件，手动读取
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

def test_gemini_basic():
    """测试 Gemini API 基本功能"""
    try:
        # 尝试安装依赖
        try:
            import google.generativeai as genai
        except ImportError:
            print("正在尝试安装 google-generativeai...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai", "--user"])
            import google.generativeai as genai
        
        # 配置 API 密钥
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ 错误: 未找到 GEMINI_API_KEY 环境变量")
            return False
            
        genai.configure(api_key=api_key)
        print(f"✅ API 密钥已配置: {api_key[:20]}...")
        
        # 创建模型实例
        model = genai.GenerativeModel('gemini-pro')
        print("✅ Gemini Pro 模型已初始化")
        
        # 测试简单对话
        print("\n🤖 测试基本对话...")
        response = model.generate_content("你好，请用中文简单介绍一下你自己。")
        print(f"📝 回复: {response.text}")
        
        return True
        
    except ImportError:
        print("❌ 错误: google-generativeai 包未安装")
        print("请运行: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False

def test_gemini_advanced():
    """测试 Gemini API 高级功能"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-pro')
        
        # 测试代码生成
        print("\n💻 测试代码生成...")
        code_prompt = "请用Python写一个计算斐波那契数列的函数，要求简洁高效"
        response = model.generate_content(code_prompt)
        print(f"📝 生成的代码:\n{response.text}")
        
        # 测试多轮对话
        print("\n💬 测试多轮对话...")
        chat = model.start_chat(history=[])
        
        response1 = chat.send_message("我想学习AI编程，你能给我一些建议吗？")
        print(f"第1轮回复: {response1.text[:100]}...")
        
        response2 = chat.send_message("具体应该从哪些技术开始学？")
        print(f"第2轮回复: {response2.text[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 高级功能测试失败: {str(e)}")
        return False

def test_model_info():
    """测试获取模型信息"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        
        print("\n📊 可用模型列表:")
        models = genai.list_models()
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"  - {model.name}")
                
        return True
        
    except Exception as e:
        print(f"❌ 模型信息获取失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试 Gemini API...")
    print("=" * 50)
    
    # 检查环境变量
    if not os.path.exists('.env'):
        print("❌ 未找到 .env 文件")
        return
    
    # 运行测试
    tests = [
        ("基本功能测试", test_gemini_basic),
        ("模型信息测试", test_model_info), 
        ("高级功能测试", test_gemini_advanced),
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
    print("\n" + "=" * 50)
    print("📋 测试结果汇总:")
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    print(f"\n🎯 总体结果: {success_count}/{total_count} 测试通过")
    
    if success_count == total_count:
        print("🎉 所有测试通过！Gemini API 工作正常")
    else:
        print("⚠️  部分测试失败，请检查配置和网络连接")

if __name__ == "__main__":
    main()