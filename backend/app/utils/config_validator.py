"""
配置验证工具
在应用启动时验证所有必需的配置项
"""

import os
from typing import Any

from loguru import logger


class ConfigValidator:
    """配置验证器"""

    # 验证规则
    REQUIRED_CONFIGS = [
        "DATABASE_URL",
        "DATABASE_URL_SYNC",
        "SECRET_KEY",
        "JWT_SECRET_KEY",
        "REDIS_URL",
        "MINIO_ENDPOINT",
        "MINIO_ACCESS_KEY",
        "MINIO_SECRET_KEY",
    ]

    SECURITY_CHECKS = {
        "SECRET_KEY": {
            "min_length": 32,
            "message": "SECRET_KEY should be at least 32 characters for security",
        },
        "JWT_SECRET_KEY": {
            "min_length": 32,
            "message": "JWT_SECRET_KEY should be at least 32 characters",
        },
    }

    # 不安全的默认值（生产环境禁止）
    UNSAFE_DEFAULTS = {
        "SECRET_KEY": ["changeme", "secret", "dev", "development"],
        "JWT_SECRET_KEY": ["changeme", "secret", "jwt"],
        "MINIO_SECRET_KEY": ["minioadmin", "minio123"],
    }

    @classmethod
    def validate_all(cls, config: Any, strict: bool = True) -> dict:
        """
        验证所有配置

        Args:
            config: 配置对象（Settings实例）
            strict: 严格模式（生产环境应为True）

        Returns:
            验证结果字典
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "checks": {},
        }

        # 1. 检查必需配置
        missing = cls._check_required(config)
        if missing:
            results["valid"] = False
            results["errors"].extend(missing)

        # 2. 检查安全性
        security_issues = cls._check_security(config)
        if security_issues:
            if strict:
                results["valid"] = False
                results["errors"].extend(security_issues)
            else:
                results["warnings"].extend(security_issues)

        # 3. 检查数据库连接
        db_check = cls._check_database(config)
        results["checks"]["database"] = db_check

        # 4. 检查Redis连接
        redis_check = cls._check_redis(config)
        results["checks"]["redis"] = redis_check

        # 5. 检查MinIO配置
        minio_check = cls._check_minio(config)
        results["checks"]["minio"] = minio_check

        # 6. 环境特定检查
        env_warnings = cls._check_environment(config)
        if env_warnings:
            results["warnings"].extend(env_warnings)

        return results

    @classmethod
    def _check_required(cls, config: Any) -> list[str]:
        """检查必需配置项"""
        errors = []

        for key in cls.REQUIRED_CONFIGS:
            value = getattr(config, key, None)
            if not value:
                errors.append(f"❌ Missing required config: {key}")

        return errors

    @classmethod
    def _check_security(cls, config: Any) -> list[str]:
        """检查安全配置"""
        issues = []

        # 检查长度
        for key, rules in cls.SECURITY_CHECKS.items():
            value = getattr(config, key, "")
            if len(value) < rules["min_length"]:
                issues.append(f"🔐 {rules['message']}")

        # 检查不安全默认值
        for key, unsafe_values in cls.UNSAFE_DEFAULTS.items():
            value = getattr(config, key, "").lower()
            if any(unsafe in value for unsafe in unsafe_values):
                issues.append(
                    f"⚠️ SECURITY WARNING: {key} contains unsafe default value. "
                    f"Change it in production!"
                )

        # 检查DEBUG模式
        if getattr(config, "DEBUG", False):
            issues.append(
                "⚠️ DEBUG mode is enabled. Disable in production for security!"
            )

        return issues

    @classmethod
    def _check_database(cls, config: Any) -> dict:
        """检查数据库配置"""
        result = {"status": "unknown", "details": []}

        db_url = getattr(config, "DATABASE_URL", "")

        # 检查URL格式
        if not db_url.startswith("postgresql+asyncpg://"):
            result["status"] = "error"
            result["details"].append("DATABASE_URL must use asyncpg driver")
            return result

        # 检查同步URL
        db_url_sync = getattr(config, "DATABASE_URL_SYNC", "")
        if not db_url_sync.startswith("postgresql://"):
            result["status"] = "warning"
            result["details"].append("DATABASE_URL_SYNC should use psycopg2 driver")

        result["status"] = "ok"
        return result

    @classmethod
    def _check_redis(cls, config: Any) -> dict:
        """检查Redis配置"""
        result = {"status": "unknown", "details": []}

        redis_url = getattr(config, "REDIS_URL", "")

        if not redis_url.startswith("redis://"):
            result["status"] = "error"
            result["details"].append("REDIS_URL format incorrect")
            return result

        result["status"] = "ok"
        return result

    @classmethod
    def _check_minio(cls, config: Any) -> dict:
        """检查MinIO配置"""
        result = {"status": "unknown", "details": []}

        endpoint = getattr(config, "MINIO_ENDPOINT", "")
        if not endpoint:
            result["status"] = "error"
            result["details"].append("MINIO_ENDPOINT not configured")
            return result

        # 检查HTTPS（生产环境建议）
        secure = getattr(config, "MINIO_SECURE", False)
        if not secure and not getattr(config, "DEBUG", False):
            result["details"].append(
                "⚠️ MINIO_SECURE=False in production. Consider using HTTPS."
            )

        result["status"] = "ok"
        return result

    @classmethod
    def _check_environment(cls, config: Any) -> list[str]:
        """环境特定检查"""
        warnings = []

        # 检查是否在容器中运行
        is_docker = os.path.exists("/.dockerenv")

        # 检查CORS配置
        cors_origins = getattr(config, "BACKEND_CORS_ORIGINS", [])
        if "*" in cors_origins:
            warnings.append(
                "⚠️ CORS allows all origins (*). Restrict in production!"
            )

        # 检查端口配置
        if is_docker:
            # Docker环境特定检查
            if "localhost" in str(getattr(config, "DATABASE_URL", "")):
                warnings.append(
                    "⚠️ Database URL uses 'localhost' in Docker. "
                    "Use container name instead."
                )

        return warnings

    @classmethod
    def print_results(cls, results: dict):
        """打印验证结果"""
        logger.info("\n" + "=" * 80)
        logger.info("🔍 Configuration Validation Results")
        logger.info("=" * 80)

        # 打印错误
        if results["errors"]:
            logger.error("\n❌ ERRORS:")
            for error in results["errors"]:
                logger.error(f"  {error}")

        # 打印警告
        if results["warnings"]:
            logger.warning("\n⚠️  WARNINGS:")
            for warning in results["warnings"]:
                logger.warning(f"  {warning}")

        # 打印检查结果
        logger.info("\n✅ Component Checks:")
        for component, check in results["checks"].items():
            status_icon = "✅" if check["status"] == "ok" else "❌"
            logger.info(f"  {status_icon} {component.capitalize()}: {check['status']}")
            for detail in check.get("details", []):
                logger.info(f"    - {detail}")

        # 总结
        if results["valid"]:
            logger.info("\n✅ Configuration validation PASSED")
        else:
            logger.error("\n❌ Configuration validation FAILED")
            logger.error("   Fix errors before deploying to production!")

        logger.info("=" * 80 + "\n")


def validate_startup_config():
    """
    启动时验证配置（在main.py中调用）

    Raises:
        SystemExit: 如果配置验证失败且在生产环境
    """
    try:
        from app.config import settings

        # 判断是否为生产环境
        is_production = not settings.DEBUG

        # 验证配置
        results = ConfigValidator.validate_all(settings, strict=is_production)

        # 打印结果
        ConfigValidator.print_results(results)

        # 生产环境下配置错误则退出
        if not results["valid"] and is_production:
            logger.critical("🚨 CRITICAL: Invalid configuration in production!")
            logger.critical("   Application startup aborted.")
            raise SystemExit(1)

        # 开发环境只警告
        if not results["valid"] and not is_production:
            logger.warning("⚠️  Configuration has issues (development mode)")

    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise
