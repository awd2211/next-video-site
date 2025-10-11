"""
分享记录模型
"""

import enum

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class SharePlatform(str, enum.Enum):
    """分享平台枚举"""

    WECHAT = "wechat"
    WEIBO = "weibo"
    QQ = "qq"
    QZONE = "qzone"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINK = "link"  # 复制链接
    OTHER = "other"


class VideoShare(Base):
    """视频分享记录"""

    __tablename__ = "video_shares"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    platform = Column(SQLEnum(SharePlatform), nullable=False, index=True)
    shared_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # IP地址和User Agent (用于分析)
    ip_address = Column(String(45), nullable=True)  # IPv6最长45字符
    user_agent = Column(String(500), nullable=True)

    # Relationships
    video = relationship("Video", back_populates="shares")
    user = relationship("User", back_populates="shares")
