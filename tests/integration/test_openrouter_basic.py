#!/usr/bin/env python3
"""
OpenRouter API Integration Test (Standard Library Only)
Tests OpenRouter API functionality and retrieves model information
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

class OpenRouterClient:
    """OpenRouter API Client using standard library"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = OPENROUTER_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-agent-orchestrator.com",  # Required by OpenRouter
            "X-Title": "AI Agent Orchestrator",  # Optional, for better analytics
        }
    
    def make_request(self, endpoint: str, method: str = "GET", data: dict = None):
        """Make HTTP request to OpenRouter API"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            # Prepare request
            req = urllib.request.Request(url, method=method)
            
            # Add headers
            for key, value in self.headers.items():
                req.add_header(key, value)
            
            # Add data for POST requests
            if data and method == "POST":
                json_data = json.dumps(data).encode('utf-8')
                req.data = json_data
            
            # Make request
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = response.read().decode('utf-8')
                return {
                    "success": True,
                    "status": response.status,
                    "data": json.loads(response_data)
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
    
    def get_models(self):
        """Get available models from OpenRouter"""
        return self.make_request("models")
    
    def chat_completion(self, messages, model="gpt-3.5-turbo", max_tokens=100):
        """Test chat completion"""
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        return self.make_request("chat/completions", method="POST", data=payload)

def test_openrouter_functionality():
    """Test OpenRouter API functionality"""
    print("🚀 OpenRouter API Test")
    print("=" * 60)
    
    client = OpenRouterClient(OPENROUTER_API_KEY)
    
    # Test 1: Get available models
    print("\n📋 Test 1: Getting Available Models")
    print("-" * 40)
    
    models_response = client.get_models()
    
    if not models_response["success"]:
        print(f"❌ Failed to get models: {models_response['error']}")
        return False
    
    models = models_response["data"].get('data', [])
    print(f"✅ Found {len(models)} available models")
    
    # Show top 10 popular models
    print(f"\n🔥 Top 10 Available Models:")
    for i, model in enumerate(models[:10]):
        model_id = model.get('id', 'Unknown')
        context_length = model.get('context_length', 'N/A')
        pricing = model.get('pricing', {})
        prompt_price = pricing.get('prompt', 'N/A')
        completion_price = pricing.get('completion', 'N/A')
        
        print(f"  {i+1:2d}. {model_id}")
        print(f"      Context: {context_length:,} tokens" if isinstance(context_length, int) else f"      Context: {context_length}")
        print(f"      Price: ${prompt_price}/M prompt, ${completion_price}/M completion")
        print()
    
    # Show free models
    free_models = [m for m in models if m.get('id', '').endswith(':free')]
    print(f"\n🆓 Free Models Available ({len(free_models)}):")
    for model in free_models[:5]:  # Show first 5 free models
        print(f"  • {model.get('id', 'Unknown')}")
    
    # Test 2: Chat completion with popular models
    print(f"\n💬 Test 2: Chat Completion Tests")
    print("-" * 40)
    
    test_models = [
        "meta-llama/llama-3.1-8b-instruct:free",
        "google/gemma-2-9b-it:free",
        "gpt-3.5-turbo",
        "claude-3-haiku"
    ]
    
    test_message = [
        {"role": "user", "content": "Hello! Please introduce yourself and tell me what you can do in exactly 30 words."}
    ]
    
    successful_tests = 0
    
    for model_name in test_models:
        print(f"\n🤖 Testing model: {model_name}")
        
        result = client.chat_completion(test_message, model=model_name, max_tokens=100)
        
        if not result["success"]:
            print(f"❌ Error: {result['error']}")
            continue
        
        # Extract response and usage information
        response_data = result["data"]
        choices = response_data.get('choices', [])
        usage = response_data.get('usage', {})
        
        if choices:
            message = choices[0].get('message', {}).get('content', 'No content')
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', 0)
            
            print(f"✅ Success!")
            print(f"📝 Response: {message[:80]}{'...' if len(message) > 80 else ''}")
            print(f"🔢 Token Usage:")
            print(f"   - Prompt tokens: {prompt_tokens}")
            print(f"   - Completion tokens: {completion_tokens}")
            print(f"   - Total tokens: {total_tokens}")
            
            successful_tests += 1
        else:
            print(f"❌ No response content received")
    
    # Summary
    print(f"\n" + "=" * 60)
    print("📊 OpenRouter API Test Summary")
    print("=" * 60)
    print(f"🔑 API Key: ...{OPENROUTER_API_KEY[-8:]}")
    print(f"🌐 Base URL: {OPENROUTER_BASE_URL}")
    print(f"📋 Available Models: {len(models)}")
    print(f"🆓 Free Models: {len(free_models)}")
    print(f"🧪 Successful Tests: {successful_tests}/{len(test_models)}")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if successful_tests > 0:
        print(f"\n🎉 OpenRouter integration is working!")
        print(f"💡 You can now use OpenRouter models in your AI Agent system")
        print(f"🔧 Popular free models available: meta-llama, google/gemma")
        print(f"💰 Premium models available: GPT-4, Claude-3, and more")
        
        # Show token costs for different models
        print(f"\n💰 Token Cost Information:")
        for model in models[:5]:
            model_id = model.get('id', 'Unknown')
            pricing = model.get('pricing', {})
            if pricing:
                prompt_price = pricing.get('prompt', 'N/A')
                completion_price = pricing.get('completion', 'N/A')
                print(f"  {model_id}: ${prompt_price}/M prompt, ${completion_price}/M completion")
    else:
        print(f"\n❌ OpenRouter integration needs attention")
        print(f"🔍 Check API key validity and network connectivity")
    
    return successful_tests > 0

def main():
    """Main test function"""
    try:
        success = test_openrouter_functionality()
        return 0 if success else 1
    except Exception as e:
        print(f"💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("🧪 OpenRouter API Integration Test")
    print("Testing API connectivity and model availability")
    print("=" * 80)
    
    exit_code = main()
    print(f"\n🏁 Test completed with exit code: {exit_code}")
    sys.exit(exit_code)