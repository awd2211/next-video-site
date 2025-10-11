"""
推荐系统 API 端点
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.video import VideoListResponse
from app.utils.dependencies import get_current_user_optional
from app.utils.recommendation_engine import RecommendationEngine

router = APIRouter()


@router.get("/personalized", response_model=List[VideoListResponse])
async def get_personalized_recommendations(
    limit: int = Query(20, ge=1, le=100, description="推荐数量"),
    exclude_ids: Optional[str] = Query(None, description="排除的视频ID列表,逗号分隔"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    获取个性化推荐视频

    - 已登录用户：基于用户行为的智能推荐（协同过滤 + 内容推荐）
    - 未登录用户：热门视频推荐
    """
    # 解析排除的视频ID
    exclude_video_ids = []
    if exclude_ids:
        try:
            exclude_video_ids = [
                int(id.strip()) for id in exclude_ids.split(",") if id.strip()
            ]
        except ValueError:
            pass

    # 创建推荐引擎
    engine = RecommendationEngine(db)

    # 获取推荐
    user_id = current_user.id if current_user else None
    recommended_videos = await engine.get_personalized_recommendations(
        user_id=user_id, limit=limit, exclude_video_ids=exclude_video_ids
    )

    return [VideoListResponse.model_validate(v) for v in recommended_videos]


@router.get("/similar/{video_id}", response_model=List[VideoListResponse])
async def get_similar_videos(
    video_id: int,
    limit: int = Query(10, ge=1, le=50, description="推荐数量"),
    exclude_ids: Optional[str] = Query(None, description="排除的视频ID列表,逗号分隔"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取相似视频推荐

    基于视频的：
    - 分类
    - 演员/导演
    - 国家
    - 评分

    计算相似度并返回最相似的视频
    """
    # 解析排除的视频ID
    exclude_video_ids = []
    if exclude_ids:
        try:
            exclude_video_ids = [
                int(id.strip()) for id in exclude_ids.split(",") if id.strip()
            ]
        except ValueError:
            pass

    # 创建推荐引擎
    engine = RecommendationEngine(db)

    # 获取相似视频
    similar_videos = await engine.get_similar_videos(
        video_id=video_id, limit=limit, exclude_video_ids=exclude_video_ids
    )

    return [VideoListResponse.model_validate(v) for v in similar_videos]


@router.get("/for-you", response_model=List[VideoListResponse])
async def get_for_you_recommendations(
    limit: int = Query(20, ge=1, le=100, description="推荐数量"),
    current_user: User = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    "为你推荐" - 首页个性化推荐

    与 /personalized 相同，但专门用于首页展示
    """
    engine = RecommendationEngine(db)
    user_id = current_user.id if current_user else None

    recommended_videos = await engine.get_personalized_recommendations(
        user_id=user_id, limit=limit, exclude_video_ids=[]
    )

    return [VideoListResponse.model_validate(v) for v in recommended_videos]
