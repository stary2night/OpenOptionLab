#!/bin/bash
# Railway 自动部署脚本
# 由红烧大虾生成

echo "=========================================="
echo "🚀 OpenOptionLab Railway 部署脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "📋 步骤 1: 检查环境"
echo "----------------------------------------"

# 检查 Git
if command_exists git; then
    echo -e "${GREEN}✓${NC} Git 已安装: $(git --version)"
else
    echo -e "${RED}✗${NC} Git 未安装，请先安装 Git"
    exit 1
fi

# 检查 GitHub CLI (可选)
if command_exists gh; then
    echo -e "${GREEN}✓${NC} GitHub CLI 已安装"
    GH_CLI=true
else
    echo -e "${YELLOW}!${NC} GitHub CLI 未安装（可选，用于自动创建仓库）"
    GH_CLI=false
fi

echo ""
echo "📋 步骤 2: 配置信息"
echo "----------------------------------------"

# 获取配置
read -p "请输入 GitHub 用户名: " GITHUB_USER
read -p "请输入仓库名称 (默认: openoptionlab-backend): " REPO_NAME
REPO_NAME=${REPO_NAME:-openoptionlab-backend}
read -p "请输入提交信息 (默认: Initial commit for Railway deployment): " COMMIT_MSG
COMMIT_MSG=${COMMIT_MSG:-"Initial commit for Railway deployment"}

echo ""
echo "配置信息:"
echo "  GitHub 用户: $GITHUB_USER"
echo "  仓库名称: $REPO_NAME"
echo "  提交信息: $COMMIT_MSG"
echo ""

# 确认
read -p "确认无误? (y/n): " confirm
if [[ $confirm != [yY] ]]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "📋 步骤 3: 准备代码"
echo "----------------------------------------"

# 进入后端目录
BACKEND_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BACKEND_DIR"

echo "当前目录: $(pwd)"

# 检查是否已经是 git 仓库
if [ -d ".git" ]; then
    echo -e "${YELLOW}!${NC} 已存在 git 仓库，将使用现有仓库"
    git status
else
    echo "初始化 git 仓库..."
    git init
    git branch -M main
fi

echo ""
echo "📋 步骤 4: 配置 Git"
echo "----------------------------------------"

# 检查远程仓库
if git remote get-url origin >/dev/null 2>&1; then
    echo -e "${YELLOW}!${NC} 远程仓库已存在:"
    git remote -v
    read -p "是否更新远程仓库地址? (y/n): " update_remote
    if [[ $update_remote == [yY] ]]; then
        git remote remove origin
        git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
    fi
else
    git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
fi

echo ""
echo "📋 步骤 5: 提交代码"
echo "----------------------------------------"

# 添加所有文件
git add .

# 检查是否有变更
if git diff --cached --quiet; then
    echo -e "${YELLOW}!${NC} 没有新的变更需要提交"
else
    git commit -m "$COMMIT_MSG"
    echo -e "${GREEN}✓${NC} 代码已提交"
fi

echo ""
echo "📋 步骤 6: 推送到 GitHub"
echo "----------------------------------------"

echo "推送代码到 GitHub..."
echo "如果提示输入密码，请输入 GitHub Personal Access Token"
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} 代码推送成功!"
    echo ""
    echo "仓库地址: https://github.com/$GITHUB_USER/$REPO_NAME"
else
    echo -e "${RED}✗${NC} 推送失败，请检查:"
    echo "  1. GitHub 仓库是否已创建"
    echo "  2. 是否有推送权限"
    echo "  3. 是否正确配置了 Git 凭证"
    exit 1
fi

echo ""
echo "=========================================="
echo "🎉 代码推送完成!"
echo "=========================================="
echo ""
echo "下一步: 部署到 Railway"
echo "----------------------------------------"
echo "1. 访问 https://railway.app"
echo "2. 使用 GitHub 账号登录"
echo "3. 点击 'New Project'"
echo "4. 选择 'Deploy from GitHub repo'"
echo "5. 选择 '$REPO_NAME' 仓库"
echo "6. 点击 'New' → 'Database' → 'Add PostgreSQL'"
echo "7. 点击 'New' → 'Database' → 'Add Redis'"
echo "8. 在 Variables 中添加 SECRET_KEY"
echo "9. 点击 'Deploy'"
echo ""
echo "生成随机密钥命令:"
echo "  openssl rand -hex 32"
echo ""
echo "部署完成后，API 地址将是:"
echo "  https://$REPO_NAME.up.railway.app"
echo ""
echo "API 文档地址:"
echo "  https://$REPO_NAME.up.railway.app/docs"
echo ""
echo "=========================================="
