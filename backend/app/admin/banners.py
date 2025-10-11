import io
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.content import Banner, BannerStatus
from app.models.user import AdminUser
from app.utils.dependencies import get_current_admin_user
from app.utils.minio_client import minio_client

router = APIRouter()


# Pydantic schemas
class BannerCreate(BaseModel):
    title: str
    image_url: str
    link_url: Optional[str] = None
    video_id: Optional[int] = None
    description: Optional[str] = None
    status: BannerStatus = BannerStatus.ACTIVE
    sort_order: int = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class BannerUpdate(BaseModel):
    title: Optional[str] = None
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    video_id: Optional[int] = None
    description: Optional[str] = None
    status: Optional[BannerStatus] = None
    sort_order: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class BannerResponse(BaseModel):
    id: int
    title: str
    image_url: str
    link_url: Optional[str]
    video_id: Optional[int]
    description: Optional[str]
    status: BannerStatus
    sort_order: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.get("/banners", response_model=dict)
async def get_banners(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[BannerStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取Banner列表"""
    query = select(Banner).order_by(desc(Banner.sort_order), desc(Banner.created_at))

    if status:
        query = query.where(Banner.status == status)

    # Get total count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    # Get paginated results
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    banners = result.scalars().all()

    return {
        "items": banners,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/banners/{banner_id}", response_model=BannerResponse)
async def get_banner(
    banner_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取单个Banner详情"""
    result = await db.execute(select(Banner).where(Banner.id == banner_id))
    banner = result.scalar_one_or_none()

    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")

    return banner


@router.post("/banners", response_model=BannerResponse)
async def create_banner(
    banner_data: BannerCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """创建Banner"""
    banner = Banner(**banner_data.model_dump())
    db.add(banner)
    await db.commit()
    await db.refresh(banner)

    return banner


@router.put("/banners/{banner_id}", response_model=BannerResponse)
async def update_banner(
    banner_id: int,
    banner_data: BannerUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """更新Banner"""
    result = await db.execute(select(Banner).where(Banner.id == banner_id))
    banner = result.scalar_one_or_none()

    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")

    # Update fields
    for key, value in banner_data.model_dump(exclude_unset=True).items():
        setattr(banner, key, value)

    await db.commit()
    await db.refresh(banner)

    return banner


@router.delete("/banners/{banner_id}")
async def delete_banner(
    banner_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """删除Banner"""
    result = await db.execute(select(Banner).where(Banner.id == banner_id))
    banner = result.scalar_one_or_none()

    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")

    await db.delete(banner)
    await db.commit()

    return {"message": "Banner deleted successfully"}


@router.put("/banners/{banner_id}/status")
async def update_banner_status(
    banner_id: int,
    status: BannerStatus,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """更新Banner状态"""
    result = await db.execute(select(Banner).where(Banner.id == banner_id))
    banner = result.scalar_one_or_none()

    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")

    banner.status = status
    await db.commit()

    return {"message": f"Banner status updated to {status}"}


@router.put("/banners/{banner_id}/sort-order")
async def update_banner_sort_order(
    banner_id: int,
    sort_order: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """更新Banner排序"""
    result = await db.execute(select(Banner).where(Banner.id == banner_id))
    banner = result.scalar_one_or_none()

    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")

    banner.sort_order = sort_order
    await db.commit()

    return {"message": "Banner sort order updated"}


@router.post("/banners/upload-image")
async def upload_banner_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """上传Banner图片"""
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, detail="不支持的图片格式，仅支持 JPG, PNG, WEBP"
        )

    try:
        # 生成文件名
        ext = file.filename.split(".")[-1]
        object_name = (
            f"banners/banner_{int(datetime.now(timezone.utc).timestamp())}.{ext}"
        )

        # 上传到 MinIO
        file_content = await file.read()
        image_url = minio_client.upload_image(
            io.BytesIO(file_content),
            object_name,
            file.content_type,
        )

        return {"image_url": image_url, "message": "图片上传成功"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")
