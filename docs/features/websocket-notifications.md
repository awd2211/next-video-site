# WebSocket实时通知系统

## 概述

VideoSite平台集成了基于WebSocket的实时通知系统,用于向管理后台推送转码进度、系统消息等实时信息。该系统采用全双工通信,支持自动重连、心跳保活、消息分发等企业级特性。

## 架构设计

```
┌─────────────────┐         WebSocket         ┌─────────────────┐
│  Admin Frontend │ ◄─────────────────────── │  FastAPI Server │
│                 │                           │                 │
│  - useWebSocket │   wss://api/v1/ws/admin  │  - ConnectionMgr│
│  - Context      │                           │  - Notification │
│  - Badge UI     │                           │  - Celery Task  │
└─────────────────┘                           └─────────────────┘
        │                                              │
        │ Auto Reconnect                               │ Broadcast
        │ Heartbeat                                    │
        │                                              ▼
        └──────────────────────────────────► Redis Pub/Sub
```

## 核心组件

### 1. 后端 (FastAPI)

#### 1.1 ConnectionManager (`backend/app/utils/websocket_manager.py`)

WebSocket连接管理器,负责维护所有活跃连接。

**主要功能**:
- 用户连接管理 (按user_id分组)
- 管理员连接管理 (独立连接池)
- 消息广播 (broadcast)
- 点对点消息 (personal message)
- 管理员群发 (admin message)
- 连接统计

**使用示例**:
```python
from app.utils.websocket_manager import manager

# 建立连接
await manager.connect(websocket, user_id=123)
await manager.connect(websocket, is_admin=True)

# 发送消息
await manager.send_personal_message({"type": "hello"}, user_id=123)
await manager.send_admin_message({"type": "system_alert"})
await manager.broadcast({"type": "announcement"})

# 断开连接
manager.disconnect(websocket, user_id=123)

# 获取统计
stats = manager.get_connection_count()
# {
#   "total_users": 50,
#   "total_user_connections": 65,
#   "total_admin_connections": 5,
#   "total_connections": 70
# }
```

#### 1.2 NotificationService (`backend/app/utils/websocket_manager.py`)

通知服务,提供高级API用于发送各类通知。

**通知类型**:

| 方法 | 说明 | 参数 |
|------|------|------|
| `notify_transcode_progress` | 转码进度更新 | video_id, status, progress, message |
| `notify_transcode_complete` | 转码完成 | video_id, title, format_type, file_size |
| `notify_transcode_failed` | 转码失败 | video_id, title, error |
| `notify_system_message` | 系统消息 | message, level, target |

**使用示例**:
```python
from app.utils.websocket_manager import notification_service
import asyncio

# 在Celery任务中使用
asyncio.run(notification_service.notify_transcode_progress(
    video_id=123,
    status='processing',
    progress=45,
    message="已完成720p转码"
))

asyncio.run(notification_service.notify_transcode_complete(
    video_id=123,
    title="示例视频",
    format_type='av1',
    file_size=1024000000
))

asyncio.run(notification_service.notify_system_message(
    message="系统将于10分钟后维护",
    level="warning",
    target="admin"
))
```

#### 1.3 WebSocket端点 (`backend/app/api/websocket.py`)

FastAPI WebSocket路由。

**端点列表**:

| 端点 | 说明 | 权限 |
|------|------|------|
| `GET /api/v1/ws?token=<jwt>` | 用户WebSocket连接 | 登录用户 |
| `GET /api/v1/ws/admin?token=<jwt>` | 管理员WebSocket连接 | 管理员 |
| `GET /api/v1/ws/stats` | 连接统计 | 公开 |

**连接示例**:
```javascript
// 前端连接
const token = localStorage.getItem('token')
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/admin?token=${token}`)

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  console.log('收到消息:', data)
}

// 心跳
setInterval(() => {
  ws.send('ping')
}, 30000)
```

### 2. 前端 (React)

#### 2.1 useWebSocket Hook (`admin-frontend/src/hooks/useWebSocket.ts`)

自定义React Hook,封装WebSocket连接逻辑。

**功能特性**:
- ✅ 自动连接 (autoConnect)
- ✅ 自动重连 (autoReconnect)
- ✅ 心跳保活 (heartbeat)
- ✅ 消息分发 (onMessage, onTranscodeProgress, etc.)
- ✅ 错误处理 (onError)
- ✅ 连接状态管理 (isConnected)

**使用示例**:
```typescript
import { useWebSocket } from '@/hooks/useWebSocket'

