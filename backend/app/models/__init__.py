from app.models.user import User, AdminUser
from app.models.video import Video, Category, Country, Tag, Actor, Director
from app.models.video import VideoCategory, VideoTag, VideoActor, VideoDirector
from app.models.comment import Comment, Rating
from app.models.user_activity import Favorite, WatchHistory
from app.models.favorite_folder import FavoriteFolder  # 🆕 收藏夹分组
from app.models.admin import Role, Permission, RolePermission, OperationLog
from app.models.content import Banner, Recommendation, Announcement, Report
from app.models.settings import SystemSettings

__all__ = [
    "User",
    "AdminUser",
    "Video",
    "Category",
    "Country",
    "Tag",
    "Actor",
    "Director",
    "VideoCategory",
    "VideoTag",
    "VideoActor",
    "VideoDirector",
    "Comment",
    "Rating",
    "Favorite",
    "FavoriteFolder",  # 🆕 收藏夹分组
    "WatchHistory",
    "Role",
    "Permission",
    "RolePermission",
    "OperationLog",
    "Banner",
    "Recommendation",
    "Announcement",
    "Report",
    "SystemSettings",
]
