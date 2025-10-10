from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class NotificationType(str, enum.Enum):
    """Notification type enum"""
    COMMENT_REPLY = "comment_reply"  # 评论回复
    VIDEO_PUBLISHED = "video_published"  # 视频发布
    SYSTEM_ANNOUNCEMENT = "system_announcement"  # 系统公告
    VIDEO_LIKED = "video_liked"  # 视频被点赞
    COMMENT_LIKED = "comment_liked"  # 评论被点赞
    NEW_FOLLOWER = "new_follower"  # 新关注者
    VIDEO_RECOMMENDATION = "video_recommendation"  # 推荐视频


class Notification(Base):
    """Notification model"""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)  # 通知类型
    title = Column(String(200), nullable=False)  # 通知标题
    content = Column(Text, nullable=False)  # 通知内容
    related_type = Column(String(50), nullable=True)  # 关联对象类型: video, comment, user
    related_id = Column(Integer, nullable=True)  # 关联对象ID
    link = Column(String(500), nullable=True)  # 跳转链接
    is_read = Column(Boolean, default=False, nullable=False, index=True)  # 是否已读
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)  # 阅读时间

    # Relationships
    user = relationship("User", backref="notifications")
