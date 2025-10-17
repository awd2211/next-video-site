"""
文件上传管理 API（优化版）
- 使用 Redis 存储会话（支持分布式）
- 使用 MinIO 原生 Multipart Upload（零内存占用）
- 后端文件验证 + MD5 校验
- 限流保护
- 上传统计
"""

import hashlib
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.upload_statistics import UploadStatistics
from app.models.user import AdminUser
from app.utils.admin_notification_service import AdminNotificationService
from app.utils.dependencies import get_current_admin_user
from app.utils.file_validator import FileValidator
from app.utils.minio_client import minio_client
from app.utils.upload_session_manager import UploadSessionManager

router = APIRouter()

# 创建限流器
limiter = Limiter(key_func=get_remote_address)


@router.post("/init-multipart")
@limiter.limit("10/hour")  # 每小时最多 10 次初始化
async def init_multipart_upload(
    request: Request,
    filename: str = Form(...),
    file_size: int = Form(...),
    file_type: str = Form(...),
    upload_type: str = Form("video"),  # video, poster, backdrop
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    初始化分片上传（使用 Redis 会话 + MinIO Multipart）

    优化:
    - 使用 Redis 存储会话，支持分布式
    - 后端验证文件
    - 创建 MinIO Multipart Upload
    - 记录上传统计
    """
    try:
        # 1. 后端验证文件
        if upload_type == "video":
            valid, error = FileValidator.validate_video_file(
                filename, file_type, file_size, max_size=5368709120  # 5GB
            )
        else:  # poster, backdrop
            valid, error = FileValidator.validate_image_file(
                filename, file_type, file_size, max_size=10485760  # 10MB
            )

        if not valid:
            raise HTTPException(status_code=400, detail=error)

        # 2. 生成唯一的上传 ID
        upload_id = hashlib.md5(
            f"{filename}{file_size}{datetime.now(timezone.utc)}{current_admin.id}".encode()
        ).hexdigest()

        # 3. 计算分片数（5MB 每片）
        chunk_size = 5 * 1024 * 1024
        total_chunks = (file_size + chunk_size - 1) // chunk_size

        # 4. 生成 MinIO 对象名称
        ext = FileValidator.get_file_extension(filename)
        timestamp = int(datetime.now(timezone.utc).timestamp())
        object_name = f"{upload_type}s/{upload_type}_{upload_id}_{timestamp}.{ext}"

        # 5. 创建 MinIO Multipart Upload
        try:
            minio_upload_id = minio_client.create_multipart_upload(
                object_name, file_type
            )
        except Exception as e:
            logger.error(f"Failed to create MinIO multipart upload: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"创建上传会话失败: {str(e)}"
            )

        # 6. 创建 Redis 会话
        await UploadSessionManager.create_session(
            upload_id=upload_id,
            filename=filename,
            file_size=file_size,
            file_type=file_type,
            total_chunks=total_chunks,
            admin_id=current_admin.id,
        )

        # 更新会话，添加 MinIO 信息
        await UploadSessionManager.update_session(
            upload_id,
            {
                "minio_upload_id": minio_upload_id,
                "object_name": object_name,
                "upload_type": upload_type,
            },
        )

        # 7. 创建上传统计记录
        upload_stat = UploadStatistics(
            upload_id=upload_id,
            filename=filename,
            file_size=file_size,
            mime_type=file_type,
            upload_type=upload_type,
            admin_id=current_admin.id,
            total_chunks=total_chunks,
            uploaded_chunks=0,
            object_name=object_name,
            minio_upload_id=minio_upload_id,
            ip_address=request.client.host if request.client else None,
            started_at=datetime.now(timezone.utc),
        )
        db.add(upload_stat)
        await db.commit()

        logger.info(
            f"✅ Initialized multipart upload: {upload_id} for {filename} ({file_size} bytes, {total_chunks} chunks)"
        )

        return {
            "upload_id": upload_id,
            "chunk_size": chunk_size,
            "total_chunks": total_chunks,
            "message": "分片上传已初始化（优化版：Redis + MinIO Multipart）",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to init multipart upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"初始化失败: {str(e)}")


@router.post("/upload-chunk")
@limiter.limit("200/minute")  # 每分钟最多 200 个分片
async def upload_chunk(
    request: Request,
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    chunk_hash: Optional[str] = Form(None),  # 🆕 MD5 校验
    file: UploadFile = File(...),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    上传单个分片（使用 MinIO Multipart Upload）

    优化:
    - 直接上传到 MinIO，无需临时文件
    - 零内存占用（流式上传）
    - MD5 校验（可选）
    - 从 Redis 读取会话
    """
    try:
        # 1. 获取会话
        session = await UploadSessionManager.get_session(upload_id)
        if not session:
            raise HTTPException(status_code=404, detail="上传会话不存在或已过期")

        # 2. 验证管理员权限
        if session.get("admin_id") != current_admin.id:
            raise HTTPException(status_code=403, detail="无权操作此上传会话")

        # 3. 读取分片数据
        chunk_data = await file.read()

        # 4. 🆕 MD5 校验（如果提供）
        if chunk_hash:
            if not FileValidator.validate_chunk_hash(chunk_data, chunk_hash):
                raise HTTPException(
                    status_code=400,
                    detail=f"分片 {chunk_index} 哈希校验失败，数据可能损坏",
                )

        # 5. 上传到 MinIO（part_number 从 1 开始）
        object_name = session.get("object_name")
        minio_upload_id = session.get("minio_upload_id")

        try:
            etag = minio_client.upload_part(
                object_name=object_name,
                upload_id=minio_upload_id,
                part_number=chunk_index + 1,  # MinIO uses 1-based indexing
                data=chunk_data,
            )
        except Exception as e:
            logger.error(f"Failed to upload part to MinIO: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"分片上传失败: {str(e)}")

        # 6. 标记分片为已上传（Redis）
        await UploadSessionManager.mark_chunk_uploaded(upload_id, chunk_index)

        # 7. 保存 ETag（用于完成上传）
        uploaded_chunks = session.get("uploaded_chunks", [])
        parts_map = session.get("parts_map", {})
        parts_map[str(chunk_index)] = etag
        await UploadSessionManager.update_session(upload_id, {"parts_map": parts_map})

        # 8. 计算进度
        progress = await UploadSessionManager.get_progress(upload_id)

        logger.debug(
            f"📦 Uploaded chunk {chunk_index}/{total_chunks - 1} for {upload_id}, progress: {progress:.2f}%"
        )

        return {
            "chunk_index": chunk_index,
            "uploaded_chunks": len(uploaded_chunks) + 1,
            "total_chunks": total_chunks,
            "progress": round(progress, 2),
            "etag": etag,
            "message": f"分片 {chunk_index + 1}/{total_chunks} 上传成功",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload chunk: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.post("/complete-multipart")
async def complete_multipart_upload(
    upload_id: str = Form(...),
    video_id: Optional[int] = Form(None),
    upload_type: str = Form("video"),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    完成分片上传（MinIO 服务端合并）

    优化:
    - MinIO 服务端自动合并，零内存
    - 无需临时文件
    - 记录上传统计
    """
    try:
        # 1. 获取会话
        session = await UploadSessionManager.get_session(upload_id)
        if not session:
            raise HTTPException(status_code=404, detail="上传会话不存在")

        # 2. 验证权限
        if session.get("admin_id") != current_admin.id:
            raise HTTPException(status_code=403, detail="无权操作此上传会话")

        # 3. 检查是否所有分片都已上传
        if not await UploadSessionManager.is_upload_complete(upload_id):
            uploaded_chunks = session.get("uploaded_chunks", [])
            total_chunks = session.get("total_chunks", 0)
            missing = set(range(total_chunks)) - set(uploaded_chunks)
            raise HTTPException(
                status_code=400,
                detail=f"上传未完成，缺少分片: {sorted(missing)[:10]}...",  # 只显示前 10 个
            )

        # 4. 准备 MinIO parts 列表
        parts_map = session.get("parts_map", {})
        parts = [
            (int(chunk_index) + 1, etag)  # (part_number, etag)
            for chunk_index, etag in sorted(parts_map.items(), key=lambda x: int(x[0]))
        ]

        # 5. 完成 MinIO Multipart Upload（服务端合并）
        object_name = session.get("object_name")
        minio_upload_id = session.get("minio_upload_id")

        try:
            file_url = minio_client.complete_multipart_upload(
                object_name=object_name,
                upload_id=minio_upload_id,
                parts=parts,
            )
        except Exception as e:
            logger.error(f"Failed to complete MinIO multipart upload: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"合并失败: {str(e)}")

        # 6. 计算上传时长和速度
        end_time = datetime.now(timezone.utc)
        created_at = datetime.fromisoformat(session.get("created_at"))
        duration = (end_time - created_at).total_seconds()
        file_size = session.get("file_size", 0)
        upload_speed = file_size / duration if duration > 0 else 0

        # 7. 更新统计记录
        from sqlalchemy import update

        await db.execute(
            update(UploadStatistics)
            .where(UploadStatistics.upload_id == upload_id)
            .values(
                uploaded_chunks=session.get("total_chunks"),
                duration_seconds=duration,
                upload_speed=upload_speed,
                is_success=True,
                completed_at=end_time,
            )
        )
        await db.commit()

        # 8. 删除 Redis 会话
        await UploadSessionManager.delete_session(upload_id)

        logger.info(
            f"✅ Completed multipart upload: {upload_id}, file: {object_name}, "
            f"duration: {duration:.2f}s, speed: {upload_speed / (1024 * 1024):.2f} MB/s"
        )

        # 9. 慢速上传警告
        if upload_speed > 0 and upload_speed < 500 * 1024:  # < 500 KB/s
            try:
                await AdminNotificationService.notify_system_warning(
                    db=db,
                    warning_type="慢速上传",
                    message=f"上传速度过慢: {upload_speed / 1024:.2f} KB/s，文件: {session.get('filename')}",
                )
            except Exception as e:
                logger.error(f"Failed to send slow upload warning: {e}")

        return {
            "url": file_url,
            "message": "文件上传完成（优化版：MinIO 服务端合并）",
            "duration_seconds": round(duration, 2),
            "upload_speed_mbps": round(upload_speed / (1024 * 1024), 2),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete multipart upload: {e}", exc_info=True)

        # 记录失败统计
        try:
            from sqlalchemy import update

            await db.execute(
                update(UploadStatistics)
                .where(UploadStatistics.upload_id == upload_id)
                .values(
                    is_success=False,
                    error_message=str(e),
                    completed_at=datetime.now(timezone.utc),
                )
            )
            await db.commit()
        except Exception:
            pass

        # 发送失败通知
        try:
            session = await UploadSessionManager.get_session(upload_id)
            if session:
                await AdminNotificationService.notify_upload_failed(
                    db=db,
                    filename=session.get("filename", "未知"),
                    user_name=current_admin.username,
                    error_reason=str(e),
                )
        except Exception as notify_err:
            logger.error(f"Failed to send upload failure notification: {notify_err}")

        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/upload-status/{upload_id}")
async def get_upload_status(
    upload_id: str,
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取上传状态（从 Redis）"""
    try:
        session = await UploadSessionManager.get_session(upload_id)
        if not session:
            raise HTTPException(status_code=404, detail="上传会话不存在")

        # 验证权限
        if session.get("admin_id") != current_admin.id:
            raise HTTPException(status_code=403, detail="无权查看此上传会话")

        progress = await UploadSessionManager.get_progress(upload_id)
        uploaded_chunks = session.get("uploaded_chunks", [])
        total_chunks = session.get("total_chunks", 0)

        return {
            "upload_id": upload_id,
            "filename": session.get("filename"),
            "file_size": session.get("file_size"),
            "uploaded_chunks": len(uploaded_chunks),
            "total_chunks": total_chunks,
            "progress": round(progress, 2),
            "missing_chunks": list(set(range(total_chunks)) - set(uploaded_chunks))[:10],
            "created_at": session.get("created_at"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get upload status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")


@router.delete("/cancel-upload/{upload_id}")
async def cancel_upload(
    upload_id: str,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """取消上传（清理 MinIO Multipart + Redis 会话）"""
    try:
        # 1. 获取会话
        session = await UploadSessionManager.get_session(upload_id)
        if not session:
            return {"message": "上传会话不存在或已过期"}

        # 2. 验证权限
        if session.get("admin_id") != current_admin.id:
            raise HTTPException(status_code=403, detail="无权取消此上传会话")

        # 3. 取消 MinIO Multipart Upload
        object_name = session.get("object_name")
        minio_upload_id = session.get("minio_upload_id")

        if object_name and minio_upload_id:
            try:
                minio_client.abort_multipart_upload(object_name, minio_upload_id)
                logger.info(f"Aborted MinIO multipart upload: {minio_upload_id}")
            except Exception as e:
                logger.warning(f"Failed to abort MinIO multipart upload: {e}")

        # 4. 删除 Redis 会话
        await UploadSessionManager.delete_session(upload_id)

        # 5. 更新统计
        from sqlalchemy import update

        await db.execute(
            update(UploadStatistics)
            .where(UploadStatistics.upload_id == upload_id)
            .values(
                is_success=False,
                error_message="用户取消上传",
                completed_at=datetime.now(timezone.utc),
            )
        )
        await db.commit()

        logger.info(f"Cancelled upload: {upload_id}")

        return {"message": "上传已取消（清理完成）"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"取消失败: {str(e)}")
