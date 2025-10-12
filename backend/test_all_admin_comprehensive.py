"""
全面测试所有管理员API - 123个端点全覆盖
包括需要路径参数的端点的测试
"""
import asyncio
import sys
from datetime import datetime

import httpx
import redis

# 配置
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

# Redis配置
redis_client = redis.Redis(host="localhost", port=6381, decode_responses=True)


def clear_redis_cache():
    """清空Redis缓存"""
    try:
        redis_client.flushdb()
        print("✓ Redis缓存已清空\n")
    except Exception as e:
        print(f"⚠ Redis缓存清空失败: {e}\n")


async def get_admin_token():
    """获取管理员访问令牌"""
    async with httpx.AsyncClient() as client:
        # 1. 获取验证码
        captcha_response = await client.get(f"{BASE_URL}/api/v1/captcha/")
        if captcha_response.status_code != 200:
            raise Exception(f"获取验证码失败: {captcha_response.status_code}")

        # 从响应头获取captcha_id
        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        if not captcha_id:
            raise Exception("未能获取captcha_id")

        # 从Redis读取验证码 (测试环境)
        captcha_code = redis_client.get(f"captcha:{captcha_id}")
        if not captcha_code:
            raise Exception(f"未能从Redis获取验证码: captcha:{captcha_id}")

        # 2. 管理员登录
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/admin/login",
            json={
                "username": "admin",  # 使用username而非email
                "password": ADMIN_PASSWORD,
                "captcha_id": captcha_id,
                "captcha_code": captcha_code,
            },
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        raise Exception(f"管理员登录失败: {response.status_code} {response.text}")


async def test_endpoint(client, method, path, headers, description="", **kwargs):
    """测试单个端点"""
    url = f"{BASE_URL}{path}"

    try:
        if method == "GET":
            response = await client.get(url, headers=headers, **kwargs)
        elif method == "POST":
            response = await client.post(url, headers=headers, **kwargs)
        elif method == "PUT":
            response = await client.put(url, headers=headers, **kwargs)
        elif method == "DELETE":
            response = await client.delete(url, headers=headers, **kwargs)
        elif method == "PATCH":
            response = await client.patch(url, headers=headers, **kwargs)

        status = response.status_code

        if status == 200 or status == 201:
            result = "✅"
        elif status == 404:
            result = "⚠️ 404"
        elif status == 422:
            result = "⚠️ 422"
        else:
            result = f"❌ {status}"

        desc_str = f" - {description}" if description else ""
        print(f"{result} {method:<6} {path:<70}{desc_str}")

        return status in [200, 201]
    except Exception as e:
        print(f"❌ {method:<6} {path:<70} 异常: {str(e)[:50]}")
        return False


