"""
文件上传管理 API（支持分片上传和断点续传）
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime, timezone
from app.database import get_db
from app.models.user import AdminUser
from app.utils.dependencies import get_current_admin_user
from app.utils.minio_client import minio_client
import hashlib
import os
import io

router = APIRouter()

# 临时存储分片信息（生产环境应使用 Redis）
upload_sessions = {}


@router.post("/init-multipart")
async def init_multipart_upload(
    filename: str = Form(...),
    file_size: int = Form(...),
    file_type: str = Form(...),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """初始化分片上传"""
    # 生成唯一的上传 ID
    upload_id = hashlib.md5(f"{filename}{file_size}{datetime.now(timezone.utc)}".encode()).hexdigest()

    # 存储上传会话信息
    upload_sessions[upload_id] = {
        "filename": filename,
        "file_size": file_size,
        "file_type": file_type,
        "uploaded_chunks": [],
        "total_chunks": 0,
        "created_at": datetime.now(timezone.utc),
    }

    return {
        "upload_id": upload_id,
        "chunk_size": 5 * 1024 * 1024,  # 5MB 每片
        "message": "分片上传已初始化"
    }


@router.post("/upload-chunk")
async def upload_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    file: UploadFile = File(...),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """上传单个分片"""
    if upload_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="上传会话不存在")

    session = upload_sessions[upload_id]
    session["total_chunks"] = total_chunks

    # 保存分片到临时位置
    temp_dir = f"/tmp/uploads/{upload_id}"
    os.makedirs(temp_dir, exist_ok=True)

    chunk_path = f"{temp_dir}/chunk_{chunk_index}"
    content = await file.read()

    with open(chunk_path, "wb") as f:
        f.write(content)

    # 记录已上传的分片
    if chunk_index not in session["uploaded_chunks"]:
        session["uploaded_chunks"].append(chunk_index)

    uploaded_count = len(session["uploaded_chunks"])
    progress = (uploaded_count / total_chunks) * 100

    return {
        "chunk_index": chunk_index,
        "uploaded_chunks": uploaded_count,
        "total_chunks": total_chunks,
        "progress": round(progress, 2),
        "message": f"分片 {chunk_index + 1}/{total_chunks} 上传成功"
    }


@router.post("/complete-multipart")
async def complete_multipart_upload(
    upload_id: str = Form(...),
    video_id: Optional[int] = Form(None),
    upload_type: str = Form("video"),  # video, poster, backdrop
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """完成分片上传并合并文件"""
    if upload_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="上传会话不存在")

    session = upload_sessions[upload_id]

    # 检查是否所有分片都已上传
    expected_chunks = list(range(session["total_chunks"]))
    uploaded_chunks = sorted(session["uploaded_chunks"])

    if uploaded_chunks != expected_chunks:
        missing = set(expected_chunks) - set(uploaded_chunks)
        raise HTTPException(
            status_code=400,
            detail=f"缺少分片: {missing}"
        )

    # 合并分片
    temp_dir = f"/tmp/uploads/{upload_id}"
    merged_file = io.BytesIO()

    for i in range(session["total_chunks"]):
        chunk_path = f"{temp_dir}/chunk_{i}"
        with open(chunk_path, "rb") as f:
            merged_file.write(f.read())

    merged_file.seek(0)

    # 上传到 MinIO
    try:
        ext = session["filename"].split(".")[-1]
        timestamp = int(datetime.now(timezone.utc).timestamp())

        if upload_type == "video":
            object_name = f"videos/video_{video_id}_{timestamp}.{ext}"
            url = minio_client.upload_video(
                merged_file,
                object_name,
                session["file_type"]
            )
        elif upload_type == "poster":
            object_name = f"posters/poster_{video_id}_{timestamp}.{ext}"
            url = minio_client.upload_image(
                merged_file,
                object_name,
                session["file_type"]
            )
        elif upload_type == "backdrop":
            object_name = f"backdrops/backdrop_{video_id}_{timestamp}.{ext}"
            url = minio_client.upload_image(
                merged_file,
                object_name,
                session["file_type"]
            )
        else:
            raise HTTPException(status_code=400, detail="不支持的上传类型")

        # 清理临时文件
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

        # 清理会话
        del upload_sessions[upload_id]

        return {
            "url": url,
            "message": "文件上传完成"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/upload-status/{upload_id}")
async def get_upload_status(
    upload_id: str,
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取上传状态"""
    if upload_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="上传会话不存在")

    session = upload_sessions[upload_id]
    uploaded_count = len(session["uploaded_chunks"])
    total_chunks = session["total_chunks"]
    progress = (uploaded_count / total_chunks * 100) if total_chunks > 0 else 0

    return {
        "upload_id": upload_id,
        "filename": session["filename"],
        "file_size": session["file_size"],
        "uploaded_chunks": uploaded_count,
        "total_chunks": total_chunks,
        "progress": round(progress, 2),
        "missing_chunks": list(set(range(total_chunks)) - set(session["uploaded_chunks"]))
    }


@router.delete("/cancel-upload/{upload_id}")
async def cancel_upload(
    upload_id: str,
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """取消上传并清理临时文件"""
    if upload_id in upload_sessions:
        # 清理临时文件
        temp_dir = f"/tmp/uploads/{upload_id}"
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

        # 清理会话
        del upload_sessions[upload_id]

    return {"message": "上传已取消"}
