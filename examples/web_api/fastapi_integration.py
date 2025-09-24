#!/usr/bin/env python3
"""
Web API示例：FastAPI集成
=======================

这个示例展示如何将AgentFlow与FastAPI集成，创建RESTful API服务。

安装依赖：
pip install fastapi uvicorn

运行方式：
python3 examples/web_api/fastapi_integration.py

然后访问：http://localhost:8000/docs 查看API文档
"""

import asyncio
import sys
import uvicorn
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.responses import JSONResponse
except ImportError:
    print("❌ 需要安装FastAPI和uvicorn:")
    print("   pip install fastapi uvicorn")
    sys.exit(1)

from agentflow.core.orchestrator import AgentOrchestrator
from agentflow.core.types import (
    AgentRole, TechStack, ProjectConfig, PlatformType, 
    ProjectComplexity, TaskPriority
)
from agentflow.agents.base import create_mock_agent
from agentflow.plugins.base import BasePlugin, PluginMetadata, PluginContext


# Pydantic模型定义
class TaskRequest(BaseModel):
    title: str
    description: str
    agent_role: str
    priority: str = "MEDIUM"
    estimated_hours: int = 1


class ProjectRequest(BaseModel):
    name: str
    description: str
    tech_stack: List[str]
    target_platform: str = "WEB"
    complexity: str = "MEDIUM"
    requirements: List[str] = []


class AgentStatus(BaseModel):
    agent_id: str
    role: str
    is_active: bool
    current_tasks: int
    completed_tasks: int
    success_rate: float


class ProjectStatus(BaseModel):
    session_id: str
    project_name: str
    status: str
    tasks_completed: int
    total_tasks: int


