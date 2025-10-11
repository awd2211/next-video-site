"""
文件上传安全验证工具
防止恶意文件上传、文件类型伪造等攻击
"""

import io
import mimetypes
import re
from typing import Tuple, List, Optional
from fastapi import UploadFile, HTTPException, status


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


# 文件魔数（文件头）映射
FILE_MAGIC_NUMBERS = {
    # 图片格式
    "image/jpeg": [
        bytes.fromhex("FFD8FF"),  # JPEG
    ],
    "image/png": [
        bytes.fromhex("89504E470D0A1A0A"),  # PNG
    ],
    "image/gif": [
        bytes.fromhex("474946383961"),  # GIF89a
        bytes.fromhex("474946383761"),  # GIF87a
    ],
    "image/webp": [
        bytes.fromhex("52494646"),  # RIFF (WebP的前4字节)
    ],
    # 视频格式
    "video/mp4": [
        bytes.fromhex("00000018667479706D703432"),  # MP4
        bytes.fromhex("00000020667479706973"),  # MP4 ISO
    ],
    "video/x-matroska": [
        bytes.fromhex("1A45DFA3"),  # MKV
    ],
    "video/x-msvideo": [
        bytes.fromhex("52494646"),  # AVI (RIFF)
    ],
    "video/quicktime": [
        bytes.fromhex("0000001466747970"),  # MOV
    ],
}


def check_file_magic(file_content: bytes, expected_mime: str) -> bool:
    """
    检查文件魔数（文件头）是否匹配MIME类型

    Args:
        file_content: 文件内容（至少前64字节）
        expected_mime: 期望的MIME类型

    Returns:
        是否匹配
    """
    if expected_mime not in FILE_MAGIC_NUMBERS:
        # 未知类型，跳过魔数检查
        return True

    magic_numbers = FILE_MAGIC_NUMBERS[expected_mime]

    for magic in magic_numbers:
        if file_content.startswith(magic):
            return True
        # WebP特殊处理：RIFF后面应该跟WEBP
        if expected_mime == "image/webp" and file_content[8:12] == b"WEBP":
            return True

    return False


def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名

    Args:
        filename: 文件名

    Returns:
        小写扩展名（包含点号，如.jpg）
    """
    if not filename or "." not in filename:
        return ""

    return "." + filename.rsplit(".", 1)[-1].lower()


async def validate_upload_file(
    file: UploadFile,
    allowed_extensions: List[str],
    allowed_mimes: List[str],
    max_size: int,
    check_magic: bool = True,
) -> Tuple[bytes, str]:
    """
    全面验证上传文件

    Args:
        file: 上传的文件
        allowed_extensions: 允许的扩展名列表 (如 ['.jpg', '.png'])
        allowed_mimes: 允许的MIME类型列表
        max_size: 最大文件大小（字节）
        check_magic: 是否检查文件魔数

    Returns:
        (file_content, extension): 文件内容和扩展名

    Raises:
        HTTPException: 如果验证失败
    """
    # 1. 检查文件名
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="文件名无效"
        )

    # 2. 检查扩展名
    ext = get_file_extension(file.filename)
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，仅支持: {', '.join(allowed_extensions)}",
        )

    # 3. 读取文件内容
    file_content = await file.read()
    file_size = len(file_content)

    # 4. 检查文件大小
    if file_size == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件为空")

    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件过大，最大允许 {max_size // (1024*1024)}MB",
        )

    # 5. 检查MIME类型（Content-Type头）
    if file.content_type not in allowed_mimes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的MIME类型: {file.content_type}",
        )

    # 6. 检查文件魔数（防止类型伪造）
    if check_magic:
        if not check_file_magic(file_content[:64], file.content_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件内容与声明的类型不匹配，可能是伪造的文件",
            )

    return file_content, ext


# 预定义的验证配置
class FileValidationPresets:
    """文件验证预设配置"""

    # 图片验证
    IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]
    IMAGE_MIMES = ["image/jpeg", "image/png", "image/webp"]
    IMAGE_MAX_SIZE = 10 * 1024 * 1024  # 10MB

    # 视频验证
    VIDEO_EXTENSIONS = [".mp4", ".avi", ".mkv", ".mov", ".flv"]
    VIDEO_MIMES = [
        "video/mp4",
        "video/x-msvideo",
        "video/x-matroska",
        "video/quicktime",
        "video/x-flv",
    ]
    VIDEO_MAX_SIZE = 5 * 1024 * 1024 * 1024  # 5GB

    # 字幕验证
    SUBTITLE_EXTENSIONS = [".srt", ".vtt", ".ass"]
    SUBTITLE_MIMES = ["text/plain", "text/vtt", "application/x-subrip"]
    SUBTITLE_MAX_SIZE = 5 * 1024 * 1024  # 5MB

    @staticmethod
    async def validate_image(file: UploadFile) -> Tuple[bytes, str]:
        """验证图片文件"""
        return await validate_upload_file(
            file,
            FileValidationPresets.IMAGE_EXTENSIONS,
            FileValidationPresets.IMAGE_MIMES,
            FileValidationPresets.IMAGE_MAX_SIZE,
            check_magic=True,
        )

    @staticmethod
    async def validate_video(file: UploadFile) -> Tuple[bytes, str]:
        """验证视频文件"""
        return await validate_upload_file(
            file,
            FileValidationPresets.VIDEO_EXTENSIONS,
            FileValidationPresets.VIDEO_MIMES,
            FileValidationPresets.VIDEO_MAX_SIZE,
            check_magic=False,  # 视频魔数检查较复杂，暂时跳过
        )

    @staticmethod
    async def validate_subtitle(file: UploadFile) -> Tuple[bytes, str]:
        """验证字幕文件"""
        return await validate_upload_file(
            file,
            FileValidationPresets.SUBTITLE_EXTENSIONS,
            FileValidationPresets.SUBTITLE_MIMES,
            FileValidationPresets.SUBTITLE_MAX_SIZE,
            check_magic=False,  # 文本文件无需魔数检查
        )
