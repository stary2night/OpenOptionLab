# OpenOptions Lab - 前后端集成说明

## 集成状态

✅ **前后端集成已完成**

## 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                        前端 (React)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  React Query │  │  Axios API  │  │   WebSocket Hook    │  │
│  │   Hooks     │  │   Service   │  │   (实时数据推送)     │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         └─────────────────┴────────────────────┘            │
│                           │                                  │
│                    HTTP / WebSocket                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                           │      后端 (FastAPI)              │
│  ┌────────────────────────┼─────────────────────────────┐   │
│  │                        ▼                              │   │
│  │  ┌─────────┐  ┌─────────────┐  ┌─────────────────┐   │   │
│  │  │  REST   │  │  WebSocket  │  │  Celery Worker  │   │   │
│  │  │   API   │  │   Server    │  │  (定时任务)      │   │   │
│  │  └────┬────┘  └──────┬──────┘  └────────┬────────┘   │   │
│  │       └──────────────┴───────────────────┘            │   │
│  │                      │                                │   │
│  │              ┌───────┴───────┐                        │   │
│  │              │   PostgreSQL  │  +  TimescaleDB        │   │
│  │              │     Redis     │  (缓存/消息队列)         │   │
│  │              └───────────────┘                        │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 前端集成

### 1. API 服务层 (`src/services/api.ts`)

封装了所有后端 API 调用：

```typescript
// 行情数据 API
getMarketOverview()      // 市场概览统计
getSymbols()             // 品种列表
getSymbolDetail()        // 品种详情
getIvRank()              // IV 排名
getPremiumRank()         // 溢价排名
getPriceChangeRank()     // 价格变动排名
getTermStructure()       // 期限结构

// 用户认证 API
login() / register() / logout()
getCurrentUser()

// 用户数据 API
getWatchlist() / addToWatchlist() / removeFromWatchlist()
getStrategies() / saveStrategy() / deleteStrategy()
```

### 2. React Query Hooks (`src/hooks/`)

提供了数据获取和缓存管理：

```typescript
// 行情数据 Hooks
useMarketOverview()      // 自动刷新: 30秒
useSymbols()             // 支持筛选、分页
useIvRank()              // 自动刷新: 60秒
usePremiumRank()
usePriceChangeRank()     // 自动刷新: 30秒
useTermStructure()
useUnusualFlows()        // 自动刷新: 15秒

// 用户认证 Hooks
useCurrentUser()
useLogin() / useRegister() / useLogout()

// 用户数据 Hooks
useWatchlist()
useStrategies()
```

### 3. WebSocket Hook (`src/hooks/useWebSocket.ts`)

实时数据推送连接管理：

```typescript
const {
  isConnected,
  lastMessage,
  subscribeSymbol,
  unsubscribeSymbol,
} = useWebSocket({
  onMarketUpdate: (data) => console.log('价格更新:', data),
  onIvUpdate: (data) => console.log('IV 更新:', data),
});
```

### 4. 环境变量配置 (`.env`)

```bash
# API 基础地址
VITE_API_BASE_URL=http://localhost:8000

# 功能开关
VITE_ENABLE_WEBSOCKET=true
```

## 后端 API 列表

### 行情数据端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/market/overview` | 市场概览统计 |
| GET | `/api/v1/market/symbols` | 品种列表（支持筛选、分页） |
| GET | `/api/v1/market/symbols/{symbol}` | 单个品种详情 |
| GET | `/api/v1/market/iv-rank` | IV 排名 |
| GET | `/api/v1/market/premium-rank` | 溢价排名 |
| GET | `/api/v1/market/price-change` | 价格变动排名 |
| GET | `/api/v1/market/term-structure` | 期限结构数据 |
| WS | `/ws/market` | WebSocket 实时数据 |

### 认证端点

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录 |
| POST | `/api/v1/auth/logout` | 用户登出 |
| POST | `/api/v1/auth/refresh` | 刷新 Token |
| GET | `/api/v1/auth/me` | 获取当前用户 |
| POST | `/api/v1/auth/password-reset` | 密码重置 |

### 用户数据端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/user/watchlist` | 自选股列表 |
| POST | `/api/v1/user/watchlist` | 添加自选股 |
| DELETE | `/api/v1/user/watchlist/{symbol}` | 删除自选股 |
| GET | `/api/v1/user/strategies` | 策略列表 |
| POST | `/api/v1/user/strategies` | 保存策略 |
| DELETE | `/api/v1/user/strategies/{id}` | 删除策略 |

## 启动步骤

### 1. 启动后端服务

```bash
cd /mnt/okcomputer/output/backend

# 使用 Docker Compose 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f api
```

服务将启动：
- API 服务: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### 2. 启动前端开发服务器

```bash
cd /mnt/okcomputer/output/app

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将运行在: http://localhost:5173

### 3. 验证集成

1. 访问 http://localhost:8000/docs 查看后端 API 文档
2. 访问 http://localhost:5173 查看前端页面
3. 打开浏览器开发者工具，查看 Network 面板确认 API 调用

## 数据流

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   数据源     │────▶│  后端 API   │────▶│  前端展示   │
│  (akshare)  │     │  (FastAPI)  │     │  (React)   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  WebSocket  │
                    │  实时推送   │
                    └─────────────┘
```

## 特性

- ✅ 自动数据刷新（配置不同刷新间隔）
- ✅ 数据缓存和去重请求
- ✅ 错误重试机制
- ✅ Token 自动刷新
- ✅ WebSocket 自动重连
- ✅ Loading 状态管理
- ✅ 响应式数据更新

## 故障排查

### 前端无法连接后端

1. 检查后端是否运行: `curl http://localhost:8000/health/`
2. 检查 CORS 配置是否正确
3. 检查 `.env` 中的 `VITE_API_BASE_URL` 是否正确

### WebSocket 连接失败

1. 检查后端 WebSocket 端点: `ws://localhost:8000/ws/market`
2. 检查防火墙设置
3. 查看浏览器控制台错误信息

### 认证失败

1. 检查 Token 是否过期
2. 检查 `localStorage` 中的 `access_token`
3. 尝试重新登录
