from datetime import datetime, timedelta
from typing import List, Optional
import uuid
import os
import shutil

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.media import Media, MediaStatus, MediaType
from app.models.upload_session import UploadSession
from app.models.user import AdminUser
from app.schemas.media import (
    MediaListResponse,
    MediaResponse,
    MediaStatsResponse,
    MediaUpdate,
    MediaUploadResponse,
)
from app.utils.dependencies import get_current_admin_user
from app.utils.minio_client import minio_client

router = APIRouter()


# ==================== 文件夹树形结构 API ====================

@router.get("/media/tree")
async def get_media_tree(
    parent_id: Optional[int] = Query(None, description="父文件夹ID，NULL获取根目录"),
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """
    获取文件夹树形结构
    - 返回指定父文件夹下的所有子文件夹（递归）
    - parent_id=None 返回根目录
    """

    async def build_tree(parent_id: Optional[int]) -> List[dict]:
        """递归构建文件夹树"""
        query = select(Media).where(
            and_(
                Media.parent_id == parent_id,
                Media.is_folder == True,
                Media.is_deleted == False
            )
        ).order_by(Media.title)

        result = await db.execute(query)
        folders = result.scalars().all()

        tree = []
        for folder in folders:
            # 统计子项数量（文件夹 + 文件）
            count_query = select(func.count()).select_from(Media).where(
                and_(Media.parent_id == folder.id, Media.is_deleted == False)
            )
            count_result = await db.execute(count_query)
            children_count = count_result.scalar()

            # 递归获取子文件夹
            children = await build_tree(folder.id)

            tree.append({
                "id": folder.id,
                "title": folder.title,
                "parent_id": folder.parent_id,
                "path": folder.path or folder.get_full_path(),
                "children_count": children_count,
                "children": children,
                "created_at": folder.created_at.isoformat() if folder.created_at else None,
            })

        return tree

    tree = await build_tree(parent_id)

    return {
        "tree": tree,
        "parent_id": parent_id
    }


@router.post("/media/folders/create")
async def create_folder(
    title: str = Query(..., min_length=1, max_length=255),
    parent_id: Optional[int] = Query(None, description="父文件夹ID"),
    description: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """创建文件夹"""

    # 检查父文件夹是否存在
    if parent_id is not None:
        parent_query = select(Media).where(
            and_(Media.id == parent_id, Media.is_folder == True, Media.is_deleted == False)
        )
        parent_result = await db.execute(parent_query)
        parent = parent_result.scalar_one_or_none()

        if not parent:
            raise HTTPException(status_code=404, detail="父文件夹不存在")

        # 构建路径
        path = f"{parent.path or parent.get_full_path()}/{title}"
    else:
        path = f"/{title}"

    # 检查同级是否存在同名文件夹
    check_query = select(Media).where(
        and_(
            Media.parent_id == parent_id,
            Media.title == title,
            Media.is_folder == True,
            Media.is_deleted == False
        )
    )
    check_result = await db.execute(check_query)
    existing = check_result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="同名文件夹已存在")

    # 创建文件夹
    folder = Media(
        title=title,
        description=description,
        filename=title,
        file_path=f"folders/{uuid.uuid4()}",  # 虚拟路径
        file_size=0,
        media_type=MediaType.IMAGE,  # 文件夹默认类型
        status=MediaStatus.READY,
        is_folder=True,
        parent_id=parent_id,
        path=path,
        uploader_id=current_user.id,
    )

    db.add(folder)
    await db.commit()
    await db.refresh(folder)

    return {
        "id": folder.id,
        "title": folder.title,
        "path": folder.path,
        "parent_id": folder.parent_id,
        "message": "文件夹创建成功"
    }


@router.put("/media/{media_id}/move")
async def move_media(
    media_id: int,
    target_parent_id: Optional[int] = Query(None, description="目标父文件夹ID"),
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """移动文件或文件夹"""

    # 获取要移动的项
    media_query = select(Media).where(
        and_(Media.id == media_id, Media.is_deleted == False)
    )
    media_result = await db.execute(media_query)
    media = media_result.scalar_one_or_none()

    if not media:
        raise HTTPException(status_code=404, detail="文件或文件夹不存在")

    # 检查目标父文件夹
    if target_parent_id is not None:
        target_query = select(Media).where(
            and_(Media.id == target_parent_id, Media.is_folder == True, Media.is_deleted == False)
        )
        target_result = await db.execute(target_query)
        target = target_result.scalar_one_or_none()

        if not target:
            raise HTTPException(status_code=404, detail="目标文件夹不存在")

        # 防止将文件夹移动到自己的子文件夹
        if media.is_folder:
            if target.path and media.path and target.path.startswith(media.path):
                raise HTTPException(status_code=400, detail="不能将文件夹移动到其子文件夹")

        new_path = f"{target.path or target.get_full_path()}/{media.title}"
    else:
        new_path = f"/{media.title}"

    # 更新路径
    media.parent_id = target_parent_id
    media.path = new_path
    media.updated_at = datetime.utcnow()

    # 如果是文件夹，递归更新所有子项的路径
    if media.is_folder:
        async def update_children_paths(folder_id: int, parent_path: str):
            children_query = select(Media).where(
                and_(Media.parent_id == folder_id, Media.is_deleted == False)
            )
            children_result = await db.execute(children_query)
            children = children_result.scalars().all()

            for child in children:
                child.path = f"{parent_path}/{child.title}"
                if child.is_folder:
                    await update_children_paths(child.id, child.path)

        await update_children_paths(media.id, new_path)

    await db.commit()

    return {
        "message": "移动成功",
        "id": media.id,
        "new_path": new_path
    }


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


@router.post("/media/folders")
async def check_folder_availability(
    folder_name: str = Query(..., min_length=1, max_length=255),
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """检查文件夹名称是否可用"""
    # 检查文件夹是否已存在
    query = select(Media.folder).where(
        and_(Media.folder == folder_name, Media.is_deleted == False)
    ).limit(1)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="文件夹已存在")

    return {"message": "文件夹可以使用", "folder_name": folder_name}


@router.delete("/media/folders/{folder_name}")
async def delete_folder(
    folder_name: str,
    move_to: Optional[str] = Query(None, description="移动文件到此文件夹，不提供则设为空"),
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """删除文件夹"""
    # 检查文件夹是否存在
    count_query = select(func.count()).select_from(Media).where(
        and_(Media.folder == folder_name, Media.is_deleted == False)
    )
    count_result = await db.execute(count_query)
    file_count = count_result.scalar()

    if file_count == 0:
        raise HTTPException(status_code=404, detail="文件夹不存在或为空")

    # 更新该文件夹下的所有文件
    query = select(Media).where(
        and_(Media.folder == folder_name, Media.is_deleted == False)
    )
    result = await db.execute(query)
    media_items = result.scalars().all()

    for media in media_items:
        media.folder = move_to
        media.updated_at = datetime.utcnow()

    await db.commit()

    return {
        "message": "文件夹删除成功",
        "affected_files": file_count,
        "moved_to": move_to or "根目录"
    }


@router.put("/media/folders/{old_name}")
async def rename_folder(
    old_name: str,
    new_name: str = Query(..., min_length=1, max_length=255),
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """重命名文件夹"""
    # 检查旧文件夹是否存在
    count_query = select(func.count()).select_from(Media).where(
        and_(Media.folder == old_name, Media.is_deleted == False)
    )
    count_result = await db.execute(count_query)
    file_count = count_result.scalar()

    if file_count == 0:
        raise HTTPException(status_code=404, detail="原文件夹不存在或为空")

    # 检查新文件夹名是否已存在
    new_query = select(Media.folder).where(
        and_(Media.folder == new_name, Media.is_deleted == False)
    ).limit(1)
    new_result = await db.execute(new_query)
    existing = new_result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="新文件夹名已存在")

    # 重命名：更新所有使用该文件夹的文件
    query = select(Media).where(
        and_(Media.folder == old_name, Media.is_deleted == False)
    )
    result = await db.execute(query)
    media_items = result.scalars().all()

    for media in media_items:
        media.folder = new_name
        media.updated_at = datetime.utcnow()

    await db.commit()

    return {
        "message": "文件夹重命名成功",
        "old_name": old_name,
        "new_name": new_name,
        "affected_files": file_count
    }


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
            # 从 MinIO 删除文件（同步方法）
            minio_client.delete_file(media.file_path)
            if media.thumbnail_path:
                minio_client.delete_file(media.thumbnail_path)
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


# ==================== 分块上传 API ====================

@router.post("/media/upload/init")
async def init_chunk_upload(
    filename: str = Query(...),
    file_size: int = Query(..., gt=0),
    mime_type: str = Query(...),
    title: str = Query(...),
    parent_id: Optional[int] = Query(None),
    description: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    chunk_size: int = Query(5242880, description="分块大小，默认5MB"),
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """
    初始化分块上传会话
    返回 upload_id 用于后续上传
    """

    # 计算总分块数
    total_chunks = (file_size + chunk_size - 1) // chunk_size

    # 生成唯一上传ID
    upload_id = str(uuid.uuid4())

    # 创建临时目录
    temp_dir = f"/tmp/uploads/{upload_id}"
    os.makedirs(temp_dir, exist_ok=True)

    # 计算过期时间（24小时）
    expires_at = datetime.utcnow() + timedelta(hours=24)

    # 创建上传会话
    session = UploadSession(
        upload_id=upload_id,
        filename=filename,
        file_size=file_size,
        mime_type=mime_type,
        chunk_size=chunk_size,
        total_chunks=total_chunks,
        uploaded_chunks=[],
        title=title,
        description=description,
        parent_id=parent_id,
        tags=tags,
        temp_dir=temp_dir,
        uploader_id=current_user.id,
        expires_at=expires_at,
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return {
        "upload_id": upload_id,
        "chunk_size": chunk_size,
        "total_chunks": total_chunks,
        "expires_at": expires_at.isoformat(),
        "message": "上传会话初始化成功"
    }


@router.post("/media/upload/chunk")
async def upload_chunk(
    upload_id: str = Query(...),
    chunk_index: int = Query(..., ge=0),
    chunk: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """
    上传单个文件分块
    chunk_index 从 0 开始
    """

    # 获取上传会话
    session_query = select(UploadSession).where(
        and_(
            UploadSession.upload_id == upload_id,
            UploadSession.uploader_id == current_user.id
        )
    )
    session_result = await db.execute(session_query)
    session = session_result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="上传会话不存在")

    # 检查是否过期
    if datetime.utcnow() > session.expires_at:
        raise HTTPException(status_code=410, detail="上传会话已过期")

    # 检查分块索引
    if chunk_index >= session.total_chunks:
        raise HTTPException(status_code=400, detail="分块索引超出范围")

    # 检查是否已上传
    if session.is_chunk_uploaded(chunk_index):
        return {
            "message": "分块已存在",
            "chunk_index": chunk_index,
            "progress": session.get_progress()
        }

    # 保存分块到临时目录
    chunk_path = os.path.join(session.temp_dir, f"chunk_{chunk_index}")

    try:
        content = await chunk.read()
        with open(chunk_path, "wb") as f:
            f.write(content)

        # 标记分块已上传
        session.mark_chunk_uploaded(chunk_index)
        session.updated_at = datetime.utcnow()

        # 检查是否所有分块都已上传
        if session.is_upload_complete():
            session.is_completed = True

        await db.commit()

        return {
            "message": "分块上传成功",
            "chunk_index": chunk_index,
            "progress": session.get_progress(),
            "is_completed": session.is_completed
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分块保存失败: {str(e)}")


@router.post("/media/upload/complete")
async def complete_chunk_upload(
    upload_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """
    完成分块上传，合并文件并创建媒体记录
    """

    # 获取上传会话
    session_query = select(UploadSession).where(
        and_(
            UploadSession.upload_id == upload_id,
            UploadSession.uploader_id == current_user.id
        )
    )
    session_result = await db.execute(session_query)
    session = session_result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="上传会话不存在")

    if not session.is_completed:
        raise HTTPException(status_code=400, detail="还有分块未上传完成")

    if session.is_merged:
        raise HTTPException(status_code=400, detail="文件已合并")

    try:
        # 合并所有分块
        merged_file_path = os.path.join(session.temp_dir, "merged_file")

        with open(merged_file_path, "wb") as merged_file:
            for i in range(session.total_chunks):
                chunk_path = os.path.join(session.temp_dir, f"chunk_{i}")
                with open(chunk_path, "rb") as chunk_file:
                    merged_file.write(chunk_file.read())

        # 上传到 MinIO
        with open(merged_file_path, "rb") as file:
            file_content = file.read()

        # 生成存储路径
        file_ext = os.path.splitext(session.filename)[1]
        object_name = f"media/{uuid.uuid4()}{file_ext}"

        # 上传到MinIO
        minio_client.upload_file(
            file_content=file_content,
            object_name=object_name,
            content_type=session.mime_type
        )

        # 获取URL
        url = minio_client.get_file_url(object_name)

        # 确定媒体类型
        if session.mime_type.startswith('image/'):
            media_type = MediaType.IMAGE
        elif session.mime_type.startswith('video/'):
            media_type = MediaType.VIDEO
        else:
            media_type = MediaType.IMAGE  # 默认

        # 创建媒体记录
        media = Media(
            title=session.title,
            description=session.description,
            filename=session.filename,
            file_path=object_name,
            file_size=session.file_size,
            mime_type=session.mime_type,
            media_type=media_type,
            status=MediaStatus.READY,
            url=url,
            parent_id=session.parent_id,
            tags=session.tags,
            uploader_id=current_user.id,
            is_folder=False,
        )

        # 设置路径
        if session.parent_id:
            parent_query = select(Media).where(Media.id == session.parent_id)
            parent_result = await db.execute(parent_query)
            parent = parent_result.scalar_one_or_none()
            if parent:
                media.path = f"{parent.path or parent.get_full_path()}/{session.filename}"

        db.add(media)
        session.is_merged = True
        session.media_id = media.id

        await db.commit()
        await db.refresh(media)

        # 清理临时文件
        try:
            shutil.rmtree(session.temp_dir)
        except Exception as e:
            print(f"清理临时文件失败: {e}")

        return {
            "message": "上传完成",
            "media_id": media.id,
            "url": url,
            "media": {
                "id": media.id,
                "title": media.title,
                "filename": media.filename,
                "file_size": media.file_size,
                "mime_type": media.mime_type,
                "url": media.url,
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件合并失败: {str(e)}")


@router.get("/media/upload/status/{upload_id}")
async def get_upload_status(
    upload_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """获取上传进度"""

    session_query = select(UploadSession).where(
        and_(
            UploadSession.upload_id == upload_id,
            UploadSession.uploader_id == current_user.id
        )
    )
    session_result = await db.execute(session_query)
    session = session_result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="上传会话不存在")

    return {
        "upload_id": session.upload_id,
        "filename": session.filename,
        "file_size": session.file_size,
        "total_chunks": session.total_chunks,
        "uploaded_chunks": session.uploaded_chunks,
        "progress": session.get_progress(),
        "is_completed": session.is_completed,
        "is_merged": session.is_merged,
        "created_at": session.created_at.isoformat(),
        "expires_at": session.expires_at.isoformat(),
    }


# ==================== 批量操作 API ====================

@router.post("/media/batch/move")
async def batch_move_media(
    media_ids: List[int] = Query(...),
    target_parent_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """批量移动文件/文件夹"""

    moved_count = 0
    errors = []

    for media_id in media_ids:
        try:
            # 获取媒体
            media_query = select(Media).where(
                and_(Media.id == media_id, Media.is_deleted == False)
            )
            media_result = await db.execute(media_query)
            media = media_result.scalar_one_or_none()

            if not media:
                errors.append({"id": media_id, "error": "不存在"})
                continue

            # 构建新路径
            if target_parent_id:
                target_query = select(Media).where(
                    and_(Media.id == target_parent_id, Media.is_folder == True)
                )
                target_result = await db.execute(target_query)
                target = target_result.scalar_one_or_none()

                if not target:
                    errors.append({"id": media_id, "error": "目标文件夹不存在"})
                    continue

                new_path = f"{target.path or target.get_full_path()}/{media.title}"
            else:
                new_path = f"/{media.title}"

            media.parent_id = target_parent_id
            media.path = new_path
            media.updated_at = datetime.utcnow()

            moved_count += 1

        except Exception as e:
            errors.append({"id": media_id, "error": str(e)})

    await db.commit()

    return {
        "message": "批量移动完成",
        "moved_count": moved_count,
        "total_count": len(media_ids),
        "errors": errors
    }


@router.delete("/media/batch/delete")
async def batch_delete_media(
    media_ids: List[int] = Query(...),
    permanent: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """批量删除文件/文件夹"""

    deleted_count = 0
    errors = []

    for media_id in media_ids:
        try:
            media_query = select(Media).where(Media.id == media_id)
            media_result = await db.execute(media_query)
            media = media_result.scalar_one_or_none()

            if not media:
                errors.append({"id": media_id, "error": "不存在"})
                continue

            if permanent:
                # 永久删除
                if not media.is_folder:
                    try:
                        minio_client.delete_file(media.file_path)
                    except Exception as e:
                        print(f"删除文件失败: {e}")

                await db.delete(media)
            else:
                # 软删除
                media.is_deleted = True
                media.deleted_at = datetime.utcnow()

            deleted_count += 1

        except Exception as e:
            errors.append({"id": media_id, "error": str(e)})

    await db.commit()

    return {
        "message": "批量删除完成",
        "deleted_count": deleted_count,
        "total_count": len(media_ids),
        "errors": errors
    }


@router.post("/media/batch/restore")
async def batch_restore_media(
    media_ids: List[int] = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """批量恢复已删除的文件/文件夹"""

    restored_count = 0
    errors = []

    for media_id in media_ids:
        try:
            media_query = select(Media).where(
                and_(Media.id == media_id, Media.is_deleted == True)
            )
            media_result = await db.execute(media_query)
            media = media_result.scalar_one_or_none()

            if not media:
                errors.append({"id": media_id, "error": "不存在或未被删除"})
                continue

            media.is_deleted = False
            media.deleted_at = None
            media.updated_at = datetime.utcnow()

            restored_count += 1

        except Exception as e:
            errors.append({"id": media_id, "error": str(e)})

    await db.commit()

    return {
        "message": "批量恢复完成",
        "restored_count": restored_count,
        "total_count": len(media_ids),
        "errors": errors
    }


@router.post("/media/batch/tags")
async def batch_update_tags(
    media_ids: List[int] = Query(...),
    tags: str = Query(""),
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """批量更新文件标签"""

    updated_count = 0
    errors = []

    for media_id in media_ids:
        try:
            media_query = select(Media).where(
                and_(Media.id == media_id, Media.is_deleted == False)
            )
            media_result = await db.execute(media_query)
            media = media_result.scalar_one_or_none()

            if not media:
                errors.append({"id": media_id, "error": "不存在"})
                continue

            media.tags = tags
            media.updated_at = datetime.utcnow()

            updated_count += 1

        except Exception as e:
            errors.append({"id": media_id, "error": str(e)})

    await db.commit()

    return {
        "message": "批量更新标签完成",
        "updated_count": updated_count,
        "total_count": len(media_ids),
        "errors": errors
    }


@router.get("/media/deleted", response_model=MediaListResponse)
async def get_deleted_media(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """获取回收站中的已删除文件"""

    # 构建查询
    query = select(Media).where(Media.is_deleted == True)

    # 搜索
    if search:
        search_filter = or_(
            Media.title.ilike(f"%{search}%"),
            Media.filename.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    # 总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 排序：按删除时间倒序
    query = query.order_by(desc(Media.deleted_at))
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


@router.delete("/media/recycle-bin/clear")
async def clear_recycle_bin(
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """清空回收站 - 永久删除所有已删除的文件"""

    # 获取所有已删除的文件
    query = select(Media).where(Media.is_deleted == True)
    result = await db.execute(query)
    deleted_items = result.scalars().all()

    cleared_count = 0
    errors = []

    for media in deleted_items:
        try:
            # 删除实际文件
            if not media.is_folder and media.file_path:
                try:
                    minio_client.delete_file(media.file_path)
                    if media.thumbnail_path:
                        minio_client.delete_file(media.thumbnail_path)
                except Exception as e:
                    print(f"删除文件失败: {e}")

            # 从数据库删除
            await db.delete(media)
            cleared_count += 1

        except Exception as e:
            errors.append({"id": media.id, "title": media.title, "error": str(e)})

    await db.commit()

    return {
        "message": "回收站已清空",
        "cleared_count": cleared_count,
        "errors": errors
    }


@router.get("/media/recycle-bin/count")
async def get_recycle_bin_count(
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """获取回收站文件数量"""

    count_query = select(func.count()).select_from(Media).where(Media.is_deleted == True)
    count_result = await db.execute(count_query)
    count = count_result.scalar()

    return {
        "count": count or 0
    }


@router.post("/media/batch/download")
async def batch_download_media(
    media_ids: List[int] = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """批量下载文件为 ZIP（后端生成）"""
    import zipfile
    import io
    from fastapi.responses import StreamingResponse

    # 查询所有文件
    query = select(Media).where(
        and_(
            Media.id.in_(media_ids),
            Media.is_deleted == False,
            Media.is_folder == False  # 只下载文件，不包括文件夹
        )
    )
    result = await db.execute(query)
    media_items = result.scalars().all()

    if not media_items:
        raise HTTPException(status_code=404, detail="没有可下载的文件")

    # 创建内存中的 ZIP 文件
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for media in media_items:
            try:
                # 从 MinIO 获取文件内容
                file_data = minio_client.get_file(media.file_path)

                # 使用文件标题作为 ZIP 中的文件名
                file_ext = os.path.splitext(media.filename)[1]
                zip_filename = f"{media.title}{file_ext}"

                # 添加到 ZIP
                zip_file.writestr(zip_filename, file_data)
            except Exception as e:
                print(f"添加文件到 ZIP 失败: {media.title}, {e}")
                continue

    # 重置指针到开始
    zip_buffer.seek(0)

    # 返回 ZIP 文件
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=files_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.zip"
        }
    )


@router.post("/media/batch/copy")
async def batch_copy_media(
    media_ids: List[int] = Query(...),
    target_parent_id: Optional[int] = Query(None, description="目标文件夹ID"),
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """批量复制文件/文件夹"""

    copied_count = 0
    errors = []

    async def copy_media_recursive(media_id: int, target_parent_id: Optional[int]) -> Optional[int]:
        """递归复制媒体（包括文件夹及其内容）"""
        try:
            # 获取原始媒体
            media_query = select(Media).where(
                and_(Media.id == media_id, Media.is_deleted == False)
            )
            media_result = await db.execute(media_query)
            original = media_result.scalar_one_or_none()

            if not original:
                return None

            # 生成新标题（避免重名）
            base_title = original.title
            new_title = f"{base_title} - 副本"

            # 检查同级是否有重名
            counter = 1
            while True:
                check_query = select(Media).where(
                    and_(
                        Media.parent_id == target_parent_id,
                        Media.title == new_title,
                        Media.is_deleted == False
                    )
                )
                check_result = await db.execute(check_query)
                if not check_result.scalar_one_or_none():
                    break
                counter += 1
                new_title = f"{base_title} - 副本{counter}"

            # 创建副本
            if original.is_folder:
                # 复制文件夹
                new_folder = Media(
                    title=new_title,
                    description=original.description,
                    filename=new_title,
                    file_path=f"folders/{uuid.uuid4()}",
                    file_size=0,
                    media_type=original.media_type,
                    status=MediaStatus.READY,
                    is_folder=True,
                    parent_id=target_parent_id,
                    tags=original.tags,
                    uploader_id=current_user.id,
                )

                # 设置路径
                if target_parent_id:
                    parent_query = select(Media).where(Media.id == target_parent_id)
                    parent_result = await db.execute(parent_query)
                    parent = parent_result.scalar_one_or_none()
                    if parent:
                        new_folder.path = f"{parent.path or parent.get_full_path()}/{new_title}"
                else:
                    new_folder.path = f"/{new_title}"

                db.add(new_folder)
                await db.flush()

                # 递归复制子项
                children_query = select(Media).where(
                    and_(Media.parent_id == original.id, Media.is_deleted == False)
                )
                children_result = await db.execute(children_query)
                children = children_result.scalars().all()

                for child in children:
                    await copy_media_recursive(child.id, new_folder.id)

                return new_folder.id

            else:
                # 复制文件
                # 从 MinIO 复制文件
                try:
                    file_data = minio_client.get_file(original.file_path)

                    # 生成新的文件路径
                    file_ext = os.path.splitext(original.filename)[1]
                    new_file_path = f"media/{uuid.uuid4()}{file_ext}"

                    # 上传副本到 MinIO
                    minio_client.upload_file(
                        file_content=file_data,
                        object_name=new_file_path,
                        content_type=original.mime_type or "application/octet-stream"
                    )

                    # 获取新 URL
                    new_url = minio_client.get_file_url(new_file_path)

                    # 创建数据库记录
                    new_media = Media(
                        title=new_title,
                        description=original.description,
                        filename=original.filename,
                        file_path=new_file_path,
                        file_size=original.file_size,
                        mime_type=original.mime_type,
                        media_type=original.media_type,
                        status=MediaStatus.READY,
                        url=new_url,
                        parent_id=target_parent_id,
                        tags=original.tags,
                        width=original.width,
                        height=original.height,
                        duration=original.duration,
                        uploader_id=current_user.id,
                        is_folder=False,
                    )

                    # 设置路径
                    if target_parent_id:
                        parent_query = select(Media).where(Media.id == target_parent_id)
                        parent_result = await db.execute(parent_query)
                        parent = parent_result.scalar_one_or_none()
                        if parent:
                            new_media.path = f"{parent.path or parent.get_full_path()}/{new_title}"
                    else:
                        new_media.path = f"/{new_title}"

                    db.add(new_media)
                    await db.flush()

                    return new_media.id

                except Exception as e:
                    print(f"复制文件失败: {e}")
                    return None

        except Exception as e:
            print(f"复制媒体失败: {e}")
            return None

    # 复制每个选中的媒体
    for media_id in media_ids:
        try:
            new_id = await copy_media_recursive(media_id, target_parent_id)
            if new_id:
                copied_count += 1
            else:
                errors.append({"id": media_id, "error": "复制失败"})
        except Exception as e:
            errors.append({"id": media_id, "error": str(e)})

    await db.commit()

    return {
        "message": "批量复制完成",
        "copied_count": copied_count,
        "total_count": len(media_ids),
        "errors": errors
    }
