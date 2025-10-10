from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean, Enum, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class VideoType(str, enum.Enum):
    """Video type enum"""
    MOVIE = "movie"
    TV_SERIES = "tv_series"
    ANIME = "anime"
    DOCUMENTARY = "documentary"


class VideoStatus(str, enum.Enum):
    """Video status enum"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Country(Base):
    """Country/Region model"""

    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(10), unique=True, nullable=False)  # ISO code
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    videos = relationship("Video", back_populates="country")


class Category(Base):
    """Category model"""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    parent = relationship("Category", remote_side=[id], backref="children")
    video_categories = relationship("VideoCategory", back_populates="category")


class Tag(Base):
    """Tag model"""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    video_tags = relationship("VideoTag", back_populates="tag")


class Actor(Base):
    """Actor model"""

    __tablename__ = "actors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    avatar = Column(String(500), nullable=True)
    biography = Column(Text, nullable=True)
    birth_date = Column(DateTime(timezone=True), nullable=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    video_actors = relationship("VideoActor", back_populates="actor")


class Director(Base):
    """Director model"""

    __tablename__ = "directors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    avatar = Column(String(500), nullable=True)
    biography = Column(Text, nullable=True)
    birth_date = Column(DateTime(timezone=True), nullable=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    video_directors = relationship("VideoDirector", back_populates="director")


class Video(Base):
    """Video model"""

    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    original_title = Column(String(500), nullable=True)
    slug = Column(String(500), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    video_type = Column(Enum(VideoType), nullable=False, default=VideoType.MOVIE)
    status = Column(Enum(VideoStatus), nullable=False, default=VideoStatus.DRAFT, index=True)

    # Media files
    video_url = Column(String(1000), nullable=True)
    trailer_url = Column(String(1000), nullable=True)
    poster_url = Column(String(500), nullable=True)
    backdrop_url = Column(String(500), nullable=True)

    # AV1 support (新增)
    av1_master_url = Column(Text, nullable=True, comment='AV1 HLS master playlist URL')
    av1_resolutions = Column(JSONB, default={}, comment='AV1分辨率URL映射')
    is_av1_available = Column(Boolean, default=False, index=True, comment='是否有AV1版本')
    av1_file_size = Column(BigInteger, nullable=True, comment='AV1文件总大小(字节)')
    h264_file_size = Column(BigInteger, nullable=True, comment='H.264文件大小(对比用)')

    # 🆕 Transcode status tracking
    transcode_status = Column(String(50), nullable=True, index=True, comment='转码状态: pending, processing, completed, failed')
    transcode_progress = Column(Integer, default=0, comment='转码进度 0-100')
    transcode_error = Column(Text, nullable=True, comment='转码错误信息')
    h264_transcode_at = Column(DateTime(timezone=True), nullable=True, comment='H.264转码完成时间')
    av1_transcode_at = Column(DateTime(timezone=True), nullable=True, comment='AV1转码完成时间')

    # Metadata
    release_year = Column(Integer, nullable=True, index=True)
    release_date = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, nullable=True)  # in minutes
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="SET NULL"), nullable=True)
    language = Column(String(50), nullable=True)
    subtitle_languages = Column(String(500), nullable=True)  # JSON array as string

    # Series info (for TV series)
    total_seasons = Column(Integer, nullable=True)
    total_episodes = Column(Integer, nullable=True)
    series_status = Column(String(50), nullable=True)  # ongoing, completed

    # Statistics
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)

    # SEO
    meta_title = Column(String(500), nullable=True)
    meta_description = Column(Text, nullable=True)
    meta_keywords = Column(String(500), nullable=True)

    # Admin fields
    is_featured = Column(Boolean, default=False)
    is_recommended = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    country = relationship("Country", back_populates="videos")
    video_categories = relationship("VideoCategory", back_populates="video", cascade="all, delete-orphan")
    video_tags = relationship("VideoTag", back_populates="video", cascade="all, delete-orphan")
    video_actors = relationship("VideoActor", back_populates="video", cascade="all, delete-orphan")
    video_directors = relationship("VideoDirector", back_populates="video", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="video", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="video", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="video", cascade="all, delete-orphan")
    watch_history = relationship("WatchHistory", back_populates="video", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="video", cascade="all, delete-orphan")
    danmaku_list = relationship("Danmaku", back_populates="video", cascade="all, delete-orphan")  # 🆕 弹幕
    shares = relationship("VideoShare", back_populates="video", cascade="all, delete-orphan")  # 🆕 分享

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
        return self.video_url or ''


# Association tables
class VideoCategory(Base):
    """Video-Category association"""

    __tablename__ = "video_categories"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    video = relationship("Video", back_populates="video_categories")
    category = relationship("Category", back_populates="video_categories")


class VideoTag(Base):
    """Video-Tag association"""

    __tablename__ = "video_tags"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    video = relationship("Video", back_populates="video_tags")
    tag = relationship("Tag", back_populates="video_tags")


class VideoActor(Base):
    """Video-Actor association"""

    __tablename__ = "video_actors"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    actor_id = Column(Integer, ForeignKey("actors.id", ondelete="CASCADE"), nullable=False)
    role_name = Column(String(200), nullable=True)  # Character name
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    video = relationship("Video", back_populates="video_actors")
    actor = relationship("Actor", back_populates="video_actors")


class VideoDirector(Base):
    """Video-Director association"""

    __tablename__ = "video_directors"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    director_id = Column(Integer, ForeignKey("directors.id", ondelete="CASCADE"), nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    video = relationship("Video", back_populates="video_directors")
    director = relationship("Director", back_populates="video_directors")
