"""
分享记录模型
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.video import Video


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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    platform: Mapped[SharePlatform] = mapped_column(SQLEnum(SharePlatform), nullable=False, index=True)
    shared_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    # IP地址和User Agent (用于分析)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv6最长45字符
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    video: Mapped[Video] = relationship("Video", back_populates="shares")
    user: Mapped[Optional[User]] = relationship("User", back_populates="shares")
