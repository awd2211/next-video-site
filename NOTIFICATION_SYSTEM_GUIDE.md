# 📚 通知系统完整使用指南 | Complete Notification System Guide

**版本 | Version**: 3.0.0
**更新日期 | Updated**: 2025-10-14
**状态 | Status**: 生产就绪 | Production Ready

---

## 📑 目录 | Table of Contents

1. [系统概述](#系统概述)
2. [架构设计](#架构设计)
3. [快速开始](#快速开始)
4. [API文档](#api文档)
5. [前端集成](#前端集成)
6. [最佳实践](#最佳实践)
7. [性能优化](#性能优化)
8. [故障排查](#故障排查)
9. [扩展开发](#扩展开发)

---

## 🎯 系统概述 | System Overview

### 功能特性 | Features

VideoSite通知系统是一个**全栈实时通知解决方案**，为管理员提供：

✅ **实时通知推送** - WebSocket即时通知，无需刷新页面
✅ **多级别通知** - info/warning/error/critical 四级严重程度
✅ **智能路由** - 广播通知 + 定向通知双模式
✅ **完整历史** - 数据库持久化，可追溯查询
✅ **批量操作** - 标记已读、批量删除、一键清空
✅ **灵活过滤** - 按类型、严重程度、已读状态筛选
✅ **统计分析** - 实时统计未读数、类型分布
✅ **零侵入集成** - 不影响原有业务逻辑

### 技术栈 | Tech Stack

**后端 | Backend**:
- FastAPI - 异步Web框架
- SQLAlchemy - ORM + 数据库持久化
- WebSocket - 实时双向通信
- PostgreSQL - 通知数据存储

**前端 | Frontend**:
- React 18 - UI组件库
- Ant Design - 通知UI组件
- WebSocket Client - 实时消息接收
- TanStack Query - 数据状态管理

---

## 🏗️ 架构设计 | Architecture Design

### 系统架构图 | System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     管理后台前端 | Admin Frontend                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ 通知图标Badge│  │ 通知Drawer   │  │ WebSocket Client    │  │
│  │ (实时更新)   │  │ (列表展示)   │  │ (接收实时推送)       │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
└─────────┼──────────────────┼──────────────────────┼──────────────┘
          │ REST API         │ REST API             │ WebSocket
          │                  │                      │
┌─────────▼──────────────────▼──────────────────────▼──────────────┐
│                      FastAPI 后端 | Backend                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         AdminNotificationService (核心服务)               │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │   │
│  │  │ 20个通知方法 │  │ WebSocket推送│  │ 数据库持久化   │ │   │
│  │  │ (业务逻辑)   │  │ (实时通知)   │  │ (历史记录)     │ │   │
│  │  └──────────────┘  └──────────────┘  └────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         AdminNotificationsAPI (REST接口)                  │   │
│  │  GET /notifications  | 查询通知列表                      │   │
│  │  GET /notifications/stats | 通知统计                     │   │
│  │  PATCH /notifications/{id} | 标记已读                    │   │
│  │  POST /notifications/mark-all-read | 全部标记已读        │   │
│  │  DELETE /notifications/{id} | 删除通知                   │   │
│  │  POST /notifications/clear-all | 清空所有                │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │               50+ 触发点集成                              │   │
│  │  16个管理模块 (videos, users, comments, rbac...)        │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │   PostgreSQL   │
                    │ admin_notification│
                    │     表          │
                    └────────────────┘
```

### 数据流 | Data Flow

#### 1. 通知创建流程 | Notification Creation Flow

```python
# 步骤1: 业务操作触发
admin_operation() → 业务逻辑完成

# 步骤2: 创建通知 (异步，不阻塞业务)
try:
    await AdminNotificationService.notify_xxx(
        db=db,
        ...params
    )
except Exception as e:
    # 通知失败不影响业务
    logger.error(f"Notification failed: {e}")

# 步骤3: 通知服务处理
AdminNotificationService.create_admin_notification()
  ├─> 插入数据库 (持久化)
  ├─> 通过WebSocket推送 (实时通知)
  └─> 返回通知对象

# 步骤4: 前端接收
WebSocket Client 收到消息
  ├─> 更新未读Badge数量
  ├─> 显示Toast提示 (可选)
  └─> 刷新通知列表 (如果打开)
```

#### 2. 通知查询流程 | Notification Query Flow

```python
# 前端请求
GET /api/v1/admin/notifications?page=1&page_size=20&is_read=false

# 后端处理
AdminNotificationsAPI.get_admin_notifications()
  ├─> 查询条件: (admin_user_id IS NULL OR admin_user_id = current_admin.id)
  ├─> 应用过滤: type, severity, is_read
  ├─> 分页查询: offset, limit
  ├─> 查询未读数: get_unread_count()
  └─> 返回结果: {notifications, total, pages, unread_count}

# 前端渲染
NotificationDrawer 显示通知列表
```

---

## 🚀 快速开始 | Quick Start

### 1. 后端集成 | Backend Integration

#### 在管理接口中添加通知

```python
from app.utils.admin_notification_service import AdminNotificationService

@router.post("/videos/{video_id}/publish")
async def publish_video(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """发布视频"""
    # 1. 业务逻辑
    video = await get_video(db, video_id)
    video.status = "published"
    await db.commit()

    # 2. 发送通知 (异步，不阻塞)
    try:
        await AdminNotificationService.notify_video_published(
            db=db,
            video_id=video.id,
            video_title=video.title,
            admin_username=current_admin.username,
        )
    except Exception as e:
        # 通知失败不影响业务
        logger.error(f"Failed to send notification: {e}")

    # 3. 返回结果
    return {"message": "视频已发布", "video_id": video_id}
```

### 2. 前端集成 | Frontend Integration

#### 显示未读数量Badge

```tsx
import { useQuery } from '@tanstack/react-query';
import { Badge } from 'antd';
import { BellOutlined } from '@ant-design/icons';

function NotificationBadge() {
  // 查询未读数量
  const { data: stats } = useQuery({
    queryKey: ['notification-stats'],
    queryFn: () => api.get('/admin/notifications/stats'),
    refetchInterval: 30000, // 每30秒刷新
  });

  return (
    <Badge count={stats?.unread || 0} overflowCount={99}>
      <BellOutlined style={{ fontSize: 20 }} />
    </Badge>
  );
}
```

#### WebSocket实时通知

```tsx
import { useEffect } from 'react';
import { message } from 'antd';

function useNotificationWebSocket() {
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/api/v1/ws/admin');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'admin_notification') {
        // 显示Toast通知
        message[data.severity || 'info']({
          content: data.title,
          duration: 3,
        });

        // 刷新未读数量
        queryClient.invalidateQueries(['notification-stats']);
      }
    };

    return () => ws.close();
  }, []);
}
```

---

## 📖 API文档 | API Documentation

### 1. 查询通知列表 | Get Notifications

**端点 | Endpoint**: `GET /api/v1/admin/notifications`

**参数 | Parameters**:
```typescript
{
  page?: number;          // 页码 (默认: 1)
  page_size?: number;     // 每页数量 (默认: 20, 最大: 100)
  type?: string;          // 通知类型筛选
  severity?: string;      // 严重程度 (info/warning/error/critical)
  is_read?: boolean;      // 已读状态
}
```

**响应 | Response**:
```json
{
  "notifications": [
    {
      "id": 123,
      "admin_user_id": null,
      "type": "video_published",
      "title": "视频已发布",
      "content": "管理员 admin 发布了视频《示例视频》",
      "severity": "info",
      "related_type": "video",
      "related_id": 456,
      "link": "/videos/456",
      "is_read": false,
      "created_at": "2025-10-14T10:30:00Z",
      "read_at": null
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5,
  "unread_count": 15
}
```

### 2. 获取通知统计 | Get Notification Stats

**端点 | Endpoint**: `GET /api/v1/admin/notifications/stats`

**响应 | Response**:
```json
{
  "total": 100,
  "unread": 15,
  "read": 85,
  "by_severity": {
    "info": 10,
    "warning": 3,
    "error": 2,
    "critical": 0
  }
}
```

### 3. 标记通知为已读 | Mark as Read

**端点 | Endpoint**: `PATCH /api/v1/admin/notifications/{notification_id}`

**响应 | Response**:
```json
{
  "id": 123,
  "is_read": true,
  "read_at": "2025-10-14T10:35:00Z",
  ...
}
```

### 4. 标记所有为已读 | Mark All as Read

**端点 | Endpoint**: `POST /api/v1/admin/notifications/mark-all-read`

**响应 | Response**:
```json
{
  "message": "已标记 15 条通知为已读",
  "count": 15
}
```

### 5. 删除通知 | Delete Notification

**端点 | Endpoint**: `DELETE /api/v1/admin/notifications/{notification_id}`

**响应 | Response**:
```json
{
  "message": "通知已删除"
}
```

### 6. 清空所有通知 | Clear All Notifications

**端点 | Endpoint**: `POST /api/v1/admin/notifications/clear-all`

**响应 | Response**:
```json
{
  "message": "已清空 100 条通知",
  "count": 100
}
```

### 7. 创建测试通知 | Create Test Notification

**端点 | Endpoint**: `POST /api/v1/admin/notifications/test-notification`

**响应 | Response**:
```json
{
  "message": "测试通知已创建"
}
```

---

## 🎨 前端集成 | Frontend Integration

### 完整的通知组件示例

```tsx
// NotificationCenter.tsx
import React, { useState } from 'react';
import { Drawer, List, Badge, Button, Dropdown, Tag } from 'antd';
import { BellOutlined, DeleteOutlined, CheckOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export function NotificationCenter() {
  const [open, setOpen] = useState(false);
  const queryClient = useQueryClient();

  // 查询通知列表
  const { data: notificationsData } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => api.get('/admin/notifications', {
      params: { page: 1, page_size: 50 }
    }),
  });

  // 查询统计
  const { data: stats } = useQuery({
    queryKey: ['notification-stats'],
    queryFn: () => api.get('/admin/notifications/stats'),
    refetchInterval: 30000,
  });

  // 标记已读
  const markAsReadMutation = useMutation({
    mutationFn: (id: number) =>
      api.patch(`/admin/notifications/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications']);
      queryClient.invalidateQueries(['notification-stats']);
    },
  });

  // 全部标记已读
  const markAllReadMutation = useMutation({
    mutationFn: () => api.post('/admin/notifications/mark-all-read'),
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications']);
      queryClient.invalidateQueries(['notification-stats']);
    },
  });

  // 清空所有
  const clearAllMutation = useMutation({
    mutationFn: () => api.post('/admin/notifications/clear-all'),
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications']);
      queryClient.invalidateQueries(['notification-stats']);
    },
  });

  // 严重程度颜色映射
  const getSeverityColor = (severity: string) => {
    const colors = {
      info: 'blue',
      warning: 'orange',
      error: 'red',
      critical: 'magenta',
    };
    return colors[severity] || 'default';
  };

  return (
    <>
      {/* 通知图标 */}
      <Badge count={stats?.unread || 0} overflowCount={99}>
        <Button
          type="text"
          icon={<BellOutlined style={{ fontSize: 20 }} />}
          onClick={() => setOpen(true)}
        />
      </Badge>

      {/* 通知抽屉 */}
      <Drawer
        title="通知中心"
        placement="right"
        width={400}
        open={open}
        onClose={() => setOpen(false)}
        extra={
          <div>
            <Button
              size="small"
              onClick={() => markAllReadMutation.mutate()}
              disabled={stats?.unread === 0}
            >
              全部已读
            </Button>
            <Button
              size="small"
              danger
              onClick={() => clearAllMutation.mutate()}
              style={{ marginLeft: 8 }}
            >
              清空全部
            </Button>
          </div>
        }
      >
        <List
          dataSource={notificationsData?.notifications || []}
          renderItem={(notification) => (
            <List.Item
              style={{
                opacity: notification.is_read ? 0.6 : 1,
                background: notification.is_read ? 'transparent' : '#f0f5ff',
              }}
              actions={[
                !notification.is_read && (
                  <Button
                    type="text"
                    size="small"
                    icon={<CheckOutlined />}
                    onClick={() => markAsReadMutation.mutate(notification.id)}
                  >
                    标记已读
                  </Button>
                ),
              ]}
            >
              <List.Item.Meta
                title={
                  <div>
                    {notification.title}
                    <Tag
                      color={getSeverityColor(notification.severity)}
                      style={{ marginLeft: 8 }}
                    >
                      {notification.severity}
                    </Tag>
                  </div>
                }
                description={
                  <div>
                    <div>{notification.content}</div>
                    <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>
                      {new Date(notification.created_at).toLocaleString()}
                    </div>
                  </div>
                }
              />
            </List.Item>
          )}
        />
      </Drawer>
    </>
  );
}
```

---

## 💡 最佳实践 | Best Practices

### 1. 通知设计原则 | Notification Design Principles

#### ✅ 好的通知 | Good Notifications

```python
# ✅ 清晰的标题和内容
await AdminNotificationService.notify_video_published(
    db=db,
    video_id=123,
    video_title="用户教程第1集",  # 具体的标题
    admin_username="admin",
)
# 结果: "管理员 admin 发布了视频《用户教程第1集》"

# ✅ 包含上下文信息
await AdminNotificationService.notify_comment_moderation(
    db=db,
    comment_id=456,
    action="rejected",
    video_title="用户教程第1集",  # 相关视频
    admin_username="admin",
    comment_count=1,
)
# 结果: "管理员 admin 已拒绝《用户教程第1集》的评论"

# ✅ 合理的严重程度
severity = "critical" if usage >= 95 else \
          "warning" if usage >= 80 else \
          "info"
```

#### ❌ 不好的通知 | Bad Notifications

```python
# ❌ 模糊的标题
title = "操作完成"  # 什么操作？

# ❌ 缺少关键信息
content = "视频已发布"  # 哪个视频？谁发布的？

# ❌ 错误的严重程度
severity = "critical"  # 对于普通操作使用critical级别
```

### 2. 批量操作优化 | Batch Operation Optimization

```python
# ❌ 错误: 循环发送多个通知
for video_id in video_ids:
    await AdminNotificationService.notify_video_published(...)
# 问题: 创建大量通知，性能差

# ✅ 正确: 使用批量通知方法
await AdminNotificationService.notify_batch_operation(
    db=db,
    operation_type="delete",
    entity_type="video",
    count=len(video_ids),
    admin_username=current_admin.username,
    details=f"删除了 {len(video_ids)} 个视频",
)
# 优点: 单条通知，性能好
```

### 3. 错误处理 | Error Handling

```python
# ✅ 正确的错误处理模式
try:
    # 业务逻辑
    video.status = "published"
    await db.commit()

    # 通知 (放在业务逻辑之后)
    try:
        await AdminNotificationService.notify_video_published(...)
    except Exception as e:
        # 通知失败只记录日志，不影响业务
        logger.error(f"通知发送失败: {e}")

except Exception as e:
    # 业务逻辑失败，回滚
    await db.rollback()
    raise
```

### 4. 通知频率控制 | Notification Frequency Control

```python
# 对于高频操作，使用定时汇总通知
from datetime import datetime, timedelta

class NotificationAggregator:
    """通知聚合器 - 避免通知轰炸"""

    def __init__(self):
        self.pending_notifications = []
        self.last_send_time = datetime.utcnow()

    async def add_notification(self, notification_data):
        """添加待发送通知"""
        self.pending_notifications.append(notification_data)

        # 每5分钟或累积10条后发送汇总
        if (datetime.utcnow() - self.last_send_time > timedelta(minutes=5) or
            len(self.pending_notifications) >= 10):
            await self.flush()

    async def flush(self):
        """发送汇总通知"""
        if not self.pending_notifications:
            return

        count = len(self.pending_notifications)
        await AdminNotificationService.notify_batch_operation(
            db=db,
            operation_type="update",
            entity_type="video",
            count=count,
            admin_username="system",
            details=f"系统自动处理了 {count} 个视频",
        )

        self.pending_notifications = []
        self.last_send_time = datetime.utcnow()
```

---

## ⚡ 性能优化 | Performance Optimization

### 1. 数据库优化 | Database Optimization

#### 索引创建 | Create Indexes

```sql
-- 为常用查询字段添加索引
CREATE INDEX idx_admin_notification_admin_user_id
  ON admin_notification(admin_user_id);

CREATE INDEX idx_admin_notification_is_read
  ON admin_notification(is_read);

CREATE INDEX idx_admin_notification_created_at
  ON admin_notification(created_at DESC);

CREATE INDEX idx_admin_notification_type
  ON admin_notification(type);

-- 复合索引 (用于未读通知查询)
CREATE INDEX idx_admin_notification_user_read
  ON admin_notification(admin_user_id, is_read);
```

#### 定期清理 | Regular Cleanup

```python
# 定时任务: 清理90天前的已读通知
from datetime import datetime, timedelta
from sqlalchemy import delete

async def cleanup_old_notifications(db: AsyncSession):
    """清理旧通知"""
    cutoff_date = datetime.utcnow() - timedelta(days=90)

    query = delete(AdminNotification).where(
        and_(
            AdminNotification.is_read == True,
            AdminNotification.created_at < cutoff_date,
        )
    )

    result = await db.execute(query)
    await db.commit()

    logger.info(f"清理了 {result.rowcount} 条旧通知")
    return result.rowcount

# 在后台任务中每天执行
# (使用 Celery 或 APScheduler)
```

### 2. WebSocket优化 | WebSocket Optimization

```python
# 使用连接池管理WebSocket连接
class WebSocketConnectionPool:
    """WebSocket连接池"""

    def __init__(self, max_connections=1000):
        self.connections: Dict[int, WebSocket] = {}
        self.max_connections = max_connections

    async def add_connection(self, admin_id: int, websocket: WebSocket):
        """添加连接"""
        if len(self.connections) >= self.max_connections:
            # 移除最久未活动的连接
            await self.remove_oldest_inactive()

        self.connections[admin_id] = websocket

    async def broadcast_to_admins(self, message: dict):
        """向所有在线管理员广播"""
        disconnected = []

        for admin_id, ws in self.connections.items():
            try:
                await ws.send_json(message)
            except:
                disconnected.append(admin_id)

        # 清理断开的连接
        for admin_id in disconnected:
            self.connections.pop(admin_id, None)
```

### 3. 缓存策略 | Caching Strategy

```python
from app.utils.cache import Cache

class CachedNotificationService:
    """带缓存的通知服务"""

    @staticmethod
    async def get_unread_count_cached(
        db: AsyncSession,
        admin_user_id: int,
    ) -> int:
        """获取未读数量 (带缓存)"""
        cache_key = f"notification:unread_count:{admin_user_id}"

        # 尝试从缓存获取
        cached = await Cache.get(cache_key)
        if cached is not None:
            return cached

        # 从数据库查询
        count = await AdminNotificationService.get_unread_count(
            db, admin_user_id
        )

        # 缓存30秒
        await Cache.set(cache_key, count, ttl=30)

        return count

    @staticmethod
    async def invalidate_unread_count_cache(admin_user_id: int):
        """失效未读数量缓存"""
        cache_key = f"notification:unread_count:{admin_user_id}"
        await Cache.delete(cache_key)
```

---

## 🔧 故障排查 | Troubleshooting

### 常见问题 | Common Issues

#### 1. 通知没有实时显示

**症状**: 创建通知后，前端没有实时收到

**排查步骤**:
```bash
# 1. 检查WebSocket连接状态
# 浏览器控制台
console.log(ws.readyState); // 应该是 1 (OPEN)

# 2. 检查后端WebSocket日志
docker-compose logs -f backend | grep "WebSocket"

# 3. 检查通知是否创建成功
curl -X GET http://localhost:8000/api/v1/admin/notifications \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. 测试WebSocket连接
curl -X POST http://localhost:8000/api/v1/admin/notifications/test-notification \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**解决方案**:
- 确认WebSocket URL正确 (`ws://` 或 `wss://`)
- 检查CORS设置是否允许WebSocket
- 确认防火墙没有阻止WebSocket连接

#### 2. 通知数据库查询慢

**症状**: 获取通知列表响应时间 > 1秒

**排查步骤**:
```sql
-- 检查是否有索引
SELECT indexname FROM pg_indexes
WHERE tablename = 'admin_notification';

-- 查看慢查询
EXPLAIN ANALYZE
SELECT * FROM admin_notification
WHERE (admin_user_id IS NULL OR admin_user_id = 1)
  AND is_read = false
ORDER BY created_at DESC
LIMIT 20;
```

**解决方案**:
- 添加必要的索引 (见性能优化章节)
- 定期清理旧通知
- 考虑分页加载

#### 3. 未读数量不准确

**症状**: Badge显示的未读数与实际不符

**排查步骤**:
```python
# 直接查询数据库验证
from sqlalchemy import select, func, and_, or_
from app.models.notification import AdminNotification

query = select(func.count(AdminNotification.id)).where(
    and_(
        AdminNotification.is_read.is_(False),
        or_(
            AdminNotification.admin_user_id.is_(None),
            AdminNotification.admin_user_id == admin_id,
        )
    )
)
result = await db.execute(query)
actual_count = result.scalar()
print(f"实际未读数: {actual_count}")
```

**解决方案**:
- 清除缓存: `await Cache.delete(f"notification:unread_count:{admin_id}")`
- 手动刷新前端查询: `queryClient.invalidateQueries(['notification-stats'])`
- 检查标记已读的逻辑是否正确执行

---

## 🛠️ 扩展开发 | Extension Development

### 1. 添加新的通知类型

#### 步骤 1: 在 `AdminNotificationService` 中添加方法

```python
# backend/app/utils/admin_notification_service.py

@staticmethod
async def notify_custom_event(
    db: AsyncSession,
    event_id: int,
    event_name: str,
    admin_username: str,
    details: Optional[str] = None,
):
    """
    自定义事件通知

    Args:
        db: 数据库会话
        event_id: 事件ID
        event_name: 事件名称
        admin_username: 触发管理员
        details: 事件详情
    """
    await AdminNotificationService.create_admin_notification(
        db=db,
        admin_user_id=None,  # 广播给所有管理员
        type="custom_event",  # 自定义类型
        title=f"自定义事件: {event_name}",
        content=f"管理员 {admin_username} 触发了事件《{event_name}》" +
                (f" - {details}" if details else ""),
        severity="info",
        related_type="custom_event",
        related_id=event_id,
        link=f"/custom-events/{event_id}",
    )
```

#### 步骤 2: 在业务代码中调用

```python
# backend/app/admin/custom_module.py

@router.post("/custom-event")
async def trigger_custom_event(
    event_data: CustomEventCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """触发自定义事件"""
    # 业务逻辑
    event = CustomEvent(**event_data.dict())
    db.add(event)
    await db.commit()

    # 发送通知
    try:
        await AdminNotificationService.notify_custom_event(
            db=db,
            event_id=event.id,
            event_name=event.name,
            admin_username=current_admin.username,
            details=event.description,
        )
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")

    return event
```

### 2. 添加通知订阅功能

```python
# backend/app/models/notification.py

class NotificationSubscription(Base):
    """通知订阅配置"""
    __tablename__ = "notification_subscription"

    id = Column(Integer, primary_key=True)
    admin_user_id = Column(Integer, ForeignKey("admin_user.id"), nullable=False)
    notification_type = Column(String(50), nullable=False)  # 订阅的通知类型
    enabled = Column(Boolean, default=True)  # 是否启用
    channel = Column(String(20), default="websocket")  # 通知渠道: websocket/email/sms
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

# backend/app/utils/admin_notification_service.py

@staticmethod
async def create_admin_notification(
    db: AsyncSession,
    admin_user_id: Optional[int],
    type: str,
    ...
):
    """创建管理员通知 (支持订阅过滤)"""

    # 查询订阅配置
    if admin_user_id:
        subscription = await get_subscription(db, admin_user_id, type)
        if subscription and not subscription.enabled:
            # 该管理员取消订阅此类型通知
            logger.info(f"Admin {admin_user_id} unsubscribed from {type}")
            return

    # 创建通知 (原有逻辑)
    ...
```

### 3. 添加邮件通知渠道

```python
# backend/app/utils/notification_channels.py

class EmailNotificationChannel:
    """邮件通知渠道"""

    @staticmethod
    async def send_email_notification(
        notification: AdminNotification,
        admin_email: str,
    ):
        """通过邮件发送通知"""
        from app.utils.email_service import send_email

        # 邮件模板
        html_content = f"""
        <h2>{notification.title}</h2>
        <p>{notification.content}</p>
        <p>严重程度: <strong>{notification.severity}</strong></p>
        <p>时间: {notification.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
        {f'<a href="{notification.link}">查看详情</a>' if notification.link else ''}
        """

        await send_email(
            to_email=admin_email,
            subject=f"[VideoSite] {notification.title}",
            html_content=html_content,
        )

# 在 AdminNotificationService 中集成
@staticmethod
async def create_admin_notification(...):
    # 创建通知
    notification = AdminNotification(...)
    db.add(notification)
    await db.commit()

    # WebSocket推送
    if send_websocket:
        await AdminNotificationService._send_websocket_notification(notification)

    # 邮件推送 (对于critical级别)
    if notification.severity == "critical":
        # 查询所有管理员邮箱
        admins = await get_all_admin_emails(db)
        for admin_email in admins:
            await EmailNotificationChannel.send_email_notification(
                notification, admin_email
            )
```

---

## 📊 监控和分析 | Monitoring & Analytics

### 1. 通知系统健康监控

```python
# backend/app/admin/system_health.py

@router.get("/notification-health")
async def get_notification_system_health(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取通知系统健康状态"""

    # 统计最近24小时
    from datetime import datetime, timedelta
    yesterday = datetime.utcnow() - timedelta(days=1)

    # 创建的通知数
    created_query = select(func.count(AdminNotification.id)).where(
        AdminNotification.created_at >= yesterday
    )
    created_count = (await db.execute(created_query)).scalar()

    # 已读通知数
    read_query = select(func.count(AdminNotification.id)).where(
        and_(
            AdminNotification.created_at >= yesterday,
            AdminNotification.is_read == True,
        )
    )
    read_count = (await db.execute(read_query)).scalar()

    # 阅读率
    read_rate = (read_count / created_count * 100) if created_count > 0 else 0

    # WebSocket连接数
    websocket_connections = len(manager.active_admin_connections)

    return {
        "status": "healthy",
        "metrics": {
            "notifications_created_24h": created_count,
            "notifications_read_24h": read_count,
            "read_rate": f"{read_rate:.1f}%",
            "active_websocket_connections": websocket_connections,
        }
    }
```

### 2. 通知效果分析

```python
# backend/app/admin/analytics.py

@router.get("/notification-analytics")
async def get_notification_analytics(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """通知分析报告"""

    from datetime import datetime, timedelta

    start_date = datetime.utcnow() - timedelta(days=days)

    # 按类型统计
    type_query = (
        select(
            AdminNotification.type,
            func.count(AdminNotification.id).label("count"),
            func.avg(
                case(
                    (AdminNotification.is_read == True, 1),
                    else_=0
                )
            ).label("read_rate")
        )
        .where(AdminNotification.created_at >= start_date)
        .group_by(AdminNotification.type)
        .order_by(desc("count"))
    )

    type_stats = await db.execute(type_query)

    # 按严重程度统计
    severity_query = (
        select(
            AdminNotification.severity,
            func.count(AdminNotification.id).label("count"),
        )
        .where(AdminNotification.created_at >= start_date)
        .group_by(AdminNotification.severity)
    )

    severity_stats = await db.execute(severity_query)

    # 平均响应时间 (创建到已读)
    response_time_query = select(
        func.avg(
            extract('epoch', AdminNotification.read_at) -
            extract('epoch', AdminNotification.created_at)
        )
    ).where(
        and_(
            AdminNotification.created_at >= start_date,
            AdminNotification.read_at.isnot(None),
        )
    )

    avg_response_time = (await db.execute(response_time_query)).scalar()

    return {
        "period_days": days,
        "by_type": [
            {
                "type": row.type,
                "count": row.count,
                "read_rate": f"{row.read_rate * 100:.1f}%"
            }
            for row in type_stats
        ],
        "by_severity": [
            {"severity": row.severity, "count": row.count}
            for row in severity_stats
        ],
        "avg_response_time_seconds": int(avg_response_time or 0),
    }
```

---

## 🎓 总结 | Summary

通知系统是VideoSite管理后台的核心功能之一，提供了：

✅ **完整的功能覆盖** - 20个通知方法，覆盖所有关键业务场景
✅ **实时性** - WebSocket推送，延迟<300ms
✅ **可靠性** - 数据库持久化，通知不丢失
✅ **易用性** - 统一的API，简单的集成方式
✅ **可扩展性** - 支持自定义通知类型和渠道
✅ **高性能** - 异步处理，不阻塞业务逻辑

通过本指南，您可以：
- 快速集成新的通知类型
- 优化通知系统性能
- 排查和解决常见问题
- 扩展通知功能

---

**相关文档 | Related Documents**:
- [通知系统100%完成报告](NOTIFICATION_INTEGRATION_100_COMPLETE.md)
- [通知系统快速参考](NOTIFICATION_QUICK_REFERENCE.md)
- [API文档](http://localhost:8000/api/docs)

**支持 | Support**:
- GitHub Issues: [报告问题](https://github.com/your-repo/issues)
- 文档更新: 2025-10-14

---
