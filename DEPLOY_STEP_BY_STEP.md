# OpenOptions Lab - 一步步部署指南

## 准备工作

您需要：
1. **GitHub 账号** (https://github.com/signup)
2. **Railway 账号** (用 GitHub 登录即可)

---

## 第 1 步：创建 GitHub 仓库

1. 访问 https://github.com/new
2. 填写信息：
   - **Repository name**: `openoptions-backend`
   - **Description**: OpenOptions Lab API
   - **Public** (勾选)
3. 点击 **Create repository**

---

## 第 2 步：上传代码

### 在您的电脑上执行以下命令：

```bash
# 1. 下载后端代码到本地
mkdir -p ~/openoptions-deploy
cd ~/openoptions-deploy

# 2. 从当前环境复制代码（或手动复制 backend 文件夹）
# 如果您有后端代码，直接复制到 ~/openoptions-deploy/backend

# 3. 进入后端目录
cd backend

# 4. 初始化 git
git init

# 5. 添加所有文件
git add .

# 6. 提交
git commit -m "Initial commit for Railway deployment"

# 7. 添加远程仓库（替换 YOUR_USERNAME 为您的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/openoptions-backend.git

# 8. 推送代码
git push -u origin master
```

**如果遇到权限问题，使用以下方式：**

```bash
# 使用 GitHub Token 方式
git remote add origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/openoptions-backend.git
git push -u origin master
```

---

## 第 3 步：部署到 Railway

1. 访问 https://railway.app
2. 点击 **Login** → 选择 **Continue with GitHub**
3. 授权 Railway 访问您的 GitHub 仓库
4. 点击 **New Project**
5. 选择 **Deploy from GitHub repo**
6. 找到并选择 `openoptions-backend` 仓库
7. 点击 **Add PostgreSQL**（添加数据库）
8. 点击 **Add Redis**（添加缓存）
9. 点击 **Deploy** 按钮

等待部署完成（约 2-3 分钟）

---

## 第 4 步：设置环境变量

1. 在 Railway 控制台，点击您的项目
2. 点击 **Variables** 标签
3. 点击 **New Variable** 添加以下变量：

```
SECRET_KEY=your-super-secret-key-here
DEBUG=false
```

**生成随机密钥：**

在终端执行：
```bash
openssl rand -hex 32
```

将生成的字符串作为 `SECRET_KEY` 的值

---

## 第 5 步：数据库迁移

1. 在 Railway 控制台，点击您的服务
2. 点击 **Command** 标签
3. 输入并执行：

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

---

## 第 6 步：获取 API 地址

1. 在 Railway 控制台，点击您的服务
2. 找到 **Domains** 部分
3. 您的 API 地址类似：

```
https://openoptions-backend.up.railway.app
```

**测试 API：**

```bash
curl https://your-app-name.up.railway.app/api/v1/health/
```

**API 文档：**

```
https://your-app-name.up.railway.app/docs
```

---

## 第 7 步：更新前端配置

1. 修改前端 `.env` 文件：

```bash
cd /path/to/your/frontend

# 创建环境变量文件
echo "VITE_API_BASE_URL=https://your-railway-app.up.railway.app" > .env
```

2. 重新构建前端：

```bash
npm run build
```

3. 部署前端（按照之前的方式）

---

## 完成！

现在您拥有：
- ✅ 前端：https://tqcpp6nizuxus.ok.kimi.link
- ✅ 后端：https://your-railway-app.up.railway.app
- ✅ 数据库：PostgreSQL (Railway 托管)
- ✅ 缓存：Redis (Railway 托管)

---

## 故障排查

### 问题 1：部署失败

**检查：**
1. Dockerfile 是否在仓库根目录
2. requirements.txt 是否包含所有依赖
3. 查看 Railway 日志找出错误

### 问题 2：数据库连接失败

**检查：**
1. PostgreSQL 是否已添加
2. 环境变量 `DATABASE_URL` 是否自动设置

### 问题 3：API 返回 500

**检查：**
1. `SECRET_KEY` 是否已设置
2. 数据库迁移是否已执行

---

## 需要帮助？

如果在部署过程中遇到问题，请告诉我：
1. 您在哪一步遇到问题？
2. 有什么错误信息？
3. 我可以帮您远程调试
