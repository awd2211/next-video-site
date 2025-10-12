from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.media import MediaType, MediaStatus


class MediaBase(BaseModel):
    """媒体基础schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    folder: Optional[str] = None
    tags: Optional[str] = None


class MediaCreate(MediaBase):
    """创建媒体"""
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    media_type: MediaType
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    thumbnail_path: Optional[str] = None
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None


class MediaUpdate(BaseModel):
    """更新媒体"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    folder: Optional[str] = None
    tags: Optional[str] = None
    status: Optional[MediaStatus] = None


class MediaResponse(MediaBase):
    """媒体响应"""
    id: int
    filename: str
    file_path: str
    file_size: int
    mime_type: Optional[str]
    media_type: MediaType
    status: MediaStatus
    width: Optional[int]
    height: Optional[int]
    duration: Optional[int]
    thumbnail_path: Optional[str]
    url: Optional[str]
    thumbnail_url: Optional[str]
    view_count: int
    download_count: int
    uploader_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    is_deleted: bool

    class Config:
        from_attributes = True


class MediaListResponse(BaseModel):
    """媒体列表响应"""
    items: list[MediaResponse]
    total: int
    page: int
    page_size: int
    pages: int


class MediaUploadResponse(BaseModel):
    """媒体上传响应"""
    id: int
    url: str
    thumbnail_url: Optional[str] = None
    message: str = "上传成功"


class MediaStatsResponse(BaseModel):
    """媒体统计响应"""
    total_count: int
    image_count: int
    video_count: int
    total_size: int
    total_views: int
    total_downloads: int
