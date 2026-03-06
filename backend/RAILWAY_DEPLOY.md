# Railway 一键部署指南

## 什么是 Railway？

Railway 是一个现代化的云平台，可以一键部署应用和数据库，无需配置服务器。

## 部署步骤

### 第一步：准备代码

确保您的代码已推送到 GitHub：

```bash
# 在 backend 目录初始化 git
cd /mnt/okcomputer/output/backend
git init
git add .
git commit -m "Initial commit for Railway deployment"

# 创建 GitHub 仓库并推送
git remote add origin https://github.com/YOUR_USERNAME/openoptions-backend.git
git push -u origin main
```

### 第二步：注册 Railway

1. 访问 https://railway.app
2. 点击 "Get Started" 使用 GitHub 账号登录

### 第三步：创建项目

1. 点击 "New Project"
2. 选择 "Deploy from GitHub repo"
3. 选择您的 `openoptions-backend` 仓库

### 第四步：添加数据库

1. 点击 "New" → "Database" → "Add PostgreSQL"
2. 点击 "New" → "Database" → "Add Redis"

Railway 会自动设置环境变量：
- `DATABASE_URL` - PostgreSQL 连接地址
- `REDIS_URL` - Redis 连接地址

### 第五步：配置环境变量

在 Railway 项目设置中添加以下变量：

```
SECRET_KEY=your-super-secret-key-here-change-this
DEBUG=false
APP_NAME=OpenOptions Lab API
APP_VERSION=1.0.0
```

生成随机密钥：
```bash
openssl rand -hex 32
```

### 第六步：部署

1. 点击 "Deploy" 按钮
2. 等待部署完成（约 2-3 分钟）
3.  Railway 会自动分配域名，如：`https://openoptions-backend.up.railway.app`

### 第七步：数据库迁移

部署完成后，运行数据库迁移：

1. 在 Railway 控制台点击 "New" → "Command"
2. 运行：
```bash
alembic upgrade head
```

或者使用 Railway CLI：
```bash
# 安装 Railway CLI
npm install -g @railway/cli

# 登录
railway login

# 选择项目
railway link

# 运行迁移
railway run alembic upgrade head
```

## 获取 API 地址

部署成功后，您的后端 API 地址为：

```
https://your-app-name.up.railway.app
```

API 文档地址：
```
https://your-app-name.up.railway.app/docs
```

## 更新前端配置

修改前端 `.env` 文件：

```bash
VITE_API_BASE_URL=https://your-app-name.up.railway.app
```

然后重新构建并部署前端。

## 监控和日志

在 Railway 控制台可以查看：
- 应用日志
- 资源使用情况
- 部署历史

## 自定义域名（可选）

1. 在 Railway 项目设置中找到 "Domains"
2. 点击 "Custom Domain"
3. 输入您的域名（如 `api.openoptions.com`）
4. 按照提示配置 DNS

## 费用说明

Railway 免费额度：
- 执行时间：500 小时/月
- 内存：512 MB
- 磁盘：1 GB
- 出站流量：100 GB/月
- PostgreSQL：500 MB
- Redis：完全免费

超出免费额度后按量计费，通常每月 $5-20 足够个人使用。

## 故障排查

### 部署失败

1. 检查 Dockerfile 是否正确
2. 查看 Railway 日志找出错误
3. 确保 requirements.txt 包含所有依赖

### 数据库连接失败

1. 确认 PostgreSQL 和 Redis 已添加
2. 检查环境变量是否正确设置
3. 查看应用日志中的连接错误

### API 返回 500 错误

1. 检查 `SECRET_KEY` 是否设置
2. 确认数据库迁移已执行
3. 查看应用日志

## 更新部署

代码更新后自动重新部署：

```bash
git add .
git commit -m "Update features"
git push
```

Railway 会自动检测并重新部署。
