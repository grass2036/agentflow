#!/usr/bin/env python3
"""
AgentFlow CLI - Command Line Interface
Main entry point for the AgentFlow framework
"""

import asyncio
import argparse
import sys
import json
import os
from typing import List, Optional
from pathlib import Path

import agentflow
from agentflow.plugins.manager import plugin_manager
from agentflow.plugins.registry import plugin_registry

def create_parser() -> argparse.ArgumentParser:
    """Create the command line argument parser"""
    parser = argparse.ArgumentParser(
        prog='agentflow',
        description='AgentFlow - Open-source AI Agent orchestration framework'
    )
    
    parser.add_argument('--version', action='version', version=f'AgentFlow {agentflow.get_version()}')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create project command
    create_parser = subparsers.add_parser('create', help='Create a new AgentFlow project')
    create_parser.add_argument('name', help='Project name')
    create_parser.add_argument('--template', choices=['basic', 'web', 'api', 'chatbot', 'data'], 
                              default='basic', help='Project template')
    create_parser.add_argument('--description', help='Project description')
    create_parser.add_argument('--dir', help='Project directory (default: current directory)')
    
    # Plugin management
    plugin_parser = subparsers.add_parser('plugins', help='Plugin management')
    plugin_subparsers = plugin_parser.add_subparsers(dest='plugin_action', help='Plugin actions')
    
    # Plugin list
    plugin_list_parser = plugin_subparsers.add_parser('list', help='List installed plugins')
    plugin_list_parser.add_argument('--available', action='store_true', help='Show available plugins')
    
    # Plugin install
    plugin_install_parser = plugin_subparsers.add_parser('install', help='Install a plugin')
    plugin_install_parser.add_argument('plugin_name', help='Plugin name to install')
    plugin_install_parser.add_argument('--config', help='Plugin configuration file')
    
    # Plugin remove
    plugin_remove_parser = plugin_subparsers.add_parser('remove', help='Remove a plugin')
    plugin_remove_parser.add_argument('plugin_name', help='Plugin name to remove')
    
    # Plugin info
    plugin_info_parser = plugin_subparsers.add_parser('info', help='Show plugin information')
    plugin_info_parser.add_argument('plugin_name', help='Plugin name')
    
    # Initialize command
    init_parser = subparsers.add_parser('init', help='Initialize AgentFlow in current directory')
    init_parser.add_argument('--template', choices=['basic', 'web', 'api', 'chatbot', 'data'], 
                            default='basic', help='Project template')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get AgentFlow status')
    
    # Dev command for development tools
    dev_parser = subparsers.add_parser('dev', help='Development tools')
    dev_subparsers = dev_parser.add_subparsers(dest='dev_action', help='Dev actions')
    
    dev_serve_parser = dev_subparsers.add_parser('serve', help='Start development server')
    dev_serve_parser.add_argument('--port', type=int, default=8000, help='Server port')
    dev_serve_parser.add_argument('--host', default='localhost', help='Server host')
    
    return parser

