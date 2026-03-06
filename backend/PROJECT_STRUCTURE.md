# OpenOptions Lab API - 项目结构

## 目录结构

```
backend/
├── alembic/                    # 数据库迁移
│   ├── env.py                  # Alembic 环境配置
│   ├── script.py.mako          # 迁移脚本模板
│   └── versions/               # 迁移版本
│       ├── 001_initial.py      # 初始迁移
│       └── 002_add_user_features.py  # 用户功能迁移
│
├── app/                        # 主应用目录
│   ├── __init__.py
│   ├── main.py                 # FastAPI 入口
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接管理
│   ├── dependencies.py         # FastAPI 依赖
│   │
│   ├── models/                 # 数据模型
│   │   ├── __init__.py         # 模型导出
│   │   ├── user.py             # 用户相关模型
│   │   └── market.py           # 行情数据模型
│   │
│   ├── routers/                # API 路由
│   │   ├── __init__.py         # 路由聚合
│   │   ├── auth.py             # 认证路由
│   │   ├── user.py             # 用户路由
│   │   ├── market.py           # 行情数据路由
│   │   ├── strategy.py         # 策略分析路由
│   │   ├── health.py           # 健康检查路由
│   │   └── websocket.py        # WebSocket 路由
│   │
│   ├── schemas/                # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── auth.py             # 认证相关 Schema
│   │   ├── user.py             # 用户相关 Schema
│   │   ├── market.py           # 行情数据 Schema
│   │   └── strategy.py         # 策略相关 Schema
│   │
│   ├── services/               # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── market_data.py      # 行情数据服务
│   │   ├── data_collector.py   # 数据采集服务
│   │   └── notification.py     # 通知服务
│   │
│   ├── tasks/                  # Celery 任务
│   │   ├── __init__.py
│   │   └── market_data.py      # 数据采集任务
│   │
│   ├── websocket/              # WebSocket 处理
│   │   ├── __init__.py
│   │   └── market.py           # 行情推送
│   │
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       ├── security.py         # 安全工具
│       └── cache.py            # 缓存工具
│
├── scripts/                    # 脚本工具
│   └── start.sh                # 快速启动脚本
│
├── tests/                      # 测试
│   ├── __init__.py
│   ├── conftest.py             # pytest 配置
│   └── test_user_system.py     # 用户系统测试
│
├── alembic.ini                 # Alembic 配置
├── docker-compose.yml          # Docker Compose 配置
├── Dockerfile                  # Docker 构建文件
├── requirements.txt            # Python 依赖
├── .env.example                # 环境变量示例
├── README.md                   # 项目说明
└── PROJECT_STRUCTURE.md        # 本文件
```

## 核心模块说明

### 1. 认证系统 (auth.py)

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/auth/register` | POST | 用户注册 |
| `/api/v1/auth/login` | POST | 用户登录 |
| `/api/v1/auth/logout` | POST | 用户登出 |
| `/api/v1/auth/refresh` | POST | 刷新 Token |
| `/api/v1/auth/me` | GET | 获取当前用户 |
| `/api/v1/auth/password-reset/request` | POST | 请求密码重置 |
| `/api/v1/auth/password-reset/confirm` | POST | 确认密码重置 |
| `/api/v1/auth/email/verify-request` | POST | 请求邮箱验证 |
| `/api/v1/auth/email/verify/{token}` | POST | 验证邮箱 |
| `/api/v1/auth/password` | PUT | 修改密码 |
| `/api/v1/auth/profile` | PUT | 更新个人资料 |
| `/api/v1/auth/avatar` | POST | 上传头像 |

### 2. 用户系统 (user.py)

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/user/favorites` | GET | 获取自选股 |
| `/api/v1/user/favorites` | POST | 添加自选股 |
| `/api/v1/user/favorites/{symbol}` | DELETE | 删除自选股 |
| `/api/v1/user/favorites/{symbol}/alert` | PUT | 设置价格提醒 |
| `/api/v1/user/strategies` | GET | 获取策略列表 |
| `/api/v1/user/strategies` | POST | 创建策略 |
| `/api/v1/user/strategies/{id}` | GET | 获取策略详情 |
| `/api/v1/user/strategies/{id}` | PUT | 更新策略 |
| `/api/v1/user/strategies/{id}` | DELETE | 删除策略 |
| `/api/v1/user/strategies/{id}/toggle` | POST | 切换策略状态 |
| `/api/v1/user/notifications` | GET | 获取通知 |
| `/api/v1/user/notifications/{id}/read` | PUT | 标记已读 |
| `/api/v1/user/notifications/read-all` | PUT | 标记全部已读 |
| `/api/v1/user/notifications/{id}` | DELETE | 删除通知 |
| `/api/v1/user/notifications/unread-count` | GET | 未读数量 |

