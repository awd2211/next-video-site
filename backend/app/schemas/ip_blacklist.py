"""
IP黑名单相关Schema
"""

from typing import Optional

from pydantic import BaseModel, Field


class IPBlacklistCreate(BaseModel):
    """添加IP到黑名单"""

    ip: str = Field(..., description="IP地址", pattern=r"^(?:\d{1,3}\.){3}\d{1,3}$")
    reason: str = Field(..., description="封禁原因", min_length=1, max_length=500)
    duration: Optional[int] = Field(
        None, description="封禁时长(秒), None表示永久封禁", ge=60
    )


class IPBlacklistResponse(BaseModel):
    """IP黑名单响应"""

    ip: str
    reason: str
    banned_at: str  # 封禁时间戳
    expires_at: Optional[str] = None  # 过期时间戳, None表示永久
    is_permanent: bool  # 是否永久封禁


class IPBlacklistListResponse(BaseModel):
    """IP黑名单列表响应"""

    total: int
    items: list[IPBlacklistResponse]


class IPBlacklistStatsResponse(BaseModel):
    """IP黑名单统计"""

    total_blacklisted: int  # 总封禁数
    permanent_count: int  # 永久封禁数
    temporary_count: int  # 临时封禁数
    auto_banned_count: int  # 自动封禁数(最近7天)
