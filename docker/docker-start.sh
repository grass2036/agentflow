#!/bin/bash

# AgentFlow Docker 启动脚本
# Docker startup script for AgentFlow

set -e

echo "🌊 AgentFlow Docker 部署脚本"
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装。请先安装 Docker。${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose 未安装。请先安装 Docker Compose。${NC}"
    exit 1
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 文件不存在，从模板创建...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 请编辑 .env 文件并填入您的 API keys${NC}"
    echo -e "${YELLOW}📝 完成后重新运行此脚本${NC}"
    exit 1
fi

# 显示菜单
echo -e "${BLUE}请选择启动模式:${NC}"
echo "1) 🚀 基础模式 (AgentFlow + Redis)"
echo "2) 💾 完整模式 (+ PostgreSQL 数据库)"
echo "3) 🌐 全功能模式 (+ Web 界面)"
echo "4) 🧹 清理和重建"
echo "5) 📊 查看日志"
echo "6) 🛑 停止服务"
echo

read -p "请输入选择 (1-6): " choice

case $choice in
    1)
        echo -e "${GREEN}🚀 启动基础模式...${NC}"
        docker-compose up -d agentflow redis
        ;;
    2)
        echo -e "${GREEN}💾 启动完整模式...${NC}"
        docker-compose --profile database up -d
        ;;
    3)
        echo -e "${GREEN}🌐 启动全功能模式...${NC}"
        docker-compose --profile database --profile web up -d
        ;;
    4)
        echo -e "${YELLOW}🧹 清理和重建...${NC}"
        docker-compose down -v
        docker-compose build --no-cache
        docker-compose up -d agentflow redis
        ;;
    5)
        echo -e "${BLUE}📊 显示日志...${NC}"
        docker-compose logs -f
        ;;
    6)
        echo -e "${RED}🛑 停止所有服务...${NC}"
        docker-compose down
        ;;
    *)
        echo -e "${RED}❌ 无效选择${NC}"
        exit 1
        ;;
esac

if [ $choice -le 3 ]; then
    echo
    echo -e "${GREEN}✅ 启动完成！${NC}"
    echo
    echo -e "${BLUE}📋 服务访问地址:${NC}"
    echo "🌊 AgentFlow API: http://localhost:8000"
    echo "📚 API文档: http://localhost:8000/docs"
    echo "🔍 健康检查: http://localhost:8000/health"
    echo "🔗 Redis: localhost:6379"
    
    if [ $choice -ge 2 ]; then
        echo "🗄️  PostgreSQL: localhost:5432"
    fi
    
    if [ $choice -eq 3 ]; then
        echo "🌐 Web界面: http://localhost:3000"
    fi
    
    echo
    echo -e "${BLUE}📝 常用命令:${NC}"
    echo "查看日志: docker-compose logs -f"
    echo "查看状态: docker-compose ps"
    echo "停止服务: docker-compose down"
    echo "重启服务: docker-compose restart"
    echo
    echo -e "${YELLOW}💡 提示: 使用 './docker-start.sh' 可重新显示此菜单${NC}"
fi