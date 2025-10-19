"""
错误信息清理工具
防止在DEBUG模式下泄露敏感信息
"""

import re
from typing import Any


class ErrorSanitizer:
    """错误信息清理器"""

    # 敏感信息正则模式
    SENSITIVE_PATTERNS = [
        (r"password['\"]?\s*[:=]\s*['\"]?([^'\"]+)", "password=***"),  # 密码
        (r"token['\"]?\s*[:=]\s*['\"]?([^'\"]+)", "token=***"),  # Token
        (r"secret['\"]?\s*[:=]\s*['\"]?([^'\"]+)", "secret=***"),  # Secret
        (r"api[_-]?key['\"]?\s*[:=]\s*['\"]?([^'\"]+)", "api_key=***"),  # API Key
        (r"([0-9]{13,19})", "***CARD***"),  # 信用卡号
        (
            r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
            "***EMAIL***",
        ),  # 邮箱（可选）
        (r"(Bearer\s+[A-Za-z0-9-._~+/]+=*)", "Bearer ***"),  # Bearer Token
        (r"(postgres://[^@]+@)", "postgres://***@"),  # 数据库连接串
        (r"(redis://[^@]+@)", "redis://***@"),  # Redis连接串
    ]

    @classmethod
    def sanitize(cls, error_message: str) -> str:
        """
        清理错误信息中的敏感数据

        Args:
            error_message: 原始错误信息

        Returns:
            清理后的错误信息
        """
        sanitized = error_message

        for pattern, replacement in cls.SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        return sanitized

    @classmethod
    def sanitize_dict(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        递归清理字典中的敏感数据

        Args:
            data: 原始字典

        Returns:
            清理后的字典
        """
        sanitized = {}

        for key, value in data.items():
            # 检查键名是否包含敏感词
            if any(
                word in key.lower()
                for word in ["password", "secret", "token", "api_key", "auth"]
            ):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_dict(value)
            elif isinstance(value, str):
                sanitized[key] = cls.sanitize(value)
            elif isinstance(value, (list, tuple)):
                sanitized[key] = [
                    cls.sanitize_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value

        return sanitized


# 使用示例：
# from app.utils.error_sanitizer import ErrorSanitizer
#
# try:
#     raise Exception("Database error: postgres://user:password123@localhost/db")
# except Exception as e:
#     safe_message = ErrorSanitizer.sanitize(str(e))
#     # safe_message = "Database error: postgres://***@localhost/db"
