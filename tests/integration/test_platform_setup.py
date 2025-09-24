#!/usr/bin/env python3
"""
AI Agent 平台配置和功能测试
检查所有必要的组件是否正确安装和配置
"""

import os
import sys
import asyncio
import importlib

def check_python_version():
    """检查Python版本"""
    print("🐍 Python版本检查:")
    version = sys.version_info
    print(f"   当前版本: Python {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 8):
        print("   ✅ Python版本满足要求 (>=3.8)")
        return True
    else:
        print("   ❌ Python版本过低，需要 >= 3.8")
        return False

def check_core_dependencies():
    """检查核心依赖"""
    print("\n📦 核心依赖检查:")
    
    required_packages = [
        ("aiohttp", "异步HTTP客户端"),
        ("pydantic", "数据验证"),
        ("typing_extensions", "类型提示扩展"),
    ]
    
    results = []
    for package, description in required_packages:
        try:
            importlib.import_module(package)
            print(f"   ✅ {package} - {description}")
            results.append(True)
        except ImportError:
            print(f"   ❌ {package} - {description} (未安装)")
            results.append(False)
    
    return all(results)

def check_optional_dependencies():
    """检查可选依赖"""
    print("\n🔧 可选依赖检查:")
    
    optional_packages = [
        ("openai", "OpenAI API客户端"),
        ("google.generativeai", "Google Gemini API"),
        ("redis", "Redis缓存"),
        ("fastapi", "Web框架"),
        ("sqlalchemy", "数据库ORM"),
        ("pytest", "测试框架"),
    ]
    
    available = []
    missing = []
    
    for package, description in optional_packages:
        try:
            importlib.import_module(package)
            print(f"   ✅ {package} - {description}")
            available.append(package)
        except ImportError:
            print(f"   ⚠️  {package} - {description} (可选，未安装)")
            missing.append(package)
    
    return available, missing

def check_ai_agent_modules():
    """检查AI Agent模块"""
    print("\n🤖 AI Agent模块检查:")
    
    try:
        from ai_agent.core.types import AgentRole, TechStack
        print("   ✅ 核心类型模块")
        
        from ai_agent.core.orchestrator import AgentOrchestrator
        print("   ✅ 编排器模块")
        
        from ai_agent.agents.base import BaseAgent
        print("   ✅ 基础Agent模块")
        
        # 测试枚举值
        print(f"   📊 支持的Agent角色: {len(AgentRole)} 个")
        print(f"   📊 支持的技术栈: {len(TechStack)} 个")
        
        return True
    except ImportError as e:
        print(f"   ❌ AI Agent模块导入失败: {e}")
        return False

def check_environment_variables():
    """检查环境变量配置"""
    print("\n🔐 环境变量检查:")
    
    # 从.env文件加载
    env_vars = {}
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    
    api_keys = [
        ("XAI_API_KEY", "X.AI Grok API密钥"),
        ("GEMINI_API_KEY", "Google Gemini API密钥"), 
        ("OPENROUTER_API_KEY", "OpenRouter API密钥"),
        ("OPENAI_API_KEY", "OpenAI API密钥"),
        ("DEEPSEEK_API_KEY", "DeepSeek API密钥"),
        ("CLAUDE_API_KEY", "Claude API密钥"),
    ]
    
    configured_apis = []
    for key, description in api_keys:
        if key in env_vars and env_vars[key] and env_vars[key] != f"your-{key.lower().replace('_', '-')}-here":
            print(f"   ✅ {key} - {description}")
            configured_apis.append(key)
        else:
            print(f"   ⚠️  {key} - {description} (未配置)")
    
    return configured_apis

async def test_basic_functionality():
    """测试基本功能"""
    print("\n🚀 基本功能测试:")
    
    try:
        from ai_agent.core.orchestrator import AgentOrchestrator
        from ai_agent.core.types import TechStack, ProjectConfig, PlatformType, ProjectComplexity
        
        # 创建编排器
        orchestrator = AgentOrchestrator()
        print("   ✅ 编排器创建成功")
        
        # 创建测试配置
        config = ProjectConfig(
            name="测试项目",
            description="基本功能测试",
            tech_stack=[TechStack.PYTHON_FASTAPI],
            target_platform=PlatformType.WEB,
            complexity=ProjectComplexity.SIMPLE,
            requirements=["基本测试"]
        )
        print("   ✅ 项目配置创建成功")
        
        # 测试项目分解
        tasks = await orchestrator.decompose_project(config)
        print(f"   ✅ 项目分解成功，生成 {len(tasks)} 个任务")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 基本功能测试失败: {e}")
        return False

def check_project_structure():
    """检查项目结构"""
    print("\n📁 项目结构检查:")
    
    required_dirs = [
        "src/ai_agent",
        "src/ai_agent/core", 
        "src/ai_agent/agents",
        "tests",
        "examples"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"   ✅ {dir_path}")
        else:
            print(f"   ❌ {dir_path} (缺失)")
            missing_dirs.append(dir_path)
    
    return len(missing_dirs) == 0

async def main():
    """主测试函数"""
    print("🚀 AI Agent 平台配置检查")
    print("=" * 50)
    
    results = {}
    
    # 运行所有检查
    results['python_version'] = check_python_version()
    results['core_deps'] = check_core_dependencies()
    available_optional, missing_optional = check_optional_dependencies()
    results['ai_agent_modules'] = check_ai_agent_modules()
    configured_apis = check_environment_variables()
    results['project_structure'] = check_project_structure()
    results['basic_functionality'] = await test_basic_functionality()
    
    # 汇总报告
    print("\n" + "=" * 50)
    print("📋 配置检查汇总:")
    
    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)
    
    for check_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {check_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 总体状态: {passed_checks}/{total_checks} 检查通过")
    
    # 建议
    print(f"\n💡 配置建议:")
    
    if len(configured_apis) > 0:
        print(f"   ✅ 已配置 {len(configured_apis)} 个API密钥")
    else:
        print("   ⚠️  建议配置至少一个API密钥以启用AI功能")
    
    if len(missing_optional) > 0:
        print(f"   📦 可选安装: pip install {' '.join(missing_optional[:3])}")
    
    if passed_checks == total_checks:
        print("\n🎉 平台配置完整，可以开始使用AI Agent!")
    else:
        print(f"\n⚠️  还有 {total_checks - passed_checks} 项需要配置")
    
    # 下一步操作建议
    print(f"\n🚀 推荐下一步操作:")
    print("   1. 运行示例: python examples/simple_demo.py")
    print("   2. 运行测试: pytest tests/")
    print("   3. 查看文档: 参考 README.md")

if __name__ == "__main__":
    asyncio.run(main())