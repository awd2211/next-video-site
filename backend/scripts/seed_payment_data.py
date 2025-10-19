"""
种子数据脚本 - 支付和订阅系统

创建初始订阅套餐、优惠券等测试数据
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import select, func

from app.database import SessionLocal
from app.models.subscription import (
    SubscriptionPlan,
    BillingPeriod,
)
from app.models.coupon import (
    Coupon,
    DiscountType,
    CouponStatus,
)
from app.models.user import AdminUser
from app.utils.security import get_password_hash


def create_subscription_plans(db):
    """创建初始订阅套餐"""
    print("Creating subscription plans...")

    plans = [
        # 月度套餐
        SubscriptionPlan(
            name="Basic Monthly",
            name_en="Basic Monthly",
            name_zh="基础月度套餐",
            description="Perfect for casual viewers",
            description_en="Perfect for casual viewers",
            description_zh="适合休闲观看的用户",
            billing_period=BillingPeriod.MONTHLY,
            price_usd=Decimal("9.99"),
            price_cny=Decimal("68.00"),
            max_video_quality="720p",
            max_concurrent_streams=1,
            allow_downloads=False,
            is_active=True,
            is_popular=False,
        ),
        SubscriptionPlan(
            name="Premium Monthly",
            name_en="Premium Monthly",
            name_zh="高级月度套餐",
            description="Best value for monthly subscribers",
            description_en="Best value for monthly subscribers",
            description_zh="月度订阅最佳选择",
            billing_period=BillingPeriod.MONTHLY,
            price_usd=Decimal("19.99"),
            price_cny=Decimal("138.00"),
            max_video_quality="1080p",
            max_concurrent_streams=2,
            allow_downloads=True,
            is_active=True,
            is_popular=True,  # 最受欢迎
        ),
        SubscriptionPlan(
            name="Ultimate Monthly",
            name_en="Ultimate Monthly",
            name_zh="至尊月度套餐",
            description="Premium experience with 4K support",
            description_en="Premium experience with 4K support",
            description_zh="支持4K的顶级体验",
            billing_period=BillingPeriod.MONTHLY,
            price_usd=Decimal("29.99"),
            price_cny=Decimal("198.00"),
            max_video_quality="4k",
            max_concurrent_streams=4,
            allow_downloads=True,
            is_active=True,
            is_popular=False,
        ),

        # 季度套餐 (优惠 10%)
        SubscriptionPlan(
            name="Premium Quarterly",
            name_en="Premium Quarterly",
            name_zh="高级季度套餐",
            description="Save 10% with quarterly billing",
            description_en="Save 10% with quarterly billing",
            description_zh="季付享9折优惠",
            billing_period=BillingPeriod.QUARTERLY,
            price_usd=Decimal("53.97"),  # $19.99 * 3 * 0.9
            price_cny=Decimal("372.60"),  # ¥138 * 3 * 0.9
            max_video_quality="1080p",
            max_concurrent_streams=2,
            allow_downloads=True,
            is_active=True,
            is_popular=False,
        ),

        # 年度套餐 (优惠 20%)
        SubscriptionPlan(
            name="Premium Yearly",
            name_en="Premium Yearly",
            name_zh="高级年度套餐",
            description="Best deal! Save 20% with yearly billing",
            description_en="Best deal! Save 20% with yearly billing",
            description_zh="最划算！年付享8折优惠",
            billing_period=BillingPeriod.YEARLY,
            price_usd=Decimal("191.90"),  # $19.99 * 12 * 0.8
            price_cny=Decimal("1324.80"),  # ¥138 * 12 * 0.8
            max_video_quality="1080p",
            max_concurrent_streams=2,
            allow_downloads=True,
            is_active=True,
            is_popular=False,
        ),
        SubscriptionPlan(
            name="Ultimate Yearly",
            name_en="Ultimate Yearly",
            name_zh="至尊年度套餐",
            description="Ultimate experience at best price",
            description_en="Ultimate experience at best price",
            description_zh="以最优价格享受至尊体验",
            billing_period=BillingPeriod.YEARLY,
            price_usd=Decimal("287.90"),  # $29.99 * 12 * 0.8
            price_cny=Decimal("1900.80"),  # ¥198 * 12 * 0.8
            max_video_quality="4k",
            max_concurrent_streams=4,
            allow_downloads=True,
            is_active=True,
            is_popular=False,
        ),

        # 终身套餐
        SubscriptionPlan(
            name="Lifetime Premium",
            name_en="Lifetime Premium",
            name_zh="终身高级套餐",
            description="One-time payment, lifetime access",
            description_en="One-time payment, lifetime access",
            description_zh="一次付费，终身使用",
            billing_period=BillingPeriod.LIFETIME,
            price_usd=Decimal("499.99"),
            price_cny=Decimal("3499.00"),
            max_video_quality="1080p",
            max_concurrent_streams=2,
            allow_downloads=True,
            is_active=True,
            is_popular=False,
        ),
    ]

    for plan in plans:
        db.add(plan)

    db.commit()
    print(f"✅ Created {len(plans)} subscription plans")

    return plans


def create_coupons(db):
    """创建测试优惠券"""
    print("Creating coupons...")

    # 获取或创建管理员用户
    admin = db.execute(
        select(AdminUser).where(AdminUser.email == "admin@videosite.com")
    ).scalar_one_or_none()
    if not admin:
        admin = AdminUser(
            email="admin@videosite.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            is_active=True,
            is_superadmin=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("✅ Created admin user (admin@videosite.com / admin123)")

    now = datetime.now()

    coupons = [
        # 新用户优惠券 - 20% 折扣
        Coupon(
            code="WELCOME20",
            description="Welcome discount for new users - 新用户欢迎优惠",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("20.00"),  # 20%
            usage_limit=1000,
            usage_count=0,
            usage_limit_per_user=1,
            valid_from=now,
            valid_until=now + timedelta(days=90),
            status=CouponStatus.ACTIVE,
            created_by=admin.id,
        ),

        # 限时促销 - 减免 $10
        Coupon(
            code="SPRING10",
            description="Spring promotion - $10 off / 春季促销 - 减免$10",
            discount_type=DiscountType.FIXED_AMOUNT,
            discount_value=Decimal("10.00"),  # $10
            usage_limit=500,
            usage_count=0,
            usage_limit_per_user=1,
            valid_from=now,
            valid_until=now + timedelta(days=30),
            minimum_amount=Decimal("50.00"),
            status=CouponStatus.ACTIVE,
            created_by=admin.id,
        ),

        # VIP 专属优惠 - 30% 折扣
        Coupon(
            code="VIP30",
            description="VIP exclusive discount - VIP专属优惠",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("30.00"),  # 30%
            usage_limit=100,
            usage_count=0,
            usage_limit_per_user=1,
            valid_from=now,
            valid_until=now + timedelta(days=180),
            status=CouponStatus.ACTIVE,
            created_by=admin.id,
        ),

        # 测试用优惠券 - 99% 折扣（几乎免费）
        Coupon(
            code="TEST99",
            description="Test coupon for development - 开发测试优惠券",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("99.00"),  # 99%
            usage_limit=10,
            usage_count=0,
            usage_limit_per_user=5,
            valid_from=now,
            valid_until=now + timedelta(days=365),
            status=CouponStatus.ACTIVE,
            created_by=admin.id,
        ),

        # 已过期优惠券（用于测试）
        Coupon(
            code="EXPIRED50",
            description="Expired test coupon - 已过期测试优惠券",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("50.00"),
            usage_limit=100,
            usage_count=0,
            usage_limit_per_user=1,
            valid_from=now - timedelta(days=60),
            valid_until=now - timedelta(days=30),
            status=CouponStatus.EXPIRED,
            created_by=admin.id,
        ),
    ]

    for coupon in coupons:
        db.add(coupon)

    db.commit()
    print(f"✅ Created {len(coupons)} coupons")

    return coupons


def main():
    """执行种子数据创建"""
    print("=" * 60)
    print("Payment System Seed Data Script")
    print("=" * 60)

    db = SessionLocal()

    try:
        # 检查是否已有数据
        existing_plans = db.execute(
            select(func.count()).select_from(SubscriptionPlan)
        ).scalar()
        existing_coupons = db.execute(
            select(func.count()).select_from(Coupon)
        ).scalar()

        if existing_plans > 0 or existing_coupons > 0:
            print(f"\n⚠️  Warning: Database already contains data:")
            print(f"   - {existing_plans} subscription plans")
            print(f"   - {existing_coupons} coupons")

            response = input("\nDo you want to continue and add more data? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                return

        # 创建数据
        print("\n📊 Creating seed data...\n")

        plans = create_subscription_plans(db)
        coupons = create_coupons(db)

        print("\n" + "=" * 60)
        print("✅ Seed data created successfully!")
        print("=" * 60)

        print("\n📦 Summary:")
        print(f"   - Subscription Plans: {len(plans)}")
        print(f"   - Coupons: {len(coupons)}")

        print("\n🔑 Admin Credentials:")
        print("   Email: admin@videosite.com")
        print("   Password: admin123")

        print("\n💳 Available Coupons:")
        for coupon in coupons:
            status_icon = "✓" if coupon.status == CouponStatus.ACTIVE else "✗"
            print(f"   {status_icon} {coupon.code} - {coupon.description}")

        print("\n💎 Subscription Plans:")
        for plan in plans:
            popular = "⭐" if plan.is_popular else "  "
            print(f"   {popular} {plan.name} - ${plan.price_usd} / {plan.billing_period.value}")

        print("\n🚀 Next Steps:")
        print("   1. Start the backend: cd backend && uvicorn app.main:app --reload")
        print("   2. Visit API docs: http://localhost:8000/api/docs")
        print("   3. Test subscription creation with coupons")
        print("   4. Check admin endpoints for management")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
