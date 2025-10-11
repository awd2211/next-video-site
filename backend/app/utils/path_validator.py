"""
路径验证和清理工具
防止路径遍历和命令注入攻击
"""

import re
import tempfile
from pathlib import Path
from typing import Union


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除危险字符

    Args:
        filename: 原始文件名

    Returns:
        安全的文件名
    """
    # 移除路径分隔符
    filename = filename.replace("/", "_").replace("\\", "_")

    # 移除特殊字符，只保留字母、数字、点、下划线、连字符
    filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

    # 移除开头的点（隐藏文件）
    filename = filename.lstrip(".")

    # 限制长度
    if len(filename) > 255:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[:250] + ("." + ext if ext else "")

    return filename or "unnamed"


def validate_path(
    path: Union[str, Path], allowed_base: Union[str, Path] = None
) -> Path:
    """
    验证路径安全性，防止路径遍历攻击

    Args:
        path: 要验证的路径
        allowed_base: 允许的基础目录

    Returns:
        验证后的绝对路径

    Raises:
        ValueError: 如果路径不安全
    """
    path = Path(path).resolve()

    # 检查是否尝试路径遍历
    path_str = str(path)
    if ".." in path_str or path_str.startswith("/etc") or path_str.startswith("/root"):
        raise ValueError(f"不安全的路径: {path}")

    # 如果指定了允许的基础目录，检查路径是否在该目录下
    if allowed_base is not None:
        allowed_base = Path(allowed_base).resolve()
        try:
            path.relative_to(allowed_base)
        except ValueError:
            raise ValueError(f"路径不在允许的目录下: {path} (允许: {allowed_base})")

    return path


def create_safe_temp_dir(prefix: str = "temp_", suffix: str = "") -> Path:
    """
    创建安全的临时目录

    Args:
        prefix: 目录前缀
        suffix: 目录后缀

    Returns:
        临时目录路径
    """
    # 清理前缀和后缀
    prefix = sanitize_filename(prefix)
    suffix = sanitize_filename(suffix)

    # 使用tempfile创建，确保唯一性和安全性
    temp_dir = Path(tempfile.mkdtemp(prefix=prefix, suffix=suffix))
    return temp_dir


def validate_video_id(video_id: Union[int, str]) -> int:
    """
    验证视频ID是否为有效的整数

    Args:
        video_id: 视频ID

    Returns:
        验证后的整数ID

    Raises:
        ValueError: 如果不是有效的整数
    """
    try:
        vid = int(video_id)
        if vid <= 0:
            raise ValueError("视频ID必须为正整数")
        if vid > 2147483647:  # PostgreSQL INTEGER max
            raise ValueError("视频ID超出范围")
        return vid
    except (TypeError, ValueError) as e:
        raise ValueError(f"无效的视频ID: {video_id}") from e


def is_safe_url(url: str) -> bool:
    """
    检查URL是否安全（防止SSRF攻击）

    Args:
        url: 要检查的URL

    Returns:
        是否安全
    """
    if not url:
        return False

    url_lower = url.lower()

    # 只允许http和https
    if not (url_lower.startswith("http://") or url_lower.startswith("https://")):
        return False

    # 禁止访问内部IP
    blocked_patterns = [
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "10.",
        "172.16.",
        "172.17.",
        "172.18.",
        "172.19.",
        "172.20.",
        "172.21.",
        "172.22.",
        "172.23.",
        "172.24.",
        "172.25.",
        "172.26.",
        "172.27.",
        "172.28.",
        "172.29.",
        "172.30.",
        "172.31.",
        "192.168.",
        "169.254.",  # Link-local
        "[::1]",  # IPv6 localhost
        "[::ffff:127.0.0.1]",
    ]

    for pattern in blocked_patterns:
        if pattern in url_lower:
            return False

    return True
