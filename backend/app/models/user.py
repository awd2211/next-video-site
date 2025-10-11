from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """User model for regular users"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    avatar = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_vip = Column(Boolean, default=False)
    vip_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    comments = relationship(
        "Comment", back_populates="user", cascade="all, delete-orphan"
    )
    ratings = relationship(
        "Rating", back_populates="user", cascade="all, delete-orphan"
    )
    favorites = relationship(
        "Favorite", back_populates="user", cascade="all, delete-orphan"
    )
    favorite_folders = relationship(
        "FavoriteFolder", back_populates="user", cascade="all, delete-orphan"
    )  # 🆕 收藏夹分组
    watch_history = relationship(
        "WatchHistory", back_populates="user", cascade="all, delete-orphan"
    )
    reports = relationship(
        "Report", back_populates="user", cascade="all, delete-orphan"
    )
    danmaku_list = relationship(
        "Danmaku", back_populates="user", cascade="all, delete-orphan"
    )  # 🆕 弹幕
    shares = relationship(
        "VideoShare", back_populates="user", cascade="all, delete-orphan"
    )  # 🆕 分享


class AdminUser(Base):
    """Admin user model with role-based access control"""

    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    avatar = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_superadmin = Column(Boolean, default=False)
    role_id = Column(
        Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    role = relationship("Role", back_populates="admin_users")
    operation_logs = relationship(
        "OperationLog", back_populates="admin_user", cascade="all, delete-orphan"
    )
