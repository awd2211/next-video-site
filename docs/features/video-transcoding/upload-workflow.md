# 边上传边转码工作流

> **零等待转码** - 上传完成立即开始转码，无缝集成

---

## 📋 功能概述

传统工作流存在的问题：
```
上传视频(10分钟) → 等待 → 手动触发转码 → 转码(30分钟) = 总计40分钟 + 人工操作
```

优化后的工作流：
```
上传视频(10分钟) → 自动触发转码(30分钟并行) = 总计10分钟 + 自动化 ⚡
```

### 核心优势

- ✅ **零等待**: 上传完成立即开始转码
- ✅ **自动化**: 无需人工干预
- ✅ **并行处理**: 上传下一个视频时，前一个正在转码
- ✅ **实时反馈**: 管理员可实时查看转码进度
- ✅ **失败重试**: 转码失败自动重试，无需重新上传

---

## 🏗️ 完整工作流架构

```
┌───────────────────────────────────────────────────────────────────┐
│              管理员后台 - 视频上传页面                             │
│  /admin/videos/upload                                              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │  [拖拽文件或点击上传]                                    │     │
│  │                                                           │     │
│  │  选择文件: movie_4k.mp4 (3GB)                           │     │
│  │  ┌─────────────────────────────────────────────────┐    │     │
│  │  │ 上传进度: ▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░ 85% (2.55GB/3GB)    │    │     │
│  │  └─────────────────────────────────────────────────┘    │     │
│  │                                                           │     │
│  │  预计剩余时间: 1分30秒                                   │     │
│  │  上传速度: 20MB/s                                        │     │
│  └──────────────────────────────────────────────────────────┘     │
└─────────────────────────┬─────────────────────────────────────────┘
                          │ 1. 分片上传 (5MB/片)
                          ▼
┌───────────────────────────────────────────────────────────────────┐
│      FastAPI Backend - 上传API                                     │
│      backend/app/admin/upload.py                                   │
│                                                                     │
│  Step 1: init_multipart_upload()                                   │
│  ─────────────────────────────────────────────────────────────     │
│  POST /api/v1/admin/upload/init-multipart                          │
│  Body: {                                                            │
│    "filename": "movie_4k.mp4",                                     │
│    "file_size": 3221225472,  // 3GB                                │
│    "file_type": "video/mp4"                                        │
│  }                                                                  │
│  Response: {                                                        │
│    "upload_id": "abc123...",                                       │
│    "chunk_size": 5242880     // 5MB                                │
│  }                                                                  │
│                                                                     │
│  Step 2: upload_chunk() × 600次                                    │
│  ─────────────────────────────────────────────────────────────     │
│  POST /api/v1/admin/upload/upload-chunk                            │
│  Body (FormData):                                                   │
│    upload_id: "abc123..."                                          │
│    chunk_index: 0-599                                              │
│    total_chunks: 600                                               │
│    file: <binary data 5MB>                                         │
│  Response: {                                                        │
│    "progress": 85.5,                                               │
│    "uploaded_chunks": 513,                                         │
│    "total_chunks": 600                                             │
│  }                                                                  │
│  存储: /tmp/uploads/abc123/chunk_{0-599}                           │
│                                                                     │
│  Step 3: complete_multipart_upload() ⭐ 关键步骤                  │
│  ─────────────────────────────────────────────────────────────     │
│  POST /api/v1/admin/upload/complete-multipart                      │
│  Body: {                                                            │
│    "upload_id": "abc123...",                                       │
│    "video_id": 456,                                                │
│    "upload_type": "video"                                          │
│  }                                                                  │
│                                                                     │
│  处理流程:                                                          │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │ 1. 验证所有分片完整性                                     │     │
│  │    ✓ 检查600个分片全部存在                               │     │
│  ├──────────────────────────────────────────────────────────┤     │
│  │ 2. 合并分片                                               │     │
│  │    merged_file = BytesIO()                                │     │
│  │    for i in range(600):                                   │     │
│  │        chunk = read(f"chunk_{i}")                         │     │
│  │        merged_file.write(chunk)                           │     │
│  │    ✓ 合并完成: 3GB完整文件                               │     │
│  ├──────────────────────────────────────────────────────────┤     │
│  │ 3. 上传到MinIO                                            │     │
│  │    object_name = "videos/456/original/source.mp4"        │     │
│  │    minio_client.upload(merged_file, object_name)          │     │
│  │    ✓ 上传成功                                            │     │
│  ├──────────────────────────────────────────────────────────┤     │
│  │ 4. 创建数据库记录                                         │     │
│  │    • videos表: INSERT (video_id=456, ...)               │     │
│  │    • transcoding_tasks表:                                │     │
│  │      INSERT (video_id=456, status='pending')             │     │
│  │    ✓ 数据库记录创建                                      │     │
│  ├──────────────────────────────────────────────────────────┤     │
│  │ 5. ✨ 立即触发转码任务 (核心!!!)                        │     │
│  │                                                           │     │
│  │    from app.tasks.video_transcoding import (             │     │
│  │        transcode_video_task                              │     │
│  │    )                                                      │     │
│  │                                                           │     │
│  │    # Celery异步任务 - 不阻塞HTTP响应                    │     │
│  │    transcode_video_task.delay(                           │     │
│  │        video_id=456,                                      │     │
│  │        source_url="videos/456/original/source.mp4"       │     │
│  │    )                                                      │     │
│  │                                                           │     │
│  │    ✓ 转码任务已加入队列                                 │     │
│  ├──────────────────────────────────────────────────────────┤     │
│  │ 6. 清理临时文件                                           │     │
│  │    shutil.rmtree("/tmp/uploads/abc123")                  │     │
│  │    ✓ 临时文件已删除                                      │     │
│  ├──────────────────────────────────────────────────────────┤     │
│  │ 7. 返回HTTP 200 (耗时: ~30秒)                           │     │
│  │    Response: {                                            │     │
│  │      "url": "videos/456/original/source.mp4",            │     │
│  │      "message": "上传成功，转码任务已启动",              │     │
│  │      "transcoding_status": "pending"                      │     │
│  │    }                                                      │     │
│  └──────────────────────────────────────────────────────────┘     │
└─────────────────────────┬─────────────────────────────────────────┘
                          │ 2. Celery异步任务
                          ▼
┌───────────────────────────────────────────────────────────────────┐
│      Redis 任务队列                                                │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │  Queue: high_priority                                     │     │
│  │  • Task 1: transcode_video(video_id=456)  ← 刚加入      │     │
│  │  • Task 2: transcode_video(video_id=455)  (处理中)      │     │
│  └──────────────────────────────────────────────────────────┘     │
└─────────────────────────┬─────────────────────────────────────────┘
                          │ 3. Worker拉取任务
                          ▼
┌───────────────────────────────────────────────────────────────────┐
│      Celery Worker #1                                              │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │  正在处理: transcode_video(video_id=456)                 │     │
│  │                                                           │     │
│  │  Step 1: 下载原始视频 (5%)                              │     │
│  │  Step 2: 分析视频元数据 (10%)                            │     │
│  │  Step 3: 决定转码分辨率 (15%)                            │     │
│  │  Step 4: 并行转码5个分辨率 (15-70%)                      │     │
│  │  Step 5: 生成HLS切片 (70-85%)                            │     │
│  │  Step 6: 生成缩略图 (85-95%)                             │     │
│  │  Step 7: 上传到MinIO (95-99%)                            │     │
│  │  Step 8: 完成 (100%) ✅                                  │     │
│  │                                                           │     │
│  │  预计完成时间: 15分钟后                                  │     │
│  └──────────────────────────────────────────────────────────┘     │
└───────────────────────────────────────────────────────────────────┘
                          │
                          │ 同时，管理员可以继续上传下一个视频
                          │
┌───────────────────────────────────────────────────────────────────┐
│      管理员后台 - 转码状态监控                                     │
│  /admin/videos/456/transcoding                                     │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │  视频: movie_4k.mp4                                       │     │
│  │  状态: 转码中                                             │     │
│  │                                                           │     │
│  │  总体进度: ▓▓▓▓▓▓▓░░░░░ 65%                             │     │
│  │                                                           │     │
│  │  当前步骤: 正在转码1080p                                 │     │
│  │                                                           │     │
│  │  已完成:                                                  │     │
│  │  ✓ 2K (2560x1440) - 5.4GB                               │     │
│  │  ✓ 720p (1280x720) - 1.1GB                              │     │
│  │  ⏳ 1080p (1920x1080) - 处理中...                       │     │
│  │  ⏸ 480p - 等待中                                         │     │
│  │  ⏸ 360p - 等待中                                         │     │
│  │                                                           │     │
│  │  预计剩余时间: 8分钟                                      │     │
│  │                                                           │     │
│  │  [重试] [取消] [查看日志]                                │     │
│  └──────────────────────────────────────────────────────────┘     │
└───────────────────────────────────────────────────────────────────┘
```