function MyComponent() {
  const { isConnected, lastMessage, sendMessage } = useWebSocket(true, {
    autoConnect: true,
    autoReconnect: true,
    reconnectInterval: 3000,
    maxReconnectAttempts: 5,
    heartbeatInterval: 30000,

    onTranscodeProgress: (message) => {
      console.log(`视频${message.video_id}转码进度: ${message.progress}%`)
    },

    onTranscodeComplete: (message) => {
      notification.success({ message: `转码完成: ${message.title}` })
    },

    onConnect: () => {
      console.log('WebSocket已连接')
    },
  })

  return (
    <div>
      <span>连接状态: {isConnected ? '已连接' : '已断开'}</span>
      <button onClick={() => sendMessage('get_stats')}>获取统计</button>
    </div>
  )
}
```

#### 2.2 WebSocketContext (`admin-frontend/src/contexts/WebSocketContext.tsx`)

全局WebSocket上下文,提供应用级别的通知管理。

**功能特性**:
- ✅ 全局连接管理
- ✅ 未读消息计数
- ✅ 转码进度跟踪 (Map<video_id, progress>)
- ✅ Ant Design通知集成

**使用示例**:
```typescript
// 在App.tsx中包裹根组件
import { WebSocketProvider } from '@/contexts/WebSocketContext'

function App() {
  return (
    <WebSocketProvider>
      <YourApp />
    </WebSocketProvider>
  )
}

// 在子组件中使用
import { useWebSocketContext } from '@/contexts/WebSocketContext'

function Header() {
  const { isConnected, unreadCount, markAsRead } = useWebSocketContext()

  return (
    <Badge count={unreadCount}>
      <BellOutlined onClick={markAsRead} />
    </Badge>
  )
}
```

#### 2.3 NotificationBadge (`admin-frontend/src/components/NotificationBadge/index.tsx`)

通知徽章组件,显示连接状态和未读消息数。

**使用示例**:
```tsx
import NotificationBadge from '@/components/NotificationBadge'

function Header() {
  return (
    <div className="header">
      <Logo />
      <NotificationBadge />
      <UserMenu />
    </div>
  )
}
```

#### 2.4 TranscodeStatus集成

TranscodeStatus组件已集成WebSocket实时更新。

**优势**:
- WebSocket连接时,优先使用实时推送
- 自动降级为轮询 (WebSocket断开时)
- 轮询频率智能调整 (连接时降低3倍)

## 消息格式

### 转码进度 (transcode_progress)

```json
{
  "type": "transcode_progress",
  "video_id": 123,
  "status": "processing",
  "progress": 45,
  "message": "已完成720p转码 (2/3)",
  "timestamp": "2025-10-10T10:30:00Z"
}
```

### 转码完成 (transcode_complete)

```json
{
  "type": "transcode_complete",
  "video_id": 123,
  "title": "示例视频",
  "format_type": "av1",
  "file_size": 1024000000,
  "timestamp": "2025-10-10T10:35:00Z"
}
```

### 转码失败 (transcode_failed)

```json
{
  "type": "transcode_failed",
  "video_id": 123,
  "title": "示例视频",
  "error": "FFmpeg process exited with code 1",
  "timestamp": "2025-10-10T10:32:00Z"
}
```

### 系统消息 (system_message)

```json
{
  "type": "system_message",
  "message": "系统将于10分钟后维护",
  "level": "warning",
  "timestamp": "2025-10-10T10:20:00Z"
}
```

### 连接成功 (connected)

```json
{
  "type": "connected",
  "message": "管理员 admin 已连接",
  "admin_id": 1,
  "connection_stats": {
    "total_users": 50,
    "total_user_connections": 65,
    "total_admin_connections": 5,
    "total_connections": 70
  }
}
```

## 安全机制

### 1. JWT认证

WebSocket连接必须携带有效的JWT token:
```
ws://localhost:8000/api/v1/ws/admin?token=<access_token>
```

后端验证:
- 解析token payload
- 检查用户是否存在
- 管理员端点检查 `is_admin` 字段

### 2. 权限隔离

- **用户端点** (`/ws`): 只接收与该用户相关的消息
- **管理员端点** (`/ws/admin`): 接收所有管理员消息

### 3. CORS配置

已在FastAPI中配置CORS:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 性能优化

### 1. 连接池管理

- 按user_id分组存储连接 (支持多设备登录)
- 管理员连接使用Set (去重)
- 自动清理断开的连接

### 2. 心跳机制

- 客户端每30秒发送 `ping`
- 服务端返回 `pong`
- 检测并清理僵尸连接

### 3. 自动重连

- 默认5次重连机会
- 重连间隔3秒
- 指数退避 (可配置)

### 4. 混合模式 (WebSocket + 轮询)

- WebSocket连接时,降低轮询频率 (3倍)
- WebSocket断开时,自动恢复轮询
- 保证消息不丢失

## 部署配置

### 1. Nginx反向代理

```nginx
# WebSocket支持
location /api/v1/ws {
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # 超时配置
    proxy_read_timeout 600s;
    proxy_send_timeout 600s;
}
```

### 2. 环境变量

```bash
# .env
REACT_APP_WS_URL=ws://localhost:8000  # WebSocket服务器地址
```

### 3. Docker Compose

```yaml
services:
  backend:
    ports:
      - "8000:8000"
    environment:
      - BACKEND_CORS_ORIGINS=http://localhost:3001,http://admin.example.com
