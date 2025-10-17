"""
通用排序工具
用于在后端API中实现灵活的排序功能
"""

from typing import Optional, Type
from sqlalchemy import asc, desc
from sqlalchemy.sql.selectable import Select
from fastapi import HTTPException


def apply_sorting(
    query: Select,
    model: Type,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "desc",
    default_sort: str = "created_at",
    allowed_fields: Optional[list[str]] = None,
) -> Select:
    """
    为SQLAlchemy查询应用排序

    Args:
        query: SQLAlchemy查询对象
        model: SQLAlchemy模型类
        sort_by: 排序字段名称
        sort_order: 排序顺序 ('asc' 或 'desc')
        default_sort: 默认排序字段
        allowed_fields: 允许排序的字段列表（None表示允许所有字段）

    Returns:
        添加了排序的查询对象

    Raises:
        HTTPException: 如果排序字段无效

    Example:
        >>> from app.models.video import Video
        >>> query = select(Video)
        >>> query = apply_sorting(query, Video, sort_by="view_count", sort_order="desc")
    """
    # 使用默认排序字段
    if not sort_by:
        sort_by = default_sort

    # 验证排序字段是否存在
    if not hasattr(model, sort_by):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort field: {sort_by}. Field does not exist on {model.__name__}",
        )

    # 验证字段是否在允许列表中
    if allowed_fields is not None and sort_by not in allowed_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Sorting by '{sort_by}' is not allowed. Allowed fields: {', '.join(allowed_fields)}",
        )

    # 验证排序顺序
    if sort_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400, detail="Invalid sort_order. Must be 'asc' or 'desc'"
        )

    # 获取模型字段
    sort_column = getattr(model, sort_by)

    # 应用排序
    if sort_order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    return query


def get_sortable_fields(model: Type) -> list[str]:
    """
    获取模型的所有可排序字段

    Args:
        model: SQLAlchemy模型类

    Returns:
        字段名称列表

    Example:
        >>> from app.models.video import Video
        >>> fields = get_sortable_fields(Video)
        >>> print(fields)
        ['id', 'title', 'view_count', 'created_at', ...]
    """
    from sqlalchemy import inspect

    mapper = inspect(model)
    return [column.key for column in mapper.columns]


# 常用的排序字段映射（前端字段名 -> 数据库字段名）
SORT_FIELD_MAPPING = {
    # 通用字段
    "createdAt": "created_at",
    "updatedAt": "updated_at",
    "created": "created_at",
    "updated": "updated_at",
    # 视频相关
    "viewCount": "view_count",
    "views": "view_count",
    "averageRating": "average_rating",
    "rating": "average_rating",
    "releaseDate": "release_date",
    # 用户相关
    "lastLogin": "last_login",
    "lastLoginAt": "last_login_at",
    "isActive": "is_active",
    # 其他
    "sortOrder": "sort_order",
    "displayOrder": "display_order",
}


def normalize_sort_field(field: str) -> str:
    """
    标准化排序字段名称（前端 camelCase -> 后端 snake_case）

    Args:
        field: 前端传入的字段名

    Returns:
        标准化后的字段名

    Example:
        >>> normalize_sort_field("viewCount")
        'view_count'
        >>> normalize_sort_field("created_at")
        'created_at'
    """
    return SORT_FIELD_MAPPING.get(field, field)
