from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('password')
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
    
    @field_validator('new_password')
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
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True