# 创建FastAPI应用
app = FastAPI(
    title="AgentFlow API",
    description="AgentFlow多智能体编排框架的RESTful API接口",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 全局协调器实例
orchestrator: Optional[AgentOrchestrator] = None
active_sessions: Dict[str, Dict[str, Any]] = {}


class WebAPIPlugin(BasePlugin):
    """Web API专用插件"""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="web_api_plugin",
            version="1.0.0",
            description="Web API集成插件，处理HTTP请求转换为任务",
            author="AgentFlow Examples",
            tags=["web", "api", "http", "integration"]
        )
    
    async def initialize(self) -> None:
        print("🌐 Web API Plugin 初始化完成")
        self.request_count = 0
    
    async def execute_task(self, context: PluginContext) -> Dict[str, Any]:
        """处理Web API任务"""
        self.request_count += 1
        
        request_type = context.data.get("request_type", "unknown")
        
        if request_type == "health_check":
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "request_count": self.request_count
            }
        
        elif request_type == "data_processing":
            data = context.data.get("data", {})
            processed_data = {
                "original": data,
                "processed_at": datetime.now().isoformat(),
                "processed_by": "web_api_plugin",
                "status": "processed"
            }
            return processed_data
        
        else:
            return {
                "error": f"Unsupported request type: {request_type}",
                "request_count": self.request_count
            }
    
    async def cleanup(self) -> None:
        print(f"🌐 Web API Plugin 清理完成，处理了 {self.request_count} 个请求")


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    global orchestrator
    
    print("🌊 启动 AgentFlow API 服务...")
    
    # 创建协调器
    orchestrator = AgentOrchestrator()
    
    # 创建智能体团队
    agent_roles = [
        AgentRole.PROJECT_MANAGER,
        AgentRole.BACKEND_DEVELOPER,
        AgentRole.FRONTEND_DEVELOPER,
        AgentRole.QA_ENGINEER
    ]
    
    for role in agent_roles:
        agent = create_mock_agent(role)
        orchestrator.register_agent(agent)
    
    # 注册Web API插件
    web_plugin = WebAPIPlugin()
    await web_plugin.initialize()
    
    print(f"✅ AgentFlow API 服务启动完成")
    print(f"   注册智能体：{len(agent_roles)} 个")
    print(f"   访问文档：http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print("🔄 关闭 AgentFlow API 服务...")


# API路由定义

@app.get("/", tags=["基础"])
async def root():
    """根路径，返回API基本信息"""
    return {
        "name": "AgentFlow API",
        "version": "1.0.0",
        "description": "多智能体编排框架的RESTful API",
        "docs_url": "/docs",
        "health_check": "/health"
    }


@app.get("/health", tags=["基础"])
async def health_check():
    """健康检查端点"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="协调器未初始化")
    
    status = orchestrator.get_orchestrator_status()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "orchestrator": {
            "registered_agents": status["registered_agents"],
            "active_sessions": status["active_sessions"],
            "total_sessions": status["total_sessions"]
        }
    }


@app.get("/agents", response_model=List[AgentStatus], tags=["智能体管理"])
async def list_agents():
    """获取所有智能体状态"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="协调器未初始化")
    
    agents_status = []
    for role, agent in orchestrator.agents.items():
        agent_status = agent.get_status()
        agents_status.append(AgentStatus(
            agent_id=agent_status["agent_id"],
            role=agent_status["role"],
            is_active=agent_status["is_active"],
            current_tasks=agent_status["current_tasks"],
            completed_tasks=agent_status["completed_tasks"],
            success_rate=agent_status["success_rate"]
        ))
    
    return agents_status


@app.get("/agents/{agent_role}", tags=["智能体管理"])
async def get_agent_status(agent_role: str):
    """获取特定智能体状态"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="协调器未初始化")
    
    try:
        role = AgentRole(agent_role)
        agent = orchestrator.agents.get(role)
        
        if not agent:
            raise HTTPException(status_code=404, detail=f"智能体 {agent_role} 未找到")
        
        return agent.get_status()
    
    except ValueError:
        raise HTTPException(status_code=400, detail=f"无效的智能体角色: {agent_role}")


@app.post("/projects", tags=["项目管理"])
async def create_project(project: ProjectRequest, background_tasks: BackgroundTasks):
    """创建和执行新项目"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="协调器未初始化")
    
    try:
        # 转换技术栈
        tech_stack = []
        for tech_name in project.tech_stack:
            try:
                tech = TechStack(tech_name.lower())
                tech_stack.append(tech)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"不支持的技术栈: {tech_name}")
        
        # 创建项目配置
        project_config = ProjectConfig(
            name=project.name,
            description=project.description,
            tech_stack=tech_stack,
            target_platform=PlatformType(project.target_platform.lower()),
            complexity=ProjectComplexity(project.complexity.lower()),
            requirements=project.requirements
        )
        
        # 在后台执行项目
        async def execute_project_background():
            try:
                result = await orchestrator.execute_project(project_config)
                active_sessions[result.get("session_id", "unknown")] = {
                    "project_name": project.name,
                    "status": "completed" if result["success"] else "failed",
                    "result": result,
                    "created_at": datetime.now().isoformat()
                }
            except Exception as e:
                print(f"后台项目执行错误: {e}")
        
        background_tasks.add_task(execute_project_background)
        
        return {
            "message": "项目创建成功，正在后台执行",
            "project_name": project.name,
            "status": "executing"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/projects", tags=["项目管理"])
async def list_projects():
    """列出所有项目会话"""
    return {
        "active_sessions": len(active_sessions),
        "sessions": [
            {
                "session_id": session_id,
                "project_name": session_data["project_name"],
                "status": session_data["status"],
                "created_at": session_data["created_at"]
            }
            for session_id, session_data in active_sessions.items()
        ]
    }


@app.get("/projects/{session_id}", tags=["项目管理"])
async def get_project_status(session_id: str):
    """获取项目状态"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="协调器未初始化")
    
    # 检查本地会话
    if session_id in active_sessions:
        return active_sessions[session_id]
    
    # 检查协调器中的会话
    session_status = orchestrator.get_session_status(session_id)
    if "error" in session_status:
        raise HTTPException(status_code=404, detail="项目会话未找到")
    
    return session_status


@app.get("/stats", tags=["统计信息"])
async def get_statistics():
    """获取系统统计信息"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="协调器未初始化")
    
    orchestrator_stats = orchestrator.get_orchestrator_status()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "orchestrator": orchestrator_stats,
        "api": {
            "active_sessions": len(active_sessions),
            "total_projects": len(active_sessions)
        }
    }


@app.post("/agents/{agent_role}/task", tags=["任务管理"])
async def create_agent_task(agent_role: str, task_data: dict):
    """为特定智能体创建任务"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="协调器未初始化")
    
    try:
        role = AgentRole(agent_role)
        agent = orchestrator.agents.get(role)
        
        if not agent:
            raise HTTPException(status_code=404, detail=f"智能体 {agent_role} 未找到")
        
        # 创建插件上下文
        context = PluginContext(
            plugin_name="api_task",
            data=task_data
        )
        
        # 执行任务
        result = await agent.execute_task(context)
        
        return {
            "agent_role": agent_role,
            "task_result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    except ValueError:
        raise HTTPException(status_code=400, detail=f"无效的智能体角色: {agent_role}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 自定义异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url.path)
        }
    )


if __name__ == "__main__":
    print("🌊 启动 AgentFlow FastAPI 服务器")
    print("=" * 50)
    print("📖 访问 http://localhost:8000/docs 查看API文档")
    print("🔍 访问 http://localhost:8000/health 进行健康检查")
    print("⚡ 按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    # 启动服务器
    uvicorn.run(
        "fastapi_integration:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        access_log=True
    )