#!/usr/bin/env python3
"""
横幅数据管理脚本 - 支持添加、清空、列表查看等操作

使用示例:
    python scripts/seed_banners.py add       # 添加示例横幅
    python scripts/seed_banners.py clear     # 清空所有横幅
    python scripts/seed_banners.py list      # 列出所有横幅
    python scripts/seed_banners.py add --force  # 强制添加(先清空再添加)
"""
import argparse
import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

from loguru import logger
from sqlalchemy import delete, func, select

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.models.content import Banner, BannerStatus


class BannerSeeder:
    """横幅数据播种器"""

    # 示例横幅数据配置
    SAMPLE_BANNERS = [
        {
            'title': '精彩电影推荐 - 星际穿越',
            'image_url': 'https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=1920&h=600&fit=crop',
            'link_url': '/videos/1',
            'video_id': None,
            'description': '探索宇宙的壮丽史诗,体验时间与空间的奇妙旅程',
            'status': BannerStatus.ACTIVE,
            'sort_order': 100,
        },
        {
            'title': '热门剧集 - 权力的游戏',
            'image_url': 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1920&h=600&fit=crop',
            'link_url': '/videos/2',
            'video_id': None,
            'description': '七大王国的权力争夺,谁能坐上铁王座?',
            'status': BannerStatus.ACTIVE,
            'sort_order': 90,
        },
        {
            'title': '动画精选 - 千与千寻',
            'image_url': 'https://images.unsplash.com/photo-1518676590629-3dcbd9c5a5c9?w=1920&h=600&fit=crop',
            'link_url': '/videos/3',
            'video_id': None,
            'description': '宫崎骏经典动画,奇幻世界的冒险之旅',
            'status': BannerStatus.ACTIVE,
            'sort_order': 80,
        },
        {
            'title': '纪录片 - 地球脉动',
            'image_url': 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1920&h=600&fit=crop',
            'link_url': '/videos/4',
            'video_id': None,
            'description': 'BBC经典纪录片,见证自然界的壮美奇观',
            'status': BannerStatus.ACTIVE,
            'sort_order': 70,
        },
        {
            'title': '新片上线 - 速度与激情',
            'image_url': 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1920&h=600&fit=crop',
            'link_url': '/videos/5',
            'video_id': None,
            'description': '极速狂飙,热血沸腾的动作盛宴',
            'status': BannerStatus.ACTIVE,
            'sort_order': 60,
        },
        {
            'title': '经典回顾 - 肖申克的救赎',
            'image_url': 'https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=1920&h=600&fit=crop',
            'link_url': '/videos/6',
            'video_id': None,
            'description': '希望是美好的东西,也许是最好的',
            'status': BannerStatus.ACTIVE,
            'sort_order': 50,
        },
        {
            'title': '悬疑惊悚 - 致命魔术',
            'image_url': 'https://images.unsplash.com/photo-1485846234645-a62644f84728?w=1920&h=600&fit=crop',
            'link_url': '/videos/7',
            'video_id': None,
            'description': '魔术师的较量,真相与幻象的交织',
            'status': BannerStatus.ACTIVE,
            'sort_order': 40,
        },
        {
            'title': '科幻巨制 - 黑客帝国',
            'image_url': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1920&h=600&fit=crop',
            'link_url': '/videos/8',
            'video_id': None,
            'description': '虚拟与现实的边界,你选择红色还是蓝色药丸?',
            'status': BannerStatus.ACTIVE,
            'sort_order': 30,
        },
    ]

    def __init__(self):
        self.db_session = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.db_session = AsyncSessionLocal()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.db_session:
            await self.db_session.close()

    async def count_banners(self) -> int:
        """统计横幅数量"""
        result = await self.db_session.execute(select(func.count(Banner.id)))
        return result.scalar() or 0

    async def list_banners(self, limit: Optional[int] = None) -> List[Banner]:
        """列出所有横幅"""
        query = select(Banner).order_by(Banner.sort_order.desc(), Banner.created_at.desc())
        if limit:
            query = query.limit(limit)
        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def add_banners(self, banners_data: List[dict], skip_duplicates: bool = True) -> int:
        """
        添加横幅数据

        Args:
            banners_data: 横幅数据列表
            skip_duplicates: 是否跳过重复的标题

        Returns:
            成功添加的数量
        """
        added_count = 0
        skipped_count = 0

        for banner_data in banners_data:
            # 检查是否存在相同标题的横幅
            if skip_duplicates:
                result = await self.db_session.execute(
                    select(Banner).where(Banner.title == banner_data['title'])
                )
                existing = result.scalar_one_or_none()
                if existing:
                    logger.info(f"跳过重复横幅: {banner_data['title']}")
                    skipped_count += 1
                    continue

            # 创建横幅
            banner = Banner(**banner_data)
            self.db_session.add(banner)
            added_count += 1
            logger.debug(f"添加横幅: {banner_data['title']}")

        await self.db_session.commit()
        logger.info(f"成功添加 {added_count} 个横幅, 跳过 {skipped_count} 个重复项")
        return added_count

    async def clear_all_banners(self, confirm: bool = False) -> int:
        """
        清空所有横幅

        Args:
            confirm: 是否确认删除

        Returns:
            删除的数量
        """
        if not confirm:
            logger.warning("需要确认才能删除所有横幅")
            return 0

        count = await self.count_banners()
        await self.db_session.execute(delete(Banner))
        await self.db_session.commit()
        logger.info(f"已删除 {count} 个横幅")
        return count

    async def add_sample_banners(self, force: bool = False) -> int:
        """
        添加示例横幅

        Args:
            force: 是否强制添加(先清空所有横幅)

        Returns:
            添加的数量
        """
        if force:
            logger.info("强制模式: 先清空现有横幅...")
            await self.clear_all_banners(confirm=True)

        return await self.add_banners(self.SAMPLE_BANNERS, skip_duplicates=not force)

    async def add_timed_banner(
        self,
        title: str,
        image_url: str,
        link_url: str,
        description: str,
        days: int = 7,
        sort_order: int = 100,
    ) -> Banner:
        """
        添加限时横幅

        Args:
            title: 标题
            image_url: 图片URL
            link_url: 链接URL
            description: 描述
            days: 有效天数
            sort_order: 排序

        Returns:
            创建的横幅对象
        """
        now = datetime.now(timezone.utc)
        end_date = now + timedelta(days=days)

        banner = Banner(
            title=title,
            image_url=image_url,
            link_url=link_url,
            description=description,
            status=BannerStatus.ACTIVE,
            sort_order=sort_order,
            start_date=now,
            end_date=end_date,
        )

        self.db_session.add(banner)
        await self.db_session.commit()
        await self.db_session.refresh(banner)

        logger.info(f"添加限时横幅: {title} (有效期: {days} 天)")
        return banner


