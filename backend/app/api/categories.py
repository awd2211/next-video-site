from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.video import Category, Country, Tag
from app.schemas.video import CategoryResponse, CountryResponse, TagResponse
from app.utils.cache import Cache
from app.utils.language import LanguageHelper, get_language

router = APIRouter()


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language),
):
    """
    Get all active categories (cached for 30 minutes)

    自动根据 Accept-Language 或 X-Language 头返回对应语言
    """
    # 缓存键包含语言
    cache_key = f"categories:all:active:{lang}"
    cached = await Cache.get(cache_key)
    if cached is not None:
        return cached

    # 从数据库查询
    result = await db.execute(
        select(Category)
        .filter(Category.is_active.is_(True))
        .order_by(Category.sort_order)
    )
    categories = result.scalars().all()

    # 根据语言返回对应字段
    localized_categories = []
    for cat in categories:
        localized_categories.append({
            "id": cat.id,
            "name": LanguageHelper.get_localized_field(cat, 'name', lang),
            "slug": cat.slug,
            "description": LanguageHelper.get_localized_field(cat, 'description', lang),
        })

    # 缓存30分钟
    await Cache.set(cache_key, localized_categories, ttl=1800)

    return localized_categories


# 移动到独立路由，但暂时放这里
countries_router = APIRouter()
tags_router = APIRouter()


@countries_router.get("", response_model=List[CountryResponse])
async def list_countries(
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language),
):
    """
    Get all countries (cached for 1 hour)

    自动根据 Accept-Language 或 X-Language 头返回对应语言
    """
    # 缓存键包含语言
    cache_key = f"countries:all:{lang}"
    cached = await Cache.get(cache_key)
    if cached is not None:
        return cached

    # 从数据库查询
    result = await db.execute(select(Country).order_by(Country.name))
    countries = result.scalars().all()

    # 根据语言返回对应字段
    localized_countries = []
    for country in countries:
        localized_countries.append({
            "id": country.id,
            "name": LanguageHelper.get_localized_field(country, 'name', lang),
            "code": country.code,
        })

    # 缓存1小时
    await Cache.set(cache_key, localized_countries, ttl=3600)

    return localized_countries


@tags_router.get("", response_model=List[TagResponse])
async def list_tags(
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language),
):
    """
    Get all tags (cached for 30 minutes)

    自动根据 Accept-Language 或 X-Language 头返回对应语言
    """
    # 缓存键包含语言
    cache_key = f"tags:all:{lang}"
    cached = await Cache.get(cache_key)
    if cached is not None:
        return cached

    # 从数据库查询
    result = await db.execute(select(Tag).order_by(Tag.name))
    tags = result.scalars().all()

    # 根据语言返回对应字段
    localized_tags = []
    for tag in tags:
        localized_tags.append({
            "id": tag.id,
            "name": LanguageHelper.get_localized_field(tag, 'name', lang),
            "slug": tag.slug,
        })

    # 缓存30分钟
    await Cache.set(cache_key, localized_tags, ttl=1800)

    return localized_tags
