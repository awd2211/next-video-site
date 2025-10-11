import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class BannerStatus(str, enum.Enum):
    """Banner status enum"""

    ACTIVE = "active"
    INACTIVE = "inactive"


class ReportStatus(str, enum.Enum):
    """Report status enum"""

    PENDING = "pending"
    PROCESSED = "processed"
    REJECTED = "rejected"


class Banner(Base):
    """Banner/Carousel model"""

    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    image_url = Column(String(500), nullable=False)
    link_url = Column(String(500), nullable=True)
    video_id = Column(
        Integer, ForeignKey("videos.id", ondelete="SET NULL"), nullable=True
    )
    description = Column(Text, nullable=True)
    status = Column(Enum(BannerStatus), nullable=False, default=BannerStatus.ACTIVE)
    sort_order = Column(Integer, default=0, index=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Recommendation(Base):
    """Recommendation position model"""

    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    position = Column(String(50), nullable=False)  # home_top, home_trending, etc.
    video_id = Column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    sort_order = Column(Integer, default=0, index=True)
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Announcement(Base):
    """Announcement model"""

    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String(50), default="info")  # info, warning, success, error
    is_active = Column(Boolean, default=True)
    is_pinned = Column(Boolean, default=False)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Report(Base):
    """User report model"""

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    video_id = Column(
        Integer, ForeignKey("videos.id", ondelete="SET NULL"), nullable=True
    )
    comment_id = Column(
        Integer, ForeignKey("comments.id", ondelete="SET NULL"), nullable=True
    )
    reason = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        Enum(ReportStatus), nullable=False, default=ReportStatus.PENDING, index=True
    )
    admin_note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="reports")
    video = relationship("Video", back_populates="reports")
