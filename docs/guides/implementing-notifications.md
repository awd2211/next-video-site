# 用户通知系统实施指南

**预计工作量**: 6-8小时
**优先级**: P0 (高)
**当前状态**: 未实现

---

## 📋 功能需求

用户通知系统用于向用户推送以下消息:
- **评论回复通知**: 用户的评论被回复时
- **点赞通知**: 用户的评论被点赞
- **系统消息**: 管理员发送的公告、警告等
- **视频更新**: 收藏的剧集更新提醒

---

## 🗄️ 数据库设计

### 1. 创建Notification模型

**文件**: `backend/app/models/notification.py`

```python
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class NotificationType(str, enum.Enum):
    """通知类型"""
    COMMENT_REPLY = "comment_reply"      # 评论回复
    COMMENT_LIKE = "comment_like"        # 评论点赞
    SYSTEM = "system"                    # 系统消息
    VIDEO_UPDATE = "video_update"        # 视频更新
    ANNOUNCEMENT = "announcement"        # 公告


class Notification(Base):
    """用户通知表"""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(Enum(NotificationType), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    link = Column(String(500), nullable=True)  # 点击后跳转的链接
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)

    # 关联数据 (可选,用于追踪来源)
    related_comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    related_video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=True)
    related_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # 触发者

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="notifications")
    related_comment = relationship("Comment", foreign_keys=[related_comment_id])
    related_video = relationship("Video", foreign_keys=[related_video_id])
    related_user = relationship("User", foreign_keys=[related_user_id])  # 触发通知的用户
```

### 2. 创建数据库迁移

**文件**: `backend/alembic/versions/add_notifications_20251010.py`

```python
"""add notifications table

Revision ID: add_notifications_20251010
Revises: add_transcode_status_20251010
Create Date: 2025-10-10 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'add_notifications_20251010'
down_revision = 'add_transcode_status_20251010'
branch_labels = None
depends_on = None


def upgrade():
    # 创建通知类型枚举
    notification_type = postgresql.ENUM(
        'comment_reply', 'comment_like', 'system', 'video_update', 'announcement',
        name='notificationtype',
        create_type=False
    )
    notification_type.create(op.get_bind(), checkfirst=True)

    # 创建notifications表
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', notification_type, nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('link', sa.String(500), nullable=True),
        sa.Column('is_read', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('related_comment_id', sa.Integer(), nullable=True),
        sa.Column('related_video_id', sa.Integer(), nullable=True),
        sa.Column('related_user_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['related_comment_id'], ['comments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['related_video_id'], ['videos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['related_user_id'], ['users.id'], ondelete='SET NULL'),
    )

    # 创建索引
    op.create_index('idx_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('idx_notifications_type', 'notifications', ['type'])
    op.create_index('idx_notifications_is_read', 'notifications', ['is_read'])
    op.create_index('idx_notifications_created_at', 'notifications', ['created_at'])
    op.create_index('idx_notifications_user_unread', 'notifications', ['user_id', 'is_read'])


def downgrade():
    op.drop_index('idx_notifications_user_unread', table_name='notifications')
    op.drop_index('idx_notifications_created_at', table_name='notifications')
    op.drop_index('idx_notifications_is_read', table_name='notifications')
    op.drop_index('idx_notifications_type', table_name='notifications')
    op.drop_index('idx_notifications_user_id', table_name='notifications')
    op.drop_table('notifications')

    notification_type = postgresql.ENUM(name='notificationtype')
    notification_type.drop(op.get_bind(), checkfirst=True)
```

**运行迁移**:
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

---

## 🔧 后端API实现

### 1. Pydantic Schemas

**文件**: `backend/app/schemas/notification.py`

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationBase(BaseModel):
    title: str
    content: str
    link: Optional[str] = None
    type: str


class NotificationCreate(NotificationBase):
    user_id: int
    related_comment_id: Optional[int] = None
    related_video_id: Optional[int] = None
    related_user_id: Optional[int] = None


class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    related_comment_id: Optional[int] = None
    related_video_id: Optional[int] = None
    related_user_id: Optional[int] = None

    class Config:
        from_attributes = True


