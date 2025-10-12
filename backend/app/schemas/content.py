from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AnnouncementResponse(BaseModel):
    """公告响应（用户端）"""

    id: int
    title: str
    content: str
    type: str
    is_pinned: bool
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
