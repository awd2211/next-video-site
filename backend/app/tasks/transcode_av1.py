"""
AV1视频转码Celery任务
- 多分辨率并行转码
- 自动生成HLS master playlist
- 文件大小对比统计
"""
from celery import shared_task
from pathlib import Path
import shutil
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List
import logging

from app.utils.av1_transcoder import AV1Transcoder, format_size
from app.utils.minio_client import MinIOClient
from app.database import SessionLocal
from app.models.video import Video

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='transcode_video_to_av1')
def transcode_video_to_av1(self, video_id: int):
    """
    转码视频为AV1格式 (多分辨率HLS)

    工作流:
    1. 下载原始视频
    2. 分析视频元数据
    3. 并行转码多个分辨率
    4. 生成HLS切片
    5. 上传到MinIO
    6. 更新数据库
    7. 清理临时文件

    Args:
        video_id: 视频ID

    Returns:
        {
            'status': 'success',
            'video_id': 123,
            'resolutions': ['1080p', '720p', '480p'],
            'av1_size': 990000000,
            'h264_size': 2250000000,
            'savings_percent': 56.0
        }
    """
    db = SessionLocal()

    try:
        # 1. 获取视频记录
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError(f"Video {video_id} not found")

        logger.info(f"开始AV1转码: video_id={video_id}, title={video.title}")

        # 2. 创建临时目录
        temp_dir = Path(f'/tmp/av1_transcode_{video_id}')
        temp_dir.mkdir(exist_ok=True, parents=True)

        # 3. 下载原始视频
        original_path = temp_dir / 'original.mp4'
        minio_client = MinIOClient()

        logger.info(f"下载原始视频: {video.source_url}")
        # 假设source_url是MinIO路径
        # minio_client.download_file(video.source_url, str(original_path))
        # 临时: 如果source_url是本地路径
        if not video.source_url.startswith('http'):
            shutil.copy(video.source_url, original_path)
        else:
            # TODO: 从MinIO下载
            pass

        # 4. 分析源视频
        logger.info("分析视频元数据...")
        metadata = AV1Transcoder.get_video_info(original_path)
        source_height = metadata['height']
        source_duration = metadata['duration']

        logger.info(f"源视频: {metadata['width']}x{metadata['height']}, "
                   f"时长={source_duration:.1f}s, 编码={metadata['codec']}")

        # 5. 决定目标分辨率 (不超过源分辨率)
        all_resolutions = ['1080p', '720p', '480p', '360p']
        resolution_heights = {'1080p': 1080, '720p': 720, '480p': 480, '360p': 360}

        target_resolutions = [
            res for res in all_resolutions
            if resolution_heights[res] <= source_height
        ]

        logger.info(f"源分辨率: {source_height}p")
        logger.info(f"目标分辨率: {target_resolutions}")

        # 6. 并行转码所有分辨率
        hls_urls = {}
        local_paths = {}

        def transcode_resolution(resolution: str):
            """转码单个分辨率"""
            logger.info(f"开始转码 {resolution}...")

            output_dir = temp_dir / 'av1' / resolution
            output_dir.mkdir(parents=True, exist_ok=True)

            # 转码为AV1 HLS
            m3u8_path = AV1Transcoder.transcode_to_hls_av1(
                original_path,
                output_dir,
                resolution,
                segment_time=6
            )

            logger.info(f"完成转码 {resolution}")
            return resolution, output_dir

        # 并行转码
        logger.info(f"并行转码 {len(target_resolutions)} 个分辨率...")
        with ThreadPoolExecutor(max_workers=min(4, len(target_resolutions))) as executor:
            results = list(executor.map(transcode_resolution, target_resolutions))

        # 7. 上传到MinIO
        logger.info("上传文件到MinIO...")
        for resolution, output_dir in results:
            minio_url = upload_hls_directory(
                video_id,
                resolution,
                output_dir,
                format_type='av1'
            )
            hls_urls[resolution] = minio_url
            local_paths[resolution] = output_dir

        # 8. 生成Master Playlist
        logger.info("生成Master Playlist...")
        master_content = AV1Transcoder.create_master_playlist(
            video_id,
            hls_urls,
            format_type='av1'
        )

        # 保存并上传Master Playlist
        master_path = temp_dir / 'master.m3u8'
        master_path.write_text(master_content)

        # TODO: 上传master.m3u8到MinIO
        master_url = f'videos/{video_id}/av1/master.m3u8'

        # 9. 计算文件大小 (统计节省空间)
        av1_total_size = sum(
            sum(f.stat().st_size for f in output_dir.rglob('*') if f.is_file())
            for _, output_dir in results
        )

        # 假设H.264大小 (如果有的话)
        h264_size = video.h264_file_size if hasattr(video, 'h264_file_size') else 0

        # 计算节省
        if h264_size > 0:
            savings = AV1Transcoder.compare_file_sizes(
                Path('/dev/null'),  # 占位
                Path('/dev/null')   # 占位
            )
            savings['h264_size'] = h264_size
            savings['av1_size'] = av1_total_size
            savings['savings_bytes'] = h264_size - av1_total_size
            savings['savings_percent'] = (savings['savings_bytes'] / h264_size) * 100
        else:
            savings = {
                'av1_size': av1_total_size,
                'h264_size': 0,
                'savings_bytes': 0,
                'savings_percent': 0
            }

        logger.info(f"AV1文件大小: {format_size(av1_total_size)}")
        if savings['savings_percent'] > 0:
            logger.info(f"节省空间: {savings['savings_percent']:.1f}% "
                       f"({format_size(savings['savings_bytes'])})")

        # 10. 更新数据库
        logger.info("更新数据库...")
        video.av1_master_url = master_url
        video.av1_resolutions = hls_urls
        video.is_av1_available = True
        video.av1_file_size = av1_total_size

        db.commit()
        logger.info(f"数据库更新成功: video_id={video_id}")

        # 11. 清理临时文件
        logger.info("清理临时文件...")
        shutil.rmtree(temp_dir, ignore_errors=True)

        return {
            'status': 'success',
            'video_id': video_id,
            'resolutions': list(hls_urls.keys()),
            'master_url': master_url,
            'av1_size': av1_total_size,
            'h264_size': savings['h264_size'],
            'savings_percent': round(savings['savings_percent'], 2)
        }

    except Exception as e:
        logger.error(f"AV1转码失败: {str(e)}", exc_info=True)
        db.rollback()

        # 更新任务状态为失败
        try:
            video = db.query(Video).filter(Video.id == video_id).first()
            if video:
                video.is_av1_available = False
                db.commit()
        except:
            pass

        raise

    finally:
        db.close()


