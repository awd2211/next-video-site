"""
弹幕Schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.danmaku import DanmakuType, DanmakuStatus
import re


class DanmakuCreate(BaseModel):
    """创建弹幕"""
    video_id: int = Field(..., gt=0, description="视频ID")
    content: str = Field(..., min_length=1, max_length=100, description="弹幕内容")
    time: float = Field(..., ge=0, description="出现时间(秒)")
    type: DanmakuType = Field(DanmakuType.SCROLL, description="弹幕类型")
    color: str = Field("#FFFFFF", description="颜色(十六进制)")
    font_size: int = Field(25, ge=12, le=36, description="字体大小")

    @validator('color')
    def validate_color(cls, v):
        if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('颜色必须是十六进制格式 (如 #FFFFFF)')
        return v.upper()


class DanmakuResponse(BaseModel):
    """弹幕响应"""
    id: int
    video_id: int
    user_id: int
    content: str
    time: float
    type: DanmakuType
    color: str
    font_size: int
    status: DanmakuStatus
    is_blocked: bool
    report_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class DanmakuListResponse(BaseModel):
    """弹幕列表响应 (用于播放器)"""
    total: int
    items: List[DanmakuResponse]


class DanmakuAdminResponse(DanmakuResponse):
    """管理后台弹幕响应 (含审核信息)"""
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    reject_reason: Optional[str]
    updated_at: Optional[datetime]
    user: Optional[dict] = None  # 用户信息

    class Config:
        from_attributes = True


class DanmakuReviewAction(BaseModel):
    """弹幕审核操作"""
    danmaku_ids: List[int] = Field(..., min_length=1, description="弹幕ID列表")
    action: str = Field(..., pattern="^(approve|reject|delete|block)$", description="操作类型")
    reject_reason: Optional[str] = Field(None, max_length=200, description="拒绝原因")


class DanmakuSearchParams(BaseModel):
    """弹幕搜索参数"""
    video_id: Optional[int] = None
    user_id: Optional[int] = None
    status: Optional[DanmakuStatus] = None
    is_blocked: Optional[bool] = None
    keyword: Optional[str] = Field(None, max_length=50, description="关键词")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class BlockedWordCreate(BaseModel):
    """创建屏蔽词"""
    word: str = Field(..., min_length=1, max_length=50, description="屏蔽词")
    is_regex: bool = Field(False, description="是否为正则表达式")


class BlockedWordResponse(BaseModel):
    """屏蔽词响应"""
    id: int
    word: str
    is_regex: bool
    created_by: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class DanmakuStatsResponse(BaseModel):
    """弹幕统计"""
    total: int = 0
    pending: int = 0
    approved: int = 0
    rejected: int = 0
    deleted: int = 0
    blocked: int = 0
    today_count: int = 0
    reported_count: int = 0
