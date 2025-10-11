"""
弹幕API - 公共接口
"""

import asyncio
import logging
import re
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.danmaku import BlockedWord, Danmaku, DanmakuStatus, DanmakuType
from app.models.user import User
from app.models.video import Video
from app.schemas.danmaku import (
    DanmakuCreate,
    DanmakuListResponse,
    DanmakuResponse,
)
from app.utils.dependencies import get_current_active_user
from app.utils.rate_limit import RateLimitPresets, limiter

router = APIRouter()
logger = logging.getLogger(__name__)


async def check_regex_with_timeout(
    pattern: str, text: str, timeout: float = 1.0
) -> bool:
    """
    在超时限制内执行正则匹配，防止ReDoS攻击

    Args:
        pattern: 正则表达式
        text: 待匹配文本
        timeout: 超时时间（秒）

    Returns:
        是否匹配（超时返回False）
    """

    def regex_match():
        return re.search(pattern, text, re.IGNORECASE) is not None

    try:
        # 使用asyncio.wait_for设置超时
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(None, regex_match), timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        logger.warning(f"正则表达式执行超时（可能是ReDoS攻击）: {pattern[:50]}")
        return False
    except re.error as e:
        logger.error(f"无效的正则表达式: {pattern[:50]}, error: {e}")
        return False


async def check_blocked_words(content: str, db: AsyncSession) -> bool:
    """检查内容是否包含屏蔽词"""
    result = await db.execute(select(BlockedWord))
    blocked_words = result.scalars().all()

    for word in blocked_words:
        if word.is_regex:
            # 使用超时保护的正则匹配
            if await check_regex_with_timeout(word.word, content, timeout=1.0):
                return True
        else:
            # 简单字符串匹配
            if word.word.lower() in content.lower():
                return True

    return False


@router.post("/", response_model=DanmakuResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimitPresets.COMMENT)  # 弹幕限流: 30/分钟 (与评论相同)
async def send_danmaku(
    request: Request,
    danmaku_data: DanmakuCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    发送弹幕

    - 自动检测屏蔽词
    - 通过审核的弹幕立即显示
    - 包含屏蔽词的弹幕标记为待审核
    """
    # 验证视频存在
    video_result = await db.execute(
        select(Video).filter(
            Video.id == danmaku_data.video_id, Video.status == "published"
        )
    )
    video = video_result.scalar_one_or_none()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="视频不存在或未发布"
        )

    # 检查屏蔽词
    has_blocked_word = await check_blocked_words(danmaku_data.content, db)

    # 创建弹幕
    danmaku = Danmaku(
        video_id=danmaku_data.video_id,
        user_id=current_user.id,
        content=danmaku_data.content,
        time=danmaku_data.time,
        type=danmaku_data.type,
        color=danmaku_data.color,
        font_size=danmaku_data.font_size,
        status=DanmakuStatus.PENDING if has_blocked_word else DanmakuStatus.APPROVED,
        is_blocked=has_blocked_word,
    )

    db.add(danmaku)
    await db.commit()
    await db.refresh(danmaku)

    return DanmakuResponse.model_validate(danmaku)


@router.get("/video/{video_id}", response_model=DanmakuListResponse)
async def get_video_danmaku(
    video_id: int,
    start_time: Optional[float] = Query(None, ge=0, description="起始时间(秒)"),
    end_time: Optional[float] = Query(None, ge=0, description="结束时间(秒)"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取视频弹幕

    - 只返回已通过审核的弹幕
    - 可选时间段筛选 (用于分段加载)
    """
    # 构建查询
    query = select(Danmaku).filter(
        Danmaku.video_id == video_id,
        Danmaku.status == DanmakuStatus.APPROVED,
        Danmaku.is_blocked == False,
    )

    # 时间段筛选
    if start_time is not None:
        query = query.filter(Danmaku.time >= start_time)
    if end_time is not None:
        query = query.filter(Danmaku.time <= end_time)

    # 按时间排序
    query = query.order_by(Danmaku.time.asc())

    # 查询总数
    count_query = (
        select(func.count())
        .select_from(Danmaku)
        .filter(
            Danmaku.video_id == video_id,
            Danmaku.status == DanmakuStatus.APPROVED,
            Danmaku.is_blocked == False,
        )
    )
    if start_time is not None:
        count_query = count_query.filter(Danmaku.time >= start_time)
    if end_time is not None:
        count_query = count_query.filter(Danmaku.time <= end_time)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 执行查询
    result = await db.execute(query)
    danmaku_list = result.scalars().all()

    return DanmakuListResponse(
        total=total, items=[DanmakuResponse.model_validate(d) for d in danmaku_list]
    )


@router.delete("/{danmaku_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_danmaku(
    danmaku_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除自己的弹幕

    - 只能删除自己发送的弹幕
    """
    result = await db.execute(
        select(Danmaku).filter(
            Danmaku.id == danmaku_id, Danmaku.user_id == current_user.id
        )
    )
    danmaku = result.scalar_one_or_none()

    if not danmaku:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="弹幕不存在或无权删除"
        )

    await db.delete(danmaku)
    await db.commit()

    return None


@router.post("/{danmaku_id}/report", status_code=status.HTTP_200_OK)
async def report_danmaku(
    danmaku_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    举报弹幕

    - 举报次数达到阈值后自动屏蔽
    """
    result = await db.execute(select(Danmaku).filter(Danmaku.id == danmaku_id))
    danmaku = result.scalar_one_or_none()

    if not danmaku:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="弹幕不存在")

    # 增加举报次数
    danmaku.report_count += 1

    # 举报次数达到5次自动屏蔽
    if danmaku.report_count >= 5:
        danmaku.is_blocked = True
        danmaku.status = DanmakuStatus.DELETED

    await db.commit()

    return {"message": "举报成功", "report_count": danmaku.report_count}


@router.get("/my-danmaku", response_model=List[DanmakuResponse])
async def get_my_danmaku(
    video_id: Optional[int] = Query(None, description="视频ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取我发送的弹幕

    - 可按视频筛选
    - 支持分页
    """
    query = select(Danmaku).filter(Danmaku.user_id == current_user.id)

    if video_id:
        query = query.filter(Danmaku.video_id == video_id)

    query = query.order_by(Danmaku.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    danmaku_list = result.scalars().all()

    return [DanmakuResponse.model_validate(d) for d in danmaku_list]
