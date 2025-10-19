"""
电视剧单集管理模型

Episode 模型代表一季中的单个剧集，核心功能：
- 连接 Season 和 Video（一个视频文件对应一集）
- 片头片尾时间标记（支持"跳过片头"功能）
- 独立的权限控制（免费集、VIP集）
- 下集预告管理
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
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
    from app.models.season import Season
    from app.models.video import Video


class EpisodeStatus(str, enum.Enum):
    """单集发布状态"""

    DRAFT = "draft"  # 草稿
    PUBLISHED = "published"  # 已发布
    ARCHIVED = "archived"  # 已归档


class Episode(Base):
    """
    电视剧单集模型

    代表一季中的某一集（如《权力的游戏》第1季第1集）
    关联到实际的视频文件，提供元数据和权限控制
    """

    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # ==================== 关联关系 ====================
    season_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("seasons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属季度ID",
    )
    video_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # 一个视频只能属于一个Episode
        index=True,
        comment="关联的视频文件ID",
    )

    # ==================== 集数信息 ====================
    episode_number: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="集数（本季内的第几集，如第1集）"
    )
    title: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="单集标题，如'凛冬将至'"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="单集简介"
    )

    # ==================== 片头片尾时间标记（秒） ====================
    # 用于"跳过片头"、"跳过片尾"功能
    intro_start: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="片头开始时间（秒）"
    )
    intro_end: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="片头结束时间（秒）"
    )
    credits_start: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="片尾开始时间（秒），用于自动跳到下一集"
    )

    # ==================== 预告片 ====================
    next_episode_preview_url: Mapped[Optional[str]] = mapped_column(
        String(1000), nullable=True, comment="下集预告视频URL"
    )
    preview_duration: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="预告时长（秒）"
    )

    # ==================== 权限控制 ====================
    is_free: Mapped[bool] = mapped_column(
        Boolean, default=False, index=True, comment="是否免费（用于'前N集免费'策略）"
    )
    vip_required: Mapped[bool] = mapped_column(
        Boolean, default=False, index=True, comment="是否需要VIP会员"
    )

    # ==================== 发布状态 ====================
    status: Mapped[EpisodeStatus] = mapped_column(
        SQLEnum(EpisodeStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=EpisodeStatus.DRAFT,
        index=True,
        comment="发布状态",
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="实际发布时间"
    )
    release_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="计划上线时间"
    )

    # ==================== 统计字段 ====================
    view_count: Mapped[int] = mapped_column(Integer, default=0, comment="观看量")
    like_count: Mapped[int] = mapped_column(Integer, default=0, comment="点赞数")
    comment_count: Mapped[int] = mapped_column(Integer, default=0, comment="评论数")

    # ==================== 排序与推荐 ====================
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, comment="排序权重（通常按episode_number排序）"
    )
    is_featured: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否推荐本集"
    )

    # ==================== 审计字段 ====================
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # ==================== 关系映射 ====================
    season: Mapped["Season"] = relationship("Season", back_populates="episodes")
    video: Mapped["Video"] = relationship("Video", back_populates="episode")

    # ==================== 约束 ====================
    __table_args__ = (
        UniqueConstraint(
            "season_id", "episode_number", name="uq_season_episode_number"
        ),
    )

    def __repr__(self):
        return f"<Episode(id={self.id}, season_id={self.season_id}, episode_number={self.episode_number}, title='{self.title}')>"

    @property
    def display_name(self) -> str:
        """
        显示名称（如：第1集）
        """
        return f"第{self.episode_number}集"

    @property
    def full_display_name(self) -> str:
        """
        完整显示名称（如：第1集 - 凛冬将至）
        """
        return f"第{self.episode_number}集 - {self.title}"

    @property
    def has_intro_markers(self) -> bool:
        """是否设置了片头时间标记"""
        return self.intro_start is not None and self.intro_end is not None

    @property
    def has_credits_marker(self) -> bool:
        """是否设置了片尾时间标记"""
        return self.credits_start is not None

    @property
    def intro_duration(self) -> int:
        """片头时长（秒）"""
        if self.has_intro_markers:
            return self.intro_end - self.intro_start
        return 0

    @property
    def is_published(self) -> bool:
        """是否已发布"""
        return self.status == EpisodeStatus.PUBLISHED

    @property
    def requires_subscription(self) -> bool:
        """是否需要订阅/VIP（用于前端权限判断）"""
        return self.vip_required and not self.is_free
