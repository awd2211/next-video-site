"""
测试交互相关模型
包括: Comment, Favorite, WatchHistory, Rating, Danmaku, Series, Watchlist, Share
"""
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.comment import Comment
from app.models.danmaku import Danmaku
from app.models.series import Series
from app.models.watchlist import Watchlist
from app.database import AsyncSessionLocal


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestCommentModel:
    """Comment 模型测试"""

    async def test_create_comment(self, test_user, test_video):
        """测试创建评论"""
        async with AsyncSessionLocal() as db:
            comment = Comment(
                video_id=test_video.id,
                user_id=test_user.id,
                content="测试评论内容"
            )
            db.add(comment)
            await db.commit()
            await db.refresh(comment)
            
            assert comment.id is not None
            assert comment.content == "测试评论内容"
            assert comment.like_count == 0
            
            await db.delete(comment)
            await db.commit()

    async def test_comment_reply(self, test_user, test_video):
        """测试评论回复"""
        async with AsyncSessionLocal() as db:
            # 创建父评论
            parent_comment = Comment(
                video_id=test_video.id,
                user_id=test_user.id,
                content="父评论"
            )
            db.add(parent_comment)
            await db.commit()
            await db.refresh(parent_comment)
            
            # 创建回复
            reply = Comment(
                video_id=test_video.id,
                user_id=test_user.id,
                content="回复评论",
                parent_id=parent_comment.id
            )
            db.add(reply)
            await db.commit()
            await db.refresh(reply)
            
            assert reply.parent_id == parent_comment.id
            
            await db.delete(reply)
            await db.delete(parent_comment)
            await db.commit()


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestDanmakuModel:
    """Danmaku 弹幕模型测试"""

    async def test_create_danmaku(self, test_user, test_video):
        """测试创建弹幕"""
        async with AsyncSessionLocal() as db:
            danmaku = Danmaku(
                video_id=test_video.id,
                user_id=test_user.id,
                content="测试弹幕",
                time=60,  # 60秒处
                type="scroll",
                color="#FFFFFF"
            )
            db.add(danmaku)
            await db.commit()
            await db.refresh(danmaku)
            
            assert danmaku.id is not None
            assert danmaku.content == "测试弹幕"
            assert danmaku.time == 60
            
            await db.delete(danmaku)
            await db.commit()


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestSeriesModel:
    """Series 系列模型测试"""

    async def test_create_series(self):
        """测试创建系列"""
        async with AsyncSessionLocal() as db:
            series = Series(
                title="测试系列",
                type="series",
                status="published"
            )
            db.add(series)
            await db.commit()
            await db.refresh(series)
            
            assert series.id is not None
            assert series.title == "测试系列"
            assert series.total_episodes == 0
            
            await db.delete(series)
            await db.commit()


@pytest.mark.model
@pytest.mark.requires_db
@pytest.mark.asyncio
class TestWatchlistModel:
    """Watchlist 观看列表模型测试"""

    async def test_create_watchlist_item(self, test_user, test_video):
        """测试创建观看列表项"""
        async with AsyncSessionLocal() as db:
            watchlist_item = Watchlist(
                user_id=test_user.id,
                video_id=test_video.id,
                position=0
            )
            db.add(watchlist_item)
            await db.commit()
            await db.refresh(watchlist_item)
            
            assert watchlist_item.id is not None
            assert watchlist_item.user_id == test_user.id
            assert watchlist_item.video_id == test_video.id
            
            await db.delete(watchlist_item)
            await db.commit()

    async def test_watchlist_unique_constraint(self, test_user, test_video):
        """测试同一用户不能重复添加同一视频"""
        async with AsyncSessionLocal() as db:
            item1 = Watchlist(
                user_id=test_user.id,
                video_id=test_video.id,
                position=0
            )
            db.add(item1)
            await db.commit()
            
            item2 = Watchlist(
                user_id=test_user.id,
                video_id=test_video.id,
                position=1
            )
            db.add(item2)
            
            with pytest.raises(IntegrityError):
                await db.commit()
            
            await db.rollback()
            await db.delete(item1)
            await db.commit()