```

## 监控和调试

### 1. 连接统计API

```bash
curl http://localhost:8000/api/v1/ws/stats
```

响应:
```json
{
  "total_users": 50,
  "total_user_connections": 65,
  "total_admin_connections": 5,
  "total_connections": 70
}
```

### 2. 浏览器调试

```javascript
// 在浏览器控制台
// 1. 查看WebSocket状态
console.log(ws.readyState)
// 0: CONNECTING
// 1: OPEN
// 2: CLOSING
// 3: CLOSED

// 2. 监听所有消息
ws.addEventListener('message', (event) => {
  console.log('WebSocket消息:', JSON.parse(event.data))
})

// 3. 手动发送心跳
ws.send('ping')
```

### 3. 后端日志

```python
import logging
logger = logging.getLogger(__name__)

# 日志输出示例
# ✅ Admin WebSocket连接已建立, 当前管理员连接数: 3
# 📡 转码进度通知已发送: video_id=123, status=processing, progress=45%
# ✅ 转码完成通知已发送: video_id=123, format=av1
# ❌ Admin WebSocket连接已断开, 剩余管理员连接数: 2
```

## 故障排查

### 问题1: 连接失败 (1006错误)

**原因**: Token无效或过期

**解决方案**:
```typescript
// 刷新token
const newToken = await refreshAccessToken()
localStorage.setItem('token', newToken)

// 重新连接
connect()
```

### 问题2: 连接断开频繁

**原因**:
- 网络不稳定
- 服务器负载高
- Nginx超时配置过短

**解决方案**:
```nginx
# 增加超时时间
proxy_read_timeout 3600s;
proxy_send_timeout 3600s;
```

### 问题3: 消息丢失

**原因**:
- WebSocket断开时未保存消息
- 重连期间消息未缓存

**解决方案**:
```typescript
// 使用混合模式 (WebSocket + 轮询)
const { isConnected } = useWebSocket(true, {
  autoReconnect: true,
})

useEffect(() => {
  if (!isConnected) {
    // WebSocket断开时,回退到轮询
    const timer = setInterval(fetchStatus, 5000)
    return () => clearInterval(timer)
  }
}, [isConnected])
```

## 扩展建议

### 1. Redis Pub/Sub

对于多服务器部署,使用Redis Pub/Sub广播消息:

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379)

# 发布消息
redis_client.publish('notifications', json.dumps({
    'type': 'transcode_progress',
    'video_id': 123,
    'progress': 45
}))

# 订阅消息
pubsub = redis_client.pubsub()
pubsub.subscribe('notifications')

for message in pubsub.listen():
    if message['type'] == 'message':
        data = json.loads(message['data'])
        await manager.send_admin_message(data)
```

### 2. 消息持久化

将通知保存到数据库:

```python
from app.models.notification import Notification

# 发送通知前保存
notification = Notification(
    user_id=user_id,
    type='transcode_complete',
    content=json.dumps(message),
    is_read=False
)
db.add(notification)
db.commit()

# 通过WebSocket发送
await manager.send_personal_message(message, user_id)
```

### 3. 消息队列

使用消息队列解耦:

```python
# Celery任务
@celery.task
def send_notification(message_type, data):
    asyncio.run(notification_service.notify_system_message(
        message=data['message'],
        level=data['level']
    ))
```

## 总结

VideoSite的WebSocket实时通知系统提供了:

✅ **高可用性**: 自动重连、心跳保活
✅ **低延迟**: 毫秒级消息推送
✅ **易集成**: React Hook + Context封装
✅ **安全性**: JWT认证 + 权限隔离
✅ **可扩展**: 支持Redis Pub/Sub、消息持久化
✅ **混合模式**: WebSocket + 轮询fallback

该系统已成功集成到视频转码流程,为管理员提供实时的转码进度监控。
