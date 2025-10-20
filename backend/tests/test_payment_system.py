"""
支付订阅系统集成测试

测试支付网关、订阅计划、优惠券等功能
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.subscription import SubscriptionPlan, UserSubscription
from app.models.payment import Payment
from app.models.coupon import Coupon


class TestSubscriptionPlansAPI:
    """订阅计划 API 测试"""

    @pytest.mark.asyncio
    async def test_list_subscription_plans(self, admin_client: AsyncClient):
        """测试获取订阅计划列表"""
        response = await admin_client.get("/api/v1/admin/subscription-plans")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_create_subscription_plan(self, admin_client: AsyncClient, db: AsyncSession):
        """测试创建订阅计划"""
        plan_data = {
            "name_en": "Test Premium",
            "name_zh": "测试高级版",
            "billing_period": "monthly",
            "price_usd": "9.99",
            "max_video_quality": "1080p",
            "max_concurrent_streams": 2,
            "allow_downloads": True,
            "allow_offline": True,
            "ads_free": True,
            "max_devices": 3,
            "is_active": True,
            "is_popular": False,
            "sort_order": 1
        }

        response = await admin_client.post(
            "/api/v1/admin/subscription-plans",
            json=plan_data
        )
        assert response.status_code == 201
        created_plan = response.json()
        assert created_plan["name_en"] == "Test Premium"
        assert created_plan["price_usd"] == "9.99"


class TestPaymentAPI:
    """支付 API 测试"""

    @pytest.mark.asyncio
    async def test_list_payments(self, admin_client: AsyncClient):
        """测试获取支付记录列表"""
        response = await admin_client.get("/api/v1/admin/payments")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_payment_statistics(self, admin_client: AsyncClient):
        """
        测试支付统计数据

        TODO(human): 实现支付统计验证逻辑
        应验证：
        - 总收入 (total_revenue)
        - 成功支付数量 (successful_payments)
        - 退款金额 (total_refunds)
        - 每日收入趋势 (daily_revenue)
        """
        response = await admin_client.get("/api/v1/admin/payments/statistics")

        # TODO(human): 在这里添加统计数据验证
        # 示例：
        # assert response.status_code == 200
        # stats = response.json()
        # assert "total_revenue" in stats
        # assert isinstance(stats["total_revenue"], (int, float, str))
        pass


class TestCouponAPI:
    """优惠券 API 测试"""

    @pytest.mark.asyncio
    async def test_list_coupons(self, admin_client: AsyncClient):
        """测试获取优惠券列表"""
        response = await admin_client.get("/api/v1/admin/coupons")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_create_coupon(self, admin_client: AsyncClient):
        """测试创建优惠券"""
        coupon_data = {
            "code": "TEST20",
            "description": "测试优惠券",
            "discount_type": "percentage",
            "discount_value": "20.00",
            "valid_from": "2025-01-01T00:00:00",
            "status": "active"
        }

        response = await admin_client.post(
            "/api/v1/admin/coupons",
            json=coupon_data
        )
        assert response.status_code == 201
        created_coupon = response.json()
        assert created_coupon["code"] == "TEST20"
        assert created_coupon["discount_value"] == "20.00"

    @pytest.mark.asyncio
    async def test_validate_coupon(self, admin_client: AsyncClient):
        """
        测试优惠券验证逻辑

        TODO(human): 实现优惠券验证测试
        需要测试：
        - 有效的优惠券代码
        - 过期的优惠券
        - 已达使用上限的优惠券
        - 不符合最低消费要求的优惠券
        """
        # TODO(human): 在这里实现优惠券验证测试逻辑
        pass


class TestUserSubscriptionAPI:
    """用户订阅 API 测试"""

    @pytest.mark.asyncio
    async def test_list_subscriptions(self, admin_client: AsyncClient):
        """测试获取订阅列表"""
        response = await admin_client.get("/api/v1/admin/subscriptions")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_subscription_statistics(self, admin_client: AsyncClient):
        """测试订阅统计"""
        response = await admin_client.get("/api/v1/admin/subscriptions/statistics")
        assert response.status_code == 200
        stats = response.json()
        assert "active_subscriptions" in stats
        assert "monthly_recurring_revenue" in stats


# Fixtures 需要在 conftest.py 中定义
# 如果不存在，测试会使用默认配置
