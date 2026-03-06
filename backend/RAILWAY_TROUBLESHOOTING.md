# Railway 部署故障排查指南

## 🔴 部署失败的常见原因

### 1. 环境变量未设置

**检查命令：**
```powershell
railway variables
```

**必须设置的变量：**
```powershell
railway variables set SECRET_KEY="your-random-secret-key-here"
```

生成密钥：
```powershell
# PowerShell
-join ((1..32) | ForEach-Object { "{0:X2}" -f (Get-Random -Maximum 256) })
```

### 2. 数据库未添加

**检查命令：**
```powershell
railway status
```

**添加数据库：**
```powershell
railway add --database postgres
railway add --database redis
```

### 3. 数据库迁移未执行

**执行迁移：**
```powershell
railway run alembic upgrade head
```

### 4. 查看详细日志

```powershell
# 实时查看日志
railway logs --follow

# 查看最新100行
railway logs --tail 100
```

---

## ✅ 完整的重新部署步骤

如果部署失败，按以下步骤重新部署：

### 步骤 1：删除旧项目（可选）
```powershell
# 在 Railway 控制台删除项目，或使用 CLI
railway delete
```

### 步骤 2：重新初始化
```powershell
cd C:\Users\dengl\Downloads\backend
railway init --name "openoptionlab-backend"
```

### 步骤 3：添加数据库
```powershell
railway add --database postgres
railway add --database redis
```

### 步骤 4：设置环境变量
```powershell
$SECRET_KEY = -join ((1..32) | ForEach-Object { "{0:X2}" -f (Get-Random -Maximum 256) })
railway variables set SECRET_KEY="$SECRET_KEY"
railway variables set DEBUG="false"
```

### 步骤 5：部署
```powershell
railway up
```

### 步骤 6：数据库迁移
```powershell
railway run alembic upgrade head
```

### 步骤 7：验证
```powershell
railway status
railway domain
```

---

## 🔍 调试技巧

### 检查容器是否启动
```powershell
railway logs
# 查找 "Application startup complete" 或错误信息
```

### 测试数据库连接
```powershell
railway run python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
```

### 手动运行应用测试
```powershell
railway run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 🆘 如果还是失败

请提供以下信息：
1. `railway logs` 的完整输出
2. `railway status` 的输出
3. `railway variables` 的输出（隐藏 SECRET_KEY）

这样可以帮助定位具体问题！