---

## 💻 核心代码实现

### 1. 后端上传完成钩子

**文件**: `backend/app/admin/upload.py`

```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import AdminUser
from app.models.video import Video
from app.models.transcoding import TranscodingTask
from app.utils.dependencies import get_current_admin_user
from app.utils.minio_client import minio_client
from app.tasks.video_transcoding import transcode_video_task  # ⭐ 导入Celery任务
import shutil
import os
import io
from datetime import datetime

router = APIRouter()

# 临时存储分片信息（生产环境应使用Redis）
upload_sessions = {}


@router.post("/complete-multipart")
async def complete_multipart_upload(
    upload_id: str = Form(...),
    video_id: Optional[int] = Form(None),
    upload_type: str = Form("video"),  # video, poster, backdrop
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    完成分片上传并触发转码

    ⭐ 核心功能: 上传完成后立即触发转码任务
    """
    if upload_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="上传会话不存在")

    session = upload_sessions[upload_id]

    # 1. 检查是否所有分片都已上传
    expected_chunks = list(range(session["total_chunks"]))
    uploaded_chunks = sorted(session["uploaded_chunks"])

    if uploaded_chunks != expected_chunks:
        missing = set(expected_chunks) - set(uploaded_chunks)
        raise HTTPException(
            status_code=400,
            detail=f"缺少分片: {missing}"
        )

    # 2. 合并分片
    temp_dir = f"/tmp/uploads/{upload_id}"
    merged_file = io.BytesIO()

    for i in range(session["total_chunks"]):
        chunk_path = f"{temp_dir}/chunk_{i}"
        with open(chunk_path, "rb") as f:
            merged_file.write(f.read())

    merged_file.seek(0)

    # 3. 上传到MinIO
    try:
        ext = session["filename"].split(".")[-1]
        timestamp = int(datetime.utcnow().timestamp())

        if upload_type == "video":
            object_name = f"videos/{video_id}/original/source.{ext}"
            url = minio_client.upload_video(
                merged_file,
                object_name,
                session["file_type"]
            )

            # ✨✨✨ 4. 立即触发转码任务 (核心!!!) ✨✨✨
            # 创建转码任务记录
            transcoding_task = TranscodingTask(
                video_id=video_id,
                status='pending',
                progress=0,
                original_file_url=url,
                original_size=session["file_size"]
            )
            db.add(transcoding_task)
            await db.commit()
            await db.refresh(transcoding_task)

            # Celery异步任务 - 不阻塞HTTP响应
            # delay()方法会立即返回,任务在后台执行
            transcode_video_task.delay(
                video_id=video_id,
                source_url=url
            )

            print(f"✅ 转码任务已触发: video_id={video_id}")

        elif upload_type == "poster":
            object_name = f"posters/{video_id}/poster_{timestamp}.{ext}"
            url = minio_client.upload_image(merged_file, object_name, session["file_type"])
        else:
            object_name = f"backdrops/{video_id}/backdrop_{timestamp}.{ext}"
            url = minio_client.upload_image(merged_file, object_name, session["file_type"])

        # 5. 清理临时文件
        shutil.rmtree(temp_dir, ignore_errors=True)

        # 6. 清理会话
        del upload_sessions[upload_id]

        return {
            "url": url,
            "message": "文件上传完成，转码任务已启动" if upload_type == "video" else "文件上传完成",
            "transcoding_status": "pending" if upload_type == "video" else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")
```

