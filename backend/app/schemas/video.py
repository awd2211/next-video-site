from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.utils.validation_config import (
    TITLE_MAX_LENGTH,
    DESCRIPTION_MAX_LENGTH,
    URL_MAX_LENGTH,
    YEAR_MIN,
    YEAR_MAX,
)
from app.utils.validators import validate_safe_url


class VideoTypeEnum(str, Enum):
    """Video type enum"""

    MOVIE = "movie"
    TV_SERIES = "tv_series"
    ANIME = "anime"
    DOCUMENTARY = "documentary"


class VideoStatusEnum(str, Enum):
    """Video status enum"""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CategoryResponse(BaseModel):
    """Category response schema"""

    id: int
    name: str
    slug: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class CountryResponse(BaseModel):
    """Country response schema"""

    id: int
    name: str
    code: str

    class Config:
        from_attributes = True


class TagResponse(BaseModel):
    """Tag response schema"""

    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True


class ActorResponse(BaseModel):
    """Actor response schema"""

    id: int
    name: str
    avatar: Optional[str] = None
    role_name: Optional[str] = None  # Character name in this video

    class Config:
        from_attributes = True


class DirectorResponse(BaseModel):
    """Director response schema"""

    id: int
    name: str
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    """Video list item response schema"""

    id: int
    title: str
    slug: str
    video_type: str
    status: str
    poster_url: Optional[str] = None
    release_year: Optional[int] = None
    duration: Optional[int] = None
    average_rating: float
    view_count: int
    created_at: datetime
    is_av1_available: bool = False  # Whether AV1 codec version is available

    class Config:
        from_attributes = True


class VideoDetailResponse(VideoListResponse):
    """Video detail response schema"""

    original_title: Optional[str] = None
    description: Optional[str] = None
    video_url: Optional[str] = None
    trailer_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    release_date: Optional[datetime] = None
    language: Optional[str] = None
    total_seasons: Optional[int] = None
    total_episodes: Optional[int] = None
    series_status: Optional[str] = None
    like_count: int
    favorite_count: int
    comment_count: int
    rating_count: int
    is_featured: bool
    is_recommended: bool
    published_at: Optional[datetime] = None

    country: Optional[CountryResponse] = None
    categories: List[CategoryResponse] = []
    tags: List[TagResponse] = []
    actors: List[ActorResponse] = []
    directors: List[DirectorResponse] = []

    @classmethod
    def model_validate(cls, obj, **kwargs):
        """Custom validation to extract nested relationships"""
        if hasattr(obj, "video_categories"):
            obj.categories = [vc.category for vc in obj.video_categories if vc.category]
        if hasattr(obj, "video_tags"):
            obj.tags = [vt.tag for vt in obj.video_tags if vt.tag]
        if hasattr(obj, "video_actors"):
            obj.actors = [va.actor for va in obj.video_actors if va.actor]
        if hasattr(obj, "video_directors"):
            obj.directors = [vd.director for vd in obj.video_directors if vd.director]
        return super().model_validate(obj, **kwargs)


class VideoCreate(BaseModel):
    """Video creation schema"""

    title: str = Field(..., min_length=1, max_length=TITLE_MAX_LENGTH)
    original_title: Optional[str] = Field(None, max_length=TITLE_MAX_LENGTH)
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGTH)
    video_type: VideoTypeEnum
    status: VideoStatusEnum = VideoStatusEnum.DRAFT
    video_url: Optional[str] = Field(None, max_length=URL_MAX_LENGTH)
    trailer_url: Optional[str] = Field(None, max_length=URL_MAX_LENGTH)
    poster_url: Optional[str] = Field(None, max_length=URL_MAX_LENGTH)
    backdrop_url: Optional[str] = Field(None, max_length=URL_MAX_LENGTH)
    release_year: Optional[int] = Field(None, ge=YEAR_MIN, le=YEAR_MAX)
    release_date: Optional[datetime] = None
    duration: Optional[int] = Field(None, gt=0)
    country_id: Optional[int] = None
    language: Optional[str] = Field(None, max_length=100)
    total_seasons: Optional[int] = Field(None, ge=0)
    total_episodes: Optional[int] = Field(None, ge=0)
    category_ids: List[int] = []
    tag_ids: List[int] = []
    actor_ids: List[int] = []
    director_ids: List[int] = []
    
    @field_validator("video_url", "trailer_url", "poster_url", "backdrop_url")
    @classmethod
    def validate_video_urls(cls, v: Optional[str]) -> Optional[str]:
        """验证视频相关URL的安全性"""
        return validate_safe_url(v)


class VideoUpdate(BaseModel):
    """Video update schema"""

    title: Optional[str] = Field(None, min_length=1, max_length=TITLE_MAX_LENGTH)
    original_title: Optional[str] = Field(None, max_length=TITLE_MAX_LENGTH)
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGTH)
    video_type: Optional[VideoTypeEnum] = None
    status: Optional[VideoStatusEnum] = None
    video_url: Optional[str] = Field(None, max_length=URL_MAX_LENGTH)
    trailer_url: Optional[str] = Field(None, max_length=URL_MAX_LENGTH)
    poster_url: Optional[str] = Field(None, max_length=URL_MAX_LENGTH)
    backdrop_url: Optional[str] = Field(None, max_length=URL_MAX_LENGTH)
    release_year: Optional[int] = Field(None, ge=YEAR_MIN, le=YEAR_MAX)
    release_date: Optional[datetime] = None
    duration: Optional[int] = Field(None, gt=0)
    country_id: Optional[int] = None
    language: Optional[str] = Field(None, max_length=100)
    total_seasons: Optional[int] = Field(None, ge=0)
    total_episodes: Optional[int] = Field(None, ge=0)
    category_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None
    actor_ids: Optional[List[int]] = None
    director_ids: Optional[List[int]] = None
    
    @field_validator("video_url", "trailer_url", "poster_url", "backdrop_url")
    @classmethod
    def validate_video_urls(cls, v: Optional[str]) -> Optional[str]:
        """验证视频相关URL的安全性"""
        return validate_safe_url(v)


class PaginatedResponse(BaseModel):
    """Paginated response schema"""

    total: int
    page: int
    page_size: int
    items: List[VideoListResponse]
    pages: int