async def cmd_add(args):
    """添加示例横幅命令"""
    async with BannerSeeder() as seeder:
        count = await seeder.add_sample_banners(force=args.force)
        print(f"\n✅ 成功添加 {count} 个横幅")

        total = await seeder.count_banners()
        print(f"📊 数据库中现有横幅总数: {total}\n")


async def cmd_clear(args):
    """清空所有横幅命令"""
    async with BannerSeeder() as seeder:
        total = await seeder.count_banners()

        if total == 0:
            print("\n⚠️  数据库中没有横幅\n")
            return

        # 确认删除
        if not args.yes:
            print(f"\n⚠️  警告: 即将删除 {total} 个横幅")
            response = input("确认删除? [y/N]: ")
            if response.lower() != 'y':
                print("❌ 已取消\n")
                return

        count = await seeder.clear_all_banners(confirm=True)
        print(f"\n✅ 已删除 {count} 个横幅\n")


async def cmd_list(args):
    """列出所有横幅命令"""
    async with BannerSeeder() as seeder:
        banners = await seeder.list_banners(limit=args.limit)

        if not banners:
            print("\n⚠️  数据库中没有横幅\n")
            return

        print(f"\n📋 横幅列表 (共 {len(banners)} 个):\n")
        print(f"{'ID':<5} {'标题':<30} {'状态':<10} {'排序':<6} {'创建时间':<20}")
        print("-" * 80)

        for banner in banners:
            status_emoji = "🟢" if banner.status == BannerStatus.ACTIVE else "🔴"
            created_at = banner.created_at.strftime("%Y-%m-%d %H:%M")
            print(
                f"{banner.id:<5} {banner.title[:28]:<30} {status_emoji} {banner.status.value:<8} "
                f"{banner.sort_order:<6} {created_at:<20}"
            )

        print()


async def cmd_add_timed(args):
    """添加限时横幅命令"""
    async with BannerSeeder() as seeder:
        banner = await seeder.add_timed_banner(
            title=args.title,
            image_url=args.image_url,
            link_url=args.link_url,
            description=args.description or args.title,
            days=args.days,
            sort_order=args.sort_order,
        )
        print(f"\n✅ 添加限时横幅: {banner.title}")
        print(f"📅 有效期至: {banner.end_date.strftime('%Y-%m-%d %H:%M')}\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='横幅数据管理工具')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # add 命令
    parser_add = subparsers.add_parser('add', help='添加示例横幅')
    parser_add.add_argument('--force', action='store_true', help='强制添加(先清空所有横幅)')

    # clear 命令
    parser_clear = subparsers.add_parser('clear', help='清空所有横幅')
    parser_clear.add_argument('-y', '--yes', action='store_true', help='跳过确认提示')

    # list 命令
    parser_list = subparsers.add_parser('list', help='列出所有横幅')
    parser_list.add_argument('-n', '--limit', type=int, help='限制显示数量')

    # add-timed 命令
    parser_timed = subparsers.add_parser('add-timed', help='添加限时横幅')
    parser_timed.add_argument('title', help='横幅标题')
    parser_timed.add_argument('image_url', help='图片URL')
    parser_timed.add_argument('link_url', help='链接URL')
    parser_timed.add_argument('-d', '--description', help='描述')
    parser_timed.add_argument('--days', type=int, default=7, help='有效天数(默认7天)')
    parser_timed.add_argument('--sort-order', type=int, default=100, help='排序优先级(默认100)')

    args = parser.parse_args()

    # 配置日志
    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    # 执行命令
    if args.command == 'add':
        asyncio.run(cmd_add(args))
    elif args.command == 'clear':
        asyncio.run(cmd_clear(args))
    elif args.command == 'list':
        asyncio.run(cmd_list(args))
    elif args.command == 'add-timed':
        asyncio.run(cmd_add_timed(args))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
