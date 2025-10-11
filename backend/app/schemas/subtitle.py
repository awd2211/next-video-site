from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SubtitleBase(BaseModel):
    """字幕基础Schema"""

    language: str = Field(
        ..., max_length=50, description="语言代码 (zh-CN, en-US, ja, ko)"
    )
    language_name: str = Field(
        ..., max_length=100, description="语言名称 (简体中文, English)"
    )
    format: str = Field(..., description="字幕格式 (srt, vtt, ass)")
    is_default: bool = Field(False, description="是否默认字幕")
    is_auto_generated: bool = Field(False, description="是否AI自动生成")
    sort_order: int = Field(0, description="排序顺序")


class SubtitleCreate(SubtitleBase):
    """创建字幕Schema"""

    video_id: int = Field(..., description="视频ID")
    file_url: str = Field(..., max_length=1000, description="字幕文件URL")


class SubtitleUpdate(BaseModel):
    """更新字幕Schema"""

    language_name: Optional[str] = Field(None, max_length=100, description="语言名称")
    file_url: Optional[str] = Field(None, max_length=1000, description="字幕文件URL")
    is_default: Optional[bool] = Field(None, description="是否默认字幕")
    sort_order: Optional[int] = Field(None, description="排序顺序")


class SubtitleResponse(SubtitleBase):
    """字幕响应Schema"""

    id: int
    video_id: int
    file_url: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubtitleListResponse(BaseModel):
    """字幕列表响应Schema"""

    subtitles: list[SubtitleResponse]
    total: int
