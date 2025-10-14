"""
美剧系列种子数据脚本
添加热门美剧系列数据
"""
import asyncio
from sqlalchemy import select
from app.database import async_session_maker
from app.models.series import Series, SeriesType, SeriesStatus
from app.models.user import AdminUser
from loguru import logger


# 定义热门美剧系列数据
TV_SERIES_DATA = [
    {
        "title": "权力的游戏 (Game of Thrones)",
        "description": "史诗级奇幻剧集，改编自乔治·R·R·马丁的《冰与火之歌》系列小说。讲述了七大王国争夺铁王座的权力游戏，以及北境守夜人对抗异鬼威胁的故事。",
        "type": SeriesType.SERIES,
        "status": SeriesStatus.PUBLISHED,
        "total_episodes": 73,
        "is_featured": True,
        "display_order": 1,
    },
    {
        "title": "绝命毒师 (Breaking Bad)",
        "description": "一位高中化学老师沃尔特·怀特在得知自己身患癌症后，为了给家人留下足够的财产，开始制造和贩卖冰毒的犯罪故事。这部剧被誉为史上最伟大的电视剧之一。",
        "type": SeriesType.SERIES,
        "status": SeriesStatus.PUBLISHED,
        "total_episodes": 62,
        "is_featured": True,
        "display_order": 2,
    },
    {
        "title": "老友记 (Friends)",
        "description": "经典情景喜剧，讲述了六个生活在纽约曼哈顿的好友之间的友情、爱情和生活琐事。这部剧陪伴了一代人的成长，至今依然深受全球观众喜爱。",
        "type": SeriesType.SERIES,
        "status": SeriesStatus.PUBLISHED,
        "total_episodes": 236,
        "is_featured": True,
        "display_order": 3,
    },
    {
        "title": "怪奇物语 (Stranger Things)",
        "description": "80年代背景的科幻恐怖剧，讲述了一个小镇上的孩子们在寻找失踪朋友的过程中，发现了神秘的政府实验和超自然力量。充满怀旧元素和惊悚氛围。",
        "type": SeriesType.SERIES,
        "status": SeriesStatus.PUBLISHED,
        "total_episodes": 42,
        "is_featured": True,
        "display_order": 4,
    },
    {
        "title": "黑镜 (Black Mirror)",
        "description": "独立单元剧集，每集探讨科技对人类社会的影响。通过讽刺和警示的手法，展现了科技发展可能带来的黑暗未来。",
        "type": SeriesType.COLLECTION,
        "status": SeriesStatus.PUBLISHED,
        "total_episodes": 27,
        "is_featured": True,
        "display_order": 5,
    },
    {
        "title": "纸牌屋 (House of Cards)",
        "description": "政治惊悚剧，讲述了野心勃勃的国会议员弗兰克·安德伍德通过操纵和背叛一步步登上权力巅峰的故事。凯文·史派西的精彩表演令人印象深刻。",
        "type": SeriesType.SERIES,
        "status": SeriesStatus.PUBLISHED,
        "total_episodes": 73,
        "is_featured": True,
        "display_order": 6,
    },
    {
        "title": "西部世界 (Westworld)",
        "description": "科幻剧集，设定在一个由人工智能控制的西部主题乐园。当机器人开始觉醒自我意识后，引发了关于意识、自由意志和人性的深刻思考。",
        "type": SeriesType.SERIES,
        "status": SeriesStatus.PUBLISHED,
        "total_episodes": 36,
        "is_featured": True,
        "display_order": 7,
    },
    {
        "title": "行尸走肉 (The Walking Dead)",
        "description": "末日生存剧，讲述了在僵尸末日世界中，幸存者们为了生存而挣扎的故事。探讨了人性、道德和文明在极端环境下的崩塌与重建。",
        "type": SeriesType.SERIES,
        "status": SeriesStatus.PUBLISHED,
        "total_episodes": 177,
        "is_featured": True,
        "display_order": 8,
    },
    {
        "title": "风骚律师 (Better Call Saul)",
        "description": "《绝命毒师》的前传，讲述了律师索尔·古德曼（吉米·麦吉尔）从一个努力奋斗的小律师逐渐蜕变为犯罪律师的故事。",
        "type": SeriesType.SERIES,
        "status": SeriesStatus.PUBLISHED,
        "total_episodes": 63,
        "is_featured": True,
        "display_order": 9,
    },
    {
        "title": "王冠 (The Crown)",
        "description": "历史传记剧，讲述了英国女王伊丽莎白二世的一生，从她1952年登基到现代的历史事件。展现了王室生活、政治斗争和个人情感的交织。",
        "type": SeriesType.SERIES,
        "status": SeriesStatus.PUBLISHED,
        "total_episodes": 60,
        "is_featured": True,
        "display_order": 10,
    },
    {
        "title": "使女的故事 (The Handmaid's Tale)",
        "description": "反乌托邦剧集，设定在一个极权主义社会，女性被剥夺权利并被迫成为生育工具。探讨了权力、压迫和反抗的主题。",
        "type": SeriesType.SERIES,
        "status": SeriesStatus.PUBLISHED,
        "total_episodes": 56,
        "is_featured": False,
        "display_order": 11,
    },
    {
        "title": "曼达洛人 (The Mandalorian)",
        "description": "《星球大战》系列的衍生剧，讲述了一个孤独的赏金猎人在银河系边缘游荡，保护一个神秘幼童的故事。以其精彩的特效和动作场面著称。",
        "type": SeriesType.SERIES,
        "status": SeriesStatus.PUBLISHED,
        "total_episodes": 24,
        "is_featured": True,
        "display_order": 12,
    },
    {
        "title": "亢奋 (Euphoria)",
        "description": "青春剧集，以大胆的视觉风格和真实的情感描绘，讲述了一群高中生面对毒品、性、身份认同和社交媒体等问题的故事。",
        "type": SeriesType.SERIES,
        "status": SeriesStatus.PUBLISHED,
        "total_episodes": 19,
        "is_featured": False,
        "display_order": 13,
    },
    {
        "title": "继承之战 (Succession)",
        "description": "家族企业剧，讲述了媒体巨头罗伊家族的继承之战。充满了权力斗争、背叛和讽刺，展现了超级富豪家族的内部纷争。",
        "type": SeriesType.SERIES,
        "status": SeriesStatus.PUBLISHED,
        "total_episodes": 39,
        "is_featured": True,
        "display_order": 14,
    },
    {
        "title": "黑吃黑 (Banshee)",
        "description": "犯罪动作剧，讲述了一个刚出狱的前罪犯假冒小镇警长身份，一边维护法律一边继续犯罪的故事。以其暴力场面和曲折剧情著称。",
        "type": SeriesType.SERIES,
        "status": SeriesStatus.PUBLISHED,
        "total_episodes": 38,
        "is_featured": False,
        "display_order": 15,
    },
    {
        "title": "良医 (The Good Doctor)",
        "description": "医疗剧，讲述了一位患有自闭症谱系障碍和学者症候群的年轻外科医生肖恩·墨菲，凭借其卓越的医术和独特的视角拯救生命的故事。",
        "type": SeriesType.SERIES,
        "status": SeriesStatus.PUBLISHED,
        "total_episodes": 126,
        "is_featured": False,
        "display_order": 16,
    },
    {
        "title": "亿万 (Billions)",
        "description": "金融剧集，讲述了纽约检察官与对冲基金大亨之间的猫鼠游戏。探讨了财富、权力和道德的界限。",
        "type": SeriesType.SERIES,
        "status": SeriesStatus.PUBLISHED,
        "total_episodes": 84,
        "is_featured": False,
        "display_order": 17,
    },
    {
        "title": "猎魔人 (The Witcher)",
        "description": "奇幻冒险剧，改编自波兰作家安杰伊·萨普科夫斯基的同名小说系列。讲述了猎魔人杰洛特在充满魔法和怪物的世界中寻找命运的故事。",
        "type": SeriesType.SERIES,
        "status": SeriesStatus.PUBLISHED,
        "total_episodes": 24,
        "is_featured": True,
        "display_order": 18,
    },
    {
        "title": "鱿鱼游戏 (Squid Game)",
        "description": "韩国生存剧集，讲述了456名负债累累的人参加一场神秘的生存游戏，争夺巨额奖金的故事。以其残酷的游戏规则和深刻的社会批判引发全球轰动。",
        "type": SeriesType.SERIES,
        "status": SeriesStatus.PUBLISHED,
        "total_episodes": 9,
        "is_featured": True,
        "display_order": 19,
    },
    {
        "title": "王者天下 (Vikings)",
        "description": "历史剧集，讲述了传奇维京勇士拉格纳·洛斯布鲁克的崛起和冒险，以及维京人对英格兰和其他地区的入侵征服。",
        "type": SeriesType.SERIES,
        "status": SeriesStatus.PUBLISHED,
        "total_episodes": 89,
        "is_featured": False,
        "display_order": 20,
    },
]