### 2. Celery转码任务

**文件**: `backend/app/tasks/video_transcoding.py`

```python
from celery import Celery, Task
from celery.utils.log import get_task_logger
from app.config import settings
from app.database import SessionLocal
from app.models.transcoding import TranscodingTask
from sqlalchemy import select
from datetime import datetime

logger = get_task_logger(__name__)

# Celery配置
celery_app = Celery(
    'videosite',
    broker=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0',
    backend=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/1'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,  # 重要: 跟踪任务启动
    task_send_sent_event=True,
)


class TranscodingTaskBase(Task):
    """转码任务基类"""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败回调"""
        video_id = kwargs.get('video_id')
        if video_id:
            db = SessionLocal()
            try:
                result = db.execute(
                    select(TranscodingTask).filter_by(video_id=video_id)
                )
                task = result.scalar_one_or_none()
                if task:
                    task.status = 'failed'
                    task.error_message = str(exc)
                    task.retry_count += 1
                    db.commit()
            finally:
                db.close()


@celery_app.task(
    base=TranscodingTaskBase,
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 300}  # 5分钟后重试
)
def transcode_video_task(self, video_id: int, source_url: str):
    """
    主转码任务

    此任务会在上传完成后立即由Celery Worker执行

    Args:
        video_id: 视频ID
        source_url: MinIO中的原始视频URL
    """
    db = SessionLocal()

    try:
        # 1. 更新任务状态为processing
        result = db.execute(
            select(TranscodingTask).filter_by(video_id=video_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(f"Transcoding task not found for video {video_id}")

        task.status = 'processing'
        task.started_at = datetime.utcnow()
        task.worker_id = self.request.hostname  # 记录worker ID
        db.commit()

        logger.info(f"🎬 开始转码视频 {video_id}, Worker: {self.request.hostname}")

        # 2. 下载原始视频
        # 3. 分析视频
        # 4. 转码
        # 5. 生成HLS
        # 6. 生成缩略图
        # 7. 上传到MinIO
        # 8. 更新数据库
        # ... (详细实现见architecture.md)

        logger.info(f"✅ 视频转码完成 {video_id}")

        return {
            'status': 'success',
            'video_id': video_id
        }

    except Exception as e:
        logger.error(f"❌ 视频转码失败 {video_id}: {str(e)}")
        raise

    finally:
        db.close()
```

