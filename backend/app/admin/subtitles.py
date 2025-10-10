from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, update
from app.database import get_db
from app.models.subtitle import Subtitle
from app.models.video import Video
from app.models.user import AdminUser
from app.schemas.subtitle import (
    SubtitleCreate,
    SubtitleUpdate,
    SubtitleResponse,
    SubtitleListResponse,
)
from app.utils.dependencies import get_current_admin_user
from typing import Optional
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/videos/{video_id}/subtitles", response_model=SubtitleListResponse)
async def get_video_subtitles(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取指定视频的所有字幕

    - **video_id**: 视频ID
    """
    # 验证视频存在
    video_result = await db.execute(select(Video).where(Video.id == video_id))
    video = video_result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

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


@router.post("/videos/{video_id}/subtitles", response_model=SubtitleResponse)
async def create_subtitle(
    video_id: int,
    subtitle_data: SubtitleCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    为视频添加字幕

    - **video_id**: 视频ID
    - **subtitle_data**: 字幕信息
    """
    # 验证视频存在
    video_result = await db.execute(select(Video).where(Video.id == video_id))
    video = video_result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    # 检查是否已存在该语言的字幕
    existing_query = select(Subtitle).where(
        and_(
            Subtitle.video_id == video_id,
            Subtitle.language == subtitle_data.language
        )
    )
    existing_result = await db.execute(existing_query)
    existing_subtitle = existing_result.scalar_one_or_none()
    if existing_subtitle:
        raise HTTPException(
            status_code=400,
            detail=f"该视频已存在 {subtitle_data.language_name} 字幕"
        )

    # 如果设置为默认字幕,取消其他字幕的默认状态
    if subtitle_data.is_default:
        await db.execute(
            update(Subtitle)
            .where(Subtitle.video_id == video_id)
            .values(is_default=False)
        )

    # 创建字幕
    new_subtitle = Subtitle(
        video_id=video_id,
        language=subtitle_data.language,
        language_name=subtitle_data.language_name,
        file_url=subtitle_data.file_url,
        format=subtitle_data.format,
        is_default=subtitle_data.is_default,
        is_auto_generated=subtitle_data.is_auto_generated,
        sort_order=subtitle_data.sort_order,
    )

    db.add(new_subtitle)
    await db.commit()
    await db.refresh(new_subtitle)

    logger.info(
        f"✅ 字幕已创建: video_id={video_id}, language={subtitle_data.language}"
    )

    return SubtitleResponse.model_validate(new_subtitle)


@router.patch("/subtitles/{subtitle_id}", response_model=SubtitleResponse)
async def update_subtitle(
    subtitle_id: int,
    subtitle_data: SubtitleUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    更新字幕信息

    - **subtitle_id**: 字幕ID
    - **subtitle_data**: 更新的字幕信息
    """
    # 查询字幕
    query = select(Subtitle).where(Subtitle.id == subtitle_id)
    result = await db.execute(query)
    subtitle = result.scalar_one_or_none()

    if not subtitle:
        raise HTTPException(status_code=404, detail="字幕不存在")

    # 如果设置为默认字幕,取消其他字幕的默认状态
    if subtitle_data.is_default is True:
        await db.execute(
            update(Subtitle)
            .where(
                and_(
                    Subtitle.video_id == subtitle.video_id,
                    Subtitle.id != subtitle_id
                )
            )
            .values(is_default=False)
        )

    # 更新字幕
    update_data = subtitle_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(subtitle, key, value)

    await db.commit()
    await db.refresh(subtitle)

    logger.info(f"✅ 字幕已更新: subtitle_id={subtitle_id}")

    return SubtitleResponse.model_validate(subtitle)


@router.delete("/subtitles/{subtitle_id}")
async def delete_subtitle(
    subtitle_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    删除字幕

    - **subtitle_id**: 字幕ID
    """
    # 查询字幕
    query = select(Subtitle).where(Subtitle.id == subtitle_id)
    result = await db.execute(query)
    subtitle = result.scalar_one_or_none()

    if not subtitle:
        raise HTTPException(status_code=404, detail="字幕不存在")

    # 删除字幕
    await db.delete(subtitle)
    await db.commit()

    logger.info(f"✅ 字幕已删除: subtitle_id={subtitle_id}")

    # TODO: 同时删除MinIO中的字幕文件

    return {"message": "字幕已删除"}


@router.post("/subtitles/upload")
async def upload_subtitle_file(
    video_id: int = Form(...),
    language: str = Form(...),
    language_name: str = Form(...),
    is_default: bool = Form(False),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    上传字幕文件

    - **video_id**: 视频ID
    - **language**: 语言代码
    - **language_name**: 语言名称
    - **is_default**: 是否默认字幕
    - **file**: 字幕文件 (支持 .srt, .vtt, .ass)
    """
    # 验证视频存在
    video_result = await db.execute(select(Video).where(Video.id == video_id))
    video = video_result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    # 验证文件格式
    if not file.filename:
        raise HTTPException(status_code=400, detail="无效的文件")

    file_ext = file.filename.lower().split('.')[-1]
    if file_ext not in ['srt', 'vtt', 'ass']:
        raise HTTPException(
            status_code=400,
            detail="不支持的字幕格式,仅支持 .srt, .vtt, .ass"
        )

    # 读取文件内容
    content = await file.read()

    # TODO: 上传到MinIO
    # 临时实现:保存到本地
    import os
    from pathlib import Path
    from app.utils.subtitle_converter import SubtitleConverter

    upload_dir = Path("/tmp/subtitles")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # 保存原始文件
    original_file_path = upload_dir / f"video_{video_id}_{language}.{file_ext}"
    with open(original_file_path, "wb") as f:
        f.write(content)

    # 🆕 如果是SRT格式,自动转换为VTT (Video.js原生支持VTT)
    if file_ext == 'srt':
        try:
            vtt_file_path = SubtitleConverter.srt_file_to_vtt_file(original_file_path)
            file_url = str(vtt_file_path)
            file_ext = 'vtt'
            logger.info(f"✅ SRT字幕已转换为VTT: {file_url}")
        except Exception as e:
            logger.error(f"❌ SRT转VTT失败: {str(e)}")
            file_url = str(original_file_path)
    else:
        file_url = str(original_file_path)

    logger.info(f"✅ 字幕文件已上传: {file_url}")

    # 创建字幕记录
    subtitle_create = SubtitleCreate(
        video_id=video_id,
        language=language,
        language_name=language_name,
        file_url=file_url,
        format=file_ext,
        is_default=is_default,
        is_auto_generated=False,
        sort_order=0,
    )

    return await create_subtitle(
        video_id=video_id,
        subtitle_data=subtitle_create,
        db=db,
        current_admin=current_admin,
    )
