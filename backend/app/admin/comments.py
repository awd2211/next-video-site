from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.comment import Comment, CommentStatus
from app.models.user import AdminUser
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


@router.get("")
async def admin_list_comments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    search: str = Query(""),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get all comments with filters"""
    query = select(Comment).options(
        selectinload(Comment.user), selectinload(Comment.video)
    )

    # Filter by status
    if status and status != "all":
        if status == "pending":
            query = query.filter(Comment.status == CommentStatus.PENDING)
        elif status == "approved":
            query = query.filter(Comment.status == CommentStatus.APPROVED)
        elif status == "rejected":
            query = query.filter(Comment.status == CommentStatus.REJECTED)

    # Search by content or username
    if search:
        query = query.filter(
            or_(
                Comment.content.ilike(f"%{search}%"),
            )
        )

    # Get total count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(Comment.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    comments = result.scalars().all()

    return {"total": total, "page": page, "page_size": page_size, "items": comments}


@router.get("/pending")
async def admin_list_pending_comments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get pending comments"""
    query = (
        select(Comment)
        .options(selectinload(Comment.user), selectinload(Comment.video))
        .filter(Comment.status == CommentStatus.PENDING)
    )

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    offset = (page - 1) * page_size
    query = query.order_by(Comment.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    comments = result.scalars().all()

    return {"total": total, "page": page, "page_size": page_size, "items": comments}


@router.put("/{comment_id}/approve")
async def admin_approve_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Approve comment"""
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.status = CommentStatus.APPROVED
    await db.commit()
    return {"message": "Comment approved"}


@router.put("/{comment_id}/reject")
async def admin_reject_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Reject comment"""
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.status = CommentStatus.REJECTED
    await db.commit()
    return {"message": "Comment rejected"}


@router.delete("/{comment_id}")
async def admin_delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Delete comment"""
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    await db.delete(comment)
    await db.commit()
    return {"message": "Comment deleted"}


@router.put("/batch/approve")
async def admin_batch_approve_comments(
    comment_ids: list[int],
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Batch approve comments"""
    result = await db.execute(select(Comment).filter(Comment.id.in_(comment_ids)))
    comments = result.scalars().all()

    for comment in comments:
        comment.status = CommentStatus.APPROVED

    await db.commit()
    return {"message": f"{len(comments)} comments approved"}


@router.put("/batch/reject")
async def admin_batch_reject_comments(
    comment_ids: list[int],
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Batch reject comments"""
    result = await db.execute(select(Comment).filter(Comment.id.in_(comment_ids)))
    comments = result.scalars().all()

    for comment in comments:
        comment.status = CommentStatus.REJECTED

    await db.commit()
    return {"message": f"{len(comments)} comments rejected"}


@router.delete("/batch")
async def admin_batch_delete_comments(
    comment_ids: list[int],
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Batch delete comments"""
    result = await db.execute(select(Comment).filter(Comment.id.in_(comment_ids)))
    comments = result.scalars().all()

    for comment in comments:
        await db.delete(comment)

    await db.commit()
    return {"message": f"{len(comments)} comments deleted"}


@router.get("/stats")
async def admin_get_comment_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get comment statistics"""
    from app.models.comment import CommentStatus

    # Total comments
    total_result = await db.execute(select(func.count(Comment.id)))
    total_comments = total_result.scalar() or 0

    # Pending comments
    pending_result = await db.execute(
        select(func.count(Comment.id)).where(Comment.status == CommentStatus.PENDING)
    )
    pending_comments = pending_result.scalar() or 0

    # Approved comments
    approved_result = await db.execute(
        select(func.count(Comment.id)).where(Comment.status == CommentStatus.APPROVED)
    )
    approved_comments = approved_result.scalar() or 0

    # Rejected comments
    rejected_result = await db.execute(
        select(func.count(Comment.id)).where(Comment.status == CommentStatus.REJECTED)
    )
    rejected_comments = rejected_result.scalar() or 0

    return {
        "total_comments": total_comments,
        "pending_comments": pending_comments,
        "approved_comments": approved_comments,
        "rejected_comments": rejected_comments,
    }
