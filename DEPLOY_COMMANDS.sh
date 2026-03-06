#!/bin/bash
# OpenOptions Lab - 完整部署脚本
# 复制此脚本到本地执行

set -e

echo "🚀 OpenOptions Lab 部署脚本"
echo "=============================="

# 检查参数
if [ -z "$1" ]; then
    echo "❌ 请提供 GitHub 用户名"
    echo "用法: ./DEPLOY_COMMANDS.sh YOUR_GITHUB_USERNAME"
    exit 1
fi

GITHUB_USERNAME=$1
REPO_NAME="openoptions-backend"

echo ""
echo "📋 部署配置:"
echo "   GitHub 用户: $GITHUB_USERNAME"
echo "   仓库名称: $REPO_NAME"
echo ""

# 步骤 1: 创建 GitHub 仓库
echo "步骤 1/5: 请在浏览器中创建 GitHub 仓库"
echo "   访问: https://github.com/new"
echo "   仓库名: $REPO_NAME"
echo "   选择: Public"
echo ""
read -p "按 Enter 继续..."

# 步骤 2: 准备代码
echo ""
echo "步骤 2/5: 准备代码..."

# 创建临时目录
TEMP_DIR=$(mktemp -d)
echo "   临时目录: $TEMP_DIR"

# 复制后端代码
cp -r /mnt/okcomputer/output/backend/* "$TEMP_DIR/"
cd "$TEMP_DIR"

# 初始化 git
git init
git config user.email "deploy@openoptions.lab"
git config user.name "Deploy Bot"

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit for Railway deployment"

# 添加远程仓库
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

echo "   ✅ 代码已准备"

# 步骤 3: 推送到 GitHub
echo ""
echo "步骤 3/5: 推送到 GitHub..."
echo "   请在浏览器中登录 GitHub 并授权"
echo ""

git push -u origin master || git push -u origin main

echo "   ✅ 代码已推送到 GitHub"

# 步骤 4: Railway 部署
echo ""
echo "步骤 4/5: Railway 部署"
echo "   请按以下步骤操作:"
echo ""
echo "   1. 访问 https://railway.app"
echo "   2. 点击 'Login' → 选择 'GitHub' 登录"
echo "   3. 点击 'New Project'"
echo "   4. 选择 'Deploy from GitHub repo'"
echo "   5. 选择 '$REPO_NAME' 仓库"
echo "   6. 点击 'Add PostgreSQL' 添加数据库"
echo "   7. 点击 'Add Redis' 添加缓存"
echo "   8. 点击 'Deploy' 按钮"
echo ""
read -p "按 Enter 继续..."

# 步骤 5: 设置环境变量
echo ""
echo "步骤 5/5: 设置环境变量"
echo ""
echo "   在 Railway 控制台 → Variables 中添加:"
echo ""
echo "   SECRET_KEY=$(openssl rand -hex 32)"
echo "   DEBUG=false"
echo ""

# 生成密钥
SECRET_KEY=$(openssl rand -hex 32)
echo "   🔑 生成的 SECRET_KEY: $SECRET_KEY"
echo ""

# 清理
rm -rf "$TEMP_DIR"

echo "=============================="
echo "✅ 部署准备完成!"
echo ""
echo "📋 后续步骤:"
echo "   1. 在 Railway 控制台点击 'Deploy'"
echo "   2. 等待部署完成 (约 2-3 分钟)"
echo "   3. 运行数据库迁移:"
echo "      railway run alembic upgrade head"
echo "   4. 获取 API 地址"
echo ""
echo "📚 详细文档: /mnt/okcomputer/output/QUICK_DEPLOY.md"
echo "=============================="
