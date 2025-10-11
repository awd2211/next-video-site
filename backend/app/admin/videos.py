import io
import logging
import math
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from slugify import slugify
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import AdminUser
from app.models.video import Video, VideoActor, VideoCategory, VideoDirector, VideoStatus, VideoTag
from app.schemas.video import (
    PaginatedResponse,
    VideoCreate,
    VideoDetailResponse,
    VideoUpdate,
)
from app.tasks.transcode_av1 import transcode_video_dual_format
from app.utils.cache import Cache
from app.utils.dependencies import get_current_admin_user
from app.utils.minio_client import minio_client

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", response_model=PaginatedResponse)
async def admin_list_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    video_type: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get all videos with filters"""
    query = select(Video).options(
        selectinload(Video.video_categories).selectinload(VideoCategory.category),
        selectinload(Video.video_actors).selectinload(VideoActor.actor),
        selectinload(Video.video_directors).selectinload(VideoDirector.director),
        selectinload(Video.video_tags).selectinload(VideoTag.tag),
        selectinload(Video.country)
    )

    # Filters
    if status:
        query = query.filter(Video.status == status)
    if video_type:
        query = query.filter(Video.video_type == video_type)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Video.title.ilike(search_pattern),
                Video.original_title.ilike(search_pattern),
            )
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar() or 0

    # Sort and paginate
    query = query.order_by(desc(Video.created_at))
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    videos = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size) if page_size > 0 and total > 0 else 0,
        "items": videos,
    }


@router.post(
    "", response_model=VideoDetailResponse, status_code=status.HTTP_201_CREATED
)
async def admin_create_video(
    video_data: VideoCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Create a new video"""
    # Generate slug from title
    slug = slugify(video_data.title)

    # Check if slug exists
    result = await db.execute(select(Video).filter(Video.slug == slug))
    if result.scalar_one_or_none():
        # Append timestamp to make it unique
        slug = f"{slug}-{int(datetime.now(timezone.utc).timestamp())}"

    # Create video
    new_video = Video(
        title=video_data.title,
        original_title=video_data.original_title,
        slug=slug,
        description=video_data.description,
        video_type=video_data.video_type,
        status=video_data.status,
        video_url=video_data.video_url,
        trailer_url=video_data.trailer_url,
        poster_url=video_data.poster_url,
        backdrop_url=video_data.backdrop_url,
        release_year=video_data.release_year,
        release_date=video_data.release_date,
        duration=video_data.duration,
        country_id=video_data.country_id,
        language=video_data.language,
        total_seasons=video_data.total_seasons,
        total_episodes=video_data.total_episodes,
    )

    db.add(new_video)
    await db.flush()

    # Batch insert categories (优化：批量插入)
    if video_data.category_ids:
        await db.execute(
            VideoCategory.__table__.insert(),
            [
                {"video_id": new_video.id, "category_id": cid}
                for cid in video_data.category_ids
            ],
        )

    # Batch insert tags (优化：批量插入)
    if video_data.tag_ids:
        await db.execute(
            VideoTag.__table__.insert(),
            [{"video_id": new_video.id, "tag_id": tid} for tid in video_data.tag_ids],
        )

    # Batch insert actors (优化：批量插入)
    if video_data.actor_ids:
        await db.execute(
            VideoActor.__table__.insert(),
            [
                {"video_id": new_video.id, "actor_id": aid}
                for aid in video_data.actor_ids
            ],
        )

    # Batch insert directors (优化：批量插入)
    if video_data.director_ids:
        await db.execute(
            VideoDirector.__table__.insert(),
            [
                {"video_id": new_video.id, "director_id": did}
                for did in video_data.director_ids
            ],
        )

    await db.commit()
    await db.refresh(new_video)

    # 清除相关缓存
    await Cache.delete_pattern("videos_list:*")  # 优化：清除列表缓存
    await Cache.delete_pattern("trending_videos:*")
    await Cache.delete_pattern("featured_videos:*")
    await Cache.delete_pattern("recommended_videos:*")
    await Cache.delete_pattern("search_results:*")

    # 🆕 触发AV1转码任务 (如果有video_url)
    if new_video.video_url:
        try:
            task = transcode_video_dual_format.delay(new_video.id)  # type: ignore[misc]
            logger.info(
                f"✅ AV1转码任务已触发: video_id={new_video.id}, task_id={task.id}"
            )
        except Exception as e:
            logger.error(f"❌ 触发AV1转码失败: video_id={new_video.id}, error={str(e)}")
            # 不阻塞视频创建流程,转码失败只记录日志

    return new_video


