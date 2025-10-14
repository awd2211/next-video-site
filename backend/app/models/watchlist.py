"""
Watchlist model for "My List" feature (like Netflix)
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.video import Video


class Watchlist(Base):
    """
    User's watchlist (My List)
    Users can add videos they want to watch later
    """

    __tablename__ = "watchlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    video_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="User's custom sort order"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Unique constraint: one user can add one video only once
    __table_args__ = (UniqueConstraint("user_id", "video_id", name="uq_user_video_watchlist"),)

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="watchlist")
    video: Mapped[Video] = relationship("Video", back_populates="watchlist")
