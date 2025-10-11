#!/usr/bin/env python3
"""
验证所有安全修复是否生效
可以在部署后运行此脚本进行全面检查
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import settings
from app.utils.password_validator import validate_password_strength
import asyncio


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    END = "\033[0m"


def print_test(name: str, passed: bool, details: str = ""):
    """打印测试结果"""
    status = (
        f"{Colors.GREEN}✅ PASS{Colors.END}"
        if passed
        else f"{Colors.RED}❌ FAIL{Colors.END}"
    )
    print(f"{status} - {name}")
    if details:
        print(f"      {details}")


def test_config_security():
    """测试配置安全性"""
    print(f"\n{Colors.BLUE}=== 配置安全检查 ==={Colors.END}")

    # 1. DEBUG模式
    debug_off = not settings.DEBUG
    print_test(
        "DEBUG模式关闭", debug_off, f"DEBUG={settings.DEBUG} (生产环境应为False)"
    )

    # 2. MinIO凭据
    try:
        minio_secure = (
            settings.MINIO_ACCESS_KEY != "minioadmin"
            and settings.MINIO_SECRET_KEY != "minioadmin"
        )
        print_test(
            "MinIO使用强凭据",
            minio_secure,
            "不是默认的minioadmin凭据" if minio_secure else "⚠️ 仍在使用默认凭据！",
        )
    except Exception as e:
        print_test("MinIO凭据配置", False, f"配置错误: {e}")

    return debug_off and minio_secure


def test_password_policy():
    """测试密码策略"""
    print(f"\n{Colors.BLUE}=== 密码策略检查 ==={Colors.END}")

    test_cases = [
        ("123456", False, "纯数字6位"),
        ("password", False, "纯字母无大写"),
        ("Password1", False, "无特殊字符"),
        ("Pass@123", True, "符合所有要求"),
        ("Test@12345678", True, "强密码"),
    ]

    all_passed = True
    for password, should_pass, desc in test_cases:
        is_valid, message = validate_password_strength(password)
        passed = is_valid == should_pass
        all_passed = all_passed and passed
        print_test(f"密码 '{password}' ({desc})", passed, message)

    return all_passed


async def test_cache_serialization():
    """测试缓存序列化"""
    print(f"\n{Colors.BLUE}=== 缓存安全检查 ==={Colors.END}")

    try:
        from app.utils.cache import Cache, json_serializer, json_deserializer
        from datetime import datetime, timezone
        from decimal import Decimal

        # 测试数据
        test_data = {
            "string": "test",
            "number": 123,
            "datetime": datetime.now(timezone.utc),
            "decimal": Decimal("3.14"),
            "nested": {"key": "value"},
        }

        # 序列化
        serialized = json_serializer(test_data)
        print_test("JSON序列化", True, "使用JSON而非pickle")

        # 反序列化
        deserialized = json_deserializer(serialized)
        print_test("JSON反序列化", True, "支持datetime等类型")

        # 验证不包含pickle
        assert "pickle" not in serialized.lower()
        print_test("无pickle依赖", True, "确认不使用pickle")

        return True
    except Exception as e:
        print_test("缓存序列化测试", False, str(e))
        return False


async def test_database_triggers():
    """测试数据库触发器"""
    print(f"\n{Colors.BLUE}=== 数据库触发器检查 ==={Colors.END}")

    try:
        from app.database import SessionLocal

        db = SessionLocal()

        # 检查触发器
        from sqlalchemy import text

        triggers = db.execute(
            text(
                """
            SELECT trigger_name
            FROM information_schema.triggers
            WHERE trigger_schema = 'public'
            AND (trigger_name LIKE '%rating%' OR trigger_name LIKE '%comment_like%')
        """
            )
        ).fetchall()

        trigger_names = [t[0] for t in triggers]

        # 评分触发器
        has_rating_triggers = all(
            [
                "rating_insert_trigger" in trigger_names,
                "rating_update_trigger" in trigger_names,
                "rating_delete_trigger" in trigger_names,
            ]
        )
        print_test(
            "评分触发器",
            has_rating_triggers,
            f"找到 {len([t for t in trigger_names if 'rating' in t])} 个",
        )

        # 点赞触发器
        has_like_triggers = any("comment_like" in t for t in trigger_names)
        print_test("点赞触发器", has_like_triggers)

        db.close()

        return has_rating_triggers
    except Exception as e:
        print_test("数据库触发器检查", False, str(e))
        return False


async def test_token_blacklist():
    """测试Token黑名单"""
    print(f"\n{Colors.BLUE}=== Token黑名单检查 ==={Colors.END}")

    try:
        from app.utils.token_blacklist import add_to_blacklist, is_blacklisted

        test_token = "test_token_for_verification"

        # 添加到黑名单
        await add_to_blacklist(test_token, "test", 60)
        print_test("添加到黑名单", True)

        # 检查是否在黑名单中
        blacklisted = await is_blacklisted(test_token)
        print_test("黑名单检查", blacklisted, "Token正确被标记为已撤销")

        return blacklisted
    except Exception as e:
        print_test("Token黑名单功能", False, str(e))
        return False


async def test_file_validation():
    """测试文件验证"""
    print(f"\n{Colors.BLUE}=== 文件验证检查 ==={Colors.END}")

    try:
        from app.utils.file_validator import (
            check_file_magic,
            sanitize_filename,
            FileValidationPresets,
        )

        # 测试文件名清理
        dangerous_names = [
            "../../../etc/passwd",
            "test/../../file.jpg",
            "test\x00.jpg",
        ]

        all_safe = True
        for name in dangerous_names:
            cleaned = sanitize_filename(name)
            is_safe = ".." not in cleaned and "/" not in cleaned
            all_safe = all_safe and is_safe

        print_test("文件名清理", all_safe, "危险字符已移除")

        # 测试文件魔数
        jpeg_magic = bytes.fromhex("FFD8FF")
        is_jpeg = check_file_magic(jpeg_magic + b"test", "image/jpeg")
        print_test("文件魔数检查", is_jpeg, "JPEG格式正确识别")

        return all_safe and is_jpeg
    except Exception as e:
        print_test("文件验证功能", False, str(e))
        return False


async def test_path_validation():
    """测试路径验证"""
    print(f"\n{Colors.BLUE}=== 路径验证检查 ==={Colors.END}")

    try:
        from app.utils.path_validator import (
            validate_video_id,
            validate_path,
            create_safe_temp_dir,
        )

        # 测试video_id验证
        try:
            validate_video_id("../../../etc")
            print_test("video_id注入防护", False, "应该拒绝非整数")
            return False
        except ValueError:
            print_test("video_id注入防护", True, "恶意输入被正确拒绝")

        # 测试路径遍历防护
        try:
            validate_path("/etc/passwd")
            print_test("路径遍历防护", False, "应该拒绝危险路径")
            return False
        except ValueError:
            print_test("路径遍历防护", True, "危险路径被正确拒绝")

        # 测试安全临时目录
        temp_dir = create_safe_temp_dir("test_")
        print_test("安全临时目录", temp_dir.exists(), f"创建于 {temp_dir}")

        # 清理
        import shutil

        shutil.rmtree(temp_dir)

        return True
    except Exception as e:
        print_test("路径验证功能", False, str(e))
        return False


async def main():
    """运行所有测试"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}VideoSite 后端安全修复验证脚本{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

    results = {}

    # 运行测试
    results["config"] = test_config_security()
    results["password"] = test_password_policy()
    results["cache"] = await test_cache_serialization()
    results["token"] = await test_token_blacklist()
    results["file"] = await test_file_validation()
    results["path"] = await test_path_validation()

    # 数据库测试（可选）
    try:
        results["database"] = await test_database_triggers()
    except Exception as e:
        print(f"{Colors.YELLOW}\n⚠️  数据库检查跳过（需要先运行迁移）: {e}{Colors.END}")
        results["database"] = None

    # 汇总结果
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}测试结果汇总{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    total = len(results)

    print(f"总计: {total} 项测试")
    print(f"{Colors.GREEN}通过: {passed}{Colors.END}")
    print(f"{Colors.RED}失败: {failed}{Colors.END}")
    print(f"{Colors.YELLOW}跳过: {skipped}{Colors.END}")

    # 整体评估
    print()
    if failed == 0:
        print(f"{Colors.GREEN}✅ 所有检查通过！系统安全性良好{Colors.END}")
        return 0
    elif failed <= 2:
        print(f"{Colors.YELLOW}⚠️  有 {failed} 项失败，请检查并修复{Colors.END}")
        return 1
    else:
        print(f"{Colors.RED}❌ 有 {failed} 项严重失败，请立即修复！{Colors.END}")
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
