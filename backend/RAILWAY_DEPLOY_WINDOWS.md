# Railway 部署步骤（Windows PowerShell）

## 步骤 1：安装 Railway CLI

以管理员身份打开 PowerShell，执行：

```powershell
# 安装 Railway CLI
npm install -g @railway/cli

# 验证安装
railway --version
```

## 步骤 2：登录 Railway

```powershell
# 登录（会打开浏览器）
railway login
```

在浏览器中点击 "Authorize" 授权。

## 步骤 3：进入后端目录并初始化项目

```powershell
# 进入 backend 目录
cd C:\Users\dengl\Downloads\backend

# 初始化 Railway 项目
railway init --name "openoptionlab-backend"
```

如果提示项目已存在，执行：
```powershell
railway link
```

## 步骤 4：添加数据库

```powershell
# 添加 PostgreSQL
railway add --database postgres

# 添加 Redis
railway add --database redis
```

## 步骤 5：设置环境变量

```powershell
# 生成随机密钥
$SECRET_KEY = -join ((1..32) | ForEach-Object { "{0:X2}" -f (Get-Random -Maximum 256) })
Write-Host "SECRET_KEY: $SECRET_KEY"

# 设置环境变量
railway variables set SECRET_KEY="$SECRET_KEY"
railway variables set DEBUG="false"
railway variables set APP_NAME="OpenOptionLab API"
railway variables set APP_VERSION="1.0.0"
```

## 步骤 6：部署应用

```powershell
# 部署
railway up
```

等待部署完成（约 2-3 分钟）。

## 步骤 7：数据库迁移

```powershell
# 运行数据库迁移
railway run alembic upgrade head
```

## 步骤 8：获取部署地址

```powershell
# 查看部署域名
railway domain

# 查看状态
railway status

# 查看日志
railway logs
```

## 完成！

部署成功后，您的 API 地址将是：
- API 文档：`https://your-app.up.railway.app/docs`
- API 地址：`https://your-app.up.railway.app`

## 常用命令

```powershell
# 重新部署
railway up

# 查看变量
railway variables

# 打开 Railway 控制台
railway open
```