### 3. 转码状态查询API

**文件**: `backend/app/api/videos.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.transcoding import TranscodingTask

router = APIRouter()


@router.get("/videos/{video_id}/transcoding-status")
async def get_transcoding_status(
    video_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    查询视频转码状态

    前端可以轮询此API来获取实时进度
    """
    result = await db.execute(
        select(TranscodingTask).filter_by(video_id=video_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        return {
            "status": "not_found",
            "message": "转码任务不存在"
        }

    return {
        "status": task.status,  # pending, processing, completed, failed
        "progress": task.progress,  # 0-100
        "current_step": task.current_step,  # "转码1080p", "生成HLS"等
        "resolutions": task.resolutions,  # 已完成的分辨率
        "error_message": task.error_message if task.status == 'failed' else None,
        "started_at": task.started_at,
        "completed_at": task.completed_at,
        "estimated_time_remaining": calculate_eta(task)  # 预计剩余时间
    }


def calculate_eta(task: TranscodingTask) -> Optional[int]:
    """计算预计剩余时间(秒)"""
    if task.status != 'processing' or not task.started_at:
        return None

    elapsed = (datetime.utcnow() - task.started_at).total_seconds()
    if task.progress == 0:
        return None

    # 简单线性估算
    total_estimated = elapsed / (task.progress / 100)
    remaining = total_estimated - elapsed
    return int(remaining)
```

