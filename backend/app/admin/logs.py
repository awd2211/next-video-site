from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database import get_db
from app.models.admin import OperationLog
from app.models.user import AdminUser
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


@router.get("/operations")
async def admin_get_operation_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get operation logs"""
    query = select(OperationLog).order_by(desc(OperationLog.created_at))

    count_result = await db.execute(select(func.count()).select_from(OperationLog))
    total = count_result.scalar()

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    logs = result.scalars().all()

    return {"total": total, "page": page, "page_size": page_size, "items": logs}