async def seed_series(session):
    """创建美剧系列数据"""
    logger.info("开始添加美剧系列数据...")

    # 获取一个管理员账号作为创建者
    admin_result = await session.execute(select(AdminUser).where(AdminUser.is_superadmin == True).limit(1))
    admin = admin_result.scalar_one_or_none()

    if not admin:
        logger.warning("未找到超级管理员账号，将不设置创建者")
        admin_id = None
    else:
        admin_id = admin.id
        logger.info(f"使用管理员 {admin.username} 作为创建者")

    created_count = 0
    existing_count = 0
    updated_count = 0

    for series_data in TV_SERIES_DATA:
        # 检查系列是否已存在
        result = await session.execute(
            select(Series).where(Series.title == series_data["title"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            # 更新现有系列
            existing.description = series_data["description"]
            existing.type = series_data["type"]
            existing.status = series_data["status"]
            existing.total_episodes = series_data["total_episodes"]
            existing.is_featured = series_data["is_featured"]
            existing.display_order = series_data["display_order"]
            updated_count += 1
            logger.info(f"更新系列: {series_data['title']}")
        else:
            # 创建新系列
            series = Series(
                **series_data,
                created_by=admin_id
            )
            session.add(series)
            created_count += 1
            logger.info(f"创建系列: {series_data['title']} ({series_data['total_episodes']} 集)")

    await session.commit()
    logger.success(f"美剧系列数据添加完成！新增: {created_count}, 更新: {updated_count}, 已存在: {existing_count}")


async def main():
    """主函数"""
    logger.info("="*60)
    logger.info("开始初始化美剧系列数据")
    logger.info("="*60)

    async with async_session_maker() as session:
        try:
            # 创建系列数据
            await seed_series(session)

            logger.info("="*60)
            logger.success("美剧系列数据初始化完成！")
            logger.info("="*60)

            # 显示统计信息
            result = await session.execute(select(Series))
            series_count = len(result.scalars().all())

            result = await session.execute(select(Series).where(Series.is_featured == True))
            featured_count = len(result.scalars().all())

            logger.info(f"当前系统中共有 {series_count} 个系列")
            logger.info(f"其中推荐系列: {featured_count} 个")

        except Exception as e:
            logger.error(f"初始化失败: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
