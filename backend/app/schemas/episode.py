"""
Episode (单集) Pydantic Schemas

用于电视剧单集的API请求验证和响应序列化
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.episode import EpisodeStatus
from app.utils.validation_config import (
    TITLE_MAX_LENGTH,
    DESCRIPTION_MAX_LENGTH,
    URL_MAX_LENGTH,
)
from app.utils.validators import validate_safe_url


class EpisodeBase(BaseModel):
    """Episode base schema with common fields"""

    title: str = Field(..., min_length=1, max_length=TITLE_MAX_LENGTH)
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGTH)


class EpisodeCreate(EpisodeBase):
    """
    创建单集的请求 Schema

    前端添加新剧集时使用
    """

    season_id: int = Field(..., gt=0, description="所属季度ID")
    video_id: int = Field(..., gt=0, description="关联的视频文件ID")
    episode_number: int = Field(..., ge=1, description="集数（本季内的第几集）")

    # 片头片尾时间标记
    intro_start: Optional[int] = Field(None, ge=0, description="片头开始时间（秒）")
    intro_end: Optional[int] = Field(None, ge=0, description="片头结束时间（秒）")
    credits_start: Optional[int] = Field(None, ge=0, description="片尾开始时间（秒）")

    # 预告片
    next_episode_preview_url: Optional[str] = Field(
        None, max_length=URL_MAX_LENGTH, description="下集预告URL"
    )
    preview_duration: Optional[int] = Field(None, ge=0, description="预告时长（秒）")

    # 权限控制
    is_free: bool = False
    vip_required: bool = False

    # 发布状态
    status: EpisodeStatus = EpisodeStatus.DRAFT
    release_date: Optional[datetime] = None

    is_featured: bool = False
    sort_order: int = 0

    @field_validator("next_episode_preview_url")
    @classmethod
    def validate_preview_url(cls, v: Optional[str]) -> Optional[str]:
        """验证预告片URL安全性"""
        return validate_safe_url(v)

    @field_validator("intro_end")
    @classmethod
    def validate_intro_end(cls, v: Optional[int], info) -> Optional[int]:
        """验证片头结束时间必须大于开始时间"""
        if v is not None and "intro_start" in info.data:
            intro_start = info.data.get("intro_start")
            if intro_start is not None and v <= intro_start:
                raise ValueError("片头结束时间必须大于开始时间")
        return v


class EpisodeUpdate(BaseModel):
    """
    更新单集的请求 Schema

    所有字段都是可选的，只更新提供的字段
    """

    title: Optional[str] = Field(None, min_length=1, max_length=TITLE_MAX_LENGTH)
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGTH)
    episode_number: Optional[int] = Field(None, ge=1)

    # 片头片尾时间标记
    intro_start: Optional[int] = Field(None, ge=0)
    intro_end: Optional[int] = Field(None, ge=0)
    credits_start: Optional[int] = Field(None, ge=0)

    # 预告片
    next_episode_preview_url: Optional[str] = Field(None, max_length=URL_MAX_LENGTH)
    preview_duration: Optional[int] = Field(None, ge=0)

    # 权限控制
    is_free: Optional[bool] = None
    vip_required: Optional[bool] = None

    # 发布状态
    status: Optional[EpisodeStatus] = None
    release_date: Optional[datetime] = None

    is_featured: Optional[bool] = None
    sort_order: Optional[int] = None

    @field_validator("next_episode_preview_url")
    @classmethod
    def validate_preview_url(cls, v: Optional[str]) -> Optional[str]:
        """验证预告片URL安全性"""
        return validate_safe_url(v)


class VideoInEpisodeResponse(BaseModel):
    """
    单集响应中的视频信息（简化版）

    只包含必要的视频字段
    """

    id: int
    title: str
    poster_url: Optional[str] = None
    video_url: Optional[str] = None
    duration: Optional[int] = None  # 分钟
    view_count: int

    class Config:
        from_attributes = True


class EpisodeListResponse(BaseModel):
    """
    单集列表响应 Schema（简化版）

    用于列表页，不包含完整的视频数据
    """

    id: int
    season_id: int
    video_id: int
    episode_number: int
    title: str
    description: Optional[str] = None

    # 片头片尾信息
    intro_start: Optional[int] = None
    intro_end: Optional[int] = None
    credits_start: Optional[int] = None

    # 权限
    is_free: bool
    vip_required: bool

    # 状态
    status: EpisodeStatus
    published_at: Optional[datetime] = None

    # 统计
    view_count: int
    like_count: int
    comment_count: int

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EpisodeDetailResponse(EpisodeListResponse):
    """
    单集详情响应 Schema（完整版）

    包含关联的视频信息
    """

    next_episode_preview_url: Optional[str] = None
    preview_duration: Optional[int] = None
    release_date: Optional[datetime] = None
    is_featured: bool
    sort_order: int

    # 关联的视频详情
    video: Optional[VideoInEpisodeResponse] = None


class PaginatedEpisodeResponse(BaseModel):
    """分页单集响应"""

    total: int
    page: int
    page_size: int
    pages: int
    items: list[EpisodeListResponse]


# ==================== 批量操作 Schemas ====================


class BatchAddEpisodes(BaseModel):
    """
    批量添加剧集

    用于一次性添加多个视频作为连续的集
    """

    season_id: int = Field(..., gt=0, description="所属季度ID")
    video_ids: list[int] = Field(
        ..., min_length=1, max_length=100, description="视频ID列表"
    )
    start_episode_number: int = Field(
        1, ge=1, description="起始集数（会自动递增）"
    )
    auto_title: bool = Field(
        True, description="是否自动生成标题（第1集、第2集...）"
    )
    title_prefix: str = Field(
        "第", max_length=10, description="自动标题前缀"
    )
    title_suffix: str = Field(
        "集", max_length=10, description="自动标题后缀"
    )
    is_free: bool = False
    vip_required: bool = False
    status: EpisodeStatus = EpisodeStatus.DRAFT


class BatchUpdateEpisodesOrder(BaseModel):
    """
    批量更新剧集顺序

    用于拖拽排序后保存新顺序
    """

    season_id: int = Field(..., gt=0, description="所属季度ID")
    episode_orders: list[dict[str, int]] = Field(
        ...,
        min_length=1,
        description='集数顺序列表，格式：[{"episode_id": 1, "episode_number": 1}, ...]',
    )


class BatchSetIntroMarkers(BaseModel):
    """
    批量设置片头片尾时间标记

    对于整季都有相同片头片尾时长的情况
    """

    episode_ids: list[int] = Field(..., min_length=1, max_length=100)
    intro_start: Optional[int] = Field(None, ge=0)
    intro_end: Optional[int] = Field(None, ge=0)
    credits_start: Optional[int] = Field(None, ge=0)


class BatchPublishEpisodes(BaseModel):
    """批量发布剧集"""

    episode_ids: list[int] = Field(..., min_length=1, max_length=100)


class BatchDeleteEpisodes(BaseModel):
    """批量删除剧集"""

    episode_ids: list[int] = Field(..., min_length=1, max_length=100)
    confirm: bool = Field(..., description="确认删除（必须为true）")

    @field_validator("confirm")
    @classmethod
    def validate_confirm(cls, v: bool) -> bool:
        if not v:
            raise ValueError("必须确认删除操作")
        return v


# ==================== 特殊功能 Schemas ====================


class EpisodeAnalyticsSummary(BaseModel):
    """
    单集分析摘要

    用于展示单集的关键数据指标
    """

    episode_id: int
    episode_number: int
    title: str
    view_count: int
    completion_rate: float = Field(
        ..., ge=0, le=1, description="完播率（0-1之间）"
    )
    avg_watch_duration: int = Field(..., ge=0, description="平均观看时长（秒）")
    retention_rate: float = Field(
        ..., ge=0, le=1, description="留存率（看下一集的比例）"
    )
    like_count: int
    comment_count: int
