"""
Sentry 配置管理 API
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.sentry_config import SentryConfig
from app.models.user import AdminUser
from app.schemas.sentry_config import (
    SentryConfigCreate,
    SentryConfigResponse,
    SentryConfigUpdate,
)
from app.utils.dependencies import get_current_admin_user, get_current_superadmin

router = APIRouter(prefix="/sentry-config", tags=["Sentry Configuration"])


@router.get("/", response_model=List[SentryConfigResponse])
async def get_sentry_configs(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取所有 Sentry 配置
    """
    result = await db.execute(select(SentryConfig).order_by(SentryConfig.id.desc()))
    configs = result.scalars().all()
    return configs


@router.get("/{config_id}", response_model=SentryConfigResponse)
async def get_sentry_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取单个 Sentry 配置
    """
    result = await db.execute(select(SentryConfig).where(SentryConfig.id == config_id))
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="Sentry 配置不存在")

    return config


@router.post("/", response_model=SentryConfigResponse)
async def create_sentry_config(
    config_data: SentryConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """
    创建 Sentry 配置（仅超级管理员）
    """
    # 创建新配置
    new_config = SentryConfig(
        **config_data.model_dump(),
        created_by=current_admin.id,
        updated_by=current_admin.id,
    )

    db.add(new_config)
    await db.commit()
    await db.refresh(new_config)

    return new_config


@router.put("/{config_id}", response_model=SentryConfigResponse)
async def update_sentry_config(
    config_id: int,
    config_data: SentryConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """
    更新 Sentry 配置（仅超级管理员）
    """
    result = await db.execute(select(SentryConfig).where(SentryConfig.id == config_id))
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="Sentry 配置不存在")

    # 更新字段
    update_data = config_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)

    config.updated_by = current_admin.id

    await db.commit()
    await db.refresh(config)

    return config


@router.delete("/{config_id}")
async def delete_sentry_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin),
):
    """
    删除 Sentry 配置（仅超级管理员）
    """
    result = await db.execute(select(SentryConfig).where(SentryConfig.id == config_id))
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="Sentry 配置不存在")

    await db.delete(config)
    await db.commit()

    return {"message": "Sentry 配置已删除"}


@router.get("/active/current", response_model=SentryConfigResponse)
async def get_active_sentry_config(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取当前激活的 Sentry 配置（最新的一条）
    """
    result = await db.execute(
        select(SentryConfig).order_by(SentryConfig.created_at.desc()).limit(1)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="未找到 Sentry 配置")

    return config
