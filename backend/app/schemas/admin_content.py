from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Tag Schemas
class TagCreate(BaseModel):
    """Tag creation schema"""

    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)


class TagUpdate(BaseModel):
    """Tag update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)


class TagResponse(BaseModel):
    """Tag response schema"""

    id: int
    name: str
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

    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=2, max_length=10, description="ISO country code")


class CountryUpdate(BaseModel):
    """Country update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=2, max_length=10)


class CountryResponse(BaseModel):
    """Country response schema"""

    id: int
    name: str
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

    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: int = Field(0, ge=0)
    is_active: bool = True


class CategoryUpdate(BaseModel):
    """Category update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    """Category response schema"""

    id: int
    name: str
    slug: str
    description: Optional[str] = None
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
    avatar: Optional[str] = None
    biography: Optional[str] = None
    birth_date: Optional[datetime] = None
    country_id: Optional[int] = None


class ActorUpdate(BaseModel):
    """Actor update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    avatar: Optional[str] = None
    biography: Optional[str] = None
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
    avatar: Optional[str] = None
    biography: Optional[str] = None
    birth_date: Optional[datetime] = None
    country_id: Optional[int] = None


class DirectorUpdate(BaseModel):
    """Director update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    avatar: Optional[str] = None
    biography: Optional[str] = None
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
