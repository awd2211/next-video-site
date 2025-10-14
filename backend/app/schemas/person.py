from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.video import VideoListResponse
from app.utils.validation_config import PERSON_NAME_MAX_LENGTH, BIOGRAPHY_MAX_LENGTH, URL_MAX_LENGTH
from app.utils.validators import validate_safe_url


class ActorBase(BaseModel):
    """Actor base schema"""

    name: str = Field(..., min_length=1, max_length=PERSON_NAME_MAX_LENGTH)
    avatar: Optional[str] = Field(None, max_length=URL_MAX_LENGTH)
    biography: Optional[str] = Field(None, max_length=BIOGRAPHY_MAX_LENGTH)
    birth_date: Optional[datetime] = None
    country_id: Optional[int] = None
    
    @field_validator("avatar")
    @classmethod
    def validate_avatar_url(cls, v: Optional[str]) -> Optional[str]:
        """验证头像URL安全性"""
        return validate_safe_url(v)


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

    name: str = Field(..., min_length=1, max_length=PERSON_NAME_MAX_LENGTH)
    avatar: Optional[str] = Field(None, max_length=URL_MAX_LENGTH)
    biography: Optional[str] = Field(None, max_length=BIOGRAPHY_MAX_LENGTH)
    birth_date: Optional[datetime] = None
    country_id: Optional[int] = None
    
    @field_validator("avatar")
    @classmethod
    def validate_avatar_url(cls, v: Optional[str]) -> Optional[str]:
        """验证头像URL安全性"""
        return validate_safe_url(v)


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
