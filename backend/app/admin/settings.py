from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.settings import SystemSettings
from app.models.user import AdminUser
from app.utils.cache import Cache
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


# Pydantic schemas
class SystemSettingsResponse(BaseModel):
    id: int
    # 网站基本信息
    site_name: str
    site_url: str
    site_description: Optional[str]
    site_keywords: Optional[str]
    site_logo: Optional[str]
    site_favicon: Optional[str]
    # SEO设置
    seo_title: Optional[str]
    seo_description: Optional[str]
    seo_keywords: Optional[str]
    # 上传设置
    upload_max_size: int
    upload_allowed_formats: List[str]
    image_max_size: int
    image_allowed_formats: List[str]
    # 视频设置
    video_auto_approve: bool
    video_require_review: bool
    video_default_quality: str
    video_enable_transcode: bool
    video_transcode_formats: List[str]
    # 评论设置
    comment_enable: bool
    comment_require_approval: bool
    comment_allow_guest: bool
    comment_max_length: int
    # 用户设置
    user_enable_registration: bool
    user_require_email_verification: bool
    user_default_avatar: Optional[str]
    user_max_favorites: int
    # 安全设置
    security_enable_captcha: bool
    security_login_max_attempts: int
    security_login_lockout_duration: int
    security_session_timeout: int
    # 其他设置
    maintenance_mode: bool
    maintenance_message: Optional[str]
    analytics_code: Optional[str]
    custom_css: Optional[str]
    custom_js: Optional[str]
    # 速率限制配置
    rate_limit_config: Optional[Dict[str, Any]]
    # 缓存配置
    cache_config: Optional[Dict[str, Any]]
    # SMTP测试配置
    smtp_test_email: Optional[str]
    smtp_last_test_at: Optional[datetime]
    smtp_last_test_status: Optional[str]
    # 支付网关配置
    payment_gateway_config: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class SystemSettingsUpdate(BaseModel):
    # 网站基本信息
    site_name: Optional[str] = None
    site_url: Optional[str] = None
    site_description: Optional[str] = None
    site_keywords: Optional[str] = None
    site_logo: Optional[str] = None
    site_favicon: Optional[str] = None
    # SEO设置
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    # 上传设置
    upload_max_size: Optional[int] = None
    upload_allowed_formats: Optional[List[str]] = None
    image_max_size: Optional[int] = None
    image_allowed_formats: Optional[List[str]] = None
    # 视频设置
    video_auto_approve: Optional[bool] = None
    video_require_review: Optional[bool] = None
    video_default_quality: Optional[str] = None
    video_enable_transcode: Optional[bool] = None
    video_transcode_formats: Optional[List[str]] = None
    # 评论设置
    comment_enable: Optional[bool] = None
    comment_require_approval: Optional[bool] = None
    comment_allow_guest: Optional[bool] = None
    comment_max_length: Optional[int] = None
    # 用户设置
    user_enable_registration: Optional[bool] = None
    user_require_email_verification: Optional[bool] = None
    user_default_avatar: Optional[str] = None
    user_max_favorites: Optional[int] = None
    # 安全设置
    security_enable_captcha: Optional[bool] = None
    security_login_max_attempts: Optional[int] = None
    security_login_lockout_duration: Optional[int] = None
    security_session_timeout: Optional[int] = None
    # 其他设置
    maintenance_mode: Optional[bool] = None
    maintenance_message: Optional[str] = None
    analytics_code: Optional[str] = None
    custom_css: Optional[str] = None
    custom_js: Optional[str] = None
    # 速率限制配置
    rate_limit_config: Optional[Dict[str, Any]] = None
    # 缓存配置
    cache_config: Optional[Dict[str, Any]] = None
    # SMTP测试配置
    smtp_test_email: Optional[str] = None
    # 支付网关配置
    payment_gateway_config: Optional[Dict[str, Any]] = None


async def get_or_create_settings(db: AsyncSession) -> SystemSettings:
    """获取或创建系统设置（单例模式）"""
    result = await db.execute(select(SystemSettings).limit(1))
    settings = result.scalar_one_or_none()

    if not settings:
        # 创建默认设置
        settings = SystemSettings(
            upload_allowed_formats=["mp4", "avi", "mkv", "webm", "flv"],
            image_allowed_formats=["jpg", "jpeg", "png", "webp"],
            video_transcode_formats=["720p", "1080p"],
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)

    return settings


