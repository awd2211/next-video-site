from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.settings import SystemSettings
from app.models.user import AdminUser
from app.utils.cache import Cache
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


# Pydantic schemas
class SystemSettingsResponse(BaseModel):
    id: int
    # 网站基本信息
    site_name: str
    site_url: str
    site_description: Optional[str]
    site_keywords: Optional[str]
    site_logo: Optional[str]
    site_favicon: Optional[str]
    # SEO设置
    seo_title: Optional[str]
    seo_description: Optional[str]
    seo_keywords: Optional[str]
    # 上传设置
    upload_max_size: int
    upload_allowed_formats: List[str]
    image_max_size: int
    image_allowed_formats: List[str]
    # 视频设置
    video_auto_approve: bool
    video_require_review: bool
    video_default_quality: str
    video_enable_transcode: bool
    video_transcode_formats: List[str]
    # 评论设置
    comment_enable: bool
    comment_require_approval: bool
    comment_allow_guest: bool
    comment_max_length: int
    # 用户设置
    user_enable_registration: bool
    user_require_email_verification: bool
    user_default_avatar: Optional[str]
    user_max_favorites: int
    # 安全设置
    security_enable_captcha: bool
    security_login_max_attempts: int
    security_login_lockout_duration: int
    security_session_timeout: int
    # 其他设置
    maintenance_mode: bool
    maintenance_message: Optional[str]
    analytics_code: Optional[str]
    custom_css: Optional[str]
    custom_js: Optional[str]

    class Config:
        from_attributes = True


class SystemSettingsUpdate(BaseModel):
    # 网站基本信息
    site_name: Optional[str] = None
    site_url: Optional[str] = None
    site_description: Optional[str] = None
    site_keywords: Optional[str] = None
    site_logo: Optional[str] = None
    site_favicon: Optional[str] = None
    # SEO设置
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    # 上传设置
    upload_max_size: Optional[int] = None
    upload_allowed_formats: Optional[List[str]] = None
    image_max_size: Optional[int] = None
    image_allowed_formats: Optional[List[str]] = None
    # 视频设置
    video_auto_approve: Optional[bool] = None
    video_require_review: Optional[bool] = None
    video_default_quality: Optional[str] = None
    video_enable_transcode: Optional[bool] = None
    video_transcode_formats: Optional[List[str]] = None
    # 评论设置
    comment_enable: Optional[bool] = None
    comment_require_approval: Optional[bool] = None
    comment_allow_guest: Optional[bool] = None
    comment_max_length: Optional[int] = None
    # 用户设置
    user_enable_registration: Optional[bool] = None
    user_require_email_verification: Optional[bool] = None
    user_default_avatar: Optional[str] = None
    user_max_favorites: Optional[int] = None
    # 安全设置
    security_enable_captcha: Optional[bool] = None
    security_login_max_attempts: Optional[int] = None
    security_login_lockout_duration: Optional[int] = None
    security_session_timeout: Optional[int] = None
    # 其他设置
    maintenance_mode: Optional[bool] = None
    maintenance_message: Optional[str] = None
    analytics_code: Optional[str] = None
    custom_css: Optional[str] = None
    custom_js: Optional[str] = None


async def get_or_create_settings(db: AsyncSession) -> SystemSettings:
    """获取或创建系统设置（单例模式）"""
    result = await db.execute(select(SystemSettings).limit(1))
    settings = result.scalar_one_or_none()

    if not settings:
        # 创建默认设置
        settings = SystemSettings(
            upload_allowed_formats=["mp4", "avi", "mkv", "webm", "flv"],
            image_allowed_formats=["jpg", "jpeg", "png", "webp"],
            video_transcode_formats=["720p", "1080p"],
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)

    return settings


@router.get("/settings", response_model=SystemSettingsResponse)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取系统设置"""
    # 尝试从缓存获取
    cache_key = "system_settings"
    cached = await Cache.get(cache_key)
    if cached:
        return cached

    settings = await get_or_create_settings(db)

    # 缓存30分钟
    response = SystemSettingsResponse.model_validate(settings)
    await Cache.set(cache_key, response.model_dump(), ttl=1800)

    return response


@router.put("/settings", response_model=SystemSettingsResponse)
async def update_settings(
    settings_data: SystemSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """更新系统设置"""
    settings = await get_or_create_settings(db)

    # 更新字段
    update_data = settings_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)

    await db.commit()
    await db.refresh(settings)

    # 清除缓存
    await Cache.delete("system_settings")

    return settings


@router.post("/settings/reset", response_model=SystemSettingsResponse)
async def reset_settings(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """重置系统设置为默认值"""
    settings: SystemSettings = await get_or_create_settings(db)

    # 重置为默认值  # type: ignore
    settings.site_name = "视频网站"
    settings.site_url = "http://localhost:3000"
    settings.site_description = None
    settings.site_keywords = None
    settings.site_logo = None
    settings.site_favicon = None

    settings.seo_title = None
    settings.seo_description = None
    settings.seo_keywords = None

    settings.upload_max_size = 1024
    settings.upload_allowed_formats = ["mp4", "avi", "mkv", "webm", "flv"]
    settings.image_max_size = 10
    settings.image_allowed_formats = ["jpg", "jpeg", "png", "webp"]

    settings.video_auto_approve = False
    settings.video_require_review = True
    settings.video_default_quality = "720p"
    settings.video_enable_transcode = True
    settings.video_transcode_formats = ["720p", "1080p"]

    settings.comment_enable = True
    settings.comment_require_approval = False
    settings.comment_allow_guest = False
    settings.comment_max_length = 500

    settings.user_enable_registration = True
    settings.user_require_email_verification = True
    settings.user_default_avatar = None
    settings.user_max_favorites = 1000

    settings.security_enable_captcha = True
    settings.security_login_max_attempts = 5
    settings.security_login_lockout_duration = 30
    settings.security_session_timeout = 7200

    settings.maintenance_mode = False
    settings.maintenance_message = None
    settings.analytics_code = None
    settings.custom_css = None
    settings.custom_js = None

    await db.commit()
    await db.refresh(settings)

    # 清除缓存
    await Cache.delete("system_settings")

    return settings
