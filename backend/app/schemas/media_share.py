"""
媒体文件分享 Schema
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MediaShareCreate(BaseModel):
    """创建分享链接"""
    media_id: int = Field(..., description="媒体文件ID")
    password: Optional[str] = Field(None, description="访问密码")
    allow_download: bool = Field(True, description="是否允许下载")
    max_downloads: Optional[int] = Field(None, description="最大下载次数")
    max_views: Optional[int] = Field(None, description="最大访问次数")
    expires_at: Optional[datetime] = Field(None, description="过期时间")
    note: Optional[str] = Field(None, description="备注")


class MediaShareUpdate(BaseModel):
    """更新分享链接"""
    password: Optional[str] = None
    allow_download: Optional[bool] = None
    max_downloads: Optional[int] = None
    max_views: Optional[int] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None
    note: Optional[str] = None


class MediaShareResponse(BaseModel):
    """分享链接响应"""
    id: int
    media_id: int
    share_code: str
    password: Optional[str] = None
    allow_download: bool
    max_downloads: Optional[int]
    download_count: int
    max_views: Optional[int]
    view_count: int
    expires_at: Optional[datetime]
    is_active: bool
    created_by: int
    note: Optional[str]
    created_at: datetime
    updated_at: datetime

    # 计算属性
    is_expired: bool
    is_available: bool

    # 媒体文件信息
    media_title: Optional[str] = None
    media_type: Optional[str] = None

    class Config:
        from_attributes = True


class MediaShareListResponse(BaseModel):
    """分享链接列表响应"""
    items: list[MediaShareResponse]
    total: int
    page: int
    page_size: int
    pages: int
