from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.video import VideoListResponse


class ActorBase(BaseModel):
    """Actor base schema"""

    name: str
    avatar: Optional[str] = None
    biography: Optional[str] = None
    birth_date: Optional[datetime] = None
    country_id: Optional[int] = None


class ActorResponse(ActorBase):
    """Actor response schema"""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ActorDetailResponse(ActorResponse):
    """Actor detail with videos"""

    videos: List[VideoListResponse] = []


class DirectorBase(BaseModel):
    """Director base schema"""

    name: str
    avatar: Optional[str] = None
    biography: Optional[str] = None
    birth_date: Optional[datetime] = None
    country_id: Optional[int] = None


class DirectorResponse(DirectorBase):
    """Director response schema"""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DirectorDetailResponse(DirectorResponse):
    """Director detail with videos"""

    videos: List[VideoListResponse] = []


class PaginatedActorResponse(BaseModel):
    """Paginated actor response"""

    total: int
    page: int
    page_size: int
    pages: int
    items: List[ActorResponse]


class PaginatedDirectorResponse(BaseModel):
    """Paginated director response"""

    total: int
    page: int
    page_size: int
    pages: int
    items: List[DirectorResponse]
