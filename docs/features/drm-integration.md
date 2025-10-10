# 企业级DRM集成指南

> **Widevine/PlayReady/FairPlay** - 好莱坞级视频保护

## 📋 目录

- [DRM方案对比](#drm方案对比)
- [Multi-DRM架构](#multi-drm架构)
- [Widevine集成](#widevine集成)
- [PlayReady集成](#playready集成)
- [FairPlay集成](#fairplay集成)
- [Shaka Packager](#shaka-packager)
- [成本分析](#成本分析)
- [实施路线图](#实施路线图)

## DRM方案对比

### 三大DRM系统

| DRM | 提供商 | 平台支持 | 安全级别 | 市场份额 | 许可费 |
|-----|--------|---------|---------|---------|--------|
| **Widevine** | Google | Android, Chrome, ChromeOS | ⭐⭐⭐⭐⭐ | 65% | 免费* |
| **PlayReady** | Microsoft | Windows, Xbox, Edge | ⭐⭐⭐⭐⭐ | 20% | 收费 |
| **FairPlay** | Apple | iOS, macOS, tvOS, Safari | ⭐⭐⭐⭐⭐ | 15% | 免费* |

*需要与DRM服务商签约,有最低消费要求

### 技术对比

| 特性 | Widevine | PlayReady | FairPlay |
|------|----------|-----------|----------|
| **协议** | MPEG-DASH, HLS | MPEG-DASH, Smooth Streaming | HLS only |
| **加密** | CENC (Common Encryption) | CENC | Sample-AES |
| **密钥交换** | License Server | License Server | Key Server |
| **安全级别** | L1/L2/L3 | SL2000/SL3000 | - |
| **硬件支持** | TEE, Secure Video Path | TEE | Secure Enclave |
| **离线播放** | ✅ | ✅ | ✅ |

## Multi-DRM架构

### 为什么需要Multi-DRM?

单一DRM无法覆盖所有平台:
- **Widevine**: Android、Chrome (不支持Safari、IE)
- **PlayReady**: Windows、Xbox (不支持macOS、iOS)
- **FairPlay**: iOS、Safari (不支持Android、Windows)

**解决方案**: Multi-DRM - 同一内容生成多个DRM版本

### Multi-DRM工作流程

```
原始视频 (MP4)
    ↓
FFmpeg编码 (H.264/HEVC + AAC)
    ↓
Shaka Packager多DRM打包
    ├─ DASH + Widevine (Android/Chrome)
    ├─ DASH + PlayReady (Windows/Xbox)
    └─ HLS + FairPlay (iOS/Safari)
    ↓
上传到CDN/MinIO
    ↓
前端检测平台并选择对应DRM
    ↓
播放器请求许可证
    ↓
DRM License Server验证
    ↓
返回解密密钥
    ↓
播放器解密播放
```

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         客户端                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Android    │  │   Windows    │  │   iOS        │      │
│  │   Chrome     │  │   Xbox       │  │   Safari     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │ Widevine        │ PlayReady        │ FairPlay     │
└─────────┼─────────────────┼──────────────────┼──────────────┘
          │                 │                  │
          ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│              Multi-DRM License Server (第三方)               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • BuyDRM KeyOS                                      │   │
│  │  • Axinom DRM                                        │   │
│  │  • PallyCon Multi-DRM                                │   │
│  │  • Irdeto                                            │   │
│  └──────────────────────────────────────────────────────┘   │
│         ↑                                                    │
│         │ 验证用户权限                                      │
│         │                                                    │
└─────────┼──────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                    VideoSite后端                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  权限验证:                                            │   │
│  │  • 用户是否登录                                       │   │
│  │  • 用户是否付费                                       │   │
│  │  • 内容是否可用                                       │   │
│  │  • 地理位置限制                                       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│              CDN / MinIO (加密内容存储)                      │
│  ├── videos/{video_id}/                                     │
│  │   ├── dash/                                             │
│  │   │   ├── manifest.mpd (Widevine + PlayReady)          │
│  │   │   ├── init_video.mp4                                │
│  │   │   ├── init_audio.mp4                                │
│  │   │   ├── segment_video_*.m4s                           │
│  │   │   └── segment_audio_*.m4s                           │
│  │   └── hls/                                              │
│  │       ├── master.m3u8                                   │
│  │       ├── playlist_*.m3u8 (FairPlay)                    │
│  │       └── segment_*.ts                                  │
└─────────────────────────────────────────────────────────────┘
```

## Widevine集成

### 1. 申请Widevine许可

访问: https://www.widevine.com/

**要求**:
- 公司营业执照
- 内容版权证明
- 技术实施计划
- 审核周期: 2-4周

### 2. 使用Shaka Packager生成Widevine DASH

```bash
# 安装Shaka Packager
wget https://github.com/shaka-project/shaka-packager/releases/download/v2.6.1/packager-linux-x64
chmod +x packager-linux-x64
sudo mv packager-linux-x64 /usr/local/bin/packager

# 生成Widevine加密的DASH
packager \
  input=input.mp4,stream=video,output=video.mp4 \
  input=input.mp4,stream=audio,output=audio.mp4 \
  --mpd_output manifest.mpd \
  --enable_widevine_encryption \
  --key_server_url "https://license.uat.widevine.com/cenc/getcontentkey/widevine_test" \
  --content_id "your_content_id" \
  --signer "widevine_test" \
  --aes_signing_key "1ae8ccd0e7985cc0b6203a55855a1034afc252980e970ca90e5202689f947ab9" \
  --aes_signing_iv "d58ce954203b7c9a9a9d467f59839249"
```

### 3. Python集成

```python
# backend/app/tasks/drm_transcode.py
import subprocess
from pathlib import Path

def package_with_widevine(
    input_video: Path,
    output_dir: Path,
    content_id: str,
    key_server_url: str,
):
    """使用Widevine DRM打包视频"""

    video_output = output_dir / 'video.mp4'
    audio_output = output_dir / 'audio.mp4'
    mpd_output = output_dir / 'manifest.mpd'

    cmd = [
        'packager',
        f'input={input_video},stream=video,output={video_output}',
        f'input={input_video},stream=audio,output={audio_output}',
        f'--mpd_output', str(mpd_output),
        '--enable_widevine_encryption',
        '--key_server_url', key_server_url,
        '--content_id', content_id,
        '--signer', settings.WIDEVINE_SIGNER,
        '--aes_signing_key', settings.WIDEVINE_SIGNING_KEY,
        '--aes_signing_iv', settings.WIDEVINE_SIGNING_IV,
    ]

    subprocess.run(cmd, check=True)

    return mpd_output
```

### 4. 前端Shaka Player集成

```typescript
// frontend/src/components/VideoPlayer/DRMPlayer.tsx
import React, { useEffect, useRef } from 'react'
import shaka from 'shaka-player'

export const WidevinePlayer: React.FC<{ manifestUrl: string, licenseUrl: string }> = ({
  manifestUrl,
  licenseUrl
}) => {
  const videoRef = useRef<HTMLVideoElement>(null)
  const playerRef = useRef<shaka.Player | null>(null)

  useEffect(() => {
    if (!videoRef.current) return

    // 初始化Shaka Player
    const player = new shaka.Player(videoRef.current)
    playerRef.current = player

    // 配置Widevine DRM
    player.configure({
      drm: {
        servers: {
          'com.widevine.alpha': licenseUrl
        }
      }
    })

    // 添加认证Header
    player.getNetworkingEngine()?.registerRequestFilter((type, request) => {
      if (type === shaka.net.NetworkingEngine.RequestType.LICENSE) {
        // 添加JWT Token
        const token = localStorage.getItem('access_token')
        request.headers['Authorization'] = `Bearer ${token}`
      }
    })

    // 加载视频
    player.load(manifestUrl).then(() => {
      console.log('Widevine video loaded')
    }).catch((error) => {
      console.error('Error loading video:', error)
    })

    return () => {
      player.destroy()
    }
  }, [manifestUrl, licenseUrl])

  return (
    <video
      ref={videoRef}
      controls
      style={{ width: '100%', height: 'auto' }}
    />
  )
}
```

## PlayReady集成

### 1. 使用Shaka Packager生成PlayReady DASH

```bash
packager \
  input=input.mp4,stream=video,output=video.mp4 \
  input=input.mp4,stream=audio,output=audio.mp4 \
  --mpd_output manifest.mpd \
  --enable_playready_encryption \
  --playready_server_url "https://playready.example.com/AcquireLicense" \
  --playready_key_id "your_key_id" \
  --playready_key "your_encryption_key"
```

### 2. 前端集成 (dash.js)

```typescript
// frontend/src/components/VideoPlayer/PlayReadyPlayer.tsx
import React, { useEffect, useRef } from 'react'
import dashjs from 'dashjs'

export const PlayReadyPlayer: React.FC<{ manifestUrl: string }> = ({ manifestUrl }) => {
  const videoRef = useRef<HTMLVideoElement>(null)
  const playerRef = useRef<any>(null)

  useEffect(() => {
    if (!videoRef.current) return

    const player = dashjs.MediaPlayer().create()
    playerRef.current = player

    // 配置PlayReady
    player.setProtectionData({
      'com.microsoft.playready': {
        serverURL: 'https://playready-license.example.com/AcquireLicense',
        httpRequestHeaders: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      }
    })

    player.initialize(videoRef.current, manifestUrl, true)

    return () => {
      player.reset()
    }
  }, [manifestUrl])

  return <video ref={videoRef} controls style={{ width: '100%' }} />
}
```

## FairPlay集成

### 1. 申请FairPlay证书

访问: https://developer.apple.com/streaming/fps/

**要求**:
- Apple开发者账号 ($99/年)
- D-U-N-S Number (邓白氏编码)
- 内容版权证明

### 2. 使用Shaka Packager生成FairPlay HLS

```bash
packager \
  'input=input.mp4,stream=video,output=video.mp4' \
  'input=input.mp4,stream=audio,output=audio.mp4' \
  --hls_master_playlist_output master.m3u8 \
  --enable_fairplay_encryption \
  --fairplay_key_uri "skd://fairplay-license.example.com" \
  --fairplay_key_id "your_key_id" \
  --fairplay_key "your_encryption_key" \
  --fairplay_iv "your_iv"
```

### 3. 前端集成 (Safari原生HLS)

```typescript
// frontend/src/components/VideoPlayer/FairPlayPlayer.tsx
import React, { useEffect, useRef } from 'react'

export const FairPlayPlayer: React.FC<{
  manifestUrl: string
  certificateUrl: string
  licenseUrl: string
}> = ({ manifestUrl, certificateUrl, licenseUrl }) => {
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    if (!videoRef.current) return
    const video = videoRef.current

    // 检测是否支持FairPlay
    if (!window.WebKitMediaKeys) {
      console.error('FairPlay not supported')
      return
    }

    video.addEventListener('webkitneedkey', async (event: any) => {
      const initData = event.initData
      const contentId = extractContentId(event.initData)

      // 1. 获取FairPlay证书
      const certificateResponse = await fetch(certificateUrl)
      const certificate = await certificateResponse.arrayBuffer()

      // 2. 创建密钥会话
      const keySession = video.webkitKeys.createSession('video/mp4', initData)

      // 3. 生成许可证请求
      const spcMessage = await generateSPCMessage(contentId, certificate, initData)

      // 4. 请求许可证
      const licenseResponse = await fetch(licenseUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/octet-stream',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: spcMessage
      })

      const licenseData = await licenseResponse.arrayBuffer()

      // 5. 更新密钥会话
      keySession.update(new Uint8Array(licenseData))
    })

    video.src = manifestUrl
    video.play()

  }, [manifestUrl, certificateUrl, licenseUrl])

  return <video ref={videoRef} controls style={{ width: '100%' }} />
}

function extractContentId(initData: Uint8Array): string {
  const contentIdString = String.fromCharCode.apply(null, Array.from(new Uint16Array(initData.buffer)))
  return contentIdString.substring(contentIdString.indexOf('skd://') + 6)
}

async function generateSPCMessage(
  contentId: string,
  certificate: ArrayBuffer,
  initData: Uint8Array
): Promise<ArrayBuffer> {
  // 生成SPC (Server Playback Context)
  // 实际实现需要调用FairPlay Streaming API
  // 这里简化处理
  return new ArrayBuffer(0)
}
```

## Shaka Packager

### 完整Multi-DRM打包脚本

```bash
#!/bin/bash
# backend/scripts/package_multidrm.sh

INPUT_VIDEO=$1
OUTPUT_DIR=$2
VIDEO_ID=$3

# 创建输出目录
mkdir -p $OUTPUT_DIR/dash
mkdir -p $OUTPUT_DIR/hls

# 1. 生成DASH (Widevine + PlayReady)
packager \
  input=$INPUT_VIDEO,stream=video,output=$OUTPUT_DIR/dash/video.mp4 \
  input=$INPUT_VIDEO,stream=audio,output=$OUTPUT_DIR/dash/audio.mp4 \
  --mpd_output $OUTPUT_DIR/dash/manifest.mpd \
  --enable_widevine_encryption \
  --enable_playready_encryption \
  --key_server_url "https://license.uat.widevine.com/cenc/getcontentkey/widevine_test" \
  --content_id "$VIDEO_ID" \
  --protection_scheme cbcs

# 2. 生成HLS (FairPlay)
packager \
  input=$INPUT_VIDEO,stream=video,output=$OUTPUT_DIR/hls/video.m4s \
  input=$INPUT_VIDEO,stream=audio,output=$OUTPUT_DIR/hls/audio.m4s \
  --hls_master_playlist_output $OUTPUT_DIR/hls/master.m3u8 \
  --enable_fairplay_encryption \
  --fairplay_key_uri "skd://fairplay-license.example.com/$VIDEO_ID" \
  --protection_scheme cbcs

echo "Multi-DRM packaging completed for video $VIDEO_ID"
```

### Python任务集成

```python
# backend/app/tasks/multidrm_transcode.py
from celery import shared_task
import subprocess
from pathlib import Path

@shared_task(bind=True)
def transcode_with_multidrm(self, video_id: int):
    """Multi-DRM转码任务"""
    db = SessionLocal()

    try:
        video = db.query(Video).filter(Video.id == video_id).first()

        # 1. 下载原始视频
        temp_dir = Path(f'/tmp/multidrm_{video_id}')
        temp_dir.mkdir(exist_ok=True)
        original = temp_dir / 'original.mp4'
        # ... 下载逻辑 ...

        # 2. FFmpeg预处理 (标准化编码)
        preprocessed = temp_dir / 'preprocessed.mp4'
        subprocess.run([
            'ffmpeg',
            '-i', str(original),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-y',
            str(preprocessed)
        ], check=True)

        # 3. Multi-DRM打包
        output_dir = temp_dir / 'output'
        output_dir.mkdir(exist_ok=True)

        subprocess.run([
            '/app/scripts/package_multidrm.sh',
            str(preprocessed),
            str(output_dir),
            str(video_id)
        ], check=True)

        # 4. 上传到MinIO
        minio_client = MinIOClient()

        # DASH文件
        dash_manifest = upload_directory_to_minio(
            output_dir / 'dash',
            f'videos/{video_id}/dash'
        )

        # HLS文件
        hls_manifest = upload_directory_to_minio(
            output_dir / 'hls',
            f'videos/{video_id}/hls'
        )

        # 5. 更新数据库
        video.dash_manifest_url = dash_manifest
        video.hls_manifest_url = hls_manifest
        video.drm_enabled = True
        video.drm_types = ['widevine', 'playready', 'fairplay']
        db.commit()

        # 6. 清理
        shutil.rmtree(temp_dir)

        return {'status': 'success', 'video_id': video_id}

    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()
```

## DRM License Server

### 使用第三方服务

推荐服务商:

#### 1. **BuyDRM KeyOS** (推荐)
- 网站: https://www.buydrm.com/
- 价格: $2,000起/年
- 支持: Widevine, PlayReady, FairPlay
- 特点: 易集成,稳定性好

#### 2. **PallyCon Multi-DRM**
- 网站: https://www.pallycon.com/
- 价格: 按流量计费 ($0.01/GB)
- 支持: 全平台
- 特点: 按需付费,无最低消费

#### 3. **Axinom DRM**
- 网站: https://www.axinom.com/
- 价格: 定制
- 支持: 企业级
- 特点: 高度定制化

### 集成示例 (BuyDRM)

```python
# backend/app/api/drm_license.py
from fastapi import APIRouter, Depends, Request
import httpx

router = APIRouter(prefix="/api/v1/drm", tags=["DRM"])

@router.post("/widevine/license")
async def get_widevine_license(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """代理Widevine许可证请求"""

    # 1. 读取客户端许可证请求
    license_request = await request.body()

    # 2. 验证用户权限
    video_id = request.headers.get('X-Video-ID')
    if not has_permission(current_user, video_id):
        raise HTTPException(status_code=403, detail="No permission")

    # 3. 转发到BuyDRM
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://wv-keyos.licensekeyserver.com/',
            content=license_request,
            headers={
                'Content-Type': 'application/octet-stream',
                'customdata': generate_customdata(current_user, video_id)
            }
        )

    # 4. 返回许可证
    return Response(
        content=response.content,
        media_type='application/octet-stream'
    )


def generate_customdata(user: User, video_id: int) -> str:
    """生成BuyDRM customdata"""
    import base64
    import json

    data = {
        'userId': user.id,
        'videoId': video_id,
        'timestamp': int(time.time()),
        # 其他业务数据
    }

    return base64.b64encode(json.dumps(data).encode()).decode()
```

## 成本分析

### 1. 技术成本

| 项目 | AES-128 | Multi-DRM |
|------|---------|-----------|
| **开发成本** | 低 (2周) | 高 (2-3月) |
| **基础设施** | FFmpeg | FFmpeg + Shaka Packager |
| **存储增加** | 0% | +50% (多格式) |
| **带宽增加** | 0% | +10% (License请求) |
| **维护成本** | 低 | 中等 |

### 2. 许可费用

| 服务商 | 初始费用 | 年费 | 流量费 | 并发限制 |
|--------|---------|------|--------|---------|
| **BuyDRM** | $5,000 | $2,000 | $0.01/GB | 10,000并发 |
| **PallyCon** | $0 | $0 | $0.02/GB | 按需 |
| **Axinom** | $10,000 | $5,000 | 定制 | 无限 |
| **自建** | $50,000+ | $10,000+ | $0 | 自定义 |

### 3. 业务成本估算

假设:
- 10万付费用户
- 每用户每月观看50GB
- 总流量: 5PB/月

**Multi-DRM成本** (PallyCon):
- 流量费: 5,000TB × $0.02 = **$100,000/月**
- 年成本: **$120万**

**AES-128成本**:
- **$0**

**结论**: 只有**高价值版权内容**才值得使用DRM

## 实施路线图

### 阶段1: 评估 (2周)

- [ ] 评估内容价值是否需要DRM
- [ ] 选择DRM服务商
- [ ] 申请Widevine/FairPlay许可
- [ ] 技术可行性评估

### 阶段2: 开发 (1-2月)

- [ ] 安装Shaka Packager
- [ ] 开发Multi-DRM转码流程
- [ ] 集成License Server
- [ ] 前端播放器适配 (Shaka Player/dash.js)
- [ ] 后端权限验证

### 阶段3: 测试 (2周)

- [ ] 多设备测试 (Android/iOS/Windows)
- [ ] 多浏览器测试 (Chrome/Safari/Edge)
- [ ] 离线播放测试
- [ ] 性能压测
- [ ] 安全渗透测试

### 阶段4: 上线 (1周)

- [ ] 灰度发布
- [ ] 监控告警
- [ ] 用户反馈收集
- [ ] 全量上线

## 总结

### 何时使用DRM?

✅ **适合DRM**:
- 院线电影、电视剧
- 体育赛事直播
- 付费音乐/MV
- 高价值培训课程 (>$1000/人)

❌ **不适合DRM** (用AES-128):
- UGC内容
- 普通在线课程
- 企业内训视频
- 低价值内容

### 决策矩阵

| 内容价值 | 用户规模 | 推荐方案 | 年成本 |
|---------|---------|---------|--------|
| 低 (<$100) | 任意 | 无加密/AES-128 | $0 |
| 中 ($100-$1000) | <10万 | AES-128 | $0 |
| 中 ($100-$1000) | >10万 | AES-128 + 水印 | <$1万 |
| 高 (>$1000) | 任意 | Multi-DRM | $2万-$100万 |

### 最佳实践

1. **分层保护**: 低价值用AES-128,高价值用DRM
2. **混合策略**: 预告片无加密,正片用DRM
3. **用户体验优先**: DRM不应影响正常用户
4. **成本控制**: 定期评估DRM ROI

---

**文档版本**: 1.0.0
**最后更新**: 2025-10-10
