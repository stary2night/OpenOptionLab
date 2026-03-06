# OpenOptions Lab - 快速部署指南

## 方案 1：Railway 一键部署（推荐，5分钟）

### 步骤 1：创建 GitHub 仓库

访问 https://github.com/new 创建新仓库，命名为 `openoptions-backend`

### 步骤 2：上传代码

```bash
# 在本地执行以下命令
cd /mnt/okcomputer/output/backend

# 初始化 git
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit for Railway deployment"

# 添加远程仓库（替换 YOUR_USERNAME 为您的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/openoptions-backend.git

# 推送代码
git push -u origin main
```

### 步骤 3：部署到 Railway

1. 访问 https://railway.app
2. 点击 "Login" → 选择 "GitHub" 登录
3. 点击 "New Project"
4. 选择 "Deploy from GitHub repo"
5. 选择 `openoptions-backend` 仓库
6. 点击 "Add PostgreSQL" 添加数据库
7. 点击 "Add Redis" 添加缓存
8. 点击 "Deploy" 按钮

### 步骤 4：设置环境变量

在 Railway 控制台 → Variables 中添加：

```
SECRET_KEY=your-super-secret-key-change-this
```

生成随机密钥：
```bash
openssl rand -hex 32
```

### 步骤 5：数据库迁移

在 Railway 控制台 → 点击您的服务 → "Command" 标签：

```bash
alembic upgrade head
```

### 步骤 6：获取 API 地址

部署完成后，Railway 会分配域名：

```
https://your-app-name.up.railway.app
```

API 文档地址：
```
https://your-app-name.up.railway.app/docs
```

---

## 方案 2：Render 部署（备选）

Render 也提供免费部署，步骤类似：

1. 访问 https://render.com
2. 用 GitHub 登录
3. 点击 "New Web Service"
4. 选择您的仓库
5. 选择 "Docker" 环境
6. 点击 "Create Web Service"

---

## 方案 3：本地 Docker 部署

如果您有服务器，可以直接用 Docker：

```bash
# 1. 进入后端目录
cd /mnt/okcomputer/output/backend

# 2. 启动所有服务
docker-compose up -d

# 3. 运行数据库迁移
docker-compose exec api alembic upgrade head

# 4. 访问 API
# http://localhost:8000
```

---

## 更新前端配置

部署后端后，修改前端配置：

```bash
cd /mnt/okcomputer/output/app

# 创建环境变量文件
echo "VITE_API_BASE_URL=https://your-railway-app.up.railway.app" > .env

# 重新构建
npm run build

# 部署前端（使用您之前的方式）
```

---

## 需要帮助？

如果您在执行过程中遇到问题，请告诉我：
1. 您卡在哪一步？
2. 有什么错误信息？
3. 您希望使用哪种部署方式？

我可以提供更详细的指导！
