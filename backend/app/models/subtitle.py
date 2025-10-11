import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class SubtitleFormat(str, enum.Enum):
    """Subtitle format enum"""

    SRT = "srt"  # SubRip
    VTT = "vtt"  # WebVTT (HTML5标准)
    ASS = "ass"  # Advanced SubStation Alpha


class Subtitle(Base):
    """Subtitle model"""

    __tablename__ = "subtitles"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    language = Column(
        String(50), nullable=False, index=True
    )  # 语言代码 (zh-CN, en-US, ja, ko)
    language_name = Column(String(100), nullable=False)  # 语言名称 (简体中文, English)
    file_url = Column(String(1000), nullable=False)  # 字幕文件URL
    format = Column(String(20), nullable=False)  # 字幕格式 (srt, vtt, ass)
    is_default = Column(Boolean, default=False, nullable=False)  # 是否默认字幕
    is_auto_generated = Column(Boolean, default=False, nullable=False)  # 是否AI自动生成
    sort_order = Column(Integer, default=0)  # 排序顺序
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    video = relationship("Video", backref="subtitles")

    # 唯一约束 (同一视频不能有重复语言的字幕)
    __table_args__ = (
        UniqueConstraint("video_id", "language", name="uq_video_language"),
    )
