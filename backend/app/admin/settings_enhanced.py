"""
Enhanced Settings Endpoints
包含SMTP测试、缓存管理、备份恢复等功能
"""

from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.email import EmailConfiguration
from app.models.settings import SystemSettings
from app.models.user import AdminUser
from app.utils.cache import Cache, CacheStats
from app.utils.dependencies import get_current_admin_user
from app.utils.email_service import send_test_email

router = APIRouter()


# Helper function
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


# Schemas
class EmailTestRequest(BaseModel):
    """SMTP测试邮件请求"""

    to_email: EmailStr


class EmailTestResponse(BaseModel):
    """SMTP测试结果"""

    success: bool
    message: str
    tested_at: datetime


class CacheClearRequest(BaseModel):
    """缓存清除请求"""

    patterns: List[str]  # ["videos:*", "categories:*", "all"]


class CacheClearResponse(BaseModel):
    """缓存清除结果"""

    success: bool
    cleared_keys: int
    patterns: List[str]


class CacheStatsResponse(BaseModel):
    """缓存统计响应"""

    stats: List[Dict[str, Any]]
    summary: Dict[str, Any]


class SettingsBackupResponse(BaseModel):
    """设置备份响应"""

    success: bool
    backup_data: Dict[str, Any]
    backup_time: datetime


class SettingsRestoreRequest(BaseModel):
    """设置恢复请求"""

    backup_data: Dict[str, Any]


# Endpoints


@router.post("/settings/test-email", response_model=EmailTestResponse)
async def test_smtp_email(
    request_data: EmailTestRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """测试SMTP邮件配置"""
    try:
        # 获取邮件配置
        result = await db.execute(select(EmailConfiguration).where(EmailConfiguration.enabled == True))
        email_config = result.scalar_one_or_none()

        if not email_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No active email configuration found"
            )

        # 发送测试邮件
        await send_test_email(email_config, request_data.to_email)

        # 更新设置记录
        settings = await get_or_create_settings(db)
        settings.smtp_test_email = request_data.to_email
        settings.smtp_last_test_at = datetime.now()
        settings.smtp_last_test_status = "success"
        await db.commit()

        # 清除缓存
        await Cache.delete("system_settings")

        return EmailTestResponse(
            success=True, message="Test email sent successfully", tested_at=datetime.now()
        )

    except Exception as e:
        # 更新失败状态
        try:
            settings = await get_or_create_settings(db)
            settings.smtp_test_email = request_data.to_email
            settings.smtp_last_test_at = datetime.now()
            settings.smtp_last_test_status = "failed"
            await db.commit()
        except Exception:
            pass  # Ignore DB errors when logging failure

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/cache/stats", response_model=CacheStatsResponse)
async def get_cache_stats(
    days: int = 7,
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取缓存统计信息"""
    stats_data = await CacheStats.get_stats(days=days)
    return CacheStatsResponse(stats=stats_data["stats"], summary=stats_data["summary"])


@router.post("/cache/clear", response_model=CacheClearResponse)
async def clear_cache(
    request_data: CacheClearRequest,
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """清除指定模式的缓存"""
    total_cleared = 0

    for pattern in request_data.patterns:
        if pattern == "all":
            # 清除所有缓存
            from app.utils.cache import get_redis

            client = await get_redis()
            await client.flushdb()
            total_cleared = -1  # 表示全部清除
            break
        else:
            # 清除指定模式
            cleared = await Cache.delete_pattern(pattern)
            total_cleared += cleared

    return CacheClearResponse(
        success=True,
        cleared_keys=total_cleared if total_cleared >= 0 else -1,
        patterns=request_data.patterns,
    )


@router.get("/settings/backup", response_model=SettingsBackupResponse)
async def backup_settings(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """备份所有系统设置"""
    settings = await get_or_create_settings(db)

    # 构建备份数据
    backup_data = {
        "site_name": settings.site_name,
        "site_url": settings.site_url,
        "site_description": settings.site_description,
        "site_keywords": settings.site_keywords,
        "site_logo": settings.site_logo,
        "site_favicon": settings.site_favicon,
        "seo_title": settings.seo_title,
        "seo_description": settings.seo_description,
        "seo_keywords": settings.seo_keywords,
        "upload_max_size": settings.upload_max_size,
        "upload_allowed_formats": settings.upload_allowed_formats,
        "image_max_size": settings.image_max_size,
        "image_allowed_formats": settings.image_allowed_formats,
        "video_auto_approve": settings.video_auto_approve,
        "video_require_review": settings.video_require_review,
        "video_default_quality": settings.video_default_quality,
        "video_enable_transcode": settings.video_enable_transcode,
        "video_transcode_formats": settings.video_transcode_formats,
        "comment_enable": settings.comment_enable,
        "comment_require_approval": settings.comment_require_approval,
        "comment_allow_guest": settings.comment_allow_guest,
        "comment_max_length": settings.comment_max_length,
        "user_enable_registration": settings.user_enable_registration,
        "user_require_email_verification": settings.user_require_email_verification,
        "user_default_avatar": settings.user_default_avatar,
        "user_max_favorites": settings.user_max_favorites,
        "security_enable_captcha": settings.security_enable_captcha,
        "security_login_max_attempts": settings.security_login_max_attempts,
        "security_login_lockout_duration": settings.security_login_lockout_duration,
        "security_session_timeout": settings.security_session_timeout,
        "maintenance_mode": settings.maintenance_mode,
        "maintenance_message": settings.maintenance_message,
        "analytics_code": settings.analytics_code,
        "custom_css": settings.custom_css,
        "custom_js": settings.custom_js,
        "rate_limit_config": settings.rate_limit_config,
        "cache_config": settings.cache_config,
    }

    return SettingsBackupResponse(success=True, backup_data=backup_data, backup_time=datetime.now())


@router.post("/settings/restore")
async def restore_settings(
    request_data: SettingsRestoreRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """从备份恢复系统设置"""
    settings = await get_or_create_settings(db)

    # 更新所有字段
    for key, value in request_data.backup_data.items():
        if hasattr(settings, key):
            setattr(settings, key, value)

    await db.commit()
    await db.refresh(settings)

    # 清除缓存
    await Cache.delete("system_settings")

    return {"success": True, "message": "Settings restored successfully"}
