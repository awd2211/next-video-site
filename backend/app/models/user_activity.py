from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.favorite_folder import FavoriteFolder
    from app.models.user import User
    from app.models.video import Video


class Favorite(Base):
    """User favorite videos"""

    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    folder_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("favorite_folders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )  # 🆕 收藏夹分组
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="favorites")
    video: Mapped[Video] = relationship("Video", back_populates="favorites")
    folder: Mapped[Optional[FavoriteFolder]] = relationship(
        "FavoriteFolder", back_populates="favorites"
    )  # 🆕 关联收藏夹


class WatchHistory(Base):
    """User watch history"""

    __tablename__ = "watch_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    watch_duration: Mapped[int] = mapped_column(Integer, default=0)  # in seconds
    last_position: Mapped[int] = mapped_column(Integer, default=0)  # in seconds
    is_completed: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), index=True
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="watch_history")
    video: Mapped[Video] = relationship("Video", back_populates="watch_history")


class SearchHistory(Base):
    """User search history for analytics and personalization"""

    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,  # Allow anonymous searches
        index=True,
    )
    query: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    results_count: Mapped[int] = mapped_column(Integer, default=0)
    clicked_video_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("videos.id", ondelete="SET NULL"), nullable=True
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True
    )  # IPv6 support
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    # Relationships
    user: Mapped[Optional[User]] = relationship("User", back_populates="search_history")
    clicked_video: Mapped[Optional[Video]] = relationship("Video")
