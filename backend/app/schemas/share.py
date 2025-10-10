"""
分享相关 Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.share import SharePlatform


class ShareCreate(BaseModel):
    """创建分享记录"""
    video_id: int = Field(..., gt=0, description="视频ID")
    platform: SharePlatform = Field(..., description="分享平台")


class ShareResponse(BaseModel):
    """分享记录响应"""
    id: int
    video_id: int
    user_id: Optional[int]
    platform: SharePlatform
    shared_at: datetime

    class Config:
        from_attributes = True


class ShareStatsResponse(BaseModel):
    """分享统计响应"""
    total_shares: int = Field(..., description="总分享次数")
    platform_stats: dict = Field(..., description="各平台分享统计")
    recent_shares: int = Field(..., description="最近7天分享次数")
