from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class SystemSettings(Base):
    """系统设置表"""

    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)

    # 网站基本信息
    site_name = Column(String(100), nullable=False, default="视频网站")
    site_url = Column(String(255), nullable=False, default="http://localhost:3000")
    site_description = Column(Text, nullable=True)
    site_keywords = Column(String(500), nullable=True)
    site_logo = Column(String(500), nullable=True)
    site_favicon = Column(String(500), nullable=True)

    # SEO设置
    seo_title = Column(String(100), nullable=True)
    seo_description = Column(Text, nullable=True)
    seo_keywords = Column(String(500), nullable=True)

    # 上传设置
    upload_max_size = Column(Integer, nullable=False, default=1024)  # MB
    upload_allowed_formats = Column(
        JSON, nullable=False, default=list
    )  # ["mp4", "avi", "mkv"]
    image_max_size = Column(Integer, nullable=False, default=10)  # MB
    image_allowed_formats = Column(
        JSON, nullable=False, default=list
    )  # ["jpg", "png", "webp"]

    # 视频设置
    video_auto_approve = Column(Boolean, nullable=False, default=False)
    video_require_review = Column(Boolean, nullable=False, default=True)
    video_default_quality = Column(String(20), nullable=False, default="720p")
    video_enable_transcode = Column(Boolean, nullable=False, default=True)
    video_transcode_formats = Column(
        JSON, nullable=False, default=list
    )  # ["720p", "1080p"]

    # 评论设置
    comment_enable = Column(Boolean, nullable=False, default=True)
    comment_require_approval = Column(Boolean, nullable=False, default=False)
    comment_allow_guest = Column(Boolean, nullable=False, default=False)
    comment_max_length = Column(Integer, nullable=False, default=500)

    # 用户设置
    user_enable_registration = Column(Boolean, nullable=False, default=True)
    user_require_email_verification = Column(Boolean, nullable=False, default=True)
    user_default_avatar = Column(String(500), nullable=True)
    user_max_favorites = Column(Integer, nullable=False, default=1000)

    # 安全设置
    security_enable_captcha = Column(Boolean, nullable=False, default=True)
    security_login_max_attempts = Column(Integer, nullable=False, default=5)
    security_login_lockout_duration = Column(
        Integer, nullable=False, default=30
    )  # 分钟
    security_session_timeout = Column(Integer, nullable=False, default=7200)  # 秒

    # 其他设置
    maintenance_mode = Column(Boolean, nullable=False, default=False)
    maintenance_message = Column(Text, nullable=True)
    analytics_code = Column(Text, nullable=True)  # Google Analytics等
    custom_css = Column(Text, nullable=True)
    custom_js = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
