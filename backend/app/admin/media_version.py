"""
媒体文件版本管理 API
"""
from datetime import datetime
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.media import Media
from app.models.media_version import MediaVersion
from app.models.user import AdminUser
from app.utils.dependencies import get_current_admin_user
from app.utils.minio_client import minio_client

router = APIRouter()


@router.get("/media/{media_id}/versions")
async def get_media_versions(
    media_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """获取文件的所有版本历史"""

    # 检查文件是否存在
    media_query = select(Media).where(
        and_(Media.id == media_id, Media.is_deleted == False)
    )
    media_result = await db.execute(media_query)
    media = media_result.scalar_one_or_none()

    if not media:
        raise HTTPException(status_code=404, detail="文件不存在")

    if media.is_folder:
        raise HTTPException(status_code=400, detail="文件夹不支持版本管理")

    # 获取版本列表
    versions_query = (
        select(MediaVersion)
        .where(MediaVersion.media_id == media_id)
        .order_by(desc(MediaVersion.version_number))
    )
    versions_result = await db.execute(versions_query)
    versions = versions_result.scalars().all()

    items = []
    for version in versions:
        items.append({
            "id": version.id,
            "version_number": version.version_number,
            "file_path": version.file_path,
            "file_size": version.file_size,
            "mime_type": version.mime_type,
            "url": version.url,
            "width": version.width,
            "height": version.height,
            "duration": version.duration,
            "change_note": version.change_note,
            "created_by": version.created_by,
            "created_at": version.created_at,
        })

    return {
        "media_id": media_id,
        "media_title": media.title,
        "current_version": {
            "file_path": media.file_path,
            "file_size": media.file_size,
            "url": media.url,
        },
        "versions": items,
        "total_versions": len(items),
    }


@router.post("/media/{media_id}/versions")
async def create_media_version(
    media_id: int,
    file: UploadFile = File(...),
    change_note: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """上传新版本的文件"""

    # 检查文件是否存在
    media_query = select(Media).where(
        and_(Media.id == media_id, Media.is_deleted == False)
    )
    media_result = await db.execute(media_query)
    media = media_result.scalar_one_or_none()

    if not media:
        raise HTTPException(status_code=404, detail="文件不存在")

    if media.is_folder:
        raise HTTPException(status_code=400, detail="文件夹不支持版本管理")

    # 获取当前最大版本号
    max_version_query = (
        select(MediaVersion.version_number)
        .where(MediaVersion.media_id == media_id)
        .order_by(desc(MediaVersion.version_number))
        .limit(1)
    )
    max_version_result = await db.execute(max_version_query)
    max_version = max_version_result.scalar_one_or_none()
    next_version = (max_version or 0) + 1

    # 保存当前版本为历史版本
    current_version = MediaVersion(
        media_id=media_id,
        version_number=next_version - 1,
        file_path=media.file_path,
        file_size=media.file_size,
        mime_type=media.mime_type,
        url=media.url,
        width=media.width,
        height=media.height,
        duration=media.duration,
        change_note="原始版本" if next_version == 1 else f"版本 {next_version - 1}",
        created_by=current_user.id,
    )
    db.add(current_version)

    # 上传新文件到 MinIO
    file_content = await file.read()
    file_ext = file.filename.split(".")[-1] if "." in file.filename else ""
    new_file_path = f"media/{uuid.uuid4()}.{file_ext}"

    try:
        minio_client.upload_file(
            file_content=file_content,
            object_name=new_file_path,
            content_type=file.content_type or "application/octet-stream",
        )

        new_url = minio_client.get_file_url(new_file_path)

        # 更新媒体记录
        media.file_path = new_file_path
        media.file_size = len(file_content)
        media.mime_type = file.content_type
        media.url = new_url
        media.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(media)

        return {
            "message": "新版本上传成功",
            "version_number": next_version,
            "media": {
                "id": media.id,
                "title": media.title,
                "url": media.url,
                "file_size": media.file_size,
            },
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.post("/media/{media_id}/versions/{version_id}/restore")
async def restore_media_version(
    media_id: int,
    version_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """恢复到指定版本"""

    # 检查文件是否存在
    media_query = select(Media).where(
        and_(Media.id == media_id, Media.is_deleted == False)
    )
    media_result = await db.execute(media_query)
    media = media_result.scalar_one_or_none()

    if not media:
        raise HTTPException(status_code=404, detail="文件不存在")

    # 检查版本是否存在
    version_query = select(MediaVersion).where(
        and_(MediaVersion.id == version_id, MediaVersion.media_id == media_id)
    )
    version_result = await db.execute(version_query)
    version = version_result.scalar_one_or_none()

    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")

    # 保存当前版本为历史
    max_version_query = (
        select(MediaVersion.version_number)
        .where(MediaVersion.media_id == media_id)
        .order_by(desc(MediaVersion.version_number))
        .limit(1)
    )
    max_version_result = await db.execute(max_version_query)
    max_version = max_version_result.scalar_one_or_none()
    next_version = (max_version or 0) + 1

    current_version = MediaVersion(
        media_id=media_id,
        version_number=next_version,
        file_path=media.file_path,
        file_size=media.file_size,
        mime_type=media.mime_type,
        url=media.url,
        width=media.width,
        height=media.height,
        duration=media.duration,
        change_note=f"恢复到版本 {version.version_number}",
        created_by=current_user.id,
    )
    db.add(current_version)

    # 恢复到指定版本
    media.file_path = version.file_path
    media.file_size = version.file_size
    media.mime_type = version.mime_type
    media.url = version.url
    media.width = version.width
    media.height = version.height
    media.duration = version.duration
    media.updated_at = datetime.utcnow()

    await db.commit()

    return {
        "message": f"已恢复到版本 {version.version_number}",
        "restored_version": version.version_number,
    }


@router.delete("/media/{media_id}/versions/{version_id}")
async def delete_media_version(
    media_id: int,
    version_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """删除指定版本（物理删除文件）"""

    # 检查版本是否存在
    version_query = select(MediaVersion).where(
        and_(MediaVersion.id == version_id, MediaVersion.media_id == media_id)
    )
    version_result = await db.execute(version_query)
    version = version_result.scalar_one_or_none()

    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")

    # 从 MinIO 删除文件
    try:
        minio_client.delete_file(version.file_path)
    except Exception as e:
        print(f"删除 MinIO 文件失败: {e}")

    # 从数据库删除版本记录
    await db.delete(version)
    await db.commit()

    return {"message": "版本已删除"}
