from app.models.admin import OperationLog, Permission, Role, RolePermission
from app.models.ai_config import AIProvider, AIProviderType  # 🆕 AI提供商配置
from app.models.ai_log import AIRequestLog, AIQuota, AITemplate, AIPerformanceMetric  # 🆕 AI日志和配额管理
from app.models.comment import Comment, Rating
from app.models.content import Announcement, Banner, Recommendation, Report
from app.models.coupon import Coupon, CouponStatus, DiscountType  # 🆕 优惠券系统
from app.models.invoice import Invoice, InvoiceStatus  # 🆕 发票系统
from app.models.payment import Payment, PaymentMethod, PaymentProvider, PaymentStatus, PaymentType, Currency  # 🆕 支付系统
from app.models.subscription import SubscriptionPlan, UserSubscription, BillingPeriod, SubscriptionStatus  # 🆕 订阅系统
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
from app.models.season import Season, SeasonStatus  # 🆕 电视剧季度管理
from app.models.episode import Episode, EpisodeStatus  # 🆕 电视剧单集管理
from app.models.settings import SystemSettings
from app.models.media import Media  # 🆕 媒体资源
from app.models.media_share import MediaShare  # 🆕 媒体文件分享
from app.models.media_version import MediaVersion  # 🆕 媒体文件版本历史
from app.models.share import VideoShare, SharePlatform  # 视频分享
from app.models.scheduling import (  # 🆕 统一内容调度系统
    ContentSchedule,
    ScheduleContentType,
    ScheduleHistory,
    ScheduleRecurrence,
    ScheduleStatus,
    ScheduleTemplate,
    PublishStrategy,
)
from app.models.permission_log import PermissionLog  # 🆕 权限审计日志
from app.models.data_scope import Department, DataScope, AdminUserDepartment  # 🆕 数据范围权限
from app.models.system_metrics import SystemMetrics, SystemAlert, SystemSLA  # 🆕 系统监控指标
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
    "Season",  # 🆕 电视剧季度
    "SeasonStatus",  # 🆕 季度状态枚举
    "Episode",  # 🆕 电视剧单集
    "EpisodeStatus",  # 🆕 单集状态枚举
    "Role",
    "Permission",
    "RolePermission",
    "OperationLog",
    "AIProvider",  # 🆕 AI提供商配置
    "AIProviderType",  # 🆕 AI提供商类型枚举
    "AIRequestLog",  # 🆕 AI请求日志
    "AIQuota",  # 🆕 AI配额管理
    "AITemplate",  # 🆕 AI模板
    "AIPerformanceMetric",  # 🆕 AI性能指标
    "OAuthConfig",  # 🆕 OAuth配置
    "ContentSchedule",  # 🆕 统一内容调度
    "ScheduleTemplate",  # 🆕 调度模板
    "ScheduleHistory",  # 🆕 调度历史
    "ScheduleContentType",  # 🆕 调度内容类型枚举
    "ScheduleStatus",  # 🆕 调度状态枚举
    "ScheduleRecurrence",  # 🆕 重复类型枚举
    "PublishStrategy",  # 🆕 发布策略枚举
    "Banner",
    "Recommendation",
    "Announcement",
    "Report",
    "SystemSettings",
    "PermissionLog",  # 🆕 权限审计日志
    "Department",  # 🆕 部门
    "DataScope",  # 🆕 数据范围权限
    "AdminUserDepartment",  # 🆕 管理员部门关联
    # 支付和订阅系统 🆕
    "SubscriptionPlan",
    "UserSubscription",
    "BillingPeriod",
    "SubscriptionStatus",
    "Payment",
    "PaymentMethod",
    "PaymentProvider",
    "PaymentStatus",
    "PaymentType",
    "Currency",
    "Coupon",
    "DiscountType",
    "CouponStatus",
    "Invoice",
    "InvoiceStatus",
    # 系统监控 🆕
    "SystemMetrics",
    "SystemAlert",
    "SystemSLA",
]