def get_project_templates() -> dict:
    """Get available project templates"""
    return {
        'basic': {
            'name': 'Basic Agent',
            'description': 'Simple AI agent template with basic functionality',
            'files': {
                'main.py': '''#!/usr/bin/env python3
"""
Basic AgentFlow Project
"""

import asyncio
from agentflow.plugins.manager import plugin_manager

async def main():
    """Main entry point"""
    print("🌊 AgentFlow Basic Project")
    
    # Initialize plugins
    await plugin_manager.initialize_all_plugins()
    
    try:
        # Your agent logic here
        print("✨ Agent is running...")
        
    finally:
        # Cleanup
        await plugin_manager.cleanup_all_plugins()

if __name__ == '__main__':
    asyncio.run(main())
''',
                'agentflow.json': '''{
  "name": "my-agent",
  "version": "1.0.0", 
  "description": "Basic AgentFlow project",
  "plugins": [],
  "config": {}
}'''
            }
        },
        'web': {
            'name': 'Web Agent',
            'description': 'Web-based AI agent with HTTP API',
            'files': {
                'main.py': '''#!/usr/bin/env python3
"""
Web AgentFlow Project
"""

import asyncio
from fastapi import FastAPI
from agentflow.plugins.manager import plugin_manager

app = FastAPI(title="AgentFlow Web Agent")

@app.get("/")
async def root():
    return {"message": "AgentFlow Web Agent is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "plugins": len(plugin_manager.registry.get_enabled_plugins())}

async def startup():
    """Initialize plugins on startup"""
    await plugin_manager.initialize_all_plugins()

async def shutdown():
    """Cleanup on shutdown"""
    await plugin_manager.cleanup_all_plugins()

if __name__ == '__main__':
    import uvicorn
    asyncio.run(startup())
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
                'agentflow.json': '''{
  "name": "web-agent",
  "version": "1.0.0",
  "description": "Web-based AgentFlow project", 
  "plugins": ["web"],
  "config": {
    "server": {
      "host": "0.0.0.0",
      "port": 8000
    }
  }
}''',
                'requirements.txt': '''fastapi>=0.100.0
uvicorn[standard]>=0.20.0
agentflow
'''
            }
        },
        'api': {
            'name': 'API Agent',
            'description': 'RESTful API agent with database integration',
            'files': {
                'main.py': '''#!/usr/bin/env python3
"""
API AgentFlow Project
"""

import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agentflow.plugins.manager import plugin_manager

app = FastAPI(title="AgentFlow API Agent")

class AgentRequest(BaseModel):
    message: str
    context: dict = {}

class AgentResponse(BaseModel):
    response: str
    status: str = "success"

@app.post("/agent/process", response_model=AgentResponse)
async def process_request(request: AgentRequest):
    """Process agent request"""
    try:
        # Your agent processing logic here
        response = f"Processed: {request.message}"
        return AgentResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/status")
async def get_status():
    """Get agent status"""
    plugin_status = await plugin_manager.health_check()
    return {
        "status": "running",
        "plugins": plugin_status,
        "active_plugins": len(plugin_manager.registry.get_enabled_plugins())
    }

if __name__ == '__main__':
    import uvicorn
    asyncio.run(plugin_manager.initialize_all_plugins())
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
                'agentflow.json': '''{
  "name": "api-agent", 
  "version": "1.0.0",
  "description": "API-based AgentFlow project",
  "plugins": ["database", "web"],
  "config": {
    "api": {
      "host": "0.0.0.0",
      "port": 8000,
      "cors_enabled": true
    }
  }
}''',
                'requirements.txt': '''fastapi>=0.100.0
uvicorn[standard]>=0.20.0
pydantic>=2.0.0
agentflow[database,web]
'''
            }
        },
        'chatbot': {
            'name': 'Chatbot Agent',
            'description': 'Conversational AI agent with chat interface',
            'files': {
                'main.py': '''#!/usr/bin/env python3
"""
Chatbot AgentFlow Project
"""

import asyncio
from agentflow.plugins.manager import plugin_manager

class ChatBot:
    def __init__(self):
        self.conversation_history = []
    
    async def process_message(self, message: str) -> str:
        """Process incoming message"""
        self.conversation_history.append({"role": "user", "content": message})
        
        # Your chatbot logic here
        response = f"I understand you said: {message}"
        
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    async def run_interactive(self):
        """Run interactive chat session"""
        print("🤖 ChatBot is ready! Type 'quit' to exit.")
        
        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if user_input:
                    response = await self.process_message(user_input)
                    print(f"Bot: {response}")
                    
            except KeyboardInterrupt:
                print("\\n👋 Goodbye!")
                break

async def main():
    """Main entry point"""
    await plugin_manager.initialize_all_plugins()
    
    try:
        chatbot = ChatBot()
        await chatbot.run_interactive()
    finally:
        await plugin_manager.cleanup_all_plugins()

if __name__ == '__main__':
    asyncio.run(main())
''',
                'agentflow.json': '''{
  "name": "chatbot-agent",
  "version": "1.0.0",
  "description": "Chatbot AgentFlow project",
  "plugins": ["langchain"],
  "config": {
    "chatbot": {
      "model": "gpt-3.5-turbo",
      "max_history": 10,
      "temperature": 0.7
    }
  }
}''',
                'requirements.txt': '''agentflow[langchain]
openai>=1.7.0
'''
            }
        },
        'data': {
            'name': 'Data Processing Agent',
            'description': 'Data analysis and processing agent',
            'files': {
                'main.py': '''#!/usr/bin/env python3
"""
Data Processing AgentFlow Project
"""

import asyncio
import pandas as pd
from agentflow.plugins.manager import plugin_manager

class DataProcessor:
    def __init__(self):
        self.data = None
    
    async def load_data(self, file_path: str):
        """Load data from file"""
        try:
            if file_path.endswith('.csv'):
                self.data = pd.read_csv(file_path)
            elif file_path.endswith('.json'):
                self.data = pd.read_json(file_path)
            else:
                raise ValueError("Unsupported file format")
            
            print(f"✅ Loaded {len(self.data)} rows of data")
            return self.data
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return None
    
    async def analyze_data(self):
        """Analyze loaded data"""
        if self.data is None:
            print("❌ No data loaded")
            return
        
        print("📊 Data Analysis:")
        print(f"Rows: {len(self.data)}")
        print(f"Columns: {len(self.data.columns)}")
        print("\\nColumn Info:")
        print(self.data.info())
        print("\\nStatistics:")
        print(self.data.describe())
    
    async def process_data(self):
        """Process data with custom logic"""
        if self.data is None:
            print("❌ No data loaded")
            return
        
        # Your data processing logic here
        processed_data = self.data.copy()
        
        print("✨ Data processing completed")
        return processed_data

async def main():
    """Main entry point"""
    await plugin_manager.initialize_all_plugins()
    
    try:
        processor = DataProcessor()
        
        # Example usage
        print("🔍 Data Processing Agent")
        
        # Load sample data or prompt for file
        sample_data = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35],
            'city': ['New York', 'London', 'Tokyo']
        })
        
        processor.data = sample_data
        await processor.analyze_data()
        await processor.process_data()
        
    finally:
        await plugin_manager.cleanup_all_plugins()

if __name__ == '__main__':
    asyncio.run(main())
''',
                'agentflow.json': '''{
  "name": "data-agent",
  "version": "1.0.0", 
  "description": "Data processing AgentFlow project",
  "plugins": ["database"],
  "config": {
    "data": {
      "input_format": ["csv", "json", "excel"],
      "output_format": "csv",
      "chunk_size": 1000
    }
  }
}''',
                'requirements.txt': '''agentflow[database]
pandas>=1.3.0
numpy>=1.21.0
'''
            }
        }
    }

