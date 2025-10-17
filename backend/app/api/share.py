"""
公开分享访问 API
用于访问通过分享链接分享的文件/文件夹
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.media import Media
from app.models.media_share import MediaShare
from app.utils.security import verify_password

router = APIRouter()


async def _is_subfolder_of(db: AsyncSession, folder_id: int, root_folder_id: int, max_depth: int = 20) -> bool:
    """
    检查 folder_id 是否是 root_folder_id 的子文件夹
    通过递归检查 parent_id 链实现

    Args:
        db: 数据库会话
        folder_id: 要检查的文件夹ID
        root_folder_id: 根文件夹ID
        max_depth: 最大递归深度，防止无限循环

    Returns:
        bool: 如果是子文件夹返回 True，否则返回 False
    """
    current_id = folder_id
    depth = 0

    while current_id and depth < max_depth:
        # 查询当前文件夹
        query = select(Media).where(Media.id == current_id)
        result = await db.execute(query)
        media = result.scalar_one_or_none()

        if not media:
            return False

        # 如果找到根文件夹，返回 True
        if current_id == root_folder_id:
            return True

        # 移动到父文件夹
        current_id = media.parent_id
        depth += 1

    return False


@router.get("/share/{share_code}")
async def get_share_info(
    share_code: str,
    password: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取分享链接信息"""

    # 查询分享记录
    share_query = select(MediaShare).where(MediaShare.share_code == share_code)
    share_result = await db.execute(share_query)
    share = share_result.scalar_one_or_none()

    if not share:
        raise HTTPException(status_code=404, detail="分享链接不存在")

    # 检查是否可用
    if not share.is_available:
        if not share.is_active:
            raise HTTPException(status_code=403, detail="分享链接已被禁用")
        if share.is_expired:
            raise HTTPException(status_code=403, detail="分享链接已过期")
        if share.max_views and share.view_count >= share.max_views:
            raise HTTPException(status_code=403, detail="分享链接访问次数已达上限")

    # 验证密码
    if share.password:
        if not password:
            raise HTTPException(status_code=401, detail="需要访问密码")
        if not verify_password(password, share.password):
            raise HTTPException(status_code=401, detail="密码错误")

    # 增加访问次数
    share.view_count += 1
    await db.commit()

    # 获取媒体信息
    media_query = select(Media).where(
        and_(Media.id == share.media_id, Media.is_deleted == False)
    )
    media_result = await db.execute(media_query)
    media = media_result.scalar_one_or_none()

    if not media:
        raise HTTPException(status_code=404, detail="文件不存在")

    # 构建响应
    response = {
        "share_code": share.share_code,
        "media": {
            "id": media.id,
            "title": media.title,
            "is_folder": media.is_folder,
            "file_size": media.file_size,
            "mime_type": media.mime_type,
            "media_type": media.media_type.value if not media.is_folder else "folder",
            "url": media.url if not media.is_folder else None,
            "thumbnail_url": media.thumbnail_url,
            "created_at": media.created_at,
        },
        "allow_download": share.allow_download,
        "download_count": share.download_count,
        "max_downloads": share.max_downloads,
        "expires_at": share.expires_at,
    }

    return response


@router.get("/share/{share_code}/folder-contents")
async def get_folder_contents(
    share_code: str,
    folder_id: Optional[int] = None,
    password: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取分享文件夹的内容"""

    # 查询分享记录
    share_query = select(MediaShare).where(MediaShare.share_code == share_code)
    share_result = await db.execute(share_query)
    share = share_result.scalar_one_or_none()

    if not share:
        raise HTTPException(status_code=404, detail="分享链接不存在")

    # 检查是否可用
    if not share.is_available:
        raise HTTPException(status_code=403, detail="分享链接不可用")

    # 验证密码
    if share.password:
        if not password:
            raise HTTPException(status_code=401, detail="需要访问密码")
        if not verify_password(password, share.password):
            raise HTTPException(status_code=401, detail="密码错误")

    # 获取根媒体
    root_media_query = select(Media).where(
        and_(Media.id == share.media_id, Media.is_deleted == False)
    )
    root_media_result = await db.execute(root_media_query)
    root_media = root_media_result.scalar_one_or_none()

    if not root_media:
        raise HTTPException(status_code=404, detail="文件不存在")

    if not root_media.is_folder:
        raise HTTPException(status_code=400, detail="此分享不是文件夹")

    # 确定要查询的文件夹ID
    target_folder_id = folder_id if folder_id else share.media_id

    # 验证目标文件夹是否在分享的文件夹内
    if folder_id and folder_id != share.media_id:
        target_query = select(Media).where(Media.id == folder_id)
        target_result = await db.execute(target_query)
        target = target_result.scalar_one_or_none()

        if not target:
            raise HTTPException(status_code=404, detail="文件夹不存在")

        # ✅ 增强：检查目标文件夹是否是分享根文件夹的子文件夹
        # 通过递归检查 parent_id 链确保权限安全
        if not await _is_subfolder_of(db, folder_id, share.media_id):
            raise HTTPException(status_code=403, detail="无权访问此文件夹")

    # 获取文件夹内容
    contents_query = select(Media).where(
        and_(
            Media.parent_id == target_folder_id,
            Media.is_deleted == False
        )
    ).order_by(Media.is_folder.desc(), Media.title)

    contents_result = await db.execute(contents_query)
    contents = contents_result.scalars().all()

    items = []
    for item in contents:
        items.append({
            "id": item.id,
            "title": item.title,
            "is_folder": item.is_folder,
            "file_size": item.file_size,
            "mime_type": item.mime_type,
            "media_type": item.media_type.value if not item.is_folder else "folder",
            "url": item.url if not item.is_folder else None,
            "thumbnail_url": item.thumbnail_url,
            "created_at": item.created_at,
        })

    return {
        "share_code": share_code,
        "folder_id": target_folder_id,
        "folder_title": root_media.title if target_folder_id == share.media_id else None,
        "items": items,
        "allow_download": share.allow_download,
    }


@router.get("/share/{share_code}/download")
async def download_shared_file(
    share_code: str,
    password: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """下载分享的文件"""

    # 查询分享记录
    share_query = select(MediaShare).where(MediaShare.share_code == share_code)
    share_result = await db.execute(share_query)
    share = share_result.scalar_one_or_none()

    if not share:
        raise HTTPException(status_code=404, detail="分享链接不存在")

    # 检查是否可用
    if not share.is_available:
        raise HTTPException(status_code=403, detail="分享链接不可用")

    # 检查是否允许下载
    if not share.allow_download:
        raise HTTPException(status_code=403, detail="此分享不允许下载")

    # 检查下载次数
    if share.max_downloads and share.download_count >= share.max_downloads:
        raise HTTPException(status_code=403, detail="下载次数已达上限")

    # 验证密码
    if share.password:
        if not password:
            raise HTTPException(status_code=401, detail="需要访问密码")
        if not verify_password(password, share.password):
            raise HTTPException(status_code=401, detail="密码错误")

    # 获取媒体信息
    media_query = select(Media).where(
        and_(Media.id == share.media_id, Media.is_deleted == False)
    )
    media_result = await db.execute(media_query)
    media = media_result.scalar_one_or_none()

    if not media:
        raise HTTPException(status_code=404, detail="文件不存在")

    if media.is_folder:
        raise HTTPException(status_code=400, detail="文件夹下载请使用批量下载接口")

    # 增加下载次数
    share.download_count += 1
    await db.commit()

    # 返回下载URL（重定向到实际文件）
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=media.url)
