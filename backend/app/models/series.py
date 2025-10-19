"""
视频专辑/系列模型
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
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.season import Season
    from app.models.user import AdminUser
    from app.models.video import Video


class SeriesType(str, enum.Enum):
    """专辑类型"""

    SERIES = "series"  # 系列剧 (连续剧集)
    COLLECTION = "collection"  # 合集 (主题合集)
    FRANCHISE = "franchise"  # 系列作品 (如电影系列)


class SeriesStatus(str, enum.Enum):
    """专辑状态"""

    DRAFT = "draft"  # 草稿
    PUBLISHED = "published"  # 已发布
    ARCHIVED = "archived"  # 已归档


# 专辑与视频的关联表
series_videos = Table(
    "series_videos",
    Base.metadata,
    Column(
        "series_id",
        Integer,
        ForeignKey("series.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "video_id",
        Integer,
        ForeignKey("videos.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("episode_number", Integer, nullable=True, comment="集数/顺序"),
    Column("added_at", DateTime(timezone=True), server_default=func.now()),
)


class Series(Base):
    """视频专辑/系列"""

    __tablename__ = "series"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True, comment="专辑标题")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="专辑描述")
    cover_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="封面图")
    type: Mapped[SeriesType] = mapped_column(
        SQLEnum(SeriesType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=SeriesType.SERIES,
        index=True,
        comment="专辑类型",
    )
    status: Mapped[SeriesStatus] = mapped_column(
        SQLEnum(SeriesStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=SeriesStatus.DRAFT,
        index=True,
        comment="发布状态",
    )

    # 统计字段
    total_episodes: Mapped[int] = mapped_column(Integer, default=0, comment="总集数")
    total_views: Mapped[int] = mapped_column(Integer, default=0, comment="总播放量")
    total_favorites: Mapped[int] = mapped_column(Integer, default=0, comment="总收藏数")

    # 排序和推荐
    display_order: Mapped[int] = mapped_column(Integer, default=0, index=True, comment="显示顺序")
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, index=True, comment="是否推荐")

    # 元数据
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # 关系
    videos: Mapped[list[Video]] = relationship("Video", secondary=series_videos, back_populates="series")
    creator: Mapped[Optional[AdminUser]] = relationship("AdminUser", foreign_keys=[created_by])
    # 🆕 Season-Episode 架构支持
    seasons: Mapped[list["Season"]] = relationship(
        "Season",
        back_populates="series",
        cascade="all, delete-orphan",
        order_by="Season.season_number",
    )

    def __repr__(self):
        return f"<Series {self.id}: {self.title}>"