def create_project_files(project_dir: Path, template_name: str, project_name: str, description: str = None):
    """Create project files from template"""
    templates = get_project_templates()
    
    if template_name not in templates:
        raise ValueError(f"Template '{template_name}' not found")
    
    template = templates[template_name]
    
    # Create project directory
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Create files from template
    for filename, content in template['files'].items():
        file_path = project_dir / filename
        
        # Replace template variables
        if filename == 'agentflow.json':
            import json
            config = json.loads(content)
            config['name'] = project_name
            if description:
                config['description'] = description
            content = json.dumps(config, indent=2)
        
        file_path.write_text(content)
        print(f"✅ Created {filename}")
    
    # Create additional directories
    (project_dir / 'plugins').mkdir(exist_ok=True)
    (project_dir / 'data').mkdir(exist_ok=True)
    
    return True

async def cmd_create(args) -> None:
    """Handle create project command"""
    print(f"🚀 Creating AgentFlow project: {args.name}")
    
    # Determine project directory
    if args.dir:
        project_dir = Path(args.dir) / args.name
    else:
        project_dir = Path.cwd() / args.name
    
    if project_dir.exists():
        print(f"❌ Directory {project_dir} already exists")
        sys.exit(1)
    
    try:
        # Create project from template
        templates = get_project_templates()
        template_info = templates[args.template]
        
        print(f"📋 Template: {template_info['name']}")
        print(f"📝 Description: {template_info['description']}")
        
        create_project_files(project_dir, args.template, args.name, args.description)
        
        print(f"\n✅ Project '{args.name}' created successfully!")
        print(f"📁 Location: {project_dir}")
        print(f"\n🚀 Next steps:")
        print(f"   cd {args.name}")
        print(f"   pip install -r requirements.txt")
        print(f"   python main.py")
        
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        sys.exit(1)

