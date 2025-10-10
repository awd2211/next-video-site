# 视频悬停预览功能

> **YouTube/Netflix风格的鼠标悬停动态预览** - 提升用户视频浏览体验

---

## 📋 功能概述

当用户在视频列表页面将鼠标悬停在视频卡片上时,自动播放该视频的动态预览片段,类似YouTube和Netflix的体验。

###  效果演示

```
┌─────────────────────────────────┐
│  [静态封面图]                    │  鼠标移开
│  视频标题                         │  ◄─────────
│  观看次数 • 发布时间               │
└─────────────────────────────────┘
            │
            │ 鼠标悬停 500ms
            ▼
┌─────────────────────────────────┐
│  [🎬 动态预览视频播放中...]       │  鼠标悬停
│  视频标题                         │  ─────────►
│  观看次数 • 发布时间               │
│  [进度条: ▓▓▓░░░ 40%]            │
└─────────────────────────────────┘
```

### 核心特性

- ✅ **自动播放**: 鼠标悬停500ms后自动播放预览
- ✅ **流畅过渡**: 封面图到预览视频无缝切换
- ✅ **懒加载**: 仅在需要时加载预览视频
- ✅ **性能优化**: 低码率预览 (480p, 500kbps)
- ✅ **精华片段**: 10秒最精彩片段或智能截取
- ✅ **静音播放**: 默认静音,hover播放不干扰用户
- ✅ **移动端适配**: 移动端点击预览,PC端hover预览

---

## 🎯 技术方案

### 方案对比

| 方案 | 优点 | 缺点 | 推荐 |
|------|------|------|------|
| **A. 预览视频片段** | 流畅连贯 | 存储增加 | ⭐⭐⭐⭐⭐ 推荐 |
| B. 缩略图序列 | 存储少 | 不够流畅 | ⭐⭐⭐ |
| C. GIF动图 | 兼容性好 | 文件大,画质差 | ⭐⭐ |

**选择方案A**: 生成10秒预览视频片段

---

## 🔧 技术实现

### 1. 后端 - 预览视频生成

#### 1.1 在转码任务中生成预览

**文件**: `backend/app/tasks/video_transcoding.py`

```python
def generate_hover_preview(
    input_path: Path,
    output_dir: Path,
    duration: float
) -> Path:
    """
    生成10秒悬停预览视频

    Args:
        input_path: 原始视频路径
        duration: 视频总时长(秒)

    Returns:
        预览视频路径
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    preview_path = output_dir / 'hover_preview.webm'

    # 🎯 策略1: 从视频中间截取10秒精华片段
    # 跳过前10%和后10%,从中间开始
    start_time = max(10, duration * 0.1)
    preview_duration = min(10, duration * 0.3)  # 最多10秒或30%时长

    cmd = [
        'ffmpeg',
        '-ss', str(start_time),  # 从start_time开始
        '-i', str(input_path),
        '-t', str(preview_duration),  # 截取preview_duration秒

        # 视频编码 - 低码率优化
        '-c:v', 'libvpx-vp9',  # VP9编码(WebM容器)
        '-vf', 'scale=854:480',  # 480p分辨率
        '-b:v', '500k',  # 500kbps码率
        '-maxrate', '600k',
        '-bufsize', '1000k',
        '-deadline', 'realtime',  # 快速编码

        # 音频 - 低码率或禁用
        '-an',  # 禁用音频(悬停预览通常静音)

        # 其他优化
        '-threads', '4',
        '-tile-columns', '2',  # VP9优化
        '-frame-parallel', '1',
        '-auto-alt-ref', '1',
        '-lag-in-frames', '25',

        '-y',
        str(preview_path)
    ]

    logger.info(f"Generating hover preview: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.warning(f"Hover preview generation failed: {result.stderr}")
        # 不是致命错误,继续转码流程
        return None

    logger.info(f"Hover preview generated: {preview_path} ({preview_path.stat().st_size} bytes)")
    return preview_path
```

#### 1.2 集成到转码流程

```python
@celery_app.task(base=TranscodingTaskBase, bind=True, max_retries=3)
def transcode_video(self, video_id: int):
    """主转码任务"""
    # ... 现有转码逻辑 ...

    # 9. 生成缩略图
    task.current_step = 'generating_thumbnails'
    task.progress = 90
    db.commit()

    thumbnails = generate_thumbnails(
        input_path=original_path,
        output_dir=temp_dir / 'thumbnails',
        duration=video_info['duration']
    )

    # ✨ 10. 生成悬停预览视频 (新增)
    task.current_step = 'generating_hover_preview'
    task.progress = 95
    db.commit()

    preview_path = generate_hover_preview(
        input_path=original_path,
        output_dir=temp_dir / 'preview',
        duration=video_info['duration']
    )

    # 上传预览视频到MinIO
    preview_url = None
    if preview_path and preview_path.exists():
        preview_url = minio_client.upload_file(
            bucket=settings.MINIO_BUCKET,
            object_name=f"videos/{video_id}/preview/hover.webm",
            file_path=str(preview_path),
            content_type='video/webm'
        )
        logger.info(f"Preview uploaded: {preview_url}")

    # ... 更新数据库 ...
    video.hover_preview_url = preview_url  # 新字段
    task.preview_url = preview_url
    db.commit()
```

