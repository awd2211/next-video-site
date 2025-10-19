"""
视频缩略图生成工具

使用 FFmpeg 从视频中提取帧作为缩略图
"""

import subprocess
import tempfile
import os
import uuid
from typing import Optional, Tuple
from loguru import logger


def generate_video_thumbnail(
    video_path: str,
    output_path: Optional[str] = None,
    timestamp: str = "00:00:01",
    width: int = 320,
    quality: int = 2
) -> Tuple[str, bytes]:
    """
    从视频生成缩略图

    Args:
        video_path: 视频文件路径（本地文件系统路径）
        output_path: 输出路径（如果为None则使用临时文件）
        timestamp: 提取帧的时间戳，格式: HH:MM:SS 或 SS
        width: 缩略图宽度（像素），高度自动计算保持比例
        quality: JPEG 质量 (1-31, 数字越小质量越高)

    Returns:
        (output_path, thumbnail_bytes): 输出路径和缩略图二进制数据

    Raises:
        Exception: FFmpeg 执行失败
    """

    # 如果没有指定输出路径，使用临时文件
    if output_path is None:
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"thumbnail_{uuid.uuid4().hex}.jpg")

    try:
        # FFmpeg 命令
        # -ss: 跳转到指定时间戳
        # -i: 输入文件
        # -vframes 1: 只提取一帧
        # -vf scale: 缩放到指定宽度，高度自动计算(-1)
        # -q:v: JPEG 质量
        cmd = [
            "ffmpeg",
            "-ss", timestamp,  # 跳转到指定时间
            "-i", video_path,  # 输入视频
            "-vframes", "1",   # 只提取1帧
            "-vf", f"scale={width}:-1",  # 缩放
            "-q:v", str(quality),  # 质量
            "-y",  # 覆盖输出文件
            output_path
        ]

        logger.debug(f"Generating thumbnail: {' '.join(cmd)}")

        # 执行 FFmpeg
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30  # 30秒超时
        )

        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='ignore')
            logger.error(f"FFmpeg failed: {error_msg}")
            raise Exception(f"FFmpeg 执行失败: {error_msg[:200]}")

        # 读取生成的缩略图
        with open(output_path, "rb") as f:
            thumbnail_bytes = f.read()

        logger.info(f"Thumbnail generated: {output_path} ({len(thumbnail_bytes)} bytes)")

        return output_path, thumbnail_bytes

    except subprocess.TimeoutExpired:
        logger.error(f"FFmpeg timeout for video: {video_path}")
        raise Exception("视频缩略图生成超时")
    except Exception as e:
        logger.error(f"Failed to generate thumbnail for {video_path}: {e}")
        raise


async def generate_and_upload_thumbnail(
    video_local_path: str,
    video_object_name: str,
    minio_client,
    timestamp: str = "00:00:01",
    width: int = 640
) -> Tuple[str, str]:
    """
    生成视频缩略图并上传到 MinIO

    Args:
        video_local_path: 本地视频文件路径
        video_object_name: MinIO 中视频的对象名称 (如: media/xxx.mp4)
        minio_client: MinIO 客户端实例
        timestamp: 提取帧的时间戳
        width: 缩略图宽度

    Returns:
        (thumbnail_path, thumbnail_url): MinIO 中的路径和访问URL

    Raises:
        Exception: 缩略图生成或上传失败
    """

    thumbnail_local_path = None

    try:
        # 1. 生成缩略图
        thumbnail_local_path, thumbnail_bytes = generate_video_thumbnail(
            video_path=video_local_path,
            timestamp=timestamp,
            width=width,
            quality=2
        )

        # 2. 生成 MinIO 对象名称
        # 将 media/xxx.mp4 转换为 thumbnails/xxx.jpg
        base_name = os.path.splitext(os.path.basename(video_object_name))[0]
        thumbnail_object_name = f"thumbnails/{base_name}.jpg"

        # 3. 上传到 MinIO
        minio_client.upload_file(
            file_content=thumbnail_bytes,
            object_name=thumbnail_object_name,
            content_type="image/jpeg"
        )

        # 4. 获取访问 URL
        thumbnail_url = minio_client.get_file_url(thumbnail_object_name)

        logger.info(f"Thumbnail uploaded: {thumbnail_object_name} -> {thumbnail_url}")

        return thumbnail_object_name, thumbnail_url

    finally:
        # 清理临时文件
        if thumbnail_local_path and os.path.exists(thumbnail_local_path):
            try:
                os.remove(thumbnail_local_path)
                logger.debug(f"Cleaned up temp thumbnail: {thumbnail_local_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temp thumbnail: {e}")
