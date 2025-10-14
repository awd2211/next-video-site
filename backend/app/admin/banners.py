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
from app.utils.sorting import apply_sorting, normalize_sort_field

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


class BannerListResponse(BaseModel):
    items: list[BannerResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.get("/banners", response_model=BannerListResponse)
async def get_banners(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[BannerStatus] = None,
    sort_by: Optional[str] = Query(
        "sort_order",
        description="排序字段: id, title, sort_order, created_at, updated_at, start_date, end_date",
    ),
    sort_order: Optional[str] = Query(
        "desc", regex="^(asc|desc)$", description="排序顺序: asc (升序) 或 desc (降序)"
    ),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取Banner列表"""
    query = select(Banner)

    if status:
        query = query.where(Banner.status == status)

    # Get total count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    # Apply sorting
    sort_field = normalize_sort_field(sort_by)
    allowed_sort_fields = [
        "id",
        "title",
        "sort_order",
        "status",
        "created_at",
        "updated_at",
        "start_date",
        "end_date",
    ]
    query = apply_sorting(
        query,
        Banner,
        sort_field,
        sort_order,
        default_sort="sort_order",
        allowed_fields=allowed_sort_fields,
    )

    # Get paginated results
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    banners = result.scalars().all()

    return {
        "items": [BannerResponse.model_validate(banner) for banner in banners],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
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

    # 🆕 发送横幅创建通知
    try:
        from app.utils.admin_notification_service import AdminNotificationService

        await AdminNotificationService.notify_banner_management(
            db=db,
            banner_id=banner.id,
            banner_title=banner.title,
            action="created",
            admin_username=current_admin.username,
        )
    except Exception as e:
        print(f"Failed to send banner creation notification: {e}")

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

    # 保存信息用于通知
    banner_title = banner.title

    await db.delete(banner)
    await db.commit()

    # 🆕 发送横幅删除通知
    try:
        from app.utils.admin_notification_service import AdminNotificationService

        await AdminNotificationService.notify_banner_management(
            db=db,
            banner_id=banner_id,
            banner_title=banner_title,
            action="deleted",
            admin_username=current_admin.username,
        )
    except Exception as e:
        print(f"Failed to send banner deletion notification: {e}")

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

    # 🆕 发送横幅状态变更通知
    try:
        from app.utils.admin_notification_service import AdminNotificationService

        action = "activated" if status == BannerStatus.ACTIVE else "deactivated"
        await AdminNotificationService.notify_banner_management(
            db=db,
            banner_id=banner_id,
            banner_title=banner.title,
            action=action,
            admin_username=current_admin.username,
        )
    except Exception as e:
        print(f"Failed to send banner status notification: {e}")

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


class BatchRequest(BaseModel):
    ids: list[int]


@router.put("/batch/enable")
async def batch_enable_banners(
    request: BatchRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """批量启用Banner"""
    if not request.ids:
        raise HTTPException(status_code=400, detail="ID列表不能为空")

    result = await db.execute(select(Banner).where(Banner.id.in_(request.ids)))
    banners = result.scalars().all()

    if not banners:
        raise HTTPException(status_code=404, detail="未找到任何Banner")

    for banner in banners:
        banner.status = BannerStatus.ACTIVE

    await db.commit()

    return {"message": f"成功启用 {len(banners)} 个Banner"}


@router.put("/batch/disable")
async def batch_disable_banners(
    request: BatchRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """批量停用Banner"""
    if not request.ids:
        raise HTTPException(status_code=400, detail="ID列表不能为空")

    result = await db.execute(select(Banner).where(Banner.id.in_(request.ids)))
    banners = result.scalars().all()

    if not banners:
        raise HTTPException(status_code=404, detail="未找到任何Banner")

    for banner in banners:
        banner.status = BannerStatus.INACTIVE

    await db.commit()

    return {"message": f"成功停用 {len(banners)} 个Banner"}
