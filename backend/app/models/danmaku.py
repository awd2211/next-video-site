"""
弹幕模型
Danmaku (Bullet Comment) Model
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import (
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import AdminUser, User
    from app.models.video import Video


class DanmakuType(str, enum.Enum):
    """弹幕类型"""

    SCROLL = "scroll"  # 滚动弹幕
    TOP = "top"  # 顶部弹幕
    BOTTOM = "bottom"  # 底部弹幕


class DanmakuStatus(str, enum.Enum):
    """弹幕状态"""

    PENDING = "pending"  # 待审核
    APPROVED = "approved"  # 已通过
    REJECTED = "rejected"  # 已拒绝
    DELETED = "deleted"  # 已删除


class Danmaku(Base):
    """弹幕模型"""

    __tablename__ = "danmaku"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # 弹幕内容
    content: Mapped[str] = mapped_column(String(100), nullable=False)  # 弹幕文本 (最多100字符)

    # 弹幕位置和样式
    time: Mapped[float] = mapped_column(Float, nullable=False, index=True)  # 出现时间 (秒)
    type: Mapped[DanmakuType] = mapped_column(
        SQLEnum(DanmakuType), default=DanmakuType.SCROLL, nullable=False
    )  # 弹幕类型
    color: Mapped[str] = mapped_column(String(7), default="#FFFFFF", nullable=False)  # 颜色 (十六进制)
    font_size: Mapped[int] = mapped_column(Integer, default=25, nullable=False)  # 字体大小

    # 审核相关
    status: Mapped[DanmakuStatus] = mapped_column(
        SQLEnum(DanmakuStatus),
        default=DanmakuStatus.APPROVED,
        nullable=False,
        index=True,
    )
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否被屏蔽

    # 审核信息
    reviewed_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reject_reason: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # 拒绝原因

    # 用户报告
    report_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 被举报次数

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    video: Mapped[Video] = relationship("Video", back_populates="danmaku_list")
    user: Mapped[User] = relationship("User", back_populates="danmaku_list")
    reviewer: Mapped[Optional[AdminUser]] = relationship("AdminUser", foreign_keys=[reviewed_by])

    def __repr__(self):
        return f"<Danmaku(id={self.id}, video_id={self.video_id}, time={self.time}, content='{self.content[:20]}...')>"


class BlockedWord(Base):
    """屏蔽词模型"""

    __tablename__ = "blocked_words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    word: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)  # 屏蔽词
    is_regex: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否为正则表达式
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # 关系
    creator: Mapped[Optional[AdminUser]] = relationship("AdminUser", foreign_keys=[created_by])

    def __repr__(self):
        return f"<BlockedWord(id={self.id}, word='{self.word}')>"
