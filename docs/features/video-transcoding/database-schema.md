# 数据库Schema设计

> **完整的数据库结构** - 支持2K/4K + 并行转码 + GPU加速

---

## 📋 概述

视频转码系统需要以下数据库表:
1. **transcoding_tasks** - 转码任务表 (新增)
2. **videos** - 视频表 (扩展现有表)
3. **transcoding_logs** - 转码日志表 (可选)

---

## 💾 完整SQL Schema

### 1. 转码任务表 (核心)

```sql
-- ==================================================
-- 转码任务表 - 跟踪每个视频的转码状态
-- ==================================================
CREATE TABLE transcoding_tasks (
    -- 主键
    id SERIAL PRIMARY KEY,
    
    -- 关联视频
    video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    
    -- 任务状态
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    -- 可选值: 'pending', 'queued', 'processing', 'completed', 'failed', 'cancelled'
    
    -- 进度跟踪
    progress INTEGER DEFAULT 0,
    -- 0-100, 转码完成百分比
    
    current_step VARCHAR(100),
    -- 当前步骤描述, 例如: "analyzing", "transcoding_1080p", "generating_hls"
    
    -- ✨ 源视频信息 (新增字段)
    source_resolution VARCHAR(20),
    -- 源视频分辨率, 例如: "3840x2160" (4K), "2560x1440" (2K), "1920x1080"
    -- 用于智能决定转码目标分辨率
    
    source_codec VARCHAR(20),
    -- 源视频编码, 例如: "h264", "hevc", "vp9"
    
    source_bitrate BIGINT,
    -- 源视频码率 (bps)
    
    source_fps FLOAT,
    -- 源视频帧率
    
    -- ✨ 转码配置 (新增字段)
    target_resolutions JSONB DEFAULT '[]',
    -- 目标分辨率列表, 例如: ["2K", "1080p", "720p", "480p", "360p"]
    
    encoding_preset VARCHAR(20) DEFAULT 'medium',
    -- FFmpeg编码预设: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
    
    -- ✨ 转码结果
    resolutions JSONB DEFAULT '{}',
    -- 已完成的分辨率和URL映射
    -- 示例: {
    --   "4K": "videos/123/hls/4K/index.m3u8",
    --   "2K": "videos/123/hls/2K/index.m3u8",
    --   "1080p": "videos/123/hls/1080p/index.m3u8",
    --   "720p": "videos/123/hls/720p/index.m3u8",
    --   "480p": "videos/123/hls/480p/index.m3u8",
    --   "360p": "videos/123/hls/360p/index.m3u8"
    -- }
    
    master_playlist_url TEXT,
    -- HLS主播放列表URL, 包含所有分辨率
    
    -- ✨ 缩略图和预览
    thumbnail_urls JSONB DEFAULT '[]',
    -- 时间轴缩略图URL列表, 例如: ["videos/123/thumbnails/thumb_0001.jpg", ...]
    
    poster_url TEXT,
    -- 封面图URL (通常是视频第5秒的截图)
    
    preview_url TEXT,
    -- ✨ 悬停预览视频URL (10秒精华片段)
    
    -- 原始文件信息
    original_file_url TEXT,
    -- 原始视频文件URL (MinIO中的路径)
    
    original_size BIGINT,
    -- 原始文件大小(字节)
    
    total_transcoded_size BIGINT,
    -- 转码后所有文件总大小(字节)
    
    -- 视频元数据
    duration FLOAT,
    -- 视频时长(秒)
    
    -- ✨ HDR支持 (新增字段)
    hdr_support BOOLEAN DEFAULT FALSE,
    -- 是否支持HDR (High Dynamic Range), 4K视频常用
    
    color_space VARCHAR(20),
    -- 色彩空间: bt709 (HD), bt2020 (4K HDR)
    
    color_transfer VARCHAR(20),
    -- 色彩传输函数: bt709, smpte2084 (HDR10), arib-std-b67 (HLG)
    
    -- ✨ GPU加速信息 (新增字段)
    gpu_accelerated BOOLEAN DEFAULT FALSE,
    -- 是否使用GPU加速
    
    gpu_type VARCHAR(50),
    -- GPU类型: nvidia_nvenc, intel_qsv, amd_vce, apple_videotoolbox
    
    transcoding_time_seconds INTEGER,
    -- 实际转码耗时(秒), 用于性能分析和优化
    
    -- ✨ Worker信息 (新增字段 - 用于调试)
    worker_id VARCHAR(100),
    -- 处理该任务的Celery worker ID, 例如: "celery@worker1"
    
    worker_hostname VARCHAR(100),
    -- Worker主机名
    
    -- 任务优先级
    priority INTEGER DEFAULT 5,
    -- 任务优先级: 1-10 (10最高)
    -- 4K视频可设置为8-10, 普通视频5, 缩略图生成1-2
    
    -- 错误处理
    error_message TEXT,
    -- 错误信息摘要
    
    error_stack TEXT,
    -- 完整错误堆栈, 用于调试
    
    retry_count INTEGER DEFAULT 0,
    -- 已重试次数
    
    max_retries INTEGER DEFAULT 3,
    -- 最大重试次数
    
    -- 时间戳
    started_at TIMESTAMP WITH TIME ZONE,
    -- 任务开始时间
    
    completed_at TIMESTAMP WITH TIME ZONE,
    -- 任务完成时间
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- 任务创建时间
    
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- 最后更新时间
    
    -- 约束
    CONSTRAINT unique_video_task UNIQUE(video_id),
    CONSTRAINT check_progress CHECK (progress >= 0 AND progress <= 100),
    CONSTRAINT check_priority CHECK (priority >= 1 AND priority <= 10),
    CONSTRAINT check_status CHECK (status IN ('pending', 'queued', 'processing', 'completed', 'failed', 'cancelled'))
);

-- ==================================================
-- 索引 - 优化查询性能
-- ==================================================

-- 状态索引 (用于查询pending/processing任务)
CREATE INDEX idx_transcoding_status ON transcoding_tasks(status);

-- 视频ID索引 (用于根据video_id快速查询)
CREATE INDEX idx_transcoding_video ON transcoding_tasks(video_id);

-- 创建时间索引 (用于按时间排序)
CREATE INDEX idx_transcoding_created ON transcoding_tasks(created_at DESC);

-- 优先级+创建时间复合索引 (用于任务队列排序)
CREATE INDEX idx_transcoding_priority ON transcoding_tasks(priority DESC, created_at);

-- Worker索引 (用于监控某个worker的任务)
CREATE INDEX idx_transcoding_worker ON transcoding_tasks(worker_id);

-- 源分辨率索引 (用于统计分析)
CREATE INDEX idx_transcoding_resolution ON transcoding_tasks(source_resolution);

-- GPU加速索引 (用于性能分析)
CREATE INDEX idx_transcoding_gpu ON transcoding_tasks(gpu_accelerated);

-- 部分索引: 只索引进行中的任务 (性能优化)
CREATE INDEX idx_transcoding_active ON transcoding_tasks(status, priority DESC)
WHERE status IN ('pending', 'queued', 'processing');

-- ==================================================
-- 触发器 - 自动更新updated_at
-- ==================================================
CREATE OR REPLACE FUNCTION update_transcoding_tasks_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_transcoding_tasks_updated_at
BEFORE UPDATE ON transcoding_tasks
FOR EACH ROW
EXECUTE FUNCTION update_transcoding_tasks_updated_at();

-- ==================================================
-- 注释 - 方便维护
-- ==================================================
COMMENT ON TABLE transcoding_tasks IS '视频转码任务表 - 支持2K/4K和并行转码';
COMMENT ON COLUMN transcoding_tasks.source_resolution IS '源视频分辨率, 用于智能决定转码档位';
COMMENT ON COLUMN transcoding_tasks.hdr_support IS '是否支持HDR, 4K视频常用';
COMMENT ON COLUMN transcoding_tasks.gpu_accelerated IS '是否使用GPU加速, 提升10倍速度';
COMMENT ON COLUMN transcoding_tasks.priority IS '任务优先级, 4K视频建议设置为8-10';
COMMENT ON COLUMN transcoding_tasks.preview_url IS '悬停预览视频URL (10秒WebM片段)';
```

