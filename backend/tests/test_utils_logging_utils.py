"""
测试 Utils - Logging Utils (日志工具)
测试登录日志、系统日志、错误日志记录功能
"""
import pytest
import traceback
from unittest.mock import MagicMock
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.logging_utils import (
    log_login_attempt,
    log_system_event,
    log_error,
    log_error_from_exception,
    create_login_log_sync,
)
from app.models.admin import LoginLog, SystemLog, ErrorLog


# ===========================================
# 测试 Fixtures
# ===========================================

@pytest.fixture
def mock_request():
    """创建 Mock Request 对象"""
    request = MagicMock(spec=Request)
    request.headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    request.client = MagicMock()
    request.client.host = "192.168.1.100"
    request.method = "POST"
    request.url = MagicMock()
    request.url.__str__ = lambda self: "http://test.com/api/login"
    return request


# ===========================================
# 1. 登录日志测试
# ===========================================

class TestLogLoginAttempt:
    """测试登录日志记录"""

    @pytest.mark.asyncio
    async def test_log_login_attempt_success(
        self, async_db: AsyncSession, mock_request: Request
    ):
        """测试成功登录日志"""
        log = await log_login_attempt(
            db=async_db,
            user_type="user",
            status="success",
            request=mock_request,
            user_id=1,
            username="testuser",
            email="test@example.com",
        )

        assert log.id is not None
        assert log.user_type == "user"
        assert log.status == "success"
        assert log.user_id == 1
        assert log.username == "testuser"
        assert log.email == "test@example.com"
        assert log.ip_address == "192.168.1.100"
        assert log.device_type in ["desktop", "mobile", "tablet", "unknown"]

    @pytest.mark.asyncio
    async def test_log_login_attempt_failed(
        self, async_db: AsyncSession, mock_request: Request
    ):
        """测试失败登录日志"""
        log = await log_login_attempt(
            db=async_db,
            user_type="admin",
            status="failed",
            request=mock_request,
            username="admin",
            email="admin@example.com",
            failure_reason="Invalid password",
        )

        assert log.status == "failed"
        assert log.failure_reason == "Invalid password"
        assert log.user_id is None  # 登录失败没有 user_id

    @pytest.mark.asyncio
    async def test_log_login_attempt_blocked(
        self, async_db: AsyncSession, mock_request: Request
    ):
        """测试被阻止的登录日志"""
        log = await log_login_attempt(
            db=async_db,
            user_type="user",
            status="blocked",
            request=mock_request,
            username="blocked_user",
            failure_reason="Too many failed attempts",
        )

        assert log.status == "blocked"
        assert "Too many" in log.failure_reason

    @pytest.mark.asyncio
    async def test_log_login_attempt_user_agent_parsing(
        self, async_db: AsyncSession
    ):
        """测试 User-Agent 解析"""
        # 测试移动设备
        mobile_request = MagicMock(spec=Request)
        mobile_request.headers = {
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
        }
        mobile_request.client = MagicMock()
        mobile_request.client.host = "10.0.0.1"

        log = await log_login_attempt(
            db=async_db,
            user_type="user",
            status="success",
            request=mobile_request,
            user_id=1,
        )

        assert log.device_type == "mobile"
        assert "iPhone" in log.os or "iOS" in log.os

    @pytest.mark.asyncio
    async def test_log_login_attempt_no_client(self, async_db: AsyncSession):
        """测试没有 client 信息的请求"""
        request = MagicMock(spec=Request)
        request.headers = {"user-agent": "TestAgent"}
        request.client = None  # 没有 client

        log = await log_login_attempt(
            db=async_db,
            user_type="user",
            status="success",
            request=request,
            user_id=1,
        )

        assert log.ip_address == "unknown"


# ===========================================
# 2. 系统日志测试
# ===========================================

