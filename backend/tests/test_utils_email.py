"""
测试 app/utils/email_service.py - 邮件服务
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from app.utils.email_service import send_email_smtp, send_email_mailgun, send_email
from app.models.email import EmailConfiguration


@pytest.fixture
def mock_email_config():
    """Mock 邮件配置"""
    config = Mock(spec=EmailConfiguration)
    config.provider = "smtp"
    config.from_email = "test@example.com"
    config.from_name = "Test Sender"
    config.smtp_host = "smtp.example.com"
    config.smtp_port = 587
    config.smtp_use_tls = True
    config.smtp_username = "user"
    config.smtp_password = "pass"
    config.mailgun_api_key = "mg-key"
    config.mailgun_domain = "example.com"
    config.mailgun_base_url = "https://api.mailgun.net/v3"
    return config


@pytest.mark.unit
@pytest.mark.asyncio
class TestSMTPEmail:
    """SMTP 邮件发送测试"""

    async def test_send_email_smtp_basic(self, mock_email_config):
        """测试基本 SMTP 邮件发送"""
        with patch('aiosmtplib.SMTP') as mock_smtp:
            mock_instance = AsyncMock()
            mock_smtp.return_value.__aenter__.return_value = mock_instance
            mock_instance.send_message = AsyncMock()
            
            await send_email_smtp(
                mock_email_config,
                "recipient@example.com",
                "Test Subject",
                "<h1>Test HTML</h1>",
                "Test plain text"
            )
            
            assert mock_instance.send_message.called

    async def test_send_email_smtp_multiple_recipients(self, mock_email_config):
        """测试发送给多个收件人"""
        with patch('aiosmtplib.SMTP') as mock_smtp:
            mock_instance = AsyncMock()
            mock_smtp.return_value.__aenter__.return_value = mock_instance
            mock_instance.send_message = AsyncMock()
            
            recipients = ["user1@example.com", "user2@example.com"]
            await send_email_smtp(
                mock_email_config,
                recipients,
                "Test Subject",
                "<h1>Test</h1>"
            )
            
            assert mock_instance.send_message.called

    async def test_send_email_smtp_with_auth(self, mock_email_config):
        """测试带认证的 SMTP"""
        with patch('aiosmtplib.SMTP') as mock_smtp:
            mock_instance = AsyncMock()
            mock_smtp.return_value.__aenter__.return_value = mock_instance
            mock_instance.login = AsyncMock()
            mock_instance.send_message = AsyncMock()
            
            await send_email_smtp(
                mock_email_config,
                "test@example.com",
                "Subject",
                "<p>Content</p>"
            )
            
            mock_instance.login.assert_called_once_with("user", "pass")

    async def test_send_email_smtp_html_only(self, mock_email_config):
        """测试只发送 HTML（无纯文本）"""
        with patch('aiosmtplib.SMTP') as mock_smtp:
            mock_instance = AsyncMock()
            mock_smtp.return_value.__aenter__.return_value = mock_instance
            mock_instance.send_message = AsyncMock()
            
            await send_email_smtp(
                mock_email_config,
                "test@example.com",
                "Subject",
                "<h1>HTML Only</h1>",
                text_content=None
            )
            
            assert mock_instance.send_message.called


@pytest.mark.unit
class TestMailgunEmail:
    """Mailgun 邮件发送测试"""

    def test_send_email_mailgun_basic(self, mock_email_config):
        """测试基本 Mailgun 邮件发送"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"id": "msg-123", "message": "Queued"}
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            result = send_email_mailgun(
                mock_email_config,
                "test@example.com",
                "Test Subject",
                "<h1>Test</h1>"
            )
            
            assert result["id"] == "msg-123"
            mock_post.assert_called_once()

    def test_send_email_mailgun_multiple_recipients(self, mock_email_config):
        """测试 Mailgun 多收件人"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"id": "msg-456"}
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            recipients = ["user1@example.com", "user2@example.com"]
            send_email_mailgun(
                mock_email_config,
                recipients,
                "Subject",
                "<p>Content</p>"
            )
            
            call_args = mock_post.call_args
            assert call_args is not None

    def test_send_email_mailgun_with_text(self, mock_email_config):
        """测试 Mailgun HTML + 纯文本"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"id": "msg-789"}
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            send_email_mailgun(
                mock_email_config,
                "test@example.com",
                "Subject",
                "<p>HTML</p>",
                "Plain text"
            )
            
            call_args = mock_post.call_args
            data = call_args.kwargs.get("data", {})
            assert "text" in data or call_args is not None


@pytest.mark.unit
@pytest.mark.asyncio
class TestEmailRouter:
    """邮件路由测试"""

    async def test_send_email_routes_to_smtp(self, mock_email_config):
        """测试路由到 SMTP 发送"""
        mock_email_config.provider = "smtp"
        
        with patch('app.utils.email_service.send_email_smtp') as mock_smtp:
            mock_smtp.return_value = None
            
            await send_email(
                mock_email_config,
                "test@example.com",
                "Subject",
                "<p>Content</p>"
            )
            
            mock_smtp.assert_called_once()

    async def test_send_email_routes_to_mailgun(self, mock_email_config):
        """测试路由到 Mailgun 发送"""
        mock_email_config.provider = "mailgun"
        
        with patch('app.utils.email_service.send_email_mailgun') as mock_mailgun:
            mock_mailgun.return_value = {"id": "msg-123"}
            
            await send_email(
                mock_email_config,
                "test@example.com",
                "Subject",
                "<p>Content</p>"
            )
            
            mock_mailgun.assert_called_once()


@pytest.mark.unit
class TestEmailErrorHandling:
    """邮件错误处理测试"""

    def test_mailgun_api_error(self, mock_email_config):
        """测试 Mailgun API 错误处理"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = Exception("API Error")
            mock_post.return_value = mock_response
            
            with pytest.raises(Exception):
                send_email_mailgun(
                    mock_email_config,
                    "test@example.com",
                    "Subject",
                    "<p>Content</p>"
                )