### 2. 扩展videos表

```sql
-- ==================================================
-- 扩展现有videos表 - 添加转码相关字段
-- ==================================================
ALTER TABLE videos
-- HLS支持
ADD COLUMN has_hls BOOLEAN DEFAULT FALSE,
ADD COLUMN hls_master_url TEXT,
ADD COLUMN available_resolutions TEXT[] DEFAULT '{}',

-- 转码状态
ADD COLUMN transcoding_status VARCHAR(20) DEFAULT 'pending',
-- 可选值: 'pending', 'processing', 'completed', 'failed'

-- ✨ 悬停预览 (新增)
ADD COLUMN hover_preview_url TEXT,
ADD COLUMN preview_generated_at TIMESTAMP WITH TIME ZONE,

-- 视频质量信息
ADD COLUMN max_resolution VARCHAR(20),
-- 最高可用分辨率, 例如: "4K", "2K", "1080p"

ADD COLUMN video_codec VARCHAR(20),
-- 视频编码: h264, hevc, vp9

ADD COLUMN audio_codec VARCHAR(20),
-- 音频编码: aac, mp3, opus

-- 性能指标
ADD COLUMN transcoding_completed_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN transcoding_duration_seconds INTEGER;

-- 索引
CREATE INDEX idx_videos_transcoding_status ON videos(transcoding_status);
CREATE INDEX idx_videos_has_hls ON videos(has_hls);
CREATE INDEX idx_videos_max_resolution ON videos(max_resolution);
CREATE INDEX idx_videos_preview_url ON videos(hover_preview_url);

-- 注释
COMMENT ON COLUMN videos.hover_preview_url IS '悬停预览视频URL (10秒WebM片段), 鼠标hover时播放';
COMMENT ON COLUMN videos.has_hls IS '是否已生成HLS流媒体文件';
COMMENT ON COLUMN videos.max_resolution IS '最高可用分辨率 (4K, 2K, 1080p等)';
```

