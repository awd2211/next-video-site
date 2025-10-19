"""
Sentry 配置公开 API
供前端获取 Sentry 配置
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.sentry_config import SentryConfig
from app.schemas.sentry_config import SentryConfigPublic

router = APIRouter(prefix="/sentry-config", tags=["Public Sentry Config"])


@router.get("/frontend", response_model=SentryConfigPublic)
async def get_frontend_sentry_config(
    db: AsyncSession = Depends(get_db),
):
    """
    获取用户前端的 Sentry 配置
    如果未配置或表不存在，返回默认禁用的配置
    """
    try:
        result = await db.execute(
            select(SentryConfig)
            .where(SentryConfig.frontend_enabled == True)
            .order_by(SentryConfig.created_at.desc())
            .limit(1)
        )
        config = result.scalar_one_or_none()

        if not config:
            # 返回默认禁用配置
            return SentryConfigPublic(
                dsn="",
                environment="production",
                traces_sample_rate="0.0",
                replays_session_sample_rate="0.0",
                replays_on_error_sample_rate="0.0",
                release_version=None,
                debug_mode=False,
                attach_stacktrace=False,
                ignore_errors=None,
                allowed_urls=None,
                denied_urls=None,
            )

        return config
    except Exception:
        # 如果表不存在或查询失败，返回默认禁用配置
        return SentryConfigPublic(
            dsn="",
            environment="production",
            traces_sample_rate="0.0",
            replays_session_sample_rate="0.0",
            replays_on_error_sample_rate="0.0",
            release_version=None,
            debug_mode=False,
            attach_stacktrace=False,
            ignore_errors=None,
            allowed_urls=None,
            denied_urls=None,
        )


@router.get("/admin-frontend", response_model=SentryConfigPublic)
async def get_admin_frontend_sentry_config(
    db: AsyncSession = Depends(get_db),
):
    """
    获取管理前端的 Sentry 配置
    如果未配置或表不存在，返回默认禁用的配置
    """
    try:
        result = await db.execute(
            select(SentryConfig)
            .where(SentryConfig.admin_frontend_enabled == True)
            .order_by(SentryConfig.created_at.desc())
            .limit(1)
        )
        config = result.scalar_one_or_none()

        if not config:
            # 返回默认禁用配置
            return SentryConfigPublic(
                dsn="",
                environment="production",
                traces_sample_rate="0.0",
                replays_session_sample_rate="0.0",
                replays_on_error_sample_rate="0.0",
                release_version=None,
                debug_mode=False,
                attach_stacktrace=False,
                ignore_errors=None,
                allowed_urls=None,
                denied_urls=None,
            )

        return config
    except Exception:
        # 如果表不存在或查询失败，返回默认禁用配置
        return SentryConfigPublic(
            dsn="",
            environment="production",
            traces_sample_rate="0.0",
            replays_session_sample_rate="0.0",
            replays_on_error_sample_rate="0.0",
            release_version=None,
            debug_mode=False,
            attach_stacktrace=False,
            ignore_errors=None,
            allowed_urls=None,
            denied_urls=None,
        )
