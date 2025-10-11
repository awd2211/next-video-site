from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class SystemSettings(Base):
    """系统设置表"""

    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 网站基本信息
    site_name: Mapped[str] = mapped_column(String(100), nullable=False, default="视频网站")
    site_url: Mapped[str] = mapped_column(String(255), nullable=False, default="http://localhost:3000")
    site_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    site_keywords: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    site_logo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    site_favicon: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # SEO设置
    seo_title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    seo_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    seo_keywords: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # 上传设置
    upload_max_size: Mapped[int] = mapped_column(Integer, nullable=False, default=1024)  # MB
    upload_allowed_formats: Mapped[list[Any]] = mapped_column(
        JSON, nullable=False, default=list
    )  # ["mp4", "avi", "mkv"]
    image_max_size: Mapped[int] = mapped_column(Integer, nullable=False, default=10)  # MB
    image_allowed_formats: Mapped[list[Any]] = mapped_column(
        JSON, nullable=False, default=list
    )  # ["jpg", "png", "webp"]

    # 视频设置
    video_auto_approve: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    video_require_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    video_default_quality: Mapped[str] = mapped_column(String(20), nullable=False, default="720p")
    video_enable_transcode: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    video_transcode_formats: Mapped[list[Any]] = mapped_column(
        JSON, nullable=False, default=list
    )  # ["720p", "1080p"]

    # 评论设置
    comment_enable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    comment_require_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    comment_allow_guest: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    comment_max_length: Mapped[int] = mapped_column(Integer, nullable=False, default=500)

    # 用户设置
    user_enable_registration: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    user_require_email_verification: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    user_default_avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    user_max_favorites: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)

    # 安全设置
    security_enable_captcha: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    security_login_max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    security_login_lockout_duration: Mapped[int] = mapped_column(
        Integer, nullable=False, default=30
    )  # 分钟
    security_session_timeout: Mapped[int] = mapped_column(Integer, nullable=False, default=7200)  # 秒

    # 其他设置
    maintenance_mode: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    maintenance_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    analytics_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Google Analytics等
    custom_css: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    custom_js: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
