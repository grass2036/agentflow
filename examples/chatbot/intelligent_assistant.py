#!/usr/bin/env python3
"""
聊天机器人示例：智能助手
========================

这个示例展示如何使用AgentFlow创建智能对话助手。

运行方式：
python3 examples/chatbot/intelligent_assistant.py
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentflow.plugins.base import BasePlugin, PluginMetadata, PluginContext
from agentflow.core.orchestrator import EventBus
from agentflow.core.types import AgentEvent, EventType, AgentRole


class ConversationMemory:
    """对话记忆管理"""
    
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.conversation_history: List[Dict[str, Any]] = []
        self.user_context = {}
        self.session_start = datetime.now()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """添加对话消息"""
        message = {
            "role": role,  # user, assistant, system
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.conversation_history.append(message)
        
        # 保持历史记录在限制范围内
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def get_recent_messages(self, count: int = 5) -> List[Dict[str, Any]]:
        """获取最近的消息"""
        return self.conversation_history[-count:] if count > 0 else self.conversation_history
    
    def set_user_context(self, key: str, value: Any):
        """设置用户上下文信息"""
        self.user_context[key] = value
    
    def get_user_context(self, key: str, default=None):
        """获取用户上下文信息"""
        return self.user_context.get(key, default)
    
    def clear_context(self):
        """清空上下文"""
        self.user_context.clear()
    
    def get_session_stats(self) -> Dict[str, Any]:
        """获取会话统计"""
        duration = (datetime.now() - self.session_start).total_seconds()
        user_messages = len([m for m in self.conversation_history if m["role"] == "user"])
        assistant_messages = len([m for m in self.conversation_history if m["role"] == "assistant"])
        
        return {
            "session_duration": f"{duration:.1f}秒",
            "total_messages": len(self.conversation_history),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "context_items": len(self.user_context)
        }


class IntelligentAssistantPlugin(BasePlugin):
    """智能助手插件"""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="intelligent_assistant",
            version="2.0.0",
            description="多功能智能对话助手，支持任务管理、信息查询和智能分析",
            author="AgentFlow Examples",
            tags=["chatbot", "assistant", "conversation", "ai"],
            supports_async=True
        )
    
    def __init__(self, config=None):
        super().__init__(config)
        self.memory = ConversationMemory()
        self.capabilities = [
            "对话聊天", "任务管理", "信息查询", "数据分析",
            "时间管理", "计算工具", "文本处理", "系统帮助"
        ]
        self.commands = {
            "/help": "显示帮助信息",
            "/stats": "显示会话统计",
            "/clear": "清空对话历史",
            "/context": "显示用户上下文",
            "/task": "任务管理功能",
            "/calc": "计算器功能",
            "/time": "时间相关功能",
            "/quit": "退出对话"
        }
    
    async def initialize(self) -> None:
        """初始化助手"""
        print("🤖 智能助手正在启动...")
        print(f"   版本：{self.metadata.version}")
        print(f"   功能：{', '.join(self.capabilities)}")
        print("✅ 智能助手准备就绪！")
        
        # 添加欢迎消息
        self.memory.add_message(
            "system",
            "智能助手已启动，输入 /help 查看可用命令",
            {"type": "system_startup"}
        )
    
    async def execute_task(self, context: PluginContext) -> Dict[str, Any]:
        """处理用户输入"""
        user_input = context.data.get("user_input", "").strip()
        
        if not user_input:
            return {"response": "请输入一些内容~", "type": "error"}
        
        # 记录用户消息
        self.memory.add_message("user", user_input)
        
        try:
            # 处理输入
            if user_input.startswith("/"):
                response = await self._handle_command(user_input)
            else:
                response = await self._handle_conversation(user_input)
            
            # 记录助手响应
            self.memory.add_message(
                "assistant", 
                response["response"],
                {"type": response["type"]}
            )
            
            return response
            
        except Exception as e:
            error_response = {
                "response": f"抱歉，处理您的请求时出现了问题：{str(e)}",
                "type": "error"
            }
            self.memory.add_message("assistant", error_response["response"])
            return error_response
    
    async def _handle_command(self, command: str) -> Dict[str, Any]:
        """处理命令"""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd == "/help":
            help_text = "🤖 智能助手帮助\n\n可用命令：\n"
            for cmd_name, cmd_desc in self.commands.items():
                help_text += f"   {cmd_name} - {cmd_desc}\n"
            help_text += f"\n功能模块：{', '.join(self.capabilities)}"
            
            return {"response": help_text, "type": "help"}
        
        elif cmd == "/stats":
            stats = self.memory.get_session_stats()
            stats_text = "📊 会话统计：\n"
            for key, value in stats.items():
                stats_text += f"   {key}: {value}\n"
            
            return {"response": stats_text, "type": "stats"}
        
        elif cmd == "/clear":
            self.memory.conversation_history.clear()
            return {"response": "✅ 对话历史已清空", "type": "system"}
        
        elif cmd == "/context":
            if self.memory.user_context:
                context_text = "📝 用户上下文：\n"
                for key, value in self.memory.user_context.items():
                    context_text += f"   {key}: {value}\n"
            else:
                context_text = "暂无用户上下文信息"
            
            return {"response": context_text, "type": "context"}
        
        elif cmd == "/task":
            return await self._handle_task_command(args)
        
        elif cmd == "/calc":
            return await self._handle_calculator(args)
        
        elif cmd == "/time":
            return await self._handle_time_command(args)
        
        elif cmd == "/quit":
            return {"response": "👋 再见！感谢使用智能助手", "type": "quit"}
        
        else:
            return {"response": f"未知命令：{cmd}，输入 /help 查看可用命令", "type": "error"}
    
    async def _handle_conversation(self, user_input: str) -> Dict[str, Any]:
        """处理常规对话"""
        user_input_lower = user_input.lower()
        
        # 问候检测
        if any(greeting in user_input_lower for greeting in ["你好", "hello", "hi", "嗨"]):
            responses = [
                "你好！我是AgentFlow智能助手，很高兴为您服务！😊",
                "嗨！有什么我可以帮助您的吗？",
                "您好！今天过得怎么样？"
            ]
            import random
            return {"response": random.choice(responses), "type": "greeting"}
        
        # 功能查询
        elif any(word in user_input_lower for word in ["功能", "能做", "会什么", "帮助"]):
            return {
                "response": f"我具备以下功能：\n• {chr(10).join(['• ' + cap for cap in self.capabilities])}\n\n输入 /help 查看详细命令",
                "type": "info"
            }
        
        # 时间查询
        elif any(word in user_input_lower for word in ["时间", "几点", "日期"]):
            now = datetime.now()
            time_info = f"🕐 当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            time_info += f"📅 星期：{['一', '二', '三', '四', '五', '六', '日'][now.weekday()]}"
            return {"response": time_info, "type": "time"}
        
        # 计算请求
        elif any(word in user_input_lower for word in ["计算", "算", "等于"]):
            return await self._handle_calculator(user_input)
        
        # 名字询问
        elif any(word in user_input_lower for word in ["你叫什么", "名字", "你是谁"]):
            name = self.memory.get_user_context("user_name")
            if name:
                return {"response": f"我是AgentFlow智能助手！很高兴认识您，{name}！", "type": "introduction"}
            else:
                return {"response": "我是AgentFlow智能助手！请问您的名字是？", "type": "introduction"}
        
        # 名字记录
        elif "我是" in user_input or "我叫" in user_input:
            import re
            name_match = re.search(r'(?:我是|我叫|叫我)([^，。！？\s]+)', user_input)
            if name_match:
                name = name_match.group(1).strip()
                self.memory.set_user_context("user_name", name)
                return {"response": f"很高兴认识您，{name}！我会记住您的名字。", "type": "personal"}
        
        # 情感表达
        elif any(word in user_input_lower for word in ["谢谢", "感谢", "不错", "很好"]):
            return {"response": "不客气！能帮到您我很开心！😊", "type": "emotional"}
        
        elif any(word in user_input_lower for word in ["难过", "烦恼", "困难"]):
            return {"response": "我理解您的感受。有什么我可以帮您解决的吗？", "type": "emotional"}
        
        # 默认智能回复
        else:
            return await self._generate_intelligent_response(user_input)
    
    async def _generate_intelligent_response(self, user_input: str) -> Dict[str, Any]:
        """生成智能回复"""
        # 分析用户输入的关键词
        keywords = user_input.split()
        
        # 基于关键词生成回复
        if any(word in user_input for word in ["项目", "工作", "任务"]):
            return {
                "response": "您在谈论工作或项目。我可以帮您管理任务，使用 /task 命令来开始吧！",
                "type": "suggestion"
            }
        
        elif any(word in user_input for word in ["数据", "分析", "统计"]):
            return {
                "response": "我具备数据分析能力！您可以提供数据，我来帮您分析。",
                "type": "capability"
            }
        
        elif any(word in user_input for word in ["学习", "教", "知识"]):
            return {
                "response": "学习很重要！我可以帮您整理知识点或制定学习计划。",
                "type": "educational"
            }
        
        else:
            # 通用智能回复
            responses = [
                "这是一个有趣的话题！请告诉我更多详情。",
                "我理解了。您希望我如何帮助您？",
                "听起来很有意思！我们可以深入探讨一下。",
                "我正在思考您的问题...您能提供更多信息吗？"
            ]
            import random
            return {"response": random.choice(responses), "type": "conversation"}
    
    async def _handle_task_command(self, args: str) -> Dict[str, Any]:
        """处理任务管理命令"""
        if not args:
            return {
                "response": "📋 任务管理功能：\n   /task add <任务> - 添加任务\n   /task list - 查看任务\n   /task done <编号> - 完成任务",
                "type": "task_help"
            }
        
        parts = args.split(maxsplit=1)
        action = parts[0].lower()
        content = parts[1] if len(parts) > 1 else ""
        
        # 获取或初始化任务列表
        tasks = self.memory.get_user_context("tasks", [])
        
        if action == "add" and content:
            task = {
                "id": len(tasks) + 1,
                "content": content,
                "created": datetime.now().isoformat(),
                "completed": False
            }
            tasks.append(task)
            self.memory.set_user_context("tasks", tasks)
            return {"response": f"✅ 已添加任务：{content}", "type": "task_add"}
        
        elif action == "list":
            if not tasks:
                return {"response": "📋 暂无任务", "type": "task_list"}
            
            task_list = "📋 任务列表：\n"
            for task in tasks:
                status = "✅" if task["completed"] else "⏳"
                task_list += f"   {task['id']}. {status} {task['content']}\n"
            
            return {"response": task_list, "type": "task_list"}
        
        elif action == "done" and content.isdigit():
            task_id = int(content)
            for task in tasks:
                if task["id"] == task_id:
                    task["completed"] = True
                    task["completed_at"] = datetime.now().isoformat()
                    self.memory.set_user_context("tasks", tasks)
                    return {"response": f"🎉 任务 {task_id} 已完成！", "type": "task_done"}
            
            return {"response": f"❌ 未找到任务 {task_id}", "type": "task_error"}
        
        else:
            return {"response": "❌ 无效的任务命令，输入 /task 查看帮助", "type": "task_error"}
    
    async def _handle_calculator(self, expression: str) -> Dict[str, Any]:
        """处理计算功能"""
        if not expression:
            return {"response": "🧮 请输入要计算的表达式，如：/calc 2+3*4", "type": "calc_help"}
        
        try:
            # 清理表达式
            expression = expression.replace("计算", "").replace("等于", "").strip()
            
            # 安全计算（仅支持基本运算）
            allowed_chars = "0123456789+-*/().,\s"
            if all(c in allowed_chars for c in expression):
                result = eval(expression)
                return {"response": f"🧮 计算结果：{expression} = {result}", "type": "calculation"}
            else:
                return {"response": "❌ 表达式包含不安全字符", "type": "calc_error"}
        
        except Exception as e:
            return {"response": f"❌ 计算错误：{str(e)}", "type": "calc_error"}
    
    async def _handle_time_command(self, args: str) -> Dict[str, Any]:
        """处理时间相关命令"""
        now = datetime.now()
        
        if not args or args == "now":
            time_info = f"🕐 当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            time_info += f"📅 星期{['一', '二', '三', '四', '五', '六', '日'][now.weekday()]}"
            return {"response": time_info, "type": "time"}
        
        elif args == "timestamp":
            return {"response": f"⏰ 时间戳：{int(now.timestamp())}", "type": "time"}
        
        else:
            return {"response": "⏰ 时间功能：\n   /time - 当前时间\n   /time timestamp - 时间戳", "type": "time_help"}
    
    async def cleanup(self) -> None:
        """清理助手"""
        stats = self.memory.get_session_stats()
        print(f"\n🤖 智能助手会话结束")
        print(f"   会话时长：{stats['session_duration']}")
        print(f"   消息总数：{stats['total_messages']}")
        print(f"👋 感谢使用AgentFlow智能助手！")


async def run_interactive_chat():
    """运行交互式对话"""
    print("🌊 AgentFlow 智能助手")
    print("=" * 50)
    
    # 创建助手
    assistant = IntelligentAssistantPlugin()
    await assistant.initialize()
    
    print("\n💬 开始对话（输入 /quit 退出，/help 查看帮助）")
    print("-" * 30)
    
    try:
        while True:
            # 获取用户输入
            try:
                user_input = input("\n您：").strip()
            except (EOFError, KeyboardInterrupt):
                break
            
            if not user_input:
                continue
            
            # 创建上下文
            context = PluginContext(
                plugin_name="intelligent_assistant",
                data={"user_input": user_input}
            )
            
            # 处理输入
            response = await assistant.execute_task(context)
            
            # 显示回复
            print(f"🤖 助手：{response['response']}")
            
            # 检查是否退出
            if response.get("type") == "quit":
                break
    
    except Exception as e:
        print(f"\n❌ 发生错误：{e}")
    
    finally:
        await assistant.cleanup()


if __name__ == "__main__":
    asyncio.run(run_interactive_chat())