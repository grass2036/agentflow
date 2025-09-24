#!/usr/bin/env python3
"""
Web API Agent Example
====================

A web-based AI agent demonstrating:
- FastAPI integration with AgentFlow
- REST API endpoints for agent interaction
- Health checks and monitoring
- Plugin system integration
- Request/response handling
- API documentation with Swagger UI
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agentflow.plugins.manager import plugin_manager
from agentflow.plugins.base import BasePlugin, PluginMetadata, PluginContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Request/Response Models
class AgentRequest(BaseModel):
    """Request model for agent processing."""
    message: str
    context: Dict = {}
    priority: int = 5  # 1-10, higher = more priority


class AgentResponse(BaseModel):
    """Response model for agent processing."""
    response: str
    status: str = "success"
    task_id: str
    processed_at: datetime
    context: Dict = {}


class TaskStatus(BaseModel):
    """Task status model."""
    task_id: str
    status: str  # pending, processing, completed, failed
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict] = None


class PluginInfo(BaseModel):
    """Plugin information model."""
    name: str
    version: str
    description: str
    status: str
    health: bool


# Plugin for web processing
class WebProcessingPlugin(BasePlugin):
    """Plugin for processing web requests."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="web_processing",
            version="1.0.0",
            description="Web request processing plugin",
            author="AgentFlow Examples",
            tags=["web", "api", "processing"]
        )
    
    async def initialize(self) -> None:
        logger.info("Initializing WebProcessing plugin")
        self.request_count = 0
        self.responses = []
        
    async def cleanup(self) -> None:
        logger.info(f"Cleaning up WebProcessing plugin. Processed {self.request_count} requests")
        
    async def process_request(self, message: str, context: Dict) -> Dict:
        """Process a web request."""
        self.request_count += 1
        
        # Simulate different types of processing based on message content
        if "hello" in message.lower():
            response = f"Hello! I'm an AgentFlow web agent. Request #{self.request_count}"
        elif "status" in message.lower():
            response = f"Agent is running normally. Processed {self.request_count} requests so far."
        elif "time" in message.lower():
            response = f"Current time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elif "echo" in message.lower():
            response = f"Echo: {message.replace('echo', '').strip()}"
        else:
            response = f"I received your message: '{message}'. This is response #{self.request_count}"
            
        result = {
            "response": response,
            "request_count": self.request_count,
            "processed_at": datetime.now().isoformat(),
            "original_message": message,
            "context_received": context
        }
        
        self.responses.append(result)
        return result


