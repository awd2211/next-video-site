"""
视频专辑/系列 Schema
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.series import SeriesStatus, SeriesType


class SeriesVideoItem(BaseModel):
    """专辑中的视频条目"""

    video_id: int
    episode_number: Optional[int] = None  # 集数/顺序
    title: str
    poster_url: Optional[str] = None
    duration: Optional[int] = None
    view_count: int = 0
    added_at: datetime

    class Config:
        from_attributes = True


class SeriesCreate(BaseModel):
    """创建专辑"""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    cover_image: Optional[str] = None
    type: SeriesType = SeriesType.SERIES
    status: SeriesStatus = SeriesStatus.DRAFT
    display_order: int = 0
    is_featured: bool = False


class SeriesUpdate(BaseModel):
    """更新专辑"""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    cover_image: Optional[str] = None
    type: Optional[SeriesType] = None
    status: Optional[SeriesStatus] = None
    display_order: Optional[int] = None
    is_featured: Optional[bool] = None


class SeriesAddVideos(BaseModel):
    """添加视频到专辑"""

    video_ids: List[int] = Field(..., min_length=1)
    start_episode_number: Optional[int] = None  # 起始集数（自动递增）


class SeriesRemoveVideos(BaseModel):
    """从专辑移除视频"""

    video_ids: List[int] = Field(..., min_length=1)


class SeriesUpdateVideoOrder(BaseModel):
    """更新视频顺序"""

    video_order: List[dict] = Field(
        ..., description="[{video_id: 1, episode_number: 1}, ...]"
    )


class SeriesListResponse(BaseModel):
    """专辑列表响应（简化版）"""

    id: int
    title: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    type: SeriesType
    status: SeriesStatus
    total_episodes: int = 0
    video_count: Optional[int] = None  # Alias for total_episodes (computed in API)
    total_views: int = 0
    total_favorites: int = 0
    is_featured: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class SeriesDetailResponse(BaseModel):
    """专辑详情响应（含视频列表）"""

    id: int
    title: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    type: SeriesType
    status: SeriesStatus
    total_episodes: int = 0
    total_views: int = 0
    total_favorites: int = 0
    display_order: int = 0
    is_featured: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    videos: List[SeriesVideoItem] = []

    class Config:
        from_attributes = True


class PaginatedSeriesResponse(BaseModel):
    """分页专辑响应"""

    total: int
    page: int
    page_size: int
    pages: int
    items: List[SeriesListResponse]
