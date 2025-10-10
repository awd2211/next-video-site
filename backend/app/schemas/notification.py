from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class NotificationBase(BaseModel):
    """通知基础Schema"""
    type: str = Field(..., description="通知类型")
    title: str = Field(..., max_length=200, description="通知标题")
    content: str = Field(..., description="通知内容")
    related_type: Optional[str] = Field(None, description="关联对象类型")
    related_id: Optional[int] = Field(None, description="关联对象ID")
    link: Optional[str] = Field(None, max_length=500, description="跳转链接")


class NotificationCreate(NotificationBase):
    """创建通知Schema"""
    user_id: int = Field(..., description="用户ID")


class NotificationUpdate(BaseModel):
    """更新通知Schema"""
    is_read: Optional[bool] = Field(None, description="是否已读")


class NotificationResponse(NotificationBase):
    """通知响应Schema"""
    id: int
    user_id: int
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationStatsResponse(BaseModel):
    """通知统计响应Schema"""
    total: int = Field(..., description="总通知数")
    unread: int = Field(..., description="未读通知数")
    read: int = Field(..., description="已读通知数")


class NotificationListResponse(BaseModel):
    """通知列表响应Schema"""
    notifications: list[NotificationResponse]
    total: int
    page: int
    page_size: int
    unread_count: int
