"""
IP黑名单管理 - 管理员API
"""

import time
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.models.user import AdminUser
from app.schemas.ip_blacklist import (
    IPBlacklistCreate,
    IPBlacklistListResponse,
    IPBlacklistResponse,
    IPBlacklistStatsResponse,
)
from app.utils.dependencies import get_current_admin_user
from app.utils.rate_limit import (
    RateLimitPresets,
    add_to_blacklist,
    check_ip_blacklist,
    get_blacklist,
    get_redis_client,
    limiter,
    remove_from_blacklist,
)

router = APIRouter()


@router.get("/", response_model=IPBlacklistListResponse, summary="获取IP黑名单列表")
@limiter.limit(RateLimitPresets.ADMIN_READ)
async def get_blacklist_list(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="搜索IP地址"),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取IP黑名单列表

    - 支持分页
    - 支持IP地址搜索
    - 显示封禁原因、时间、是否永久
    """
    blacklist = await get_blacklist()

    # 搜索过滤
    if search:
        blacklist = [item for item in blacklist if search.lower() in item["ip"].lower()]

    # 排序: 永久封禁在前, 然后按封禁时间倒序
    blacklist.sort(key=lambda x: (0 if x["is_permanent"] else 1, -int(x["banned_at"])))

    # 分页
    total = len(blacklist)
    start = (page - 1) * page_size
    end = start + page_size
    items = blacklist[start:end]

    return IPBlacklistListResponse(
        total=total, items=[IPBlacklistResponse(**item) for item in items]
    )


@router.post(
    "/",
    response_model=IPBlacklistResponse,
    summary="添加IP到黑名单",
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def add_ip_to_blacklist(
    request: Request,
    data: IPBlacklistCreate,
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    添加IP到黑名单

    - **ip**: IP地址
    - **reason**: 封禁原因
    - **duration**: 封禁时长(秒), 不传或传None表示永久封禁
    """
    # 检查IP是否已在黑名单
    if await check_ip_blacklist(data.ip):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"IP {data.ip} 已在黑名单中"
        )

    # 添加到黑名单
    await add_to_blacklist(
        ip=data.ip, reason=f"{data.reason} (管理员手动添加)", duration=data.duration
    )

    # 获取添加后的信息
    blacklist = await get_blacklist()
    item = next((x for x in blacklist if x["ip"] == data.ip), None)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="添加失败"
        )

    return IPBlacklistResponse(**item)


@router.delete(
    "/{ip}", status_code=status.HTTP_204_NO_CONTENT, summary="从黑名单移除IP"
)
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def remove_ip_from_blacklist(
    request: Request,
    ip: str,
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    从黑名单移除IP

    - 移除后该IP可以立即访问
    """
    # 检查IP是否在黑名单
    if not await check_ip_blacklist(ip):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"IP {ip} 不在黑名单中"
        )

    # 从黑名单移除
    await remove_from_blacklist(ip)

    return None


@router.get("/{ip}", response_model=IPBlacklistResponse, summary="查询IP黑名单状态")
@limiter.limit(RateLimitPresets.ADMIN_READ)
async def check_ip_status(
    request: Request,
    ip: str,
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    查询IP是否在黑名单中

    - 返回封禁详情
    """
    if not await check_ip_blacklist(ip):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"IP {ip} 不在黑名单中"
        )

    blacklist = await get_blacklist()
    item = next((x for x in blacklist if x["ip"] == ip), None)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"IP {ip} 信息未找到"
        )

    return IPBlacklistResponse(**item)


@router.get(
    "/stats/summary", response_model=IPBlacklistStatsResponse, summary="获取黑名单统计"
)
@limiter.limit(RateLimitPresets.ADMIN_READ)
async def get_blacklist_stats(
    request: Request,
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取IP黑名单统计数据

    - 总封禁数
    - 永久封禁数
    - 临时封禁数
    - 自动封禁数(最近7天)
    """
    blacklist = await get_blacklist()

    total_blacklisted = len(blacklist)
    permanent_count = sum(1 for item in blacklist if item["is_permanent"])
    temporary_count = total_blacklisted - permanent_count

    # 统计最近7天自动封禁数
    seven_days_ago = int(time.time()) - (7 * 24 * 60 * 60)
    auto_banned_count = 0

    for item in blacklist:
        banned_at = int(item["banned_at"])
        if banned_at >= seven_days_ago and "Too many failed" in item["reason"]:
            auto_banned_count += 1

    return IPBlacklistStatsResponse(
        total_blacklisted=total_blacklisted,
        permanent_count=permanent_count,
        temporary_count=temporary_count,
        auto_banned_count=auto_banned_count,
    )


@router.post("/batch-remove", status_code=status.HTTP_200_OK, summary="批量移除IP")
@limiter.limit(RateLimitPresets.ADMIN_WRITE)
async def batch_remove_ips(
    request: Request,
    ips: list[str],
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    批量移除多个IP

    - 用于批量解封操作
    """
    removed = []
    failed = []

    for ip in ips:
        try:
            if await check_ip_blacklist(ip):
                await remove_from_blacklist(ip)
                removed.append(ip)
            else:
                failed.append({"ip": ip, "reason": "不在黑名单中"})
        except Exception as e:
            failed.append({"ip": ip, "reason": str(e)})

    return {
        "success": len(removed),
        "failed": len(failed),
        "removed_ips": removed,
        "failed_items": failed,
    }
