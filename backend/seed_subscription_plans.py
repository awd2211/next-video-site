"""
Seed default subscription plans
"""
import asyncio
import json
from decimal import Decimal
from sqlalchemy import text
from app.database import async_engine

# 定义默认订阅计划
default_plans = [
    # ==================== 基础版 ====================
    {
        "name": "Basic Monthly",
        "name_en": "Basic Monthly",
        "name_zh": "基础版 - 月付",
        "description": "Perfect for casual viewers who want ad-free experience",
        "description_en": "Perfect for casual viewers who want ad-free experience",
        "description_zh": "适合偶尔观看的用户，享受无广告体验",
        "billing_period": "MONTHLY",
        "price_usd": Decimal("9.99"),
        "price_cny": Decimal("68.00"),
        "price_eur": Decimal("8.99"),
        "trial_days": 7,
        "features": json.dumps([
            "高清1080p视频",
            "无广告观看",
            "单设备播放",
            "基础内容库访问"
        ]),
        "max_video_quality": "1080p",
        "max_concurrent_streams": 1,
        "allow_downloads": False,
        "ad_free": True,
        "is_active": True,
        "is_popular": False,
        "display_order": 1
    },
    {
        "name": "Basic Quarterly",
        "name_en": "Basic Quarterly",
        "name_zh": "基础版 - 季付",
        "description": "Save 15% with quarterly billing",
        "description_en": "Save 15% with quarterly billing",
        "description_zh": "季付享85折优惠",
        "billing_period": "QUARTERLY",
        "price_usd": Decimal("25.47"),  # 9.99 * 3 * 0.85
        "price_cny": Decimal("173.40"),  # 68 * 3 * 0.85
        "price_eur": Decimal("22.93"),
        "trial_days": 7,
        "features": json.dumps([
            "高清1080p视频",
            "无广告观看",
            "单设备播放",
            "基础内容库访问",
            "季付优惠15%"
        ]),
        "max_video_quality": "1080p",
        "max_concurrent_streams": 1,
        "allow_downloads": False,
        "ad_free": True,
        "is_active": True,
        "is_popular": False,
        "display_order": 2
    },
    {
        "name": "Basic Yearly",
        "name_en": "Basic Yearly",
        "name_zh": "基础版 - 年付",
        "description": "Best value - Save 30% with annual billing",
        "description_en": "Best value - Save 30% with annual billing",
        "description_zh": "年付享7折优惠，最划算",
        "billing_period": "YEARLY",
        "price_usd": Decimal("83.92"),  # 9.99 * 12 * 0.7
        "price_cny": Decimal("571.20"),  # 68 * 12 * 0.7
        "price_eur": Decimal("75.52"),
        "trial_days": 14,  # 年付提供更长试用期
        "features": json.dumps([
            "高清1080p视频",
            "无广告观看",
            "单设备播放",
            "基础内容库访问",
            "年付优惠30%",
            "14天免费试用"
        ]),
        "max_video_quality": "1080p",
        "max_concurrent_streams": 1,
        "allow_downloads": False,
        "ad_free": True,
        "is_active": True,
        "is_popular": False,
        "display_order": 3
    },

    # ==================== 标准版 ====================
    {
        "name": "Standard Monthly",
        "name_en": "Standard Monthly",
        "name_zh": "标准版 - 月付",
        "description": "Great for families with 2K streaming and downloads",
        "description_en": "Great for families with 2K streaming and downloads",
        "description_zh": "适合家庭使用，支持2K画质和离线下载",
        "billing_period": "MONTHLY",
        "price_usd": Decimal("14.99"),
        "price_cny": Decimal("98.00"),
        "price_eur": Decimal("13.99"),
        "trial_days": 7,
        "features": json.dumps([
            "2K超清视频",
            "无广告观看",
            "2台设备同时播放",
            "完整内容库访问",
            "离线下载功能",
            "家庭共享"
        ]),
        "max_video_quality": "2k",
        "max_concurrent_streams": 2,
        "allow_downloads": True,
        "ad_free": True,
        "is_active": True,
        "is_popular": True,  # 标准版标记为热门
        "display_order": 4
    },
    {
        "name": "Standard Quarterly",
        "name_en": "Standard Quarterly",
        "name_zh": "标准版 - 季付",
        "description": "Save 15% with quarterly billing",
        "description_en": "Save 15% with quarterly billing",
        "description_zh": "季付享85折优惠",
        "billing_period": "QUARTERLY",
        "price_usd": Decimal("38.22"),  # 14.99 * 3 * 0.85
        "price_cny": Decimal("249.90"),  # 98 * 3 * 0.85
        "price_eur": Decimal("35.67"),
        "trial_days": 7,
        "features": json.dumps([
            "2K超清视频",
            "无广告观看",
            "2台设备同时播放",
            "完整内容库访问",
            "离线下载功能",
            "家庭共享",
            "季付优惠15%"
        ]),
        "max_video_quality": "2k",
        "max_concurrent_streams": 2,
        "allow_downloads": True,
        "ad_free": True,
        "is_active": True,
        "is_popular": False,
        "display_order": 5
    },
    {
        "name": "Standard Yearly",
        "name_en": "Standard Yearly",
        "name_zh": "标准版 - 年付",
        "description": "Best value - Save 30% with annual billing",
        "description_en": "Best value - Save 30% with annual billing",
        "description_zh": "年付享7折优惠，最划算",
        "billing_period": "YEARLY",
        "price_usd": Decimal("125.92"),  # 14.99 * 12 * 0.7
        "price_cny": Decimal("823.20"),  # 98 * 12 * 0.7
        "price_eur": Decimal("117.52"),
        "trial_days": 14,
        "features": json.dumps([
            "2K超清视频",
            "无广告观看",
            "2台设备同时播放",
            "完整内容库访问",
            "离线下载功能",
            "家庭共享",
            "年付优惠30%",
            "14天免费试用"
        ]),
        "max_video_quality": "2k",
        "max_concurrent_streams": 2,
        "allow_downloads": True,
        "ad_free": True,
        "is_active": True,
        "is_popular": True,  # 年付标准版也很热门
        "display_order": 6
    },

    # ==================== 高级版 ====================
    {
        "name": "Premium Monthly",
        "name_en": "Premium Monthly",
        "name_zh": "高级版 - 月付",
        "description": "Ultimate experience with 4K HDR and exclusive content",
        "description_en": "Ultimate experience with 4K HDR and exclusive content",
        "description_zh": "终极体验，支持4K HDR和独家内容",
        "billing_period": "MONTHLY",
        "price_usd": Decimal("19.99"),
        "price_cny": Decimal("128.00"),
        "price_eur": Decimal("17.99"),
        "trial_days": 14,
        "features": json.dumps([
            "4K HDR超清视频",
            "无广告观看",
            "4台设备同时播放",
            "完整内容库+独家内容",
            "无限离线下载",
            "家庭共享",
            "优先客服支持",
            "提前观看新内容"
        ]),
        "max_video_quality": "4k",
        "max_concurrent_streams": 4,
        "allow_downloads": True,
        "ad_free": True,
        "is_active": True,
        "is_popular": False,
        "display_order": 7
    },
    {
        "name": "Premium Quarterly",
        "name_en": "Premium Quarterly",
        "name_zh": "高级版 - 季付",
        "description": "Save 15% with quarterly billing",
        "description_en": "Save 15% with quarterly billing",
        "description_zh": "季付享85折优惠",
        "billing_period": "QUARTERLY",
        "price_usd": Decimal("50.97"),  # 19.99 * 3 * 0.85
        "price_cny": Decimal("326.40"),  # 128 * 3 * 0.85
        "price_eur": Decimal("45.87"),
        "trial_days": 14,
        "features": json.dumps([
            "4K HDR超清视频",
            "无广告观看",
            "4台设备同时播放",
            "完整内容库+独家内容",
            "无限离线下载",
            "家庭共享",
            "优先客服支持",
            "提前观看新内容",
            "季付优惠15%"
        ]),
        "max_video_quality": "4k",
        "max_concurrent_streams": 4,
        "allow_downloads": True,
        "ad_free": True,
        "is_active": True,
        "is_popular": False,
        "display_order": 8
    },
    {
        "name": "Premium Yearly",
        "name_en": "Premium Yearly",
        "name_zh": "高级版 - 年付",
        "description": "Best value - Save 30% with annual billing",
        "description_en": "Best value - Save 30% with annual billing",
        "description_zh": "年付享7折优惠，最划算",
        "billing_period": "YEARLY",
        "price_usd": Decimal("167.92"),  # 19.99 * 12 * 0.7
        "price_cny": Decimal("1075.20"),  # 128 * 12 * 0.7
        "price_eur": Decimal("151.52"),
        "trial_days": 14,
        "features": json.dumps([
            "4K HDR超清视频",
            "无广告观看",
            "4台设备同时播放",
            "完整内容库+独家内容",
            "无限离线下载",
            "家庭共享",
            "优先客服支持",
            "提前观看新内容",
            "年付优惠30%",
            "14天免费试用"
        ]),
        "max_video_quality": "4k",
        "max_concurrent_streams": 4,
        "allow_downloads": True,
        "ad_free": True,
        "is_active": True,
        "is_popular": False,
        "display_order": 9
    },

    # ==================== 终身会员 ====================
    {
        "name": "Premium Lifetime",
        "name_en": "Premium Lifetime",
        "name_zh": "高级版 - 终身会员",
        "description": "One-time payment for lifetime premium access",
        "description_en": "One-time payment for lifetime premium access",
        "description_zh": "一次付费，终身尊享高级会员所有权益",
        "billing_period": "LIFETIME",
        "price_usd": Decimal("599.99"),
        "price_cny": Decimal("3999.00"),
        "price_eur": Decimal("549.99"),
        "trial_days": 30,  # 终身会员提供最长试用期
        "features": json.dumps([
            "4K HDR超清视频",
            "无广告观看",
            "4台设备同时播放",
            "完整内容库+独家内容",
            "无限离线下载",
            "家庭共享",
            "VIP专属客服",
            "提前观看新内容",
            "终身免费更新",
            "所有未来新功能",
            "30天无理由退款",
            "专属身份标识"
        ]),
        "max_video_quality": "4k",
        "max_concurrent_streams": 4,
        "allow_downloads": True,
        "ad_free": True,
        "is_active": True,
        "is_popular": False,
        "display_order": 10
    },

    # ==================== 学生优惠版 ====================
    {
        "name": "Student Monthly",
        "name_en": "Student Monthly",
        "name_zh": "学生版 - 月付",
        "description": "Special discount for students with valid student ID",
        "description_en": "Special discount for students with valid student ID",
        "description_zh": "学生专享优惠，需验证学生身份",
        "billing_period": "MONTHLY",
        "price_usd": Decimal("6.99"),
        "price_cny": Decimal("48.00"),
        "price_eur": Decimal("5.99"),
        "trial_days": 7,
        "features": json.dumps([
            "2K超清视频",
            "无广告观看",
            "单设备播放",
            "完整内容库访问",
            "离线下载功能",
            "学生专属优惠",
            "需验证学生身份"
        ]),
        "max_video_quality": "2k",
        "max_concurrent_streams": 1,
        "allow_downloads": True,
        "ad_free": True,
        "is_active": True,
        "is_popular": False,
        "display_order": 11
    },

    # ==================== 家庭共享版 ====================
    {
        "name": "Family Yearly",
        "name_en": "Family Yearly",
        "name_zh": "家庭共享版 - 年付",
        "description": "Perfect for families - Up to 6 accounts with 4K streaming",
        "description_en": "Perfect for families - Up to 6 accounts with 4K streaming",
        "description_zh": "最适合家庭 - 最多6个账户共享，支持4K",
        "billing_period": "YEARLY",
        "price_usd": Decimal("249.99"),
        "price_cny": Decimal("1680.00"),
        "price_eur": Decimal("229.99"),
        "trial_days": 14,
        "features": json.dumps([
            "4K HDR超清视频",
            "无广告观看",
            "6台设备同时播放",
            "最多6个独立账户",
            "完整内容库+独家内容",
            "无限离线下载",
            "家长控制功能",
            "儿童专区",
            "优先客服支持"
        ]),
        "max_video_quality": "4k",
        "max_concurrent_streams": 6,
        "allow_downloads": True,
        "ad_free": True,
        "is_active": True,
        "is_popular": True,  # 家庭版很热门
        "display_order": 12
    }
]


