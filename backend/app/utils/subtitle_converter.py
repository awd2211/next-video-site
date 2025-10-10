"""
字幕格式转换工具 - SRT 转 VTT

Video.js原生只支持WebVTT格式,需要将SRT转换为VTT
"""

import re
from pathlib import Path
from typing import Union
import logging

logger = logging.getLogger(__name__)


class SubtitleConverter:
    """字幕转换器"""

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
        vtt_content += re.sub(
            r'(\d{2}:\d{2}:\d{2}),(\d{3})',
            r'\1.\2',
            srt_content
        )

        return vtt_content

    @staticmethod
    def srt_file_to_vtt_file(
        srt_path: Union[str, Path],
        vtt_path: Union[str, Path] = None
    ) -> Path:
        """
        将SRT文件转换为VTT文件

        Args:
            srt_path: SRT文件路径
            vtt_path: VTT输出路径 (可选,默认为同名.vtt文件)

        Returns:
            VTT文件路径
        """
        srt_path = Path(srt_path)

        if not srt_path.exists():
            raise FileNotFoundError(f"SRT文件不存在: {srt_path}")

        # 读取SRT内容
        with open(srt_path, 'r', encoding='utf-8') as f:
            srt_content = f.read()

        # 转换为VTT
        vtt_content = SubtitleConverter.srt_to_vtt(srt_content)

        # 确定输出路径
        if vtt_path is None:
            vtt_path = srt_path.with_suffix('.vtt')
        else:
            vtt_path = Path(vtt_path)

        # 写入VTT文件
        vtt_path.parent.mkdir(parents=True, exist_ok=True)
        with open(vtt_path, 'w', encoding='utf-8') as f:
            f.write(vtt_content)

        logger.info(f"✅ SRT已转换为VTT: {srt_path} -> {vtt_path}")

        return vtt_path

    @staticmethod
    def convert_subtitle_format(
        input_path: Union[str, Path],
        output_format: str = 'vtt'
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
        input_format = input_path.suffix.lower().lstrip('.')

        if input_format == output_format:
            logger.info(f"字幕已经是{output_format}格式,无需转换")
            return input_path

        if input_format == 'srt' and output_format == 'vtt':
            return SubtitleConverter.srt_file_to_vtt_file(input_path)
        else:
            raise NotImplementedError(
                f"暂不支持 {input_format} -> {output_format} 转换"
            )


# 便捷函数
def srt_to_vtt(srt_content: str) -> str:
    """快捷函数: SRT内容转VTT"""
    return SubtitleConverter.srt_to_vtt(srt_content)


def convert_subtitle_file(input_path: str, output_format: str = 'vtt') -> Path:
    """快捷函数: 字幕文件转换"""
    return SubtitleConverter.convert_subtitle_format(input_path, output_format)
