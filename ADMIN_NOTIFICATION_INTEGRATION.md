# 管理员后台 WebSocket 通知集成完成

## 概述

管理员后台的 WebSocket 通知系统已经完成对接，实现了以下功能：

- ✅ 后端管理员通知 API (`/api/v1/admin/notifications`)
- ✅ 后端 WebSocket 管理员端点 (`/api/v1/ws/admin`)
- ✅ 前端 WebSocket Context 处理管理员通知
- ✅ 前端通知抽屉组件展示通知列表
- ✅ 前端通知徽章组件实时显示未读数量
- ✅ 实时通知弹窗 (不同严重程度有不同样式)

## 架构说明

### 后端组件

1. **AdminNotification 模型** (`backend/app/models/notification.py`)
   - 存储管理员通知数据
   - 支持不同的严重程度 (info/warning/error/critical)
   - 支持关联到其他对象 (related_type, related_id)

2. **AdminNotificationService** (`backend/app/utils/admin_notification_service.py`)
   - 创建管理员通知
   - 通过 WebSocket 发送实时通知
   - 提供多种便捷方法创建特定类型通知

3. **管理员通知 API** (`backend/app/admin/admin_notifications.py`)
   - `GET /api/v1/admin/notifications` - 获取通知列表
   - `GET /api/v1/admin/notifications/stats` - 获取通知统计
   - `PATCH /api/v1/admin/notifications/{id}` - 标记通知为已读
   - `POST /api/v1/admin/notifications/mark-all-read` - 全部标记已读
   - `DELETE /api/v1/admin/notifications/{id}` - 删除通知
   - `POST /api/v1/admin/notifications/clear-all` - 清空所有通知
   - `POST /api/v1/admin/notifications/test-notification` - 创建测试通知

4. **WebSocket 管理员端点** (`backend/app/api/websocket.py`)
   - `ws://localhost:8000/api/v1/ws/admin?token=<access_token>`
   - 需要管理员权限
   - 接收消息类型: `admin_notification`, `transcode_progress`, 等

### 前端组件

1. **adminNotificationService** (`admin-frontend/src/services/adminNotificationService.ts`)
   - 封装所有管理员通知相关API调用

2. **WebSocketContext** (`admin-frontend/src/contexts/WebSocketContext.tsx`)
   - 管理 WebSocket 连接
   - 处理 `admin_notification` 类型消息
   - 根据严重程度显示不同样式的通知弹窗
   - 自动刷新通知列表

3. **NotificationDrawer** (`admin-frontend/src/components/NotificationDrawer/`)
   - 显示通知列表
   - 支持筛选 (未读/全部)
   - 支持标记已读、删除、清空操作
   - 点击通知可跳转到相关页面

4. **NotificationBadge** (`admin-frontend/src/components/NotificationBadge/`)
   - 显示未读通知数量
   - 集成在 AdminLayout Header 中
   - 点击打开通知抽屉
   - 实时更新未读计数

## 通知流程

```
1. 后端触发事件 (如系统错误、新用户注册等)
   ↓
2. AdminNotificationService.create_admin_notification()
   ↓
3. 保存通知到数据库
   ↓
4. 通过 WebSocketManager.send_admin_message() 发送实时通知
   ↓
5. 前端 WebSocket 接收消息 (type: 'admin_notification')
   ↓
6. WebSocketContext 处理通知
   - 更新 adminUnreadCount
   - 刷新通知列表查询
   - 显示通知弹窗 (根据严重程度)
   ↓
7. NotificationBadge 显示未读数量
   ↓
8. 用户点击查看详情 (NotificationDrawer)
```

## 通知类型

后端预定义的通知类型 (`NotificationType`):

- `NEW_USER_REGISTRATION` - 新用户注册
- `PENDING_COMMENT_REVIEW` - 待审核评论
- `SYSTEM_ERROR_ALERT` - 系统错误告警
- `STORAGE_WARNING` - 存储空间警告
- `UPLOAD_FAILED` - 上传失败
- `VIDEO_PROCESSING_COMPLETE` - 视频处理完成
- `SUSPICIOUS_ACTIVITY` - 可疑活动

## 严重程度

通知严重程度及其展示样式:

| 严重程度 | 颜色 | 图标 | 自动关闭 |
|---------|------|------|---------|
| `info` | 蓝色 | BellOutlined | 5秒 |
| `warning` | 橙色 | WarningOutlined | 5秒 |
| `error` | 红色 | CloseCircleOutlined | 不关闭 |
| `critical` | 红色 | ExclamationCircleOutlined | 不关闭 |

## 测试方法

### 1. 后端测试