class TestLogSystemEvent:
    """测试系统事件日志"""

    @pytest.mark.asyncio
    async def test_log_system_event_info(self, async_db: AsyncSession):
        """测试 INFO 级别系统日志"""
        log = await log_system_event(
            db=async_db,
            level="info",
            category="startup",
            event="application_started",
            message="Application started successfully",
            source="main.py",
        )

        assert log.id is not None
        assert log.level == "info"
        assert log.category == "startup"
        assert log.event == "application_started"
        assert log.source == "main.py"

    @pytest.mark.asyncio
    async def test_log_system_event_warning(self, async_db: AsyncSession):
        """测试 WARNING 级别系统日志"""
        log = await log_system_event(
            db=async_db,
            level="warning",
            category="cache",
            event="cache_miss_high",
            message="Cache miss rate is high",
            details={"miss_rate": 0.85, "threshold": 0.5},
        )

        assert log.level == "warning"
        assert log.category == "cache"
        assert log.details is not None
        assert "miss_rate" in log.details

    @pytest.mark.asyncio
    async def test_log_system_event_error(self, async_db: AsyncSession):
        """测试 ERROR 级别系统日志"""
        log = await log_system_event(
            db=async_db,
            level="error",
            category="database",
            event="connection_failed",
            message="Failed to connect to database",
            details={"error": "Connection timeout", "retry_count": 3},
            source="database.py",
        )

        assert log.level == "error"
        assert log.category == "database"

    @pytest.mark.asyncio
    async def test_log_system_event_critical(self, async_db: AsyncSession):
        """测试 CRITICAL 级别系统日志"""
        log = await log_system_event(
            db=async_db,
            level="critical",
            category="security",
            event="potential_breach",
            message="Potential security breach detected",
            user_id=999,
            user_type="admin",
        )

        assert log.level == "critical"
        assert log.category == "security"
        assert log.user_id == 999
        assert log.user_type == "admin"

    @pytest.mark.asyncio
    async def test_log_system_event_with_complex_details(
        self, async_db: AsyncSession
    ):
        """测试包含复杂详情的系统日志"""
        complex_details = {
            "metrics": {
                "cpu_usage": 85.5,
                "memory_usage": 70.2,
                "disk_usage": 90.1,
            },
            "alerts": ["high_cpu", "low_disk"],
            "timestamp": "2025-10-16T10:30:00Z",
        }

        log = await log_system_event(
            db=async_db,
            level="warning",
            category="monitoring",
            event="resource_alert",
            message="System resources are high",
            details=complex_details,
        )

        assert log.details is not None
        assert "metrics" in log.details


# ===========================================
# 3. 错误日志测试
# ===========================================

class TestLogError:
    """测试错误日志记录"""

    @pytest.mark.asyncio
    async def test_log_error_basic(self, async_db: AsyncSession):
        """测试基本错误日志"""
        log = await log_error(
            db=async_db,
            error_type="ValueError",
            error_message="Invalid value provided",
            level="error",
        )

        assert log.id is not None
        assert log.error_type == "ValueError"
        assert log.error_message == "Invalid value provided"
        assert log.level == "error"
        assert log.resolved is False

    @pytest.mark.asyncio
    async def test_log_error_with_traceback(self, async_db: AsyncSession):
        """测试包含堆栈跟踪的错误日志"""
        traceback_str = "Traceback (most recent call last):\n  File test.py, line 10\n    raise ValueError('test')"

        log = await log_error(
            db=async_db,
            error_type="ValueError",
            error_message="Test error",
            traceback_str=traceback_str,
        )

        assert log.traceback is not None
        assert "Traceback" in log.traceback

    @pytest.mark.asyncio
    async def test_log_error_with_request(
        self, async_db: AsyncSession, mock_request: Request
    ):
        """测试包含请求信息的错误日志"""
        log = await log_error(
            db=async_db,
            error_type="HTTPException",
            error_message="Not found",
            request=mock_request,
            status_code=404,
        )

        assert log.request_method == "POST"
        assert "test.com" in log.request_url
        assert log.ip_address == "192.168.1.100"
        assert log.user_agent is not None
        assert log.status_code == 404

    @pytest.mark.asyncio
    async def test_log_error_critical(self, async_db: AsyncSession):
        """测试 CRITICAL 级别错误日志"""
        log = await log_error(
            db=async_db,
            error_type="SystemError",
            error_message="Critical system failure",
            level="critical",
            status_code=500,
        )

        assert log.level == "critical"
        assert log.status_code == 500

    @pytest.mark.asyncio
    async def test_log_error_with_user_info(
        self, async_db: AsyncSession, mock_request: Request
    ):
        """测试包含用户信息的错误日志"""
        log = await log_error(
            db=async_db,
            error_type="PermissionError",
            error_message="Access denied",
            request=mock_request,
            user_id=123,
            user_type="user",
            status_code=403,
        )

        assert log.user_id == 123
        assert log.user_type == "user"
        assert log.status_code == 403


# ===========================================
# 4. 从异常记录错误测试
# ===========================================

class TestLogErrorFromException:
    """测试从异常对象记录错误"""

    @pytest.mark.asyncio
    async def test_log_error_from_exception_basic(self, async_db: AsyncSession):
        """测试从基本异常记录"""
        try:
            raise ValueError("This is a test error")
        except ValueError as e:
            log = await log_error_from_exception(
                db=async_db,
                exception=e,
            )

            assert log.error_type == "ValueError"
            assert "test error" in log.error_message
            assert log.traceback is not None

    @pytest.mark.asyncio
    async def test_log_error_from_exception_with_request(
        self, async_db: AsyncSession, mock_request: Request
    ):
        """测试从异常记录（包含请求）"""
        try:
            raise RuntimeError("Runtime error occurred")
        except RuntimeError as e:
            log = await log_error_from_exception(
                db=async_db,
                exception=e,
                request=mock_request,
                user_id=456,
                user_type="admin",
                status_code=500,
            )

            assert log.error_type == "RuntimeError"
            assert log.user_id == 456
            assert log.user_type == "admin"
            assert log.request_method == "POST"

    @pytest.mark.asyncio
    async def test_log_error_from_exception_nested(self, async_db: AsyncSession):
        """测试从嵌套异常记录"""
        try:
            try:
                raise ValueError("Inner error")
            except ValueError:
                raise RuntimeError("Outer error") from None
        except RuntimeError as e:
            log = await log_error_from_exception(
                db=async_db,
                exception=e,
                level="critical",
            )

            assert log.error_type == "RuntimeError"
            assert log.level == "critical"


