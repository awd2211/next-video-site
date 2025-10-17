"""
AI Management Admin API
管理AI提供商配置、测试连接、查看使用统计
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.ai_config import AIProvider
from app.models.user import AdminUser
from app.schemas.ai import (
    AIProviderCreate,
    AIProviderListResponse,
    AIProviderResponse,
    AIProviderUpdate,
    AIChatRequest,
    AIChatResponse,
    AIModelsResponse,
    AIModelInfo,
    AITestRequest,
    AITestResponse,
    AIUsageStats,
    AIUsageStatsResponse,
)
from app.utils.ai_service import AIService
from app.utils.cache import Cache
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


@router.get("/providers", response_model=AIProviderListResponse)
async def get_providers(
    skip: int = 0,
    limit: int = 100,
    provider_type: Optional[str] = None,
    enabled: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取AI提供商列表"""
    query = select(AIProvider)

    # 过滤
    if provider_type:
        query = query.where(AIProvider.provider_type == provider_type)
    if enabled is not None:
        query = query.where(AIProvider.enabled == enabled)

    # 排序
    query = query.order_by(AIProvider.created_at.desc())

    # 获取总数
    total_query = select(AIProvider)
    if provider_type:
        total_query = total_query.where(AIProvider.provider_type == provider_type)
    if enabled is not None:
        total_query = total_query.where(AIProvider.enabled == enabled)

    result = await db.execute(total_query)
    total = len(result.scalars().all())

    # 分页
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    providers = result.scalars().all()

    return AIProviderListResponse(total=total, items=providers)


