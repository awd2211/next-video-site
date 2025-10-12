"""
管理员API深度测试 - 测试所有端点类型（GET/POST/PUT/DELETE/PATCH）
"""
import asyncio
import sys
from typing import Any, Dict

import httpx
import redis

BASE_URL = "http://localhost:8000"
redis_client = redis.Redis(host="localhost", port=6381, decode_responses=True)


async def get_admin_token() -> str:
    """获取管理员token"""
    async with httpx.AsyncClient() as client:
        # 获取验证码
        captcha_response = await client.get(f"{BASE_URL}/api/v1/captcha/")
        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        captcha_code = redis_client.get(f"captcha:{captcha_id}")

        # 管理员登录
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/admin/login",
            json={
                "username": "admin",
                "password": "admin123",
                "captcha_id": captcha_id,
                "captcha_code": captcha_code,
            },
        )
        return response.json()["access_token"]


class AdminAPITester:
    """管理员API测试器"""

    def __init__(self, token: str):
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}
        self.results = {
            "GET": {"success": 0, "failed": 0, "total": 0},
            "POST": {"success": 0, "failed": 0, "total": 0},
            "PUT": {"success": 0, "failed": 0, "total": 0},
            "DELETE": {"success": 0, "failed": 0, "total": 0},
            "PATCH": {"success": 0, "failed": 0, "total": 0},
        }
        self.errors = []

    async def test_get(
        self,
        client: httpx.AsyncClient,
        path: str,
        desc: str,
        params: Dict[str, Any] = None,
    ) -> bool:
        """测试GET端点"""
        self.results["GET"]["total"] += 1
        try:
            response = await client.get(
                f"{BASE_URL}{path}", headers=self.headers, params=params or {}
            )
            if response.status_code in [200, 201]:
                print(f"  ✅ GET  {path:<60} {desc}")
                self.results["GET"]["success"] += 1
                return True
            elif response.status_code == 404:
                print(f"  ⚠️  GET  {path:<60} {desc} (404 - 资源不存在)")
                self.results["GET"]["failed"] += 1
                return False
            elif response.status_code == 422:
                print(f"  ⚠️  GET  {path:<60} {desc} (422 - 参数错误)")
                self.results["GET"]["failed"] += 1
                return False
            else:
                print(f"  ❌ GET  {path:<60} {desc} ({response.status_code})")
                self.errors.append(
                    {
                        "method": "GET",
                        "path": path,
                        "status": response.status_code,
                        "error": response.text[:200],
                    }
                )
                self.results["GET"]["failed"] += 1
                return False
        except Exception as e:
            print(f"  ❌ GET  {path:<60} {desc} (异常: {str(e)[:50]})")
            self.errors.append({"method": "GET", "path": path, "error": str(e)[:200]})
            self.results["GET"]["failed"] += 1
            return False

    async def test_post(
        self, client: httpx.AsyncClient, path: str, desc: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """测试POST端点"""
        self.results["POST"]["total"] += 1
        try:
            response = await client.post(
                f"{BASE_URL}{path}", headers=self.headers, json=data
            )
            if response.status_code in [200, 201]:
                print(f"  ✅ POST {path:<60} {desc}")
                self.results["POST"]["success"] += 1
                return response.json()
            else:
                print(f"  ❌ POST {path:<60} {desc} ({response.status_code})")
                self.errors.append(
                    {
                        "method": "POST",
                        "path": path,
                        "status": response.status_code,
                        "error": response.text[:200],
                    }
                )
                self.results["POST"]["failed"] += 1
                return None
        except Exception as e:
            print(f"  ❌ POST {path:<60} {desc} (异常: {str(e)[:50]})")
            self.errors.append({"method": "POST", "path": path, "error": str(e)[:200]})
            self.results["POST"]["failed"] += 1
            return None

    async def test_put(
        self, client: httpx.AsyncClient, path: str, desc: str, data: Dict[str, Any]
    ) -> bool:
        """测试PUT端点"""
        self.results["PUT"]["total"] += 1
        try:
            response = await client.put(
                f"{BASE_URL}{path}", headers=self.headers, json=data
            )
            if response.status_code in [200, 201]:
                print(f"  ✅ PUT  {path:<60} {desc}")
                self.results["PUT"]["success"] += 1
                return True
            else:
                print(f"  ❌ PUT  {path:<60} {desc} ({response.status_code})")
                self.errors.append(
                    {
                        "method": "PUT",
                        "path": path,
                        "status": response.status_code,
                        "error": response.text[:200],
                    }
                )
                self.results["PUT"]["failed"] += 1
                return False
        except Exception as e:
            print(f"  ❌ PUT  {path:<60} {desc} (异常: {str(e)[:50]})")
            self.errors.append({"method": "PUT", "path": path, "error": str(e)[:200]})
            self.results["PUT"]["failed"] += 1
            return False

    async def test_delete(
        self, client: httpx.AsyncClient, path: str, desc: str
    ) -> bool:
        """测试DELETE端点"""
        self.results["DELETE"]["total"] += 1
        try:
            response = await client.delete(f"{BASE_URL}{path}", headers=self.headers)
            if response.status_code in [200, 201, 204]:
                print(f"  ✅ DEL  {path:<60} {desc}")
                self.results["DELETE"]["success"] += 1
                return True
            else:
                print(f"  ❌ DEL  {path:<60} {desc} ({response.status_code})")
                self.errors.append(
                    {
                        "method": "DELETE",
                        "path": path,
                        "status": response.status_code,
                        "error": response.text[:200],
                    }
                )
                self.results["DELETE"]["failed"] += 1
                return False
        except Exception as e:
            print(f"  ❌ DEL  {path:<60} {desc} (异常: {str(e)[:50]})")
            self.errors.append(
                {"method": "DELETE", "path": path, "error": str(e)[:200]}
            )
            self.results["DELETE"]["failed"] += 1
            return False

    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "=" * 100)
        print("测试结果摘要")
        print("=" * 100)

        total_success = sum(r["success"] for r in self.results.values())
        total_failed = sum(r["failed"] for r in self.results.values())
        total_tests = sum(r["total"] for r in self.results.values())

        for method, result in self.results.items():
            if result["total"] > 0:
                success_rate = (
                    result["success"] / result["total"] * 100
                    if result["total"] > 0
                    else 0
                )
                print(
                    f"{method:<7} {result['success']:>3}/{result['total']:>3} ({success_rate:>5.1f}%)"
                )

        print("-" * 100)
        overall_rate = total_success / total_tests * 100 if total_tests > 0 else 0
        print(f"总计    {total_success:>3}/{total_tests:>3} ({overall_rate:>5.1f}%)")
        print("=" * 100)

        if self.errors:
            print(f"\n发现 {len(self.errors)} 个错误:")
            for i, error in enumerate(self.errors[:10], 1):
                print(f"\n{i}. {error['method']} {error['path']}")
                if "status" in error:
                    print(f"   状态码: {error['status']}")
                print(f"   错误: {error['error']}")

            if len(self.errors) > 10:
                print(f"\n... 还有 {len(self.errors) - 10} 个错误未显示")


