"""
Pydantic schemas for shared watchlist
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SharedWatchlistCreate(BaseModel):
    """Schema for creating a shared watchlist"""

    title: str = Field(..., min_length=1, max_length=200, description="Title of the shared list")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description")
    video_ids: list[int] = Field(..., min_items=1, description="List of video IDs to share")
    expires_in_days: Optional[int] = Field(
        None, ge=1, le=365, description="Optional expiration in days (1-365)"
    )


class SharedWatchlistUpdate(BaseModel):
    """Schema for updating a shared watchlist"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    video_ids: Optional[list[int]] = Field(None, min_items=1)
    is_active: Optional[bool] = None


class SharedWatchlistResponse(BaseModel):
    """Schema for shared watchlist response"""

    id: int
    user_id: int
    share_token: str
    title: str
    description: Optional[str]
    video_ids: list[int]
    is_active: bool
    view_count: int
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


class SharedWatchlistPublicResponse(BaseModel):
    """Schema for public shared watchlist view (without user_id)"""

    share_token: str
    title: str
    description: Optional[str]
    video_ids: list[int]
    view_count: int
    created_at: datetime
    username: str = Field(..., description="Username of the list creator")

    class Config:
        from_attributes = True


class ShareLinkResponse(BaseModel):
    """Schema for share link creation response"""

    share_token: str
    share_url: str
    title: str
    expires_at: Optional[datetime]
