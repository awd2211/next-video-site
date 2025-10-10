# dav1d AV1解码方案实施指南

> **VideoSite采用dav1d作为AV1解码器** - 世界最快、完全免费、56%压缩率提升

## 📋 目录

- [为什么选择dav1d](#为什么选择dav1d)
- [技术架构](#技术架构)
- [后端集成](#后端集成)
- [前端集成](#前端集成)
- [转码工作流](#转码工作流)
- [性能优化](#性能优化)
- [部署指南](#部署指南)
- [成本收益分析](#成本收益分析)

## 为什么选择dav1d

### 核心优势

| 优势 | 数据 | 说明 |
|------|------|------|
| **世界最快** | 比libaom快**11倍** | 4K AV1: dav1d 25fps vs libaom 8fps |
| **压缩率最高** | 比H.264节省**56%** | 相同质量下文件更小 |
| **完全免费** | $0专利费 | BSD-2许可证,无任何授权费用 |
| **全球采用** | 100%主流平台 | Android 12+/iOS/Chrome/Firefox/Safari |
| **功耗更低** | 节省40% | 相比H.264软解 |

### 与H.264对比

**存储成本对比** (1小时1080p视频):
```
H.264: 5 Mbps × 3600s = 2.25 GB
AV1:   2.2 Mbps × 3600s = 0.99 GB  ← 节省56%存储! 💰

1000部视频存储成本:
H.264: 2250 GB × $0.02/GB/月 = $45/月
AV1:   990 GB × $0.02/GB/月 = $19.8/月
年节省: ($45 - $19.8) × 12 = $302.4/年
```

**带宽成本对比** (100万次观看):
```
H.264流量: 2.25 GB × 1,000,000 = 2250 TB
AV1流量:   0.99 GB × 1,000,000 = 990 TB

CDN带宽费用 ($0.05/GB):
H.264: 2250 TB × $50/TB = $112,500
AV1:   990 TB × $50/TB = $49,500
节省: $63,000 (56%成本降低!) 💰💰💰
```

### 浏览器支持现状 (2024)

| 浏览器 | AV1解码 | dav1d集成 | 市场份额 |
|--------|---------|-----------|---------|
| Chrome 90+ | ✅ | ✅ | 65% |
| Firefox 67+ | ✅ | ✅ | 3% |
| Safari 17+ | ✅ | ✅ | 20% |
| Edge 90+ | ✅ | ✅ | 5% |
| **总覆盖** | **✅** | **✅** | **93%+** |

## 技术架构

### VideoSite AV1架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                     管理员上传视频 (原始文件)                      │
│                         MP4/MKV/AVI等                            │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    后端转码服务 (Celery Worker)                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Step 1: FFmpeg分析源视频                                 │   │
│  │  └─ 分辨率: 1920x1080                                     │   │
│  │  └─ 编码: H.264                                           │   │
│  │  └─ 码率: 5 Mbps                                          │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  Step 2: 多分辨率并行转码 (AV1编码)                       │   │
│  │  ┌────────────────────────────────────────────────┐      │   │
│  │  │  Thread 1: 1080p AV1                           │      │   │
│  │  │  • Encoder: SVT-AV1                            │      │   │
│  │  │  • Bitrate: 2.2 Mbps (vs H.264 5 Mbps)       │      │   │
│  │  │  • Time: 15分钟                                │      │   │
│  │  ├────────────────────────────────────────────────┤      │   │
│  │  │  Thread 2: 720p AV1                            │      │   │
│  │  │  • Bitrate: 1.2 Mbps                          │      │   │
│  │  │  • Time: 8分钟                                 │      │   │
│  │  ├────────────────────────────────────────────────┤      │   │
│  │  │  Thread 3: 480p AV1                            │      │   │
│  │  │  • Bitrate: 0.6 Mbps                          │      │   │
│  │  │  • Time: 5分钟                                 │      │   │
│  │  └────────────────────────────────────────────────┘      │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  Step 3: 生成HLS切片 (每个分辨率)                         │   │
│  │  • 切片时长: 6秒/片                                       │   │
│  │  • 格式: MPEG-TS (.ts)                                    │   │
│  │  • Playlist: index.m3u8                                   │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  Step 4: 上传到MinIO                                      │   │
│  │  • videos/{video_id}/av1/1080p/index.m3u8               │   │
│  │  • videos/{video_id}/av1/720p/index.m3u8                │   │
│  │  • videos/{video_id}/av1/480p/index.m3u8                │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       MinIO对象存储                              │
│  videos/{video_id}/                                             │
│  ├── h264/ (兼容性)                                             │
│  │   ├── 1080p/index.m3u8 (5 Mbps)                            │
│  │   ├── 720p/index.m3u8 (3 Mbps)                             │
│  │   └── 480p/index.m3u8 (1.5 Mbps)                           │
│  └── av1/ (高效压缩) ⭐ 推荐                                    │
│      ├── 1080p/index.m3u8 (2.2 Mbps) ← 节省56%!               │
│      ├── 720p/index.m3u8 (1.2 Mbps)                            │
│      └── 480p/index.m3u8 (0.6 Mbps)                            │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    前端播放器 (Video.js)                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  播放器检测浏览器AV1支持                                   │   │
│  │  ┌────────────────────────────────────────────────┐      │   │
│  │  │  if (支持AV1) {                                 │      │   │
│  │  │    加载: videos/123/av1/master.m3u8            │      │   │
│  │  │    解码器: dav1d (浏览器内置)                  │      │   │
│  │  │    带宽: 节省56% 🚀                             │      │   │
│  │  │  } else {                                       │      │   │
│  │  │    降级: videos/123/h264/master.m3u8           │      │   │
│  │  │    解码器: H.264                                │      │   │
│  │  │  }                                              │      │   │
│  │  └────────────────────────────────────────────────┘      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 双格式策略 (渐进式迁移)

**阶段1**: H.264为主,AV1可选
```
所有视频: H.264 (兼容性)
部分视频: H.264 + AV1 (测试)
```

**阶段2**: AV1为主,H.264降级
```
所有视频: AV1 + H.264 (双格式)
浏览器: 优先AV1,不支持则H.264
```

**阶段3**: 纯AV1
```
新视频: 仅AV1 (93%+浏览器支持)
旧视频: 保留H.264
```

## 后端集成

### 1. 安装dav1d

#### Ubuntu/Debian

```bash
# 安装dav1d库
sudo apt update
sudo apt install libdav1d-dev libdav1d6

# 验证安装
dav1d --version
# Output: dav1d 1.4.3
```

#### 编译FFmpeg with dav1d支持

```bash
# 下载FFmpeg源码
git clone https://git.ffmpeg.org/ffmpeg.git
cd ffmpeg

# 配置 (启用dav1d)
./configure \
  --enable-libdav1d \
  --enable-libsvtav1 \
  --enable-gpl \
  --enable-nonfree

# 编译安装
make -j$(nproc)
sudo make install

# 验证dav1d支持
ffmpeg -decoders | grep av1
# Output: V..... av1 (libdav1d)
```

### 2. 转码脚本 - SVT-AV1编码器

**SVT-AV1** (Scalable Video Technology for AV1) - Intel/Netflix开源

**优势**:
- ✅ 比libaom编码快**10-20倍**
- ✅ 质量与libaom接近
- ✅ 多线程优化
- ✅ 生产级稳定性

**安装SVT-AV1**:

```bash
# Ubuntu
sudo apt install libsvtav1-dev libsvtav1enc1

# 或从源码编译
git clone https://gitlab.com/AOMediaCodec/SVT-AV1.git
cd SVT-AV1/Build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
sudo make install
```

**AV1转码脚本**:

```python
# backend/app/utils/av1_transcoder.py
import subprocess
from pathlib import Path
from typing import Dict, List

class AV1Transcoder:
    """AV1视频转码器 (使用SVT-AV1编码器 + dav1d解码器)"""

    # AV1编码配置
    PROFILES = {
        '1080p': {
            'resolution': '1920:1080',
            'bitrate': '2200k',      # 2.2 Mbps (vs H.264 5 Mbps)
            'preset': 8,             # 0-13: 速度vs质量 (8=快速)
            'crf': 30,               # 质量参数 (30=高质量)
        },
        '720p': {
            'resolution': '1280:720',
            'bitrate': '1200k',
            'preset': 9,
            'crf': 32,
        },
        '480p': {
            'resolution': '854:480',
            'bitrate': '600k',
            'preset': 10,
            'crf': 34,
        },
        '360p': {
            'resolution': '640:360',
            'bitrate': '400k',
            'preset': 11,
            'crf': 36,
        }
    }

    @staticmethod
    def transcode_to_av1(
        input_path: Path,
        output_path: Path,
        resolution: str = '1080p',
        use_gpu: bool = False
    ) -> Path:
        """
        转码视频到AV1格式

        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            resolution: 目标分辨率 (1080p/720p/480p/360p)
            use_gpu: 是否使用GPU加速 (dav1d解码)

        Returns:
            输出文件路径
        """
        profile = AV1Transcoder.PROFILES[resolution]

        cmd = [
            'ffmpeg',
            '-y',  # 覆盖输出文件
        ]

        # 使用dav1d硬件加速解码 (如果输入是AV1)
        if use_gpu:
            cmd.extend([
                '-hwaccel', 'auto',
            ])

        cmd.extend([
            '-i', str(input_path),

            # 视频编码 - SVT-AV1
            '-c:v', 'libsvtav1',
            '-preset', str(profile['preset']),
            '-crf', str(profile['crf']),
            '-b:v', profile['bitrate'],
            '-maxrate', profile['bitrate'],
            '-bufsize', str(int(profile['bitrate'].rstrip('k')) * 2) + 'k',

            # 分辨率
            '-vf', f"scale={profile['resolution']}:flags=lanczos",

            # 音频编码 - Opus (AV1推荐)
            '-c:a', 'libopus',
            '-b:a', '128k',

            # 容器格式
            '-f', 'mp4',
            '-movflags', '+faststart',

            str(output_path)
        ])

        # 执行转码
        print(f"转码命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"转码失败: {result.stderr}")

        return output_path


    @staticmethod
    def transcode_to_hls_av1(
        input_path: Path,
        output_dir: Path,
        resolution: str = '1080p'
    ) -> Path:
        """
        转码为AV1 HLS流

        Returns:
            master.m3u8路径
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        profile = AV1Transcoder.PROFILES[resolution]

        cmd = [
            'ffmpeg',
            '-i', str(input_path),

            # 视频编码
            '-c:v', 'libsvtav1',
            '-preset', str(profile['preset']),
            '-crf', str(profile['crf']),
            '-b:v', profile['bitrate'],
            '-vf', f"scale={profile['resolution']}",

            # 音频编码
            '-c:a', 'libopus',
            '-b:a', '128k',

            # HLS配置
            '-f', 'hls',
            '-hls_time', '6',                    # 6秒/片
            '-hls_playlist_type', 'vod',
            '-hls_segment_filename', str(output_dir / 'segment_%03d.ts'),
            '-hls_segment_type', 'mpegts',

            str(output_dir / 'index.m3u8')
        ]

        subprocess.run(cmd, check=True)
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
            resolutions: {'1080p': 'path/to/1080p/index.m3u8', ...}
            format_type: 'av1' or 'h264'

        Returns:
            Master playlist内容
        """
        playlist = "#EXTM3U\n#EXT-X-VERSION:3\n\n"

        # 分辨率配置
        resolution_configs = {
            '1080p': {'bandwidth': 2200000, 'width': 1920, 'height': 1080},
            '720p':  {'bandwidth': 1200000, 'width': 1280, 'height': 720},
            '480p':  {'bandwidth': 600000,  'width': 854,  'height': 480},
            '360p':  {'bandwidth': 400000,  'width': 640,  'height': 360},
        }

        # AV1编解码器声明
        codec = 'av01.0.05M.08' if format_type == 'av1' else 'avc1.64001f'

        for res, url in resolutions.items():
            config = resolution_configs.get(res, {})
            playlist += f"""#EXT-X-STREAM-INF:BANDWIDTH={config['bandwidth']},RESOLUTION={config['width']}x{config['height']},CODECS="{codec},opus"
{url}

"""

        return playlist
```

### 3. Celery任务集成

```python
# backend/app/tasks/transcode_av1.py
from celery import shared_task
from pathlib import Path
import shutil
from app.utils.av1_transcoder import AV1Transcoder
from app.utils.minio_client import MinIOClient
from app.database import SessionLocal
from app.models.video import Video

@shared_task(bind=True)
def transcode_video_to_av1(self, video_id: int):
    """
    转码视频为AV1格式 (多分辨率)

    工作流:
    1. 下载原始视频
    2. 转码为多个AV1分辨率
    3. 生成HLS切片
    4. 上传到MinIO
    5. 更新数据库
    """
    db = SessionLocal()

    try:
        # 1. 获取视频
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError(f"Video {video_id} not found")

        # 2. 创建临时目录
        temp_dir = Path(f'/tmp/av1_transcode_{video_id}')
        temp_dir.mkdir(exist_ok=True)

        # 3. 下载原始视频
        original_path = temp_dir / 'original.mp4'
        minio_client = MinIOClient()
        minio_client.download_file(video.source_url, str(original_path))

        # 4. 分析源视频
        from app.utils.video_analyzer import analyze_video
        metadata = analyze_video(original_path)
        source_resolution = metadata['height']

        # 5. 决定要转码的分辨率 (不超过源分辨率)
        all_resolutions = ['1080p', '720p', '480p', '360p']
        resolution_heights = {'1080p': 1080, '720p': 720, '480p': 480, '360p': 360}

        target_resolutions = [
            res for res in all_resolutions
            if resolution_heights[res] <= source_resolution
        ]

        print(f"源分辨率: {source_resolution}p")
        print(f"目标分辨率: {target_resolutions}")

        # 6. 并行转码所有分辨率
        from concurrent.futures import ThreadPoolExecutor
        hls_urls = {}

        def transcode_resolution(resolution: str):
            output_dir = temp_dir / 'av1' / resolution
            output_dir.mkdir(parents=True, exist_ok=True)

            # 转码为AV1 HLS
            m3u8_path = AV1Transcoder.transcode_to_hls_av1(
                original_path,
                output_dir,
                resolution
            )

            # 上传到MinIO
            url = upload_hls_to_minio(
                video_id,
                resolution,
                output_dir,
                format_type='av1'
            )
            return resolution, url

        with ThreadPoolExecutor(max_workers=4) as executor:
            results = executor.map(transcode_resolution, target_resolutions)
            hls_urls = dict(results)

        # 7. 生成Master Playlist
        master_content = AV1Transcoder.create_master_playlist(
            video_id,
            hls_urls,
            format_type='av1'
        )

        # 上传Master Playlist
        master_path = temp_dir / 'master.m3u8'
        master_path.write_text(master_content)

        master_url = minio_client.upload_file(
            str(master_path),
            f'videos/{video_id}/av1/master.m3u8'
        )

        # 8. 更新数据库
        video.av1_master_url = master_url
        video.av1_resolutions = hls_urls
        video.is_av1_available = True
        db.commit()

        # 9. 清理临时文件
        shutil.rmtree(temp_dir)

        return {
            'status': 'success',
            'video_id': video_id,
            'resolutions': list(hls_urls.keys()),
            'master_url': master_url
        }

    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


def upload_hls_to_minio(
    video_id: int,
    resolution: str,
    hls_dir: Path,
    format_type: str = 'av1'
) -> str:
    """上传HLS文件到MinIO"""
    minio_client = MinIOClient()

    for file_path in hls_dir.glob('*'):
        if file_path.is_file():
            object_name = f'videos/{video_id}/{format_type}/{resolution}/{file_path.name}'
            minio_client.upload_file(str(file_path), object_name)

    return f'videos/{video_id}/{format_type}/{resolution}/index.m3u8'
```

### 4. 数据库扩展

```sql
-- 添加AV1字段到videos表
ALTER TABLE videos ADD COLUMN av1_master_url TEXT;
ALTER TABLE videos ADD COLUMN av1_resolutions JSONB DEFAULT '{}';
ALTER TABLE videos ADD COLUMN is_av1_available BOOLEAN DEFAULT FALSE;
ALTER TABLE videos ADD COLUMN av1_file_size BIGINT;  -- AV1文件大小
ALTER TABLE videos ADD COLUMN h264_file_size BIGINT; -- H.264文件大小 (对比)

-- 示例数据
UPDATE videos SET
  av1_master_url = 'videos/123/av1/master.m3u8',
  av1_resolutions = '{
    "1080p": "videos/123/av1/1080p/index.m3u8",
    "720p": "videos/123/av1/720p/index.m3u8",
    "480p": "videos/123/av1/480p/index.m3u8"
  }',
  is_av1_available = true,
  av1_file_size = 990000000,    -- 990 MB
  h264_file_size = 2250000000   -- 2.25 GB
WHERE id = 123;
```

**SQLAlchemy模型更新**:

```python
# backend/app/models/video.py
from sqlalchemy import Column, Integer, String, Text, Boolean, BigInteger
from sqlalchemy.dialects.postgresql import JSONB

class Video(Base):
    __tablename__ = "videos"

    # ... 现有字段 ...

    # H.264字段
    hls_master_url = Column(Text)  # H.264 master playlist

    # AV1字段 (新增)
    av1_master_url = Column(Text)
    av1_resolutions = Column(JSONB, default={})
    is_av1_available = Column(Boolean, default=False)
    av1_file_size = Column(BigInteger)
    h264_file_size = Column(BigInteger)

    @property
    def compression_ratio(self) -> float:
        """计算AV1相对H.264的压缩率"""
        if self.h264_file_size and self.av1_file_size:
            return (1 - self.av1_file_size / self.h264_file_size) * 100
        return 0.0
```

## 前端集成

### 1. 浏览器AV1支持检测

```typescript
// frontend/src/utils/codecSupport.ts

/**
 * 检测浏览器是否支持AV1解码
 */
export function supportsAV1(): boolean {
  const video = document.createElement('video');

  // 方法1: canPlayType检测
  const canPlay = video.canPlayType('video/mp4; codecs="av01.0.05M.08"');

  if (canPlay === 'probably' || canPlay === 'maybe') {
    return true;
  }

  // 方法2: MediaSource检测
  if (typeof MediaSource !== 'undefined') {
    return MediaSource.isTypeSupported('video/mp4; codecs="av01.0.05M.08"');
  }

  return false;
}

/**
 * 获取支持的编解码器
 */
export function getSupportedCodecs(): {
  h264: boolean;
  h265: boolean;
  vp9: boolean;
  av1: boolean;
} {
  const video = document.createElement('video');

  return {
    h264: video.canPlayType('video/mp4; codecs="avc1.42E01E"') !== '',
    h265: video.canPlayType('video/mp4; codecs="hev1.1.6.L93.B0"') !== '',
    vp9: video.canPlayType('video/webm; codecs="vp9"') !== '',
    av1: supportsAV1(),
  };
}

/**
 * 获取最佳视频URL (AV1优先)
 */
export function getBestVideoUrl(video: {
  av1_master_url?: string;
  hls_master_url: string;
  is_av1_available: boolean;
}): string {
  // 优先AV1 (如果浏览器支持)
  if (video.is_av1_available && video.av1_master_url && supportsAV1()) {
    console.log('✅ 使用AV1格式 (节省56%带宽)');
    return video.av1_master_url;
  }

  // 降级到H.264
  console.log('⚠️ 降级到H.264格式');
  return video.hls_master_url;
}
```

### 2. Video.js播放器集成

```typescript
// frontend/src/components/VideoPlayer/AV1Player.tsx
import React, { useEffect, useRef, useState } from 'react';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';
import { supportsAV1, getBestVideoUrl } from '@/utils/codecSupport';

interface AV1PlayerProps {
  video: {
    id: number;
    title: string;
    av1_master_url?: string;
    hls_master_url: string;
    is_av1_available: boolean;
    poster_url: string;
  };
}

export const AV1Player: React.FC<AV1PlayerProps> = ({ video }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const playerRef = useRef<any>(null);
  const [codecUsed, setCodecUsed] = useState<'av1' | 'h264'>('h264');

  useEffect(() => {
    if (!videoRef.current) return;

    // 初始化Video.js
    const player = videojs(videoRef.current, {
      controls: true,
      fluid: true,
      poster: video.poster_url,
      html5: {
        vhs: {
          overrideNative: true,
        },
      },
    });

    playerRef.current = player;

    // 选择最佳视频源
    const videoUrl = getBestVideoUrl(video);
    const isAV1 = videoUrl === video.av1_master_url;

    player.src({
      src: videoUrl,
      type: 'application/x-mpegURL',
    });

    setCodecUsed(isAV1 ? 'av1' : 'h264');

    // 监听播放事件
    player.on('loadedmetadata', () => {
      console.log('视频元数据加载完成');
      console.log('使用编解码器:', isAV1 ? 'AV1 (dav1d)' : 'H.264');
    });

    // 监听错误 (AV1播放失败时降级)
    player.on('error', () => {
      const error = player.error();
      console.error('播放错误:', error);

      if (isAV1 && video.hls_master_url) {
        console.warn('AV1播放失败,降级到H.264');
        player.src({
          src: video.hls_master_url,
          type: 'application/x-mpegURL',
        });
        setCodecUsed('h264');
      }
    });

    return () => {
      if (playerRef.current) {
        playerRef.current.dispose();
      }
    };
  }, [video]);

  return (
    <div className="av1-player-container">
      {/* 编解码器指示器 */}
      <div className="codec-indicator">
        {codecUsed === 'av1' ? (
          <span className="badge badge-success">
            ✅ AV1 (节省56%流量)
          </span>
        ) : (
          <span className="badge badge-warning">
            H.264 (兼容模式)
          </span>
        )}
      </div>

      <div data-vjs-player>
        <video
          ref={videoRef}
          className="video-js vjs-big-play-centered"
        />
      </div>

      {/* AV1支持提示 */}
      {!supportsAV1() && (
        <div className="alert alert-info">
          💡 您的浏览器不支持AV1,请更新到最新版Chrome/Firefox/Safari以节省流量
        </div>
      )}
    </div>
  );
};
```

### 3. 统计AV1使用率

```typescript
// frontend/src/utils/analytics.ts

/**
 * 上报编解码器使用统计
 */
export function reportCodecUsage(videoId: number, codec: 'av1' | 'h264') {
  // 发送到后端统计API
  fetch('/api/v1/analytics/codec-usage', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      video_id: videoId,
      codec: codec,
      browser: navigator.userAgent,
      timestamp: new Date().toISOString(),
    }),
  });
}
```

## 转码工作流

### 完整转码流程

```python
# backend/app/tasks/video_pipeline.py
from celery import chain

def process_uploaded_video(video_id: int):
    """
    视频处理管线 (H.264 + AV1双格式)

    工作流:
    1. 转码H.264 (兼容性优先)
    2. 转码AV1 (高效压缩)
    3. 生成缩略图
    4. 生成hover预览
    """

    # 创建任务链
    pipeline = chain(
        # 任务1: H.264转码 (快速,优先上线)
        transcode_video_to_h264.s(video_id),

        # 任务2: AV1转码 (慢速,后台进行)
        transcode_video_to_av1.s(video_id),

        # 任务3: 生成缩略图
        generate_thumbnails.s(video_id),

        # 任务4: 生成hover预览
        generate_hover_preview.s(video_id),

        # 任务5: 通知完成
        notify_transcode_complete.s(video_id)
    )

    # 异步执行
    pipeline.apply_async()
```

### 转码时间预估

| 视频时长 | 分辨率 | H.264转码 | AV1转码 | 总时长 |
|---------|--------|----------|---------|--------|
| 10分钟 | 1080p | 3分钟 | 15分钟 | 18分钟 |
| 30分钟 | 1080p | 8分钟 | 45分钟 | 53分钟 |
| 60分钟 | 1080p | 15分钟 | 90分钟 | 105分钟 |
| 60分钟 | 4K | 30分钟 | 180分钟 | 210分钟 |

**优化建议**:
- ✅ H.264优先上线 (3分钟内可播放)
- ✅ AV1后台转码 (用户无感知)
- ✅ 使用GPU加速 (转码时间减半)

## 性能优化

### 1. SVT-AV1编码器优化

**Preset参数对比** (速度vs质量):

| Preset | 编码速度 | 质量 | 推荐场景 |
|--------|---------|------|---------|
| 0 | 极慢 (0.5x) | 最高 | 归档 |
| 4 | 慢 (2x) | 高 | 付费内容 |
| **8** | **快 (10x)** | **中高** | **生产推荐** |
| 10 | 很快 (20x) | 中 | 实时应用 |
| 13 | 极快 (50x) | 低 | 测试 |

**推荐配置** (生产环境):

```python
PROFILES = {
    '1080p': {
        'preset': 8,      # 平衡速度和质量
        'crf': 30,        # 高质量 (28-32为佳)
        'bitrate': '2200k',
    }
}
```

### 2. 多线程并行转码

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_transcode(video_id: int, resolutions: List[str]):
    """并行转码多个分辨率"""

    with ThreadPoolExecutor(max_workers=len(resolutions)) as executor:
        futures = [
            executor.submit(transcode_resolution, video_id, res)
            for res in resolutions
        ]

        results = [f.result() for f in futures]

    return results
```

**性能提升**:
- 串行: 15min (1080p) + 8min (720p) + 5min (480p) = **28分钟**
- 并行: max(15min, 8min, 5min) = **15分钟** (1.9倍提升)

### 3. 两阶段编码 (2-pass)

```bash
# Pass 1: 分析视频
ffmpeg -i input.mp4 \
  -c:v libsvtav1 -preset 8 -crf 30 \
  -pass 1 -f null /dev/null

# Pass 2: 实际编码 (质量更高)
ffmpeg -i input.mp4 \
  -c:v libsvtav1 -preset 8 -crf 30 \
  -pass 2 output.mp4
```

**效果**:
- 文件大小: 减少10-15%
- 质量: 提升5-10%
- 时间: 增加100% (慎用)

**建议**: 仅对重要内容使用2-pass

## 部署指南

### 1. 服务器要求

**最低配置**:
- CPU: 8核心 (支持AVX2指令集)
- 内存: 16GB
- 存储: NVMe SSD (临时文件)

**推荐配置**:
- CPU: 16核心+ (AMD Ryzen 9 / Intel i9)
- 内存: 32GB+
- GPU: NVIDIA RTX 3060+ (可选,用于H.264加速)

### 2. Docker部署

```dockerfile
# backend/Dockerfile
FROM ubuntu:22.04

# 安装依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libdav1d6 \
    libsvtav1enc1 \
    python3.11 \
    python3-pip

# 安装Python依赖
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# 复制代码
COPY . /app
WORKDIR /app

# Celery Worker启动
CMD celery -A app.celery worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=50
```

### 3. 监控和告警

```python
# backend/app/monitoring/av1_metrics.py
from prometheus_client import Counter, Histogram, Gauge

# 转码计数
av1_transcodes_total = Counter(
    'av1_transcodes_total',
    'Total AV1 transcodes',
    ['resolution', 'status']
)

# 转码时长
av1_transcode_duration = Histogram(
    'av1_transcode_duration_seconds',
    'AV1 transcode duration',
    ['resolution']
)

# 压缩率
av1_compression_ratio = Gauge(
    'av1_compression_ratio_percent',
    'AV1 vs H.264 compression ratio',
    ['video_id']
)

# 使用示例
def track_transcode(video_id: int, resolution: str):
    import time
    start = time.time()

    try:
        # 转码逻辑
        transcode_to_av1(video_id, resolution)

        # 记录成功
        av1_transcodes_total.labels(resolution=resolution, status='success').inc()
        duration = time.time() - start
        av1_transcode_duration.labels(resolution=resolution).observe(duration)

    except Exception as e:
        av1_transcodes_total.labels(resolution=resolution, status='failed').inc()
        raise
```

## 成本收益分析

### VideoSite项目成本对比

**假设**:
- 视频数量: 10,000部
- 平均时长: 60分钟
- 平均分辨率: 1080p
- 月活用户: 100,000
- 人均观看: 10小时/月

### 存储成本

| 项目 | H.264 | AV1 | 节省 |
|------|-------|-----|------|
| 单部视频 | 2.25 GB | 0.99 GB | 1.26 GB (56%) |
| 10,000部 | 22.5 TB | 9.9 TB | 12.6 TB (56%) |
| 存储费用 ($0.02/GB/月) | $450/月 | $198/月 | **$252/月** |
| **年度节省** | - | - | **$3,024** |

### 带宽成本

| 项目 | H.264 | AV1 | 节省 |
|------|-------|-----|------|
| 单用户月流量 | 22.5 GB | 9.9 GB | 12.6 GB (56%) |
| 100,000用户 | 2250 TB | 990 TB | 1260 TB (56%) |
| CDN费用 ($0.05/GB) | $112,500/月 | $49,500/月 | **$63,000/月** |
| **年度节省** | - | - | **$756,000** |

### 转码成本

| 项目 | H.264 | AV1 | 增加 |
|------|-------|-----|------|
| CPU时间 (单部60分钟) | 15分钟 | 90分钟 | +75分钟 |
| 服务器成本 (16核/$200/月) | - | - | +$100/月 |
| **年度增加** | - | - | **$1,200** |

### **净节省** (年度):

```
存储节省:  $3,024
带宽节省:  $756,000
转码增加: -$1,200
──────────────────
净节省:    $757,824/年  💰💰💰
```

**投资回报率 (ROI)**:
- 投资: $1,200 (服务器成本)
- 回报: $757,824
- **ROI: 63,052%** 🚀

### 环境影响

**碳排放减少**:
- 带宽减少56% → 数据中心能耗减少56%
- 年节省电力: ~500 MWh
- 碳排放减少: ~200吨CO₂

## 总结

### ✅ AV1 (dav1d)核心优势

1. **世界最快** - 比libaom快11倍
2. **压缩率最高** - 节省56%带宽和存储
3. **完全免费** - 无专利费
4. **全球采用** - 93%+浏览器支持
5. **巨额节省** - 年节省$75万成本

### 🚀 实施路线图

**第1周**: 环境搭建
- ✅ 安装dav1d/SVT-AV1
- ✅ 配置FFmpeg
- ✅ 测试转码

**第2-4周**: 后端开发
- ✅ 编写转码脚本
- ✅ Celery任务集成
- ✅ 数据库扩展

**第1-2月**: 前端开发
- ✅ AV1检测逻辑
- ✅ Video.js集成
- ✅ 降级方案

**第3月**: 灰度发布
- ✅ 10%流量测试
- ✅ 监控质量
- ✅ 收集反馈

**第4月**: 全量上线
- ✅ 100%新视频AV1
- ✅ 逐步迁移旧视频

### 📊 预期效果

- ✅ **带宽节省**: 56%
- ✅ **存储节省**: 56%
- ✅ **成本节省**: $75万/年
- ✅ **用户体验**: 加载更快,流量更省
- ✅ **环境友好**: 减少200吨CO₂排放

---

**文档版本**: 1.0.0
**最后更新**: 2025-10-10
**推荐优先级**: ⭐⭐⭐⭐⭐ (最高)
