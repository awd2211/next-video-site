from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import Optional
from app.database import get_db
from app.models.comment import Comment, CommentStatus
from app.models.user import User
from app.models.video import Video
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    PaginatedCommentResponse,
    UserBrief,
)
from app.utils.dependencies import get_current_user, get_current_active_user
from app.utils.notification_service import NotificationService

router = APIRouter()


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new comment on a video.
    Users can reply to existing comments by providing parent_id.
    """
    # Verify video exists
    video_result = await db.execute(select(Video).where(Video.id == comment_data.video_id))
    video = video_result.scalar_one_or_none()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    # Verify parent comment exists if provided
    parent = None
    if comment_data.parent_id:
        parent_result = await db.execute(
            select(Comment).where(
                and_(
                    Comment.id == comment_data.parent_id,
                    Comment.video_id == comment_data.video_id
                )
            ).options(selectinload(Comment.user))
        )
        parent = parent_result.scalar_one_or_none()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found"
            )

    # Create comment
    new_comment = Comment(
        video_id=comment_data.video_id,
        user_id=current_user.id,
        parent_id=comment_data.parent_id,
        content=comment_data.content,
        status=CommentStatus.APPROVED,  # Auto-approve for now
    )

    db.add(new_comment)

    # Update video comment count
    video.comment_count += 1

    await db.commit()
    await db.refresh(new_comment)

    # Load user relationship
    await db.refresh(new_comment, ["user"])

    # 🆕 发送通知 (如果是回复评论)
    if parent and parent.user_id != current_user.id:
        try:
            await NotificationService.notify_comment_reply(
                db=db,
                target_user_id=parent.user_id,
                replier_name=current_user.username or current_user.email,
                reply_content=comment_data.content,
                video_id=comment_data.video_id,
                comment_id=new_comment.id,
            )
        except Exception as e:
            # 通知失败不影响评论创建
            print(f"发送通知失败: {e}")

    # Build response
    response_data = CommentResponse.model_validate(new_comment)
    response_data.reply_count = 0
    return response_data


@router.get("/video/{video_id}", response_model=PaginatedCommentResponse)
async def get_video_comments(
    video_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    parent_id: Optional[int] = Query(None, description="Filter by parent comment ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get comments for a specific video.
    If parent_id is provided, returns replies to that comment.
    Otherwise, returns top-level comments.
    """
    # Build base query
    query = select(Comment).where(Comment.video_id == video_id)

    # Filter by parent_id or get top-level comments
    if parent_id is not None:
        query = query.where(Comment.parent_id == parent_id)
    else:
        query = query.where(Comment.parent_id.is_(None))

    # Only show approved comments
    query = query.where(Comment.status == CommentStatus.APPROVED)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated comments
    query = (
        query
        .options(selectinload(Comment.user))
        .order_by(Comment.is_pinned.desc(), Comment.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    comments = result.scalars().all()

    # Get reply counts for each comment
    comment_ids = [comment.id for comment in comments]
    if comment_ids:
        reply_count_query = (
            select(Comment.parent_id, func.count(Comment.id).label("count"))
            .where(
                and_(
                    Comment.parent_id.in_(comment_ids),
                    Comment.status == CommentStatus.APPROVED
                )
            )
            .group_by(Comment.parent_id)
        )
        reply_counts_result = await db.execute(reply_count_query)
        reply_counts = {parent_id: count for parent_id, count in reply_counts_result.all()}
    else:
        reply_counts = {}

    # Build response items
    items = []
    for comment in comments:
        comment_data = CommentResponse.model_validate(comment)
        comment_data.reply_count = reply_counts.get(comment.id, 0)
        items.append(comment_data)

    return PaginatedCommentResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific comment by ID"""
    query = (
        select(Comment)
        .where(Comment.id == comment_id)
        .options(selectinload(Comment.user))
    )

    result = await db.execute(query)
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Get reply count
    reply_count_query = select(func.count()).where(
        and_(
            Comment.parent_id == comment_id,
            Comment.status == CommentStatus.APPROVED
        )
    )
    reply_count_result = await db.execute(reply_count_query)
    reply_count = reply_count_result.scalar()

    comment_data = CommentResponse.model_validate(comment)
    comment_data.reply_count = reply_count
    return comment_data


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a comment (only by the comment owner)"""
    query = select(Comment).where(Comment.id == comment_id)
    result = await db.execute(query)
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own comments"
        )

    # Update comment
    comment.content = comment_data.content
    await db.commit()
    await db.refresh(comment, ["user"])

    # Get reply count
    reply_count_query = select(func.count()).where(
        and_(
            Comment.parent_id == comment_id,
            Comment.status == CommentStatus.APPROVED
        )
    )
    reply_count_result = await db.execute(reply_count_query)
    reply_count = reply_count_result.scalar()

    comment_response = CommentResponse.model_validate(comment)
    comment_response.reply_count = reply_count
    return comment_response


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a comment (only by the comment owner)"""
    query = select(Comment).where(Comment.id == comment_id)
    result = await db.execute(query)
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments"
        )

    # Update video comment count
    video_result = await db.execute(select(Video).where(Video.id == comment.video_id))
    video = video_result.scalar_one_or_none()
    if video and video.comment_count > 0:
        video.comment_count -= 1

    # Delete comment (cascade will handle replies)
    await db.delete(comment)
    await db.commit()

    return None


@router.get("/user/me", response_model=PaginatedCommentResponse)
async def get_my_comments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's comments"""
    # Count total
    count_query = select(func.count()).where(Comment.user_id == current_user.id)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated comments
    query = (
        select(Comment)
        .where(Comment.user_id == current_user.id)
        .options(selectinload(Comment.user))
        .order_by(Comment.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    comments = result.scalars().all()

    # Get reply counts
    comment_ids = [comment.id for comment in comments]
    if comment_ids:
        reply_count_query = (
            select(Comment.parent_id, func.count(Comment.id).label("count"))
            .where(Comment.parent_id.in_(comment_ids))
            .group_by(Comment.parent_id)
        )
        reply_counts_result = await db.execute(reply_count_query)
        reply_counts = {parent_id: count for parent_id, count in reply_counts_result.all()}
    else:
        reply_counts = {}

    # Build response items
    items = []
    for comment in comments:
        comment_data = CommentResponse.model_validate(comment)
        comment_data.reply_count = reply_counts.get(comment.id, 0)
        items.append(comment_data)

    return PaginatedCommentResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.post("/{comment_id}/like", status_code=status.HTTP_200_OK)
async def like_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Like a comment (increment like count)"""
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    comment.like_count += 1
    await db.commit()

    return {"like_count": comment.like_count}


@router.delete("/{comment_id}/like", status_code=status.HTTP_200_OK)
async def unlike_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Unlike a comment (decrement like count)"""
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    comment.like_count = max(0, comment.like_count - 1)
    await db.commit()

    return {"like_count": comment.like_count}
