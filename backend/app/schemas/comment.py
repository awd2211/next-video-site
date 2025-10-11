from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class CommentStatusEnum(str, Enum):
    """Comment status enum"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class CommentCreate(BaseModel):
    """Comment creation schema"""

    video_id: int = Field(..., gt=0)
    parent_id: Optional[int] = Field(None, gt=0)
    content: str = Field(..., min_length=1, max_length=1000)


class CommentUpdate(BaseModel):
    """Comment update schema"""

    content: str = Field(..., min_length=1, max_length=1000)


class UserBrief(BaseModel):
    """Brief user info for comment"""

    id: int
    username: str
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    """Comment response schema"""

    id: int
    video_id: int
    user_id: int
    parent_id: Optional[int] = None
    content: str
    status: CommentStatusEnum
    like_count: int
    is_pinned: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    user: UserBrief
    reply_count: int = 0
    replies: List["CommentResponse"] = []

    class Config:
        from_attributes = True


# Update forward references
CommentResponse.model_rebuild()


class PaginatedCommentResponse(BaseModel):
    """Paginated comment response"""

    total: int
    page: int
    page_size: int
    pages: int
    items: List[CommentResponse]
