#!/usr/bin/env python3
"""
OpenRouter API Integration Test
Tests OpenRouter API functionality and retrieves model information
"""

import asyncio
import json
import sys
import os
from datetime import datetime
import aiohttp

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# OpenRouter API Configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

class OpenRouterClient:
    """OpenRouter API Client"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = OPENROUTER_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-agent-orchestrator.com",  # Required by OpenRouter
            "X-Title": "AI Agent Orchestrator",  # Optional, for better analytics
        }
    
    async def get_models(self):
        """Get available models from OpenRouter"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/models",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        error_text = await response.text()
                        return {"error": f"HTTP {response.status}: {error_text}"}
            except Exception as e:
                return {"error": f"Request failed: {str(e)}"}
    
    async def chat_completion(self, messages, model="gpt-3.5-turbo", max_tokens=100):
        """Test chat completion"""
        async with aiohttp.ClientSession() as session:
            try:
                payload = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
                
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        error_text = await response.text()
                        return {"error": f"HTTP {response.status}: {error_text}"}
            except Exception as e:
                return {"error": f"Request failed: {str(e)}"}

async def test_openrouter_functionality():
    """Test OpenRouter API functionality"""
    print("🚀 OpenRouter API Test")
    print("=" * 60)
    
    client = OpenRouterClient(OPENROUTER_API_KEY)
    
    # Test 1: Get available models
    print("\n📋 Test 1: Getting Available Models")
    print("-" * 40)
    
    models_response = await client.get_models()
    
    if "error" in models_response:
        print(f"❌ Failed to get models: {models_response['error']}")
        return False
    
    models = models_response.get('data', [])
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
        print(f"      Context: {context_length:,} tokens" if context_length != 'N/A' else f"      Context: {context_length}")
        print(f"      Price: ${prompt_price}/M prompt, ${completion_price}/M completion")
        print()
    
    # Test 2: Chat completion with popular models
    print("\n💬 Test 2: Chat Completion Tests")
    print("-" * 40)
    
    test_models = [
        "gpt-3.5-turbo",
        "gpt-4",
        "claude-3-haiku",
        "meta-llama/llama-3.1-8b-instruct:free",
        "google/gemma-2-9b-it:free"
    ]
    
    test_message = [
        {"role": "user", "content": "Hello! Please introduce yourself and tell me what you can do in exactly 50 words."}
    ]
    
    successful_tests = 0
    
    for model_name in test_models:
        print(f"\n🤖 Testing model: {model_name}")
        
        result = await client.chat_completion(test_message, model=model_name, max_tokens=150)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            continue
        
        # Extract response and usage information
        choices = result.get('choices', [])
        usage = result.get('usage', {})
        
        if choices:
            message = choices[0].get('message', {}).get('content', 'No content')
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', 0)
            
            print(f"✅ Success!")
            print(f"📝 Response: {message[:100]}{'...' if len(message) > 100 else ''}")
            print(f"🔢 Token Usage:")
            print(f"   - Prompt tokens: {prompt_tokens}")
            print(f"   - Completion tokens: {completion_tokens}")
            print(f"   - Total tokens: {total_tokens}")
            
            successful_tests += 1
        else:
            print(f"❌ No response content received")
    
    # Test 3: Get account usage/credits (if available)
    print(f"\n💳 Test 3: Account Information")
    print("-" * 40)
    
    # Note: OpenRouter doesn't have a standard credits endpoint, 
    # but we can check if our requests are working
    print(f"✅ API Key is working - {successful_tests}/{len(test_models)} models tested successfully")
    
    # Summary
    print(f"\n" + "=" * 60)
    print("📊 OpenRouter API Test Summary")
    print("=" * 60)
    print(f"🔑 API Key: ...{OPENROUTER_API_KEY[-8:]}")
    print(f"🌐 Base URL: {OPENROUTER_BASE_URL}")
    print(f"📋 Available Models: {len(models)}")
    print(f"🧪 Successful Tests: {successful_tests}/{len(test_models)}")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if successful_tests > 0:
        print(f"\n🎉 OpenRouter integration is working!")
        print(f"💡 You can now use OpenRouter models in your AI Agent system")
        print(f"🔧 Popular free models available: meta-llama, google/gemma")
        print(f"💰 Premium models available: GPT-4, Claude-3, and more")
    else:
        print(f"\n❌ OpenRouter integration needs attention")
        print(f"🔍 Check API key validity and network connectivity")
    
    return successful_tests > 0

async def main():
    """Main test function"""
    try:
        success = await test_openrouter_functionality()
        return 0 if success else 1
    except Exception as e:
        print(f"💥 Test failed with exception: {e}")
        return 1

if __name__ == "__main__":
    print("🧪 OpenRouter API Integration Test")
    print("Testing API connectivity and model availability")
    print("=" * 80)
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)