@router.get("/{video_id}", response_model=VideoDetailResponse)
async def admin_get_video(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get video details"""
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    return video


@router.put("/{video_id}", response_model=VideoDetailResponse)
async def admin_update_video(
    video_id: int,
    video_data: VideoUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Update video"""
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Update fields
    update_data = video_data.dict(exclude_unset=True)

    # Handle relationships separately
    category_ids = update_data.pop("category_ids", None)
    tag_ids = update_data.pop("tag_ids", None)
    actor_ids = update_data.pop("actor_ids", None)
    director_ids = update_data.pop("director_ids", None)

    # 🆕 检测video_url是否更新
    video_url_updated = (
        "video_url" in update_data and update_data["video_url"] != video.video_url
    )

    # Update basic fields
    for field, value in update_data.items():
        setattr(video, field, value)

    # Update categories if provided (优化：批量操作)
    if category_ids is not None:
        # Remove existing
        await db.execute(
            VideoCategory.__table__.delete().where(VideoCategory.video_id == video_id)
        )
        # Batch insert new
        if category_ids:
            await db.execute(
                VideoCategory.__table__.insert(),
                [{"video_id": video.id, "category_id": cid} for cid in category_ids],
            )

    # Update tags if provided (优化：批量操作)
    if tag_ids is not None:
        await db.execute(
            VideoTag.__table__.delete().where(VideoTag.video_id == video_id)
        )
        if tag_ids:
            await db.execute(
                VideoTag.__table__.insert(),
                [{"video_id": video.id, "tag_id": tid} for tid in tag_ids],
            )

    # Update actors if provided (优化：批量操作)
    if actor_ids is not None:
        await db.execute(
            VideoActor.__table__.delete().where(VideoActor.video_id == video_id)
        )
        if actor_ids:
            await db.execute(
                VideoActor.__table__.insert(),
                [{"video_id": video.id, "actor_id": aid} for aid in actor_ids],
            )

    # Update directors if provided (优化：批量操作)
    if director_ids is not None:
        await db.execute(
            VideoDirector.__table__.delete().where(VideoDirector.video_id == video_id)
        )
        if director_ids:
            await db.execute(
                VideoDirector.__table__.insert(),
                [{"video_id": video.id, "director_id": did} for did in director_ids],
            )

    await db.commit()
    await db.refresh(video)

    # 清除相关缓存
    await Cache.delete_pattern("videos_list:*")  # 优化：清除列表缓存
    await Cache.delete_pattern("trending_videos:*")
    await Cache.delete_pattern("featured_videos:*")
    await Cache.delete_pattern("recommended_videos:*")
    await Cache.delete_pattern("search_results:*")

    # 🆕 如果video_url更新了,触发AV1转码任务
    if video_url_updated and video.video_url:
        try:
            task = transcode_video_dual_format.delay(video.id)  # type: ignore[misc]
            logger.info(
                f"✅ AV1转码任务已触发(更新): video_id={video.id}, task_id={task.id}"
            )
        except Exception as e:
            logger.error(
                f"❌ 触发AV1转码失败(更新): video_id={video.id}, error={str(e)}"
            )

    return video


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_video(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Delete video"""
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    await db.delete(video)
    await db.commit()

    # 清除相关缓存
    await Cache.delete_pattern("videos_list:*")  # 优化：清除列表缓存
    await Cache.delete_pattern("trending_videos:*")
    await Cache.delete_pattern("featured_videos:*")
    await Cache.delete_pattern("recommended_videos:*")
    await Cache.delete_pattern("search_results:*")

    return None


@router.put("/{video_id}/status")
async def admin_update_video_status(
    video_id: int,
    status: VideoStatus,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Update video status"""
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    video.status = status
    if status == VideoStatus.PUBLISHED and not video.published_at:
        video.published_at = datetime.now(timezone.utc)

    await db.commit()

    # 清除相关缓存
    await Cache.delete_pattern("trending_videos:*")
    await Cache.delete_pattern("featured_videos:*")
    await Cache.delete_pattern("recommended_videos:*")
    await Cache.delete_pattern("search_results:*")

    return {"message": "Status updated successfully"}


@router.post("/{video_id}/upload-video")
async def admin_upload_video_file(
    video_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Upload video file"""
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # 验证文件类型
    allowed_types = ["video/mp4", "video/avi", "video/mkv", "video/mov", "video/flv"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, detail="不支持的视频格式，仅支持 MP4, AVI, MKV, MOV, FLV"
        )

    try:
        # 生成文件名
        ext = file.filename.split(".")[-1]
        object_name = f"videos/video_{video_id}_{int(datetime.now(timezone.utc).timestamp())}.{ext}"

        # 上传到 MinIO
        file_content = await file.read()
        video_url = minio_client.upload_video(
            io.BytesIO(file_content),
            object_name,
            file.content_type,
        )

        # 更新视频记录
        video.video_url = video_url
        await db.commit()

        return {"video_url": video_url, "message": "视频上传成功"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.post("/{video_id}/upload-poster")
async def admin_upload_poster(
    video_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Upload video poster/cover"""
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # 验证文件类型
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, detail="不支持的图片格式，仅支持 JPG, PNG, WEBP"
        )

    try:
        # 生成文件名
        ext = file.filename.split(".")[-1]
        object_name = f"posters/poster_{video_id}_{int(datetime.now(timezone.utc).timestamp())}.{ext}"

        # 上传到 MinIO
        file_content = await file.read()
        poster_url = minio_client.upload_image(
            io.BytesIO(file_content),
            object_name,
            file.content_type,
        )

        # 更新视频记录
        video.poster_url = poster_url
        await db.commit()

        return {"poster_url": poster_url, "message": "海报上传成功"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.post("/{video_id}/upload-backdrop")
async def admin_upload_backdrop(
    video_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Upload video backdrop image"""
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # 验证文件类型
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="不支持的图片格式")

    try:
        # 生成文件名
        ext = file.filename.split(".")[-1]
        object_name = f"backdrops/backdrop_{video_id}_{int(datetime.now(timezone.utc).timestamp())}.{ext}"

        # 上传到 MinIO
        file_content = await file.read()
        backdrop_url = minio_client.upload_image(
            io.BytesIO(file_content),
            object_name,
            file.content_type,
        )

        # 更新视频记录
        video.backdrop_url = backdrop_url
        await db.commit()

        return {"backdrop_url": backdrop_url, "message": "背景图上传成功"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")
