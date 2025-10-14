"""
Shared Watchlist model for list sharing feature
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
import secrets

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class SharedWatchlist(Base):
    """
    Shared watchlist for public sharing
    Users can generate a shareable link for their watchlist
    """

    __tablename__ = "shared_watchlists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    share_token: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, index=True, comment="Unique token for sharing"
    )
    title: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="Custom title for shared list"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Optional description"
    )
    video_ids: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Comma-separated video IDs"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="Whether the share link is active"
    )
    view_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="Number of views"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Optional expiration date"
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="shared_watchlists")

    @staticmethod
    def generate_share_token() -> str:
        """Generate a unique share token"""
        return secrets.token_urlsafe(24)
