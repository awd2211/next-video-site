from app.models.user import User, AdminUser
from app.models.video import Video, Category, Country, Tag, Actor, Director
from app.models.video import VideoCategory, VideoTag, VideoActor, VideoDirector
from app.models.comment import Comment, Rating
from app.models.user_activity import Favorite, WatchHistory
from app.models.favorite_folder import FavoriteFolder  # 🆕 收藏夹分组
from app.models.danmaku import Danmaku, BlockedWord, DanmakuType, DanmakuStatus  # 🆕 弹幕系统
from app.models.share import VideoShare, SharePlatform  # 🆕 分享系统
from app.models.series import Series, SeriesType, SeriesStatus  # 🆕 视频系列/专辑
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
    "Danmaku",  # 🆕 弹幕
    "BlockedWord",  # 🆕 屏蔽词
    "DanmakuType",  # 🆕 弹幕类型枚举
    "DanmakuStatus",  # 🆕 弹幕状态枚举
    "VideoShare",  # 🆕 分享记录
    "SharePlatform",  # 🆕 分享平台枚举
    "Series",  # 🆕 视频系列/专辑
    "SeriesType",  # 🆕 系列类型枚举
    "SeriesStatus",  # 🆕 系列状态枚举
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
