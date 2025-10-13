"""
视频哈希和重复检测工具
使用多种方法检测重复视频
"""

import hashlib
import io
from typing import Optional, Tuple

from loguru import logger


def calculate_file_hash(file_content: bytes, algorithm: str = "md5") -> str:
    """
    计算文件的哈希值

    Args:
        file_content: 文件字节内容
        algorithm: 哈希算法 (md5, sha1, sha256)

    Returns:
        str: 十六进制哈希值
    """
    if algorithm == "md5":
        hasher = hashlib.md5()
    elif algorithm == "sha1":
        hasher = hashlib.sha1()
    elif algorithm == "sha256":
        hasher = hashlib.sha256()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    hasher.update(file_content)
    return hasher.hexdigest()


def calculate_partial_hash(file_content: bytes, chunk_size: int = 65536) -> str:
    """
    计算文件的部分哈希值（头部+尾部）
    这对大文件更快，且能检测大多数重复

    Args:
        file_content: 文件字节内容
        chunk_size: 每个块的大小（字节）

    Returns:
        str: MD5 哈希值
    """
    hasher = hashlib.md5()

    # 计算头部
    hasher.update(file_content[:chunk_size])

    # 如果文件足够大，也计算尾部
    if len(file_content) > chunk_size * 2:
        hasher.update(file_content[-chunk_size:])

    return hasher.hexdigest()


def calculate_streaming_hash(
    file_stream: io.BytesIO, algorithm: str = "md5", chunk_size: int = 8192
) -> str:
    """
    流式计算文件哈希（适用于大文件）

    Args:
        file_stream: 文件流对象
        algorithm: 哈希算法
        chunk_size: 读取块大小

    Returns:
        str: 哈希值
    """
    if algorithm == "md5":
        hasher = hashlib.md5()
    elif algorithm == "sha1":
        hasher = hashlib.sha1()
    elif algorithm == "sha256":
        hasher = hashlib.sha256()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    # 重置指针到开始
    file_stream.seek(0)

    # 分块读取并更新哈希
    while True:
        chunk = file_stream.read(chunk_size)
        if not chunk:
            break
        hasher.update(chunk)

    # 重置指针
    file_stream.seek(0)

    return hasher.hexdigest()


def calculate_metadata_hash(
    title: str,
    duration: Optional[int] = None,
    file_size: Optional[int] = None,
) -> str:
    """
    基于元数据计算哈希
    用于检测相似或重新上传的视频

    Args:
        title: 视频标题
        duration: 视频时长（秒）
        file_size: 文件大小（字节）

    Returns:
        str: MD5 哈希值
    """
    hasher = hashlib.md5()

    # 标准化标题（移除空格、转小写）
    normalized_title = title.lower().strip().replace(" ", "")
    hasher.update(normalized_title.encode("utf-8"))

    if duration:
        hasher.update(str(duration).encode("utf-8"))

    if file_size:
        hasher.update(str(file_size).encode("utf-8"))

    return hasher.hexdigest()


def calculate_perceptual_hash_from_frames(
    frame_data: list[bytes], sample_size: int = 8
) -> str:
    """
    从视频帧计算感知哈希
    这可以检测经过轻微编辑的视频

    Args:
        frame_data: 视频帧字节数据列表
        sample_size: 采样大小

    Returns:
        str: 感知哈希字符串

    Note:
        这是一个简化版本，实际实现需要使用 OpenCV 或 imagehash 库
        来提取关键帧并计算感知哈希
    """
    # 简化实现：对所有帧数据计算哈希
    hasher = hashlib.md5()

    for frame in frame_data[:sample_size]:
        hasher.update(frame)

    return hasher.hexdigest()


def compare_hashes(hash1: str, hash2: str) -> bool:
    """
    比较两个哈希值是否相同

    Args:
        hash1: 第一个哈希
        hash2: 第二个哈希

    Returns:
        bool: 是否相同
    """
    return hash1.lower() == hash2.lower()


def calculate_video_fingerprint(
    file_content: bytes,
    title: str,
    duration: Optional[int] = None,
) -> dict:
    """
    计算视频的完整指纹
    包含多种哈希方法的结果

    Args:
        file_content: 文件字节内容
        title: 视频标题
        duration: 视频时长

    Returns:
        dict: 包含多种哈希值的字典
    """
    try:
        file_size = len(file_content)

        fingerprint = {
            "file_hash_md5": calculate_file_hash(file_content, "md5"),
            "file_hash_sha256": calculate_file_hash(file_content, "sha256"),
            "partial_hash": calculate_partial_hash(file_content),
            "metadata_hash": calculate_metadata_hash(title, duration, file_size),
            "file_size": file_size,
        }

        return fingerprint

    except Exception as e:
        logger.error(f"计算视频指纹失败: {e}", exc_info=True)
        raise


async def check_duplicate_video(
    db,
    file_hash: str,
    partial_hash: Optional[str] = None,
    metadata_hash: Optional[str] = None,
) -> Tuple[bool, Optional[int]]:
    """
    检查数据库中是否存在重复视频

    Args:
        db: 数据库会话
        file_hash: 完整文件哈希
        partial_hash: 部分文件哈希
        metadata_hash: 元数据哈希

    Returns:
        Tuple[bool, Optional[int]]: (是否重复, 重复视频的ID)
    """
    from sqlalchemy import or_, select

    from app.models.video import Video

    # 构建查询条件
    conditions = []

    if file_hash:
        conditions.append(Video.file_hash == file_hash)
    if partial_hash:
        conditions.append(Video.partial_hash == partial_hash)
    if metadata_hash:
        conditions.append(Video.metadata_hash == metadata_hash)

    if not conditions:
        return False, None

    # 查询数据库
    query = select(Video).filter(or_(*conditions)).limit(1)
    result = await db.execute(query)
    duplicate = result.scalar_one_or_none()

    if duplicate:
        return True, duplicate.id

    return False, None
