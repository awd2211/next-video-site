from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Favorite Folder Schemas
class FavoriteFolderBase(BaseModel):
    """Base schema for favorite folder"""
    name: str = Field(..., min_length=1, max_length=100, description="Folder name")
    description: Optional[str] = Field(None, max_length=500, description="Folder description")
    is_public: bool = Field(False, description="Whether the folder is public")


class FavoriteFolderCreate(FavoriteFolderBase):
    """Schema for creating a favorite folder"""
    pass


class FavoriteFolderUpdate(BaseModel):
    """Schema for updating a favorite folder"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_public: Optional[bool] = None


class FavoriteFolderResponse(FavoriteFolderBase):
    """Schema for favorite folder response"""
    id: int
    user_id: int
    is_default: bool
    video_count: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class FavoriteFolderWithVideos(FavoriteFolderResponse):
    """Schema for favorite folder with video list"""
    videos: list = Field(default_factory=list, description="Videos in this folder")

    class Config:
        from_attributes = True


class MoveFavoriteToFolder(BaseModel):
    """Schema for moving favorite to a folder"""
    favorite_id: int = Field(..., description="Favorite ID")
    target_folder_id: Optional[int] = Field(None, description="Target folder ID (None for default)")


class BatchMoveFavoritesToFolder(BaseModel):
    """Schema for batch moving favorites to a folder"""
    favorite_ids: list[int] = Field(..., min_items=1, description="List of favorite IDs")
    target_folder_id: Optional[int] = Field(None, description="Target folder ID (None for default)")
