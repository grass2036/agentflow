# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **hybrid AI Agent system** with two main components:

1. **Python AI Agent Orchestrator** - A multi-agent system for automated software development
2. **PHP XAI Client** - A multi-language AI programming assistant that integrates with X.AI's Grok models

## Key Commands

### Python Development
```bash
# Development setup
pip install -e .[dev]
pre-commit install

# Testing
pytest                          # Run all tests
pytest tests/unit              # Unit tests only
pytest -m integration         # Integration tests only
pytest --cov=ai_agent         # With coverage

# Code quality
black .                        # Format code
isort .                        # Sort imports
mypy src/                      # Type checking
flake8                         # Linting

# Package building
python -m build               # Build distribution packages
```

### PHP XAI Client
```bash
# Basic usage
php xai_client.php                              # Demo with multiple languages
php examples/multi_language_examples.php       # Full feature demo
php tests/test_xai_client.php                  # Run tests
php examples/config_formats_demo.php           # Config format comparison

# Environment setup
cp .env.example .env           # Create environment file (add your XAI_API_KEY)
```

## Code Architecture

### Python Agent System (`src/ai_agent/`)

**Core Components:**
- `core/orchestrator.py` - Main orchestration engine with TaskScheduler, EventBus, and AgentOrchestrator
- `core/types.py` - Comprehensive type definitions for agents, tasks, tech stacks, and events
- `core/task.py` - Task management with dependencies, priorities, and lifecycle
- `agents/base.py` - Abstract base class for all agents
- `agents/project_manager.py` - Concrete implementation example

**Key Design Patterns:**
- **Event-driven architecture**: EventBus for agent communication
- **Plugin system**: Extensible agent registration via `orchestrator.register_agent()`
- **Async task execution**: Parallel task execution with semaphore-based concurrency control
- **Dependency management**: Task dependency resolution in scheduler

**Agent Roles**: PROJECT_MANAGER, ARCHITECT, BACKEND_DEVELOPER, FRONTEND_DEVELOPER, QA_ENGINEER, DEVOPS_ENGINEER, UI_UX_DESIGNER, DATA_ENGINEER, SECURITY_ENGINEER

**Tech Stack Support**: 25+ technologies across backend (Python, Node.js, Java, Go, C#, PHP, Rust), frontend (Vue, React, Angular, Svelte), mobile (Flutter, React Native), databases, and cloud platforms.

### PHP XAI Integration (`src/`, `config/`, `examples/`)

**Core Components:**
- `src/XaiClient.php` - Main client with multi-language support and automatic model selection
- `src/ConfigLoader.php` - Multi-format configuration loader (PHP, JSON, YAML)
- `config/xai_config.php` - Master configuration with 10 programming languages defined

**Multi-Language Support:**
Each language has specialized system prompts, recommended models, file extension mapping, and common task definitions for: PHP, JavaScript, Python, Java, Go, Rust, C++, Swift, Kotlin, C#.

**Configuration System:**
- Supports 3 formats: PHP (default), JSON, YAML
- Auto-detection with priority: PHP > JSON > YAML
- Language-specific parameters (temperature, model preferences)

## Development Patterns

### Adding New Agents (Python)
1. Extend `BaseAgent` class in `agents/`
2. Define capabilities in `types.py` AGENT_CAPABILITIES
3. Register with orchestrator: `orchestrator.register_agent(YourAgent())`
4. Implement `execute_task()` method with async support

### Adding New Programming Languages (PHP)
1. Add language config in `config/xai_config.php` under `programming_languages`
2. Include: name, system_prompt, recommended_model, temperature, file_extensions, common_tasks
3. Use `chatWithLanguage()` method for language-specific interactions
4. Test with file detection: `detectLanguageFromFile()`

### Project Execution Flow (Python)
1. `decompose_project()` breaks down ProjectConfig into tasks with dependencies
2. `TaskScheduler` manages task queue with priority and dependency resolution
3. Tasks execute in parallel with concurrency limits (semaphore)
4. `EventBus` broadcasts task lifecycle events
5. Results aggregated into deliverables by agent role

## Important Implementation Details

### Python System
- **Async throughout**: All task execution uses asyncio with proper semaphore limiting
- **Type safety**: Comprehensive type hints with mypy strict checking
- **Event system**: Pattern-based event subscription with wildcard support
- **Session management**: Each project execution gets unique session with tracking
- **Dependency resolution**: Topological task sorting with circular dependency detection

### PHP System  
- **Multi-format configs**: ConfigLoader automatically detects and loads PHP/JSON/YAML
- **Language detection**: File extension mapping to programming languages
- **Context injection**: Dynamic system prompt building based on language and task
- **Error handling**: Comprehensive exception handling with meaningful messages

## Configuration Management

### Environment Variables
- `XAI_API_KEY` - Required for XAI/Grok API access
- Store in `.env` file (already in .gitignore)

### Tech Stack Compatibility
Defined in `types.py` with compatibility matrix between frontend, backend, and database technologies.

### Agent Capabilities
Each agent role has defined supported tech stacks, specialties, and tools in AGENT_CAPABILITIES mapping.

## Testing Strategy

### Python Tests
- Located in `tests/` with unit/integration separation
- Async test support with pytest-asyncio
- Coverage reporting to htmlcov/
- Markers for test categorization: unit, integration, e2e, slow, external

### PHP Tests
- Simple test runner in `tests/test_xai_client.php`
- Tests multi-language functionality, file detection, config loading
- Creates/cleans temporary files for testing