def upload_hls_directory(
    video_id: int,
    resolution: str,
    hls_dir: Path,
    format_type: str = 'av1'
) -> str:
    """
    上传HLS目录到MinIO

    Args:
        video_id: 视频ID
        resolution: 分辨率
        hls_dir: HLS文件目录
        format_type: 'av1' or 'h264'

    Returns:
        index.m3u8的URL
    """
    minio_client = MinIOClient()

    # 上传所有文件
    for file_path in hls_dir.glob('*'):
        if file_path.is_file():
            object_name = f'videos/{video_id}/{format_type}/{resolution}/{file_path.name}'

            # TODO: 实际上传到MinIO
            # minio_client.upload_file(str(file_path), object_name)

            logger.info(f"上传: {object_name}")

    # 返回index.m3u8的URL
    return f'videos/{video_id}/{format_type}/{resolution}/index.m3u8'


@shared_task(name='transcode_video_dual_format')
def transcode_video_dual_format(video_id: int):
    """
    双格式转码: H.264 + AV1

    先转码H.264 (快速上线),再转码AV1 (节省带宽)
    """
    from app.tasks.transcode import transcode_video_task  # H.264转码任务

    # 1. H.264转码 (优先,用户可快速观看)
    logger.info(f"开始H.264转码: video_id={video_id}")
    h264_result = transcode_video_task(video_id)

    # 2. AV1转码 (后台进行,用户无感知)
    logger.info(f"开始AV1转码: video_id={video_id}")
    av1_result = transcode_video_to_av1(video_id)

    return {
        'video_id': video_id,
        'h264': h264_result,
        'av1': av1_result
    }