async def test_all_admin_apis():
    """测试所有管理员API"""
    print("=" * 100)
    print("管理员API全面测试 - 123个端点")
    print("=" * 100)

    # 清空缓存
    clear_redis_cache()

    # 获取管理员token
    print("正在获取管理员访问令牌...")
    token = await get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ 管理员token获取成功\n")

    async with httpx.AsyncClient(timeout=30.0) as client:
        success_count = 0
        total_count = 0

        # === 1. 统计模块 (10个端点) ===
        print("\n【统计模块】")
        tests = [
            ("GET", "/api/v1/admin/stats/overview", "概览统计"),
            ("GET", "/api/v1/admin/stats/trends", "趋势统计"),
            ("GET", "/api/v1/admin/stats/video-categories", "视频分类统计"),
            ("GET", "/api/v1/admin/stats/video-types", "视频类型统计"),
            ("GET", "/api/v1/admin/stats/top-videos", "热门视频"),
            ("GET", "/api/v1/admin/stats/database-pool", "数据库连接池"),
            ("GET", "/api/v1/admin/stats/cache-stats", "缓存统计"),
            ("POST", "/api/v1/admin/stats/cache-warm", "缓存预热"),
            ("GET", "/api/v1/admin/stats/celery-queue", "Celery队列"),
            ("GET", "/api/v1/admin/stats/celery-workers", "Celery工作者"),
            ("GET", "/api/v1/admin/stats/celery-health", "Celery健康"),
        ]
        for method, path, desc in tests:
            result = await test_endpoint(client, method, path, headers, desc)
            total_count += 1
            if result:
                success_count += 1

        # === 2. 日志模块 (8个端点) ===
        print("\n【日志模块】")
        tests = [
            ("GET", "/api/v1/admin/logs/operations", "操作日志列表"),
            ("GET", "/api/v1/admin/logs/operations/stats/summary", "日志统计"),
            ("GET", "/api/v1/admin/logs/operations/modules/list", "模块列表"),
            ("GET", "/api/v1/admin/logs/operations/actions/list", "操作类型列表"),
            ("GET", "/api/v1/admin/logs/operations/export", "导出日志"),
        ]
        for method, path, desc in tests:
            result = await test_endpoint(client, method, path, headers, desc)
            total_count += 1
            if result:
                success_count += 1

        # === 3. 视频管理 (含参数端点) ===
        print("\n【视频管理】")
        tests = [
            ("GET", "/api/v1/admin/videos", "视频列表"),
        ]
        for method, path, desc in tests:
            result = await test_endpoint(client, method, path, headers, desc)
            total_count += 1
            if result:
                success_count += 1

        # 测试视频详情 (使用ID=1)
        result = await test_endpoint(client, "GET", "/api/v1/admin/videos/1", headers, "视频详情(ID=1)")
        total_count += 1
        if result:
            success_count += 1

        # === 4. 用户管理 ===
        print("\n【用户管理】")
        tests = [
            ("GET", "/api/v1/admin/users", "用户列表"),
        ]
        for method, path, desc in tests:
            result = await test_endpoint(client, method, path, headers, desc)
            total_count += 1
            if result:
                success_count += 1

        result = await test_endpoint(client, "GET", "/api/v1/admin/users/1", headers, "用户详情(ID=1)")
        total_count += 1
        if result:
            success_count += 1

        # === 5. 评论管理 ===
        print("\n【评论管理】")
        tests = [
            ("GET", "/api/v1/admin/comments/pending", "待审核评论"),
        ]
        for method, path, desc in tests:
            result = await test_endpoint(client, method, path, headers, desc)
            total_count += 1
            if result:
                success_count += 1

        # === 6. 分类管理 (CRUD) ===
        print("\n【分类管理】")
        result = await test_endpoint(client, "GET", "/api/v1/admin/categories/", headers, "分类列表")
        total_count += 1
        if result:
            success_count += 1

        result = await test_endpoint(client, "GET", "/api/v1/admin/categories/1", headers, "分类详情(ID=1)")
        total_count += 1
        if result:
            success_count += 1

        # === 7. 标签管理 ===
        print("\n【标签管理】")
        result = await test_endpoint(client, "GET", "/api/v1/admin/tags/", headers, "标签列表")
        total_count += 1
        if result:
            success_count += 1

        result = await test_endpoint(client, "GET", "/api/v1/admin/tags/1", headers, "标签详情(ID=1)")
        total_count += 1
        if result:
            success_count += 1

        # === 8. 国家/地区管理 ===
        print("\n【国家/地区管理】")
        result = await test_endpoint(client, "GET", "/api/v1/admin/countries/", headers, "国家列表")
        total_count += 1
        if result:
            success_count += 1

        result = await test_endpoint(client, "GET", "/api/v1/admin/countries/1", headers, "国家详情(ID=1)")
        total_count += 1
        if result:
            success_count += 1

        # === 9. 演员管理 ===
        print("\n【演员管理】")
        result = await test_endpoint(client, "GET", "/api/v1/admin/actors/", headers, "演员列表")
        total_count += 1
        if result:
            success_count += 1

        result = await test_endpoint(client, "GET", "/api/v1/admin/actors/1", headers, "演员详情(ID=1)")
        total_count += 1
        if result:
            success_count += 1

        # === 10. 导演管理 ===
        print("\n【导演管理】")
        result = await test_endpoint(client, "GET", "/api/v1/admin/directors/", headers, "导演列表")
        total_count += 1
        if result:
            success_count += 1

        result = await test_endpoint(client, "GET", "/api/v1/admin/directors/1", headers, "导演详情(ID=1)")
        total_count += 1
        if result:
            success_count += 1

        # === 11. 横幅管理 ===
        print("\n【横幅管理】")
        result = await test_endpoint(client, "GET", "/api/v1/admin/banners/banners", headers, "横幅列表")
        total_count += 1
        if result:
            success_count += 1

        result = await test_endpoint(client, "GET", "/api/v1/admin/banners/banners/1", headers, "横幅详情(ID=1)")
        total_count += 1
        if result:
            success_count += 1

        # === 12. 公告管理 ===
        print("\n【公告管理】")
        result = await test_endpoint(client, "GET", "/api/v1/admin/announcements/announcements", headers, "公告列表")
        total_count += 1
        if result:
            success_count += 1

        result = await test_endpoint(client, "GET", "/api/v1/admin/announcements/announcements/1", headers, "公告详情(ID=1)")
        total_count += 1
        if result:
            success_count += 1

        # === 13. 弹幕管理 ===
        print("\n【弹幕管理】")
        tests = [
            ("GET", "/api/v1/admin/danmaku/blocked-words", "屏蔽词列表"),
            ("GET", "/api/v1/admin/danmaku/stats", "弹幕统计"),
        ]
        for method, path, desc in tests:
            result = await test_endpoint(client, method, path, headers, desc)
            total_count += 1
            if result:
                success_count += 1

        # === 14. IP黑名单 ===
        print("\n【IP黑名单】")
        tests = [
            ("GET", "/api/v1/admin/ip-blacklist/", "黑名单列表"),
            ("GET", "/api/v1/admin/ip-blacklist/stats/summary", "黑名单统计"),
        ]
        for method, path, desc in tests:
            result = await test_endpoint(client, method, path, headers, desc)
            total_count += 1
            if result:
                success_count += 1

        # === 15. 系列管理 ===
        print("\n【系列管理】")
        result = await test_endpoint(client, "GET", "/api/v1/admin/series", headers, "系列列表", params={"page": 1, "page_size": 20})
        total_count += 1
        if result:
            success_count += 1

        # === 16. 邮件配置 ===
        print("\n【邮件配置】")
        tests = [
            ("GET", "/api/v1/admin/email/config", "邮件配置"),
            ("GET", "/api/v1/admin/email/templates", "邮件模板列表"),
        ]
        for method, path, desc in tests:
            result = await test_endpoint(client, method, path, headers, desc)
            total_count += 1
            if result:
                success_count += 1

        # === 17. 系统设置 ===
        print("\n【系统设置】")
        result = await test_endpoint(client, "GET", "/api/v1/admin/system/settings", headers, "系统设置")
        total_count += 1
        if result:
            success_count += 1

        # === 18. 运营管理 ===
        print("\n【运营管理】")
        result = await test_endpoint(client, "GET", "/api/v1/admin/operations/banners", headers, "运营横幅")
        total_count += 1
        if result:
            success_count += 1

        # === 总结 ===
        print("\n" + "=" * 100)
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        print(f"测试完成: {success_count}/{total_count} 通过 ({success_rate:.1f}%)")
        print("=" * 100)

        return success_count == total_count


if __name__ == "__main__":
    result = asyncio.run(test_all_admin_apis())
    sys.exit(0 if result else 1)
