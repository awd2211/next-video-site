from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.admin import OperationLog, Role
    from app.models.comment import Comment, Rating
    from app.models.content import Report
    from app.models.dashboard import DashboardLayout
    from app.models.danmaku import Danmaku
    from app.models.favorite_folder import FavoriteFolder
    from app.models.media import Media
    from app.models.share import VideoShare
    from app.models.shared_watchlist import SharedWatchlist
    from app.models.user_activity import Favorite, SearchHistory, WatchHistory
    from app.models.watchlist import Watchlist


class User(Base):
    """User model for regular users"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255))  # Optional for OAuth users
    full_name: Mapped[Optional[str]] = mapped_column(String(200))
    avatar: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_vip: Mapped[bool] = mapped_column(Boolean, default=False)
    vip_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # OAuth fields
    oauth_provider: Mapped[Optional[str]] = mapped_column(String(50))  # google, facebook, etc.
    oauth_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)  # Provider's user ID
    oauth_email: Mapped[Optional[str]] = mapped_column(String(255))  # Email from OAuth provider
    oauth_avatar: Mapped[Optional[str]] = mapped_column(String(500))  # Avatar URL from OAuth provider

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    comments: Mapped[list[Comment]] = relationship(
        "Comment", back_populates="user", cascade="all, delete-orphan"
    )
    ratings: Mapped[list[Rating]] = relationship(
        "Rating", back_populates="user", cascade="all, delete-orphan"
    )
    favorites: Mapped[list[Favorite]] = relationship(
        "Favorite", back_populates="user", cascade="all, delete-orphan"
    )
    favorite_folders: Mapped[list[FavoriteFolder]] = relationship(
        "FavoriteFolder", back_populates="user", cascade="all, delete-orphan"
    )  # 🆕 收藏夹分组
    watch_history: Mapped[list[WatchHistory]] = relationship(
        "WatchHistory", back_populates="user", cascade="all, delete-orphan"
    )
    search_history: Mapped[list[SearchHistory]] = relationship(
        "SearchHistory", back_populates="user", cascade="all, delete-orphan"
    )  # 🆕 搜索历史
    reports: Mapped[list[Report]] = relationship(
        "Report", back_populates="user", cascade="all, delete-orphan"
    )
    danmaku_list: Mapped[list[Danmaku]] = relationship(
        "Danmaku", back_populates="user", cascade="all, delete-orphan"
    )  # 🆕 弹幕
    shares: Mapped[list[VideoShare]] = relationship(
        "VideoShare", back_populates="user", cascade="all, delete-orphan"
    )  # 🆕 分享
    watchlist: Mapped[list[Watchlist]] = relationship(
        "Watchlist", back_populates="user", cascade="all, delete-orphan"
    )  # 🆕 待看列表 (My List)
    shared_watchlists: Mapped[list[SharedWatchlist]] = relationship(
        "SharedWatchlist", back_populates="user", cascade="all, delete-orphan"
    )  # 🆕 分享的待看列表


class AdminUser(Base):
    """Admin user model with role-based access control"""

    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(200))
    avatar: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superadmin: Mapped[bool] = mapped_column(Boolean, default=False)
    role_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True
    )

    # 2FA (Two-Factor Authentication) fields
    totp_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    totp_secret: Mapped[Optional[str]] = mapped_column(String(500))  # Encrypted TOTP secret
    backup_codes: Mapped[Optional[str]] = mapped_column(String(2000))  # JSON array of encrypted backup codes
    totp_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    role: Mapped[Optional[Role]] = relationship("Role", back_populates="admin_users")
    operation_logs: Mapped[list[OperationLog]] = relationship(
        "OperationLog", back_populates="admin_user", cascade="all, delete-orphan"
    )
    uploaded_media: Mapped[list["Media"]] = relationship(
        "Media", back_populates="uploader", cascade="all, delete-orphan"
    )
    dashboard_layout: Mapped[Optional[DashboardLayout]] = relationship(
        "DashboardLayout", back_populates="admin_user", uselist=False, cascade="all, delete-orphan"
    )
