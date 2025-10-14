from app.models.admin import OperationLog, Permission, Role, RolePermission
from app.models.ai_config import AIProvider, AIProviderType  # 🆕 AI提供商配置
from app.models.comment import Comment, Rating
from app.models.content import Announcement, Banner, Recommendation, Report
from app.models.oauth_config import OAuthConfig  # 🆕 OAuth配置
from app.models.dashboard import DashboardLayout  # 🆕 仪表板布局
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
from app.models.user_activity import Favorite, SearchHistory, WatchHistory
from app.models.watchlist import Watchlist  # 🆕 待看列表 (My List)
from app.models.shared_watchlist import SharedWatchlist  # 🆕 共享待看列表
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
    "SearchHistory",  # 🆕 搜索历史
    "Watchlist",  # 🆕 待看列表 (My List)
    "SharedWatchlist",  # 🆕 共享待看列表
    "Danmaku",  # 🆕 弹幕
    "BlockedWord",  # 🆕 屏蔽词
    "DanmakuType",  # 🆕 弹幕类型枚举
    "DanmakuStatus",  # 🆕 弹幕状态枚举
    "DashboardLayout",  # 🆕 仪表板布局
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
    "AIProvider",  # 🆕 AI提供商配置
    "AIProviderType",  # 🆕 AI提供商类型枚举
    "OAuthConfig",  # 🆕 OAuth配置
    "Banner",
    "Recommendation",
    "Announcement",
    "Report",
    "SystemSettings",
]
