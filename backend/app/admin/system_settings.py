from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from app.models.user import AdminUser
from app.models.settings import SystemSettings
from app.admin.auth import get_current_admin_user

router = APIRouter()


# Pydantic schemas
class SystemSettingsBase(BaseModel):
    # 网站基本信息
    site_name: str = "视频网站"
    site_url: str = "http://localhost:3000"
    site_description: Optional[str] = None
    site_keywords: Optional[str] = None
    site_logo: Optional[str] = None
    site_favicon: Optional[str] = None

    # SEO设置
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None

    # 上传设置
    upload_max_size: int = 1024  # MB
    upload_allowed_formats: List[str] = ["mp4", "avi", "mkv", "webm", "flv"]
    image_max_size: int = 10  # MB
    image_allowed_formats: List[str] = ["jpg", "jpeg", "png", "webp", "gif"]

    # 视频设置
    video_auto_approve: bool = False
    video_require_review: bool = True
    video_default_quality: str = "720p"
    video_enable_transcode: bool = True
    video_transcode_formats: List[str] = ["720p", "1080p"]

    # 评论设置
    comment_enable: bool = True
    comment_require_approval: bool = False
    comment_allow_guest: bool = False
    comment_max_length: int = 500

    # 用户设置
    user_enable_registration: bool = True
    user_require_email_verification: bool = True
    user_default_avatar: Optional[str] = None
    user_max_favorites: int = 1000

    # 安全设置
    security_enable_captcha: bool = True
    security_login_max_attempts: int = 5
    security_login_lockout_duration: int = 30  # 分钟
    security_session_timeout: int = 7200  # 秒

    # 其他设置
    maintenance_mode: bool = False
    maintenance_message: Optional[str] = None
    analytics_code: Optional[str] = None
    custom_css: Optional[str] = None
    custom_js: Optional[str] = None


class SystemSettingsUpdate(SystemSettingsBase):
    pass


class SystemSettingsResponse(SystemSettingsBase):
    id: int

    class Config:
        from_attributes = True


@router.get("/settings", response_model=SystemSettingsResponse)
async def get_system_settings(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取系统设置"""
    result = await db.execute(select(SystemSettings).limit(1))
    settings = result.scalar_one_or_none()

    if not settings:
        # 如果没有设置记录，创建默认设置
        settings = SystemSettings(
            site_name="视频网站",
            site_url="http://localhost:3000",
            upload_max_size=1024,
            upload_allowed_formats=["mp4", "avi", "mkv", "webm", "flv"],
            image_max_size=10,
            image_allowed_formats=["jpg", "jpeg", "png", "webp", "gif"],
            video_auto_approve=False,
            video_require_review=True,
            video_default_quality="720p",
            video_enable_transcode=True,
            video_transcode_formats=["720p", "1080p"],
            comment_enable=True,
            comment_require_approval=False,
            comment_allow_guest=False,
            comment_max_length=500,
            user_enable_registration=True,
            user_require_email_verification=True,
            user_max_favorites=1000,
            security_enable_captcha=True,
            security_login_max_attempts=5,
            security_login_lockout_duration=30,
            security_session_timeout=7200,
            maintenance_mode=False,
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)

    return settings


@router.put("/settings", response_model=SystemSettingsResponse)
async def update_system_settings(
    settings_update: SystemSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """更新系统设置"""
    result = await db.execute(select(SystemSettings).limit(1))
    settings = result.scalar_one_or_none()

    if not settings:
        # 创建新设置
        settings = SystemSettings(**settings_update.model_dump())
        db.add(settings)
    else:
        # 更新现有设置
        for key, value in settings_update.model_dump().items():
            setattr(settings, key, value)

    await db.commit()
    await db.refresh(settings)

    return settings


@router.post("/settings/reset")
async def reset_system_settings(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """重置系统设置为默认值"""
    if current_admin.role != "superadmin":
        raise HTTPException(status_code=403, detail="Only superadmin can reset settings")

    result = await db.execute(select(SystemSettings).limit(1))
    settings = result.scalar_one_or_none()

    if settings:
        await db.delete(settings)
        await db.commit()

    # 创建默认设置
    default_settings = SystemSettings(
        site_name="视频网站",
        site_url="http://localhost:3000",
        upload_max_size=1024,
        upload_allowed_formats=["mp4", "avi", "mkv", "webm", "flv"],
        image_max_size=10,
        image_allowed_formats=["jpg", "jpeg", "png", "webp", "gif"],
        video_auto_approve=False,
        video_require_review=True,
        video_default_quality="720p",
        video_enable_transcode=True,
        video_transcode_formats=["720p", "1080p"],
        comment_enable=True,
        comment_require_approval=False,
        comment_allow_guest=False,
        comment_max_length=500,
        user_enable_registration=True,
        user_require_email_verification=True,
        user_max_favorites=1000,
        security_enable_captcha=True,
        security_login_max_attempts=5,
        security_login_lockout_duration=30,
        security_session_timeout=7200,
        maintenance_mode=False,
    )
    db.add(default_settings)
    await db.commit()
    await db.refresh(default_settings)

    return {"message": "System settings reset to default", "settings": default_settings}