@router.get("/providers/{provider_id}", response_model=AIProviderResponse)
async def get_provider(
    provider_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取单个AI提供商配置"""
    result = await db.execute(select(AIProvider).where(AIProvider.id == provider_id))
    provider = result.scalar_one_or_none()

    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    return provider


@router.post("/providers", response_model=AIProviderResponse, status_code=201)
async def create_provider(
    provider_data: AIProviderCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """创建AI提供商配置"""
    # 如果设置为默认,取消其他默认配置
    if provider_data.is_default:
        result = await db.execute(
            select(AIProvider).where(
                AIProvider.provider_type == provider_data.provider_type,
                AIProvider.is_default == True,
            )
        )
        existing_defaults = result.scalars().all()
        for existing in existing_defaults:
            existing.is_default = False

    # 创建新配置
    provider = AIProvider(**provider_data.model_dump())
    db.add(provider)
    await db.commit()
    await db.refresh(provider)

    # 清除缓存
    await Cache.delete(f"ai_providers:{provider_data.provider_type}")

    logger.info(f"Admin {current_admin.username} created AI provider: {provider.name}")

    # 发送AI提供商管理通知
    try:
        from app.utils.admin_notification_service import AdminNotificationService

        await AdminNotificationService.notify_ai_provider_management(
            db=db,
            provider_id=provider.id,
            provider_name=provider.name,
            action="created",
            admin_username=current_admin.username,
            details=f"类型: {provider.provider_type}, 模型: {provider.model_name}",
        )
    except Exception as e:
        print(f"Failed to send AI provider creation notification: {e}")

    return provider


@router.put("/providers/{provider_id}", response_model=AIProviderResponse)
async def update_provider(
    provider_id: int,
    provider_data: AIProviderUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """更新AI提供商配置"""
    result = await db.execute(select(AIProvider).where(AIProvider.id == provider_id))
    provider = result.scalar_one_or_none()

    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    # 如果设置为默认,取消其他默认配置
    if provider_data.is_default and not provider.is_default:
        result = await db.execute(
            select(AIProvider).where(
                AIProvider.provider_type == provider.provider_type,
                AIProvider.is_default == True,
                AIProvider.id != provider_id,
            )
        )
        existing_defaults = result.scalars().all()
        for existing in existing_defaults:
            existing.is_default = False

    # 更新字段
    update_data = provider_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(provider, key, value)

    await db.commit()
    await db.refresh(provider)

    # 清除缓存
    await Cache.delete(f"ai_providers:{provider.provider_type}")

    logger.info(f"Admin {current_admin.username} updated AI provider: {provider.name}")

    # 发送AI提供商管理通知
    try:
        from app.utils.admin_notification_service import AdminNotificationService

        # 构建更新详情
        details_parts = []
        if provider_data.enabled is not None:
            details_parts.append(f"状态: {'启用' if provider_data.enabled else '禁用'}")
        if provider_data.model_name is not None:
            details_parts.append(f"模型: {provider_data.model_name}")
        if provider_data.is_default is not None and provider_data.is_default:
            details_parts.append("设置为默认")

        await AdminNotificationService.notify_ai_provider_management(
            db=db,
            provider_id=provider.id,
            provider_name=provider.name,
            action="updated",
            admin_username=current_admin.username,
            details=", ".join(details_parts) if details_parts else "更新了提供商配置",
        )
    except Exception as e:
        print(f"Failed to send AI provider update notification: {e}")

    return provider


@router.delete("/providers/{provider_id}", status_code=204)
async def delete_provider(
    provider_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """删除AI提供商配置"""
    result = await db.execute(select(AIProvider).where(AIProvider.id == provider_id))
    provider = result.scalar_one_or_none()

    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    provider_type = provider.provider_type
    provider_name = provider.name

    await db.delete(provider)
    await db.commit()

    # 清除缓存
    await Cache.delete(f"ai_providers:{provider_type}")

    logger.info(f"Admin {current_admin.username} deleted AI provider: {provider_name}")

    # 发送AI提供商管理通知
    try:
        from app.utils.admin_notification_service import AdminNotificationService

        await AdminNotificationService.notify_ai_provider_management(
            db=db,
            provider_id=provider_id,
            provider_name=provider_name,
            action="deleted",
            admin_username=current_admin.username,
            details=f"类型: {provider_type}",
        )
    except Exception as e:
        print(f"Failed to send AI provider deletion notification: {e}")

    return None


@router.post("/providers/{provider_id}/test", response_model=AITestResponse)
async def test_provider(
    provider_id: int,
    test_data: AITestRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """测试AI提供商连接"""
    result = await db.execute(select(AIProvider).where(AIProvider.id == provider_id))
    provider = result.scalar_one_or_none()

    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    # 测试连接
    test_result = await AIService.test_connection(
        provider_type=provider.provider_type,
        api_key=provider.api_key,
        base_url=provider.base_url,
        model_name=provider.model_name,
    )

    # 更新测试状态
    provider.last_test_at = datetime.utcnow()
    provider.last_test_status = "success" if test_result["success"] else "failed"
    provider.last_test_message = test_result["message"]
    await db.commit()

    # 发送AI提供商测试通知
    try:
        from app.utils.admin_notification_service import AdminNotificationService

        await AdminNotificationService.notify_ai_provider_management(
            db=db,
            provider_id=provider.id,
            provider_name=provider.name,
            action="tested",
            admin_username=current_admin.username,
            details=f"测试{'成功' if test_result['success'] else '失败'}, 延迟: {test_result['latency_ms']}ms",
        )
    except Exception as e:
        print(f"Failed to send AI provider test notification: {e}")

    if test_result["success"]:
        return AITestResponse(
            success=True,
            response=test_result["message"],
            latency_ms=test_result["latency_ms"],
        )
    else:
        return AITestResponse(
            success=False, error=test_result["message"], latency_ms=test_result["latency_ms"]
        )


@router.post("/chat", response_model=AIChatResponse)
async def chat_with_ai(
    chat_data: AIChatRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """使用AI提供商进行聊天"""
    result = await db.execute(select(AIProvider).where(AIProvider.id == chat_data.provider_id))
    provider = result.scalar_one_or_none()

    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    if not provider.enabled:
        raise HTTPException(status_code=400, detail="Provider is disabled")

    # 调用AI服务
    chat_result = await AIService.chat_completion(
        provider_type=provider.provider_type,
        api_key=provider.api_key,
        model_name=provider.model_name,
        messages=chat_data.messages,
        base_url=provider.base_url,
        max_tokens=provider.max_tokens or 2048,
        temperature=provider.temperature or 0.7,
        top_p=provider.top_p or 1.0,
        frequency_penalty=provider.frequency_penalty or 0.0,
        presence_penalty=provider.presence_penalty or 0.0,
    )

    # 更新使用统计
    if chat_result["success"]:
        provider.total_requests += 1
        provider.total_tokens += chat_result.get("tokens_used", 0)
        provider.last_used_at = datetime.utcnow()
        await db.commit()

    if chat_result["success"]:
        return AIChatResponse(
            success=True,
            response=chat_result["response"],
            tokens_used=chat_result["tokens_used"],
            latency_ms=chat_result["latency_ms"],
            model=chat_result.get("model"),
        )
    else:
        return AIChatResponse(
            success=False,
            error=chat_result["error"],
            latency_ms=chat_result["latency_ms"],
        )


@router.get("/models/{provider_type}", response_model=AIModelsResponse)
async def get_available_models(
    provider_type: str,
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取指定提供商的可用模型列表"""
    if provider_type not in ["openai", "grok", "google"]:
        raise HTTPException(status_code=400, detail="Invalid provider type")

    models = AIService.get_available_models(provider_type)
    return AIModelsResponse(
        provider_type=provider_type, models=[AIModelInfo(**m) for m in models]
    )


@router.get("/usage", response_model=AIUsageStatsResponse)
async def get_usage_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取AI使用统计"""
    result = await db.execute(select(AIProvider).order_by(AIProvider.total_requests.desc()))
    providers = result.scalars().all()

    stats = [
        AIUsageStats(
            provider_id=p.id,
            provider_name=p.name,
            provider_type=p.provider_type,
            total_requests=p.total_requests,
            total_tokens=p.total_tokens,
            last_used_at=p.last_used_at,
            enabled=p.enabled,
        )
        for p in providers
    ]

    total_requests = sum(p.total_requests for p in providers)
    total_tokens = sum(p.total_tokens for p in providers)

    return AIUsageStatsResponse(
        stats=stats, total_requests=total_requests, total_tokens=total_tokens
    )
