from app.models.admin import OperationLog, Permission, Role, RolePermission
from app.models.comment import Comment, Rating
from app.models.content import Announcement, Banner, Recommendation, Report
from app.models.danmaku import (  # 🆕 弹幕系统
    BlockedWord,
    Danmaku,
    DanmakuStatus,
    DanmakuType,
)
from app.models.favorite_folder import FavoriteFolder  # 🆕 收藏夹分组
from app.models.series import Series, SeriesStatus, SeriesType  # 🆕 视频系列/专辑
from app.models.settings import SystemSettings
from app.models.media import Media  # 🆕 媒体资源
from app.models.media_share import MediaShare  # 🆕 媒体文件分享
from app.models.media_version import MediaVersion  # 🆕 媒体文件版本历史
from app.models.share import VideoShare, SharePlatform  # 视频分享
from app.models.user import AdminUser, User
from app.models.user_activity import Favorite, WatchHistory
from app.models.video import (
    Actor,
    Category,
    Country,
    Director,
    Tag,
    Video,
    VideoActor,
    VideoCategory,
    VideoDirector,
    VideoTag,
)

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
    "Media",  # 🆕 媒体资源
    "MediaShare",  # 🆕 媒体文件分享
    "MediaVersion",  # 🆕 媒体文件版本历史
    "VideoShare",  # 视频分享
    "SharePlatform",  # 分享平台枚举
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
