#!/bin/bash
# Railway 自动部署脚本
# 由红烧大虾生成

echo "=========================================="
echo "🚀 OpenOptionLab Railway 自动部署脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查命令
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "📋 步骤 1: 安装 Railway CLI"
echo "----------------------------------------"

if command_exists railway; then
    echo -e "${GREEN}✓${NC} Railway CLI 已安装"
else
    echo "正在安装 Railway CLI..."
    npm install -g @railway/cli
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗${NC} 安装失败，请手动安装: npm install -g @railway/cli"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} Railway CLI 安装成功"
fi

echo ""
echo "📋 步骤 2: 登录 Railway"
echo "----------------------------------------"
echo "这将打开浏览器让您登录 Railway..."
railway login

if [ $? -ne 0 ]; then
    echo -e "${RED}✗${NC} 登录失败"
    exit 1
fi

echo -e "${GREEN}✓${NC} 登录成功"

echo ""
echo "📋 步骤 3: 创建项目"
echo "----------------------------------------"

# 进入后端目录
cd "$(dirname "$0")"

echo "当前目录: $(pwd)"
echo "创建 Railway 项目..."

railway init --name "openoptionlab-backend"

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}!${NC} 项目可能已存在，尝试关联现有项目..."
    railway link
fi

echo ""
echo "📋 步骤 4: 添加 PostgreSQL 数据库"
echo "----------------------------------------"

railway add --database postgres

echo ""
echo "📋 步骤 5: 添加 Redis 缓存"
echo "----------------------------------------"

railway add --database redis

echo ""
echo "📋 步骤 6: 设置环境变量"
echo "----------------------------------------"

# 生成随机密钥
SECRET_KEY=$(openssl rand -hex 32)
echo "生成的 SECRET_KEY: $SECRET_KEY"

railway variables set SECRET_KEY="$SECRET_KEY"
railway variables set DEBUG="false"
railway variables set APP_NAME="OpenOptionLab API"
railway variables set APP_VERSION="1.0.0"

echo -e "${GREEN}✓${NC} 环境变量设置完成"

echo ""
echo "📋 步骤 7: 部署应用"
echo "----------------------------------------"

echo "开始部署..."
railway up

if [ $? -ne 0 ]; then
    echo -e "${RED}✗${NC} 部署失败"
    exit 1
fi

echo -e "${GREEN}✓${NC} 部署成功！"

echo ""
echo "📋 步骤 8: 数据库迁移"
echo "----------------------------------------"

echo "运行数据库迁移..."
railway run alembic upgrade head

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}!${NC} 数据库迁移可能已执行或遇到问题"
fi

echo ""
echo "=========================================="
echo "🎉 部署完成！"
echo "=========================================="
echo ""

# 获取部署域名
echo "获取部署信息..."
railway domain

echo ""
echo "📊 部署详情:"
echo "----------------------------------------"
railway status

echo ""
echo "🔗 访问地址:"
echo "  - API 文档: https://$(railway domain | head -1)/docs"
echo "  - API 地址: https://$(railway domain | head -1)"
echo ""
echo "📋 常用命令:"
echo "  - 查看日志: railway logs"
echo "  - 查看变量: railway variables"
echo "  - 重新部署: railway up"
echo "  - 打开控制台: railway open"
echo ""
echo "=========================================="