### 2. 数据库扩展

**扩展 `videos` 表**:

```sql
ALTER TABLE videos
ADD COLUMN hover_preview_url TEXT,
ADD COLUMN preview_generated_at TIMESTAMP WITH TIME ZONE;

-- 索引
CREATE INDEX idx_videos_preview_url ON videos(hover_preview_url);

-- 注释
COMMENT ON COLUMN videos.hover_preview_url IS '悬停预览视频URL (10秒WebM片段)';
```

**扩展 `transcoding_tasks` 表**:

```sql
ALTER TABLE transcoding_tasks
ADD COLUMN preview_url TEXT,
ADD COLUMN preview_size_bytes BIGINT;

COMMENT ON COLUMN transcoding_tasks.preview_url IS '悬停预览视频URL';
```

### 3. 后端API

**文件**: `backend/app/api/videos.py`

```python
from app.schemas.video import VideoListResponse

@router.get("/videos", response_model=PaginatedResponse)
async def list_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取视频列表 (含预览URL)"""

    # ... 查询逻辑 ...

    # 返回数据包含hover_preview_url
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{
            "id": video.id,
            "title": video.title,
            "poster_url": video.poster_url,
            "hover_preview_url": video.hover_preview_url,  # ✨ 新增字段
            # ... 其他字段 ...
        } for video in videos]
    }
```

### 4. 前端实现

#### 4.1 VideoCard组件升级

**文件**: `frontend/src/components/VideoCard/VideoCardWithPreview.tsx`

```typescript
import React, { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Video } from '@/types'

interface VideoCardWithPreviewProps {
  video: Video
}

const VideoCardWithPreview: React.FC<VideoCardWithPreviewProps> = ({ video }) => {
  const [showPreview, setShowPreview] = useState(false)
  const [previewLoaded, setPreviewLoaded] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  const hoverTimerRef = useRef<NodeJS.Timeout | null>(null)

  // 鼠标进入 - 延迟500ms后显示预览
  const handleMouseEnter = () => {
    if (!video.hover_preview_url) return

    hoverTimerRef.current = setTimeout(() => {
      setShowPreview(true)
    }, 500) // 500ms延迟,避免误触
  }

  // 鼠标离开 - 立即隐藏预览
  const handleMouseLeave = () => {
    if (hoverTimerRef.current) {
      clearTimeout(hoverTimerRef.current)
      hoverTimerRef.current = null
    }
    setShowPreview(false)
    setPreviewLoaded(false)
  }

  // 预览视频加载完成后自动播放
  useEffect(() => {
    if (showPreview && videoRef.current) {
      videoRef.current.play().catch(err => {
        console.warn('Preview autoplay failed:', err)
      })
    }
  }, [showPreview])

  // 清理定时器
  useEffect(() => {
    return () => {
      if (hoverTimerRef.current) {
        clearTimeout(hoverTimerRef.current)
      }
    }
  }, [])

  return (
    <Link to={`/video/${video.id}`}>
      <div
        className="relative overflow-hidden rounded-lg bg-gray-900 cursor-pointer group"
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        {/* 封面图 */}
        <div className={`relative aspect-video ${showPreview ? 'opacity-0' : 'opacity-100'} transition-opacity duration-300`}>
          <img
            src={video.poster_url}
            alt={video.title}
            className="w-full h-full object-cover"
            loading="lazy"
          />

          {/* 播放按钮叠加层 */}
          <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all">
            <div className="w-16 h-16 rounded-full bg-white bg-opacity-80 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
              <svg className="w-8 h-8 text-black ml-1" fill="currentColor" viewBox="0 0 20 20">
                <path d="M6 4l10 6-10 6V4z"/>
              </svg>
            </div>
          </div>
        </div>

        {/* ✨ 悬停预览视频 */}
        {video.hover_preview_url && showPreview && (
          <div className="absolute inset-0">
            <video
              ref={videoRef}
              src={video.hover_preview_url}
              className="w-full h-full object-cover"
              muted  // 静音播放
              loop  // 循环播放
              playsInline  // iOS内联播放
              onLoadedData={() => setPreviewLoaded(true)}
              onError={(e) => {
                console.error('Preview video error:', e)
                setShowPreview(false)
              }}
            />

            {/* 加载指示器 */}
            {!previewLoaded && (
              <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
              </div>
            )}

            {/* 预览标签 */}
            <div className="absolute top-2 left-2 bg-black bg-opacity-70 text-white text-xs px-2 py-1 rounded">
              预览中
            </div>
          </div>
        )}

        {/* 视频信息 */}
        <div className="p-4">
          <h3 className="text-lg font-semibold text-white line-clamp-2 mb-2">
            {video.title}
          </h3>
          <div className="flex items-center text-sm text-gray-400">
            <span>{video.view_count?.toLocaleString()} 次观看</span>
            <span className="mx-2">•</span>
            <span>{new Date(video.created_at).toLocaleDateString()}</span>
          </div>
        </div>
      </div>
    </Link>
  )
}

export default VideoCardWithPreview
```

