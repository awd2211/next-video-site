"""
RBAC (Role-Based Access Control) schemas
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Permission Schemas
class PermissionBase(BaseModel):
    """Base permission schema"""

    name: str = Field(..., description="Permission name")
    code: str = Field(..., description="Permission code (e.g., 'video.create')")
    description: Optional[str] = Field(None, description="Permission description")
    module: str = Field(..., description="Module name (e.g., 'video', 'user')")


class PermissionCreate(PermissionBase):
    """Schema for creating a permission"""

    pass


class PermissionUpdate(BaseModel):
    """Schema for updating a permission"""

    name: Optional[str] = None
    description: Optional[str] = None


class PermissionResponse(PermissionBase):
    """Schema for permission response"""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Role Schemas
class RoleBase(BaseModel):
    """Base role schema"""

    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    is_active: bool = Field(True, description="Whether the role is active")


class RoleCreate(RoleBase):
    """Schema for creating a role"""

    permission_ids: List[int] = Field(default_factory=list, description="List of permission IDs")


class RoleUpdate(BaseModel):
    """Schema for updating a role"""

    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permission_ids: Optional[List[int]] = None


class RoleResponse(RoleBase):
    """Schema for role response"""

    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True


class RoleListResponse(BaseModel):
    """Schema for role list response"""

    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    permission_count: int = 0

    class Config:
        from_attributes = True


# Role-Permission Assignment Schemas
class RolePermissionAssign(BaseModel):
    """Schema for assigning permissions to a role"""

    permission_ids: List[int] = Field(..., description="List of permission IDs to assign")


# Admin User Role Assignment
class AdminUserRoleAssign(BaseModel):
    """Schema for assigning a role to an admin user"""

    role_id: Optional[int] = Field(None, description="Role ID to assign (None to unassign)")


# Admin User with Role
class AdminUserRoleResponse(BaseModel):
    """Schema for admin user with role information"""

    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_superadmin: bool
    role_id: Optional[int]
    role: Optional[RoleResponse]
    created_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


# Bulk Operations
class BulkPermissionAssign(BaseModel):
    """Schema for bulk assigning permissions to roles"""

    role_ids: List[int] = Field(..., description="List of role IDs")
    permission_ids: List[int] = Field(..., description="List of permission IDs to assign")


class BulkPermissionRemove(BaseModel):
    """Schema for bulk removing permissions from roles"""

    role_ids: List[int] = Field(..., description="List of role IDs")
    permission_ids: List[int] = Field(..., description="List of permission IDs to remove")


# Permission Check
class PermissionCheckRequest(BaseModel):
    """Schema for checking permissions"""

    permission_codes: List[str] = Field(..., description="List of permission codes to check")


class PermissionCheckResponse(BaseModel):
    """Schema for permission check response"""

    has_all: bool = Field(..., description="Whether user has all requested permissions")
    has_any: bool = Field(..., description="Whether user has any of the requested permissions")
    permissions: dict[str, bool] = Field(..., description="Map of permission codes to boolean")
