"""
管理员个人资料管理 API
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import AdminUser
from app.utils.dependencies import get_current_admin_user
from app.utils.security import get_password_hash, verify_password

router = APIRouter()


class AdminProfileResponse(BaseModel):
    """管理员资料响应"""

    id: int
    email: str
    username: str
    full_name: str | None
    avatar: str | None
    is_superadmin: bool
    role_id: int | None
    timezone: str | None = "UTC"
    preferred_language: str | None = "en-US"
    preferred_theme: str | None = "light"
    created_at: str | None
    last_login_at: str | None

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    """更新个人资料请求"""

    full_name: str | None = Field(None, max_length=200, description="全名")
    avatar: str | None = Field(None, max_length=500, description="头像URL")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""

    old_password: str = Field(..., min_length=6, description="当前密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


class ChangeEmailRequest(BaseModel):
    """修改邮箱请求"""

    new_email: EmailStr = Field(..., description="新邮箱地址")
    password: str = Field(..., description="当前密码用于验证")


class UpdatePreferencesRequest(BaseModel):
    """更新用户偏好设置请求"""

    timezone: str | None = Field(None, description="时区 (e.g., 'America/New_York', 'Asia/Shanghai', 'UTC')")
    preferred_language: str | None = Field(None, description="首选语言 (e.g., 'en-US', 'zh-CN')")
    preferred_theme: str | None = Field(None, description="首选主题 ('light' 或 'dark')")


def _build_profile_response(admin: AdminUser) -> AdminProfileResponse:
    """构建管理员资料响应（辅助函数，减少代码重复）"""
    return AdminProfileResponse(
        id=admin.id,
        email=admin.email,
        username=admin.username,
        full_name=admin.full_name,
        avatar=admin.avatar,
        is_superadmin=admin.is_superadmin,
        role_id=admin.role_id,
        timezone=admin.timezone or "UTC",
        preferred_language=admin.preferred_language or "en-US",
        preferred_theme=admin.preferred_theme or "light",
        created_at=admin.created_at.isoformat() if admin.created_at else None,
        last_login_at=admin.last_login_at.isoformat() if admin.last_login_at else None,
    )


@router.get("/me", response_model=AdminProfileResponse, summary="获取当前管理员信息")
async def get_current_admin_profile(
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取当前登录管理员的个人资料

    返回管理员的完整信息，不包括敏感字段如密码
    """
    return _build_profile_response(current_admin)


@router.put("/me", response_model=AdminProfileResponse, summary="更新个人资料")
async def update_admin_profile(
    profile_data: UpdateProfileRequest,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新当前管理员的个人资料

    可以更新以下字段:
    - full_name: 全名
    - avatar: 头像URL

    不能修改: username, email, is_superadmin, role_id
    """
    # 更新可修改字段
    if profile_data.full_name is not None:
        current_admin.full_name = profile_data.full_name

    if profile_data.avatar is not None:
        current_admin.avatar = profile_data.avatar

    await db.commit()
    await db.refresh(current_admin)

    return _build_profile_response(current_admin)


@router.put("/me/password", summary="修改密码")
async def change_admin_password(
    password_data: ChangePasswordRequest,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    修改当前管理员的密码

    需要提供:
    - old_password: 当前密码（用于验证身份）
    - new_password: 新密码（至少6个字符）

    修改成功后，当前token仍然有效，但建议重新登录
    """
    # 验证旧密码
    if not verify_password(password_data.old_password, current_admin.hashed_password):
        raise HTTPException(status_code=400, detail="当前密码错误")

    # 检查新密码是否与旧密码相同
    if verify_password(password_data.new_password, current_admin.hashed_password):
        raise HTTPException(status_code=400, detail="新密码不能与当前密码相同")

    # 更新密码
    current_admin.hashed_password = get_password_hash(password_data.new_password)
    await db.commit()

    return {"message": "密码修改成功，建议重新登录"}


@router.put("/me/email", response_model=AdminProfileResponse, summary="修改邮箱")
async def change_admin_email(
    email_data: ChangeEmailRequest,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    修改当前管理员的邮箱地址

    需要提供:
    - new_email: 新邮箱地址
    - password: 当前密码（用于验证身份）

    新邮箱不能与系统中已存在的邮箱重复
    """
    # 验证密码
    if not verify_password(email_data.password, current_admin.hashed_password):
        raise HTTPException(status_code=400, detail="密码错误")

    # 检查新邮箱是否与当前邮箱相同
    if email_data.new_email == current_admin.email:
        raise HTTPException(status_code=400, detail="新邮箱不能与当前邮箱相同")

    # 检查新邮箱是否已被使用
    result = await db.execute(
        select(AdminUser).where(AdminUser.email == email_data.new_email)
    )
    existing_admin = result.scalar_one_or_none()
    if existing_admin:
        raise HTTPException(status_code=400, detail="该邮箱已被使用")

    # 更新邮箱
    current_admin.email = email_data.new_email
    await db.commit()
    await db.refresh(current_admin)

    return _build_profile_response(current_admin)


@router.put("/me/preferences", response_model=AdminProfileResponse, summary="更新用户偏好设置")
async def update_admin_preferences(
    preferences: UpdatePreferencesRequest,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新当前管理员的偏好设置

    可以更新以下设置:
    - timezone: 时区设置（例如: 'UTC', 'America/New_York', 'Asia/Shanghai'）
    - preferred_language: 首选语言（'en-US' 或 'zh-CN'）
    - preferred_theme: 首选主题（'light' 或 'dark'）

    所有字段都是可选的，只更新提供的字段
    """
    # 验证并更新时区
    if preferences.timezone is not None:
        current_admin.timezone = preferences.timezone

    # 验证并更新语言
    if preferences.preferred_language is not None:
        allowed_languages = ["en-US", "zh-CN"]
        if preferences.preferred_language not in allowed_languages:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的语言。允许的语言: {', '.join(allowed_languages)}"
            )
        current_admin.preferred_language = preferences.preferred_language

    # 验证并更新主题
    if preferences.preferred_theme is not None:
        allowed_themes = ["light", "dark"]
        if preferences.preferred_theme not in allowed_themes:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的主题。允许的主题: {', '.join(allowed_themes)}"
            )
        current_admin.preferred_theme = preferences.preferred_theme

    await db.commit()
    await db.refresh(current_admin)

    return _build_profile_response(current_admin)