#### 4.2 移动端适配

```typescript
// 检测设备类型
const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)

// 移动端使用点击触发,PC端使用hover
const triggerEvent = isMobile ? 'onClick' : 'onMouseEnter'

<div
  {...(isMobile ? {
    onClick: handleClick  // 移动端点击播放
  } : {
    onMouseEnter: handleMouseEnter,  // PC端hover播放
    onMouseLeave: handleMouseLeave
  })}
>
  {/* VideoCard内容 */}
</div>
```

#### 4.3 性能优化

```typescript
// 1. 使用Intersection Observer懒加载
const [isVisible, setIsVisible] = useState(false)
const cardRef = useRef<HTMLDivElement>(null)

useEffect(() => {
  const observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        setIsVisible(true)
        observer.disconnect()
      }
    },
    { rootMargin: '50px' }  // 提前50px加载
  )

  if (cardRef.current) {
    observer.observe(cardRef.current)
  }

  return () => observer.disconnect()
}, [])

// 2. 预加载优化
{isVisible && video.hover_preview_url && (
  <link rel="preload" as="video" href={video.hover_preview_url} />
)}

// 3. 节流防抖
import { useDebounce } from '@/hooks/useDebounce'

const debouncedShowPreview = useDebounce(showPreview, 100)
```

---

## 📊 性能分析

### 预览视频文件大小

| 时长 | 分辨率 | 码率 | 编码 | 文件大小 | 加载时间(4G) |
|------|--------|------|------|----------|--------------|
| 10秒 | 480p | 500kbps | VP9 | ~625KB | <1秒 |
| 10秒 | 720p | 1Mbps | VP9 | ~1.25MB | 1-2秒 |
| 5秒 | 480p | 500kbps | VP9 | ~312KB | <0.5秒 |

**推荐**: 10秒 480p VP9编码,文件约600KB

### 带宽消耗估算

假设每个用户浏览20个视频卡片,hover 3个:

- 每用户流量: 600KB × 3 = 1.8MB
- 1000用户/天: 1.8GB
- 30,000用户/月: 54GB
- **月成本** (CDN ¥0.2/GB): ~¥11

### 存储成本

- 每视频预览: ~600KB
- 10,000个视频: 6GB
- **存储成本** (¥0.1/GB/月): ~¥0.6/月

**结论**: 成本可控,用户体验提升显著 ✅

---

## 🎨 用户体验优化

### 1. 渐进式加载

```typescript
// 优先显示封面图,后台加载预览视频
const [previewReady, setPreviewReady] = useState(false)

useEffect(() => {
  if (video.hover_preview_url && isVisible) {
    // 后台预加载
    const video = document.createElement('video')
    video.src = video.hover_preview_url
    video.load()
    video.addEventListener('canplaythrough', () => {
      setPreviewReady(true)
    })
  }
}, [video.hover_preview_url, isVisible])
```

### 2. 视觉反馈

```typescript
// 加载过程显示进度
<div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-700">
  <div
    className="h-full bg-blue-500 transition-all duration-300"
    style={{ width: `${loadProgress}%` }}
  />
</div>
```

### 3. 错误降级

```typescript
const [previewError, setPreviewError] = useState(false)

// 预览失败时回退到封面图
if (previewError) {
  return <img src={video.poster_url} alt={video.title} />
}
```

---

## 🧪 测试清单

- [ ] 预览视频正确生成 (10秒, 480p, VP9)
- [ ] 数据库字段正确保存
- [ ] API返回hover_preview_url字段
- [ ] 鼠标hover触发预览播放
- [ ] 鼠标离开停止预览
- [ ] 移动端点击触发预览
- [ ] 预览视频循环播放
- [ ] 静音播放
- [ ] 懒加载正常工作
- [ ] 预览失败时优雅降级
- [ ] 性能监控无异常
- [ ] 多浏览器兼容性测试

---

## 📚 参考资料

- [YouTube Engineering Blog - Video Previews](https://blog.youtube/engineering/)
- [Netflix TechBlog - Hover Previews](https://netflixtechblog.com/)
- [WebM VP9 Encoding Guide](https://trac.ffmpeg.org/wiki/Encode/VP9)
- [MDN - HTMLVideoElement](https://developer.mozilla.org/en-US/docs/Web/API/HTMLVideoElement)

---

**文档版本**: 1.0.0
**创建时间**: 2025-10-09
**最后更新**: 2025-10-09
**作者**: Claude AI
