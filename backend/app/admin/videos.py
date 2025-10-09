from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.models.video import Video, VideoCategory, VideoTag, VideoActor, VideoDirector
from app.models.user import AdminUser
from app.schemas.video import VideoDetailResponse, VideoCreate, VideoUpdate, PaginatedResponse
from app.utils.dependencies import get_current_admin_user
from app.utils.minio_client import minio_client
from app.utils.cache import Cache
from slugify import slugify
import io

router = APIRouter()


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
    query = select(Video)

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
    total = result.scalar()

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
        "items": videos,
    }


@router.post("", response_model=VideoDetailResponse, status_code=status.HTTP_201_CREATED)
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
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"

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

    # Add categories
    for category_id in video_data.category_ids:
        video_category = VideoCategory(video_id=new_video.id, category_id=category_id)
        db.add(video_category)

    # Add tags
    for tag_id in video_data.tag_ids:
        video_tag = VideoTag(video_id=new_video.id, tag_id=tag_id)
        db.add(video_tag)

    # Add actors
    for actor_id in video_data.actor_ids:
        video_actor = VideoActor(video_id=new_video.id, actor_id=actor_id)
        db.add(video_actor)

    # Add directors
    for director_id in video_data.director_ids:
        video_director = VideoDirector(video_id=new_video.id, director_id=director_id)
        db.add(video_director)

    await db.commit()
    await db.refresh(new_video)

    # 清除相关缓存
    await Cache.delete_pattern("trending_videos:*")
    await Cache.delete_pattern("featured_videos:*")
    await Cache.delete_pattern("recommended_videos:*")
    await Cache.delete_pattern("search_results:*")

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

    # Update basic fields
    for field, value in update_data.items():
        setattr(video, field, value)

    # Update categories if provided
    if category_ids is not None:
        # Remove existing
        await db.execute(select(VideoCategory).filter(VideoCategory.video_id == video_id))
        # Add new
        for category_id in category_ids:
            video_category = VideoCategory(video_id=video.id, category_id=category_id)
            db.add(video_category)

    await db.commit()
    await db.refresh(video)

    # 清除相关缓存
    await Cache.delete_pattern("trending_videos:*")
    await Cache.delete_pattern("featured_videos:*")
    await Cache.delete_pattern("recommended_videos:*")
    await Cache.delete_pattern("search_results:*")

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
    await Cache.delete_pattern("trending_videos:*")
    await Cache.delete_pattern("featured_videos:*")
    await Cache.delete_pattern("recommended_videos:*")
    await Cache.delete_pattern("search_results:*")

    return None


@router.put("/{video_id}/status")
async def admin_update_video_status(
    video_id: int,
    status: str,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Update video status"""
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    video.status = status
    if status == "published" and not video.published_at:
        video.published_at = datetime.utcnow()

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
        raise HTTPException(status_code=400, detail=f"不支持的视频格式，仅支持 MP4, AVI, MKV, MOV, FLV")

    try:
        # 生成文件名
        ext = file.filename.split(".")[-1]
        object_name = f"videos/video_{video_id}_{int(datetime.utcnow().timestamp())}.{ext}"

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
        raise HTTPException(status_code=400, detail="不支持的图片格式，仅支持 JPG, PNG, WEBP")

    try:
        # 生成文件名
        ext = file.filename.split(".")[-1]
        object_name = f"posters/poster_{video_id}_{int(datetime.utcnow().timestamp())}.{ext}"

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
        object_name = f"backdrops/backdrop_{video_id}_{int(datetime.utcnow().timestamp())}.{ext}"

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
