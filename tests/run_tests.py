#!/usr/bin/env python3
"""
Test Runner for AI Agent Orchestrator
Provides easy access to run different types of tests
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and show results"""
    print(f"\n🚀 {description}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"⚠️ Warnings/Errors:\n{result.stderr}")
            
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
        else:
            print(f"❌ {description} failed with exit code {result.returncode}")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"💥 Error running {description}: {e}")
        return False

def main():
    """Main test runner"""
    print("🧪 AI Agent Orchestrator Test Suite")
    print("=" * 60)
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print(f"📂 Working directory: {os.getcwd()}")
    print(f"🐍 Python version: {sys.version}")
    
    # Test categories
    tests = {
        "demos": {
            "description": "System Demonstrations",
            "commands": [
                ("python tests/demos/demo_ai_agents.py", "Multi-Agent Coordination Demo")
            ]
        },
        "integration": {
            "description": "Integration Tests", 
            "commands": [
                ("python tests/integration/basic_xai_test.py", "XAI Basic Connection Test"),
                ("python tests/integration/test_openrouter_basic.py", "OpenRouter Basic Test"),
                ("python tests/integration/test_grok_premium_toggle.py", "Grok Premium Toggle Test"),
                ("python tests/integration/test_dashboard.py", "Dashboard Test"),
            ]
        },
        "unit": {
            "description": "Unit Tests",
            "commands": [
                ("python -m pytest tests/unit/ -v", "Unit Test Suite")
            ]
        },
        "tools": {
            "description": "Account Tools & Utilities",
            "commands": [
                ("python tests/tools/check_limits.py", "Check Account Limits"),
                ("python tests/tools/detailed_limits_check.py", "Detailed Limits Analysis"),
            ]
        },
        "generated": {
            "description": "Generated Code Validation",
            "commands": [
                ("python -m py_compile tests/generated/grok_generated_email_sender.py", "Validate Generated Email Sender")
            ]
        }
    }
    
    # Check if specific test type was requested
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        if test_type in tests:
            print(f"\n🎯 Running {tests[test_type]['description']}")
            success = True
            for cmd, desc in tests[test_type]['commands']:
                if not run_command(cmd, desc):
                    success = False
            
            if success:
                print(f"\n🎉 {tests[test_type]['description']} completed successfully!")
            else:
                print(f"\n❌ Some {tests[test_type]['description']} failed!")
            
            return 0 if success else 1
        else:
            print(f"❌ Unknown test type: {test_type}")
            print(f"Available types: {', '.join(tests.keys())}")
            return 1
    
    # Run all tests
    print("\n🎯 Running All Test Categories")
    overall_success = True
    
    for test_type, test_info in tests.items():
        print(f"\n" + "=" * 60)
        print(f"📋 {test_info['description']}")
        print("=" * 60)
        
        category_success = True
        for cmd, desc in test_info['commands']:
            if not run_command(cmd, desc):
                category_success = False
                overall_success = False
        
        if category_success:
            print(f"✅ {test_info['description']} - All tests passed")
        else:
            print(f"❌ {test_info['description']} - Some tests failed")
    
    # Final summary
    print("\n" + "=" * 60)
    print("🏁 Test Suite Summary")
    print("=" * 60)
    
    if overall_success:
        print("🎉 All tests completed successfully!")
        print("✓ System demonstrations working")
        print("✓ Integration tests passing")
        print("✓ Unit tests passing")
        print("✓ Generated code validates")
    else:
        print("❌ Some tests failed!")
        print("📋 Check the output above for details")
    
    return 0 if overall_success else 1

def show_help():
    """Show usage help"""
    print("🧪 AI Agent Test Runner")
    print("=" * 30)
    print()
    print("Usage:")
    print("  python tests/run_tests.py [test_type]")
    print()
    print("Test Types:")
    print("  demos       - System demonstrations")
    print("  integration - Integration tests")
    print("  unit        - Unit tests")
    print("  generated   - Generated code validation")
    print("  (no args)   - Run all tests")
    print()
    print("Examples:")
    print("  python tests/run_tests.py demos")
    print("  python tests/run_tests.py integration")
    print("  python tests/run_tests.py")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h", "help"]:
        show_help()
        sys.exit(0)
    
    sys.exit(main())