"""
AV1视频转码工具类
使用dav1d解码器 + SVT-AV1编码器
"""
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)


class AV1Transcoder:
    """
    AV1视频转码器
    - 解码器: libdav1d (世界最快)
    - 编码器: libsvtav1 (生产级质量)
    """

    # SVT-AV1编码配置 (使用CRF模式,质量优先)
    PROFILES = {
        '1080p': {
            'resolution': '1920:1080',
            'preset': 8,             # 0-13: 速度vs质量 (8=快速高质量)
            'crf': 30,               # 质量参数 (28-32为最佳, 自动实现~56%压缩)
            'audio_bitrate': '128k',
        },
        '720p': {
            'resolution': '1280:720',
            'preset': 8,
            'crf': 32,
            'audio_bitrate': '128k',
        },
        '480p': {
            'resolution': '854:480',
            'preset': 8,
            'crf': 34,
            'audio_bitrate': '96k',
        },
        '360p': {
            'resolution': '640:360',
            'preset': 9,
            'crf': 36,
            'audio_bitrate': '96k',
        }
    }

    @staticmethod
    def get_video_info(input_path: Path) -> Dict:
        """
        获取视频元数据

        Returns:
            {
                'width': 1920,
                'height': 1080,
                'duration': 3600.0,
                'codec': 'h264',
                'bitrate': 5000000
            }
        """
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(input_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"FFprobe failed: {result.stderr}")

        data = json.loads(result.stdout)

        # 获取视频流
        video_stream = next(
            (s for s in data['streams'] if s['codec_type'] == 'video'),
            None
        )

        if not video_stream:
            raise Exception("No video stream found")

        return {
            'width': int(video_stream.get('width', 0)),
            'height': int(video_stream.get('height', 0)),
            'duration': float(data['format'].get('duration', 0)),
            'codec': video_stream.get('codec_name', 'unknown'),
            'bitrate': int(data['format'].get('bit_rate', 0)),
        }

    @staticmethod
    def transcode_to_av1(
        input_path: Path,
        output_path: Path,
        resolution: str = '1080p',
        use_gpu_decode: bool = False,
        two_pass: bool = False
    ) -> Path:
        """
        转码视频到AV1格式 (MP4容器)

        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            resolution: 目标分辨率 (1080p/720p/480p/360p)
            use_gpu_decode: 是否使用GPU加速解码
            two_pass: 是否使用两阶段编码 (更高质量,但慢2倍)

        Returns:
            输出文件路径
        """
        if resolution not in AV1Transcoder.PROFILES:
            raise ValueError(f"Invalid resolution: {resolution}")

        profile = AV1Transcoder.PROFILES[resolution]

        # 基础命令
        cmd = ['ffmpeg', '-y']

        # GPU加速解码 (可选)
        if use_gpu_decode:
            cmd.extend(['-hwaccel', 'auto'])

        # 输入文件
        cmd.extend(['-i', str(input_path)])

        # 视频编码 - SVT-AV1 (CRF模式)
        cmd.extend([
            '-c:v', 'libsvtav1',
            '-preset', str(profile['preset']),
            '-crf', str(profile['crf']),
            '-g', '240',             # Keyframe interval (8 seconds @ 30fps)
            '-pix_fmt', 'yuv420p',   # Pixel format
        ])

        # 分辨率缩放
        cmd.extend([
            '-vf', f"scale={profile['resolution']}:flags=lanczos",
        ])

        # 音频编码 - Opus (AV1推荐)
        cmd.extend([
            '-c:a', 'libopus',
            '-b:a', profile['audio_bitrate'],
        ])

        # 容器格式 - MP4
        cmd.extend([
            '-f', 'mp4',
            '-movflags', '+faststart',  # 快速启动
        ])

        # 输出文件
        cmd.append(str(output_path))

        # 执行转码
        logger.info(f"转码命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"转码失败: {result.stderr}")
            raise Exception(f"AV1转码失败: {result.stderr}")

        logger.info(f"转码成功: {output_path}")
        return output_path

    @staticmethod
    def transcode_to_hls_av1(
        input_path: Path,
        output_dir: Path,
        resolution: str = '1080p',
        segment_time: int = 6
    ) -> Path:
        """
        转码为AV1 HLS流 (用于Web播放)

        Args:
            input_path: 输入视频
            output_dir: 输出目录
            resolution: 分辨率
            segment_time: 分片时长 (秒)

        Returns:
            index.m3u8路径
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        profile = AV1Transcoder.PROFILES[resolution]

        cmd = [
            'ffmpeg', '-y',
            '-i', str(input_path),

            # 视频编码 - SVT-AV1 (CRF模式)
            '-c:v', 'libsvtav1',
            '-preset', str(profile['preset']),
            '-crf', str(profile['crf']),
            '-g', '240',
            '-pix_fmt', 'yuv420p',
            '-vf', f"scale={profile['resolution']}:flags=lanczos",

            # 音频编码
            '-c:a', 'libopus',
            '-b:a', profile['audio_bitrate'],

            # HLS配置
            '-f', 'hls',
            '-hls_time', str(segment_time),
            '-hls_playlist_type', 'vod',
            '-hls_segment_filename', str(output_dir / 'segment_%03d.ts'),
            '-hls_segment_type', 'mpegts',

            str(output_dir / 'index.m3u8')
        ]

        logger.info(f"生成HLS: {output_dir}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"HLS生成失败: {result.stderr}")
            raise Exception(f"HLS生成失败: {result.stderr}")

        return output_dir / 'index.m3u8'

    @staticmethod
    def create_master_playlist(
        video_id: int,
        resolutions: Dict[str, str],
        format_type: str = 'av1'
    ) -> str:
        """
        生成HLS Master Playlist

        Args:
            video_id: 视频ID
            resolutions: {'1080p': 'videos/123/av1/1080p/index.m3u8', ...}
            format_type: 'av1' or 'h264'

        Returns:
            Master playlist内容
        """
        playlist = "#EXTM3U\n"
        playlist += "#EXT-X-VERSION:3\n\n"

        # 分辨率配置
        resolution_configs = {
            '1080p': {'bandwidth': 2200000, 'width': 1920, 'height': 1080},
            '720p':  {'bandwidth': 1200000, 'width': 1280, 'height': 720},
            '480p':  {'bandwidth': 600000,  'width': 854,  'height': 480},
            '360p':  {'bandwidth': 400000,  'width': 640,  'height': 360},
        }

        # 编解码器声明
        # AV1: av01.0.05M.08 (Profile 0, Level 5.0, Main Tier, 8-bit)
        # H.264: avc1.64001f (High Profile, Level 3.1)
        codec = 'av01.0.05M.08,opus' if format_type == 'av1' else 'avc1.64001f,mp4a.40.2'

        # 按分辨率从高到低排序
        sorted_resolutions = sorted(
            resolutions.items(),
            key=lambda x: resolution_configs.get(x[0], {}).get('height', 0),
            reverse=True
        )

        for res, url in sorted_resolutions:
            config = resolution_configs.get(res, {})
            if not config:
                continue

            playlist += f'#EXT-X-STREAM-INF:BANDWIDTH={config["bandwidth"]},'
            playlist += f'RESOLUTION={config["width"]}x{config["height"]},'
            playlist += f'CODECS="{codec}"\n'
            playlist += f'{url}\n\n'

        return playlist

    @staticmethod
    def compare_file_sizes(h264_path: Path, av1_path: Path) -> Dict:
        """
        对比H.264和AV1文件大小

        Returns:
            {
                'h264_size': 2250000000,
                'av1_size': 990000000,
                'savings_bytes': 1260000000,
                'savings_percent': 56.0
            }
        """
        h264_size = h264_path.stat().st_size if h264_path.exists() else 0
        av1_size = av1_path.stat().st_size if av1_path.exists() else 0

        if h264_size == 0:
            return {
                'h264_size': 0,
                'av1_size': av1_size,
                'savings_bytes': 0,
                'savings_percent': 0.0
            }

        savings_bytes = h264_size - av1_size
        savings_percent = (savings_bytes / h264_size) * 100

        return {
            'h264_size': h264_size,
            'av1_size': av1_size,
            'savings_bytes': savings_bytes,
            'savings_percent': round(savings_percent, 2)
        }

    @staticmethod
    def extract_thumbnail(
        input_path: Path,
        output_path: Path,
        timestamp: float = 5.0,
        size: str = '1280x720'
    ) -> Path:
        """
        从视频中提取缩略图

        Args:
            input_path: 输入视频路径
            output_path: 输出图片路径
            timestamp: 提取位置(秒), 默认第5秒
            size: 缩略图尺寸, 默认1280x720

        Returns:
            输出图片路径

        Example:
            >>> thumbnail = AV1Transcoder.extract_thumbnail(
            ...     Path('video.mp4'),
            ...     Path('thumbnail.jpg'),
            ...     timestamp=5.0
            ... )
        """
        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # FFmpeg命令
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(timestamp),  # 跳转到指定时间
            '-i', str(input_path),
            '-vframes', '1',        # 只提取1帧
            '-vf', f'scale={size}:force_original_aspect_ratio=decrease,pad={size}:(ow-iw)/2:(oh-ih)/2',
            '-q:v', '2',            # 高质量 (1-31, 越小越好)
            str(output_path)
        ]

        logger.info(f"提取缩略图: {output_path} (时间点: {timestamp}s)")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"缩略图提取失败: {result.stderr}")
            raise Exception(f"缩略图提取失败: {result.stderr}")

        if not output_path.exists():
            raise Exception(f"缩略图文件未生成: {output_path}")

        logger.info(f"✅ 缩略图已生成: {output_path} ({format_size(output_path.stat().st_size)})")
        return output_path

    @staticmethod
    def extract_multiple_thumbnails(
        input_path: Path,
        output_dir: Path,
        count: int = 5,
        size: str = '1280x720'
    ) -> List[Path]:
        """
        提取多个缩略图 (用于悬停预览/GIF等)

        Args:
            input_path: 输入视频
            output_dir: 输出目录
            count: 提取数量
            size: 缩略图尺寸

        Returns:
            缩略图路径列表
        """
        # 获取视频时长
        info = AV1Transcoder.get_video_info(input_path)
        duration = info['duration']

        if duration < 10:
            # 视频太短,只提取1张
            count = 1

        # 均匀分布时间点
        timestamps = []
        interval = duration / (count + 1)
        for i in range(1, count + 1):
            timestamps.append(interval * i)

        # 提取缩略图
        thumbnails = []
        for i, timestamp in enumerate(timestamps):
            output_path = output_dir / f'thumbnail_{i+1}.jpg'
            try:
                thumb = AV1Transcoder.extract_thumbnail(
                    input_path,
                    output_path,
                    timestamp=timestamp,
                    size=size
                )
                thumbnails.append(thumb)
            except Exception as e:
                logger.error(f"提取第{i+1}张缩略图失败: {str(e)}")

        return thumbnails


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"
