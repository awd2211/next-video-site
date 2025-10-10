# 视频加密与防盗链系统

> **HLS AES-128加密** - 防止视频盗链和非法下载

## 📋 目录

- [加密方案对比](#加密方案对比)
- [推荐方案: HLS AES-128](#推荐方案-hls-aes-128)
- [数据库设计](#数据库设计)
- [加密实现](#加密实现)
- [密钥服务器](#密钥服务器)
- [前端集成](#前端集成)
- [防盗链措施](#防盗链措施)
- [安全最佳实践](#安全最佳实践)

## 加密方案对比

| 方案 | 安全级别 | 实现难度 | 成本 | 兼容性 | 推荐场景 |
|------|---------|---------|------|--------|---------|
| **HLS AES-128** | ⭐⭐⭐ | 低 | 免费 | ✅ 全平台 | 中小型平台 |
| **Widevine DRM** | ⭐⭐⭐⭐⭐ | 高 | $$$$ | Android/Chrome | 企业级 |
| **PlayReady DRM** | ⭐⭐⭐⭐⭐ | 高 | $$$$ | Windows/Xbox | 微软生态 |
| **FairPlay DRM** | ⭐⭐⭐⭐⭐ | 高 | $$$$ | iOS/Safari | Apple生态 |
| **无加密** | ⭐ | - | 免费 | ✅ 全平台 | 公开内容 |

## 推荐方案: HLS AES-128

### 为什么选择AES-128?

✅ **易于实现**: FFmpeg原生支持,无需第三方DRM服务
✅ **成本低**: 完全免费,无许可费用
✅ **兼容性好**: 所有现代浏览器和设备支持
✅ **效果显著**: 可阻止95%的非技术用户盗版
✅ **灵活可控**: 自主控制密钥和访问策略

❌ **局限性**:
- 无法防止专业破解工具
- 密钥可能被抓包获取
- 不适合高价值版权内容 (如好莱坞电影)

### 适用场景

- ✅ 在线教育课程
- ✅ 企业培训视频
- ✅ 付费会员内容
- ✅ 用户上传视频 (防盗链)
- ❌ 院线电影、体育赛事直播 (建议用Widevine DRM)

## 加密原理

### HLS AES-128工作流程

```
1. 生成加密密钥
   ↓
2. FFmpeg使用密钥加密HLS切片
   ↓
3. m3u8播放列表包含密钥URL
   ↓
4. 播放器请求密钥API (需JWT Token)
   ↓
5. 服务器验证权限并返回密钥
   ↓
6. Video.js自动解密播放
```

### 加密示例

**未加密的m3u8**:
```m3u8
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:6
#EXTINF:6.0,
segment_000.ts
#EXTINF:6.0,
segment_001.ts
```

**加密后的m3u8**:
```m3u8
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:6
#EXT-X-KEY:METHOD=AES-128,URI="https://api.example.com/v1/keys/abc123?token=xyz",IV=0x12345678901234567890123456789012
#EXTINF:6.0,
segment_000.ts
#EXTINF:6.0,
segment_001.ts
```

**关键参数**:
- `METHOD=AES-128`: 使用AES-128 CBC加密
- `URI`: 密钥服务器地址 (需Token验证)
- `IV`: 初始化向量 (16字节)

## 数据库设计

### 加密密钥表 (encryption_keys)

```sql
CREATE TABLE encryption_keys (
    id SERIAL PRIMARY KEY,
    video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,

    -- 密钥信息
    key_id VARCHAR(64) UNIQUE NOT NULL,        -- 密钥ID (用于URL)
    encryption_key BYTEA NOT NULL,             -- 16字节AES密钥 (加密存储)
    iv BYTEA NOT NULL,                         -- 16字节初始化向量

    -- 密钥轮换
    version INTEGER DEFAULT 1,                 -- 密钥版本
    is_active BOOLEAN DEFAULT TRUE,            -- 是否激活
    expires_at TIMESTAMP,                      -- 密钥过期时间

    -- 加密配置
    encryption_method VARCHAR(20) DEFAULT 'AES-128',
    key_format VARCHAR(50) DEFAULT 'identity',

    -- 审计
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES admin_users(id),

    -- 索引
    INDEX idx_encryption_keys_video_id (video_id),
    INDEX idx_encryption_keys_key_id (key_id),
    INDEX idx_encryption_keys_active (is_active, expires_at)
);
```

### 视频访问日志 (video_access_logs)

```sql
CREATE TABLE video_access_logs (
    id BIGSERIAL PRIMARY KEY,
    video_id INTEGER NOT NULL REFERENCES videos(id),
    user_id INTEGER REFERENCES users(id),

    -- 访问信息
    access_type VARCHAR(20),  -- 'key_request', 'video_play', 'download_attempt'
    key_id VARCHAR(64),
    token_hash VARCHAR(64),

    -- 客户端信息
    ip_address INET,
    user_agent TEXT,
    referer TEXT,
    device_fingerprint VARCHAR(64),

    -- 地理位置
    country_code CHAR(2),
    city VARCHAR(100),

    -- 结果
    status VARCHAR(20),  -- 'success', 'denied', 'expired', 'invalid_token'
    error_message TEXT,

    -- 时间
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 索引
    INDEX idx_video_access_logs_video_id (video_id),
    INDEX idx_video_access_logs_user_id (user_id),
    INDEX idx_video_access_logs_ip (ip_address),
    INDEX idx_video_access_logs_accessed_at (accessed_at)
);
```

### 播放限制表 (playback_restrictions)

```sql
CREATE TABLE playback_restrictions (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,

    -- 访问控制
    require_auth BOOLEAN DEFAULT TRUE,         -- 是否需要登录
    allowed_domains TEXT[],                    -- 允许的域名白名单
    blocked_ips INET[],                        -- IP黑名单
    allowed_countries CHAR(2)[],               -- 国家白名单

    -- 时间限制
    available_from TIMESTAMP,                  -- 可用开始时间
    available_until TIMESTAMP,                 -- 可用结束时间

    -- 播放限制
    max_plays_per_user INTEGER,               -- 每用户最大播放次数
    max_concurrent_streams INTEGER DEFAULT 3,  -- 最大并发流数
    play_duration_limit INTEGER,               -- 播放时长限制 (秒)

    -- Token配置
    token_ttl INTEGER DEFAULT 3600,            -- Token有效期 (秒)
    allow_token_refresh BOOLEAN DEFAULT TRUE,

    -- 水印
    enable_watermark BOOLEAN DEFAULT FALSE,
    watermark_text TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_video_restriction UNIQUE(video_id)
);
```

### SQLAlchemy ORM模型

```python
# backend/app/models/encryption.py
from sqlalchemy import Column, Integer, String, Boolean, LargeBinary, TIMESTAMP, ARRAY, Text
from sqlalchemy.dialects.postgresql import INET
from app.database import Base
from datetime import datetime
from cryptography.fernet import Fernet
import os

class EncryptionKey(Base):
    __tablename__ = "encryption_keys"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)

    # 密钥信息
    key_id = Column(String(64), unique=True, nullable=False, index=True)
    encryption_key = Column(LargeBinary, nullable=False)  # 加密存储
    iv = Column(LargeBinary, nullable=False)

    # 密钥轮换
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True, index=True)
    expires_at = Column(TIMESTAMP)

    # 加密配置
    encryption_method = Column(String(20), default='AES-128')
    key_format = Column(String(50), default='identity')

    # 审计
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("admin_users.id"))

    # 关系
    video = relationship("Video", back_populates="encryption_key")


class VideoAccessLog(Base):
    __tablename__ = "video_access_logs"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)

    # 访问信息
    access_type = Column(String(20))
    key_id = Column(String(64))
    token_hash = Column(String(64))

    # 客户端信息
    ip_address = Column(INET, index=True)
    user_agent = Column(Text)
    referer = Column(Text)
    device_fingerprint = Column(String(64))

    # 地理位置
    country_code = Column(String(2))
    city = Column(String(100))

    # 结果
    status = Column(String(20))
    error_message = Column(Text)

    # 时间
    accessed_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)


class PlaybackRestriction(Base):
    __tablename__ = "playback_restrictions"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), unique=True)

    # 访问控制
    require_auth = Column(Boolean, default=True)
    allowed_domains = Column(ARRAY(Text))
    blocked_ips = Column(ARRAY(INET))
    allowed_countries = Column(ARRAY(String(2)))

    # 时间限制
    available_from = Column(TIMESTAMP)
    available_until = Column(TIMESTAMP)

    # 播放限制
    max_plays_per_user = Column(Integer)
    max_concurrent_streams = Column(Integer, default=3)
    play_duration_limit = Column(Integer)

    # Token配置
    token_ttl = Column(Integer, default=3600)
    allow_token_refresh = Column(Boolean, default=True)

    # 水印
    enable_watermark = Column(Boolean, default=False)
    watermark_text = Column(Text)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    video = relationship("Video", back_populates="playback_restriction")
```

## 加密实现

### 1. 生成加密密钥

```python
# backend/app/utils/encryption.py
import os
import secrets
from cryptography.fernet import Fernet
from app.config import settings

# 主密钥 (用于加密存储的视频密钥)
MASTER_KEY = settings.ENCRYPTION_MASTER_KEY.encode()
fernet = Fernet(MASTER_KEY)


def generate_encryption_key():
    """生成16字节AES-128密钥"""
    return os.urandom(16)


def generate_iv():
    """生成16字节初始化向量"""
    return os.urandom(16)


def generate_key_id():
    """生成唯一密钥ID"""
    return secrets.token_urlsafe(32)


def encrypt_key(key: bytes) -> bytes:
    """使用主密钥加密视频密钥 (用于数据库存储)"""
    return fernet.encrypt(key)


def decrypt_key(encrypted_key: bytes) -> bytes:
    """解密视频密钥"""
    return fernet.decrypt(encrypted_key)


def create_video_encryption_key(video_id: int, db):
    """为视频创建加密密钥"""
    from app.models.encryption import EncryptionKey

    # 生成密钥和IV
    key = generate_encryption_key()
    iv = generate_iv()
    key_id = generate_key_id()

    # 加密后存储
    encrypted_key = encrypt_key(key)

    # 保存到数据库
    encryption_key = EncryptionKey(
        video_id=video_id,
        key_id=key_id,
        encryption_key=encrypted_key,
        iv=iv,
        version=1,
        is_active=True,
    )
    db.add(encryption_key)
    db.commit()

    return encryption_key
```

### 2. FFmpeg加密转码

```python
# backend/app/tasks/transcode.py
import subprocess
from pathlib import Path
from app.utils.encryption import decrypt_key

def transcode_with_encryption(
    input_path: Path,
    output_dir: Path,
    resolution: str,
    encryption_key_obj
):
    """使用AES-128加密生成HLS"""

    # 解密密钥
    key = decrypt_key(encryption_key_obj.encryption_key)
    iv = encryption_key_obj.iv

    # 保存密钥到临时文件 (FFmpeg需要)
    key_file = output_dir / 'enc.key'
    key_file.write_bytes(key)

    # 保存密钥信息文件
    key_info_file = output_dir / 'enc.keyinfo'
    key_info_content = f"""https://api.videosite.com/api/v1/keys/{encryption_key_obj.key_id}
{key_file}
{iv.hex()}
"""
    key_info_file.write_text(key_info_content)

    # FFmpeg命令
    cmd = [
        'ffmpeg',
        '-i', str(input_path),

        # 视频编码
        '-c:v', 'h264_nvenc',  # GPU编码
        '-preset', 'p4',
        '-b:v', PROFILES[resolution]['bitrate'],
        '-vf', f"scale={PROFILES[resolution]['resolution']}",

        # 音频编码
        '-c:a', 'aac',
        '-b:a', PROFILES[resolution]['audio_bitrate'],

        # HLS配置
        '-f', 'hls',
        '-hls_time', '6',
        '-hls_playlist_type', 'vod',
        '-hls_segment_filename', str(output_dir / 'segment_%03d.ts'),

        # ✨ AES-128加密
        '-hls_key_info_file', str(key_info_file),

        # 输出
        '-y',
        str(output_dir / 'index.m3u8')
    ]

    # 执行
    subprocess.run(cmd, check=True)

    # 清理临时密钥文件
    key_file.unlink()
    key_info_file.unlink()

    return output_dir / 'index.m3u8'
```

### 3. 完整转码流程

```python
# backend/app/tasks/transcode.py
from celery import shared_task

@shared_task(bind=True)
def transcode_video_with_encryption(self, video_id: int):
    """转码并加密视频"""
    db = SessionLocal()

    try:
        # 1. 获取视频
        video = db.query(Video).filter(Video.id == video_id).first()

        # 2. 创建加密密钥
        encryption_key = create_video_encryption_key(video_id, db)

        # 3. 下载原始视频
        temp_dir = Path(f'/tmp/transcode_{video_id}')
        temp_dir.mkdir(exist_ok=True)
        original_path = temp_dir / 'original.mp4'
        # ... 从MinIO下载 ...

        # 4. 转码所有分辨率 (带加密)
        resolutions = ['1080p', '720p', '480p', '360p']
        hls_urls = {}

        for resolution in resolutions:
            output_dir = temp_dir / resolution
            output_dir.mkdir(exist_ok=True)

            # 加密转码
            m3u8_path = transcode_with_encryption(
                original_path,
                output_dir,
                resolution,
                encryption_key
            )

            # 上传到MinIO
            hls_url = upload_hls_to_minio(video_id, resolution, output_dir)
            hls_urls[resolution] = hls_url

        # 5. 生成Master Playlist
        master_url = create_master_playlist(video_id, hls_urls, encryption_key)

        # 6. 更新数据库
        video.hls_master_url = master_url
        video.is_encrypted = True
        db.commit()

        # 7. 清理
        shutil.rmtree(temp_dir)

        return {'status': 'success', 'video_id': video_id}

    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()
```

## 密钥服务器

### 密钥分发API

```python
# backend/app/api/encryption.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.encryption import EncryptionKey, VideoAccessLog, PlaybackRestriction
from app.models.user import User
from app.utils.dependencies import get_current_user_optional
from app.utils.encryption import decrypt_key
import hashlib
from datetime import datetime

router = APIRouter(prefix="/api/v1/keys", tags=["Encryption"])


@router.get("/{key_id}")
async def get_encryption_key(
    key_id: str,
    token: str,  # JWT Token
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    """
    获取视频解密密钥

    安全措施:
    1. JWT Token验证
    2. Referer检查
    3. IP限制
    4. 播放次数限制
    5. 时间限制
    """

    # 1. 验证密钥存在
    result = await db.execute(
        select(EncryptionKey).filter(
            EncryptionKey.key_id == key_id,
            EncryptionKey.is_active == True
        )
    )
    encryption_key = result.scalar_one_or_none()

    if not encryption_key:
        await log_access(db, None, key_id, request, 'denied', 'Key not found')
        raise HTTPException(status_code=404, detail="Key not found")

    video_id = encryption_key.video_id

    # 2. 检查密钥是否过期
    if encryption_key.expires_at and encryption_key.expires_at < datetime.utcnow():
        await log_access(db, video_id, key_id, request, 'denied', 'Key expired')
        raise HTTPException(status_code=403, detail="Key expired")

    # 3. 获取播放限制
    result = await db.execute(
        select(PlaybackRestriction).filter(PlaybackRestriction.video_id == video_id)
    )
    restriction = result.scalar_one_or_none()

    if restriction:
        # 4. 验证Token (JWT)
        if restriction.require_auth:
            from app.utils.security import decode_token
            payload = decode_token(token)
            if not payload or payload.get('video_id') != video_id:
                await log_access(db, video_id, key_id, request, 'denied', 'Invalid token')
                raise HTTPException(status_code=401, detail="Invalid token")

            # Token过期检查
            if payload.get('exp', 0) < datetime.utcnow().timestamp():
                await log_access(db, video_id, key_id, request, 'denied', 'Token expired')
                raise HTTPException(status_code=401, detail="Token expired")

        # 5. Referer检查 (防盗链)
        referer = request.headers.get('referer', '')
        if restriction.allowed_domains:
            allowed = any(domain in referer for domain in restriction.allowed_domains)
            if not allowed:
                await log_access(db, video_id, key_id, request, 'denied', 'Invalid referer')
                raise HTTPException(status_code=403, detail="Access denied - invalid referer")

        # 6. IP黑名单检查
        client_ip = request.client.host
        if restriction.blocked_ips and client_ip in restriction.blocked_ips:
            await log_access(db, video_id, key_id, request, 'denied', 'IP blocked')
            raise HTTPException(status_code=403, detail="Access denied - IP blocked")

        # 7. 地理位置限制
        if restriction.allowed_countries:
            # TODO: 通过IP获取国家代码
            # country_code = get_country_from_ip(client_ip)
            # if country_code not in restriction.allowed_countries:
            #     raise HTTPException(status_code=403, detail="Geographic restriction")
            pass

        # 8. 播放次数限制
        if restriction.max_plays_per_user and current_user:
            play_count = await get_user_play_count(db, video_id, current_user.id)
            if play_count >= restriction.max_plays_per_user:
                await log_access(db, video_id, key_id, request, 'denied', 'Play limit exceeded')
                raise HTTPException(status_code=403, detail="Play limit exceeded")

    # 9. 解密密钥
    decrypted_key = decrypt_key(encryption_key.encryption_key)

    # 10. 记录访问日志
    await log_access(db, video_id, key_id, request, 'success', None, current_user)

    # 11. 返回密钥 (二进制)
    return Response(
        content=decrypted_key,
        media_type="application/octet-stream",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache",
        }
    )


async def log_access(
    db: AsyncSession,
    video_id: int,
    key_id: str,
    request: Request,
    status: str,
    error_message: str = None,
    user: User = None
):
    """记录访问日志"""
    log = VideoAccessLog(
        video_id=video_id,
        user_id=user.id if user else None,
        access_type='key_request',
        key_id=key_id,
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        referer=request.headers.get('referer'),
        status=status,
        error_message=error_message,
    )
    db.add(log)
    await db.commit()


async def get_user_play_count(db: AsyncSession, video_id: int, user_id: int) -> int:
    """获取用户播放次数"""
    result = await db.execute(
        select(func.count(VideoAccessLog.id)).filter(
            VideoAccessLog.video_id == video_id,
            VideoAccessLog.user_id == user_id,
            VideoAccessLog.access_type == 'key_request',
            VideoAccessLog.status == 'success'
        )
    )
    return result.scalar() or 0
```

### 生成播放Token

```python
# backend/app/api/videos.py

@router.get("/{video_id}/play-token")
async def generate_play_token(
    video_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """生成视频播放Token"""

    # 1. 验证视频存在
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # 2. 检查用户权限 (是否购买、是否会员等)
    # TODO: 权限检查逻辑

    # 3. 获取Token配置
    result = await db.execute(
        select(PlaybackRestriction).filter(PlaybackRestriction.video_id == video_id)
    )
    restriction = result.scalar_one_or_none()
    ttl = restriction.token_ttl if restriction else 3600

    # 4. 生成JWT Token
    from app.utils.security import create_access_token
    from datetime import timedelta

    token_data = {
        "sub": str(current_user.id),
        "video_id": video_id,
        "exp": datetime.utcnow() + timedelta(seconds=ttl),
        "type": "video_playback"
    }
    token = create_access_token(token_data)

    return {
        "token": token,
        "expires_in": ttl,
        "video_id": video_id
    }
```

## 前端集成

### Video.js自动解密

```typescript
// frontend/src/components/VideoPlayer/EncryptedVideoPlayer.tsx
import React, { useEffect, useRef, useState } from 'react'
import videojs from 'video.js'
import axios from '@/utils/axios'

interface EncryptedVideoPlayerProps {
  videoId: number
  videoUrl: string  // HLS master.m3u8 URL
}

export const EncryptedVideoPlayer: React.FC<EncryptedVideoPlayerProps> = ({
  videoId,
  videoUrl
}) => {
  const videoRef = useRef<HTMLVideoElement>(null)
  const playerRef = useRef<any>(null)
  const [playToken, setPlayToken] = useState<string>('')

  useEffect(() => {
    // 1. 获取播放Token
    const fetchPlayToken = async () => {
      try {
        const response = await axios.get(`/api/v1/videos/${videoId}/play-token`)
        setPlayToken(response.data.token)
      } catch (error) {
        console.error('Failed to get play token:', error)
      }
    }
    fetchPlayToken()
  }, [videoId])

  useEffect(() => {
    if (!videoRef.current || !playToken) return

    // 2. 初始化Video.js
    const player = videojs(videoRef.current, {
      controls: true,
      fluid: true,
      html5: {
        vhs: {
          overrideNative: true,
          // ✨ 密钥请求拦截
          xhr: {
            beforeRequest: (options: any) => {
              // 如果是密钥请求,添加Token参数
              if (options.uri.includes('/api/v1/keys/')) {
                const separator = options.uri.includes('?') ? '&' : '?'
                options.uri = `${options.uri}${separator}token=${playToken}`
              }
              return options
            }
          }
        },
      },
    })

    // 3. 加载视频
    player.src({
      src: videoUrl,
      type: 'application/x-mpegURL'
    })

    playerRef.current = player

    // 4. 错误处理
    player.on('error', () => {
      const error = player.error()
      if (error && error.code === 4) {
        console.error('Decryption error - invalid key')
        // 显示友好错误提示
      }
    })

    return () => {
      if (playerRef.current) {
        playerRef.current.dispose()
      }
    }
  }, [playToken, videoUrl])

  return (
    <div className="encrypted-video-player">
      {!playToken && (
        <div className="loading">获取播放权限中...</div>
      )}
      <div data-vjs-player>
        <video
          ref={videoRef}
          className="video-js vjs-big-play-centered"
        />
      </div>
    </div>
  )
}
```

### 管理后台 - 加密配置

```typescript
// admin-frontend/src/pages/Videos/EncryptionSettings.tsx
import React, { useState, useEffect } from 'react'
import { Form, Switch, InputNumber, Select, Button, Space, message } from 'antd'
import axios from '@/utils/axios'

export const EncryptionSettings: React.FC<{ videoId: number }> = ({ videoId }) => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)

  const onFinish = async (values: any) => {
    setLoading(true)
    try {
      // 1. 启用加密 (如果未加密)
      if (values.enable_encryption) {
        await axios.post(`/api/v1/admin/videos/${videoId}/enable-encryption`)
      }

      // 2. 更新播放限制
      await axios.put(`/api/v1/admin/videos/${videoId}/restrictions`, {
        require_auth: values.require_auth,
        allowed_domains: values.allowed_domains?.split('\n').filter(Boolean),
        max_plays_per_user: values.max_plays_per_user,
        max_concurrent_streams: values.max_concurrent_streams,
        token_ttl: values.token_ttl,
      })

      message.success('保存成功')
    } catch (error) {
      message.error('保存失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Form form={form} onFinish={onFinish} layout="vertical">
      <Form.Item name="enable_encryption" label="启用加密" valuePropName="checked">
        <Switch />
      </Form.Item>

      <Form.Item name="require_auth" label="需要登录" valuePropName="checked">
        <Switch />
      </Form.Item>

      <Form.Item name="allowed_domains" label="允许的域名 (每行一个)">
        <Input.TextArea
          rows={4}
          placeholder="https://www.example.com&#10;https://app.example.com"
        />
      </Form.Item>

      <Form.Item name="max_plays_per_user" label="每用户最大播放次数">
        <InputNumber min={1} max={1000} />
      </Form.Item>

      <Form.Item name="max_concurrent_streams" label="最大并发流数">
        <InputNumber min={1} max={10} />
      </Form.Item>

      <Form.Item name="token_ttl" label="Token有效期 (秒)">
        <InputNumber min={60} max={86400} />
      </Form.Item>

      <Button type="primary" htmlType="submit" loading={loading}>
        保存配置
      </Button>
    </Form>
  )
}
```

## 防盗链措施

### 1. Referer检查

```python
def check_referer(request: Request, allowed_domains: list[str]):
    """检查Referer防止盗链"""
    referer = request.headers.get('referer', '')

    if not referer:
        return False

    # 检查是否来自允许的域名
    for domain in allowed_domains:
        if domain in referer:
            return True

    return False
```

### 2. 时间戳签名

```python
import hashlib
import time

def generate_signed_url(video_url: str, secret: str, ttl: int = 3600):
    """生成带时间戳签名的URL"""
    timestamp = int(time.time()) + ttl
    sign_string = f"{video_url}{timestamp}{secret}"
    signature = hashlib.md5(sign_string.encode()).hexdigest()

    return f"{video_url}?expires={timestamp}&sign={signature}"


def verify_signed_url(url: str, secret: str) -> bool:
    """验证签名URL"""
    from urllib.parse import urlparse, parse_qs

    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    expires = int(params.get('expires', [0])[0])
    signature = params.get('sign', [''])[0]

    # 检查是否过期
    if int(time.time()) > expires:
        return False

    # 验证签名
    base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    sign_string = f"{base_url}{expires}{secret}"
    expected_signature = hashlib.md5(sign_string.encode()).hexdigest()

    return signature == expected_signature
```

### 3. 设备指纹绑定

```typescript
// frontend/src/utils/deviceFingerprint.ts
import FingerprintJS from '@fingerprintjs/fingerprintjs'

export async function getDeviceFingerprint(): Promise<string> {
  const fp = await FingerprintJS.load()
  const result = await fp.get()
  return result.visitorId
}

// 使用
const fingerprint = await getDeviceFingerprint()
axios.defaults.headers.common['X-Device-Fingerprint'] = fingerprint
```

```python
# backend/app/api/encryption.py

@router.get("/{key_id}")
async def get_encryption_key(
    key_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # 检查设备指纹
    device_fingerprint = request.headers.get('x-device-fingerprint')

    # 验证此设备是否有权限播放
    # ...
```

### 4. 动态密钥轮换

```python
from celery import shared_task
from datetime import timedelta

@shared_task
def rotate_encryption_keys():
    """定期轮换加密密钥 (每周执行)"""
    db = SessionLocal()

    try:
        # 查找需要轮换的密钥 (超过7天)
        threshold = datetime.utcnow() - timedelta(days=7)
        old_keys = db.query(EncryptionKey).filter(
            EncryptionKey.created_at < threshold,
            EncryptionKey.is_active == True
        ).all()

        for old_key in old_keys:
            # 创建新版本密钥
            new_key = generate_encryption_key()
            new_iv = generate_iv()
            new_key_id = generate_key_id()

            # 停用旧密钥
            old_key.is_active = False

            # 创建新密钥
            new_encryption_key = EncryptionKey(
                video_id=old_key.video_id,
                key_id=new_key_id,
                encryption_key=encrypt_key(new_key),
                iv=new_iv,
                version=old_key.version + 1,
                is_active=True,
            )
            db.add(new_encryption_key)

            # 重新转码视频 (使用新密钥)
            transcode_video_with_encryption.delay(old_key.video_id)

        db.commit()
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()
```

## 安全最佳实践

### 1. 密钥管理

✅ **永远不要**:
- 将加密密钥硬编码在代码中
- 在前端JavaScript中存储密钥
- 通过URL参数传递密钥 (使用POST或Header)
- 在日志中记录密钥

✅ **应该**:
- 使用环境变量存储主密钥 (`ENCRYPTION_MASTER_KEY`)
- 加密存储视频密钥到数据库
- 定期轮换密钥
- 使用HTTPS传输密钥

### 2. Token安全

```python
# 生成短期Token (1小时)
token_data = {
    "video_id": video_id,
    "user_id": user_id,
    "exp": datetime.utcnow() + timedelta(hours=1),
    "nonce": secrets.token_hex(16),  # 防重放
}
token = create_access_token(token_data)
```

### 3. 访问日志监控

```python
# 监控异常访问模式
@shared_task
def detect_suspicious_access():
    """检测可疑访问"""
    db = SessionLocal()

    # 1. 单IP高频请求
    suspicious_ips = db.execute("""
        SELECT ip_address, COUNT(*) as request_count
        FROM video_access_logs
        WHERE accessed_at > NOW() - INTERVAL '1 hour'
        GROUP BY ip_address
        HAVING COUNT(*) > 1000
    """).fetchall()

    for ip, count in suspicious_ips:
        # 加入黑名单
        block_ip(ip)

    # 2. 失败率高的密钥请求
    failed_keys = db.execute("""
        SELECT key_id, COUNT(*) as fail_count
        FROM video_access_logs
        WHERE status = 'denied'
          AND accessed_at > NOW() - INTERVAL '1 hour'
        GROUP BY key_id
        HAVING COUNT(*) > 100
    """).fetchall()

    # 发送告警
    for key_id, count in failed_keys:
        send_alert(f"High failure rate for key {key_id}: {count} denials")

    db.close()
```

### 4. 环境配置

```bash
# backend/.env

# 主加密密钥 (使用Fernet生成)
ENCRYPTION_MASTER_KEY=your-fernet-key-here

# JWT密钥
JWT_SECRET_KEY=your-jwt-secret-here

# Token有效期
DEFAULT_TOKEN_TTL=3600

# 允许的域名
ALLOWED_DOMAINS=https://www.videosite.com,https://app.videosite.com
```

生成主密钥:
```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())  # 复制到 .env
```

## 性能优化

### 1. 密钥缓存

```python
from functools import lru_cache
from app.utils.cache import cache_result

@cache_result(ttl=3600)
async def get_encryption_key_cached(key_id: str):
    """缓存密钥 (1小时)"""
    # ... 从数据库获取密钥 ...
    return encryption_key
```

### 2. CDN配置

MinIO配置CORS和缓存:
```python
# 允许跨域请求 (密钥服务器)
minio_client.set_bucket_policy(
    bucket_name='videos',
    policy={
        "Statement": [{
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": ["arn:aws:s3:::videos/*/hls/*.m3u8"],  # 只允许m3u8
            "Condition": {
                "StringLike": {
                    "aws:Referer": ["https://www.videosite.com/*"]
                }
            }
        }]
    }
)
```

### 3. 并发限制

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.get("/{key_id}")
@limiter.limit("60/minute")  # 每分钟最多60次
async def get_encryption_key(...):
    # ...
```

## 成本分析

### AES-128加密成本

| 项目 | CPU转码 | GPU转码 |
|------|---------|---------|
| **转码时间增加** | +5% | +2% |
| **存储增加** | 0% | 0% |
| **带宽增加** | 0% | 0% |
| **计算成本** | 几乎无 | 几乎无 |

**结论**: AES-128加密对性能影响极小 (<5%),成本几乎为零。

### vs DRM方案

| 方案 | 初始成本 | 年费 | 视频处理费 |
|------|---------|------|-----------|
| **AES-128** | $0 | $0 | $0 |
| **Widevine** | $5,000 | $2,000 | $0.01/GB |
| **Multi-DRM** | $10,000 | $5,000 | $0.02/GB |

## 监控和告警

### Prometheus指标

```python
from prometheus_client import Counter, Histogram

# 密钥请求计数
key_request_counter = Counter(
    'video_key_requests_total',
    'Total number of encryption key requests',
    ['video_id', 'status']
)

# 密钥请求延迟
key_request_duration = Histogram(
    'video_key_request_duration_seconds',
    'Encryption key request duration'
)

@router.get("/{key_id}")
async def get_encryption_key(...):
    with key_request_duration.time():
        # ... 处理逻辑 ...
        key_request_counter.labels(video_id=video_id, status='success').inc()
```

### Grafana仪表板

- 密钥请求QPS
- 失败率趋势
- Top访问IP
- 地理分布
- Token过期率

## 总结

### HLS AES-128加密优势

✅ **易于实现**: FFmpeg原生支持,无需复杂集成
✅ **成本低**: 完全免费,无许可费用
✅ **效果好**: 可阻止95%非技术用户盗版
✅ **性能影响小**: 转码时间增加<5%
✅ **兼容性好**: 所有现代浏览器支持

### 适用场景

- ✅ 在线教育平台
- ✅ 企业培训视频
- ✅ 付费会员内容
- ✅ UGC平台防盗链
- ❌ 高价值版权内容 (建议Widevine DRM)

### 下一步

1. 实现密钥生成和存储
2. 修改转码任务集成加密
3. 开发密钥分发API
4. 前端播放器集成
5. 配置访问控制策略
6. 部署监控告警

---

**文档版本**: 1.0.0
**最后更新**: 2025-10-10
