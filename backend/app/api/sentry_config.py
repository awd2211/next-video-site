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
    """
    result = await db.execute(
        select(SentryConfig)
        .where(SentryConfig.frontend_enabled == True)
        .order_by(SentryConfig.created_at.desc())
        .limit(1)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="未配置 Sentry")

    return config


@router.get("/admin-frontend", response_model=SentryConfigPublic)
async def get_admin_frontend_sentry_config(
    db: AsyncSession = Depends(get_db),
):
    """
    获取管理前端的 Sentry 配置
    """
    result = await db.execute(
        select(SentryConfig)
        .where(SentryConfig.admin_frontend_enabled == True)
        .order_by(SentryConfig.created_at.desc())
        .limit(1)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="未配置 Sentry")

    return config
