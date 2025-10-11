"""
管理员视频管理 API
"""

import io
import math
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import AdminUser
from app.models.video import (
    Country,
    Video,
    VideoCategory,
    VideoStatus,
    VideoTag,
    VideoType,
)
from app.schemas.video import PaginatedResponse, VideoCreate, VideoResponse, VideoUpdate
from app.utils.dependencies import get_current_admin_user
from app.utils.minio_client import minio_client

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_videos_admin(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[VideoStatus] = None,
    video_type: Optional[VideoType] = None,
    country_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取视频列表（管理员）"""
    query = select(Video)

    # 搜索过滤
    if search:
        query = query.filter(
            or_(
                Video.title.ilike(f"%{search}%"),
                Video.description.ilike(f"%{search}%"),
            )
        )

    # 状态过滤
    if status:
        query = query.filter(Video.status == status)

    # 类型过滤
    if video_type:
        query = query.filter(Video.video_type == video_type)

    # 国家过滤
    if country_id:
        query = query.filter(Video.country_id == country_id)

    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar()

    # 排序和分页
    query = query.order_by(desc(Video.created_at))
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    videos = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size) if page_size > 0 else 0,
        "items": videos,
    }


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video_admin(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取视频详情（管理员）"""
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    return video


@router.post("", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def create_video(
    video_data: VideoCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """创建视频"""
    # 验证国家是否存在
    if video_data.country_id:
        result = await db.execute(
            select(Country).filter(Country.id == video_data.country_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="国家不存在")

    # 创建视频
    video_dict = video_data.dict(exclude={"category_ids", "tag_ids"})
    video = Video(**video_dict)
    db.add(video)
    await db.flush()

    # 添加分类关联
    if video_data.category_ids:
        for cat_id in video_data.category_ids:
            video_cat = VideoCategory(video_id=video.id, category_id=cat_id)
            db.add(video_cat)

    # 添加标签关联
    if video_data.tag_ids:
        for tag_id in video_data.tag_ids:
            video_tag = VideoTag(video_id=video.id, tag_id=tag_id)
            db.add(video_tag)

    await db.commit()
    await db.refresh(video)

    return video


@router.put("/{video_id}", response_model=VideoResponse)
async def update_video(
    video_id: int,
    video_data: VideoUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """更新视频"""
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    # 验证国家是否存在
    if video_data.country_id:
        result = await db.execute(
            select(Country).filter(Country.id == video_data.country_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="国家不存在")

    # 更新基本字段
    update_dict = video_data.dict(
        exclude_unset=True, exclude={"category_ids", "tag_ids"}
    )
    for key, value in update_dict.items():
        setattr(video, key, value)

    # 更新分类关联
    if video_data.category_ids is not None:
        # 删除旧的关联
        await db.execute(
            select(VideoCategory).filter(VideoCategory.video_id == video_id)
        )
        # 添加新的关联
        for cat_id in video_data.category_ids:
            video_cat = VideoCategory(video_id=video.id, category_id=cat_id)
            db.add(video_cat)

    # 更新标签关联
    if video_data.tag_ids is not None:
        # 删除旧的关联
        await db.execute(select(VideoTag).filter(VideoTag.video_id == video_id))
        # 添加新的关联
        for tag_id in video_data.tag_ids:
            video_tag = VideoTag(video_id=video.id, tag_id=tag_id)
            db.add(video_tag)

    await db.commit()
    await db.refresh(video)

    return video


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """删除视频"""
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    # 删除 MinIO 中的视频文件
    if video.video_url:
        try:
            # 从 URL 提取对象名称
            object_name = video.video_url.split("/")[-1]
            minio_client.delete_file(f"videos/{object_name}")
        except Exception as e:
            print(f"删除视频文件失败: {e}")

    # 删除封面图片
    if video.cover_image:
        try:
            object_name = video.cover_image.split("/")[-1]
            minio_client.delete_file(f"covers/{object_name}")
        except Exception as e:
            print(f"删除封面图片失败: {e}")

    await db.delete(video)
    await db.commit()


@router.post("/{video_id}/upload-cover", response_model=dict)
async def upload_cover_image(
    video_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """上传视频封面图片"""
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    # 验证文件类型
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="不支持的文件类型")

    try:
        # 生成文件名
        ext = file.filename.split(".")[-1]
        object_name = f"covers/video_{video_id}_{datetime.now().timestamp()}.{ext}"

        # 上传到 MinIO
        file_content = await file.read()
        cover_url = minio_client.upload_image(
            io.BytesIO(file_content),
            object_name,
            file.content_type,
        )

        # 更新视频记录
        video.cover_image = cover_url
        await db.commit()

        return {"cover_url": cover_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/stats/overview", response_model=dict)
async def get_video_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取视频统计数据"""
    # 总视频数
    total_result = await db.execute(select(func.count(Video.id)))
    total_videos = total_result.scalar()

    # 已发布视频数
    published_result = await db.execute(
        select(func.count(Video.id)).filter(Video.status == VideoStatus.PUBLISHED)
    )
    published_videos = published_result.scalar()

    # 草稿数
    draft_result = await db.execute(
        select(func.count(Video.id)).filter(Video.status == VideoStatus.DRAFT)
    )
    draft_videos = draft_result.scalar()

    # 总播放量
    views_result = await db.execute(select(func.sum(Video.view_count)))
    total_views = views_result.scalar() or 0

    return {
        "total_videos": total_videos,
        "published_videos": published_videos,
        "draft_videos": draft_videos,
        "total_views": total_views,
    }