### 3. 转码日志表 (可选 - 用于调试)

```sql
-- ==================================================
-- 转码日志表 - 记录详细的转码步骤和日志
-- ==================================================
CREATE TABLE transcoding_logs (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES transcoding_tasks(id) ON DELETE CASCADE,
    level VARCHAR(20) NOT NULL,
    -- 日志级别: DEBUG, INFO, WARNING, ERROR
    
    message TEXT NOT NULL,
    -- 日志消息
    
    metadata JSONB,
    -- 额外的元数据, 例如: {"resolution": "1080p", "bitrate": "5000k"}
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_logs_task ON transcoding_logs(task_id, created_at DESC);
CREATE INDEX idx_logs_level ON transcoding_logs(level);

-- 注释
COMMENT ON TABLE transcoding_logs IS '转码日志表 - 记录详细的转码步骤, 用于调试';
```

---

## 📊 SQLAlchemy ORM模型

### Python模型定义

**文件**: `backend/app/models/transcoding.py`

```python
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean, BIGINT, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class TranscodingTask(Base):
    """转码任务模型"""
    
    __tablename__ = "transcoding_tasks"

    # 主键和关联
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), unique=True, nullable=False)

    # 状态
    status = Column(String(20), default='pending', nullable=False, index=True)
    progress = Column(Integer, default=0)
    current_step = Column(String(100))

    # 源视频信息
    source_resolution = Column(String(20), index=True)
    source_codec = Column(String(20))
    source_bitrate = Column(BIGINT)
    source_fps = Column(Float)

    # 转码配置
    target_resolutions = Column(JSON, default=[])
    encoding_preset = Column(String(20), default='medium')

    # 转码结果
    resolutions = Column(JSON, default={})
    master_playlist_url = Column(Text)
    thumbnail_urls = Column(JSON, default=[])
    poster_url = Column(Text)
    preview_url = Column(Text)

    # 原始文件
    original_file_url = Column(Text)
    original_size = Column(BIGINT)
    total_transcoded_size = Column(BIGINT)

    # 视频元数据
    duration = Column(Float)

    # HDR支持
    hdr_support = Column(Boolean, default=False)
    color_space = Column(String(20))
    color_transfer = Column(String(20))

    # GPU加速
    gpu_accelerated = Column(Boolean, default=False, index=True)
    gpu_type = Column(String(50))
    transcoding_time_seconds = Column(Integer)

    # Worker信息
    worker_id = Column(String(100), index=True)
    worker_hostname = Column(String(100))

    # 优先级
    priority = Column(Integer, default=5, index=True)

    # 错误处理
    error_message = Column(Text)
    error_stack = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # 时间戳
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    video = relationship("Video", back_populates="transcoding_task")

    def __repr__(self):
        return f"<TranscodingTask(id={self.id}, video_id={self.video_id}, status={self.status}, progress={self.progress}%)>"


class TranscodingLog(Base):
    """转码日志模型 (可选)"""
    
    __tablename__ = "transcoding_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("transcoding_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    level = Column(String(20), nullable=False, index=True)
    message = Column(Text, nullable=False)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    task = relationship("TranscodingTask")

    def __repr__(self):
        return f"<TranscodingLog(id={self.id}, task_id={self.task_id}, level={self.level})>"
```

