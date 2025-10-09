from fastapi import APIRouter, Depends
from app.models.user import AdminUser
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


@router.get("")
async def admin_get_settings(
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get system settings"""
    return {"message": "Settings endpoint - to be implemented"}
