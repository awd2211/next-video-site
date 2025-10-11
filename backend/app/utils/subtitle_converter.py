"""
字幕格式转换工具 - SRT 转 VTT

Video.js原生只支持WebVTT格式,需要将SRT转换为VTT

支持的编码:
- UTF-8 (推荐)
- UTF-8 with BOM
- GBK/GB2312 (中文简体)
- Big5 (中文繁体)
- ISO-8859-1 (Latin-1)

支持的格式转换:
- SRT → VTT ✅
- VTT → SRT (待实现)
- ASS → VTT (待实现)
"""

import logging
import re
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger(__name__)


class SubtitleConverter:
    """字幕转换器"""

    @staticmethod
    def detect_encoding(file_path: Union[str, Path]) -> str:
        """
        检测文件编码

        Args:
            file_path: 文件路径

        Returns:
            检测到的编码 (utf-8, gbk, big5, etc.)
        """
        file_path = Path(file_path)

        # 读取文件前4096字节用于检测
        with open(file_path, "rb") as f:
            raw_data = f.read(4096)

        # 检测BOM
        if raw_data.startswith(b"\xef\xbb\xbf"):
            return "utf-8-sig"
        elif raw_data.startswith(b"\xff\xfe"):
            return "utf-16-le"
        elif raw_data.startswith(b"\xfe\xff"):
            return "utf-16-be"

        # 尝试常见编码
        for encoding in ["utf-8", "gbk", "gb2312", "big5", "iso-8859-1"]:
            try:
                raw_data.decode(encoding)
                logger.info(f"检测到编码: {encoding}")
                return encoding
            except (UnicodeDecodeError, LookupError):
                continue

        # 默认使用UTF-8
        logger.warning("无法检测编码,默认使用UTF-8")
        return "utf-8"

    @staticmethod
    def srt_to_vtt(srt_content: str) -> str:
        """
        将SRT字幕转换为VTT格式

        SRT格式示例:
        1
        00:00:00,000 --> 00:00:02,000
        Hello World

        VTT格式示例:
        WEBVTT

        00:00:00.000 --> 00:00:02.000
        Hello World

        Args:
            srt_content: SRT字幕内容

        Returns:
            VTT字幕内容
        """
        # VTT文件必须以WEBVTT开头
        vtt_content = "WEBVTT\n\n"

        # 将逗号替换为点号 (SRT使用逗号作为毫秒分隔符,VTT使用点号)
        # 00:00:00,000 -> 00:00:00.000
        vtt_content += re.sub(r"(\d{2}:\d{2}:\d{2}),(\d{3})", r"\1.\2", srt_content)

        return vtt_content

    @staticmethod
    def srt_file_to_vtt_file(
        srt_path: Union[str, Path],
        vtt_path: Union[str, Path] = None,
        encoding: Optional[str] = None,
    ) -> Path:
        """
        将SRT文件转换为VTT文件 (自动检测编码)

        Args:
            srt_path: SRT文件路径
            vtt_path: VTT输出路径 (可选,默认为同名.vtt文件)
            encoding: 指定编码 (可选,默认自动检测)

        Returns:
            VTT文件路径

        Raises:
            FileNotFoundError: SRT文件不存在
            UnicodeDecodeError: 编码错误
        """
        srt_path = Path(srt_path)

        if not srt_path.exists():
            raise FileNotFoundError(f"SRT文件不存在: {srt_path}")

        # 自动检测编码
        if encoding is None:
            encoding = SubtitleConverter.detect_encoding(srt_path)
            logger.info(f"使用编码: {encoding}")

        # 读取SRT内容 (支持多种编码)
        try:
            with open(srt_path, "r", encoding=encoding, errors="replace") as f:
                srt_content = f.read()
        except Exception as e:
            logger.error(f"读取SRT文件失败: {e}")
            # Fallback: 使用UTF-8并忽略错误
            with open(srt_path, "r", encoding="utf-8", errors="ignore") as f:
                srt_content = f.read()
            logger.warning("使用UTF-8 fallback读取,部分字符可能丢失")

        # 转换为VTT
        vtt_content = SubtitleConverter.srt_to_vtt(srt_content)

        # 确定输出路径
        if vtt_path is None:
            vtt_path = srt_path.with_suffix(".vtt")
        else:
            vtt_path = Path(vtt_path)

        # 写入VTT文件 (始终使用UTF-8)
        try:
            vtt_path.parent.mkdir(parents=True, exist_ok=True)
            with open(vtt_path, "w", encoding="utf-8") as f:
                f.write(vtt_content)
        except Exception as e:
            logger.error(f"写入VTT文件失败: {e}")
            raise

        file_size = vtt_path.stat().st_size
        logger.info(f"✅ SRT已转换为VTT: {srt_path} -> {vtt_path} ({file_size} bytes)")

        return vtt_path

    @staticmethod
    def convert_subtitle_format(
        input_path: Union[str, Path], output_format: str = "vtt"
    ) -> Path:
        """
        通用字幕格式转换

        Args:
            input_path: 输入字幕文件路径
            output_format: 目标格式 (vtt, srt)

        Returns:
            输出文件路径
        """
        input_path = Path(input_path)
        input_format = input_path.suffix.lower().lstrip(".")

        if input_format == output_format:
            logger.info(f"字幕已经是{output_format}格式,无需转换")
            return input_path

        if input_format == "srt" and output_format == "vtt":
            return SubtitleConverter.srt_file_to_vtt_file(input_path)
        else:
            raise NotImplementedError(
                f"暂不支持 {input_format} -> {output_format} 转换"
            )


# 便捷函数
def srt_to_vtt(srt_content: str) -> str:
    """快捷函数: SRT内容转VTT"""
    return SubtitleConverter.srt_to_vtt(srt_content)


def convert_subtitle_file(input_path: str, output_format: str = "vtt") -> Path:
    """快捷函数: 字幕文件转换"""
    return SubtitleConverter.convert_subtitle_format(input_path, output_format)