class NotificationStats(BaseModel):
    """通知统计"""
    total: int
    unread: int


class PaginatedNotificationsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[NotificationResponse]
    stats: NotificationStats
```

### 2. API端点

**文件**: `backend/app/api/notifications.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import (
    NotificationResponse,
    PaginatedNotificationsResponse,
    NotificationStats,
)
from app.utils.dependencies import get_current_active_user
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=PaginatedNotificationsResponse)
async def get_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取当前用户的通知列表

    - **page**: 页码
    - **page_size**: 每页数量
    - **unread_only**: 只显示未读通知
    """
    # 构建查询
    query = select(Notification).where(Notification.user_id == current_user.id)

    if unread_only:
        query = query.where(Notification.is_read == False)

    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 统计未读数
    unread_query = select(func.count()).where(
        and_(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        )
    )
    unread_result = await db.execute(unread_query)
    unread = unread_result.scalar()

    # 分页查询
    query = query.order_by(desc(Notification.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    notifications = result.scalars().all()

    return PaginatedNotificationsResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[NotificationResponse.model_validate(n) for n in notifications],
        stats=NotificationStats(total=total, unread=unread)
    )


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """标记通知为已读"""
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user.id
            )
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now()
        await db.commit()
        await db.refresh(notification)

    return NotificationResponse.model_validate(notification)


@router.post("/mark-all-read")
async def mark_all_as_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """标记所有通知为已读"""
    from sqlalchemy import update

    await db.execute(
        update(Notification)
        .where(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_read == False
            )
        )
        .values(is_read=True, read_at=datetime.now())
    )
    await db.commit()

    return {"message": "All notifications marked as read"}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """删除通知"""
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user.id
            )
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    await db.delete(notification)
    await db.commit()

    return None


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_all_notifications(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """清空所有通知"""
    result = await db.execute(
        select(Notification).where(Notification.user_id == current_user.id)
    )
    notifications = result.scalars().all()

    for notification in notifications:
        await db.delete(notification)

    await db.commit()

    return None


@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取通知统计信息 (用于Header徽章)"""
    # 总数
    total_result = await db.execute(
        select(func.count()).where(Notification.user_id == current_user.id)
    )
    total = total_result.scalar()

    # 未读数
    unread_result = await db.execute(
        select(func.count()).where(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_read == False
            )
        )
    )
    unread = unread_result.scalar()

    return NotificationStats(total=total, unread=unread)
```

### 3. 通知创建工具类

**文件**: `backend/app/utils/notification_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.models.comment import Comment
from app.models.video import Video


class NotificationService:
    """通知服务"""

    @staticmethod
    async def create_comment_reply_notification(
        db: AsyncSession,
        parent_comment: Comment,
        reply_comment: Comment,
        reply_user: User
    ):
        """
        创建评论回复通知

        当用户A回复了用户B的评论时,通知用户B
        """
        # 不给自己发通知
        if parent_comment.user_id == reply_user.id:
            return

        notification = Notification(
            user_id=parent_comment.user_id,  # 被回复的用户
            type=NotificationType.COMMENT_REPLY,
            title=f"{reply_user.username} 回复了你的评论",
            content=reply_comment.content[:200],  # 限制长度
            link=f"/videos/{reply_comment.video_id}?comment={reply_comment.id}",
            related_comment_id=reply_comment.id,
            related_video_id=reply_comment.video_id,
            related_user_id=reply_user.id
        )

        db.add(notification)
        await db.commit()

    @staticmethod
    async def create_system_notification(
        db: AsyncSession,
        user_id: int,
        title: str,
        content: str,
        link: str = None
    ):
        """创建系统通知 (管理员发送)"""
        notification = Notification(
            user_id=user_id,
            type=NotificationType.SYSTEM,
            title=title,
            content=content,
            link=link
        )

        db.add(notification)
        await db.commit()

    @staticmethod
    async def create_video_update_notification(
        db: AsyncSession,
        user_id: int,
        video: Video
    ):
        """创建视频更新通知 (用于剧集更新)"""
        notification = Notification(
            user_id=user_id,
            type=NotificationType.VIDEO_UPDATE,
            title=f"《{video.title}》更新了",
            content=f"你收藏的剧集《{video.title}》有新内容更新",
            link=f"/videos/{video.id}",
            related_video_id=video.id
        )

        db.add(notification)
        await db.commit()
