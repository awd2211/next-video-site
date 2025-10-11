"""
智能推荐引擎

支持多种推荐策略：
1. 基于内容的推荐（Content-Based）- 基于视频属性相似度
2. 基于用户行为的推荐 - 基于观看历史、收藏、评分
3. 混合推荐 - 结合多种策略

"""

from collections import defaultdict
from typing import List, Optional

from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user_activity import Favorite, WatchHistory
from app.models.video import Video, VideoStatus
from app.utils.cache import Cache


class RecommendationEngine:
    """推荐引擎核心类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_personalized_recommendations(
        self,
        user_id: Optional[int],
        limit: int = 20,
        exclude_video_ids: Optional[List[int]] = None,
    ) -> List[Video]:
        """
        获取个性化推荐

        策略：
        - 如果用户已登录：60% 协同过滤 + 40% 内容推荐
        - 如果用户未登录：100% 热门推荐
        """
        exclude_ids = exclude_video_ids or []

        if user_id:
            # 已登录用户：个性化推荐
            cache_key = f"personalized_recommendations:user_{user_id}:limit_{limit}"
            cached = await Cache.get(cache_key)
            if cached:
                # 检查缓存数据类型,确保是Video对象而非字典
                if len(cached) > 0 and isinstance(cached[0], Video):
                    return cached
                # 如果缓存数据类型不对或为空,清空缓存重新查询
                cached = None

            # 获取协同过滤推荐（基于相似用户）
            collaborative_videos = (
                await self._get_collaborative_filtering_recommendations(
                    user_id, limit=int(limit * 0.6), exclude_ids=exclude_ids
                )
            )
            collaborative_ids = [v.id for v in collaborative_videos]

            # 获取内容推荐（基于用户历史）
            content_videos = await self._get_content_based_recommendations(
                user_id,
                limit=int(limit * 0.4),
                exclude_ids=exclude_ids + collaborative_ids,
            )

            # 合并结果
            recommended_videos = collaborative_videos + content_videos

            # 如果推荐不足，用热门视频补充
            if len(recommended_videos) < limit:
                popular_videos = await self._get_popular_videos(
                    limit=limit - len(recommended_videos),
                    exclude_ids=exclude_ids + [v.id for v in recommended_videos],
                )
                recommended_videos.extend(popular_videos)

            # 缓存10分钟
            await Cache.set(cache_key, recommended_videos[:limit], ttl=600)
            return recommended_videos[:limit]

        else:
            # 未登录用户：热门推荐
            return await self._get_popular_videos(limit=limit, exclude_ids=exclude_ids)

    async def get_similar_videos(
        self,
        video_id: int,
        limit: int = 10,
        exclude_video_ids: Optional[List[int]] = None,
    ) -> List[Video]:
        """
        获取相似视频推荐

        基于：
        - 相同分类
        - 相同演员/导演
        - 相同国家
        - 相似评分
        """
        cache_key = f"similar_videos:video_{video_id}:limit_{limit}"
        cached = await Cache.get(cache_key)
        if cached:
            # 检查缓存数据类型,确保是Video对象而非字典
            if len(cached) > 0 and isinstance(cached[0], Video):
                return cached
            # 如果缓存数据类型不对或为空,清空缓存重新查询
            cached = None

        exclude_ids = exclude_video_ids or []
        exclude_ids.append(video_id)

        # 获取目标视频信息
        result = await self.db.execute(
            select(Video)
            .options(
                selectinload(Video.video_categories),
                selectinload(Video.video_actors),
                selectinload(Video.video_directors),
            )
            .filter(Video.id == video_id)
        )
        target_video = result.scalar_one_or_none()

        if not target_video:
            return []

        # 提取目标视频的特征
        category_ids = [vc.category_id for vc in target_video.video_categories]
        actor_ids = [va.actor_id for va in target_video.video_actors]
        director_ids = [vd.director_id for vd in target_video.video_directors]

        # 构建相似度评分查询
        # 这里使用简单的特征匹配评分
        candidates_query = (
            select(Video)
            .options(
                selectinload(Video.country),
                selectinload(Video.video_categories),
                selectinload(Video.video_actors),
                selectinload(Video.video_directors),
            )
            .filter(Video.status == VideoStatus.PUBLISHED, Video.id.not_in(exclude_ids))
        )

        # 至少匹配一个分类或演员或导演
        if category_ids or actor_ids or director_ids:
            filters = []
            if category_ids:
                filters.append(Video.video_categories.any(category_id__in=category_ids))
            if actor_ids:
                filters.append(Video.video_actors.any(actor_id__in=actor_ids))
            if director_ids:
                filters.append(Video.video_directors.any(director_id__in=director_ids))

            candidates_query = candidates_query.filter(or_(*filters))

        # 优先显示相同国家的视频
        if target_video.country_id:
            candidates_query = candidates_query.order_by(
                (Video.country_id == target_video.country_id).desc()
            )

        # 按观看次数排序
        candidates_query = candidates_query.order_by(desc(Video.view_count)).limit(
            limit * 2
        )

        result = await self.db.execute(candidates_query)
        candidates = result.scalars().all()

        # 计算相似度并排序
        scored_videos = []
        for candidate in candidates:
            score = self._calculate_similarity_score(target_video, candidate)
            scored_videos.append((candidate, score))

        # 按相似度排序
        scored_videos.sort(key=lambda x: x[1], reverse=True)
        similar_videos = [v for v, _ in scored_videos[:limit]]

        # 缓存30分钟
        await Cache.set(cache_key, similar_videos, ttl=1800)
        return similar_videos

    async def _get_collaborative_filtering_recommendations(
        self, user_id: int, limit: int, exclude_ids: List[int]
    ) -> List[Video]:
        """
        协同过滤推荐

        步骤：
        1. 找到相似用户（有相似观看/评分/收藏行为的用户）
        2. 推荐这些用户喜欢但当前用户未看过的视频
        """
        # 获取当前用户的行为数据
        user_watched_result = await self.db.execute(
            select(WatchHistory.video_id).filter(WatchHistory.user_id == user_id)
        )
        user_watched_ids = [row[0] for row in user_watched_result.fetchall()]

        user_favorited_result = await self.db.execute(
            select(Favorite.video_id).filter(Favorite.user_id == user_id)
        )
        user_favorited_ids = [row[0] for row in user_favorited_result.fetchall()]

        # 如果用户没有任何行为数据，返回空
        if not user_watched_ids and not user_favorited_ids:
            return []

        # 找到有相似行为的用户
        # 这里简化处理：找到观看过相同视频的其他用户
        similar_users_result = await self.db.execute(
            select(
                WatchHistory.user_id, func.count(WatchHistory.id).label("overlap_count")
            )
            .filter(
                WatchHistory.user_id != user_id,
                WatchHistory.video_id.in_(user_watched_ids),
            )
            .group_by(WatchHistory.user_id)
            .order_by(desc("overlap_count"))
            .limit(20)  # 找前20个最相似的用户
        )
        similar_user_ids = [row[0] for row in similar_users_result.fetchall()]

        if not similar_user_ids:
            return []

        # 获取这些相似用户喜欢的视频
        # 通过收藏和高评分来衡量"喜欢"
        recommended_video_ids_result = await self.db.execute(
            select(Favorite.video_id, func.count(Favorite.id).label("favorite_count"))
            .filter(
                Favorite.user_id.in_(similar_user_ids),
                Favorite.video_id.not_in(
                    user_watched_ids + user_favorited_ids + exclude_ids
                ),
            )
            .group_by(Favorite.video_id)
            .order_by(desc("favorite_count"))
            .limit(limit)
        )
        recommended_video_ids = [
            row[0] for row in recommended_video_ids_result.fetchall()
        ]

        # 获取视频详情
        if not recommended_video_ids:
            return []

        from app.models.video import VideoCategory

        result = await self.db.execute(
            select(Video)
            .options(
                selectinload(Video.country),
                selectinload(Video.video_categories).selectinload(VideoCategory.category)
            )
            .filter(
                Video.id.in_(recommended_video_ids),
                Video.status == VideoStatus.PUBLISHED,
            )
        )
        return list(result.scalars().all())

    async def _get_content_based_recommendations(
        self, user_id: int, limit: int, exclude_ids: List[int]
    ) -> List[Video]:
        """
        基于内容的推荐

        分析用户的观看历史，推荐相似内容的视频
        """
        # 获取用户最近观看的视频（最多取20个）
        recent_watched_result = await self.db.execute(
            select(WatchHistory.video_id)
            .filter(WatchHistory.user_id == user_id)
            .order_by(desc(WatchHistory.updated_at))
            .limit(20)
        )
        recent_video_ids = [row[0] for row in recent_watched_result.fetchall()]

        if not recent_video_ids:
            return []

        # 获取这些视频的分类、演员、导演
        videos_result = await self.db.execute(
            select(Video)
            .options(
                selectinload(Video.video_categories),
                selectinload(Video.video_actors),
                selectinload(Video.video_directors),
            )
            .filter(Video.id.in_(recent_video_ids))
        )
        watched_videos = list(videos_result.scalars().all())

        # 统计用户偏好的分类、演员、导演
        category_counts = defaultdict(int)
        actor_counts = defaultdict(int)
        director_counts = defaultdict(int)
        country_counts = defaultdict(int)

        for video in watched_videos:
            for vc in video.video_categories:
                category_counts[vc.category_id] += 1
            for va in video.video_actors:
                actor_counts[va.actor_id] += 1
            for vd in video.video_directors:
                director_counts[vd.director_id] += 1
            if video.country_id:
                country_counts[video.country_id] += 1

        # 获取最常见的偏好
        top_categories = sorted(
            category_counts.items(), key=lambda x: x[1], reverse=True
        )[:3]
        top_actors = sorted(actor_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_directors = sorted(
            director_counts.items(), key=lambda x: x[1], reverse=True
        )[:2]

        # 构建推荐查询
        filters = []
        if top_categories:
            category_ids = [c[0] for c in top_categories]
            filters.append(Video.video_categories.any(category_id__in=category_ids))
        if top_actors:
            actor_ids = [a[0] for a in top_actors]
            filters.append(Video.video_actors.any(actor_id__in=actor_ids))
        if top_directors:
            director_ids = [d[0] for d in top_directors]
            filters.append(Video.video_directors.any(director_id__in=director_ids))

        if not filters:
            return []

        # 查询推荐视频
        from app.models.video import VideoCategory

        query = (
            select(Video)
            .options(
                selectinload(Video.country),
                selectinload(Video.video_categories).selectinload(VideoCategory.category)
            )
            .filter(
                Video.status == VideoStatus.PUBLISHED,
                Video.id.not_in(recent_video_ids + exclude_ids),
                or_(*filters),
            )
            .order_by(desc(Video.average_rating), desc(Video.view_count))
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def _get_popular_videos(
        self, limit: int, exclude_ids: List[int]
    ) -> List[Video]:
        """获取热门视频（按观看次数和评分综合排序）"""
        cache_key = f"popular_videos:limit_{limit}"
        cached = await Cache.get(cache_key)
        if cached:
            # 检查缓存数据类型,确保是Video对象而非字典
            if len(cached) > 0 and isinstance(cached[0], Video):
                # 过滤掉排除的视频
                filtered = [v for v in cached if v.id not in exclude_ids]
                return filtered[:limit]
            # 如果缓存数据类型不对或为空,清空缓存重新查询
            cached = None

        # 查询热门视频
        from app.models.video import VideoCategory

        query = (
            select(Video)
            .options(
                selectinload(Video.country),
                selectinload(Video.video_categories).selectinload(VideoCategory.category)
            )
            .filter(
                Video.status == VideoStatus.PUBLISHED,
                Video.id.not_in(exclude_ids) if exclude_ids else True,
            )
            .order_by(
                desc(
                    Video.view_count * 0.7
                    + Video.average_rating * Video.rating_count * 0.3
                )
            )
            .limit(limit * 2)  # 多取一些以便过滤后仍有足够数量
        )

        result = await self.db.execute(query)
        popular_videos = list(result.scalars().all())

        # 缓存15分钟
        await Cache.set(cache_key, popular_videos, ttl=900)
        return popular_videos[:limit]

    def _calculate_similarity_score(self, video1: Video, video2: Video) -> float:
        """
        计算两个视频的相似度分数

        考虑因素：
        - 分类重叠
        - 演员重叠
        - 导演重叠
        - 国家相同
        - 评分相近
        """
        score = 0.0

        # 分类相似度（权重40%）
        categories1 = {vc.category_id for vc in video1.video_categories}
        categories2 = {vc.category_id for vc in video2.video_categories}
        if categories1 and categories2:
            category_overlap = len(categories1 & categories2) / len(
                categories1 | categories2
            )
            score += category_overlap * 0.4

        # 演员相似度（权重30%）
        actors1 = {va.actor_id for va in video1.video_actors}
        actors2 = {va.actor_id for va in video2.video_actors}
        if actors1 and actors2:
            actor_overlap = len(actors1 & actors2) / len(actors1 | actors2)
            score += actor_overlap * 0.3

        # 导演相似度（权重20%）
        directors1 = {vd.director_id for vd in video1.video_directors}
        directors2 = {vd.director_id for vd in video2.video_directors}
        if directors1 and directors2:
            director_overlap = len(directors1 & directors2) / len(
                directors1 | directors2
            )
            score += director_overlap * 0.2

        # 国家相同（权重5%）
        if (
            video1.country_id
            and video2.country_id
            and video1.country_id == video2.country_id
        ):
            score += 0.05

        # 评分相近（权重5%）
        if video1.average_rating and video2.average_rating:
            rating_diff = abs(video1.average_rating - video2.average_rating)
            rating_similarity = max(0, 1 - rating_diff / 10)  # 假设评分最大10分
            score += rating_similarity * 0.05

        return score
