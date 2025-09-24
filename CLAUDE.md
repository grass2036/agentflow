# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgentFlow is an **open-source AI Agent orchestration framework** built in Python for creating intelligent multi-agent systems. It provides async-first architecture, comprehensive plugin system, event-driven communication, and advanced task management with dependency resolution.

The framework is designed for building complex AI workflows where multiple specialized agents collaborate seamlessly to accomplish sophisticated tasks.

## Key Commands

### Core Development Commands
```bash
# Install for development
pip install -e .

# Run core functionality tests  
python3 run_basic_tests.py          # 7 essential tests for all core components

# CLI operations
python3 -m agentflow --version      # Version information
python3 -m agentflow status         # System status
python3 -m agentflow plugins list --available  # List all available plugins

# Quick demonstration
python3 simple_agent_example.py    # Standalone demo processing 5 tasks
```

### Testing & Quality
```bash
# Run unit tests (requires pytest installation)
pytest tests/unit/                  # Unit tests
pytest tests/integration/           # Integration tests
pytest --cov=agentflow             # Coverage analysis

# Code formatting (if tools installed)
black .                            # Code formatting  
isort .                            # Import sorting
mypy agentflow/                    # Type checking
```

### Plugin Management
```bash
python3 -m agentflow plugins list --available    # View built-in plugins
python3 -m agentflow plugins info <plugin_name>  # Plugin details
```

### Project Creation
```bash
agentflow create <project_name> --template basic    # Create new project
agentflow init --template basic                     # Initialize current directory  
```

## Core Architecture

### Main Components (`agentflow/`)

**Core Engine (`core/`):**
- `orchestrator.py` - Main coordination system with TaskScheduler, EventBus, and AgentOrchestrator
- `types.py` - Complete type system with AgentRole, TechStack, TaskPriority, ProjectConfig enums and data classes
- `task.py` - Task lifecycle management with dependencies, priorities, and execution tracking

**Agent System (`agents/`):**
- `base.py` - Abstract BaseAgent class with async execution, performance metrics, and health checking
- `project_manager.py` - Concrete agent implementation example
- All agents extend BaseAgent and implement `execute_task()` async method

**Plugin Architecture (`plugins/`):**
- `base.py` - BasePlugin abstract class with metadata, lifecycle hooks, and context management
- `manager.py` - PluginManager handles initialization, cleanup, and plugin orchestration
- `registry.py` - PluginRegistry for plugin registration, discovery, and metadata management
- `discovery.py` - Automatic plugin discovery from multiple sources (entry points, file paths)
- `builtin/` - Built-in plugins: hello_world, openai_plugin, openrouter_plugin

**CLI System (`cli/`):**
- `main.py` - Command-line interface with project creation, plugin management, status reporting
- Supports `python -m agentflow` execution via `__main__.py`

### Key Design Patterns

**Event-Driven Architecture:**
- EventBus manages publish/subscribe pattern with pattern matching and wildcard support
- AgentEvent objects carry type, source, data, and session information
- Async event processing with error isolation

**Task Orchestration:**
- TaskScheduler manages dependency resolution with topological sorting
- Parallel execution with semaphore-based concurrency control (configurable limits)
- Task states: PENDING, READY, IN_PROGRESS, COMPLETED, FAILED, BLOCKED, CANCELLED

**Plugin System:**
- BasePlugin with metadata, initialize/cleanup lifecycle, and hook registration
- Automatic discovery from entry points and file system
- PluginMetadata includes name, version, dependencies, supported configurations

**Async-First Design:**
- All task execution uses asyncio with proper semaphore limiting
- Agent communication through async event system
- Concurrent task processing with dependency respect

### Agent Roles & Capabilities

**Supported Agent Roles:** PROJECT_MANAGER, ARCHITECT, BACKEND_DEVELOPER, FRONTEND_DEVELOPER, QA_ENGINEER, DEVOPS_ENGINEER, UI_UX_DESIGNER, DATA_ENGINEER, SECURITY_ENGINEER

**Technology Stack Support:** 25+ technologies including Python, Node.js, Java, Go, C#, PHP, Rust, Vue, React, Angular, Svelte, Flutter, React Native, PostgreSQL, MySQL, MongoDB, Docker, Kubernetes, AWS, Azure, GCP.

## Development Patterns

### Adding New Agents
1. Extend BaseAgent in `agentflow/agents/`
2. Implement required `execute_task(task: Task) -> Dict[str, Any]` method
3. Define agent capabilities in `types.py` AGENT_CAPABILITIES mapping
4. Register with orchestrator: `orchestrator.register_agent(agent_instance)`
5. Add role to AgentRole enum if needed

### Creating Plugins
1. Extend BasePlugin in new file
2. Define metadata property with PluginMetadata
3. Implement initialize() and cleanup() lifecycle methods
4. Add plugin hooks and task execution logic
5. Register in pyproject.toml entry-points or place in builtin/ directory

### Project Execution Flow
1. ProjectConfig defines requirements, tech stack, complexity
2. `decompose_project()` breaks down into Task objects with dependencies
3. TaskScheduler queues tasks and resolves dependencies
4. EventBus broadcasts task lifecycle events
5. AgentOrchestrator coordinates parallel execution with concurrency limits
6. Results aggregated into deliverables by agent role

## Important Implementation Details

### Session Management
- Each project execution gets unique session ID
- Session tracking includes start/end times, task completion rates, performance metrics
- Active session monitoring with status reporting

### Type Safety & Validation
- Comprehensive type hints throughout codebase
- Pydantic integration for runtime validation
- Strict mypy configuration in pyproject.toml

### Configuration Management
- Environment variables loaded from `.env` file (API keys: OPENROUTER_API_KEY, GEMINI_API_KEY, etc.)
- Project configuration via `pyproject.toml` with plugin entry-points
- Plugin-specific configuration through PluginConfig objects

### Error Handling & Monitoring
- Comprehensive logging with structured messages
- Agent health checks with load monitoring and success rate tracking
- Performance metrics collection (tasks completed, failure rates, execution times)
- Exception isolation in event processing and task execution

### Testing Architecture
- `run_basic_tests.py` - Core functionality verification (7 essential tests)
- `tests/unit/` - Pytest-based unit tests with async support
- `tests/integration/` - API integration testing for external services
- Mock agents for testing (`create_mock_agent()` utility)

## Critical Notes

**Package Structure:** Core code is in `agentflow/` directory, not `src/` or other locations.

**CLI Usage:** Always use `python3 -m agentflow` for CLI commands, supported by `agentflow/__main__.py`.

**Plugin Discovery:** Built-in plugins auto-discovered from `agentflow/plugins/builtin/`, external plugins via entry-points.

**Task Dependencies:** Use topological sorting for dependency resolution - circular dependencies are detected and rejected.

**Async Patterns:** All agent execution and event handling is async - use `await` for task operations and event publishing.