### 扩展Video模型

**文件**: `backend/app/models/video.py`

```python
# 在现有Video模型中添加:

class Video(Base):
    __tablename__ = "videos"
    
    # ... 现有字段 ...
    
    # HLS支持
    has_hls = Column(Boolean, default=False, index=True)
    hls_master_url = Column(Text)
    available_resolutions = Column(ARRAY(String), default=[])
    
    # 转码状态
    transcoding_status = Column(String(20), default='pending', index=True)
    
    # 悬停预览
    hover_preview_url = Column(Text, index=True)
    preview_generated_at = Column(DateTime(timezone=True))
    
    # 视频质量信息
    max_resolution = Column(String(20), index=True)
    video_codec = Column(String(20))
    audio_codec = Column(String(20))
    
    # 性能指标
    transcoding_completed_at = Column(DateTime(timezone=True))
    transcoding_duration_seconds = Column(Integer)
    
    # 关系
    transcoding_task = relationship("TranscodingTask", back_populates="video", uselist=False)
```

---

## 🔄 Alembic迁移脚本

**文件**: `backend/alembic/versions/xxx_add_transcoding_tables.py`

```python
"""Add transcoding tables and extend videos table

Revision ID: xxx
Revises: yyy
Create Date: 2025-10-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'xxx'
down_revision = 'yyy'
branch_labels = None
depends_on = None


def upgrade():
    # 创建transcoding_tasks表
    op.create_table(
        'transcoding_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('progress', sa.Integer(), server_default='0'),
        sa.Column('current_step', sa.String(length=100)),
        
        # 源视频信息
        sa.Column('source_resolution', sa.String(length=20)),
        sa.Column('source_codec', sa.String(length=20)),
        sa.Column('source_bitrate', sa.BigInteger()),
        sa.Column('source_fps', sa.Float()),
        
        # 转码配置
        sa.Column('target_resolutions', postgresql.JSONB(), server_default='[]'),
        sa.Column('encoding_preset', sa.String(length=20), server_default='medium'),
        
        # 转码结果
        sa.Column('resolutions', postgresql.JSONB(), server_default='{}'),
        sa.Column('master_playlist_url', sa.Text()),
        sa.Column('thumbnail_urls', postgresql.JSONB(), server_default='[]'),
        sa.Column('poster_url', sa.Text()),
        sa.Column('preview_url', sa.Text()),
        
        # 原始文件
        sa.Column('original_file_url', sa.Text()),
        sa.Column('original_size', sa.BigInteger()),
        sa.Column('total_transcoded_size', sa.BigInteger()),
        
        # 视频元数据
        sa.Column('duration', sa.Float()),
        
        # HDR支持
        sa.Column('hdr_support', sa.Boolean(), server_default='false'),
        sa.Column('color_space', sa.String(length=20)),
        sa.Column('color_transfer', sa.String(length=20)),
        
        # GPU加速
        sa.Column('gpu_accelerated', sa.Boolean(), server_default='false'),
        sa.Column('gpu_type', sa.String(length=50)),
        sa.Column('transcoding_time_seconds', sa.Integer()),
        
        # Worker信息
        sa.Column('worker_id', sa.String(length=100)),
        sa.Column('worker_hostname', sa.String(length=100)),
        
        # 优先级
        sa.Column('priority', sa.Integer(), server_default='5'),
        
        # 错误处理
        sa.Column('error_message', sa.Text()),
        sa.Column('error_stack', sa.Text()),
        sa.Column('retry_count', sa.Integer(), server_default='0'),
        sa.Column('max_retries', sa.Integer(), server_default='3'),
        
        # 时间戳
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('video_id')
    )
    
    # 创建索引
    op.create_index('idx_transcoding_status', 'transcoding_tasks', ['status'])
    op.create_index('idx_transcoding_video', 'transcoding_tasks', ['video_id'])
    op.create_index('idx_transcoding_created', 'transcoding_tasks', [sa.text('created_at DESC')])
    op.create_index('idx_transcoding_priority', 'transcoding_tasks', [sa.text('priority DESC'), 'created_at'])
    op.create_index('idx_transcoding_worker', 'transcoding_tasks', ['worker_id'])
    op.create_index('idx_transcoding_resolution', 'transcoding_tasks', ['source_resolution'])
    op.create_index('idx_transcoding_gpu', 'transcoding_tasks', ['gpu_accelerated'])
    
    # 扩展videos表
    op.add_column('videos', sa.Column('has_hls', sa.Boolean(), server_default='false'))
    op.add_column('videos', sa.Column('hls_master_url', sa.Text()))
    op.add_column('videos', sa.Column('available_resolutions', postgresql.ARRAY(sa.String()), server_default='{}'))
    op.add_column('videos', sa.Column('transcoding_status', sa.String(length=20), server_default='pending'))
    op.add_column('videos', sa.Column('hover_preview_url', sa.Text()))
    op.add_column('videos', sa.Column('preview_generated_at', sa.DateTime(timezone=True)))
    op.add_column('videos', sa.Column('max_resolution', sa.String(length=20)))
    op.add_column('videos', sa.Column('video_codec', sa.String(length=20)))
    op.add_column('videos', sa.Column('audio_codec', sa.String(length=20)))
    op.add_column('videos', sa.Column('transcoding_completed_at', sa.DateTime(timezone=True)))
    op.add_column('videos', sa.Column('transcoding_duration_seconds', sa.Integer()))
    
    # 创建videos表的索引
    op.create_index('idx_videos_transcoding_status', 'videos', ['transcoding_status'])
    op.create_index('idx_videos_has_hls', 'videos', ['has_hls'])
    op.create_index('idx_videos_max_resolution', 'videos', ['max_resolution'])
    op.create_index('idx_videos_preview_url', 'videos', ['hover_preview_url'])


def downgrade():
    # 删除videos表的索引和列
    op.drop_index('idx_videos_preview_url', table_name='videos')
    op.drop_index('idx_videos_max_resolution', table_name='videos')
    op.drop_index('idx_videos_has_hls', table_name='videos')
    op.drop_index('idx_videos_transcoding_status', table_name='videos')
    
    op.drop_column('videos', 'transcoding_duration_seconds')
    op.drop_column('videos', 'transcoding_completed_at')
    op.drop_column('videos', 'audio_codec')
    op.drop_column('videos', 'video_codec')
    op.drop_column('videos', 'max_resolution')
    op.drop_column('videos', 'preview_generated_at')
    op.drop_column('videos', 'hover_preview_url')
    op.drop_column('videos', 'transcoding_status')
    op.drop_column('videos', 'available_resolutions')
    op.drop_column('videos', 'hls_master_url')
    op.drop_column('videos', 'has_hls')
    
    # 删除transcoding_tasks表
    op.drop_index('idx_transcoding_gpu', table_name='transcoding_tasks')
    op.drop_index('idx_transcoding_resolution', table_name='transcoding_tasks')
    op.drop_index('idx_transcoding_worker', table_name='transcoding_tasks')
    op.drop_index('idx_transcoding_priority', table_name='transcoding_tasks')
    op.drop_index('idx_transcoding_created', table_name='transcoding_tasks')
    op.drop_index('idx_transcoding_video', table_name='transcoding_tasks')
    op.drop_index('idx_transcoding_status', table_name='transcoding_tasks')
    op.drop_table('transcoding_tasks')
```

