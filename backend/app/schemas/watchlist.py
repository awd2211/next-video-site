"""
Watchlist (My List) Schemas
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.video import VideoListResponse


class WatchlistBase(BaseModel):
    """Base schema for watchlist"""

    video_id: int


class WatchlistCreate(WatchlistBase):
    """Schema for creating watchlist entry"""

    pass


class WatchlistResponse(BaseModel):
    """Schema for watchlist response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    video_id: int
    position: int
    created_at: datetime


class WatchlistWithVideo(WatchlistResponse):
    """Schema for watchlist with video details"""

    video: VideoListResponse


class WatchlistReorderRequest(BaseModel):
    """Schema for reordering watchlist"""

    video_ids: list[int]  # List of video IDs in new order


class WatchlistStatusResponse(BaseModel):
    """Schema for checking if video is in watchlist"""

    in_watchlist: bool
    watchlist_id: Optional[int] = None