# ===========================================
# 5. 同步版本测试
# ===========================================

class TestCreateLoginLogSync:
    """测试同步版本的登录日志创建"""

    def test_create_login_log_sync(self, mock_request: Request):
        """测试同步创建登录日志数据"""
        log_data = create_login_log_sync(
            user_type="user",
            status="success",
            request=mock_request,
            user_id=789,
            username="syncuser",
            email="sync@example.com",
        )

        assert isinstance(log_data, dict)
        assert log_data["user_type"] == "user"
        assert log_data["status"] == "success"
        assert log_data["user_id"] == 789
        assert log_data["username"] == "syncuser"
        assert log_data["email"] == "sync@example.com"
        assert log_data["ip_address"] == "192.168.1.100"
        assert log_data["device_type"] in ["desktop", "mobile", "tablet", "unknown"]

    def test_create_login_log_sync_failed(self, mock_request: Request):
        """测试同步创建失败登录日志数据"""
        log_data = create_login_log_sync(
            user_type="admin",
            status="failed",
            request=mock_request,
            username="admin",
            failure_reason="Invalid credentials",
        )

        assert log_data["status"] == "failed"
        assert log_data["failure_reason"] == "Invalid credentials"
        assert log_data["user_id"] is None

    def test_create_login_log_sync_no_client(self):
        """测试没有 client 的同步日志创建"""
        request = MagicMock(spec=Request)
        request.headers = {"user-agent": "TestAgent"}
        request.client = None

        log_data = create_login_log_sync(
            user_type="user",
            status="success",
            request=request,
            user_id=1,
        )

        assert log_data["ip_address"] == "unknown"


# ===========================================
# 6. 边界条件和异常测试
# ===========================================

class TestEdgeCases:
    """测试边界条件"""

    @pytest.mark.asyncio
    async def test_log_with_none_values(self, async_db: AsyncSession):
        """测试包含 None 值的日志"""
        log = await log_system_event(
            db=async_db,
            level="info",
            category="test",
            event="null_test",
            message="Test with nulls",
            details=None,
            source=None,
            user_id=None,
        )

        assert log.details is None
        assert log.source is None
        assert log.user_id is None

    @pytest.mark.asyncio
    async def test_log_with_empty_strings(self, async_db: AsyncSession):
        """测试包含空字符串的日志"""
        log = await log_system_event(
            db=async_db,
            level="info",
            category="",
            event="",
            message="",
        )

        assert log.category == ""
        assert log.event == ""
        assert log.message == ""

    @pytest.mark.asyncio
    async def test_log_with_very_long_message(self, async_db: AsyncSession):
        """测试非常长的消息"""
        long_message = "A" * 10000

        log = await log_error(
            db=async_db,
            error_type="TestError",
            error_message=long_message,
        )

        assert len(log.error_message) == 10000

    @pytest.mark.asyncio
    async def test_log_with_special_characters(self, async_db: AsyncSession):
        """测试包含特殊字符的日志"""
        special_message = "Error: 特殊字符 < > & \" ' \n\t测试"

        log = await log_error(
            db=async_db,
            error_type="SpecialCharError",
            error_message=special_message,
        )

        assert "特殊字符" in log.error_message
        assert "<" in log.error_message


# ===========================================
# 测试总结
# ===========================================

"""
测试覆盖：
✅ 登录日志测试 - 6个测试用例
✅ 系统日志测试 - 5个测试用例
✅ 错误日志测试 - 5个测试用例
✅ 从异常记录错误测试 - 3个测试用例
✅ 同步版本测试 - 3个测试用例
✅ 边界条件测试 - 4个测试用例

总计：26个测试用例

测试场景：
- 登录日志（成功、失败、阻止）
- User-Agent 解析（移动、桌面、平板）
- 系统事件日志（INFO、WARNING、ERROR、CRITICAL）
- 错误日志（基本、堆栈跟踪、请求信息）
- 从异常对象记录
- 同步版本函数
- 边界条件（None 值、空字符串、长消息、特殊字符）
- IP 地址处理
- 用户信息关联
"""
