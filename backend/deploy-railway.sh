#!/bin/bash
# OpenOptions Lab - Railway 部署脚本

set -e

echo "🚀 OpenOptions Lab Railway 部署脚本"
echo "======================================"

# 检查 Railway CLI
if ! command -v railway &> /dev/null; then
    echo "📦 安装 Railway CLI..."
    npm install -g @railway/cli
fi

# 登录 Railway
echo "🔑 登录 Railway..."
railway login

# 检查是否在项目目录
if [ ! -f "railway.json" ]; then
    echo "❌ 错误：请在 backend 目录运行此脚本"
    exit 1
fi

# 初始化项目（如果不存在）
echo "📁 初始化 Railway 项目..."
railway init --name openoptions-api || true

# 链接项目
echo "🔗 链接到 Railway 项目..."
railway link

# 检查数据库
echo "🗄️  检查数据库..."
railway add --database postgres || echo "PostgreSQL 已存在"
railway add --database redis || echo "Redis 已存在"

# 设置环境变量
echo "⚙️  设置环境变量..."
railway variables set DEBUG=false
railway variables set APP_NAME="OpenOptions Lab API"
railway variables set APP_VERSION="1.0.0"

# 生成随机密钥
SECRET_KEY=$(openssl rand -hex 32)
railway variables set SECRET_KEY="$SECRET_KEY"
echo "✅ 已生成 SECRET_KEY"

# 部署
echo "🚀 开始部署..."
railway up

# 运行数据库迁移
echo "🗄️  运行数据库迁移..."
railway run alembic upgrade head

# 获取域名
echo ""
echo "======================================"
echo "✅ 部署完成！"
echo ""
echo "🌐 API 地址："
railway domain
echo ""
echo "📚 API 文档："
echo "   https://$(railway domain | tail -1)/docs"
echo ""
echo "🔧 管理控制台："
echo "   https://railway.app/dashboard"
echo "======================================"