@router.get("/settings", response_model=SystemSettingsResponse)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取系统设置"""
    # 尝试从缓存获取
    cache_key = "system_settings"
    cached = await Cache.get(cache_key)
    if cached:
        return cached

    settings = await get_or_create_settings(db)

    # 缓存30分钟
    response = SystemSettingsResponse.model_validate(settings)
    await Cache.set(cache_key, response.model_dump(), ttl=1800)

    return response


@router.put("/settings", response_model=SystemSettingsResponse)
async def update_settings(
    settings_data: SystemSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """更新系统设置"""
    settings = await get_or_create_settings(db)

    # 更新字段
    update_data = settings_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)

    await db.commit()
    await db.refresh(settings)

    # 清除缓存
    await Cache.delete("system_settings")

    # 发送系统设置变更通知
    try:
        from app.utils.admin_notification_service import AdminNotificationService

        # 确定变更的设置类别
        changed_categories = set()
        for key in update_data.keys():
            if key.startswith("site_") or key in ["site_name", "site_url"]:
                changed_categories.add("site")
            elif key.startswith("video_"):
                changed_categories.add("video")
            elif key.startswith("comment_"):
                changed_categories.add("comment")
            elif key.startswith("user_"):
                changed_categories.add("user")
            elif key.startswith("security_"):
                changed_categories.add("security")
            else:
                changed_categories.add("other")

        # 生成详情
        if len(changed_categories) == 1:
            category = list(changed_categories)[0]
        elif len(changed_categories) > 1:
            category = "other"
            details = f"更新了 {len(update_data)} 项设置"
        else:
            category = "other"
            details = None

        if len(changed_categories) == 1:
            details = f"更新了 {len(update_data)} 项设置"

        await AdminNotificationService.notify_system_settings_change(
            db=db,
            setting_category=category,
            action="updated",
            admin_username=current_admin.username,
            details=details,
        )
    except Exception as e:
        print(f"Failed to send settings update notification: {e}")

    return settings


@router.post("/settings/reset", response_model=SystemSettingsResponse)
async def reset_settings(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """重置系统设置为默认值"""
    settings: SystemSettings = await get_or_create_settings(db)

    # 重置为默认值  # type: ignore
    settings.site_name = "视频网站"
    settings.site_url = "http://localhost:3000"
    settings.site_description = None
    settings.site_keywords = None
    settings.site_logo = None
    settings.site_favicon = None

    settings.seo_title = None
    settings.seo_description = None
    settings.seo_keywords = None

    settings.upload_max_size = 1024
    settings.upload_allowed_formats = ["mp4", "avi", "mkv", "webm", "flv"]
    settings.image_max_size = 10
    settings.image_allowed_formats = ["jpg", "jpeg", "png", "webp"]

    settings.video_auto_approve = False
    settings.video_require_review = True
    settings.video_default_quality = "720p"
    settings.video_enable_transcode = True
    settings.video_transcode_formats = ["720p", "1080p"]

    settings.comment_enable = True
    settings.comment_require_approval = False
    settings.comment_allow_guest = False
    settings.comment_max_length = 500

    settings.user_enable_registration = True
    settings.user_require_email_verification = True
    settings.user_default_avatar = None
    settings.user_max_favorites = 1000

    settings.security_enable_captcha = True
    settings.security_login_max_attempts = 5
    settings.security_login_lockout_duration = 30
    settings.security_session_timeout = 7200

    settings.maintenance_mode = False
    settings.maintenance_message = None
    settings.analytics_code = None
    settings.custom_css = None
    settings.custom_js = None

    await db.commit()
    await db.refresh(settings)

    # 清除缓存
    await Cache.delete("system_settings")

    # 发送系统设置重置通知
    try:
        from app.utils.admin_notification_service import AdminNotificationService

        await AdminNotificationService.notify_system_settings_change(
            db=db,
            setting_category="all",
            action="reset",
            admin_username=current_admin.username,
            details="已重置所有设置为默认值",
        )
    except Exception as e:
        print(f"Failed to send settings reset notification: {e}")

    return settings


# 支付网关测试连接
class PaymentGatewayTestRequest(BaseModel):
    gateway: str  # stripe, paypal, alipay
    config: Dict[str, Any]


class PaymentGatewayTestResponse(BaseModel):
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None


@router.post("/settings/test-payment-gateway", response_model=PaymentGatewayTestResponse)
async def test_payment_gateway(
    test_request: PaymentGatewayTestRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """测试支付网关连接"""
    gateway = test_request.gateway.lower()
    config = test_request.config

    try:
        if gateway == "stripe":
            # 测试 Stripe 连接
            import stripe
            stripe.api_key = config.get("secret_key")

            # 尝试获取账户信息
            account = stripe.Account.retrieve()

            return PaymentGatewayTestResponse(
                success=True,
                message=f"Stripe 连接成功！账户 ID: {account.id}",
                details={
                    "account_id": account.id,
                    "email": account.email,
                    "country": account.country,
                    "charges_enabled": account.charges_enabled,
                }
            )

        elif gateway == "paypal":
            # 测试 PayPal 连接
            from paypalrestsdk import Api

            api = Api({
                'mode': config.get("environment", "sandbox"),
                'client_id': config.get("client_id"),
                'client_secret': config.get("client_secret")
            })

            # 获取 access token 来验证凭证
            token = api.get_access_token()

            return PaymentGatewayTestResponse(
                success=True,
                message=f"PayPal 连接成功！环境: {config.get('environment', 'sandbox')}",
                details={
                    "environment": config.get("environment"),
                    "token_obtained": bool(token),
                }
            )

        elif gateway == "alipay":
            # 测试支付宝连接（基本验证）
            required_keys = ["app_id", "private_key", "public_key"]
            missing_keys = [key for key in required_keys if not config.get(key)]

            if missing_keys:
                return PaymentGatewayTestResponse(
                    success=False,
                    message=f"配置不完整，缺少: {', '.join(missing_keys)}"
                )

            # 简单验证 App ID 格式
            app_id = config.get("app_id")
            if not app_id or len(app_id) < 10:
                return PaymentGatewayTestResponse(
                    success=False,
                    message="App ID 格式无效"
                )

            return PaymentGatewayTestResponse(
                success=True,
                message=f"支付宝配置验证通过！App ID: {app_id[:8]}...",
                details={
                    "app_id_prefix": app_id[:8],
                    "gateway_url": config.get("gateway_url"),
                }
            )

        else:
            return PaymentGatewayTestResponse(
                success=False,
                message=f"不支持的支付网关: {gateway}"
            )

    except Exception as e:
        return PaymentGatewayTestResponse(
            success=False,
            message=f"连接失败: {str(e)}"
        )
