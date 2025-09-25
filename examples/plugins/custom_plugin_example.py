#!/usr/bin/env python3
"""
插件开发示例：自定义插件
========================

这个示例展示如何创建自定义插件，包括完整的生命周期管理。

运行方式：
python3 examples/plugins/custom_plugin_example.py
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentflow.plugins.base import BasePlugin, PluginMetadata, PluginContext
from agentflow.plugins.manager import plugin_manager


class DataProcessorPlugin(BasePlugin):
    """数据处理插件示例"""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="data_processor",
            version="1.2.0",
            description="强大的数据处理和分析插件",
            author="AgentFlow Examples",
            homepage="https://github.com/agentflow/examples",
            tags=["data", "processing", "analysis", "custom"],
            supports_async=True
        )
    
    def __init__(self, config=None):
        super().__init__(config)
        self.processed_count = 0
        self.error_count = 0
        self.data_cache = {}
        self.operations_log = []
    
    async def initialize(self) -> None:
        """插件初始化"""
        print(f"🔌 {self.metadata.name} v{self.metadata.version} 初始化中...")
        
        # 注册支持的钩子
        self.register_hook("process_data")
        self.register_hook("validate_data")
        self.register_hook("transform_data")
        
        # 设置默认配置
        self.max_cache_size = self.config.config.get("max_cache_size", 100)
        self.enable_logging = self.config.config.get("enable_logging", True)
        
        print(f"   ✓ 最大缓存：{self.max_cache_size}")
        print(f"   ✓ 日志记录：{self.enable_logging}")
        print(f"   ✓ 支持的钩子：{', '.join(self.get_hooks())}")
        print(f"🟢 {self.metadata.name} 初始化完成！")
    
    async def execute_task(self, context: PluginContext) -> Dict[str, Any]:
        """执行数据处理任务"""
        operation = context.data.get("operation", "unknown")
        data = context.data.get("data")
        
        if not data:
            return {"error": "没有提供数据", "success": False}
        
        try:
            # 记录操作开始
            start_time = datetime.now()
            
            # 根据操作类型处理数据
            result = await self._process_by_operation(operation, data, context)
            
            # 记录操作结果
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.processed_count += 1
            
            if self.enable_logging:
                self.operations_log.append({
                    "timestamp": start_time.isoformat(),
                    "operation": operation,
                    "duration": duration,
                    "success": True,
                    "data_size": len(str(data))
                })
            
            result.update({
                "success": True,
                "processed_count": self.processed_count,
                "duration": f"{duration:.3f}s"
            })
            
            return result
            
        except Exception as e:
            self.error_count += 1
            error_result = {
                "error": str(e),
                "success": False,
                "error_count": self.error_count,
                "operation": operation
            }
            
            if self.enable_logging:
                self.operations_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "operation": operation,
                    "error": str(e),
                    "success": False
                })
            
            return error_result
    
    async def _process_by_operation(self, operation: str, data: Any, context: PluginContext) -> Dict[str, Any]:
        """根据操作类型处理数据"""
        
        if operation == "count":
            # 计数操作
            if isinstance(data, (list, dict, str)):
                count = len(data)
                return {"operation": "count", "result": count, "data_type": type(data).__name__}
            else:
                return {"operation": "count", "result": 1, "data_type": type(data).__name__}
        
        elif operation == "sum":
            # 求和操作
            if isinstance(data, list) and all(isinstance(x, (int, float)) for x in data):
                total = sum(data)
                return {"operation": "sum", "result": total, "items_count": len(data)}
            else:
                raise ValueError("求和操作需要数字列表")
        
        elif operation == "filter":
            # 过滤操作
            filter_condition = context.data.get("condition", {})
            if isinstance(data, list) and isinstance(filter_condition, dict):
                filtered = self._filter_data(data, filter_condition)
                return {
                    "operation": "filter",
                    "result": filtered,
                    "original_count": len(data),
                    "filtered_count": len(filtered)
                }
            else:
                raise ValueError("过滤操作需要列表数据和条件字典")
        
        elif operation == "group":
            # 分组操作
            group_key = context.data.get("group_by")
            if isinstance(data, list) and group_key:
                grouped = self._group_data(data, group_key)
                return {
                    "operation": "group",
                    "result": grouped,
                    "groups_count": len(grouped),
                    "group_by": group_key
                }
            else:
                raise ValueError("分组操作需要列表数据和分组键")
        
        elif operation == "validate":
            # 验证操作
            schema = context.data.get("schema", {})
            validation_result = self._validate_data(data, schema)
            return {
                "operation": "validate",
                "result": validation_result,
                "is_valid": validation_result["is_valid"]
            }
        
        elif operation == "cache":
            # 缓存操作
            cache_key = context.data.get("key", f"cache_{len(self.data_cache)}")
            self._manage_cache(cache_key, data)
            return {
                "operation": "cache",
                "result": f"数据已缓存到键：{cache_key}",
                "cache_size": len(self.data_cache)
            }
        
        else:
            raise ValueError(f"不支持的操作：{operation}")
    
    def _filter_data(self, data: list, condition: dict) -> list:
        """过滤数据"""
        filtered = []
        for item in data:
            if isinstance(item, dict):
                match = True
                for key, value in condition.items():
                    if key not in item or item[key] != value:
                        match = False
                        break
                if match:
                    filtered.append(item)
            elif hasattr(item, '__dict__'):
                # 对象过滤
                match = True
                for key, value in condition.items():
                    if not hasattr(item, key) or getattr(item, key) != value:
                        match = False
                        break
                if match:
                    filtered.append(item)
        return filtered
    
    def _group_data(self, data: list, group_key: str) -> dict:
        """分组数据"""
        groups = {}
        for item in data:
            if isinstance(item, dict) and group_key in item:
                key = item[group_key]
            elif hasattr(item, group_key):
                key = getattr(item, group_key)
            else:
                key = "unknown"
            
            if key not in groups:
                groups[key] = []
            groups[key].append(item)
        
        return groups
    
    def _validate_data(self, data: Any, schema: dict) -> dict:
        """验证数据"""
        errors = []
        
        # 简单的类型验证
        expected_type = schema.get("type")
        if expected_type:
            if expected_type == "list" and not isinstance(data, list):
                errors.append(f"期望类型 list，实际类型 {type(data).__name__}")
            elif expected_type == "dict" and not isinstance(data, dict):
                errors.append(f"期望类型 dict，实际类型 {type(data).__name__}")
            elif expected_type == "str" and not isinstance(data, str):
                errors.append(f"期望类型 str，实际类型 {type(data).__name__}")
        
        # 必需字段验证
        required_fields = schema.get("required", [])
        if isinstance(data, dict):
            for field in required_fields:
                if field not in data:
                    errors.append(f"缺少必需字段：{field}")
        
        # 长度验证
        min_length = schema.get("min_length")
        max_length = schema.get("max_length")
        if hasattr(data, '__len__'):
            data_len = len(data)
            if min_length and data_len < min_length:
                errors.append(f"长度 {data_len} 小于最小长度 {min_length}")
            if max_length and data_len > max_length:
                errors.append(f"长度 {data_len} 大于最大长度 {max_length}")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "schema_applied": schema
        }
    
    def _manage_cache(self, key: str, data: Any):
        """管理缓存"""
        # 如果缓存满了，删除最旧的项
        if len(self.data_cache) >= self.max_cache_size:
            oldest_key = next(iter(self.data_cache))
            del self.data_cache[oldest_key]
        
        self.data_cache[key] = {
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "access_count": 0
        }
    
    def get_cache(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if key in self.data_cache:
            self.data_cache[key]["access_count"] += 1
            return self.data_cache[key]["data"]
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取插件统计信息"""
        return {
            "processed_count": self.processed_count,
            "error_count": self.error_count,
            "success_rate": (self.processed_count / (self.processed_count + self.error_count) * 100) 
                          if (self.processed_count + self.error_count) > 0 else 0,
            "cache_size": len(self.data_cache),
            "operations_logged": len(self.operations_log),
            "supported_operations": [
                "count", "sum", "filter", "group", "validate", "cache"
            ]
        }
    
    async def cleanup(self) -> None:
        """插件清理"""
        print(f"\n🧹 {self.metadata.name} 开始清理...")
        
        stats = self.get_statistics()
        print(f"   📊 处理统计：")
        print(f"      - 成功处理：{stats['processed_count']} 次")
        print(f"      - 错误次数：{stats['error_count']} 次")
        print(f"      - 成功率：{stats['success_rate']:.1f}%")
        print(f"      - 缓存大小：{stats['cache_size']}")
        
        # 清理资源
        self.data_cache.clear()
        self.operations_log.clear()
        
        print(f"🔴 {self.metadata.name} 清理完成")


