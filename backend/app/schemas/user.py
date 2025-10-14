from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""

    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """验证密码强度"""
        from app.utils.password_validator import validate_password_field

        return validate_password_field(v)


class UserUpdate(BaseModel):
    """User update schema"""

    full_name: Optional[str] = None
    avatar: Optional[str] = None


class PasswordChange(BaseModel):
    """Password change schema"""

    old_password: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, v: str) -> str:
        """验证新密码强度"""
        from app.utils.password_validator import validate_password_field

        return validate_password_field(v)


class UserResponse(UserBase):
    """User response schema"""

    id: int
    avatar: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_vip: bool
    vip_expires_at: Optional[datetime] = None
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdminUserResponse(BaseModel):
    """Admin user response schema"""

    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool
    is_superadmin: bool
    role_id: Optional[int] = None
    timezone: Optional[str] = "UTC"
    preferred_language: Optional[str] = "en-US"
    preferred_theme: Optional[str] = "light"
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdminUserPreferencesUpdate(BaseModel):
    """Admin user preferences update schema"""

    timezone: Optional[str] = Field(None, description="User timezone (e.g., 'America/New_York', 'Asia/Shanghai', 'UTC')")
    preferred_language: Optional[str] = Field(None, description="Preferred language (e.g., 'en-US', 'zh-CN')")
    preferred_theme: Optional[str] = Field(None, description="Preferred theme ('light' or 'dark')")

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        """Validate language code"""
        if v is not None:
            allowed_languages = ["en-US", "zh-CN"]
            if v not in allowed_languages:
                raise ValueError(f"Language must be one of: {', '.join(allowed_languages)}")
        return v

    @field_validator("preferred_theme")
    @classmethod
    def validate_theme(cls, v: Optional[str]) -> Optional[str]:
        """Validate theme"""
        if v is not None:
            allowed_themes = ["light", "dark"]
            if v not in allowed_themes:
                raise ValueError(f"Theme must be one of: {', '.join(allowed_themes)}")
        return v
