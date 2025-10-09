from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str


class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = None
    avatar: Optional[str] = None


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
