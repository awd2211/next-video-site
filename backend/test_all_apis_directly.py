#!/usr/bin/env python3
"""
直接测试所有API端点的脚本
不依赖pytest fixtures,直接与后端服务通信
"""
import asyncio
import httpx
from typing import Dict, List, Tuple
import json


BASE_URL = "http://localhost:8000"
REDIS_HOST = "localhost"
REDIS_PORT = 6381


async def get_admin_token(client: httpx.AsyncClient) -> str:
    """获取管理员token"""
    import redis

    # 获取验证码
    cap_response = await client.get(f"{BASE_URL}/api/v1/captcha/")
    captcha_id = cap_response.headers.get("x-captcha-id")

    # 从Redis读取验证码
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    captcha_code = r.get(f"captcha:{captcha_id}")

    # 登录
    response = await client.post(
        f"{BASE_URL}/api/v1/auth/admin/login",
        json={
            "username": "admin",
            "password": "admin123456",
            "captcha_id": captcha_id,
            "captcha_code": captcha_code
        }
    )

    if response.status_code == 200:
        return response.json()["access_token"]
    raise Exception(f"Admin login failed: {response.status_code} - {response.text}")


async def get_user_token(client: httpx.AsyncClient) -> str:
    """获取用户token"""
    response = await client.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "test123456"
        }
    )

    if response.status_code == 200:
        return response.json()["access_token"]
    raise Exception(f"User login failed: {response.status_code} - {response.text}")


async def test_endpoint(
    client: httpx.AsyncClient,
    method: str,
    path: str,
    headers: Dict = None,
    json_data: Dict = None,
    description: str = ""
) -> Tuple[int, str]:
    """
    测试单个端点
    返回: (status_code, result_message)
    """
    try:
        if method == "GET":
            response = await client.get(f"{BASE_URL}{path}", headers=headers)
        elif method == "POST":
            response = await client.post(f"{BASE_URL}{path}", headers=headers, json=json_data)
        elif method == "PUT":
            response = await client.put(f"{BASE_URL}{path}", headers=headers, json=json_data)
        elif method == "DELETE":
            response = await client.delete(f"{BASE_URL}{path}", headers=headers)
        elif method == "PATCH":
            response = await client.patch(f"{BASE_URL}{path}", headers=headers, json=json_data)
        else:
            return (0, f"Unknown method: {method}")

        status = response.status_code

        # 判断是否成功
        if status in [200, 201, 204]:
            return (status, "✓ PASS")
        elif status in [401, 403]:
            # 对于需要认证的端点,401/403可能是正常的
            if headers is None:
                return (status, "✓ PASS (Auth required)")
            else:
                return (status, "⚠ WARNING (Auth failed)")
        elif status in [404]:
            return (status, "⚠ INFO (Not found - may be empty)")
        elif status in [422]:
            return (status, "⚠ INFO (Validation error)")
        elif status in [429]:
            return (status, "⚠ INFO (Rate limited)")
        elif status in [409]:
            return (status, "⚠ INFO (Conflict/Duplicate)")
        elif status in [500, 503]:
            return (status, "✗ FAIL (Server error)")
        else:
            return (status, f"⚠ UNKNOWN ({status})")

    except Exception as e:
        return (0, f"✗ ERROR: {str(e)[:100]}")