```

### 4. 集成到评论API

修改 `backend/app/api/comments.py`:

```python
# 在创建评论端点中添加:
from app.utils.notification_service import NotificationService

@router.post("/", response_model=CommentResponse)
async def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # ... 创建评论逻辑 ...

    # 🆕 如果是回复评论,发送通知
    if new_comment.parent_id:
        parent_result = await db.execute(
            select(Comment).where(Comment.id == new_comment.parent_id)
        )
        parent_comment = parent_result.scalar_one_or_none()

        if parent_comment:
            await NotificationService.create_comment_reply_notification(
                db,
                parent_comment,
                new_comment,
                current_user
            )

    return new_comment
```

---

## 🎨 前端实现

### 1. API Service

**文件**: `frontend/src/services/notificationService.ts`

```typescript
import api from './api'

export interface Notification {
  id: number
  user_id: number
  type: string
  title: string
  content: string
  link?: string
  is_read: boolean
  created_at: string
  read_at?: string
  related_comment_id?: number
  related_video_id?: number
  related_user_id?: number
}

export interface NotificationStats {
  total: number
  unread: number
}

export interface PaginatedNotifications {
  total: number
  page: number
  page_size: number
  items: Notification[]
  stats: NotificationStats
}

export const notificationService = {
  // 获取通知列表
  getNotifications: async (
    page: number = 1,
    pageSize: number = 20,
    unreadOnly: boolean = false
  ): Promise<PaginatedNotifications> => {
    const response = await api.get('/notifications/', {
      params: { page, page_size: pageSize, unread_only: unreadOnly }
    })
    return response.data
  },

  // 获取统计信息
  getStats: async (): Promise<NotificationStats> => {
    const response = await api.get('/notifications/stats')
    return response.data
  },

  // 标记为已读
  markAsRead: async (notificationId: number): Promise<Notification> => {
    const response = await api.patch(`/notifications/${notificationId}/read`)
    return response.data
  },

  // 标记全部已读
  markAllAsRead: async (): Promise<void> => {
    await api.post('/notifications/mark-all-read')
  },

  // 删除通知
  deleteNotification: async (notificationId: number): Promise<void> => {
    await api.delete(`/notifications/${notificationId}`)
  },

  // 清空所有通知
  clearAll: async (): Promise<void> => {
    await api.delete('/notifications/')
  }
}
```

### 2. Header通知铃铛组件

**文件**: `frontend/src/components/NotificationBell.tsx`

```typescript
import React, { useState, useEffect } from 'react'
import { Bell } from 'lucide-react'
import { notificationService, Notification } from '../services/notificationService'
import { Link } from 'react-router-dom'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'

