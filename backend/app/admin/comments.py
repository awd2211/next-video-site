from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.comment import Comment, CommentStatus
from app.models.user import AdminUser
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


@router.get("/pending")
async def admin_list_pending_comments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get pending comments"""
    query = select(Comment).filter(Comment.status == CommentStatus.PENDING)
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
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
