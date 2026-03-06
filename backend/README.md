# OpenOptions Lab API

专业的期权数据分析平台后端 API

## 技术栈

- **框架**: FastAPI (Python 3.11+)
- **数据库**: PostgreSQL + TimescaleDB (时序数据)
- **缓存**: Redis
- **任务队列**: Celery
- **容器化**: Docker + Docker Compose

## 快速开始

### 使用 Docker Compose (推荐)

```bash
# 1. 克隆项目并进入目录
cd backend

# 2. 复制环境变量文件
cp .env.example .env

# 3. 启动所有服务
docker-compose up -d

# 4. 查看 API 文档
open http://localhost:8000/docs
```

### 本地开发

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件配置数据库连接

# 4. 运行数据库迁移
alembic upgrade head

# 5. 启动开发服务器
uvicorn app.main:app --reload
```

## API 端点

### 认证
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新 Token
- `GET /api/v1/auth/me` - 获取当前用户信息
- `POST /api/v1/auth/password-reset/request` - 请求密码重置
- `POST /api/v1/auth/password-reset/confirm` - 确认密码重置
- `POST /api/v1/auth/email/verify-request` - 请求邮箱验证
- `POST /api/v1/auth/email/verify/{token}` - 验证邮箱
- `PUT /api/v1/auth/password` - 修改密码
- `PUT /api/v1/auth/profile` - 更新个人资料
- `POST /api/v1/auth/avatar` - 上传头像

### 行情数据
- `GET /api/v1/market/snapshot` - 市场快照
- `GET /api/v1/market/snapshot/{symbol}` - 品种详情
- `GET /api/v1/market/{symbol}/history` - 历史数据
- `GET /api/v1/market/top/iv-rise` - 隐波上升排行
- `GET /api/v1/market/top/iv-fall` - 隐波下降排行
- `GET /api/v1/market/top/premium-high` - 溢价最高排行
- `GET /api/v1/market/top/premium-low` - 溢价最低排行
- `GET /api/v1/market/unusual-flows` - 异动监控

### 用户
- `GET /api/v1/user/favorites` - 获取自选股
- `POST /api/v1/user/favorites` - 添加自选股
- `DELETE /api/v1/user/favorites/{symbol}` - 删除自选股
- `PUT /api/v1/user/favorites/{symbol}/alert` - 设置价格提醒
- `GET /api/v1/user/strategies` - 获取策略列表
- `POST /api/v1/user/strategies` - 创建策略
- `GET /api/v1/user/strategies/{strategy_id}` - 获取策略详情
- `PUT /api/v1/user/strategies/{strategy_id}` - 更新策略
- `DELETE /api/v1/user/strategies/{strategy_id}` - 删除策略
- `POST /api/v1/user/strategies/{strategy_id}/toggle` - 切换策略状态
- `GET /api/v1/user/notifications` - 获取通知列表
- `PUT /api/v1/user/notifications/{notification_id}/read` - 标记通知已读
- `PUT /api/v1/user/notifications/read-all` - 标记所有通知已读
- `DELETE /api/v1/user/notifications/{notification_id}` - 删除通知
- `GET /api/v1/user/notifications/unread-count` - 获取未读通知数量

### 策略分析
- `POST /api/v1/strategy/analyze` - 分析策略
- `GET /api/v1/strategy/templates` - 获取策略模板

### 健康检查
- `GET /api/v1/health/` - 基础健康检查
- `GET /api/v1/health/db` - 数据库健康检查
- `GET /api/v1/health/cache` - 缓存健康检查
- `GET /api/v1/health/full` - 完整健康检查

### WebSocket
- `WS /ws/market` - 实时行情数据推送

## 使用示例

### 用户注册
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPassword123!",
    "phone": "13800138000"
  }'
```

### 用户登录
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPassword123!"
  }'
```

### 获取行情快照
```bash
curl http://localhost:8000/api/v1/market/snapshot
```

### 添加自选股
```bash
curl -X POST http://localhost:8000/api/v1/user/favorites \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "symbol": "510050",
    "symbol_type": "ETF",
    "remark": "50ETF"
  }'
```

### WebSocket 连接
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/market');

ws.onopen = () => {
  // Subscribe to symbols
  ws.send(JSON.stringify({
    action: 'subscribe',
    symbols: ['510050', '510300']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Market update:', data);
};
```

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置
│   ├── database.py          # 数据库连接
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── market.py
│   ├── routers/             # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── market.py
│   │   ├── user.py
│   │   ├── strategy.py
│   │   └── health.py
│   ├── services/            # 业务逻辑
│   │   ├── __init__.py
│   │   ├── market_data.py   # 行情数据服务
│   │   ├── data_collector.py # 数据采集服务
│   │   └── notification.py  # 通知服务
│   ├── websocket/           # WebSocket
│   │   ├── __init__.py
│   │   └── market.py        # 行情推送
│   ├── tasks/               # Celery 任务
│   │   ├── __init__.py
│   │   └── market_data.py   # 数据采集任务
│   └── utils/               # 工具函数
├── alembic/                 # 数据库迁移
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tests/                   # 测试
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── alembic.ini
└── README.md
```

## 开发计划

### 阶段 1: 基础架构 ✅
- [x] FastAPI 项目框架
- [x] PostgreSQL + TimescaleDB 配置
- [x] Redis 缓存配置
- [x] Docker 容器化
- [x] 数据库迁移设置

### 阶段 2: 行情数据 ✅
- [x] 对接数据源 (akshare/tushare)
- [x] 数据采集服务
- [x] WebSocket 实时推送
- [x] Celery 定时任务

### 阶段 3: 用户系统 ✅
- [x] 用户注册/登录/登出
- [x] JWT Token 认证
- [x] 密码重置功能
- [x] 邮箱验证功能
- [x] 个人资料管理
- [x] 自选股完整 CRUD
- [x] 策略保存和管理
- [x] 通知系统
- [x] 登录历史记录

### 阶段 4: 高级功能 (待实现)
- [ ] 波动率计算引擎
- [ ] 策略回测
- [ ] 异动监控告警

## 许可证

MIT License
