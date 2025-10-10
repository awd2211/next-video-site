"""
图片处理工具
功能:
- 图片压缩
- 尺寸调整
- 格式转换
- 生成多种尺寸缩略图
- WebP转换
"""
from PIL import Image
import io
from typing import Tuple, Optional, BinaryIO
import os


class ImageProcessor:
    """图片处理器"""

    # 预设尺寸
    THUMBNAIL_SIZES = {
        "small": (320, 180),      # 小缩略图
        "medium": (640, 360),     # 中等缩略图
        "large": (1280, 720),     # 大缩略图
        "poster_small": (200, 300),   # 海报小图
        "poster_medium": (400, 600),  # 海报中图
        "poster_large": (800, 1200),  # 海报大图
    }

    # 质量设置
    QUALITY_SETTINGS = {
        "low": 60,
        "medium": 75,
        "high": 85,
        "original": 95,
    }

    @staticmethod
    def compress_image(
        image_file: BinaryIO,
        max_size: Tuple[int, int] = (1920, 1080),
        quality: str = "medium",
        output_format: str = "JPEG",
    ) -> io.BytesIO:
        """
        压缩图片

        Args:
            image_file: 图片文件对象
            max_size: 最大尺寸 (width, height)
            quality: 质量等级 (low, medium, high, original)
            output_format: 输出格式 (JPEG, PNG, WEBP)

        Returns:
            压缩后的图片BytesIO对象
        """
        # 打开图片
        img = Image.open(image_file)

        # 转换RGBA到RGB (JPEG不支持透明度)
        if img.mode in ("RGBA", "LA", "P"):
            if output_format == "JPEG":
                # 创建白色背景
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = background
            else:
                img = img.convert("RGBA")

        # 调整尺寸 (保持宽高比)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # 压缩质量
        quality_value = ImageProcessor.QUALITY_SETTINGS.get(quality, 75)

        # 保存到BytesIO
        output = io.BytesIO()
        save_kwargs = {"format": output_format, "quality": quality_value}

        if output_format == "JPEG":
            save_kwargs["optimize"] = True
            save_kwargs["progressive"] = True  # 渐进式JPEG
        elif output_format == "WEBP":
            save_kwargs["method"] = 6  # 压缩方法 (0-6, 6最慢但最好)

        img.save(output, **save_kwargs)
        output.seek(0)

        return output

    @staticmethod
    def create_thumbnails(
        image_file: BinaryIO,
        sizes: list[str] = ["small", "medium", "large"],
        output_format: str = "WEBP",
    ) -> dict[str, io.BytesIO]:
        """
        生成多种尺寸的缩略图

        Args:
            image_file: 原始图片
            sizes: 尺寸列表 (使用预设尺寸名称)
            output_format: 输出格式

        Returns:
            {size_name: BytesIO} 字典
        """
        img = Image.open(image_file)

        if img.mode in ("RGBA", "LA", "P") and output_format == "JPEG":
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = background

        thumbnails = {}

        for size_name in sizes:
            if size_name not in ImageProcessor.THUMBNAIL_SIZES:
                continue

            target_size = ImageProcessor.THUMBNAIL_SIZES[size_name]

            # 复制图片以免影响原图
            thumb_img = img.copy()
            thumb_img.thumbnail(target_size, Image.Resampling.LANCZOS)

            # 保存
            output = io.BytesIO()
            save_kwargs = {"format": output_format, "quality": 85}

            if output_format == "WEBP":
                save_kwargs["method"] = 6

            thumb_img.save(output, **save_kwargs)
            output.seek(0)

            thumbnails[size_name] = output

        return thumbnails

    @staticmethod
    def convert_to_webp(image_file: BinaryIO, quality: int = 85) -> io.BytesIO:
        """
        转换为WebP格式 (更高压缩率)

        Args:
            image_file: 原始图片
            quality: 质量 (0-100)

        Returns:
            WebP格式的BytesIO
        """
        img = Image.open(image_file)

        # WebP支持透明度
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if img.mode in ("RGBA", "LA", "P") else "RGB")

        output = io.BytesIO()
        img.save(output, format="WEBP", quality=quality, method=6)
        output.seek(0)

        return output

    @staticmethod
    def get_image_info(image_file: BinaryIO) -> dict:
        """
        获取图片信息

        Returns:
            {
                "format": "JPEG",
                "mode": "RGB",
                "width": 1920,
                "height": 1080,
                "size_bytes": 123456
            }
        """
        image_file.seek(0)
        img = Image.open(image_file)
        image_file.seek(0, os.SEEK_END)
        size_bytes = image_file.tell()
        image_file.seek(0)

        return {
            "format": img.format,
            "mode": img.mode,
            "width": img.width,
            "height": img.height,
            "size_bytes": size_bytes,
        }

    @staticmethod
    def should_compress(image_file: BinaryIO, threshold_mb: float = 1.0) -> bool:
        """
        判断是否需要压缩

        Args:
            image_file: 图片文件
            threshold_mb: 阈值 (MB)

        Returns:
            bool
        """
        info = ImageProcessor.get_image_info(image_file)
        size_mb = info["size_bytes"] / (1024 * 1024)
        return size_mb > threshold_mb
