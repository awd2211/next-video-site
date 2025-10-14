"""
测试系统相关模型
包括: Settings, Notification, EmailConfig, AIConfig, OAuthConfig, Dashboard
"""
import pytest
from sqlalchemy import select

from app.models.settings import SystemSettings
from app.models.notification import Notification, AdminNotification
from app.models.email import EmailConfiguration
from app.models.ai_config import AIConfig
from app.models.oauth_config import OAuthConfiguration
from app.models.dashboard import DashboardLayout
from app.database import AsyncSessionLocal


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestSystemSettingsModel:
    """SystemSettings 模型测试"""

    async def test_create_settings(self):
        """测试创建系统设置"""
        async with AsyncSessionLocal() as db:
            settings = SystemSettings(
                key="test_setting",
                value="test_value"
            )
            db.add(settings)
            await db.commit()
            await db.refresh(settings)
            
            assert settings.id is not None
            assert settings.key == "test_setting"
            
            await db.delete(settings)
            await db.commit()


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestNotificationModel:
    """Notification 模型测试"""

    async def test_create_notification(self, test_user):
        """测试创建通知"""
        async with AsyncSessionLocal() as db:
            notification = Notification(
                user_id=test_user.id,
                type="system",
                title="测试通知",
                content="通知内容"
            )
            db.add(notification)
            await db.commit()
            await db.refresh(notification)
            
            assert notification.id is not None
            assert notification.is_read is False
            
            await db.delete(notification)
            await db.commit()


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestAdminNotificationModel:
    """AdminNotification 模型测试"""

    async def test_create_admin_notification(self, test_admin):
        """测试创建管理员通知"""
        async with AsyncSessionLocal() as db:
            notification = AdminNotification(
                admin_user_id=test_admin.id,
                type="system",
                title="管理员通知",
                content="通知内容",
                priority="high"
            )
            db.add(notification)
            await db.commit()
            await db.refresh(notification)
            
            assert notification.id is not None
            assert notification.priority == "high"
            
            await db.delete(notification)
            await db.commit()


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestEmailConfigModel:
    """EmailConfiguration 模型测试"""

    async def test_create_email_config(self):
        """测试创建邮件配置"""
        async with AsyncSessionLocal() as db:
            config = EmailConfiguration(
                provider="smtp",
                smtp_host="smtp.example.com",
                smtp_port=587,
                from_email="test@example.com"
            )
            db.add(config)
            await db.commit()
            await db.refresh(config)
            
            assert config.id is not None
            assert config.provider == "smtp"
            
            await db.delete(config)
            await db.commit()


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestAIConfigModel:
    """AIConfig 模型测试"""

    async def test_create_ai_config(self):
        """测试创建 AI 配置"""
        async with AsyncSessionLocal() as db:
            config = AIConfig(
                provider_name="OpenAI",
                provider_type="openai",
                api_key="sk-test",
                is_active=True
            )
            db.add(config)
            await db.commit()
            await db.refresh(config)
            
            assert config.id is not None
            assert config.provider_type == "openai"
            
            await db.delete(config)
            await db.commit()


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestOAuthConfigModel:
    """OAuthConfiguration 模型测试"""

    async def test_create_oauth_config(self):
        """测试创建 OAuth 配置"""
        async with AsyncSessionLocal() as db:
            config = OAuthConfiguration(
                provider="google",
                client_id="test-client-id",
                is_enabled=True
            )
            db.add(config)
            await db.commit()
            await db.refresh(config)
            
            assert config.id is not None
            assert config.provider == "google"
            
            await db.delete(config)
            await db.commit()


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestDashboardLayoutModel:
    """DashboardLayout 模型测试"""

    async def test_create_dashboard_layout(self, test_admin):
        """测试创建仪表盘布局"""
        async with AsyncSessionLocal() as db:
            layout = DashboardLayout(
                admin_user_id=test_admin.id,
                layout_config={"widgets": [{"id": "1", "type": "stats"}]}
            )
            db.add(layout)
            await db.commit()
            await db.refresh(layout)
            
            assert layout.id is not None
            assert layout.admin_user_id == test_admin.id
            
            await db.delete(layout)
            await db.commit()

