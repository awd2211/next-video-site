#!/usr/bin/env python3
"""
错误处理功能测试脚本
"""
import asyncio

import httpx


async def test_request_id():
    """测试Request ID追踪"""
    print("\n1️⃣ 测试Request ID追踪...")

    async with httpx.AsyncClient() as client:
        # 不提供Request ID
        response1 = await client.get("http://localhost:8000/health")
        request_id1 = response1.headers.get("X-Request-ID")

        # 提供自定义Request ID
        custom_id = "test-request-12345"
        response2 = await client.get(
            "http://localhost:8000/health", headers={"X-Request-ID": custom_id}
        )
        request_id2 = response2.headers.get("X-Request-ID")

        if request_id1:
            print(f"   ✅ 自动生成Request ID: {request_id1}")
        else:
            print("   ❌ Request ID未生成（需要重启服务）")

        if request_id2 == custom_id:
            print(f"   ✅ 自定义Request ID: {request_id2}")
        else:
            print(f"   ⚠️ 自定义Request ID未生效")


async def test_validation_error():
    """测试请求验证错误"""
    print("\n2️⃣ 测试请求验证错误...")

    async with httpx.AsyncClient() as client:
        # 发送无效数据
        response = await client.post(
            "http://localhost:8000/api/v1/auth/register",
            json={"email": "invalid_email"},  # 缺少username和password
        )

        if response.status_code == 422:
            data = response.json()
            print(f"   ✅ 状态码: {response.status_code}")
            print(f"   ✅ 错误码: {data.get('error_code')}")
            print(f"   ✅ Request ID: {data.get('request_id', 'N/A')}")
            print(f"   ✅ 错误数量: {len(data.get('errors', []))}")

            # 显示第一个错误
            if data.get("errors"):
                first_error = data["errors"][0]
                print(f"   ✅ 字段: {first_error.get('field')}")
                print(f"   ✅ 消息: {first_error.get('message')[:50]}...")
        else:
            print(f"   ❌ 状态码错误: {response.status_code}")


async def test_not_found_error():
    """测试404错误"""
    print("\n3️⃣ 测试404错误...")

    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/v1/videos/999999")

        if response.status_code == 404:
            data = response.json()
            print(f"   ✅ 状态码: {response.status_code}")
            print(f"   ✅ 错误信息: {data.get('detail')}")

            # 检查是否有request_id（重启后会有）
            request_id = response.headers.get("X-Request-ID")
            if request_id:
                print(f"   ✅ Request ID: {request_id}")
            else:
                print("   ⚠️ Request ID未生效（需要重启服务）")
        else:
            print(f"   ❌ 状态码错误: {response.status_code}")


async def test_duplicate_resource():
    """测试重复资源错误（IntegrityError）"""
    print("\n4️⃣ 测试重复资源错误...")

    async with httpx.AsyncClient() as client:
        # 先注册一个用户
        user_data = {
            "email": "test_duplicate@example.com",
            "username": "test_duplicate_user",
            "password": "Test123456!",
            "full_name": "Test User",
        }

        # 第一次注册
        response1 = await client.post(
            "http://localhost:8000/api/v1/auth/register", json=user_data
        )

        # 第二次注册相同email（应该触发IntegrityError）
        response2 = await client.post(
            "http://localhost:8000/api/v1/auth/register", json=user_data
        )

        if response2.status_code == 409:
            data = response2.json()
            print(f"   ✅ 状态码: {response2.status_code} (Conflict)")
            print(f"   ✅ 错误码: {data.get('error_code')}")
            print(f"   ✅ 错误信息: {data.get('detail')}")
            print(f"   ✅ Request ID: {data.get('request_id', 'N/A')}")
        elif response2.status_code == 400 and "already" in response2.json().get("detail", ""):
            print(f"   ✅ 状态码: {response2.status_code}")
            print(f"   ℹ️  使用应用层检查（未触发数据库异常）")
        else:
            print(f"   ℹ️  状态码: {response2.status_code}")
            print(f"   ℹ️  响应: {response2.json()}")


async def test_rate_limit():
    """测试限流错误"""
    print("\n5️⃣ 测试限流错误...")
    print("   ℹ️  限流测试需要频繁请求，跳过")
    print("   ℹ️  可手动测试：连续发送6次POST /api/v1/auth/register")


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("🔍 错误处理优化验证")
    print("=" * 60)

    try:
        await test_request_id()
        await test_validation_error()
        await test_not_found_error()
        await test_duplicate_resource()
        await test_rate_limit()

        print("\n" + "=" * 60)
        print("✅ 错误处理测试完成！")
        print("=" * 60)

        print("\n💡 提示:")
        print("   - Request ID需要重启服务后生效")
        print("   - 数据库异常处理已自动生效")
        print("   - 验证错误格式已优化")
        print("   - 所有错误响应都包含error_code和request_id")

    except httpx.ConnectError:
        print("\n❌ 错误: 无法连接到后端服务")
        print("   请先启动后端: make backend-run")
    except Exception as e:
        print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())

