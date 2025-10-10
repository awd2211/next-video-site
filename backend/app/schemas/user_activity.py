from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.video import VideoListResponse


class FavoriteCreate(BaseModel):
    """Favorite creation schema"""
    video_id: int = Field(..., gt=0)
    folder_id: Optional[int] = Field(None, description="Folder ID (None for default folder)")


class FavoriteResponse(BaseModel):
    """Favorite response schema"""
    id: int
    user_id: int
    video_id: int
    folder_id: Optional[int] = None
    created_at: datetime

    video: Optional[VideoListResponse] = None

    class Config:
        from_attributes = True


class PaginatedFavoriteResponse(BaseModel):
    """Paginated favorite response"""
    total: int
    page: int
    page_size: int
    items: List[FavoriteResponse]


class WatchHistoryCreate(BaseModel):
    """Watch history creation schema"""
    video_id: int = Field(..., gt=0)
    watch_duration: int = Field(0, ge=0, description="Total watch duration in seconds")
    last_position: int = Field(0, ge=0, description="Last playback position in seconds")
    is_completed: bool = Field(False, description="Whether the video was fully watched")


class WatchHistoryUpdate(BaseModel):
    """Watch history update schema"""
    watch_duration: Optional[int] = Field(None, ge=0)
    last_position: Optional[int] = Field(None, ge=0)
    is_completed: Optional[bool] = None


class WatchHistoryResponse(BaseModel):
    """Watch history response schema"""
    id: int
    user_id: int
    video_id: int
    watch_duration: int
    last_position: int
    is_completed: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    video: Optional[VideoListResponse] = None

    class Config:
        from_attributes = True


class PaginatedWatchHistoryResponse(BaseModel):
    """Paginated watch history response"""
    total: int
    page: int
    page_size: int
    items: List[WatchHistoryResponse]
