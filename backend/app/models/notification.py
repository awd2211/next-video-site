from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import AdminUser, User


class NotificationType(str, enum.Enum):
    """Notification type enum"""

    # User notifications
    COMMENT_REPLY = "comment_reply"  # 评论回复
    VIDEO_PUBLISHED = "video_published"  # 视频发布
    SYSTEM_ANNOUNCEMENT = "system_announcement"  # 系统公告
    VIDEO_LIKED = "video_liked"  # 视频被点赞
    COMMENT_LIKED = "comment_liked"  # 评论被点赞
    NEW_FOLLOWER = "new_follower"  # 新关注者
    VIDEO_RECOMMENDATION = "video_recommendation"  # 推荐视频

    # Admin notifications
    NEW_USER_REGISTRATION = "new_user_registration"  # 新用户注册
    PENDING_COMMENT_REVIEW = "pending_comment_review"  # 待审核评论
    SYSTEM_ERROR_ALERT = "system_error_alert"  # 系统错误告警
    STORAGE_WARNING = "storage_warning"  # 存储空间警告
    UPLOAD_FAILED = "upload_failed"  # 上传失败
    VIDEO_PROCESSING_COMPLETE = "video_processing_complete"  # 视频处理完成
    SUSPICIOUS_ACTIVITY = "suspicious_activity"  # 可疑活动


class Notification(Base):
    """Notification model"""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # 通知类型
    title: Mapped[str] = mapped_column(String(200), nullable=False)  # 通知标题
    content: Mapped[str] = mapped_column(Text, nullable=False)  # 通知内容
    related_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # 关联对象类型: video, comment, user
    related_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 关联对象ID
    link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # 跳转链接
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)  # 是否已读
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # 阅读时间

    # Relationships
    user: Mapped[User] = relationship("User", backref="notifications")


class AdminNotification(Base):
    """Admin notification model - for notifications to admin users"""

    __tablename__ = "admin_notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    admin_user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("admin_users.id", ondelete="CASCADE"), nullable=True, index=True
    )  # None means broadcast to all admins
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(
        String(20), default="info", nullable=False
    )  # info, warning, error, critical
    related_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    related_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    admin_user: Mapped[Optional[AdminUser]] = relationship("AdminUser", backref="admin_notifications")
