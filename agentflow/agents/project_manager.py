"""
项目经理Agent
负责项目规划、需求分析、进度管理和风险控制
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from .base import BaseAgent
from ..core.types import AgentRole, AgentCapability, TechStack, get_agent_capability
from ..core.task import Task

logger = logging.getLogger(__name__)

class ProjectManagerAgent(BaseAgent):
    """项目经理Agent"""
    
    def __init__(self):
        capability = get_agent_capability(AgentRole.PROJECT_MANAGER)
        super().__init__(AgentRole.PROJECT_MANAGER, capability)
        
        # 项目管理专用工具
        self._init_pm_tools()
        
        # 项目管理配置
        self.configure(
            risk_threshold=0.7,
            timeline_buffer=0.2,  # 20%时间缓冲
            quality_gate_enabled=True
        )
    
    def _init_pm_tools(self):
        """初始化项目管理工具"""
        self.tools.update({
            "requirement_analyzer": self._analyze_requirements,
            "timeline_estimator": self._estimate_timeline,
            "risk_assessor": self._assess_risks,
            "resource_planner": self._plan_resources,
            "progress_tracker": self._track_progress,
            "stakeholder_communicator": self._communicate_with_stakeholders
        })
    
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """执行项目管理任务"""
        logger.info(f"项目经理开始执行任务: {task.title}")
        
        try:
            # 分析任务类型
            task_type = self._identify_task_type(task)
            
            # 根据任务类型执行相应的工作流
            if "需求分析" in task.title:
                result = await self._execute_requirement_analysis(task)
            elif "项目规划" in task.title:
                result = await self._execute_project_planning(task)
            elif "风险评估" in task.title:
                result = await self._execute_risk_assessment(task)
            elif "进度管理" in task.title:
                result = await self._execute_progress_management(task)
            else:
                result = await self._execute_general_pm_task(task)
            
            # 添加通用的项目管理元数据
            result.update({
                "pm_metadata": {
                    "task_type": task_type,
                    "complexity_score": self._calculate_complexity_score(task),
                    "estimated_effort": self._estimate_effort(task),
                    "quality_score": self._assess_quality(result)
                }
            })
            
            return result
            
        except Exception as e:
            logger.error(f"项目经理任务执行失败: {e}")
            raise
    
    def _identify_task_type(self, task: Task) -> str:
        """识别任务类型"""
        title_lower = task.title.lower()
        
        if any(keyword in title_lower for keyword in ["需求", "requirement", "分析"]):
            return "requirement_analysis"
        elif any(keyword in title_lower for keyword in ["规划", "planning", "计划"]):
            return "project_planning"
        elif any(keyword in title_lower for keyword in ["风险", "risk", "评估"]):
            return "risk_assessment"
        elif any(keyword in title_lower for keyword in ["进度", "progress", "跟踪"]):
            return "progress_tracking"
        else:
            return "general_management"
    
    async def _execute_requirement_analysis(self, task: Task) -> Dict[str, Any]:
        """执行需求分析"""
        logger.info("执行需求分析工作流")
        
        # 模拟需求分析过程
        await asyncio.sleep(0.1)
        
        # 从任务上下文获取需求信息
        requirements = task.context.get("requirements", [])
        project_description = task.context.get("project_description", "")
        
        # 需求分析结果
        analyzed_requirements = []
        for i, req in enumerate(requirements, 1):
            analyzed_requirements.append({
                "id": f"REQ-{i:03d}",
                "description": req,
                "priority": self._prioritize_requirement(req),
                "complexity": self._assess_requirement_complexity(req),
                "dependencies": self._identify_requirement_dependencies(req, requirements),
                "acceptance_criteria": self._generate_acceptance_criteria(req)
            })
        
        # 功能性和非功能性需求分类
        functional_requirements = [req for req in analyzed_requirements 
                                 if self._is_functional_requirement(req["description"])]
        non_functional_requirements = [req for req in analyzed_requirements 
                                     if not self._is_functional_requirement(req["description"])]
        
        # 干系人分析
        stakeholders = self._identify_stakeholders(task.context)
        
        # 项目范围定义
        scope = self._define_project_scope(analyzed_requirements, task.context)
        
        return {
            "status": "completed",
            "deliverables": {
                "requirement_document": {
                    "functional_requirements": functional_requirements,
                    "non_functional_requirements": non_functional_requirements,
                    "total_requirements": len(analyzed_requirements),
                    "high_priority_count": len([r for r in analyzed_requirements if r["priority"] == "高"]),
                    "complexity_distribution": self._get_complexity_distribution(analyzed_requirements)
                },
                "stakeholder_analysis": stakeholders,
                "project_scope": scope,
                "requirement_traceability_matrix": self._create_traceability_matrix(analyzed_requirements)
            },
            "metrics": {
                "analysis_coverage": "100%",
                "requirement_completeness": self._assess_requirement_completeness(analyzed_requirements),
                "stakeholder_alignment": "高"
            },
            "recommendations": self._generate_requirement_recommendations(analyzed_requirements)
        }
    
    async def _execute_project_planning(self, task: Task) -> Dict[str, Any]:
        """执行项目规划"""
        logger.info("执行项目规划工作流")
        
        await asyncio.sleep(0.1)
        
        # 获取项目信息
        project_name = task.context.get("project_name", "未命名项目")
        requirements = task.context.get("requirements", [])
        tech_stack = task.tech_requirements
        complexity = task.context.get("complexity", "medium")
        
        # 工作分解结构 (WBS)
        wbs = self._create_work_breakdown_structure(requirements, tech_stack)
        
        # 时间估算
        timeline = self._estimate_project_timeline(wbs, complexity)
        
        # 资源规划
        resource_plan = self._plan_project_resources(wbs, tech_stack)
        
        # 里程碑定义
        milestones = self._define_milestones(timeline)
        
        # 风险登记册
        risk_register = self._create_risk_register(tech_stack, complexity)
        
        # 质量计划
        quality_plan = self._create_quality_plan(requirements, tech_stack)
        
        return {
            "status": "completed",
            "deliverables": {
                "project_plan": {
                    "project_name": project_name,
                    "wbs": wbs,
                    "timeline": timeline,
                    "milestones": milestones,
                    "estimated_duration": f"{timeline['total_weeks']}周",
                    "estimated_effort": f"{timeline['total_hours']}小时"
                },
                "resource_plan": resource_plan,
                "risk_register": risk_register,
                "quality_plan": quality_plan,
                "communication_plan": self._create_communication_plan()
            },
            "metrics": {
                "planning_completeness": "95%",
                "resource_utilization": "85%",
                "timeline_confidence": "高"
            },
            "next_steps": [
                "获得干系人批准",
                "启动开发团队",
                "建立监控机制",
                "开始需求细化"
            ]
        }
    
    async def _execute_risk_assessment(self, task: Task) -> Dict[str, Any]:
        """执行风险评估"""
        logger.info("执行风险评估工作流")
        
        await asyncio.sleep(0.1)
        
        # 识别项目风险
        risks = self._identify_project_risks(task)
        
        # 风险评估和量化
        assessed_risks = []
        for risk in risks:
            assessed_risk = {
                "id": risk["id"],
                "description": risk["description"],
                "category": risk["category"],
                "probability": risk["probability"],
                "impact": risk["impact"],
                "risk_score": risk["probability"] * risk["impact"],
                "mitigation_strategy": risk["mitigation"],
                "contingency_plan": risk["contingency"],
                "owner": risk["owner"]
            }
            assessed_risks.append(assessed_risk)
        
        # 风险优先级排序
        high_priority_risks = [r for r in assessed_risks if r["risk_score"] >= 15]
        medium_priority_risks = [r for r in assessed_risks if 8 <= r["risk_score"] < 15]
        low_priority_risks = [r for r in assessed_risks if r["risk_score"] < 8]
        
        # 整体风险评估
        overall_risk_level = self._calculate_overall_risk_level(assessed_risks)
        
        return {
            "status": "completed",
            "deliverables": {
                "risk_assessment": {
                    "total_risks": len(assessed_risks),
                    "high_priority_risks": high_priority_risks,
                    "medium_priority_risks": medium_priority_risks,
                    "low_priority_risks": low_priority_risks,
                    "overall_risk_level": overall_risk_level
                },
                "risk_response_plan": {
                    "immediate_actions": [r["mitigation_strategy"] for r in high_priority_risks],
                    "monitoring_plan": "周度风险审查",
                    "escalation_criteria": "风险评分>20或影响>4"
                },
                "risk_monitoring_dashboard": {
                    "key_indicators": ["技术债务", "团队稳定性", "需求变更频率"],
                    "alert_thresholds": {"high": 15, "medium": 8}
                }
            },
            "metrics": {
                "risk_coverage": "100%",
                "mitigation_completeness": "90%",
                "overall_risk_score": sum(r["risk_score"] for r in assessed_risks)
            },
            "recommendations": self._generate_risk_recommendations(assessed_risks)
        }
    
    async def _execute_progress_management(self, task: Task) -> Dict[str, Any]:
        """执行进度管理"""
        logger.info("执行进度管理工作流")
        
        await asyncio.sleep(0.1)
        
        # 模拟项目进度数据
        progress_data = self._simulate_progress_data(task)
        
        return {
            "status": "completed",
            "deliverables": {
                "progress_report": progress_data,
                "performance_metrics": self._calculate_performance_metrics(progress_data),
                "forecast": self._forecast_project_completion(progress_data)
            }
        }
    
    async def _execute_general_pm_task(self, task: Task) -> Dict[str, Any]:
        """执行通用项目管理任务"""
        logger.info("执行通用项目管理任务")
        
        await asyncio.sleep(0.1)
        
        return {
            "status": "completed",
            "deliverables": {
                "task_output": f"已完成项目管理任务: {task.title}",
                "recommendations": ["建议定期评审", "保持沟通畅通"],
                "next_actions": ["跟进执行情况", "更新项目状态"]
            }
        }
    
    # 辅助方法
    def _prioritize_requirement(self, requirement: str) -> str:
        """需求优先级评估"""
        # 简化的优先级评估逻辑
        high_priority_keywords = ["用户", "安全", "登录", "认证", "核心"]
        medium_priority_keywords = ["管理", "报表", "统计", "搜索"]
        
        req_lower = requirement.lower()
        
        if any(keyword in req_lower for keyword in high_priority_keywords):
            return "高"
        elif any(keyword in req_lower for keyword in medium_priority_keywords):
            return "中"
        else:
            return "低"
    
    def _assess_requirement_complexity(self, requirement: str) -> str:
        """评估需求复杂度"""
        complex_keywords = ["集成", "同步", "算法", "机器学习", "大数据"]
        simple_keywords = ["显示", "列表", "基本", "简单"]
        
        req_lower = requirement.lower()
        
        if any(keyword in req_lower for keyword in complex_keywords):
            return "复杂"
        elif any(keyword in req_lower for keyword in simple_keywords):
            return "简单"
        else:
            return "中等"
    
    def _identify_requirement_dependencies(self, requirement: str, all_requirements: List[str]) -> List[str]:
        """识别需求依赖"""
        dependencies = []
        
        # 简化的依赖识别逻辑
        if "用户" in requirement and "认证" not in requirement:
            auth_reqs = [req for req in all_requirements if "认证" in req or "登录" in req]
            dependencies.extend(auth_reqs[:1])  # 添加第一个认证相关需求
        
        return dependencies
    
    def _generate_acceptance_criteria(self, requirement: str) -> List[str]:
        """生成验收标准"""
        return [
            f"功能正确实现: {requirement}",
            "用户体验良好",
            "性能满足要求",
            "安全性验证通过"
        ]
    
    def _is_functional_requirement(self, requirement: str) -> bool:
        """判断是否为功能性需求"""
        non_functional_keywords = ["性能", "安全", "可用性", "可扩展", "响应时间"]
        return not any(keyword in requirement for keyword in non_functional_keywords)
    
    def _identify_stakeholders(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """识别项目干系人"""
        return [
            {"role": "产品经理", "interest": "高", "influence": "高"},
            {"role": "开发团队", "interest": "中", "influence": "中"},
            {"role": "最终用户", "interest": "高", "influence": "低"},
            {"role": "运维团队", "interest": "中", "influence": "中"}
        ]
    
    def _define_project_scope(self, requirements: List[Dict], context: Dict[str, Any]) -> Dict[str, Any]:
        """定义项目范围"""
        return {
            "included": f"实现{len(requirements)}个功能需求",
            "excluded": "第三方系统深度集成",
            "assumptions": ["团队技术能力充足", "需求相对稳定"],
            "constraints": ["预算限制", "时间约束", "技术栈限制"]
        }
    
    def _calculate_complexity_score(self, task: Task) -> float:
        """计算任务复杂度评分"""
        base_score = 1.0
        
        # 基于技术栈数量调整
        tech_count_factor = len(task.tech_requirements) * 0.1
        
        # 基于描述长度调整（更长的描述通常意味着更复杂）
        description_factor = min(len(task.description) / 100, 1.0)
        
        return base_score + tech_count_factor + description_factor
    
    def _estimate_effort(self, task: Task) -> Dict[str, Any]:
        """估算任务工作量"""
        base_hours = task.estimated_hours
        complexity_multiplier = self._calculate_complexity_score(task)
        
        estimated_hours = int(base_hours * complexity_multiplier)
        
        return {
            "base_estimate": base_hours,
            "complexity_adjusted": estimated_hours,
            "confidence_level": "中等",
            "buffer_included": "20%"
        }
    
    def _assess_quality(self, result: Dict[str, Any]) -> float:
        """评估输出质量"""
        quality_score = 0.8  # 基础质量分
        
        # 基于交付物完整性调整
        deliverables = result.get("deliverables", {})
        if len(deliverables) >= 3:
            quality_score += 0.1
        
        # 基于指标完整性调整
        metrics = result.get("metrics", {})
        if len(metrics) >= 2:
            quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    # 其他辅助方法的简化实现
    def _create_traceability_matrix(self, requirements: List[Dict]) -> Dict[str, Any]:
        return {"requirements_count": len(requirements), "traceability": "已建立"}
    
    def _assess_requirement_completeness(self, requirements: List[Dict]) -> str:
        return "90%" if len(requirements) > 3 else "70%"
    
    def _generate_requirement_recommendations(self, requirements: List[Dict]) -> List[str]:
        return ["建议进行原型验证", "需要用户反馈确认", "考虑分阶段实施"]
    
    def _get_complexity_distribution(self, requirements: List[Dict]) -> Dict[str, int]:
        from collections import Counter
        return dict(Counter(req["complexity"] for req in requirements))
    
    def _create_work_breakdown_structure(self, requirements: List[str], tech_stack: List[TechStack]) -> Dict[str, Any]:
        return {
            "phases": ["需求分析", "设计", "开发", "测试", "部署"],
            "total_tasks": len(requirements) * 2,
            "estimated_complexity": "中等"
        }
    
    def _estimate_project_timeline(self, wbs: Dict, complexity: str) -> Dict[str, Any]:
        base_weeks = 4
        complexity_multiplier = {"simple": 0.8, "medium": 1.0, "complex": 1.5}.get(complexity, 1.0)
        
        total_weeks = int(base_weeks * complexity_multiplier)
        total_hours = total_weeks * 40  # 假设每周40小时
        
        return {
            "total_weeks": total_weeks,
            "total_hours": total_hours,
            "phases": {
                "需求分析": f"{total_weeks * 0.2:.1f}周",
                "设计": f"{total_weeks * 0.3:.1f}周",
                "开发": f"{total_weeks * 0.4:.1f}周",
                "测试": f"{total_weeks * 0.1:.1f}周"
            }
        }
    
    def _plan_project_resources(self, wbs: Dict, tech_stack: List[TechStack]) -> Dict[str, Any]:
        return {
            "team_size": len(tech_stack),
            "required_skills": [tech.value for tech in tech_stack],
            "budget_estimate": "中等"
        }
    
    def _define_milestones(self, timeline: Dict) -> List[Dict[str, str]]:
        return [
            {"name": "需求确认", "date": "第1周结束"},
            {"name": "设计完成", "date": "第2周结束"},
            {"name": "开发完成", "date": f"第{timeline['total_weeks']-1}周结束"},
            {"name": "项目交付", "date": f"第{timeline['total_weeks']}周结束"}
        ]
    
    def _create_risk_register(self, tech_stack: List[TechStack], complexity: str) -> List[Dict[str, Any]]:
        risks = [
            {
                "id": "RISK-001",
                "description": "技术选型风险",
                "category": "技术",
                "probability": 3,
                "impact": 4,
                "mitigation": "技术预研和原型验证",
                "contingency": "准备备选方案",
                "owner": "技术负责人"
            },
            {
                "id": "RISK-002", 
                "description": "需求变更风险",
                "category": "需求",
                "probability": 4,
                "impact": 3,
                "mitigation": "建立变更控制流程",
                "contingency": "预留变更缓冲",
                "owner": "项目经理"
            }
        ]
        
        return risks
    
    def _create_quality_plan(self, requirements: List[str], tech_stack: List[TechStack]) -> Dict[str, Any]:
        return {
            "quality_standards": ["代码规范", "测试覆盖率>80%", "性能基准"],
            "review_process": "代码评审 + 设计评审",
            "testing_strategy": "单元测试 + 集成测试 + 用户测试"
        }
    
    def _create_communication_plan(self) -> Dict[str, Any]:
        return {
            "meetings": {
                "daily_standup": "每日站会",
                "weekly_review": "周度评审",
                "milestone_review": "里程碑评审"
            },
            "reports": ["周度进度报告", "风险状态报告"],
            "stakeholder_updates": "双周更新"
        }
    
    def _identify_project_risks(self, task: Task) -> List[Dict[str, Any]]:
        # 返回上面_create_risk_register的结果
        return self._create_risk_register(task.tech_requirements, task.context.get("complexity", "medium"))
    
    def _calculate_overall_risk_level(self, risks: List[Dict[str, Any]]) -> str:
        avg_risk_score = sum(r["risk_score"] for r in risks) / len(risks) if risks else 0
        
        if avg_risk_score >= 15:
            return "高"
        elif avg_risk_score >= 8:
            return "中"
        else:
            return "低"
    
    def _generate_risk_recommendations(self, risks: List[Dict[str, Any]]) -> List[str]:
        return [
            "建立定期风险审查机制",
            "为高风险项目制定应急预案",
            "加强团队沟通和协作"
        ]
    
    def _simulate_progress_data(self, task: Task) -> Dict[str, Any]:
        return {
            "overall_progress": "65%",
            "completed_tasks": 13,
            "total_tasks": 20,
            "on_schedule": True,
            "budget_utilization": "60%"
        }
    
    def _calculate_performance_metrics(self, progress_data: Dict) -> Dict[str, Any]:
        return {
            "velocity": "1.5任务/天",
            "quality_index": "85%",
            "team_productivity": "良好"
        }
    
    def _forecast_project_completion(self, progress_data: Dict) -> Dict[str, Any]:
        return {
            "estimated_completion": "3周后",
            "confidence_level": "80%",
            "potential_delays": ["需求变更", "资源瓶颈"]
        }
    
    # 工具方法实现
    async def _analyze_requirements(self, requirements: List[str]) -> Dict[str, Any]:
        """需求分析工具"""
        return {"analyzed": True, "count": len(requirements)}
    
    async def _estimate_timeline(self, tasks: List[str]) -> Dict[str, Any]:
        """时间估算工具"""
        return {"estimated_weeks": len(tasks) // 2}
    
    async def _assess_risks(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """风险评估工具"""
        return {"risk_level": "medium", "key_risks": 3}
    
    async def _plan_resources(self, requirements: List[str]) -> Dict[str, Any]:
        """资源规划工具"""
        return {"team_size": len(requirements) // 3}
    
    async def _track_progress(self, tasks: List[str]) -> Dict[str, Any]:
        """进度跟踪工具"""
        return {"progress": "60%", "on_track": True}
    
    async def _communicate_with_stakeholders(self, message: str) -> Dict[str, Any]:
        """干系人沟通工具"""
        return {"sent": True, "recipients": ["product_owner", "dev_team"]}

# 便捷函数
def create_project_manager() -> ProjectManagerAgent:
    """创建项目经理Agent实例"""
    return ProjectManagerAgent()