"""
弹幕管理后台API
"""

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete as sql_delete
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.danmaku import BlockedWord, Danmaku, DanmakuStatus
from app.models.user import AdminUser
from app.schemas.danmaku import (
    BlockedWordCreate,
    BlockedWordResponse,
    DanmakuAdminResponse,
    DanmakuReviewAction,
    DanmakuSearchParams,
    DanmakuStatsResponse,
)
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


@router.get("/stats", response_model=DanmakuStatsResponse)
async def get_danmaku_stats(
    admin_user: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """获取弹幕统计"""
    # 总数
    total_result = await db.execute(select(func.count(Danmaku.id)))
    total = total_result.scalar() or 0

    # 各状态统计
    pending_result = await db.execute(
        select(func.count(Danmaku.id)).filter(Danmaku.status == DanmakuStatus.PENDING)
    )
    pending = pending_result.scalar() or 0

    approved_result = await db.execute(
        select(func.count(Danmaku.id)).filter(Danmaku.status == DanmakuStatus.APPROVED)
    )
    approved = approved_result.scalar() or 0

    rejected_result = await db.execute(
        select(func.count(Danmaku.id)).filter(Danmaku.status == DanmakuStatus.REJECTED)
    )
    rejected = rejected_result.scalar() or 0

    deleted_result = await db.execute(
        select(func.count(Danmaku.id)).filter(Danmaku.status == DanmakuStatus.DELETED)
    )
    deleted = deleted_result.scalar() or 0

    # 被屏蔽统计
    blocked_result = await db.execute(
        select(func.count(Danmaku.id)).filter(Danmaku.is_blocked.is_(True))
    )
    blocked = blocked_result.scalar() or 0

    # 今日弹幕数
    today = datetime.now(timezone.utc).date()
    today_result = await db.execute(
        select(func.count(Danmaku.id)).filter(func.date(Danmaku.created_at) == today)
    )
    today_count = today_result.scalar() or 0

    # 被举报弹幕数 (举报次数 > 0)
    reported_result = await db.execute(
        select(func.count(Danmaku.id)).filter(Danmaku.report_count > 0)
    )
    reported_count = reported_result.scalar() or 0

    return DanmakuStatsResponse(
        total=total,
        pending=pending,
        approved=approved,
        rejected=rejected,
        deleted=deleted,
        blocked=blocked,
        today_count=today_count,
        reported_count=reported_count,
    )


@router.post("/search", response_model=dict)
async def search_danmaku(
    search_params: DanmakuSearchParams,
    admin_user: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    搜索弹幕 (管理后台)

    - 支持多维度筛选
    - 支持关键词搜索
    - 返回用户信息
    """
    query = select(Danmaku).options(selectinload(Danmaku.user))

    # 视频ID筛选
    if search_params.video_id:
        query = query.filter(Danmaku.video_id == search_params.video_id)

    # 用户ID筛选
    if search_params.user_id:
        query = query.filter(Danmaku.user_id == search_params.user_id)

    # 状态筛选
    if search_params.status:
        query = query.filter(Danmaku.status == search_params.status)

    # 屏蔽状态筛选
    if search_params.is_blocked is not None:
        query = query.filter(Danmaku.is_blocked == search_params.is_blocked)

    # 关键词搜索
    if search_params.keyword:
        query = query.filter(Danmaku.content.ilike(f"%{search_params.keyword}%"))

    # 日期范围筛选
    if search_params.start_date:
        query = query.filter(Danmaku.created_at >= search_params.start_date)
    if search_params.end_date:
        query = query.filter(Danmaku.created_at <= search_params.end_date)

    # 查询总数
    count_query = select(func.count()).select_from(Danmaku)
    if search_params.video_id:
        count_query = count_query.filter(Danmaku.video_id == search_params.video_id)
    if search_params.user_id:
        count_query = count_query.filter(Danmaku.user_id == search_params.user_id)
    if search_params.status:
        count_query = count_query.filter(Danmaku.status == search_params.status)
    if search_params.is_blocked is not None:
        count_query = count_query.filter(Danmaku.is_blocked == search_params.is_blocked)
    if search_params.keyword:
        count_query = count_query.filter(
            Danmaku.content.ilike(f"%{search_params.keyword}%")
        )
    if search_params.start_date:
        count_query = count_query.filter(Danmaku.created_at >= search_params.start_date)
    if search_params.end_date:
        count_query = count_query.filter(Danmaku.created_at <= search_params.end_date)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页和排序
    query = query.order_by(Danmaku.created_at.desc())
    query = query.offset((search_params.page - 1) * search_params.page_size)
    query = query.limit(search_params.page_size)

    # 执行查询
    result = await db.execute(query)
    danmaku_list = result.scalars().all()

    # 构建响应 (包含用户信息)
    items = []
    for d in danmaku_list:
        danmaku_dict = DanmakuAdminResponse.model_validate(d).model_dump()
        if d.user:
            danmaku_dict["user"] = {
                "id": d.user.id,
                "username": d.user.username,
                "email": d.user.email,
            }
        items.append(danmaku_dict)

    return {
        "total": total,
        "page": search_params.page,
        "page_size": search_params.page_size,
        "items": items,
    }


@router.post("/review", status_code=status.HTTP_200_OK)
async def review_danmaku(
    review_action: DanmakuReviewAction,
    admin_user: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    弹幕审核操作

    - approve: 通过审核
    - reject: 拒绝
    - delete: 删除
    - block: 屏蔽
    """
    # 验证弹幕是否存在
    result = await db.execute(
        select(func.count(Danmaku.id)).filter(Danmaku.id.in_(review_action.danmaku_ids))
    )
    count = result.scalar() or 0

    if count != len(review_action.danmaku_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="部分弹幕不存在"
        )

    # 批量更新操作（优化：使用bulk update）
    update_values = {
        "reviewed_by": admin_user.id,
        "reviewed_at": datetime.now(timezone.utc),
    }

    if review_action.action == "approve":
        update_values["status"] = DanmakuStatus.APPROVED
        update_values["is_blocked"] = False
    elif review_action.action == "reject":
        update_values["status"] = DanmakuStatus.REJECTED
        update_values["reject_reason"] = review_action.reject_reason
    elif review_action.action == "delete":
        update_values["status"] = DanmakuStatus.DELETED
    elif review_action.action == "block":
        update_values["is_blocked"] = True
        update_values["status"] = DanmakuStatus.DELETED

    await db.execute(
        update(Danmaku)
        .where(Danmaku.id.in_(review_action.danmaku_ids))
        .values(**update_values)
    )

    await db.commit()

    # 🆕 发送弹幕审核通知
    try:
        from app.utils.admin_notification_service import AdminNotificationService

        await AdminNotificationService.notify_danmaku_management(
            db=db,
            danmaku_id=review_action.danmaku_ids[0] if len(review_action.danmaku_ids) == 1 else 0,
            action=review_action.action,
            admin_username=admin_user.username,
            danmaku_count=len(review_action.danmaku_ids),
        )
    except Exception as e:
        print(f"Failed to send danmaku review notification: {e}")

    return {"message": f"已处理 {len(review_action.danmaku_ids)} 条弹幕"}


@router.delete("/{danmaku_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_danmaku(
    danmaku_id: int,
    admin_user: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """删除弹幕 (物理删除)"""
    result = await db.execute(select(Danmaku).filter(Danmaku.id == danmaku_id))
    danmaku = result.scalar_one_or_none()

    if not danmaku:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="弹幕不存在")

    await db.delete(danmaku)
    await db.commit()

    return None


@router.delete("/batch", status_code=status.HTTP_200_OK)
async def batch_delete_danmaku(
    danmaku_ids: List[int],
    admin_user: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """批量删除弹幕"""
    await db.execute(sql_delete(Danmaku).where(Danmaku.id.in_(danmaku_ids)))
    await db.commit()

    # 🆕 发送批量删除弹幕通知
    try:
        from app.utils.admin_notification_service import AdminNotificationService

        await AdminNotificationService.notify_danmaku_management(
            db=db,
            danmaku_id=danmaku_ids[0] if len(danmaku_ids) == 1 else 0,
            action="deleted",
            admin_username=admin_user.username,
            danmaku_count=len(danmaku_ids),
        )
    except Exception as e:
        print(f"Failed to send batch danmaku deletion notification: {e}")

    return {"message": f"已删除 {len(danmaku_ids)} 条弹幕"}


# ============ 屏蔽词管理 ============


@router.get("/blocked-words", response_model=List[BlockedWordResponse])
async def get_blocked_words(
    admin_user: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """获取屏蔽词列表"""
    result = await db.execute(
        select(BlockedWord).order_by(BlockedWord.created_at.desc())
    )
    blocked_words = result.scalars().all()

    return [BlockedWordResponse.model_validate(w) for w in blocked_words]


@router.post(
    "/blocked-words",
    response_model=BlockedWordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_blocked_word(
    word_data: BlockedWordCreate,
    admin_user: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """添加屏蔽词"""
    # 检查是否已存在
    result = await db.execute(
        select(BlockedWord).filter(BlockedWord.word == word_data.word)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="该屏蔽词已存在"
        )

    # 创建屏蔽词
    blocked_word = BlockedWord(
        word=word_data.word,
        is_regex=word_data.is_regex,
        created_by=admin_user.id,
    )

    db.add(blocked_word)
    await db.commit()
    await db.refresh(blocked_word)

    return BlockedWordResponse.model_validate(blocked_word)


@router.delete("/blocked-words/{word_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blocked_word(
    word_id: int,
    admin_user: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """删除屏蔽词"""
    result = await db.execute(select(BlockedWord).filter(BlockedWord.id == word_id))
    blocked_word = result.scalar_one_or_none()

    if not blocked_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="屏蔽词不存在"
        )

    await db.delete(blocked_word)
    await db.commit()

    return None