async def seed_subscription_plans():
    """Insert default subscription plans"""
    async with async_engine.begin() as conn:
        # Check if plans already exist
        result = await conn.execute(
            text("SELECT COUNT(*) FROM subscription_plans")
        )
        count = result.scalar()

        if count > 0:
            print(f"⚠️  Database already has {count} subscription plans.")
            print("🔄 Clearing and re-seeding with new data...")

            # Clear existing plans
            await conn.execute(text("DELETE FROM subscription_plans"))
            print("✓ Cleared existing plans")

        # Insert plans
        for plan in default_plans:
            insert_query = text("""
                INSERT INTO subscription_plans
                (name, name_en, name_zh, description, description_en, description_zh,
                 billing_period, price_usd, price_cny, price_eur, trial_days,
                 features, max_video_quality, max_concurrent_streams,
                 allow_downloads, ad_free, is_active, is_popular, display_order)
                VALUES
                (:name, :name_en, :name_zh, :description, :description_en, :description_zh,
                 :billing_period, :price_usd, :price_cny, :price_eur, :trial_days,
                 :features, :max_video_quality, :max_concurrent_streams,
                 :allow_downloads, :ad_free, :is_active, :is_popular, :display_order)
            """)

            await conn.execute(insert_query, plan)
            print(f"✓ Created plan: {plan['name_zh']} (${plan['price_usd']}/{plan['billing_period']})")

        print(f"\n🎉 Successfully seeded {len(default_plans)} subscription plans!")

        # Show summary
        print("\n" + "="*60)
        print("订阅计划汇总:")
        print("="*60)

        # Group by tier
        tiers = {
            "基础版": [p for p in default_plans if "Basic" in p["name"]],
            "标准版": [p for p in default_plans if "Standard" in p["name"]],
            "高级版": [p for p in default_plans if "Premium" in p["name"] and "Lifetime" not in p["name"]],
            "特殊版本": [p for p in default_plans if "Student" in p["name"] or "Family" in p["name"] or "Lifetime" in p["name"]]
        }

        for tier_name, tier_plans in tiers.items():
            if tier_plans:
                print(f"\n【{tier_name}】")
                for p in tier_plans:
                    period_zh = {
                        "MONTHLY": "月付",
                        "QUARTERLY": "季付",
                        "YEARLY": "年付",
                        "LIFETIME": "终身"
                    }.get(p["billing_period"], p["billing_period"])
                    print(f"  • {p['name_zh']:20s} - ¥{p['price_cny']:>7} ({period_zh})")


if __name__ == "__main__":
    asyncio.run(seed_subscription_plans())
