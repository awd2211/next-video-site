from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RatingCreate(BaseModel):
    """Rating creation schema"""
    video_id: int = Field(..., gt=0)
    score: float = Field(..., ge=0, le=10, description="Rating score from 0 to 10")


class RatingUpdate(BaseModel):
    """Rating update schema"""
    score: float = Field(..., ge=0, le=10, description="Rating score from 0 to 10")


class RatingResponse(BaseModel):
    """Rating response schema"""
    id: int
    video_id: int
    user_id: int
    score: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VideoRatingStats(BaseModel):
    """Video rating statistics"""
    video_id: int
    average_rating: float
    rating_count: int
    user_rating: Optional[float] = None  # Current user's rating if logged in
