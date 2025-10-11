"""
全面测试所有管理员API端点
"""
import asyncio
import httpx
import redis

BASE_URL = "http://localhost:8000"

async def get_admin_token():
    """获取管理员token"""
    async with httpx.AsyncClient() as client:
        # 获取验证码
        cap_resp = await client.get(f"{BASE_URL}/api/v1/captcha/")
        captcha_id = cap_resp.headers.get("x-captcha-id")

        # 从Redis获取验证码
        r = redis.Redis(host="localhost", port=6381, decode_responses=True)
        code = r.get(f"captcha:{captcha_id}")

        if not code:
            print("❌ 无法从Redis获取验证码")
            return None

        # 管理员登录
        login_resp = await client.post(
            f"{BASE_URL}/api/v1/auth/admin/login",
            json={
                "username": "admin",
                "password": "admin123456",
                "captcha_id": captcha_id,
                "captcha_code": code,
            },
        )

        if login_resp.status_code != 200:
            print(f"❌ 管理员登录失败: {login_resp.status_code}")
            print(login_resp.text[:200])
            return None

        return login_resp.json()["access_token"]


async def test_endpoint(client, method, path, headers, description=""):
    """测试单个端点"""
    url = f"{BASE_URL}{path}"

    try:
        if method == "GET":
            response = await client.get(url, headers=headers, timeout=10.0)
        elif method == "POST":
            response = await client.post(url, headers=headers, json={}, timeout=10.0)
        elif method == "PUT":
            response = await client.put(url, headers=headers, json={}, timeout=10.0)
        elif method == "DELETE":
            response = await client.delete(url, headers=headers, timeout=10.0)
        elif method == "PATCH":
            response = await client.patch(url, headers=headers, json={}, timeout=10.0)
        else:
            return (0, "Unknown method")

        status = response.status_code

        # 判断结果
        if status == 200:
            return (status, "✓ PASS")
        elif status == 201:
            return (status, "✓ PASS (Created)")
        elif status == 204:
            return (status, "✓ PASS (No Content)")
        elif status == 400:
            return (status, "⚠ Bad Request (Expected)")
        elif status == 401:
            return (status, "⚠ Unauthorized")
        elif status == 403:
            return (status, "⚠ Forbidden")
        elif status == 404:
            return (status, "⚠ Not Found (Expected)")
        elif status == 405:
            return (status, "⚠ Method Not Allowed")
        elif status == 422:
            return (status, "⚠ Validation Error (Expected)")
        elif status == 500:
            detail = response.text[:200]
            return (status, f"✗ FAIL (Server error): {detail}")
        else:
            return (status, f"? Unknown status")

    except Exception as e:
        return (0, f"✗ ERROR: {str(e)[:100]}")


async def main():
    """主测试函数"""
    print("=" * 80)
    print("VideoSite 管理员 API 全面测试")
    print("=" * 80)

    # 获取管理员token
    print("\n正在获取管理员token...")
    admin_token = await get_admin_token()

    if not admin_token:
        print("❌ 无法获取管理员token,测试终止")
        return

    print("✓ 管理员token获取成功\n")

    headers = {"Authorization": f"Bearer {admin_token}"}

    # 定义所有管理员API端点 (只测试GET和不需要参数的端点)
    tests = [
        # Stats 模块
        ("GET", "/api/v1/admin/stats/overview", "统计-概览"),
        ("GET", "/api/v1/admin/stats/trends", "统计-趋势"),
        ("GET", "/api/v1/admin/stats/video-categories", "统计-分类"),
        ("GET", "/api/v1/admin/stats/video-types", "统计-类型"),
        ("GET", "/api/v1/admin/stats/top-videos", "统计-Top视频"),
        ("GET", "/api/v1/admin/stats/cache-stats", "统计-缓存"),
        ("GET", "/api/v1/admin/stats/database-pool", "统计-数据库连接池"),
        ("GET", "/api/v1/admin/stats/celery-workers", "统计-Celery工作进程"),
        ("GET", "/api/v1/admin/stats/celery-queue", "统计-Celery队列"),
        ("GET", "/api/v1/admin/stats/celery-health", "统计-Celery健康"),

        # Logs 模块
        ("GET", "/api/v1/admin/logs/operations", "日志-操作日志列表"),
        ("GET", "/api/v1/admin/logs/operations/stats/summary", "日志-统计摘要"),
        ("GET", "/api/v1/admin/logs/operations/modules/list", "日志-模块列表"),
        ("GET", "/api/v1/admin/logs/operations/actions/list", "日志-操作列表"),

        # Videos 模块
        ("GET", "/api/v1/admin/videos", "视频-列表"),

        # Users 模块
        ("GET", "/api/v1/admin/users", "用户-列表"),

        # Comments 模块
        ("GET", "/api/v1/admin/comments", "评论-列表"),
        ("GET", "/api/v1/admin/comments/pending", "评论-待审核"),

        # Categories 模块
        ("GET", "/api/v1/admin/categories/", "分类-列表"),

        # Countries 模块
        ("GET", "/api/v1/admin/countries/", "国家-列表"),

        # Tags 模块
        ("GET", "/api/v1/admin/tags/", "标签-列表"),

        # Actors 模块
        ("GET", "/api/v1/admin/actors/", "演员-列表"),

        # Directors 模块
        ("GET", "/api/v1/admin/directors/", "导演-列表"),

        # Series 模块
        ("GET", "/api/v1/admin/series", "专辑-列表"),

        # Banners 模块
        ("GET", "/api/v1/admin/banners/banners", "Banner-列表"),

        # Announcements 模块
        ("GET", "/api/v1/admin/announcements/announcements", "公告-列表"),

        # Danmaku 模块
        ("GET", "/api/v1/admin/danmaku/stats", "弹幕-统计"),
        ("GET", "/api/v1/admin/danmaku/blocked-words", "弹幕-屏蔽词列表"),

        # Email Config 模块
        ("GET", "/api/v1/admin/email_config/config", "邮件-配置列表"),
        ("GET", "/api/v1/admin/email_config/templates", "邮件-模板列表"),

        # Settings 模块
        ("GET", "/api/v1/admin/settings/settings", "系统-设置"),

        # IP Blacklist 模块
        ("GET", "/api/v1/admin/ip_blacklist/", "IP黑名单-列表"),

        # Operations 模块
        ("GET", "/api/v1/admin/operations/banners", "运营-Banner"),
    ]

    print(f"\n开始测试 {len(tests)} 个管理员GET端点...\n")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        results = {
            "pass": [],
            "warning": [],
            "fail": [],
            "error": [],
        }

        for method, path, desc in tests:
            status, result = await test_endpoint(client, method, path, headers, desc)

            # 格式化输出
            status_str = f"[{status:3}]" if status > 0 else "[ERR]"
            print(f"{method:6} {path:60} {status_str} {result:30} # {desc}")

            # 分类结果
            if "✓ PASS" in result:
                results["pass"].append((method, path, status, desc))
            elif "⚠" in result:
                results["warning"].append((method, path, status, desc))
            elif "✗ FAIL" in result:
                results["fail"].append((method, path, status, desc))
            elif "✗ ERROR" in result:
                results["error"].append((method, path, result, desc))

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
                print(f"  {method} {path} - {desc}: {error}")

        # 计算成功率
        success_rate = (len(results["pass"]) / len(tests)) * 100
        print(f"\n成功率: {success_rate:.1f}%")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