### 4. 前端实时进度监控

**文件**: `admin-frontend/src/pages/Videos/TranscodingStatus.tsx`

```typescript
import React, { useState, useEffect } from 'react'
import { Progress, Card, Descriptions, Tag, Button } from 'antd'
import { CheckCircleOutlined, SyncOutlined, CloseCircleOutlined } from '@ant-design/icons'
import axios from 'axios'

interface TranscodingStatusProps {
  videoId: number
}

const TranscodingStatus: React.FC<TranscodingStatusProps> = ({ videoId }) => {
  const [status, setStatus] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  // 轮询获取转码状态
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await axios.get(`/api/v1/videos/${videoId}/transcoding-status`)
        setStatus(response.data)
        setLoading(false)

        // 如果still processing, 继续轮询
        if (response.data.status === 'processing' || response.data.status === 'pending') {
          setTimeout(fetchStatus, 2000) // 每2秒轮询一次
        }
      } catch (error) {
        console.error('获取转码状态失败:', error)
        setLoading(false)
      }
    }

    fetchStatus()
  }, [videoId])

  if (loading) {
    return <div>加载中...</div>
  }

  if (!status) {
    return <div>未找到转码任务</div>
  }

  const getStatusTag = () => {
    switch (status.status) {
      case 'pending':
        return <Tag icon={<SyncOutlined spin />} color="processing">排队中</Tag>
      case 'processing':
        return <Tag icon={<SyncOutlined spin />} color="processing">转码中</Tag>
      case 'completed':
        return <Tag icon={<CheckCircleOutlined />} color="success">已完成</Tag>
      case 'failed':
        return <Tag icon={<CloseCircleOutlined />} color="error">失败</Tag>
      default:
        return <Tag>{status.status}</Tag>
    }
  }

  return (
    <Card title="转码状态" extra={getStatusTag()}>
      <Progress
        percent={status.progress}
        status={status.status === 'failed' ? 'exception' : status.status === 'completed' ? 'success' : 'active'}
        strokeWidth={15}
      />

      <Descriptions column={2} style={{ marginTop: 20 }}>
        <Descriptions.Item label="当前步骤">{status.current_step || '-'}</Descriptions.Item>
        <Descriptions.Item label="预计剩余">
          {status.estimated_time_remaining ? `${Math.round(status.estimated_time_remaining / 60)}分钟` : '-'}
        </Descriptions.Item>
        <Descriptions.Item label="已完成分辨率">
          {Object.keys(status.resolutions || {}).join(', ') || '无'}
        </Descriptions.Item>
      </Descriptions>

      {status.status === 'failed' && (
        <div style={{ marginTop: 20, color: 'red' }}>
          错误信息: {status.error_message}
          <Button type="link" onClick={() => retryTranscoding(videoId)}>
            重试
          </Button>
        </div>
      )}
    </Card>
  )
}

async function retryTranscoding(videoId: number) {
  try {
    await axios.post(`/api/v1/admin/transcoding/${videoId}/retry`)
    message.success('转码任务已重新提交')
    window.location.reload()
  } catch (error) {
    message.error('重试失败')
  }
}

export default TranscodingStatus
```

---

## 📊 工作流时序图

