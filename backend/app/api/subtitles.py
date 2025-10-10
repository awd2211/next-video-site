from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.subtitle import Subtitle
from app.models.video import Video
from app.schemas.subtitle import SubtitleResponse, SubtitleListResponse

router = APIRouter()


@router.get("/{video_id}/subtitles", response_model=SubtitleListResponse)
async def get_video_subtitles(
    video_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    获取指定视频的所有字幕 (公开API)

    - **video_id**: 视频ID

    返回该视频的所有可用字幕列表,按排序顺序排列
    """
    # 验证视频存在
    video_result = await db.execute(
        select(Video).where(Video.id == video_id)
    )
    video = video_result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # 查询字幕
    query = (
        select(Subtitle)
        .where(Subtitle.video_id == video_id)
        .order_by(Subtitle.sort_order, Subtitle.created_at)
    )
    result = await db.execute(query)
    subtitles = result.scalars().all()

    return SubtitleListResponse(
        subtitles=[SubtitleResponse.model_validate(s) for s in subtitles],
        total=len(subtitles),
    )