async def main():
    """主测试函数"""
    print("=" * 80)
    print("VideoSite 后端 API 全面测试")
    print("=" * 80)
    print()

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 获取tokens
        print("正在获取认证tokens...")
        try:
            user_token = await get_user_token(client)
            user_headers = {"Authorization": f"Bearer {user_token}"}
            print("✓ 用户token获取成功")
        except Exception as e:
            print(f"⚠ 用户token获取失败: {e}")
            user_headers = None

        try:
            admin_token = await get_admin_token(client)
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            print("✓ 管理员token获取成功")
        except Exception as e:
            print(f"⚠ 管理员token获取失败: {e}")
            admin_headers = None

        print()
        print("=" * 80)

        # 定义所有测试端点
        tests = [
            # ===== 公开API (17个) =====
            ("GET", "/", None, None, "根端点"),
            ("GET", "/health", None, None, "健康检查"),
            ("GET", "/api/v1/captcha/", None, None, "获取验证码"),
            ("GET", "/api/v1/categories", None, None, "分类列表"),
            ("GET", "/api/v1/countries", None, None, "国家列表"),
            ("GET", "/api/v1/tags", None, None, "标签列表"),
            ("GET", "/api/v1/videos", None, None, "视频列表"),
            ("GET", "/api/v1/videos/trending", None, None, "热门视频"),
            ("GET", "/api/v1/videos/featured", None, None, "推荐视频"),
            ("GET", "/api/v1/videos/recommended", None, None, "精选视频"),
            ("GET", "/api/v1/search?q=test", None, None, "搜索视频"),
            ("GET", "/api/v1/actors/", None, None, "演员列表"),
            ("GET", "/api/v1/directors/", None, None, "导演列表"),
            ("GET", "/api/v1/series", None, None, "专辑列表"),
            ("GET", "/api/v1/series/featured/list", None, None, "推荐专辑"),
            ("GET", "/api/v1/recommendations/personalized", None, None, "个性化推荐"),
            ("GET", "/api/v1/recommendations/for-you", None, None, "为你推荐"),

            # ===== 用户认证API (10个) =====
            ("GET", "/api/v1/auth/me", user_headers, None, "获取当前用户"),
            ("POST", "/api/v1/auth/refresh", None, {"refresh_token": "dummy"}, "刷新token"),

            # ===== 用户资料API (6个) =====
            ("GET", "/api/v1/users/me", user_headers, None, "获取用户资料"),
            ("PUT", "/api/v1/users/me", user_headers, {"full_name": "Test"}, "更新用户资料"),

            # ===== 评论API (8个) =====
            ("GET", "/api/v1/comments/user/me", user_headers, None, "获取我的评论"),

            # ===== 弹幕API (5个) =====
            ("GET", "/api/v1/danmaku/my-danmaku", user_headers, None, "获取我的弹幕"),

            # ===== 收藏API (7个) =====
            ("GET", "/api/v1/favorites/", user_headers, None, "获取收藏列表"),
            ("GET", "/api/v1/favorites/folders", user_headers, None, "获取收藏夹列表"),

            # ===== 观看历史API (6个) =====
            ("GET", "/api/v1/history/", user_headers, None, "获取观看历史"),

            # ===== 通知API (6个) =====
            ("GET", "/api/v1/notifications/", user_headers, None, "获取通知列表"),
            ("GET", "/api/v1/notifications/stats", user_headers, None, "获取通知统计"),

            # ===== 管理员认证API (3个) =====
            ("GET", "/api/v1/auth/admin/me", admin_headers, None, "获取管理员信息"),

            # ===== 管理员视频管理API (9个) =====
            ("GET", "/api/v1/admin/videos", admin_headers, None, "管理员-获取所有视频"),

            # ===== 管理员用户管理API (2个) =====
            ("GET", "/api/v1/admin/users", admin_headers, None, "管理员-获取所有用户"),

            # ===== 管理员评论管理API (8个) =====
            ("GET", "/api/v1/admin/comments", admin_headers, None, "管理员-获取所有评论"),
            ("GET", "/api/v1/admin/comments/pending", admin_headers, None, "管理员-获取待审核评论"),

            # ===== 管理员分类管理API (5个) =====
            ("GET", "/api/v1/admin/categories/", admin_headers, None, "管理员-获取所有分类"),

            # ===== 管理员国家管理API (5个) =====
            ("GET", "/api/v1/admin/countries/", admin_headers, None, "管理员-获取所有国家"),

            # ===== 管理员标签管理API (5个) =====
            ("GET", "/api/v1/admin/tags/", admin_headers, None, "管理员-获取所有标签"),

            # ===== 管理员演员管理API (5个) =====
            ("GET", "/api/v1/admin/actors/", admin_headers, None, "管理员-获取所有演员"),

            # ===== 管理员导演管理API (5个) =====
            ("GET", "/api/v1/admin/directors/", admin_headers, None, "管理员-获取所有导演"),

            # ===== 管理员专辑管理API (8个) =====
            ("GET", "/api/v1/admin/series", admin_headers, None, "管理员-获取专辑列表"),

            # ===== 管理员Banner管理API (8个) =====
            ("GET", "/api/v1/admin/banners/banners", admin_headers, None, "管理员-获取Banner列表"),

            # ===== 管理员公告管理API (7个) =====
            ("GET", "/api/v1/admin/announcements/announcements", admin_headers, None, "管理员-获取公告列表"),

            # ===== 管理员统计API (11个) =====
            ("GET", "/api/v1/admin/stats/overview", admin_headers, None, "管理员-获取概览统计"),
            ("GET", "/api/v1/admin/stats/trends", admin_headers, None, "管理员-获取趋势统计"),
            ("GET", "/api/v1/admin/stats/video-categories", admin_headers, None, "管理员-获取分类统计"),
            ("GET", "/api/v1/admin/stats/top-videos", admin_headers, None, "管理员-获取Top10视频"),
            ("GET", "/api/v1/admin/stats/cache-stats", admin_headers, None, "管理员-获取缓存统计"),

            # ===== 管理员日志API (7个) =====
            ("GET", "/api/v1/admin/logs/operations", admin_headers, None, "管理员-获取操作日志"),
            ("GET", "/api/v1/admin/logs/operations/stats/summary", admin_headers, None, "管理员-获取日志统计"),

            # ===== WebSocket测试 (1个) =====
            ("GET", "/api/v1/ws/stats", None, None, "获取WebSocket统计"),
        ]

        # 执行测试
        results = {
            "pass": [],
            "warning": [],
            "fail": [],
            "error": []
        }

        print("\n开始测试 {} 个端点...\n".format(len(tests)))

        for method, path, headers, json_data, description in tests:
            status, result = await test_endpoint(client, method, path, headers, json_data, description)

            # 格式化输出
            print(f"{method:6} {path:60} [{status:3}] {result:30} # {description}")

            # 分类结果
            if "PASS" in result:
                results["pass"].append((method, path, description))
            elif "WARNING" in result or "INFO" in result:
                results["warning"].append((method, path, status, description))
            elif "FAIL" in result:
                results["fail"].append((method, path, status, description))
            elif "ERROR" in result:
                results["error"].append((method, path, result, description))

        # 输出总结
        print("\n" + "=" * 80)
        print("测试总结")
        print("=" * 80)
        print(f"总测试数: {len(tests)}")
        print(f"通过: {len(results['pass'])} ✓")
        print(f"警告/信息: {len(results['warning'])} ⚠")
        print(f"失败: {len(results['fail'])} ✗")
        print(f"错误: {len(results['error'])} ✗")
        print()

        if results["fail"]:
            print("\n失败的端点:")
            for method, path, status, desc in results["fail"]:
                print(f"  {method} {path} [{status}] - {desc}")

        if results["error"]:
            print("\n错误的端点:")
            for method, path, error, desc in results["error"]:
                print(f"  {method} {path} - {error}")

        # 计算成功率
        success_rate = (len(results["pass"]) / len(tests)) * 100
        print(f"\n成功率: {success_rate:.1f}%")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