---

## 📊 查询示例

### 常用查询

```sql
-- 1. 获取所有待处理的任务 (按优先级排序)
SELECT id, video_id, priority, created_at
FROM transcoding_tasks
WHERE status = 'pending'
ORDER BY priority DESC, created_at;

-- 2. 获取正在处理的任务
SELECT t.id, t.video_id, v.title, t.progress, t.current_step, t.worker_id
FROM transcoding_tasks t
JOIN videos v ON t.video_id = v.id
WHERE t.status = 'processing';

-- 3. 获取失败的任务 (需要重试)
SELECT id, video_id, error_message, retry_count, max_retries
FROM transcoding_tasks
WHERE status = 'failed' AND retry_count < max_retries;

-- 4. 统计各分辨率的转码情况
SELECT 
    source_resolution,
    COUNT(*) as total_tasks,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
    AVG(transcoding_time_seconds) as avg_time
FROM transcoding_tasks
GROUP BY source_resolution;

-- 5. GPU vs CPU性能对比
SELECT 
    gpu_accelerated,
    COUNT(*) as total,
    AVG(transcoding_time_seconds) as avg_time,
    MIN(transcoding_time_seconds) as min_time,
    MAX(transcoding_time_seconds) as max_time
FROM transcoding_tasks
WHERE status = 'completed' AND transcoding_time_seconds IS NOT NULL
GROUP BY gpu_accelerated;

-- 6. 获取某个视频的完整转码信息
SELECT 
    t.*,
    v.title,
    v.has_hls,
    v.max_resolution
FROM transcoding_tasks t
JOIN videos v ON t.video_id = v.id
WHERE v.id = 123;

-- 7. 查找转码时间最长的10个视频
SELECT 
    t.video_id,
    v.title,
    t.source_resolution,
    t.transcoding_time_seconds,
    t.gpu_accelerated
FROM transcoding_tasks t
JOIN videos v ON t.video_id = v.id
WHERE t.status = 'completed'
ORDER BY t.transcoding_time_seconds DESC
LIMIT 10;
```

---

## 🔧 维护操作

### 清理旧任务

```sql
-- 删除30天前已完成的任务
DELETE FROM transcoding_tasks
WHERE status = 'completed'
  AND completed_at < NOW() - INTERVAL '30 days';

-- 删除失败且超过最大重试次数的任务
DELETE FROM transcoding_tasks
WHERE status = 'failed'
  AND retry_count >= max_retries
  AND created_at < NOW() - INTERVAL '7 days';
```

### 性能监控

```sql
-- 查看表大小
SELECT
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
    pg_size_pretty(pg_relation_size(relid)) AS table_size,
    pg_size_pretty(pg_total_relation_size(relid) - pg_relation_size(relid)) AS index_size
FROM pg_catalog.pg_statio_user_tables
WHERE relname IN ('transcoding_tasks', 'videos')
ORDER BY pg_total_relation_size(relid) DESC;

-- 查看慢查询
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
  AND tablename = 'transcoding_tasks'
ORDER BY idx_scan DESC;
```

---

**文档版本**: 1.0.0
**创建时间**: 2025-10-10
**作者**: Claude AI
