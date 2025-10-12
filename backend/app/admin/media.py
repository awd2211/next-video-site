from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.media import Media, MediaStatus, MediaType
from app.models.user import AdminUser
from app.schemas.media import (
    MediaCreate,
    MediaListResponse,
    MediaResponse,
    MediaStatsResponse,
    MediaUpdate,
    MediaUploadResponse,
)
from app.utils.dependencies import get_current_admin_user
from app.utils.minio_client import minio_client

router = APIRouter()


@router.get("/media/stats", response_model=MediaStatsResponse)
async def get_media_stats(
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """获取媒体统计信息"""
    # 总数
    total_count_query = select(func.count()).select_from(Media).where(Media.is_deleted == False)
    total_count_result = await db.execute(total_count_query)
    total_count = total_count_result.scalar()

    # 图片数量
    image_count_query = (
        select(func.count())
        .select_from(Media)
        .where(and_(Media.media_type == MediaType.IMAGE, Media.is_deleted == False))
    )
    image_count_result = await db.execute(image_count_query)
    image_count = image_count_result.scalar()

    # 视频数量
    video_count_query = (
        select(func.count())
        .select_from(Media)
        .where(and_(Media.media_type == MediaType.VIDEO, Media.is_deleted == False))
    )
    video_count_result = await db.execute(video_count_query)
    video_count = video_count_result.scalar()

    # 总大小
    total_size_query = select(func.sum(Media.file_size)).where(Media.is_deleted == False)
    total_size_result = await db.execute(total_size_query)
    total_size = total_size_result.scalar() or 0

    # 总查看次数
    total_views_query = select(func.sum(Media.view_count)).where(Media.is_deleted == False)
    total_views_result = await db.execute(total_views_query)
    total_views = total_views_result.scalar() or 0

    # 总下载次数
    total_downloads_query = select(func.sum(Media.download_count)).where(Media.is_deleted == False)
    total_downloads_result = await db.execute(total_downloads_query)
    total_downloads = total_downloads_result.scalar() or 0

    return MediaStatsResponse(
        total_count=total_count,
        image_count=image_count,
        video_count=video_count,
        total_size=total_size,
        total_views=total_views,
        total_downloads=total_downloads,
    )


@router.get("/media/folders")
async def get_folders(
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """获取所有文件夹列表"""
    query = (
        select(Media.folder, func.count(Media.id).label("count"))
        .where(and_(Media.folder.is_not(None), Media.is_deleted == False))
        .group_by(Media.folder)
        .order_by(Media.folder)
    )

    result = await db.execute(query)
    folders = result.all()

    return [{"name": folder, "count": count} for folder, count in folders]


@router.get("/media", response_model=MediaListResponse)
async def get_media_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    media_type: Optional[MediaType] = None,
    status: Optional[MediaStatus] = None,
    folder: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """获取媒体资源列表"""

    # 构建查询
    query = select(Media).where(Media.is_deleted == False)

    # 过滤条件
    if media_type:
        query = query.where(Media.media_type == media_type)
    if status:
        query = query.where(Media.status == status)
    if folder:
        query = query.where(Media.folder == folder)
    if search:
        search_filter = or_(
            Media.title.ilike(f"%{search}%"),
            Media.description.ilike(f"%{search}%"),
            Media.tags.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    # 总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页和排序
    query = query.order_by(desc(Media.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)

    # 执行查询
    result = await db.execute(query)
    items = result.scalars().all()

    return MediaListResponse(
        items=[MediaResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/media/{media_id}", response_model=MediaResponse)
async def get_media_detail(
    media_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """获取媒体资源详情"""
    result = await db.execute(
        select(Media).where(and_(Media.id == media_id, Media.is_deleted == False))
    )
    media = result.scalar_one_or_none()

    if not media:
        raise HTTPException(status_code=404, detail="媒体资源不存在")

    return MediaResponse.model_validate(media)


@router.post("/media/upload", response_model=MediaUploadResponse)
async def upload_media(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    folder: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """上传媒体文件"""

    # 检查文件类型
    content_type = file.content_type or ""
    if content_type.startswith("image/"):
        media_type = MediaType.IMAGE
    elif content_type.startswith("video/"):
        media_type = MediaType.VIDEO
    else:
        raise HTTPException(status_code=400, detail="不支持的文件类型")

    try:
        # 读取文件内容
        file_content = await file.read()
        file_size = len(file_content)

        # 生成文件路径
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = f"media/{media_type.value}/{filename}"

        # 上传到 MinIO
        object_name = await minio_client.upload_file(
            file_content=file_content,
            object_name=file_path,
            content_type=content_type,
        )

        # 获取文件URL
        url = minio_client.get_file_url(object_name)

        # 创建数据库记录
        media = Media(
            title=title,
            description=description,
            filename=file.filename or "",
            file_path=file_path,
            file_size=file_size,
            mime_type=content_type,
            media_type=media_type,
            status=MediaStatus.READY,
            folder=folder,
            tags=tags,
            url=url,
            uploader_id=current_user.id,
        )

        db.add(media)
        await db.commit()
        await db.refresh(media)

        return MediaUploadResponse(
            id=media.id,
            url=url,
            message="上传成功",
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.put("/media/{media_id}", response_model=MediaResponse)
async def update_media(
    media_id: int,
    media_update: MediaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """更新媒体资源"""
    result = await db.execute(
        select(Media).where(and_(Media.id == media_id, Media.is_deleted == False))
    )
    media = result.scalar_one_or_none()

    if not media:
        raise HTTPException(status_code=404, detail="媒体资源不存在")

    # 更新字段
    update_data = media_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(media, field, value)

    media.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(media)

    return MediaResponse.model_validate(media)


@router.delete("/media/{media_id}")
async def delete_media(
    media_id: int,
    permanent: bool = Query(False, description="是否永久删除"),
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """删除媒体资源"""
    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalar_one_or_none()

    if not media:
        raise HTTPException(status_code=404, detail="媒体资源不存在")

    if permanent:
        # 永久删除
        try:
            # 从 MinIO 删除文件
            await minio_client.delete_file(media.file_path)
            if media.thumbnail_path:
                await minio_client.delete_file(media.thumbnail_path)
        except Exception as e:
            print(f"删除文件失败: {e}")

        await db.delete(media)
    else:
        # 软删除
        media.is_deleted = True
        media.deleted_at = datetime.utcnow()

    await db.commit()

    return {"message": "删除成功"}


@router.post("/media/{media_id}/restore")
async def restore_media(
    media_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """恢复已删除的媒体资源"""
    result = await db.execute(
        select(Media).where(and_(Media.id == media_id, Media.is_deleted == True))
    )
    media = result.scalar_one_or_none()

    if not media:
        raise HTTPException(status_code=404, detail="媒体资源不存在")

    media.is_deleted = False
    media.deleted_at = None

    await db.commit()

    return {"message": "恢复成功"}