### 3. 行情数据 (market.py)

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/market/snapshot` | GET | 市场快照 |
| `/api/v1/market/snapshot/{symbol}` | GET | 品种详情 |
| `/api/v1/market/{symbol}/history` | GET | 历史数据 |
| `/api/v1/market/top/iv-rise` | GET | 隐波上升排行 |
| `/api/v1/market/top/iv-fall` | GET | 隐波下降排行 |
| `/api/v1/market/top/premium-high` | GET | 溢价最高排行 |
| `/api/v1/market/top/premium-low` | GET | 溢价最低排行 |
| `/api/v1/market/unusual-flows` | GET | 异动监控 |

### 4. 策略分析 (strategy.py)

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/strategy/analyze` | POST | 分析策略 |
| `/api/v1/strategy/templates` | GET | 获取策略模板 |

### 5. WebSocket 实时推送

| 端点 | 描述 |
|------|------|
| `/ws/market` | 行情数据实时推送 |

## 数据模型

### 用户相关模型

```
User
├── id, username, email, password_hash
├── phone, avatar, bio
├── is_active, is_vip, is_admin
├── email_verified
├── created_at, updated_at, last_login
│
├── UserFavorite (1:N)
│   ├── symbol, symbol_type, remark
│   ├── notes, alert_enabled, alert_settings
│   └── created_at
│
├── UserStrategy (1:N)
│   ├── name, description, strategy_type
│   ├── legs (JSONB), parameters (JSONB), tags (JSONB)
│   ├── underlying_symbol, underlying_price
│   ├── probability_of_profit
│   ├── initial_capital, current_pnl, pnl_percent
│   ├── is_active, closed_at
│   └── created_at, updated_at
│
├── UserNotification (1:N)
│   ├── type, title, message, data (JSONB)
│   ├── is_read, read_at
│   └── created_at
│
├── PasswordReset (1:N)
│   ├── token, expires_at, used
│   └── created_at
│
├── EmailVerification (1:N)
│   ├── token, expires_at, used
│   └── created_at
│
└── LoginHistory (1:N)
    ├── ip_address, user_agent
    ├── login_method, success, failure_reason
    └── created_at
```

### 行情数据模型

```
MarketSnapshot
├── symbol, name, market_type
├── price, change, change_percent
├── volume, open_interest
├── iv, iv_percentile, iv_rank
├── hv, hv_percentile
├── put_call_ratio
└── timestamp

OptionContract
├── symbol, underlying_symbol
├── option_type, strike, expiry_date
└── created_at

MarketQuote (TimescaleDB  hypertable)
├── symbol, price, volume, open_interest
├── bid, ask, bid_volume, ask_volume
├── iv, delta, gamma, theta, vega, rho
└── timestamp

OptionQuote (TimescaleDB hypertable)
├── symbol, underlying_price
├── strike, expiry_date, days_to_expiry
├── price, volume, open_interest
├── iv, delta, gamma, theta, vega, rho
├── intrinsic_value, time_value
├── break_even, max_profit, max_loss
└── timestamp

UnusualFlow (TimescaleDB hypertable)
├── symbol, option_symbol
├── option_type, strike, expiry_date
├── volume, open_interest, volume_oi_ratio
├── premium, sentiment
└── timestamp
```

## 开发阶段

### ✅ 阶段 1: 基础架构
- FastAPI 项目框架
- PostgreSQL + TimescaleDB 配置
- Redis 缓存配置
- Docker 容器化
- 数据库迁移设置

### ✅ 阶段 2: 行情数据服务
- 对接 akshare 数据源
- 数据采集服务
- WebSocket 实时推送
- Celery 定时任务

### ✅ 阶段 3: 用户系统
- 用户注册/登录/登出
- JWT Token 认证
- 密码重置功能
- 邮箱验证功能
- 个人资料管理
- 自选股完整 CRUD
- 策略保存和管理
- 通知系统
- 登录历史记录

### 🔄 阶段 4: 高级功能 (待实现)
- 波动率计算引擎
- 策略回测
- 异动监控告警
- 期权定价模型
- 风险分析工具

## 快速开始

```bash
# 1. 进入后端目录
cd backend

# 2. 复制环境变量
cp .env.example .env

# 3. 启动服务 (Docker)
./scripts/start.sh

# 4. 访问 API 文档
open http://localhost:8000/docs

# 5. 运行测试
cd tests && python test_user_system.py
```

## 技术栈

- **框架**: FastAPI (Python 3.11+)
- **数据库**: PostgreSQL 15 + TimescaleDB 2.11
- **缓存**: Redis 7
- **任务队列**: Celery + Redis
- **容器化**: Docker + Docker Compose
- **数据接口**: akshare (中国金融数据)
