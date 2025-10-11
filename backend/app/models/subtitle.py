from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.video import Video


class SubtitleFormat(str, enum.Enum):
    """Subtitle format enum"""

    SRT = "srt"  # SubRip
    VTT = "vtt"  # WebVTT (HTML5标准)
    ASS = "ass"  # Advanced SubStation Alpha


class Subtitle(Base):
    """Subtitle model"""

    __tablename__ = "subtitles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    language: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # 语言代码 (zh-CN, en-US, ja, ko)
    language_name: Mapped[str] = mapped_column(String(100), nullable=False)  # 语言名称 (简体中文, English)
    file_url: Mapped[str] = mapped_column(String(1000), nullable=False)  # 字幕文件URL
    format: Mapped[str] = mapped_column(String(20), nullable=False)  # 字幕格式 (srt, vtt, ass)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否默认字幕
    is_auto_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否AI自动生成
    sort_order: Mapped[int] = mapped_column(Integer, default=0)  # 排序顺序
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    video: Mapped[Video] = relationship("Video", backref="subtitles")

    # 唯一约束 (同一视频不能有重复语言的字幕)
    __table_args__ = (
        UniqueConstraint("video_id", "language", name="uq_video_language"),
    )