async def cmd_plugins(args) -> None:
    """Handle plugin management commands"""
    if args.plugin_action == 'list':
        if args.available:
            print("🔍 Discovering available plugins...")
            await plugin_manager.discover_and_load_plugins()
            available = plugin_registry.list_available_plugins()
            
            print("\n📦 Available Plugins:")
            print("=" * 40)
            
            if not available:
                print("No plugins found")
            else:
                for plugin_name in available:
                    metadata = plugin_registry.get_plugin_metadata(plugin_name)
                    if metadata:
                        print(f"🔸 {metadata.name} v{metadata.version}")
                        print(f"   {metadata.description}")
                        print(f"   Author: {metadata.author}")
                        if metadata.tags:
                            print(f"   Tags: {', '.join(metadata.tags)}")
                        print()
        else:
            enabled = plugin_registry.list_enabled_plugins()
            all_plugins = plugin_registry.list_active_plugins()
            
            print("🔌 Installed Plugins:")
            print("=" * 40)
            
            if not all_plugins:
                print("No plugins installed")
            else:
                for plugin_name in all_plugins:
                    status = "✅ Enabled" if plugin_name in enabled else "❌ Disabled"
                    metadata = plugin_registry.get_plugin_metadata(plugin_name)
                    if metadata:
                        print(f"🔸 {metadata.name} v{metadata.version} [{status}]")
                        print(f"   {metadata.description}")
                        print()
    
    elif args.plugin_action == 'install':
        print(f"📦 Installing plugin: {args.plugin_name}")
        
        # Load plugin configuration if provided
        config = None
        if args.config:
            try:
                with open(args.config, 'r') as f:
                    import json
                    config_data = json.load(f)
                    from agentflow.plugins.base import PluginConfig
                    config = PluginConfig(**config_data)
            except Exception as e:
                print(f"❌ Error loading config: {e}")
                return
        
        success = await plugin_manager.install_plugin(args.plugin_name, config)
        if success:
            print(f"✅ Plugin {args.plugin_name} installed successfully")
        else:
            print(f"❌ Failed to install plugin {args.plugin_name}")
    
    elif args.plugin_action == 'remove':
        print(f"🗑️  Removing plugin: {args.plugin_name}")
        success = await plugin_manager.uninstall_plugin(args.plugin_name)
        if success:
            print(f"✅ Plugin {args.plugin_name} removed successfully")
        else:
            print(f"❌ Failed to remove plugin {args.plugin_name}")
    
    elif args.plugin_action == 'info':
        metadata = plugin_registry.get_plugin_metadata(args.plugin_name)
        if not metadata:
            print(f"❌ Plugin {args.plugin_name} not found")
            return
        
        print(f"🔌 Plugin Information: {metadata.name}")
        print("=" * 50)
        print(f"Name: {metadata.name}")
        print(f"Version: {metadata.version}")
        print(f"Description: {metadata.description}")
        print(f"Author: {metadata.author}")
        if metadata.homepage:
            print(f"Homepage: {metadata.homepage}")
        if metadata.tags:
            print(f"Tags: {', '.join(metadata.tags)}")
        if metadata.dependencies:
            print(f"Dependencies: {', '.join(metadata.dependencies)}")
        print(f"Async Support: {metadata.supports_async}")
        print(f"Min AgentFlow Version: {metadata.min_agentflow_version}")

async def cmd_init(args) -> None:
    """Handle init command"""
    print("🔧 Initializing AgentFlow in current directory...")
    
    current_dir = Path.cwd()
    project_name = current_dir.name
    
    # Check if already initialized
    if (current_dir / 'agentflow.json').exists():
        print("❌ AgentFlow already initialized in this directory")
        return
    
    try:
        templates = get_project_templates()
        template_info = templates[args.template]
        
        print(f"📋 Template: {template_info['name']}")
        print(f"📝 Description: {template_info['description']}")
        
        # Create files in current directory
        for filename, content in template_info['files'].items():
            file_path = current_dir / filename
            
            if filename == 'agentflow.json':
                import json
                config = json.loads(content)
                config['name'] = project_name
                content = json.dumps(config, indent=2)
            
            file_path.write_text(content)
            print(f"✅ Created {filename}")
        
        # Create additional directories
        (current_dir / 'plugins').mkdir(exist_ok=True)
        (current_dir / 'data').mkdir(exist_ok=True)
        
        print(f"\n✅ AgentFlow initialized successfully!")
        print(f"🚀 Run 'python main.py' to start your agent")
        
    except Exception as e:
        print(f"❌ Error initializing AgentFlow: {e}")

