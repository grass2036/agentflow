# Basic Agent Example

This example demonstrates the core functionality of AgentFlow including:

- Agent initialization and cleanup
- Plugin system integration
- Event handling and task processing
- Configuration management
- Asynchronous task processing

## Features Demonstrated

1. **Agent Lifecycle Management**: Proper initialization and cleanup of agent resources
2. **Plugin System**: Creating and registering custom plugins
3. **Task Processing**: Asynchronous task queue processing with concurrency control
4. **Configuration**: Loading and using configuration from `agentflow.json`
5. **Logging**: Structured logging throughout the application
6. **Error Handling**: Graceful error handling and recovery

## Running the Example

```bash
# Install dependencies
pip install -r requirements.txt

# Run the example
python main.py
```

## What It Does

1. Creates a `BasicAgent` instance
2. Registers a `SimpleTaskPlugin` 
3. Initializes the plugin system
4. Adds 5 example tasks to the processing queue
5. Processes tasks concurrently (max 3 at a time)
6. Shows processing results
7. Cleans up resources

## Key Components

### BasicAgent Class
- Manages the overall agent lifecycle
- Handles task queuing and processing
- Integrates with the plugin system

### SimpleTaskPlugin Class
- Demonstrates plugin development
- Processes different types of tasks
- Maintains processing statistics

### Configuration
The `agentflow.json` file configures:
- Agent name and description
- Plugin list
- Concurrency settings
- Logging configuration

## Expected Output

```
🌊 AgentFlow Basic Agent Example
========================================

Adding 5 tasks to processing queue...
Processing tasks...

==================================================
PROCESSING RESULTS
==================================================
Total tasks processed: 5
Success rate: 100%

Task Details:
 1. Task task_001: completed
    Result: Processed data_processing task successfully
 2. Task task_002: completed  
    Result: Processed text_analysis task successfully
...
==================================================

👋 Example completed
```

## Learning Points

- How to create and configure an AgentFlow agent
- Plugin development patterns
- Asynchronous task processing
- Resource management and cleanup
- Configuration and logging best practices