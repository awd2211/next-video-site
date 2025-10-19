"""
Season (季度) Pydantic Schemas

用于电视剧季度的API请求验证和响应序列化
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.season import SeasonStatus
from app.utils.validation_config import (
    SERIES_NAME_MAX_LENGTH,
    DESCRIPTION_MAX_LENGTH,
    URL_MAX_LENGTH,
)
from app.utils.validators import validate_safe_url


class SeasonBase(BaseModel):
    """Season base schema with common fields"""

    title: str = Field(..., min_length=1, max_length=SERIES_NAME_MAX_LENGTH)
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGTH)


class SeasonCreate(SeasonBase):
    """
    创建季度的请求 Schema

    前端创建新季时使用
    """

    series_id: int = Field(..., gt=0, description="所属剧集ID")
    season_number: int = Field(..., ge=1, description="季数（第1季、第2季...）")
    status: SeasonStatus = SeasonStatus.DRAFT
    vip_required: bool = False
    poster_url: Optional[str] = Field(None, max_length=URL_MAX_LENGTH)
    backdrop_url: Optional[str] = Field(None, max_length=URL_MAX_LENGTH)
    trailer_url: Optional[str] = Field(None, max_length=URL_MAX_LENGTH)
    release_date: Optional[datetime] = None
    is_featured: bool = False
    sort_order: int = 0

    @field_validator("poster_url", "backdrop_url", "trailer_url")
    @classmethod
    def validate_urls(cls, v: Optional[str]) -> Optional[str]:
        """验证URL安全性"""
        return validate_safe_url(v)


class SeasonUpdate(BaseModel):
    """
    更新季度的请求 Schema

    所有字段都是可选的，只更新提供的字段
    """

    title: Optional[str] = Field(None, min_length=1, max_length=SERIES_NAME_MAX_LENGTH)
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGTH)
    status: Optional[SeasonStatus] = None
    vip_required: Optional[bool] = None
    poster_url: Optional[str] = Field(None, max_length=URL_MAX_LENGTH)
    backdrop_url: Optional[str] = Field(None, max_length=URL_MAX_LENGTH)
    trailer_url: Optional[str] = Field(None, max_length=URL_MAX_LENGTH)
    release_date: Optional[datetime] = None
    is_featured: Optional[bool] = None
    sort_order: Optional[int] = None

    @field_validator("poster_url", "backdrop_url", "trailer_url")
    @classmethod
    def validate_urls(cls, v: Optional[str]) -> Optional[str]:
        """验证URL安全性"""
        return validate_safe_url(v)


class SeasonListResponse(BaseModel):
    """
    季度列表响应 Schema（简化版）

    用于列表页，不包含完整的剧集信息
    """

    id: int
    series_id: int
    season_number: int
    title: str
    description: Optional[str] = None
    status: SeasonStatus
    vip_required: bool
    poster_url: Optional[str] = None
    total_episodes: int
    total_duration: int
    view_count: int
    favorite_count: int
    average_rating: float
    is_featured: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # 允许从 ORM 模型创建


class EpisodeInSeasonResponse(BaseModel):
    """
    季度详情中的剧集信息（嵌套在 SeasonDetailResponse 中）

    精简的剧集信息，不包含完整的 Video 数据
    """

    id: int
    video_id: int
    episode_number: int
    title: str
    description: Optional[str] = None
    is_free: bool
    vip_required: bool
    status: str
    view_count: int
    published_at: Optional[datetime] = None

    # 片头片尾信息
    intro_start: Optional[int] = None
    intro_end: Optional[int] = None
    credits_start: Optional[int] = None

    class Config:
        from_attributes = True


class SeasonDetailResponse(SeasonListResponse):
    """
    季度详情响应 Schema（完整版）

    包含该季下的所有剧集列表
    """

    backdrop_url: Optional[str] = None
    trailer_url: Optional[str] = None
    release_date: Optional[datetime] = None
    published_at: Optional[datetime] = None
    episodes: list[EpisodeInSeasonResponse] = []


class PaginatedSeasonResponse(BaseModel):
    """分页季度响应"""

    total: int
    page: int
    page_size: int
    pages: int
    items: list[SeasonListResponse]


# ==================== 批量操作 Schemas ====================


class BatchPublishSeasons(BaseModel):
    """批量发布季度"""

    season_ids: list[int] = Field(..., min_length=1, max_length=100)


class BatchArchiveSeasons(BaseModel):
    """批量归档季度"""

    season_ids: list[int] = Field(..., min_length=1, max_length=100)


class BatchDeleteSeasons(BaseModel):
    """批量删除季度"""

    season_ids: list[int] = Field(..., min_length=1, max_length=100)
    confirm: bool = Field(
        ..., description="确认删除（必须为true，防止误操作）"
    )

    @field_validator("confirm")
    @classmethod
    def validate_confirm(cls, v: bool) -> bool:
        if not v:
            raise ValueError("必须确认删除操作")
        return v
