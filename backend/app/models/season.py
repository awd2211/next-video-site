"""
电视剧季度管理模型

Season 模型提供了"剧集-季-集"三层架构的中间层，支持：
- 分季发布控制
- VIP权限管理
- 独立的封面和描述
- 统计数据聚合
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.episode import Episode
    from app.models.series import Series


class SeasonStatus(str, enum.Enum):
    """季度发布状态"""

    DRAFT = "draft"  # 草稿
    PUBLISHED = "published"  # 已发布
    ARCHIVED = "archived"  # 已归档


class Season(Base):
    """
    电视剧季度模型

    代表一部剧集的某一季（如《权力的游戏》第1季）
    管理该季下的所有集（Episodes）
    """

    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # ==================== 关联关系 ====================
    series_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("series.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属剧集ID",
    )

    # ==================== 基本信息 ====================
    season_number: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="季数（第1季、第2季...）"
    )
    title: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="季标题，如'第一季：凛冬将至'"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="季简介"
    )

    # ==================== 发布控制 ====================
    status: Mapped[SeasonStatus] = mapped_column(
        SQLEnum(SeasonStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=SeasonStatus.DRAFT,
        index=True,
        comment="发布状态",
    )
    release_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="上线时间"
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="实际发布时间"
    )

    # ==================== 权限控制 ====================
    vip_required: Mapped[bool] = mapped_column(
        Boolean, default=False, index=True, comment="是否需要VIP会员"
    )

    # ==================== 媒体资源 ====================
    poster_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="季封面图URL"
    )
    backdrop_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="季背景图URL"
    )
    trailer_url: Mapped[Optional[str]] = mapped_column(
        String(1000), nullable=True, comment="季预告片URL"
    )

    # ==================== 统计字段 ====================
    total_episodes: Mapped[int] = mapped_column(
        Integer, default=0, comment="总集数（自动计算）"
    )
    total_duration: Mapped[int] = mapped_column(
        Integer, default=0, comment="总时长（分钟，自动计算）"
    )
    view_count: Mapped[int] = mapped_column(Integer, default=0, comment="季总观看量")
    favorite_count: Mapped[int] = mapped_column(Integer, default=0, comment="季总收藏数")
    average_rating: Mapped[float] = mapped_column(
        Float, default=0.0, comment="季平均评分"
    )

    # ==================== 推荐与排序 ====================
    is_featured: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否推荐"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, comment="排序权重（数字越大越靠前）"
    )

    # ==================== 审计字段 ====================
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # ==================== 关系映射 ====================
    series: Mapped["Series"] = relationship("Series", back_populates="seasons")
    episodes: Mapped[list["Episode"]] = relationship(
        "Episode",
        back_populates="season",
        cascade="all, delete-orphan",
        order_by="Episode.episode_number",
    )

    # ==================== 约束 ====================
    __table_args__ = (
        UniqueConstraint(
            "series_id", "season_number", name="uq_series_season_number"
        ),
    )

    def __repr__(self):
        return f"<Season(id={self.id}, series_id={self.series_id}, season_number={self.season_number}, title='{self.title}')>"

    @property
    def display_name(self) -> str:
        """显示名称（如：第1季）"""
        return f"第{self.season_number}季"

    @property
    def is_published(self) -> bool:
        """是否已发布"""
        return self.status == SeasonStatus.PUBLISHED

    @property
    def completion_rate(self) -> float:
        """
        完播率（如果有统计数据）

        完播率 = 完整观看人数 / 开始观看人数
        需要配合 EpisodeAnalytics 使用
        """
        # 这里返回占位值，实际计算需要查询 EpisodeAnalytics 表
        return 0.0