运行测试脚本创建各种类型的通知:

```bash
cd backend
source venv/bin/activate
python test_admin_notifications.py
```

### 2. 前端测试

1. 启动后端服务:
   ```bash
   cd backend
   make backend-run
   ```

2. 启动管理前端:
   ```bash
   cd admin-frontend
   pnpm run dev
   ```

3. 登录管理后台并观察:
   - Header 右上角的通知图标 (应该显示未读数量)
   - WebSocket 连接状态 (控制台日志)
   - 点击通知图标打开通知抽屉

4. 通过 API 创建测试通知:
   ```bash
   # 需要先获取管理员 token
   curl -X POST http://localhost:8000/api/v1/admin/notifications/test-notification \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

## 现有功能确认

✅ 通知功能已经存在并完整实现，包括:

1. **NotificationBadge 组件** - 已集成到 AdminLayout
2. **NotificationDrawer 组件** - 完整的通知列表和管理
3. **adminNotificationService** - API 服务层
4. **后端通知 API** - 已在 main.py 注册
5. **WebSocket 支持** - 已有 WebSocket Context

## 最新改进

本次改进主要是**完善 WebSocket 集成**:

1. **WebSocketContext 增强**:
   - 添加 `handleAdminNotification` 函数处理管理员通知
   - 添加 `adminUnreadCount` 状态
   - 在 `onMessage` 回调中处理 `admin_notification` 类型
   - 自动刷新通知列表查询

2. **NotificationBadge 增强**:
   - 集成 WebSocketContext 获取实时连接状态
   - 统一查询 key 为 `adminNotificationStats`

3. **测试脚本**:
   - 创建 `test_admin_notifications.py` 用于后端测试

## 使用示例

### 后端触发通知

```python
from app.utils.admin_notification_service import AdminNotificationService

# 系统错误告警
await AdminNotificationService.notify_system_error(
    db=db,
    error_type="DatabaseError",
    error_message="连接失败",
    error_id=1,
)

# 存储空间警告
await AdminNotificationService.notify_storage_warning(
    db=db,
    usage_percent=85.5,
    used_gb=85.5,
    total_gb=100.0,
)

# 新用户注册
await AdminNotificationService.notify_new_user_registration(
    db=db,
    user_id=user.id,
    username=user.username,
    email=user.email,
)

# 自定义通知
await AdminNotificationService.create_admin_notification(
    db=db,
    admin_user_id=None,  # None = 广播给所有管理员
    type="custom_notification",
    title="自定义通知",
    content="通知内容",
    severity="warning",
    link="/some-page",
    send_websocket=True,
)
```

### 前端使用通知

```typescript
import { useWebSocketContext } from '@/contexts/WebSocketContext'

function MyComponent() {
  const { isConnected, adminUnreadCount } = useWebSocketContext()

  return (
    <div>
      WebSocket: {isConnected ? '已连接' : '未连接'}
      未读通知: {adminUnreadCount}
    </div>
  )
}
```

## 注意事项

1. **WebSocket 连接需要认证** - URL 必须包含 `token` 参数
2. **自动重连** - WebSocket 断开后会自动尝试重连
3. **心跳机制** - 每 30 秒发送 ping 保持连接
4. **查询一致性** - 使用统一的 queryKey 确保缓存一致性
5. **严重程度** - error/critical 级别通知不会自动关闭，需要手动处理

## 相关文件

### 后端
- `backend/app/models/notification.py` - 通知模型
- `backend/app/admin/admin_notifications.py` - 通知 API
- `backend/app/utils/admin_notification_service.py` - 通知服务
- `backend/app/utils/websocket_manager.py` - WebSocket 管理器
- `backend/app/api/websocket.py` - WebSocket 端点

### 前端
- `admin-frontend/src/contexts/WebSocketContext.tsx` - WebSocket Context
- `admin-frontend/src/components/NotificationBadge/` - 通知徽章
- `admin-frontend/src/components/NotificationDrawer/` - 通知抽屉
- `admin-frontend/src/services/adminNotificationService.ts` - 通知服务
- `admin-frontend/src/hooks/useWebSocket.ts` - WebSocket Hook

## 总结

管理员后台通知系统已经完整实现并集成 WebSocket 实时推送功能。系统可以:

1. ✅ 接收各类系统事件并创建通知
2. ✅ 通过 WebSocket 实时推送给管理员
3. ✅ 在前端显示不同样式的通知弹窗
4. ✅ 提供完整的通知管理界面
5. ✅ 支持筛选、标记已读、删除等操作
6. ✅ 实时更新未读计数

系统已经可以投入使用，无需额外开发。
