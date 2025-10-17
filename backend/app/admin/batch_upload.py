"""
批量视频上传管理 API
支持多文件并发上传、断点续传、进度追踪
"""

import hashlib
import io
import os
import shutil
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, BackgroundTasks
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import AdminUser
from app.models.upload_session import UploadSession
from app.utils.dependencies import get_current_admin_user
from app.utils.minio_client import minio_client
from app.utils.video_hash import calculate_video_fingerprint, check_duplicate_video

router = APIRouter()


@router.post("/batch/init")
async def init_batch_upload(
    files: List[dict],  # [{"filename": "...", "file_size": ..., "mime_type": "..."}]
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """初始化批量上传"""
    batch_id = hashlib.md5(f"{current_admin.id}{datetime.now(timezone.utc)}".encode()).hexdigest()
    upload_sessions = []

    for file_info in files:
        # 生成唯一的上传 ID
        upload_id = hashlib.md5(
            f"{file_info['filename']}{file_info['file_size']}{datetime.now(timezone.utc)}".encode()
        ).hexdigest()

        # 计算分块数
        chunk_size = 5 * 1024 * 1024  # 5MB
        total_chunks = (file_info["file_size"] + chunk_size - 1) // chunk_size

        # 创建临时目录
        temp_dir = f"/tmp/uploads/{upload_id}"
        os.makedirs(temp_dir, exist_ok=True)

        # 创建上传会话
        session = UploadSession(
            upload_id=upload_id,
            filename=file_info["filename"],
            file_size=file_info["file_size"],
            mime_type=file_info.get("mime_type"),
            chunk_size=chunk_size,
            total_chunks=total_chunks,
            uploaded_chunks=[],
            title=file_info.get("title", file_info["filename"]),
            description=file_info.get("description"),
            parent_id=file_info.get("parent_id"),
            tags=file_info.get("tags"),
            temp_dir=temp_dir,
            uploader_id=current_admin.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )

        db.add(session)
        upload_sessions.append(
            {
                "upload_id": upload_id,
                "filename": file_info["filename"],
                "chunk_size": chunk_size,
                "total_chunks": total_chunks,
            }
        )

    await db.commit()

    return {
        "batch_id": batch_id,
        "sessions": upload_sessions,
        "message": f"已初始化 {len(files)} 个文件的上传会话",
    }


@router.post("/batch/chunk")
async def upload_batch_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """上传批量上传的单个分片"""
    # 查询上传会话
    result = await db.execute(
        select(UploadSession).filter(UploadSession.upload_id == upload_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="上传会话不存在")

    # 检查权限
    if session.uploader_id != current_admin.id:
        raise HTTPException(status_code=403, detail="无权访问此上传会话")

    # 检查会话是否过期
    if session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="上传会话已过期")

    # 保存分片
    chunk_path = f"{session.temp_dir}/chunk_{chunk_index}"
    content = await file.read()

    with open(chunk_path, "wb") as f:
        f.write(content)

    # 更新已上传分片列表
    if chunk_index not in session.uploaded_chunks:
        session.uploaded_chunks.append(chunk_index)
        session.uploaded_chunks.sort()

    await db.commit()

    progress = session.get_progress()

    return {
        "upload_id": upload_id,
        "chunk_index": chunk_index,
        "uploaded_chunks": len(session.uploaded_chunks),
        "total_chunks": session.total_chunks,
        "progress": round(progress, 2),
    }


@router.post("/batch/complete/{upload_id}")
async def complete_batch_upload_item(
    upload_id: str,
    background_tasks: BackgroundTasks,
    video_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """完成批量上传中的单个文件"""
    # 查询上传会话
    result = await db.execute(
        select(UploadSession).filter(UploadSession.upload_id == upload_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="上传会话不存在")

    # 检查权限
    if session.uploader_id != current_admin.id:
        raise HTTPException(status_code=403, detail="无权访问此上传会话")

    # 检查是否所有分片都已上传
    if not session.is_upload_complete():
        missing = set(range(session.total_chunks)) - set(session.uploaded_chunks)
        raise HTTPException(status_code=400, detail=f"缺少分片: {list(missing)[:10]}")

    # 合并分片
    merged_file = io.BytesIO()

    try:
        for i in range(session.total_chunks):
            chunk_path = f"{session.temp_dir}/chunk_{i}"
            with open(chunk_path, "rb") as f:
                merged_file.write(f.read())

        merged_file.seek(0)

        # 计算视频指纹（用于重复检测）
        file_content = merged_file.read()
        merged_file.seek(0)  # 重置指针

        fingerprint = calculate_video_fingerprint(
            file_content=file_content,
            title=session.title or session.filename,
            duration=0  # 无法获取时长，使用0
        )

        # 检查是否重复
        is_duplicate, duplicate_video_id = await check_duplicate_video(
            db=db,
            file_hash=fingerprint['file_hash_md5'],
            partial_hash=fingerprint['partial_hash'],
            metadata_hash=fingerprint.get('metadata_hash')
        )

        if is_duplicate:
            # 清理临时文件
            shutil.rmtree(session.temp_dir, ignore_errors=True)
            raise HTTPException(
                status_code=409,
                detail=f"视频重复，已存在相同的视频 (ID: {duplicate_video_id})"
            )

        # 上传到 MinIO
        ext = session.filename.split(".")[-1]
        timestamp = int(datetime.now(timezone.utc).timestamp())
        object_name = f"videos/batch_{upload_id}_{timestamp}.{ext}"

        url = minio_client.upload_video(merged_file, object_name, session.mime_type or "video/mp4")

        # 标记为已完成和已合并
        session.is_completed = True
        session.is_merged = True
        await db.commit()

        # 后台任务清理临时文件
        background_tasks.add_task(cleanup_temp_files, session.temp_dir)

        return {
            "upload_id": upload_id,
            "url": url,
            "filename": session.filename,
            "message": "文件上传完成",
        }

    except Exception as e:
        logger.error(f"合并上传文件失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/batch/status")
async def get_batch_upload_status(
    upload_ids: str,  # 逗号分隔的 upload_id 列表
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取批量上传的状态"""
    ids = upload_ids.split(",")

    result = await db.execute(
        select(UploadSession).filter(
            UploadSession.upload_id.in_(ids),
            UploadSession.uploader_id == current_admin.id,
        )
    )
    sessions = result.scalars().all()

    status_list = []
    for session in sessions:
        status_list.append(
            {
                "upload_id": session.upload_id,
                "filename": session.filename,
                "file_size": session.file_size,
                "uploaded_chunks": len(session.uploaded_chunks),
                "total_chunks": session.total_chunks,
                "progress": round(session.get_progress(), 2),
                "is_completed": session.is_completed,
                "is_merged": session.is_merged,
            }
        )

    return {"sessions": status_list}


@router.delete("/batch/cancel/{upload_id}")
async def cancel_batch_upload_item(
    upload_id: str,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """取消批量上传中的单个文件"""
    result = await db.execute(
        select(UploadSession).filter(UploadSession.upload_id == upload_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        return {"message": "上传会话不存在或已删除"}

    # 检查权限
    if session.uploader_id != current_admin.id:
        raise HTTPException(status_code=403, detail="无权访问此上传会话")

    # 清理临时文件
    shutil.rmtree(session.temp_dir, ignore_errors=True)

    # 删除会话
    await db.delete(session)
    await db.commit()

    return {"message": "上传已取消"}


def cleanup_temp_files(temp_dir: str):
    """后台任务：清理临时文件"""
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
        logger.info(f"已清理临时目录: {temp_dir}")
    except Exception as e:
        logger.error(f"清理临时目录失败: {e}", exc_info=True)