async def demo_plugin_usage():
    """演示插件使用"""
    print("🌊 AgentFlow 自定义插件开发示例")
    print("=" * 60)
    
    # 创建插件实例
    from agentflow.plugins.base import PluginConfig
    config = PluginConfig(
        enabled=True,
        config={
            "max_cache_size": 50,
            "enable_logging": True
        }
    )
    plugin = DataProcessorPlugin(config)
    
    try:
        # 初始化插件
        await plugin.initialize()
        
        # 测试用例
        test_cases = [
            {
                "name": "计数操作",
                "context": PluginContext(
                    agent_id="data_processor",
                    task_id="task_count",
                    session_id="demo_session",
                    data={
                        "operation": "count",
                        "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                    }
                )
            },
            {
                "name": "求和操作",
                "context": PluginContext(
                    agent_id="data_processor",
                    task_id="task_sum",
                    session_id="demo_session",
                    data={
                        "operation": "sum",
                        "data": [10, 20, 30, 40, 50]
                    }
                )
            },
            {
                "name": "过滤操作",
                "context": PluginContext(
                    agent_id="data_processor",
                    task_id="task_sum",
                    session_id="demo_session",
                    data={
                        "operation": "filter",
                        "data": [
                            {"name": "Alice", "age": 25, "city": "北京"},
                            {"name": "Bob", "age": 30, "city": "上海"},
                            {"name": "Charlie", "age": 25, "city": "广州"},
                            {"name": "Diana", "age": 28, "city": "北京"}
                        ],
                        "condition": {"city": "北京"}
                    }
                )
            },
            {
                "name": "分组操作",
                "context": PluginContext(
                    agent_id="data_processor",
                    task_id="task_sum",
                    session_id="demo_session",
                    data={
                        "operation": "group",
                        "data": [
                            {"name": "产品A", "category": "电子", "price": 100},
                            {"name": "产品B", "category": "服装", "price": 50},
                            {"name": "产品C", "category": "电子", "price": 200},
                            {"name": "产品D", "category": "服装", "price": 80}
                        ],
                        "group_by": "category"
                    }
                )
            },
            {
                "name": "数据验证",
                "context": PluginContext(
                    agent_id="data_processor",
                    task_id="task_sum",
                    session_id="demo_session",
                    data={
                        "operation": "validate",
                        "data": {"name": "测试用户", "email": "test@example.com"},
                        "schema": {
                            "type": "dict",
                            "required": ["name", "email"],
                            "min_length": 1
                        }
                    }
                )
            },
            {
                "name": "缓存操作",
                "context": PluginContext(
                    agent_id="data_processor",
                    task_id="task_sum",
                    session_id="demo_session",
                    data={
                        "operation": "cache",
                        "key": "user_data",
                        "data": {"user_id": 123, "preferences": {"theme": "dark"}}
                    }
                )
            }
        ]
        
        print(f"\n🎯 开始执行 {len(test_cases)} 个测试用例：")
        print("-" * 40)
        
        # 执行所有测试用例
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. {test_case['name']}：")
            result = await plugin.execute_task(test_case["context"])
            
            if result.get("success"):
                print(f"   ✅ 成功：{result.get('result', '无结果')}")
                if "duration" in result:
                    print(f"   ⏱️  耗时：{result['duration']}")
            else:
                print(f"   ❌ 失败：{result.get('error', '未知错误')}")
        
        # 测试缓存获取
        print(f"\n🗄️ 测试缓存获取：")
        cached_data = plugin.get_cache("user_data")
        if cached_data:
            print(f"   ✅ 缓存命中：{cached_data}")
        else:
            print(f"   ❌ 缓存未命中")
        
        # 显示统计信息
        stats = plugin.get_statistics()
        print(f"\n📊 插件执行统计：")
        for key, value in stats.items():
            if key == "supported_operations":
                print(f"   {key}: {', '.join(value)}")
            else:
                print(f"   {key}: {value}")
        
    finally:
        # 清理插件
        await plugin.cleanup()


if __name__ == "__main__":
    asyncio.run(demo_plugin_usage())