```
时间轴 | 管理员操作                | 后端处理                    | Worker处理
───────┼──────────────────────────┼───────────────────────────┼────────────────────────
00:00  │ 选择4K视频 (3GB)         │                            │
00:00  │ 点击上传                  │                            │
00:00  │ ↓                        │ 接收init请求               │
00:00  │ 开始上传分片 (5MB/片)    │ 创建upload_id              │
00:01  │ 上传进度: 10%            │ 保存chunk_0-60             │
00:02  │ 上传进度: 20%            │ 保存chunk_61-120           │
00:05  │ 上传进度: 50%            │ 保存chunk_121-300          │
00:08  │ 上传进度: 80%            │ 保存chunk_301-480          │
00:10  │ 上传进度: 100% ✅        │ 保存chunk_481-600 (完成)  │
00:10  │ ↓                        │ ↓                          │
00:10  │ 触发complete_multipart   │ 合并600个分片 (30秒)       │
00:10  │                          │ 上传到MinIO (完整3GB)       │
00:10  │                          │ 创建数据库记录              │
00:10  │                          │ ✨ 触发Celery任务          │
00:10  │                          │ 返回HTTP 200 ✅            │
00:10  │ 收到成功响应              │                            │
00:10  │ "上传成功,转码中..."     │                            │
00:10  │                          │                            │ Worker拉取任务 ⚡
00:11  │ 管理员继续上传下一个      │                            │ 下载原始视频 (5%)
00:12  │ (可以并行操作!)          │                            │ 分析视频 (10%)
00:13  │                          │                            │ 决定分辨率 (15%)
00:15  │                          │                            │ 并行转码 (15-70%)
00:20  │                          │                            │ ├─ 2K (处理中)
00:20  │                          │                            │ ├─ 1080p (处理中)
00:20  │                          │                            │ ├─ 720p (完成✅)
00:20  │                          │                            │ ├─ 480p (完成✅)
00:20  │                          │                            │ └─ 360p (完成✅)
00:23  │                          │                            │ 所有分辨率完成 ✅
00:24  │                          │                            │ 生成HLS (70-85%)
00:25  │                          │                            │ 生成缩略图 (85-95%)
00:26  │                          │                            │ 上传到MinIO (95-99%)
00:27  │                          │                            │ 更新数据库 (100%)
00:27  │                          │                            │ 转码完成 ✅✅✅
00:27  │ 查看转码状态              │ 返回completed状态          │
00:27  │ ✅ 转码完成               │                            │
```

**总结**:
- 上传耗时: 10分钟
- 转码耗时: 17分钟 (并行,在后台进行)
- 管理员等待: 0分钟 (上传完成即可继续其他操作)
- **效率提升**: 从40分钟串行 → 10分钟 + 自动化

---

## 🎯 最佳实践

### 1. 使用WebSocket替代轮询 (优化)

```typescript
// frontend: 使用WebSocket获取实时进度
const ws = new WebSocket(`ws://localhost:8000/ws/transcoding/${videoId}`)

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  setProgress(data.progress)
  setCurrentStep(data.current_step)
}
```

### 2. 断点续传支持

如果上传中断,可以从上次的chunk继续:

```typescript
// 前端检查已上传的chunks
const statusResponse = await axios.get(`/api/v1/admin/upload/upload-status/${uploadId}`)
const missingChunks = statusResponse.data.missing_chunks

// 只上传缺失的chunks
for (const chunkIndex of missingChunks) {
  await uploadChunk(chunkIndex)
}
```

### 3. 任务优先级

4K视频优先转码:

```python
# 根据分辨率设置不同队列
if source_height >= 2160:  # 4K
    transcode_video_task.apply_async(
        args=[video_id, source_url],
        queue='high_priority',
        priority=10
    )
else:
    transcode_video_task.apply_async(
        args=[video_id, source_url],
        queue='normal',
        priority=5
    )
```

---

## 🔧 监控和调试

### 使用Flower监控Celery

```bash
# 启动Flower
celery -A app.tasks.transcoding flower --port=5555

# 访问: http://localhost:5555
# 可以看到:
# - 活跃的任务
# - 完成的任务
# - 失败的任务
# - Worker状态
# - 任务详细日志
```

### 日志记录

```python
import logging

logger = logging.getLogger(__name__)

# 在转码过程中记录详细日志
logger.info(f"视频 {video_id} 转码开始")
logger.info(f"源分辨率: {source_height}p, 时长: {duration}s")
logger.info(f"目标分辨率: {target_resolutions}")
logger.info(f"转码完成, 耗时: {elapsed_time}s")
```

---

**文档版本**: 1.0.0
**创建时间**: 2025-10-10
**作者**: Claude AI
