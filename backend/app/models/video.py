from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.comment import Comment, Rating
    from app.models.content import Report
    from app.models.danmaku import Danmaku
    from app.models.episode import Episode
    from app.models.series import Series
    from app.models.share import VideoShare
    from app.models.user_activity import Favorite, WatchHistory
    from app.models.watchlist import Watchlist


class VideoType(str, enum.Enum):
    """Video type enum"""

    MOVIE = "movie"
    TV_SERIES = "tv_series"
    ANIME = "anime"
    DOCUMENTARY = "documentary"


class VideoStatus(str, enum.Enum):
    """Video status enum"""

    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class Country(Base):
    """Country/Region model"""

    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment='中文名称')
    name_en: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment='英文名称')
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)  # ISO code
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    videos: Mapped[list[Video]] = relationship("Video", back_populates="country")


class Category(Base):
    """Category model"""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment='中文名称')
    name_en: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment='英文名称')
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment='中文描述')
    description_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment='英文描述')
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    parent: Mapped[Optional[Category]] = relationship("Category", remote_side=[id], backref="children")
    video_categories: Mapped[list[VideoCategory]] = relationship("VideoCategory", back_populates="category")


class Tag(Base):
    """Tag model"""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment='中文名称')
    name_en: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment='英文名称')
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    video_tags: Mapped[list[VideoTag]] = relationship("VideoTag", back_populates="tag")


class Actor(Base):
    """Actor model"""

    __tablename__ = "actors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    biography: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    birth_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    country_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("countries.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    video_actors: Mapped[list[VideoActor]] = relationship("VideoActor", back_populates="actor")


class Director(Base):
    """Director model"""

    __tablename__ = "directors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    biography: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    birth_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    country_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("countries.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    video_directors: Mapped[list[VideoDirector]] = relationship("VideoDirector", back_populates="director")


