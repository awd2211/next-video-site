from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.video import Category, Country, Tag
from app.schemas.video import CategoryResponse, CountryResponse, TagResponse
from app.utils.cache import Cache

router = APIRouter()


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
):
    """Get all active categories (cached for 30 minutes)"""
    # 尝试从缓存获取
    cache_key = "categories:all:active"
    cached = await Cache.get(cache_key)
    if cached is not None:
        return cached

    # 从数据库查询
    result = await db.execute(
        select(Category)
        .filter(Category.is_active == True)
        .order_by(Category.sort_order)
    )
    categories = result.scalars().all()

    # 转换为响应模型
    response = [CategoryResponse.model_validate(c) for c in categories]

    # 缓存30分钟
    await Cache.set(cache_key, response, ttl=1800)

    return response


# 移动到独立路由，但暂时放这里
countries_router = APIRouter()
tags_router = APIRouter()


@countries_router.get("", response_model=List[CountryResponse])
async def list_countries(
    db: AsyncSession = Depends(get_db),
):
    """Get all countries (cached for 1 hour)"""
    # 尝试从缓存获取
    cache_key = "countries:all"
    cached = await Cache.get(cache_key)
    if cached is not None:
        return cached

    # 从数据库查询
    result = await db.execute(select(Country).order_by(Country.name))
    countries = result.scalars().all()

    # 转换为响应模型
    response = [CountryResponse.model_validate(c) for c in countries]

    # 缓存1小时
    await Cache.set(cache_key, response, ttl=3600)

    return response


@tags_router.get("", response_model=List[TagResponse])
async def list_tags(
    db: AsyncSession = Depends(get_db),
):
    """Get all tags (cached for 30 minutes)"""
    # 尝试从缓存获取
    cache_key = "tags:all"
    cached = await Cache.get(cache_key)
    if cached is not None:
        return cached

    # 从数据库查询
    result = await db.execute(select(Tag).order_by(Tag.name))
    tags = result.scalars().all()

    # 转换为响应模型
    response = [TagResponse.model_validate(c) for c in tags]

    # 缓存30分钟
    await Cache.set(cache_key, response, ttl=1800)

    return response