# FastAPI app
app = FastAPI(
    title="AgentFlow Web API Example",
    description="A web-based AI agent built with AgentFlow",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
tasks_storage: Dict[str, TaskStatus] = {}
task_counter = 0


def generate_task_id() -> str:
    """Generate a unique task ID."""
    global task_counter
    task_counter += 1
    return f"task_{task_counter:06d}"


@app.on_event("startup")
async def startup_event():
    """Initialize the agent and plugins on startup."""
    logger.info("Starting up AgentFlow Web API...")
    
    # Register and initialize plugins
    from agentflow.plugins.registry import plugin_registry
    plugin_registry.register_plugin_class(WebProcessingPlugin)
    plugin_manager.registry.create_plugin_instance("web_processing")
    
    await plugin_manager.initialize_all_plugins()
    logger.info("AgentFlow Web API startup completed")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown."""
    logger.info("Shutting down AgentFlow Web API...")
    await plugin_manager.cleanup_all_plugins()
    logger.info("AgentFlow Web API shutdown completed")


@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "AgentFlow Web API Agent",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "process": "/agent/process (POST)",
            "status": "/agent/status",
            "tasks": "/tasks",
            "plugins": "/plugins"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check plugin health
        plugin_health = await plugin_manager.health_check()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "plugins": plugin_health,
            "active_plugins": len(plugin_manager.registry.get_enabled_plugins()),
            "total_tasks": len(tasks_storage),
            "pending_tasks": sum(1 for t in tasks_storage.values() if t.status == "pending"),
            "completed_tasks": sum(1 for t in tasks_storage.values() if t.status == "completed")
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post("/agent/process", response_model=AgentResponse)
async def process_request(request: AgentRequest, background_tasks: BackgroundTasks):
    """Process an agent request."""
    task_id = generate_task_id()
    
    # Create task status
    task_status = TaskStatus(
        task_id=task_id,
        status="pending",
        created_at=datetime.now()
    )
    tasks_storage[task_id] = task_status
    
    try:
        # Update status to processing
        task_status.status = "processing"
        
        # Get plugin and process request
        plugin = plugin_manager.registry.get_plugin("web_processing")
        if not plugin:
            raise HTTPException(status_code=500, detail="Web processing plugin not available")
        
        # Process the request
        result = await plugin.process_request(request.message, request.context)
        
        # Update task status
        task_status.status = "completed"
        task_status.completed_at = datetime.now()
        task_status.result = result
        
        return AgentResponse(
            response=result["response"],
            task_id=task_id,
            processed_at=datetime.fromisoformat(result["processed_at"]),
            context=result.get("context_received", {})
        )
        
    except Exception as e:
        task_status.status = "failed"
        task_status.completed_at = datetime.now()
        logger.error(f"Error processing request {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.get("/agent/status")
async def get_agent_status():
    """Get agent status and statistics."""
    plugin = plugin_manager.registry.get_plugin("web_processing")
    plugin_stats = {}
    
    if plugin:
        plugin_stats = {
            "request_count": getattr(plugin, "request_count", 0),
            "total_responses": len(getattr(plugin, "responses", []))
        }
    
    return {
        "agent": {
            "name": "web-api-agent",
            "status": "running",
            "uptime": "N/A",  # Could implement uptime tracking
            "version": "1.0.0"
        },
        "tasks": {
            "total": len(tasks_storage),
            "pending": sum(1 for t in tasks_storage.values() if t.status == "pending"),
            "processing": sum(1 for t in tasks_storage.values() if t.status == "processing"),
            "completed": sum(1 for t in tasks_storage.values() if t.status == "completed"),
            "failed": sum(1 for t in tasks_storage.values() if t.status == "failed")
        },
        "plugins": plugin_stats
    }


@app.get("/tasks", response_model=List[TaskStatus])
async def list_tasks(limit: int = 100):
    """List recent tasks."""
    # Return most recent tasks
    sorted_tasks = sorted(
        tasks_storage.values(),
        key=lambda t: t.created_at,
        reverse=True
    )
    return sorted_tasks[:limit]


@app.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task(task_id: str):
    """Get specific task status."""
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_storage[task_id]


@app.get("/plugins", response_model=List[PluginInfo])
async def list_plugins():
    """List all plugins and their status."""
    plugins = []
    
    for plugin_name in plugin_manager.registry.list_active_plugins():
        plugin = plugin_manager.registry.get_plugin(plugin_name)
        if plugin:
            # Check health
            try:
                health_status = await plugin_manager.health_check()
                is_healthy = health_status.get(plugin_name, False)
            except:
                is_healthy = False
                
            plugins.append(PluginInfo(
                name=plugin.metadata.name,
                version=plugin.metadata.version,
                description=plugin.metadata.description,
                status="enabled" if plugin.is_enabled else "disabled",
                health=is_healthy
            ))
    
    return plugins


@app.delete("/tasks")
async def clear_tasks():
    """Clear all task history."""
    cleared_count = len(tasks_storage)
    tasks_storage.clear()
    global task_counter
    task_counter = 0
    
    return {
        "message": f"Cleared {cleared_count} tasks",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    print("🌊 Starting AgentFlow Web API Agent")
    print("="*40)
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("⚡ Press Ctrl+C to stop")
    print()
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )