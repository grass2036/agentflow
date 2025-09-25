#!/usr/bin/env python3
"""
数据处理示例：数据分析器
=======================

这个示例展示如何使用AgentFlow进行数据分析和处理。

运行方式：
python3 examples/data_processing/data_analyzer.py
"""

import asyncio
import json
import csv
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import random
import statistics

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentflow.plugins.base import BasePlugin, PluginMetadata, PluginContext


class DataAnalyzerPlugin(BasePlugin):
    """数据分析插件"""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="data_analyzer",
            version="1.5.0",
            description="强大的数据分析和统计处理插件",
            author="AgentFlow Examples",
            tags=["data", "analysis", "statistics", "processing"],
            supports_async=True
        )
    
    def __init__(self, config=None):
        super().__init__(config)
        self.analysis_history = []
        self.processed_datasets = 0
        
    async def initialize(self) -> None:
        print("📊 数据分析器初始化中...")
        print("   支持的分析类型：统计分析、趋势分析、分组分析、异常检测")
        print("✅ 数据分析器准备就绪！")
    
    async def execute_task(self, context: PluginContext) -> Dict[str, Any]:
        """执行数据分析任务"""
        analysis_type = context.data.get("analysis_type", "basic_stats")
        data = context.data.get("data", [])
        
        if not data:
            return {"error": "没有提供数据", "success": False}
        
        start_time = datetime.now()
        
        try:
            if analysis_type == "basic_stats":
                result = await self._basic_statistics(data)
            elif analysis_type == "trend_analysis":
                result = await self._trend_analysis(data)
            elif analysis_type == "group_analysis":
                result = await self._group_analysis(data, context.data.get("group_by"))
            elif analysis_type == "anomaly_detection":
                result = await self._anomaly_detection(data)
            elif analysis_type == "correlation":
                result = await self._correlation_analysis(data)
            elif analysis_type == "time_series":
                result = await self._time_series_analysis(data)
            else:
                return {"error": f"不支持的分析类型：{analysis_type}", "success": False}
            
            # 记录分析历史
            duration = (datetime.now() - start_time).total_seconds()
            self.analysis_history.append({
                "type": analysis_type,
                "timestamp": start_time.isoformat(),
                "duration": duration,
                "data_size": len(data),
                "success": True
            })
            
            self.processed_datasets += 1
            
            result.update({
                "success": True,
                "analysis_type": analysis_type,
                "data_size": len(data),
                "processing_time": f"{duration:.3f}s",
                "processed_datasets": self.processed_datasets
            })
            
            return result
            
        except Exception as e:
            error_result = {
                "error": str(e),
                "success": False,
                "analysis_type": analysis_type
            }
            
            self.analysis_history.append({
                "type": analysis_type,
                "timestamp": start_time.isoformat(),
                "error": str(e),
                "success": False
            })
            
            return error_result
    
    async def _basic_statistics(self, data: List) -> Dict[str, Any]:
        """基础统计分析"""
        # 提取数值数据
        numeric_data = []
        for item in data:
            if isinstance(item, (int, float)):
                numeric_data.append(item)
            elif isinstance(item, dict):
                for value in item.values():
                    if isinstance(value, (int, float)):
                        numeric_data.append(value)
        
        if not numeric_data:
            return {"error": "没有找到数值数据"}
        
        stats = {
            "count": len(numeric_data),
            "mean": statistics.mean(numeric_data),
            "median": statistics.median(numeric_data),
            "min": min(numeric_data),
            "max": max(numeric_data),
            "range": max(numeric_data) - min(numeric_data),
            "sum": sum(numeric_data)
        }
        
        # 计算标准差（如果数据量足够）
        if len(numeric_data) > 1:
            stats["std_dev"] = statistics.stdev(numeric_data)
            stats["variance"] = statistics.variance(numeric_data)
        
        # 分位数
        stats["quartiles"] = {
            "q1": statistics.quantiles(numeric_data, n=4)[0] if len(numeric_data) >= 4 else None,
            "q2": statistics.median(numeric_data),
            "q3": statistics.quantiles(numeric_data, n=4)[2] if len(numeric_data) >= 4 else None
        }
        
        return {"statistics": stats}
    
    async def _trend_analysis(self, data: List) -> Dict[str, Any]:
        """趋势分析"""
        if len(data) < 3:
            return {"error": "趋势分析需要至少3个数据点"}
        
        # 提取数值序列
        values = []
        timestamps = []
        
        for i, item in enumerate(data):
            if isinstance(item, (int, float)):
                values.append(item)
                timestamps.append(i)
            elif isinstance(item, dict) and "value" in item:
                values.append(item["value"])
                timestamps.append(item.get("timestamp", i))
            elif isinstance(item, dict) and "y" in item:
                values.append(item["y"])
                timestamps.append(item.get("x", i))
        
        if len(values) < 3:
            return {"error": "没有足够的数值数据进行趋势分析"}
        
        # 计算趋势
        n = len(values)
        sum_x = sum(range(n))
        sum_y = sum(values)
        sum_xy = sum(i * values[i] for i in range(n))
        sum_x2 = sum(i * i for i in range(n))
        
        # 线性回归斜率
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # 趋势方向
        if slope > 0.01:
            trend = "上升"
        elif slope < -0.01:
            trend = "下降"
        else:
            trend = "平稳"
        
        # 计算变化率
        changes = [values[i+1] - values[i] for i in range(len(values)-1)]
        avg_change = sum(changes) / len(changes) if changes else 0
        
        return {
            "trend": {
                "direction": trend,
                "slope": slope,
                "intercept": intercept,
                "average_change": avg_change,
                "total_change": values[-1] - values[0],
                "change_percentage": ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
            }
        }
    
    async def _group_analysis(self, data: List, group_by: str = None) -> Dict[str, Any]:
        """分组分析"""
        if not group_by:
            return {"error": "需要指定分组字段"}
        
        if not all(isinstance(item, dict) for item in data):
            return {"error": "分组分析需要字典类型的数据"}
        
        groups = {}
        
        # 按指定字段分组
        for item in data:
            if group_by not in item:
                continue
            
            group_key = item[group_by]
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(item)
        
        if not groups:
            return {"error": f"没有找到分组字段：{group_by}"}
        
        # 分析每个组
        group_analysis = {}
        for group_key, group_items in groups.items():
            group_stats = {
                "count": len(group_items),
                "items": group_items[:5]  # 只显示前5项作为示例
            }
            
            # 如果组内有数值字段，计算统计信息
            numeric_fields = {}
            for item in group_items:
                for field, value in item.items():
                    if field != group_by and isinstance(value, (int, float)):
                        if field not in numeric_fields:
                            numeric_fields[field] = []
                        numeric_fields[field].append(value)
            
            # 为每个数值字段计算统计
            for field, values in numeric_fields.items():
                if values:
                    group_stats[f"{field}_stats"] = {
                        "count": len(values),
                        "mean": statistics.mean(values),
                        "sum": sum(values),
                        "min": min(values),
                        "max": max(values)
                    }
            
            group_analysis[str(group_key)] = group_stats
        
        return {
            "group_analysis": group_analysis,
            "total_groups": len(groups),
            "group_by": group_by
        }
    
    async def _anomaly_detection(self, data: List) -> Dict[str, Any]:
        """异常检测"""
        # 提取数值数据
        numeric_data = []
        indices = []
        
        for i, item in enumerate(data):
            if isinstance(item, (int, float)):
                numeric_data.append(item)
                indices.append(i)
            elif isinstance(item, dict) and "value" in item:
                numeric_data.append(item["value"])
                indices.append(i)
        
        if len(numeric_data) < 5:
            return {"error": "异常检测需要至少5个数据点"}
        
        # 使用IQR方法检测异常
        mean_val = statistics.mean(numeric_data)
        std_val = statistics.stdev(numeric_data)
        
        # Z-score方法（阈值为2.5）
        z_score_outliers = []
        for i, value in enumerate(numeric_data):
            z_score = abs(value - mean_val) / std_val if std_val > 0 else 0
            if z_score > 2.5:
                z_score_outliers.append({
                    "index": indices[i],
                    "value": value,
                    "z_score": z_score
                })
        
        # IQR方法
        if len(numeric_data) >= 4:
            q1 = statistics.quantiles(numeric_data, n=4)[0]
            q3 = statistics.quantiles(numeric_data, n=4)[2]
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            iqr_outliers = []
            for i, value in enumerate(numeric_data):
                if value < lower_bound or value > upper_bound:
                    iqr_outliers.append({
                        "index": indices[i],
                        "value": value,
                        "reason": "below_lower_bound" if value < lower_bound else "above_upper_bound"
                    })
        else:
            iqr_outliers = []
        
        return {
            "anomaly_detection": {
                "z_score_outliers": z_score_outliers,
                "iqr_outliers": iqr_outliers,
                "total_anomalies": len(set(o["index"] for o in z_score_outliers + iqr_outliers)),
                "data_points": len(numeric_data),
                "anomaly_rate": len(set(o["index"] for o in z_score_outliers + iqr_outliers)) / len(numeric_data) * 100
            }
        }
    
    async def _correlation_analysis(self, data: List) -> Dict[str, Any]:
        """相关性分析"""
        if not all(isinstance(item, dict) for item in data):
            return {"error": "相关性分析需要字典类型的数据"}
        
        # 找出所有数值字段
        numeric_fields = {}
        for item in data:
            for field, value in item.items():
                if isinstance(value, (int, float)):
                    if field not in numeric_fields:
                        numeric_fields[field] = []
                    numeric_fields[field].append(value)
        
        if len(numeric_fields) < 2:
            return {"error": "相关性分析需要至少2个数值字段"}
        
        # 计算相关系数
        correlations = {}
        field_names = list(numeric_fields.keys())
        
        for i in range(len(field_names)):
            for j in range(i + 1, len(field_names)):
                field1, field2 = field_names[i], field_names[j]
                values1, values2 = numeric_fields[field1], numeric_fields[field2]
                
                # 确保两个字段有相同数量的数据点
                min_len = min(len(values1), len(values2))
                if min_len > 1:
                    try:
                        correlation = statistics.correlation(values1[:min_len], values2[:min_len])
                        correlations[f"{field1}_vs_{field2}"] = {
                            "correlation": correlation,
                            "strength": self._interpret_correlation(correlation),
                            "data_points": min_len
                        }
                    except statistics.StatisticsError:
                        correlations[f"{field1}_vs_{field2}"] = {
                            "correlation": 0,
                            "strength": "无法计算",
                            "data_points": min_len
                        }
        
        return {"correlation_analysis": correlations}
    
    def _interpret_correlation(self, correlation: float) -> str:
        """解释相关系数强度"""
        abs_corr = abs(correlation)
        if abs_corr >= 0.8:
            return "强相关"
        elif abs_corr >= 0.6:
            return "中等相关"
        elif abs_corr >= 0.3:
            return "弱相关"
        else:
            return "很弱或无相关"
    
    async def _time_series_analysis(self, data: List) -> Dict[str, Any]:
        """时间序列分析"""
        # 期望数据格式：[{"timestamp": "...", "value": ...}, ...]
        time_series = []
        
        for item in data:
            if isinstance(item, dict) and "timestamp" in item and "value" in item:
                try:
                    timestamp = datetime.fromisoformat(item["timestamp"].replace('Z', '+00:00'))
                    time_series.append({"timestamp": timestamp, "value": item["value"]})
                except:
                    pass
            elif isinstance(item, dict) and "date" in item and "value" in item:
                try:
                    timestamp = datetime.fromisoformat(str(item["date"]))
                    time_series.append({"timestamp": timestamp, "value": item["value"]})
                except:
                    pass
        
        if len(time_series) < 3:
            return {"error": "时间序列分析需要至少3个带时间戳的数据点"}
        
        # 按时间排序
        time_series.sort(key=lambda x: x["timestamp"])
        
        # 计算时间间隔
        intervals = []
        for i in range(1, len(time_series)):
            interval = (time_series[i]["timestamp"] - time_series[i-1]["timestamp"]).total_seconds()
            intervals.append(interval)
        
        # 值的变化
        values = [item["value"] for item in time_series]
        value_changes = [values[i+1] - values[i] for i in range(len(values)-1)]
        
        # 季节性检测（简单方法）
        seasonality_detected = False
        if len(values) >= 12:  # 需要足够的数据点
            # 检查是否有周期性模式
            seasonality_detected = self._detect_seasonality(values)
        
        return {
            "time_series_analysis": {
                "data_points": len(time_series),
                "time_span": str(time_series[-1]["timestamp"] - time_series[0]["timestamp"]),
                "average_interval": f"{statistics.mean(intervals):.1f} 秒" if intervals else "N/A",
                "value_trend": "上升" if sum(value_changes) > 0 else "下降" if sum(value_changes) < 0 else "平稳",
                "volatility": statistics.stdev(value_changes) if len(value_changes) > 1 else 0,
                "seasonality_detected": seasonality_detected,
                "peak_value": max(values),
                "trough_value": min(values),
                "peak_timestamp": time_series[values.index(max(values))]["timestamp"].isoformat(),
                "trough_timestamp": time_series[values.index(min(values))]["timestamp"].isoformat()
            }
        }
    
    def _detect_seasonality(self, values: List[float]) -> bool:
        """简单的季节性检测"""
        # 这里使用简化的方法，实际应用中可能需要更复杂的算法
        if len(values) < 12:
            return False
        
        # 检查每季度的平均值是否有显著差异
        quarter_size = len(values) // 4
        quarters = [
            values[i*quarter_size:(i+1)*quarter_size] 
            for i in range(4)
        ]
        
        quarter_means = [statistics.mean(q) for q in quarters if q]
        
        if len(quarter_means) >= 2:
            # 如果季度间平均值的标准差相对较大，可能存在季节性
            mean_of_means = statistics.mean(quarter_means)
            if mean_of_means != 0:
                coefficient_of_variation = statistics.stdev(quarter_means) / mean_of_means
                return coefficient_of_variation > 0.1  # 阈值可调整
        
        return False
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """获取分析总结"""
        successful_analyses = [h for h in self.analysis_history if h["success"]]
        failed_analyses = [h for h in self.analysis_history if not h["success"]]
        
        return {
            "processed_datasets": self.processed_datasets,
            "total_analyses": len(self.analysis_history),
            "successful_analyses": len(successful_analyses),
            "failed_analyses": len(failed_analyses),
            "success_rate": (len(successful_analyses) / len(self.analysis_history) * 100) 
                          if self.analysis_history else 0,
            "average_processing_time": statistics.mean([h["duration"] for h in successful_analyses]) 
                                     if successful_analyses else 0,
            "analysis_types_used": list(set(h["type"] for h in self.analysis_history))
        }
    
    async def cleanup(self) -> None:
        """清理分析器"""
        summary = self.get_analysis_summary()
        print(f"\n📊 数据分析器会话结束")
        print(f"   处理数据集：{summary['processed_datasets']} 个")
        print(f"   分析成功率：{summary['success_rate']:.1f}%")
        print(f"   平均处理时间：{summary['average_processing_time']:.3f}秒")


async def run_analysis_demo():
    """运行数据分析演示"""
    print("🌊 AgentFlow 数据分析器演示")
    print("=" * 60)
    
    # 创建分析器
    analyzer = DataAnalyzerPlugin()
    await analyzer.initialize()
    
    # 生成示例数据
    def generate_sample_data():
        """生成多种类型的示例数据"""
        
        # 1. 销售数据
        sales_data = []
        base_date = datetime(2024, 1, 1)
        for i in range(30):
            sales_data.append({
                "date": (base_date + timedelta(days=i)).isoformat(),
                "sales": random.randint(1000, 5000) + random.randint(-200, 200),
                "region": random.choice(["北京", "上海", "广州", "深圳"]),
                "product": random.choice(["产品A", "产品B", "产品C"])
            })
        
        # 2. 时间序列数据
        time_series_data = []
        for i in range(24):
            time_series_data.append({
                "timestamp": (datetime.now() - timedelta(hours=24-i)).isoformat(),
                "value": 100 + 10 * math.sin(i * 0.5) + random.random() * 5
            })
        
        # 3. 用户数据
        user_data = []
        for i in range(100):
            user_data.append({
                "age": random.randint(18, 65),
                "income": random.randint(30000, 200000),
                "city": random.choice(["北京", "上海", "广州", "深圳", "杭州"]),
                "satisfaction": random.randint(1, 10)
            })
        
        return sales_data, time_series_data, user_data
    
    # 模拟数学函数
    import math
    sales_data, time_series_data, user_data = generate_sample_data()
    
    # 分析任务列表
    analysis_tasks = [
        {
            "name": "基础统计分析 - 销售数据",
            "context": PluginContext(
                agent_id="data_analyzer",
                task_id="analysis_task",
                session_id="demo_session",
                data={
                    "analysis_type": "basic_stats",
                    "data": [item["sales"] for item in sales_data]
                }
            )
        },
        {
            "name": "趋势分析 - 销售趋势",
            "context": PluginContext(
                agent_id="data_analyzer",
                task_id="analysis_task",
                session_id="demo_session",
                data={
                    "analysis_type": "trend_analysis",
                    "data": [{"x": i, "y": item["sales"]} for i, item in enumerate(sales_data)]
                }
            )
        },
        {
            "name": "分组分析 - 按地区分组",
            "context": PluginContext(
                agent_id="data_analyzer",
                task_id="analysis_task",
                session_id="demo_session",
                data={
                    "analysis_type": "group_analysis",
                    "data": sales_data,
                    "group_by": "region"
                }
            )
        },
        {
            "name": "异常检测 - 用户收入",
            "context": PluginContext(
                agent_id="data_analyzer",
                task_id="analysis_task",
                session_id="demo_session",
                data={
                    "analysis_type": "anomaly_detection",
                    "data": [item["income"] for item in user_data]
                }
            )
        },
        {
            "name": "相关性分析 - 年龄vs收入vs满意度",
            "context": PluginContext(
                agent_id="data_analyzer",
                task_id="analysis_task",
                session_id="demo_session",
                data={
                    "analysis_type": "correlation",
                    "data": user_data
                }
            )
        },
        {
            "name": "时间序列分析",
            "context": PluginContext(
                agent_id="data_analyzer",
                task_id="analysis_task",
                session_id="demo_session",
                data={
                    "analysis_type": "time_series",
                    "data": time_series_data
                }
            )
        }
    ]
    
    print(f"\n🎯 开始执行 {len(analysis_tasks)} 个分析任务：")
    print("-" * 40)
    
    # 执行所有分析任务
    for i, task in enumerate(analysis_tasks, 1):
        print(f"\n{i}. {task['name']}：")
        result = await analyzer.execute_task(task["context"])
        
        if result.get("success"):
            print(f"   ✅ 分析完成 (耗时：{result.get('processing_time', 'N/A')})")
            
            # 显示关键结果
            if "statistics" in result:
                stats = result["statistics"]
                print(f"      📊 统计结果：平均值={stats['mean']:.2f}, 中位数={stats['median']:.2f}")
            
            elif "trend" in result:
                trend = result["trend"]
                print(f"      📈 趋势：{trend['direction']}, 变化率={trend['change_percentage']:.1f}%")
            
            elif "group_analysis" in result:
                groups = result["group_analysis"]
                print(f"      📊 分组：{result['total_groups']} 个组")
                for group_name, group_data in list(groups.items())[:2]:  # 只显示前2组
                    print(f"         - {group_name}: {group_data['count']} 项")
            
            elif "anomaly_detection" in result:
                anomaly = result["anomaly_detection"]
                print(f"      🚨 异常：{anomaly['total_anomalies']} 个 ({anomaly['anomaly_rate']:.1f}%)")
            
            elif "correlation_analysis" in result:
                correlations = result["correlation_analysis"]
                print(f"      🔗 相关性：{len(correlations)} 对字段")
                for pair, data in list(correlations.items())[:2]:  # 显示前2对
                    print(f"         - {pair}: {data['strength']} ({data['correlation']:.3f})")
            
            elif "time_series_analysis" in result:
                ts = result["time_series_analysis"]
                print(f"      📅 时序：{ts['data_points']} 个点, 趋势={ts['value_trend']}")
        
        else:
            print(f"   ❌ 分析失败：{result.get('error', '未知错误')}")
    
    # 显示总结
    print("\n" + "=" * 60)
    summary = analyzer.get_analysis_summary()
    print("📊 分析总结：")
    for key, value in summary.items():
        if key == "analysis_types_used":
            print(f"   {key}: {', '.join(value)}")
        elif isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")
    
    await analyzer.cleanup()


if __name__ == "__main__":
    asyncio.run(run_analysis_demo())