export const NotificationBell: React.FC = () => {
  const [unreadCount, setUnreadCount] = useState(0)
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [showDropdown, setShowDropdown] = useState(false)
  const [loading, setLoading] = useState(false)

  // 每30秒刷新未读数
  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchStats = async () => {
    try {
      const stats = await notificationService.getStats()
      setUnreadCount(stats.unread)
    } catch (error) {
      console.error('Failed to fetch notification stats:', error)
    }
  }

  const fetchNotifications = async () => {
    setLoading(true)
    try {
      const data = await notificationService.getNotifications(1, 10, false)
      setNotifications(data.items)
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleBellClick = () => {
    if (!showDropdown) {
      fetchNotifications()
    }
    setShowDropdown(!showDropdown)
  }

  const handleMarkAsRead = async (notificationId: number) => {
    try {
      await notificationService.markAsRead(notificationId)
      setNotifications(prev =>
        prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
      )
      setUnreadCount(prev => Math.max(0, prev - 1))
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
    }
  }

  const handleMarkAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead()
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })))
      setUnreadCount(0)
    } catch (error) {
      console.error('Failed to mark all as read:', error)
    }
  }

  return (
    <div className="relative">
      {/* 铃铛按钮 */}
      <button
        onClick={handleBellClick}
        className="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none"
      >
        <Bell className="w-6 h-6" />
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* 下拉菜单 */}
      {showDropdown && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
          {/* 头部 */}
          <div className="flex items-center justify-between p-4 border-b">
            <h3 className="text-lg font-semibold">通知</h3>
            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllAsRead}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                全部已读
              </button>
            )}
          </div>

          {/* 通知列表 */}
          {loading ? (
            <div className="p-4 text-center text-gray-500">加载中...</div>
          ) : notifications.length === 0 ? (
            <div className="p-4 text-center text-gray-500">暂无通知</div>
          ) : (
            <div className="divide-y">
              {notifications.map(notification => (
                <Link
                  key={notification.id}
                  to={notification.link || '/notifications'}
                  onClick={() => {
                    if (!notification.is_read) {
                      handleMarkAsRead(notification.id)
                    }
                    setShowDropdown(false)
                  }}
                  className={`block p-4 hover:bg-gray-50 transition ${
                    !notification.is_read ? 'bg-blue-50' : ''
                  }`}
                >
                  <div className="flex items-start">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900">
                        {notification.title}
                      </p>
                      <p className="text-sm text-gray-600 truncate">
                        {notification.content}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        {formatDistanceToNow(new Date(notification.created_at), {
                          addSuffix: true,
                          locale: zhCN
                        })}
                      </p>
                    </div>
                    {!notification.is_read && (
                      <div className="ml-2">
                        <span className="inline-block w-2 h-2 bg-blue-600 rounded-full"></span>
                      </div>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          )}

          {/* 底部 */}
          <div className="p-3 border-t">
            <Link
              to="/notifications"
              onClick={() => setShowDropdown(false)}
              className="block text-center text-sm text-blue-600 hover:text-blue-800"
            >
              查看全部通知
            </Link>
          </div>
        </div>
      )}

      {/* 点击外部关闭 */}
      {showDropdown && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowDropdown(false)}
        />
      )}
    </div>
  )
}
```

### 3. 通知列表页面

**文件**: `frontend/src/pages/Notifications/index.tsx`

```typescript
import React, { useState, useEffect } from 'react'
import { notificationService, Notification } from '../../services/notificationService'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { Link } from 'react-router-dom'
import { Trash2, CheckCheck } from 'lucide-react'

const NotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [filter, setFilter] = useState<'all' | 'unread'>('all')

  useEffect(() => {
    fetchNotifications()
  }, [page, filter])

  const fetchNotifications = async () => {
    setLoading(true)
    try {
      const data = await notificationService.getNotifications(
        page,
        20,
        filter === 'unread'
      )
      setNotifications(data.items)
      setTotal(data.total)
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleMarkAsRead = async (id: number) => {
    await notificationService.markAsRead(id)
    fetchNotifications()
  }

  const handleDelete = async (id: number) => {
    if (confirm('确定要删除这条通知吗?')) {
      await notificationService.deleteNotification(id)
      fetchNotifications()
    }
  }

  const handleMarkAllAsRead = async () => {
    await notificationService.markAllAsRead()
    fetchNotifications()
  }

  const handleClearAll = async () => {
    if (confirm('确定要清空所有通知吗?')) {
      await notificationService.clearAll()
      fetchNotifications()
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* 头部 */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">通知中心</h1>
          <div className="space-x-2">
            <button
              onClick={handleMarkAllAsRead}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              <CheckCheck className="w-4 h-4 inline mr-1" />
              全部已读
            </button>
            <button
              onClick={handleClearAll}
              className="px-4 py-2 text-sm bg-red-600 text-white rounded hover:bg-red-700"
            >
              <Trash2 className="w-4 h-4 inline mr-1" />
              清空通知
            </button>
          </div>
        </div>

        {/* 筛选 */}
        <div className="mb-4">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 mr-2 rounded ${
              filter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200'
            }`}
          >
            全部
          </button>
          <button
            onClick={() => setFilter('unread')}
            className={`px-4 py-2 rounded ${
              filter === 'unread' ? 'bg-blue-600 text-white' : 'bg-gray-200'
            }`}
          >
            未读
          </button>
        </div>

        {/* 通知列表 */}
        {loading ? (
          <div className="text-center py-12">加载中...</div>
        ) : notifications.length === 0 ? (
          <div className="text-center py-12 text-gray-500">暂无通知</div>
        ) : (
          <div className="bg-white rounded-lg shadow divide-y">
            {notifications.map(notification => (
              <div
                key={notification.id}
                className={`p-4 ${!notification.is_read ? 'bg-blue-50' : ''}`}
              >
                <div className="flex items-start justify-between">
                  <Link
                    to={notification.link || '#'}
                    className="flex-1"
                    onClick={() => !notification.is_read && handleMarkAsRead(notification.id)}
                  >
                    <h3 className="font-semibold text-gray-900 mb-1">
                      {notification.title}
                    </h3>
                    <p className="text-gray-600 text-sm mb-2">
                      {notification.content}
                    </p>
                    <p className="text-xs text-gray-400">
                      {formatDistanceToNow(new Date(notification.created_at), {
                        addSuffix: true,
                        locale: zhCN
                      })}
                    </p>
                  </Link>

                  <button
                    onClick={() => handleDelete(notification.id)}
                    className="ml-4 p-2 text-gray-400 hover:text-red-600"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 分页 */}
        {total > 20 && (
          <div className="mt-6 flex justify-center">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 border rounded mr-2 disabled:opacity-50"
            >
              上一页
            </button>
            <span className="px-4 py-2">
              第 {page} 页 / 共 {Math.ceil(total / 20)} 页
            </span>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={page >= Math.ceil(total / 20)}
              className="px-4 py-2 border rounded ml-2 disabled:opacity-50"
            >
              下一页
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default NotificationsPage
```

### 4. 集成到Header

修改 `frontend/src/components/Header.tsx`:

```typescript
import { NotificationBell } from './NotificationBell'

// 在Header组件中添加:
<div className="flex items-center space-x-4">
  {/* ... 其他元素 ... */}
  <NotificationBell />
  {/* ... */}
</div>
```

---

## 📝 注册路由

### 后端

`backend/app/main.py`:

```python
from app.api import notifications

app.include_router(
    notifications.router,
    prefix=f"{settings.API_V1_PREFIX}/notifications",
    tags=["Notifications"]
)
```

### 前端

`frontend/src/App.tsx`:

```typescript
import NotificationsPage from './pages/Notifications'

// 在路由中添加:
<Route path="/notifications" element={<NotificationsPage />} />
```

---

## 🧪 测试

### 1. 后端测试

```python
# backend/tests/test_notifications.py
import pytest
from app.models.notification import Notification, NotificationType

async def test_create_notification(db, test_user):
    notification = Notification(
        user_id=test_user.id,
        type=NotificationType.SYSTEM,
        title="测试通知",
        content="这是一条测试通知"
    )
    db.add(notification)
    await db.commit()

    assert notification.id is not None
    assert notification.is_read == False

async def test_get_notifications(client, test_user_token):
    response = await client.get(
        "/api/v1/notifications/",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "stats" in data
```

---

## ✅ 完成清单

- [ ] 创建Notification数据库模型
- [ ] 运行数据库迁移
- [ ] 实现后端API (7个端点)
- [ ] 创建NotificationService工具类
- [ ] 集成到评论API (触发通知)
- [ ] 前端API Service
- [ ] NotificationBell组件
- [ ] 通知列表页面
- [ ] 注册路由 (前后端)
- [ ] 编写测试

---

## 🚀 未来优化

1. **实时推送**: 使用WebSocket替代轮询
2. **邮件通知**: 重要通知发送邮件
3. **推送通知**: 集成Web Push API
4. **通知偏好设置**: 用户可自定义通知类型
5. **批量操作**: 选择多条通知批量删除/已读

---

**预计完成时间**: 6-8小时
**当前进度**: 📝 文档完成,待实施