class Video(Base):
    """Video model"""

    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    original_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    slug: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    video_type: Mapped[VideoType] = mapped_column(Enum(VideoType), nullable=False, default=VideoType.MOVIE)
    status: Mapped[VideoStatus] = mapped_column(
        Enum(VideoStatus), nullable=False, default=VideoStatus.DRAFT, index=True
    )

    # Media files
    video_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    trailer_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    poster_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    backdrop_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # 🆕 Video Hash fields (for duplicate detection)
    file_hash_md5: Mapped[Optional[str]] = mapped_column(String(32), index=True, nullable=True, comment="完整文件MD5哈希")
    partial_hash: Mapped[Optional[str]] = mapped_column(String(32), index=True, nullable=True, comment="部分内容哈希(头+尾)")
    metadata_hash: Mapped[Optional[str]] = mapped_column(String(32), index=True, nullable=True, comment="元数据哈希(标题+时长+大小)")

    # AV1 support (新增)
    av1_master_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="AV1 HLS master playlist URL")
    av1_resolutions: Mapped[dict[str, Any]] = mapped_column(JSONB, default={}, comment="AV1分辨率URL映射")
    is_av1_available: Mapped[bool] = mapped_column(
        Boolean, default=False, index=True, comment="是否有AV1版本"
    )
    av1_file_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True, comment="AV1文件总大小(字节)")
    h264_file_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True, comment="H.264文件大小(对比用)")

    # 🆕 Transcode status tracking
    transcode_status: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="转码状态: pending, processing, completed, failed",
    )
    transcode_progress: Mapped[int] = mapped_column(Integer, default=0, comment="转码进度 0-100")
    transcode_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="转码错误信息")
    h264_transcode_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="H.264转码完成时间"
    )
    av1_transcode_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="AV1转码完成时间"
    )

    # Metadata
    release_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    release_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # in minutes
    country_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("countries.id", ondelete="SET NULL"), nullable=True
    )
    language: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    subtitle_languages: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # JSON array as string

    # Series info (for TV series)
    total_seasons: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_episodes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    series_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # ongoing, completed

    # 🆕 Episode numbering (for TV series without seasons, e.g., Chinese dramas)
    absolute_episode_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
        comment="绝对集数（用于不分季的剧集，如第25集）。有 Season/Episode 架构的剧集不使用此字段。"
    )

    # Statistics
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    favorite_count: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    average_rating: Mapped[float] = mapped_column(Float, default=0.0)
    rating_count: Mapped[int] = mapped_column(Integer, default=0)

    # SEO
    meta_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_keywords: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # 全文搜索向量（由数据库触发器自动维护）
    search_vector: Mapped[Optional[Any]] = mapped_column(TSVECTOR, nullable=True)

    # Admin fields
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, comment="推荐标记")
    is_recommended: Mapped[bool] = mapped_column(Boolean, default=False)
    is_trending: Mapped[bool] = mapped_column(Boolean, default=False, index=True, comment="热门标记")
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, index=True, comment="置顶标记")
    quality_score: Mapped[int] = mapped_column(Integer, default=0, comment="质量评分 0-100")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    scheduled_publish_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True, comment="定时发布时间"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    country: Mapped[Optional[Country]] = relationship("Country", back_populates="videos")
    video_categories: Mapped[list[VideoCategory]] = relationship(
        "VideoCategory", back_populates="video", cascade="all, delete-orphan"
    )
    video_tags: Mapped[list[VideoTag]] = relationship(
        "VideoTag", back_populates="video", cascade="all, delete-orphan"
    )
    video_actors: Mapped[list[VideoActor]] = relationship(
        "VideoActor", back_populates="video", cascade="all, delete-orphan"
    )
    video_directors: Mapped[list[VideoDirector]] = relationship(
        "VideoDirector", back_populates="video", cascade="all, delete-orphan"
    )
    comments: Mapped[list[Comment]] = relationship(
        "Comment", back_populates="video", cascade="all, delete-orphan"
    )
    ratings: Mapped[list[Rating]] = relationship(
        "Rating", back_populates="video", cascade="all, delete-orphan"
    )
    favorites: Mapped[list[Favorite]] = relationship(
        "Favorite", back_populates="video", cascade="all, delete-orphan"
    )
    watch_history: Mapped[list[WatchHistory]] = relationship(
        "WatchHistory", back_populates="video", cascade="all, delete-orphan"
    )
    reports: Mapped[list[Report]] = relationship(
        "Report", back_populates="video", cascade="all, delete-orphan"
    )
    danmaku_list: Mapped[list[Danmaku]] = relationship(
        "Danmaku", back_populates="video", cascade="all, delete-orphan"
    )  # 🆕 弹幕
    shares: Mapped[list[VideoShare]] = relationship(
        "VideoShare", back_populates="video", cascade="all, delete-orphan"
    )  # 🆕 分享
    series: Mapped[list[Series]] = relationship(
        "Series", secondary="series_videos", back_populates="videos"
    )  # 🆕 专辑/系列
    watchlist: Mapped[list[Watchlist]] = relationship(
        "Watchlist", back_populates="video", cascade="all, delete-orphan"
    )  # 🆕 待看列表 (My List)
    episode: Mapped[Optional["Episode"]] = relationship(
        "Episode", back_populates="video", uselist=False
    )  # 🆕 Season-Episode 架构（一对一关系）

    @property
    def compression_ratio(self) -> float:
        """计算AV1相对H.264的压缩率"""
        if self.h264_file_size and self.av1_file_size and self.h264_file_size > 0:
            return round((1 - self.av1_file_size / self.h264_file_size) * 100, 2)
        return 0.0

    @property
    def best_video_url(self) -> str:
        """返回最佳视频URL (优先AV1)"""
        if self.is_av1_available and self.av1_master_url:
            return self.av1_master_url
        return self.video_url or ""


# Association tables
class VideoCategory(Base):
    """Video-Category association"""

    __tablename__ = "video_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    video: Mapped[Video] = relationship("Video", back_populates="video_categories")
    category: Mapped[Category] = relationship("Category", back_populates="video_categories")


class VideoTag(Base):
    """Video-Tag association"""

    __tablename__ = "video_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    video: Mapped[Video] = relationship("Video", back_populates="video_tags")
    tag: Mapped[Tag] = relationship("Tag", back_populates="video_tags")


class VideoActor(Base):
    """Video-Actor association"""

    __tablename__ = "video_actors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    actor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("actors.id", ondelete="CASCADE"), nullable=False
    )
    role_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # Character name
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    video: Mapped[Video] = relationship("Video", back_populates="video_actors")
    actor: Mapped[Actor] = relationship("Actor", back_populates="video_actors")


class VideoDirector(Base):
    """Video-Director association"""

    __tablename__ = "video_directors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    director_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("directors.id", ondelete="CASCADE"), nullable=False
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    video: Mapped[Video] = relationship("Video", back_populates="video_directors")
    director: Mapped[Director] = relationship("Director", back_populates="video_directors")
