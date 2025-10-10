# 视频字幕管理系统

> **多语言字幕** - 支持SRT、VTT、ASS格式，自动生成与手动上传

## 📋 目录

- [功能特性](#功能特性)
- [字幕格式支持](#字幕格式支持)
- [数据库设计](#数据库设计)
- [后端API实现](#后端api实现)
- [前端集成](#前端集成)
- [字幕上传流程](#字幕上传流程)
- [字幕自动生成](#字幕自动生成)
- [字幕编辑器](#字幕编辑器)
- [性能优化](#性能优化)

## 功能特性

### ✅ 核心功能

- **多格式支持**: SRT、WebVTT、ASS/SSA
- **多语言字幕**: 每个视频支持多语言轨道
- **自动生成**: AI语音识别自动生成字幕
- **手动上传**: 管理员上传字幕文件
- **在线编辑**: 浏览器内字幕编辑器
- **默认字幕**: 设置默认语言
- **字幕搜索**: 按字幕内容搜索视频

### 🎯 使用场景

| 场景 | 方案 | 说明 |
|------|------|------|
| **中文视频** | 手动上传中文字幕 | 准确度最高 |
| **英文视频** | AI自动生成 + 人工校对 | 效率高 |
| **多语言发布** | 上传多个语言字幕 | 覆盖国际用户 |
| **教育视频** | 详细字幕 + 时间轴 | 便于学习 |

## 字幕格式支持

### 1. SRT (SubRip)

**最通用** - 兼容性最好

```srt
1
00:00:01,000 --> 00:00:04,000
欢迎来到视频网站

2
00:00:05,000 --> 00:00:08,000
这是第二句字幕
```

**特点**:
- ✅ 简单易读
- ✅ 兼容性最好
- ❌ 不支持样式

### 2. WebVTT (Web Video Text Tracks)

**Web标准** - HTML5原生支持

```vtt
WEBVTT

00:00:01.000 --> 00:00:04.000
欢迎来到视频网站

00:00:05.000 --> 00:00:08.000
这是第二句字幕

NOTE 这是注释
```

**特点**:
- ✅ HTML5标准
- ✅ 支持样式
- ✅ Video.js原生支持

### 3. ASS/SSA (Advanced SubStation Alpha)

**高级样式** - 支持复杂排版

```ass
[Script Info]
Title: 视频字幕

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour
Style: Default,Arial,20,&H00FFFFFF

[Events]
Format: Layer, Start, End, Style, Text
Dialogue: 0,0:00:01.00,0:00:04.00,Default,欢迎来到视频网站
```

**特点**:
- ✅ 支持高级样式
- ✅ 字体、颜色、位置
- ❌ 文件较大

## 数据库设计

### 字幕表 (subtitles)

```sql
CREATE TABLE subtitles (
    id SERIAL PRIMARY KEY,
    video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,

    -- 语言信息
    language VARCHAR(10) NOT NULL,  -- ISO 639-1: 'zh', 'en', 'ja', 'ko', etc.
    language_name VARCHAR(50),      -- '中文', 'English', '日本語'

    -- 字幕文件
    file_url TEXT NOT NULL,         -- MinIO存储路径
    format VARCHAR(10) NOT NULL,    -- 'srt', 'vtt', 'ass'
    file_size INTEGER,              -- 文件大小 (bytes)

    -- 字幕属性
    is_default BOOLEAN DEFAULT FALSE,  -- 是否为默认字幕
    is_auto_generated BOOLEAN DEFAULT FALSE,  -- 是否AI自动生成
    is_verified BOOLEAN DEFAULT FALSE,  -- 是否已人工校对

    -- 字幕统计
    subtitle_count INTEGER,         -- 字幕条数
    duration_seconds FLOAT,         -- 总时长

    -- 上传信息
    uploaded_by INTEGER REFERENCES admin_users(id),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 编辑历史
    last_edited_by INTEGER REFERENCES admin_users(id),
    last_edited_at TIMESTAMP,

    -- 索引
    CONSTRAINT unique_video_language UNIQUE(video_id, language),
    INDEX idx_subtitles_video_id (video_id),
    INDEX idx_subtitles_language (language)
);
```

### 字幕内容表 (subtitle_contents) - 用于搜索

```sql
CREATE TABLE subtitle_contents (
    id SERIAL PRIMARY KEY,
    subtitle_id INTEGER NOT NULL REFERENCES subtitles(id) ON DELETE CASCADE,

    -- 时间轴
    sequence_number INTEGER NOT NULL,  -- 序号
    start_time FLOAT NOT NULL,         -- 开始时间 (秒)
    end_time FLOAT NOT NULL,           -- 结束时间 (秒)

    -- 字幕文本
    text TEXT NOT NULL,                -- 字幕内容
    text_clean TEXT,                   -- 清理后的文本 (用于搜索)

    -- 全文搜索索引
    text_vector TSVECTOR,

    -- 索引
    INDEX idx_subtitle_contents_subtitle_id (subtitle_id),
    INDEX idx_subtitle_contents_time (start_time, end_time)
);

-- 全文搜索索引
CREATE INDEX idx_subtitle_contents_text_vector ON subtitle_contents USING GIN(text_vector);

-- 自动更新text_vector
CREATE TRIGGER subtitle_contents_text_vector_update
BEFORE INSERT OR UPDATE ON subtitle_contents
FOR EACH ROW EXECUTE FUNCTION
tsvector_update_trigger(text_vector, 'pg_catalog.simple', text_clean);
```

### SQLAlchemy ORM模型

```python
# backend/app/models/subtitle.py
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from app.database import Base

class Subtitle(Base):
    __tablename__ = "subtitles"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)

    # 语言信息
    language = Column(String(10), nullable=False)  # ISO 639-1
    language_name = Column(String(50))

    # 字幕文件
    file_url = Column(Text, nullable=False)
    format = Column(String(10), nullable=False)
    file_size = Column(Integer)

    # 字幕属性
    is_default = Column(Boolean, default=False)
    is_auto_generated = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)

    # 字幕统计
    subtitle_count = Column(Integer)
    duration_seconds = Column(Float)

    # 上传信息
    uploaded_by = Column(Integer, ForeignKey("admin_users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    last_edited_by = Column(Integer, ForeignKey("admin_users.id"))
    last_edited_at = Column(DateTime)

    # 关系
    video = relationship("Video", back_populates="subtitles")
    contents = relationship("SubtitleContent", back_populates="subtitle", cascade="all, delete-orphan")
    uploader = relationship("AdminUser", foreign_keys=[uploaded_by])

    __table_args__ = (
        Index('idx_subtitles_video_id', 'video_id'),
        Index('idx_subtitles_language', 'language'),
    )


class SubtitleContent(Base):
    __tablename__ = "subtitle_contents"

    id = Column(Integer, primary_key=True, index=True)
    subtitle_id = Column(Integer, ForeignKey("subtitles.id", ondelete="CASCADE"), nullable=False)

    # 时间轴
    sequence_number = Column(Integer, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)

    # 字幕文本
    text = Column(Text, nullable=False)
    text_clean = Column(Text)
    text_vector = Column(TSVECTOR)

    # 关系
    subtitle = relationship("Subtitle", back_populates="contents")

    __table_args__ = (
        Index('idx_subtitle_contents_subtitle_id', 'subtitle_id'),
        Index('idx_subtitle_contents_time', 'start_time', 'end_time'),
        Index('idx_subtitle_contents_text_vector', 'text_vector', postgresql_using='gin'),
    )
```

### Alembic迁移脚本

```python
# backend/alembic/versions/xxxx_add_subtitles.py
def upgrade():
    # 创建字幕表
    op.create_table(
        'subtitles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=False),
        sa.Column('language', sa.String(10), nullable=False),
        sa.Column('language_name', sa.String(50)),
        sa.Column('file_url', sa.Text(), nullable=False),
        sa.Column('format', sa.String(10), nullable=False),
        sa.Column('file_size', sa.Integer()),
        sa.Column('is_default', sa.Boolean(), default=False),
        sa.Column('is_auto_generated', sa.Boolean(), default=False),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('subtitle_count', sa.Integer()),
        sa.Column('duration_seconds', sa.Float()),
        sa.Column('uploaded_by', sa.Integer()),
        sa.Column('uploaded_at', sa.DateTime()),
        sa.Column('last_edited_by', sa.Integer()),
        sa.Column('last_edited_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['admin_users.id']),
        sa.ForeignKeyConstraint(['last_edited_by'], ['admin_users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('video_id', 'language', name='unique_video_language')
    )

    op.create_index('idx_subtitles_video_id', 'subtitles', ['video_id'])
    op.create_index('idx_subtitles_language', 'subtitles', ['language'])

    # 创建字幕内容表
    op.create_table(
        'subtitle_contents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subtitle_id', sa.Integer(), nullable=False),
        sa.Column('sequence_number', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.Float(), nullable=False),
        sa.Column('end_time', sa.Float(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('text_clean', sa.Text()),
        sa.Column('text_vector', TSVECTOR()),
        sa.ForeignKeyConstraint(['subtitle_id'], ['subtitles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index('idx_subtitle_contents_subtitle_id', 'subtitle_contents', ['subtitle_id'])
    op.create_index('idx_subtitle_contents_time', 'subtitle_contents', ['start_time', 'end_time'])
    op.create_index('idx_subtitle_contents_text_vector', 'subtitle_contents', ['text_vector'], postgresql_using='gin')

    # 全文搜索触发器
    op.execute("""
        CREATE TRIGGER subtitle_contents_text_vector_update
        BEFORE INSERT OR UPDATE ON subtitle_contents
        FOR EACH ROW EXECUTE FUNCTION
        tsvector_update_trigger(text_vector, 'pg_catalog.simple', text_clean);
    """)


def downgrade():
    op.drop_table('subtitle_contents')
    op.drop_table('subtitles')
```

## 后端API实现

### Pydantic Schemas

```python
# backend/app/schemas/subtitle.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SubtitleBase(BaseModel):
    language: str = Field(..., description="语言代码 (ISO 639-1)")
    language_name: str = Field(..., description="语言名称")
    is_default: bool = Field(False, description="是否为默认字幕")

class SubtitleCreate(SubtitleBase):
    video_id: int
    format: str = Field(..., description="字幕格式: srt, vtt, ass")

class SubtitleUpdate(BaseModel):
    language_name: Optional[str] = None
    is_default: Optional[bool] = None
    is_verified: Optional[bool] = None

class SubtitleContentItem(BaseModel):
    sequence_number: int
    start_time: float
    end_time: float
    text: str

class SubtitleResponse(SubtitleBase):
    id: int
    video_id: int
    file_url: str
    format: str
    file_size: Optional[int]
    is_auto_generated: bool
    is_verified: bool
    subtitle_count: Optional[int]
    duration_seconds: Optional[float]
    uploaded_at: datetime
    uploaded_by: Optional[int]

    class Config:
        from_attributes = True

class SubtitleListResponse(BaseModel):
    subtitles: List[SubtitleResponse]
    total: int
```

### 管理员API (上传、编辑、删除)

```python
# backend/app/admin/subtitles.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.database import get_db
from app.models.subtitle import Subtitle, SubtitleContent
from app.models.user import AdminUser
from app.schemas.subtitle import SubtitleCreate, SubtitleUpdate, SubtitleResponse
from app.utils.dependencies import get_current_admin_user
from app.utils.minio_client import MinIOClient
import chardet
import re
from pathlib import Path

router = APIRouter(prefix="/admin/subtitles", tags=["Admin - Subtitles"])

@router.post("/upload", response_model=SubtitleResponse)
async def upload_subtitle(
    video_id: int = Form(...),
    language: str = Form(...),
    language_name: str = Form(...),
    is_default: bool = Form(False),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user),
):
    """上传字幕文件"""

    # 1. 验证视频存在
    from app.models.video import Video
    result = await db.execute(select(Video).filter(Video.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # 2. 验证文件格式
    allowed_formats = ['srt', 'vtt', 'ass', 'ssa']
    file_ext = Path(file.filename).suffix.lower().lstrip('.')
    if file_ext not in allowed_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Allowed: {', '.join(allowed_formats)}"
        )

    # 3. 读取文件内容
    content = await file.read()

    # 检测编码
    detected = chardet.detect(content)
    encoding = detected['encoding'] or 'utf-8'

    try:
        text_content = content.decode(encoding)
    except:
        text_content = content.decode('utf-8', errors='ignore')

    # 4. 上传到MinIO
    minio_client = MinIOClient()
    object_name = f"subtitles/{video_id}/{language}.{file_ext}"

    subtitle_url = await minio_client.upload_file(
        file_data=content,
        object_name=object_name,
        content_type=f"text/{file_ext}"
    )

    # 5. 解析字幕内容
    subtitle_items = parse_subtitle_file(text_content, file_ext)

    # 6. 如果设置为默认，取消其他默认字幕
    if is_default:
        await db.execute(
            update(Subtitle)
            .where(Subtitle.video_id == video_id)
            .values(is_default=False)
        )

    # 7. 创建字幕记录
    subtitle = Subtitle(
        video_id=video_id,
        language=language,
        language_name=language_name,
        file_url=subtitle_url,
        format=file_ext,
        file_size=len(content),
        is_default=is_default,
        is_auto_generated=False,
        subtitle_count=len(subtitle_items),
        duration_seconds=subtitle_items[-1]['end_time'] if subtitle_items else 0,
        uploaded_by=admin.id,
    )
    db.add(subtitle)
    await db.flush()

    # 8. 保存字幕内容 (用于搜索)
    for item in subtitle_items:
        content_item = SubtitleContent(
            subtitle_id=subtitle.id,
            sequence_number=item['sequence'],
            start_time=item['start_time'],
            end_time=item['end_time'],
            text=item['text'],
            text_clean=clean_subtitle_text(item['text']),
        )
        db.add(content_item)

    await db.commit()
    await db.refresh(subtitle)

    return subtitle


@router.get("/video/{video_id}", response_model=List[SubtitleResponse])
async def get_video_subtitles(
    video_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取视频的所有字幕"""
    result = await db.execute(
        select(Subtitle).filter(Subtitle.video_id == video_id).order_by(Subtitle.is_default.desc())
    )
    subtitles = result.scalars().all()
    return subtitles


@router.patch("/{subtitle_id}", response_model=SubtitleResponse)
async def update_subtitle(
    subtitle_id: int,
    update_data: SubtitleUpdate,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user),
):
    """更新字幕信息"""
    result = await db.execute(select(Subtitle).filter(Subtitle.id == subtitle_id))
    subtitle = result.scalar_one_or_none()

    if not subtitle:
        raise HTTPException(status_code=404, detail="Subtitle not found")

    # 如果设置为默认，取消其他默认字幕
    if update_data.is_default:
        await db.execute(
            update(Subtitle)
            .where(Subtitle.video_id == subtitle.video_id, Subtitle.id != subtitle_id)
            .values(is_default=False)
        )

    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(subtitle, field, value)

    subtitle.last_edited_by = admin.id
    subtitle.last_edited_at = datetime.utcnow()

    await db.commit()
    await db.refresh(subtitle)
    return subtitle


@router.delete("/{subtitle_id}")
async def delete_subtitle(
    subtitle_id: int,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user),
):
    """删除字幕"""
    result = await db.execute(select(Subtitle).filter(Subtitle.id == subtitle_id))
    subtitle = result.scalar_one_or_none()

    if not subtitle:
        raise HTTPException(status_code=404, detail="Subtitle not found")

    # 删除MinIO文件
    minio_client = MinIOClient()
    await minio_client.delete_file(subtitle.file_url)

    # 删除数据库记录 (级联删除contents)
    await db.delete(subtitle)
    await db.commit()

    return {"message": "Subtitle deleted successfully"}


def parse_subtitle_file(content: str, format: str) -> List[dict]:
    """解析字幕文件"""
    if format == 'srt':
        return parse_srt(content)
    elif format == 'vtt':
        return parse_vtt(content)
    elif format in ['ass', 'ssa']:
        return parse_ass(content)
    else:
        raise ValueError(f"Unsupported format: {format}")


def parse_srt(content: str) -> List[dict]:
    """解析SRT字幕"""
    items = []
    blocks = re.split(r'\n\s*\n', content.strip())

    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue

        sequence = int(lines[0])
        timecode = lines[1]
        text = '\n'.join(lines[2:])

        # 解析时间: 00:00:01,000 --> 00:00:04,000
        match = re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})', timecode)
        if match:
            h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, match.groups())
            start_time = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000
            end_time = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000

            items.append({
                'sequence': sequence,
                'start_time': start_time,
                'end_time': end_time,
                'text': text
            })

    return items


def parse_vtt(content: str) -> List[dict]:
    """解析VTT字幕"""
    items = []
    blocks = re.split(r'\n\s*\n', content.strip())
    sequence = 0

    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 2:
            continue

        # 跳过WEBVTT头和NOTE
        if lines[0].startswith('WEBVTT') or lines[0].startswith('NOTE'):
            continue

        # 如果第一行是时间码
        timecode_line = lines[0] if '-->' in lines[0] else (lines[1] if len(lines) > 1 and '-->' in lines[1] else None)
        if not timecode_line:
            continue

        text_start_idx = 1 if '-->' in lines[0] else 2
        text = '\n'.join(lines[text_start_idx:])

        # 解析时间: 00:00:01.000 --> 00:00:04.000
        match = re.match(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})\.(\d{3})', timecode_line)
        if match:
            h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, match.groups())
            start_time = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000
            end_time = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000

            sequence += 1
            items.append({
                'sequence': sequence,
                'start_time': start_time,
                'end_time': end_time,
                'text': text
            })

    return items


def parse_ass(content: str) -> List[dict]:
    """解析ASS/SSA字幕"""
    items = []
    lines = content.split('\n')
    sequence = 0

    for line in lines:
        if line.startswith('Dialogue:'):
            parts = line[9:].split(',', 9)
            if len(parts) < 10:
                continue

            start = parts[1].strip()
            end = parts[2].strip()
            text = parts[9].strip()

            # 解析时间: 0:00:01.00
            def parse_ass_time(time_str):
                match = re.match(r'(\d+):(\d{2}):(\d{2})\.(\d{2})', time_str)
                if match:
                    h, m, s, cs = map(int, match.groups())
                    return h * 3600 + m * 60 + s + cs / 100
                return 0

            sequence += 1
            items.append({
                'sequence': sequence,
                'start_time': parse_ass_time(start),
                'end_time': parse_ass_time(end),
                'text': text
            })

    return items


def clean_subtitle_text(text: str) -> str:
    """清理字幕文本 (用于搜索)"""
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    # 移除VTT样式标签
    text = re.sub(r'\{[^}]+\}', '', text)
    # 移除多余空格
    text = re.sub(r'\s+', ' ', text).strip()
    return text
```

### 公共API (前端播放器使用)

```python
# backend/app/api/subtitles.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.subtitle import Subtitle
from app.schemas.subtitle import SubtitleResponse
from typing import List

router = APIRouter(prefix="/api/v1/subtitles", tags=["Subtitles"])

@router.get("/video/{video_id}", response_model=List[SubtitleResponse])
async def get_video_subtitles(
    video_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取视频的所有字幕 (公开API)"""
    result = await db.execute(
        select(Subtitle)
        .filter(Subtitle.video_id == video_id)
        .order_by(Subtitle.is_default.desc(), Subtitle.language)
    )
    subtitles = result.scalars().all()
    return subtitles
```

### 注册路由

```python
# backend/app/main.py
from app.admin.subtitles import router as admin_subtitles_router
from app.api.subtitles import router as api_subtitles_router

app.include_router(admin_subtitles_router)
app.include_router(api_subtitles_router)
```

## 前端集成

### Video.js字幕配置

```typescript
// frontend/src/components/VideoPlayer/VideoPlayer.tsx
import React, { useEffect, useRef, useState } from 'react'
import videojs from 'video.js'
import 'video.js/dist/video-js.css'
import axios from '@/utils/axios'

interface Subtitle {
  id: number
  language: string
  language_name: string
  file_url: string
  format: string
  is_default: boolean
}

interface VideoPlayerProps {
  videoId: number
  videoUrl: string
  posterUrl?: string
}

export const VideoPlayerWithSubtitles: React.FC<VideoPlayerProps> = ({
  videoId,
  videoUrl,
  posterUrl
}) => {
  const videoRef = useRef<HTMLVideoElement>(null)
  const playerRef = useRef<any>(null)
  const [subtitles, setSubtitles] = useState<Subtitle[]>([])

  useEffect(() => {
    // 1. 获取字幕列表
    const fetchSubtitles = async () => {
      try {
        const response = await axios.get(`/api/v1/subtitles/video/${videoId}`)
        setSubtitles(response.data)
      } catch (error) {
        console.error('Failed to fetch subtitles:', error)
      }
    }
    fetchSubtitles()
  }, [videoId])

  useEffect(() => {
    if (!videoRef.current) return

    // 2. 初始化Video.js播放器
    const player = videojs(videoRef.current, {
      controls: true,
      fluid: true,
      poster: posterUrl,
      html5: {
        vhs: {
          overrideNative: true,
        },
      },
    })

    playerRef.current = player

    return () => {
      if (playerRef.current) {
        playerRef.current.dispose()
      }
    }
  }, [])

  useEffect(() => {
    if (!playerRef.current || subtitles.length === 0) return

    // 3. 添加字幕轨道到播放器
    subtitles.forEach((subtitle) => {
      // 移除旧的轨道
      const tracks = playerRef.current.remoteTextTracks()
      for (let i = tracks.length - 1; i >= 0; i--) {
        if (tracks[i].language === subtitle.language) {
          playerRef.current.removeRemoteTextTrack(tracks[i])
        }
      }

      // 添加新轨道
      playerRef.current.addRemoteTextTrack({
        kind: 'subtitles',
        label: subtitle.language_name,
        srclang: subtitle.language,
        src: subtitle.file_url,
        default: subtitle.is_default,
      }, false)
    })
  }, [subtitles])

  return (
    <div className="video-player-container">
      <div data-vjs-player>
        <video
          ref={videoRef}
          className="video-js vjs-big-play-centered"
        >
          <source src={videoUrl} type="application/x-mpegURL" />
        </video>
      </div>

      {/* 字幕信息显示 */}
      {subtitles.length > 0 && (
        <div className="subtitle-info">
          <p>可用字幕: {subtitles.map(s => s.language_name).join(', ')}</p>
        </div>
      )}
    </div>
  )
}
```

### 管理后台 - 字幕管理页面

```typescript
// admin-frontend/src/pages/Subtitles/SubtitleManagement.tsx
import React, { useState } from 'react'
import { Table, Button, Upload, Modal, Form, Select, Switch, message } from 'antd'
import { UploadOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons'
import axios from '@/utils/axios'
import type { UploadFile } from 'antd'

export const SubtitleManagement: React.FC<{ videoId: number }> = ({ videoId }) => {
  const [subtitles, setSubtitles] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [uploadModalVisible, setUploadModalVisible] = useState(false)
  const [form] = Form.useForm()

  // 获取字幕列表
  const fetchSubtitles = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`/api/v1/admin/subtitles/video/${videoId}`)
      setSubtitles(response.data)
    } catch (error) {
      message.error('获取字幕失败')
    } finally {
      setLoading(false)
    }
  }

  // 上传字幕
  const handleUpload = async (values: any) => {
    const formData = new FormData()
    formData.append('video_id', String(videoId))
    formData.append('language', values.language)
    formData.append('language_name', values.language_name)
    formData.append('is_default', String(values.is_default || false))
    formData.append('file', values.file[0].originFileObj)

    try {
      await axios.post('/api/v1/admin/subtitles/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      message.success('字幕上传成功')
      setUploadModalVisible(false)
      form.resetFields()
      fetchSubtitles()
    } catch (error) {
      message.error('字幕上传失败')
    }
  }

  // 删除字幕
  const handleDelete = async (subtitleId: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个字幕吗？',
      onOk: async () => {
        try {
          await axios.delete(`/api/v1/admin/subtitles/${subtitleId}`)
          message.success('字幕删除成功')
          fetchSubtitles()
        } catch (error) {
          message.error('字幕删除失败')
        }
      }
    })
  }

  // 设置默认字幕
  const handleSetDefault = async (subtitleId: number) => {
    try {
      await axios.patch(`/api/v1/admin/subtitles/${subtitleId}`, {
        is_default: true
      })
      message.success('已设置为默认字幕')
      fetchSubtitles()
    } catch (error) {
      message.error('设置失败')
    }
  }

  const columns = [
    {
      title: '语言',
      dataIndex: 'language_name',
      key: 'language_name',
    },
    {
      title: '格式',
      dataIndex: 'format',
      key: 'format',
      render: (format: string) => format.toUpperCase()
    },
    {
      title: '字幕条数',
      dataIndex: 'subtitle_count',
      key: 'subtitle_count',
    },
    {
      title: '时长',
      dataIndex: 'duration_seconds',
      key: 'duration_seconds',
      render: (seconds: number) => `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`
    },
    {
      title: '默认',
      dataIndex: 'is_default',
      key: 'is_default',
      render: (isDefault: boolean, record: any) => (
        <Switch
          checked={isDefault}
          onChange={() => handleSetDefault(record.id)}
        />
      )
    },
    {
      title: '来源',
      dataIndex: 'is_auto_generated',
      key: 'is_auto_generated',
      render: (isAuto: boolean) => isAuto ? 'AI生成' : '手动上传'
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, record: any) => (
        <>
          <Button
            type="link"
            icon={<DeleteOutlined />}
            danger
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </>
      )
    }
  ]

  useEffect(() => {
    fetchSubtitles()
  }, [videoId])

  return (
    <div>
      <Button
        type="primary"
        icon={<UploadOutlined />}
        onClick={() => setUploadModalVisible(true)}
        style={{ marginBottom: 16 }}
      >
        上传字幕
      </Button>

      <Table
        dataSource={subtitles}
        columns={columns}
        loading={loading}
        rowKey="id"
      />

      {/* 上传字幕弹窗 */}
      <Modal
        title="上传字幕"
        open={uploadModalVisible}
        onCancel={() => setUploadModalVisible(false)}
        onOk={() => form.submit()}
      >
        <Form form={form} onFinish={handleUpload} layout="vertical">
          <Form.Item
            name="language"
            label="语言代码"
            rules={[{ required: true, message: '请输入语言代码' }]}
          >
            <Select>
              <Select.Option value="zh">zh (中文)</Select.Option>
              <Select.Option value="en">en (English)</Select.Option>
              <Select.Option value="ja">ja (日本語)</Select.Option>
              <Select.Option value="ko">ko (한국어)</Select.Option>
              <Select.Option value="es">es (Español)</Select.Option>
              <Select.Option value="fr">fr (Français)</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="language_name"
            label="语言名称"
            rules={[{ required: true, message: '请输入语言名称' }]}
          >
            <Input placeholder="例如: 中文、English" />
          </Form.Item>

          <Form.Item
            name="file"
            label="字幕文件"
            valuePropName="fileList"
            getValueFromEvent={(e) => e.fileList}
            rules={[{ required: true, message: '请上传字幕文件' }]}
          >
            <Upload
              beforeUpload={() => false}
              maxCount={1}
              accept=".srt,.vtt,.ass,.ssa"
            >
              <Button icon={<UploadOutlined />}>选择文件 (SRT/VTT/ASS)</Button>
            </Upload>
          </Form.Item>

          <Form.Item
            name="is_default"
            label="设为默认字幕"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
```

## 字幕上传流程

```
管理员上传字幕
      ↓
验证文件格式 (SRT/VTT/ASS)
      ↓
检测文件编码 (chardet)
      ↓
解析字幕内容
      ↓
上传到MinIO (subtitles/{video_id}/{language}.{format})
      ↓
保存到数据库 (subtitles表)
      ↓
提取字幕文本 (subtitle_contents表 - 用于搜索)
      ↓
返回成功响应
      ↓
前端刷新字幕列表
      ↓
播放器自动加载字幕
```

## 字幕自动生成

### 使用Whisper AI (OpenAI)

```python
# backend/app/tasks/subtitle_generation.py
from celery import shared_task
from openai import OpenAI
from pathlib import Path
import tempfile
from app.models.subtitle import Subtitle
from app.database import SessionLocal
from app.utils.minio_client import MinIOClient

client = OpenAI(api_key=settings.OPENAI_API_KEY)

@shared_task(bind=True)
def generate_subtitle_task(self, video_id: int, language: str = 'zh'):
    """AI自动生成字幕"""
    db = SessionLocal()

    try:
        # 1. 下载视频文件
        from app.models.video import Video
        video = db.query(Video).filter(Video.id == video_id).first()

        minio_client = MinIOClient()
        video_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        minio_client.download_file(video.source_url, video_file.name)

        # 2. 提取音频 (使用FFmpeg)
        audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        subprocess.run([
            'ffmpeg',
            '-i', video_file.name,
            '-vn',  # 不处理视频
            '-acodec', 'libmp3lame',
            '-ab', '128k',
            '-y',
            audio_file.name
        ], check=True)

        # 3. 调用Whisper API生成字幕
        with open(audio_file.name, 'rb') as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="srt",  # 直接返回SRT格式
                language=language,
            )

        # 4. 上传SRT到MinIO
        srt_content = transcript.encode('utf-8')
        object_name = f"subtitles/{video_id}/{language}_auto.srt"
        subtitle_url = minio_client.upload_file(
            file_data=srt_content,
            object_name=object_name,
            content_type="text/srt"
        )

        # 5. 解析并保存到数据库
        subtitle_items = parse_srt(transcript)

        subtitle = Subtitle(
            video_id=video_id,
            language=language,
            language_name=get_language_name(language),
            file_url=subtitle_url,
            format='srt',
            file_size=len(srt_content),
            is_auto_generated=True,
            is_verified=False,  # 需要人工校对
            subtitle_count=len(subtitle_items),
            duration_seconds=subtitle_items[-1]['end_time'] if subtitle_items else 0,
        )
        db.add(subtitle)
        db.flush()

        # 保存字幕内容
        from app.models.subtitle import SubtitleContent
        for item in subtitle_items:
            content_item = SubtitleContent(
                subtitle_id=subtitle.id,
                sequence_number=item['sequence'],
                start_time=item['start_time'],
                end_time=item['end_time'],
                text=item['text'],
                text_clean=clean_subtitle_text(item['text']),
            )
            db.add(content_item)

        db.commit()

        # 6. 清理临时文件
        Path(video_file.name).unlink()
        Path(audio_file.name).unlink()

        return {
            'status': 'success',
            'subtitle_id': subtitle.id,
            'subtitle_count': len(subtitle_items)
        }

    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


def get_language_name(code: str) -> str:
    """语言代码转名称"""
    mapping = {
        'zh': '中文',
        'en': 'English',
        'ja': '日本語',
        'ko': '한국어',
        'es': 'Español',
        'fr': 'Français',
    }
    return mapping.get(code, code.upper())
```

### 触发自动生成

```python
# backend/app/admin/subtitles.py

@router.post("/generate-auto/{video_id}")
async def generate_auto_subtitle(
    video_id: int,
    language: str = 'zh',
    admin: AdminUser = Depends(get_current_admin_user),
):
    """触发AI自动生成字幕"""
    task = generate_subtitle_task.delay(video_id, language)
    return {
        'task_id': task.id,
        'message': '字幕生成任务已启动'
    }
```

## 字幕编辑器

### 在线字幕编辑器 (简化版)

```typescript
// admin-frontend/src/components/SubtitleEditor/SubtitleEditor.tsx
import React, { useState, useRef, useEffect } from 'react'
import { Table, Input, Button, InputNumber, message } from 'antd'
import { PlayCircleOutlined, PauseCircleOutlined } from '@ant-design/icons'
import axios from '@/utils/axios'

interface SubtitleItem {
  id: number
  sequence_number: number
  start_time: number
  end_time: number
  text: string
}

export const SubtitleEditor: React.FC<{ subtitleId: number }> = ({ subtitleId }) => {
  const [items, setItems] = useState<SubtitleItem[]>([])
  const [playing, setPlaying] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)

  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    const s = Math.floor(seconds % 60)
    const ms = Math.floor((seconds % 1) * 1000)
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}.${String(ms).padStart(3, '0')}`
  }

  const handleTextChange = (id: number, newText: string) => {
    setItems(prev => prev.map(item =>
      item.id === id ? { ...item, text: newText } : item
    ))
  }

  const handleTimeChange = (id: number, field: 'start_time' | 'end_time', value: number) => {
    setItems(prev => prev.map(item =>
      item.id === id ? { ...item, [field]: value } : item
    ))
  }

  const handleSave = async () => {
    try {
      await axios.post(`/api/v1/admin/subtitles/${subtitleId}/update-contents`, {
        items: items
      })
      message.success('保存成功')
    } catch (error) {
      message.error('保存失败')
    }
  }

  const columns = [
    {
      title: '#',
      dataIndex: 'sequence_number',
      width: 60,
    },
    {
      title: '开始时间',
      dataIndex: 'start_time',
      width: 150,
      render: (time: number, record: SubtitleItem) => (
        <InputNumber
          value={time}
          step={0.1}
          onChange={(val) => handleTimeChange(record.id, 'start_time', val || 0)}
          formatter={(val) => formatTime(val || 0)}
        />
      )
    },
    {
      title: '结束时间',
      dataIndex: 'end_time',
      width: 150,
      render: (time: number, record: SubtitleItem) => (
        <InputNumber
          value={time}
          step={0.1}
          onChange={(val) => handleTimeChange(record.id, 'end_time', val || 0)}
          formatter={(val) => formatTime(val || 0)}
        />
      )
    },
    {
      title: '字幕文本',
      dataIndex: 'text',
      render: (text: string, record: SubtitleItem) => (
        <Input.TextArea
          value={text}
          onChange={(e) => handleTextChange(record.id, e.target.value)}
          autoSize={{ minRows: 1, maxRows: 3 }}
        />
      )
    },
  ]

  return (
    <div>
      <Button type="primary" onClick={handleSave} style={{ marginBottom: 16 }}>
        保存修改
      </Button>

      <Table
        dataSource={items}
        columns={columns}
        rowKey="id"
        pagination={{ pageSize: 20 }}
      />
    </div>
  )
}
```

## 性能优化

### 1. 字幕文件CDN加速

```python
# 使用CloudFlare CDN缓存字幕文件
# MinIO配置公开读取权限
minio_client.set_bucket_policy(
    bucket_name='videos',
    policy={
        "Statement": [{
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::videos/subtitles/*"]
        }]
    }
)
```

### 2. 字幕内容全文搜索

```python
# backend/app/api/search.py

@router.get("/search/by-subtitle")
async def search_by_subtitle(
    query: str,
    language: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """通过字幕内容搜索视频"""

    # 使用PostgreSQL全文搜索
    stmt = select(Video).join(Subtitle).join(SubtitleContent).where(
        SubtitleContent.text_vector.match(query)
    )

    if language:
        stmt = stmt.where(Subtitle.language == language)

    result = await db.execute(stmt.distinct())
    videos = result.scalars().all()

    return videos
```

### 3. 缓存字幕列表

```python
from app.utils.cache import cache_result

@cache_result(ttl=3600)  # 缓存1小时
async def get_video_subtitles_cached(video_id: int, db: AsyncSession):
    result = await db.execute(
        select(Subtitle).filter(Subtitle.video_id == video_id)
    )
    return result.scalars().all()
```

## 总结

字幕管理系统完整功能:

✅ **多格式支持**: SRT、VTT、ASS/SSA
✅ **多语言轨道**: 每个视频支持多语言
✅ **手动上传**: 管理员上传字幕文件
✅ **AI自动生成**: Whisper API自动生成字幕
✅ **在线编辑**: 浏览器内字幕编辑器
✅ **全文搜索**: 按字幕内容搜索视频
✅ **Video.js集成**: 前端播放器自动加载字幕
✅ **性能优化**: CDN加速、缓存、全文索引

**下一步**: 根据需求实现具体功能模块。

---

**文档版本**: 1.0.0
**最后更新**: 2025-10-10