async def cmd_dev(args) -> None:
    """Handle development commands"""
    if args.dev_action == 'serve':
        print(f"🚀 Starting AgentFlow development server...")
        print(f"📡 Host: {args.host}")
        print(f"🔌 Port: {args.port}")
        
        try:
            # Initialize plugins
            await plugin_manager.initialize_all_plugins()
            
            # Start development server
            from fastapi import FastAPI
            import uvicorn
            
            app = FastAPI(
                title="AgentFlow Development Server",
                description="Development server for AgentFlow projects",
                version=agentflow.get_version()
            )
            
            @app.get("/")
            async def root():
                return {
                    "message": "AgentFlow Development Server",
                    "version": agentflow.get_version(),
                    "status": "running"
                }
            
            @app.get("/health")
            async def health():
                plugin_health = await plugin_manager.health_check()
                return {
                    "status": "healthy",
                    "plugins": plugin_health,
                    "plugin_count": len(plugin_registry.get_enabled_plugins())
                }
            
            @app.get("/plugins")
            async def list_plugins():
                return plugin_manager.get_plugin_status()
            
            print(f"\n🌐 Server running at http://{args.host}:{args.port}")
            print(f"📚 API docs at http://{args.host}:{args.port}/docs")
            print(f"\n💡 Press Ctrl+C to stop")
            
            uvicorn.run(app, host=args.host, port=args.port, log_level="info")
            
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
        except Exception as e:
            print(f"❌ Error starting server: {e}")
        finally:
            await plugin_manager.cleanup_all_plugins()

async def cmd_status(args) -> None:
    """Handle status command"""
    print("📊 AgentFlow Status")
    print("=" * 40)
    
    # Basic info
    info = agentflow.get_info()
    print(f"🌊 {info['name']} v{info['version']}")
    print(f"📝 {info['description']}")
    print(f"🏠 {info['homepage']}")
    print()
    
    # Plugin status
    plugin_status = plugin_manager.get_plugin_status()
    print(f"🔌 Plugins:")
    print(f"   Total: {plugin_status['total_plugins']}")
    print(f"   Enabled: {plugin_status['enabled_plugins']}")
    print(f"   Initialized: {plugin_status['initialized_plugins']}")
    print()
    
    # Health check
    print("🏥 Health Check:")
    try:
        health = await plugin_manager.health_check()
        healthy_count = sum(1 for status in health.values() if status)
        total_count = len(health)
        
        if total_count > 0:
            print(f"   Healthy plugins: {healthy_count}/{total_count}")
            for plugin_name, is_healthy in health.items():
                status_icon = "✅" if is_healthy else "❌"
                print(f"   {status_icon} {plugin_name}")
        else:
            print("   No plugins to check")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
    
    # Current directory status
    print()
    print("📁 Current Directory:")
    current_dir = Path.cwd()
    agentflow_config = current_dir / 'agentflow.json'
    
    if agentflow_config.exists():
        print(f"   ✅ AgentFlow project detected")
        try:
            with open(agentflow_config, 'r') as f:
                import json
                config = json.load(f)
                print(f"   📋 Project: {config.get('name', 'Unknown')}")
                print(f"   📝 Description: {config.get('description', 'No description')}")
                print(f"   🔌 Configured plugins: {len(config.get('plugins', []))}")
        except Exception as e:
            print(f"   ⚠️  Config file exists but couldn't parse: {e}")
    else:
        print(f"   ❌ No AgentFlow project in current directory")
        print(f"   💡 Run 'agentflow init' to initialize")

def main() -> None:
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🌊 AgentFlow CLI")
    print("-" * 20)
    
    try:
        if args.command == 'create':
            asyncio.run(cmd_create(args))
        elif args.command == 'plugins':
            asyncio.run(cmd_plugins(args))
        elif args.command == 'init':
            asyncio.run(cmd_init(args))
        elif args.command == 'dev':
            asyncio.run(cmd_dev(args))
        elif args.command == 'status':
            asyncio.run(cmd_status(args))
        else:
            print(f"❌ Unknown command: {args.command}")
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"💥 CLI Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()