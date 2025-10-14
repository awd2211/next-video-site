from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.utils.validation_config import DESCRIPTION_MAX_LENGTH


# Tag Schemas
class TagCreate(BaseModel):
    """Tag creation schema"""

    name: str = Field(..., min_length=1, max_length=100, description="中文名称")
    name_en: Optional[str] = Field(None, max_length=100, description="英文名称")
    slug: str = Field(..., min_length=1, max_length=100)


class TagUpdate(BaseModel):
    """Tag update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=100, description="中文名称")
    name_en: Optional[str] = Field(None, max_length=100, description="英文名称")
    slug: Optional[str] = Field(None, min_length=1, max_length=100)


class TagResponse(BaseModel):
    """Tag response schema"""

    id: int
    name: str
    name_en: Optional[str] = None
    slug: str
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedTagResponse(BaseModel):
    """Paginated tag response"""

    total: int
    page: int
    page_size: int
    pages: int
    items: List[TagResponse]


# Country Schemas
class CountryCreate(BaseModel):
    """Country creation schema"""

    name: str = Field(..., min_length=1, max_length=100, description="中文名称")
    name_en: Optional[str] = Field(None, max_length=100, description="英文名称")
    code: str = Field(..., min_length=2, max_length=10, description="ISO country code")


class CountryUpdate(BaseModel):
    """Country update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=100, description="中文名称")
    name_en: Optional[str] = Field(None, max_length=100, description="英文名称")
    code: Optional[str] = Field(None, min_length=2, max_length=10)


class CountryResponse(BaseModel):
    """Country response schema"""

    id: int
    name: str
    name_en: Optional[str] = None
    code: str
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedCountryResponse(BaseModel):
    """Paginated country response"""

    total: int
    page: int
    page_size: int
    pages: int
    items: List[CountryResponse]


# Category Schemas
class CategoryCreate(BaseModel):
    """Category creation schema"""

    name: str = Field(..., min_length=1, max_length=100, description="中文名称")
    name_en: Optional[str] = Field(None, max_length=100, description="英文名称")
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGTH, description="中文描述")
    description_en: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGTH, description="英文描述")
    parent_id: Optional[int] = None
    sort_order: int = Field(0, ge=0)
    is_active: bool = True


class CategoryUpdate(BaseModel):
    """Category update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=100, description="中文名称")
    name_en: Optional[str] = Field(None, max_length=100, description="英文名称")
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGTH, description="中文描述")
    description_en: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGTH, description="英文描述")
    parent_id: Optional[int] = None
    sort_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    """Category response schema"""

    id: int
    name: str
    name_en: Optional[str] = None
    slug: str
    description: Optional[str] = None
    description_en: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedCategoryResponse(BaseModel):
    """Paginated category response"""

    total: int
    page: int
    page_size: int
    pages: int
    items: List[CategoryResponse]


# Actor Schemas
class ActorCreate(BaseModel):
    """Actor creation schema"""

    name: str = Field(..., min_length=1, max_length=200)
    avatar: Optional[str] = Field(None, max_length=2048)
    biography: Optional[str] = Field(None, max_length=1000)
    birth_date: Optional[datetime] = None
    country_id: Optional[int] = None


class ActorUpdate(BaseModel):
    """Actor update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    avatar: Optional[str] = Field(None, max_length=2048)
    biography: Optional[str] = Field(None, max_length=1000)
    birth_date: Optional[datetime] = None
    country_id: Optional[int] = None


class ActorAdminResponse(BaseModel):
    """Actor admin response schema"""

    id: int
    name: str
    avatar: Optional[str] = None
    biography: Optional[str] = None
    birth_date: Optional[datetime] = None
    country_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedActorAdminResponse(BaseModel):
    """Paginated actor admin response"""

    total: int
    page: int
    page_size: int
    pages: int
    items: List[ActorAdminResponse]


# Director Schemas
class DirectorCreate(BaseModel):
    """Director creation schema"""

    name: str = Field(..., min_length=1, max_length=200)
    avatar: Optional[str] = Field(None, max_length=2048)
    biography: Optional[str] = Field(None, max_length=1000)
    birth_date: Optional[datetime] = None
    country_id: Optional[int] = None


class DirectorUpdate(BaseModel):
    """Director update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    avatar: Optional[str] = Field(None, max_length=2048)
    biography: Optional[str] = Field(None, max_length=1000)
    birth_date: Optional[datetime] = None
    country_id: Optional[int] = None


class DirectorAdminResponse(BaseModel):
    """Director admin response schema"""

    id: int
    name: str
    avatar: Optional[str] = None
    biography: Optional[str] = None
    birth_date: Optional[datetime] = None
    country_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedDirectorAdminResponse(BaseModel):
    """Paginated director admin response"""

    total: int
    page: int
    page_size: int
    pages: int
    items: List[DirectorAdminResponse]


# Announcement Schemas
class AnnouncementCreate(BaseModel):
    """Announcement creation schema"""

    title: str = Field(..., min_length=1, max_length=200, description="中文标题")
    title_en: Optional[str] = Field(None, max_length=200, description="英文标题")
    content: str = Field(..., min_length=1, max_length=2000, description="中文内容")
    content_en: Optional[str] = Field(None, max_length=2000, description="英文内容")
    type: str = Field("info", description="类型: info, warning, success, error")
    is_active: bool = True
    is_pinned: bool = False
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class AnnouncementUpdate(BaseModel):
    """Announcement update schema"""

    title: Optional[str] = Field(None, min_length=1, max_length=200, description="中文标题")
    title_en: Optional[str] = Field(None, max_length=200, description="英文标题")
    content: Optional[str] = Field(None, min_length=1, max_length=2000, description="中文内容")
    content_en: Optional[str] = Field(None, max_length=2000, description="英文内容")
    type: Optional[str] = Field(None, description="类型: info, warning, success, error")
    is_active: Optional[bool] = None
    is_pinned: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class AnnouncementResponse(BaseModel):
    """Announcement response schema"""

    id: int
    title: str
    title_en: Optional[str] = None
    content: str
    content_en: Optional[str] = None
    type: str
    is_active: bool
    is_pinned: bool
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaginatedAnnouncementResponse(BaseModel):
    """Paginated announcement response"""

    total: int
    page: int
    page_size: int
    pages: int
    items: List[AnnouncementResponse]