async def test_all_admin_apis():
    """深度测试所有管理员API"""
    print("=" * 100)
    print("管理员API深度测试")
    print("=" * 100)
    print("\n正在获取管理员token...")
    token = await get_admin_token()
    print("✓ Token获取成功\n")

    tester = AdminAPITester(token)

    async with httpx.AsyncClient(timeout=30.0) as client:
        # ========== 1. GET端点测试 (带路径参数) ==========
        print("\n【1. GET端点 - 带路径参数】")
        await tester.test_get(client, "/api/v1/admin/videos/1", "视频详情 ID=1")
        await tester.test_get(client, "/api/v1/admin/users/1", "用户详情 ID=1")
        await tester.test_get(client, "/api/v1/admin/categories/1", "分类详情 ID=1")
        await tester.test_get(client, "/api/v1/admin/tags/1", "标签详情 ID=1")
        await tester.test_get(client, "/api/v1/admin/countries/1", "国家详情 ID=1")
        await tester.test_get(client, "/api/v1/admin/actors/1", "演员详情 ID=1")
        await tester.test_get(client, "/api/v1/admin/directors/1", "导演详情 ID=1")
        await tester.test_get(
            client, "/api/v1/admin/banners/banners/1", "横幅详情 ID=1"
        )
        await tester.test_get(
            client, "/api/v1/admin/announcements/announcements/1", "公告详情 ID=1"
        )

        # ========== 2. 分页测试 ==========
        print("\n【2. 分页和过滤测试】")
        await tester.test_get(
            client, "/api/v1/admin/videos", "视频列表-第1页", {"page": 1, "page_size": 10}
        )
        await tester.test_get(
            client, "/api/v1/admin/videos", "视频列表-第2页", {"page": 2, "page_size": 5}
        )
        await tester.test_get(
            client,
            "/api/v1/admin/videos",
            "视频列表-搜索",
            {"search": "测试", "page": 1},
        )
        await tester.test_get(
            client,
            "/api/v1/admin/users",
            "用户列表-过滤",
            {"page": 1, "page_size": 20},
        )
        await tester.test_get(
            client,
            "/api/v1/admin/logs/operations",
            "日志列表-分页",
            {"page": 1, "page_size": 50},
        )

        # ========== 3. POST端点测试 (创建操作) ==========
        print("\n【3. POST端点 - 创建操作】")

        # 创建分类
        category_data = await tester.test_post(
            client,
            "/api/v1/admin/categories/",
            "创建分类",
            {"name": "深度测试分类", "slug": "deep-test-category", "is_active": True},
        )

        # 创建标签
        tag_data = await tester.test_post(
            client,
            "/api/v1/admin/tags/",
            "创建标签",
            {"name": "深度测试标签", "slug": "deep-test-tag", "is_active": True},
        )

        # 创建国家
        country_data = await tester.test_post(
            client,
            "/api/v1/admin/countries/",
            "创建国家",
            {"name": "测试国家", "code": "TT", "is_active": True},
        )

        # 创建演员
        actor_data = await tester.test_post(
            client,
            "/api/v1/admin/actors/",
            "创建演员",
            {
                "name": "测试演员",
                "slug": "test-actor-deep",
                "bio": "这是一个测试演员",
                "is_active": True,
            },
        )

        # 创建导演
        director_data = await tester.test_post(
            client,
            "/api/v1/admin/directors/",
            "创建导演",
            {
                "name": "测试导演",
                "slug": "test-director-deep",
                "bio": "这是一个测试导演",
                "is_active": True,
            },
        )

        # ========== 4. PUT端点测试 (更新操作) ==========
        print("\n【4. PUT端点 - 更新操作】")

        if category_data and "id" in category_data:
            await tester.test_put(
                client,
                f"/api/v1/admin/categories/{category_data['id']}",
                "更新分类",
                {"name": "深度测试分类(已更新)", "is_active": True},
            )

        if tag_data and "id" in tag_data:
            await tester.test_put(
                client,
                f"/api/v1/admin/tags/{tag_data['id']}",
                "更新标签",
                {"name": "深度测试标签(已更新)", "is_active": True},
            )

        if actor_data and "id" in actor_data:
            await tester.test_put(
                client,
                f"/api/v1/admin/actors/{actor_data['id']}",
                "更新演员",
                {"name": "测试演员(已更新)", "bio": "更新后的简介", "is_active": True},
            )

        # ========== 5. DELETE端点测试 (删除操作) ==========
        print("\n【5. DELETE端点 - 删除操作】")

        if category_data and "id" in category_data:
            await tester.test_delete(
                client,
                f"/api/v1/admin/categories/{category_data['id']}",
                "删除测试分类",
            )

        if tag_data and "id" in tag_data:
            await tester.test_delete(
                client, f"/api/v1/admin/tags/{tag_data['id']}", "删除测试标签"
            )

        if country_data and "id" in country_data:
            await tester.test_delete(
                client, f"/api/v1/admin/countries/{country_data['id']}", "删除测试国家"
            )

        # ========== 6. 统计和监控端点 ==========
        print("\n【6. 统计和监控端点】")
        await tester.test_get(client, "/api/v1/admin/stats/overview", "概览统计")
        await tester.test_get(client, "/api/v1/admin/stats/trends", "趋势统计")
        await tester.test_get(
            client, "/api/v1/admin/stats/database-pool", "数据库连接池"
        )
        await tester.test_get(client, "/api/v1/admin/stats/cache-stats", "缓存统计")

        # ========== 7. 系统管理端点 ==========
        print("\n【7. 系统管理端点】")
        await tester.test_get(client, "/api/v1/admin/system/settings", "系统设置")
        await tester.test_get(client, "/api/v1/admin/email/config", "邮件配置")
        await tester.test_get(client, "/api/v1/admin/email/templates", "邮件模板")

    # 打印测试摘要
    tester.print_summary()

    # 返回测试是否完全通过
    return all(r["failed"] == 0 for r in tester.results.values())


if __name__ == "__main__":
    result = asyncio.run(test_all_admin_apis())
    sys.exit(0 if result else 1)
