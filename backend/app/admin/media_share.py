"""
媒体文件分享 API
"""
from datetime import datetime
from typing import List, Optional
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.media import Media
from app.models.media_share import MediaShare
from app.models.user import AdminUser
from app.utils.dependencies import get_current_admin_user
from app.utils.security import get_password_hash

router = APIRouter()


def generate_share_code(length=8):
    """生成随机分享码"""
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


@router.post("/media/{media_id}/share")
async def create_media_share(
    media_id: int,
    share_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """创建文件分享链接"""

    # 检查媒体文件是否存在
    media_query = select(Media).where(and_(Media.id == media_id, Media.is_deleted == False))
    media_result = await db.execute(media_query)
    media = media_result.scalar_one_or_none()

    if not media:
        raise HTTPException(status_code=404, detail="文件不存在")

    if media.is_folder:
        raise HTTPException(status_code=400, detail="不支持分享文件夹")

    # 生成唯一的分享码
    share_code = generate_share_code()

    # 确保分享码唯一
    while True:
        existing = await db.execute(
            select(MediaShare).where(MediaShare.share_code == share_code)
        )
        if not existing.scalar_one_or_none():
            break
        share_code = generate_share_code()

    # 处理密码
    password_hash = None
    if share_data.get('password'):
        password_hash = get_password_hash(share_data['password'])

    # 创建分享记录
    share = MediaShare(
        media_id=media_id,
        share_code=share_code,
        password=password_hash,
        allow_download=share_data.get('allow_download', True),
        max_downloads=share_data.get('max_downloads'),
        max_views=share_data.get('max_views'),
        expires_at=share_data.get('expires_at'),
        created_by=current_user.id,
        note=share_data.get('note'),
    )

    db.add(share)
    await db.commit()
    await db.refresh(share)

    return {
        "id": share.id,
        "share_code": share.share_code,
        "share_url": f"/share/{share.share_code}",
        "created_at": share.created_at,
    }


@router.get("/media/shares")
async def list_media_shares(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    media_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """获取分享链接列表"""

    # 构建查询
    query = select(MediaShare).join(Media)

    # 筛选条件
    if media_id:
        query = query.where(MediaShare.media_id == media_id)
    if is_active is not None:
        query = query.where(MediaShare.is_active == is_active)

    # 计算总数
    count_query = select(func.count()).select_from(MediaShare)
    if media_id:
        count_query = count_query.where(MediaShare.media_id == media_id)
    if is_active is not None:
        count_query = count_query.where(MediaShare.is_active == is_active)

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # 分页和排序
    query = query.order_by(MediaShare.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    shares = result.scalars().all()

    # 构建响应
    items = []
    for share in shares:
        items.append({
            "id": share.id,
            "media_id": share.media_id,
            "media_title": share.media.title,
            "media_type": share.media.media_type.value if not share.media.is_folder else "folder",
            "share_code": share.share_code,
            "share_url": f"/share/{share.share_code}",
            "has_password": bool(share.password),
            "allow_download": share.allow_download,
            "max_downloads": share.max_downloads,
            "download_count": share.download_count,
            "max_views": share.max_views,
            "view_count": share.view_count,
            "expires_at": share.expires_at,
            "is_active": share.is_active,
            "is_expired": share.is_expired,
            "is_available": share.is_available,
            "note": share.note,
            "created_at": share.created_at,
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }


@router.put("/media/shares/{share_id}")
async def update_media_share(
    share_id: int,
    share_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """更新分享链接"""

    share_query = select(MediaShare).where(MediaShare.id == share_id)
    share_result = await db.execute(share_query)
    share = share_result.scalar_one_or_none()

    if not share:
        raise HTTPException(status_code=404, detail="分享链接不存在")

    # 更新字段
    if 'password' in share_data:
        if share_data['password']:
            share.password = get_password_hash(share_data['password'])
        else:
            share.password = None

    if 'allow_download' in share_data:
        share.allow_download = share_data['allow_download']
    if 'max_downloads' in share_data:
        share.max_downloads = share_data['max_downloads']
    if 'max_views' in share_data:
        share.max_views = share_data['max_views']
    if 'expires_at' in share_data:
        share.expires_at = share_data['expires_at']
    if 'is_active' in share_data:
        share.is_active = share_data['is_active']
    if 'note' in share_data:
        share.note = share_data['note']

    share.updated_at = datetime.utcnow()

    await db.commit()

    return {"message": "分享链接已更新"}


@router.delete("/media/shares/{share_id}")
async def delete_media_share(
    share_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """删除分享链接"""

    share_query = select(MediaShare).where(MediaShare.id == share_id)
    share_result = await db.execute(share_query)
    share = share_result.scalar_one_or_none()

    if not share:
        raise HTTPException(status_code=404, detail="分享链接不存在")

    await db.delete(share)
    await db.commit()

    return {"message": "分享链接已删除"}


@router.get("/media/{media_id}/shares")
async def get_media_shares(
    media_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """获取某个文件的所有分享链接"""

    # 检查文件是否存在
    media_query = select(Media).where(and_(Media.id == media_id, Media.is_deleted == False))
    media_result = await db.execute(media_query)
    media = media_result.scalar_one_or_none()

    if not media:
        raise HTTPException(status_code=404, detail="文件不存在")

    # 获取分享链接
    shares_query = select(MediaShare).where(MediaShare.media_id == media_id).order_by(desc(MediaShare.created_at))
    shares_result = await db.execute(shares_query)
    shares = shares_result.scalars().all()

    return {
        "media_id": media_id,
        "media_title": media.title,
        "shares": [
            {
                "id": share.id,
                "share_code": share.share_code,
                "share_url": f"/share/{share.share_code}",
                "has_password": bool(share.password),
                "allow_download": share.allow_download,
                "download_count": share.download_count,
                "view_count": share.view_count,
                "is_active": share.is_active,
                "is_available": share.is_available,
                "expires_at": share.expires_at,
                "created_at": share.created_at,
            }
            for share in shares
        ],
    }
