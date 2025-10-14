from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SearchHistoryCreate(BaseModel):
    """Schema for creating search history entry"""

    query: str = Field(..., min_length=1, max_length=255)
    results_count: int = Field(default=0, ge=0)
    clicked_video_id: Optional[int] = None


class SearchHistoryResponse(BaseModel):
    """Schema for search history response"""

    id: int
    query: str
    results_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class PopularSearchResponse(BaseModel):
    """Schema for popular searches"""

    query: str
    search_count: int


class SearchHistoryStats(BaseModel):
    """Search history statistics for admin analytics"""

    total_searches: int
    unique_queries: int
    avg_results_per_search: float
    top_searches: list[PopularSearchResponse]
