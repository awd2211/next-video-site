from fastapi import APIRouter, Depends
from app.models.user import AdminUser
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


@router.get("/banners")
async def admin_list_banners(
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """Admin: Get banners"""
    return {"message": "Banners endpoint - to be implemented"}
