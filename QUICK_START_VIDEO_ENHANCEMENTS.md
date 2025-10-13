# 🚀 视频管理增强功能 - 快速开始指南

本指南帮助你快速启用和测试新增的视频管理功能。

## 📦 已实现的功能

✅ **批量上传系统** - 多文件并发上传，支持断点续传
✅ **视频预览** - 鼠标悬停即可预览视频
✅ **重复检测** - 基于哈希的智能去重

## ⚡ 快速启动（5分钟）

### 步骤 1: 后端设置

```bash
# 进入后端目录
cd /home/eric/video/backend

# 激活虚拟环境
source venv/bin/activate

# 运行数据库迁移（如果需要）
alembic upgrade head

# 重启后端服务
# 如果正在运行，先停止
pkill -f "uvicorn app.main:app"

# 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 步骤 2: 前端设置

```bash
# 在新终端中进入管理前端目录
cd /home/eric/video/admin-frontend

# 安装依赖（如果还没安装）
pnpm install

# 启动开发服务器
pnpm run dev
```

### 步骤 3: 验证功能

打开浏览器访问: `http://localhost:3001`

---

## 🎯 功能测试

### 1. 测试批量上传 (2分钟)

1. **访问视频列表**
   - 登录管理后台
   - 点击左侧菜单 "视频管理"

2. **开始批量上传**
   - ~~点击页面上的 "批量上传" 按钮~~ (需要添加入口)
   - 或直接使用 `BatchUploader` 组件

3. **上传测试文件**
   - 拖拽2-3个视频文件到上传区域
   - 观察每个文件的上传进度
   - 尝试暂停/继续某个上传
   - 尝试删除某个上传任务

4. **验证结果**
   - 所有文件上传完成后，刷新视频列表
   - 确认新视频出现在列表中

### 2. 测试视频预览 (1分钟)

1. **进入视频列表**
   - 确保列表中有至少一个已上传视频的记录

2. **触发预览**
   - 将鼠标悬停在任意视频标题上
   - 等待300ms（配置的延迟时间）
   - 应该看到弹出预览窗口

3. **检查预览内容**
   - ✅ 视频自动播放（静音）
   - ✅ 显示观看数、评分、点赞等统计
   - ✅ 显示分类标签
   - ✅ 显示视频描述
   - ✅ 如果有AV1版本，显示AV1标签

4. **测试交互**
   - 鼠标移开，预览窗口应关闭
   - 视频停止播放
   - 再次悬停，重新加载

### 3. 测试重复检测 (需要集成)

**注意**: 重复检测功能的工具类已实现，但还需要集成到上传流程。

**手动测试方法**:

```python
# 在Python控制台中测试
cd backend
source venv/bin/activate
python

>>> from app.utils.video_hash import calculate_video_fingerprint
>>>
>>> # 读取测试视频
>>> with open('/path/to/test/video.mp4', 'rb') as f:
>>>     content = f.read()
>>>
>>> # 计算指纹
>>> fingerprint = calculate_video_fingerprint(
>>>     file_content=content,
>>>     title="Test Video",
>>>     duration=120
>>> )
>>>
>>> print(fingerprint)
```

---

## 🔧 如何使用新功能

### 使用批量上传组件

```tsx
// 在你的React页面中
import BatchUploader from '@/components/BatchUploader'

function VideoUploadPage() {
  const handleUploadComplete = (urls: string[]) => {
    console.log('所有文件上传完成:', urls)
    // 更新视频列表或其他操作
  }

  return (
    <div>
      <h2>批量上传视频</h2>
      <BatchUploader
        onAllComplete={handleUploadComplete}
        accept="video/*"
        maxSize={2048}  // 2GB per file
        maxCount={10}   // Max 10 files
        autoUpload={false}  // 手动开始上传
      />
    </div>
  )
}
```

### 使用视频预览组件

```tsx
// 在任何显示视频的地方使用
import VideoPreviewPopover from '@/components/VideoPreviewPopover'

function VideoItem({ video }) {
  return (
    <VideoPreviewPopover video={video} hoverDelay={300}>
      <div className="video-item">
        <img src={video.poster_url} alt={video.title} />
        <h3>{video.title}</h3>
      </div>
    </VideoPreviewPopover>
  )
}
```

### 使用重复检测API

```python
# 在上传处理函数中
from app.utils.video_hash import calculate_video_fingerprint, check_duplicate_video

async def process_upload(file_content: bytes, title: str, db: Session):
    # 1. 计算视频指纹
    fingerprint = calculate_video_fingerprint(
        file_content=file_content,
        title=title,
        duration=None  # 可选
    )

    # 2. 检查是否重复
    is_duplicate, duplicate_id = await check_duplicate_video(
        db=db,
        file_hash=fingerprint['file_hash_md5'],
        partial_hash=fingerprint['partial_hash'],
        metadata_hash=fingerprint['metadata_hash']
    )

    if is_duplicate:
        raise HTTPException(
            status_code=409,
            detail=f"视频已存在，ID: {duplicate_id}"
        )

    # 3. 继续上传流程...
```

---

## 📋 完整功能清单

### ✅ 已完成

| 功能 | 状态 | 文件 |
|-----|------|------|
| 批量上传后端API | ✅ | `/backend/app/admin/batch_upload.py` |
| 批量上传前端组件 | ✅ | `/admin-frontend/src/components/BatchUploader.tsx` |
| 上传会话管理 | ✅ | `/backend/app/models/upload_session.py` |
| 视频预览组件 | ✅ | `/admin-frontend/src/components/VideoPreviewPopover.tsx` |
| 预览样式 | ✅ | `/admin-frontend/src/components/VideoPreviewPopover.css` |
| 集成到视频列表 | ✅ | `/admin-frontend/src/pages/Videos/List.tsx` |
| 视频哈希工具 | ✅ | `/backend/app/utils/video_hash.py` |
| 重复检测逻辑 | ✅ | `/backend/app/utils/video_hash.py` |

### 🚧 需要完善

| 功能 | 优先级 | 预计时间 |
|-----|-------|---------|
| 批量上传入口按钮 | 高 | 10分钟 |
| 重复检测集成到上传流程 | 高 | 30分钟 |
| Video模型添加哈希字段 | 高 | 20分钟 |
| 数据库迁移脚本 | 高 | 15分钟 |
| 重复检测UI界面 | 中 | 1小时 |
| localStorage恢复上传 | 中 | 1小时 |

### ⏳ 待实现

| 功能 | 优先级 | 预计时间 |
|-----|-------|---------|
| 推荐算法 | 中 | 2-3天 |
| 视频分析仪表板 | 中 | 3-4天 |
| 质量评分系统 | 低 | 2-3天 |

---

## 🔍 故障排查

### 问题 1: 批量上传失败

**症状**: 上传初始化失败，返回404

**解决方案**:
```bash
# 检查路由是否正确注册
cd /home/eric/video/backend
grep "batch_upload" app/main.py

# 应该看到:
# from app.admin import batch_upload as admin_batch_upload
# app.include_router(admin_batch_upload.router, ...)

# 如果没有，手动添加到 main.py
```

### 问题 2: 视频预览不显示

**症状**: 悬停时没有弹窗

**解决方案**:
1. 检查是否导入了组件
2. 检查CSS文件是否加载
3. 检查视频数据是否完整
4. 打开浏览器控制台查看错误

```tsx
// 确保导入了组件
import VideoPreviewPopover from '@/components/VideoPreviewPopover'

// 确保video对象包含必要字段
console.log(video)  // 应该有 title, video_url等
```

### 问题 3: 上传会话找不到

**症状**: 上传分块时返回"上传会话不存在"

**解决方案**:
```bash
# 检查数据库表是否存在
cd /home/eric/video/backend
source venv/bin/activate
python

>>> from app.database import SessionLocal
>>> from app.models.upload_session import UploadSession
>>> db = SessionLocal()
>>> sessions = db.query(UploadSession).all()
>>> print(len(sessions))

# 如果表不存在，运行迁移
exit()
alembic upgrade head
```

---

## 🎨 自定义配置

### 修改上传分块大小

```python
# backend/app/admin/batch_upload.py
CHUNK_SIZE = 10 * 1024 * 1024  # 改为 10MB
```

```tsx
// admin-frontend/src/components/BatchUploader.tsx
const CHUNK_SIZE = 10 * 1024 * 1024  // 改为 10MB
```

### 修改预览延迟时间

```tsx
// admin-frontend/src/pages/Videos/List.tsx
<VideoPreviewPopover video={record} hoverDelay={500}>  {/* 改为500ms */}
```

### 修改并发上传数量

```tsx
// admin-frontend/src/components/BatchUploader.tsx
const concurrency = 5  // 改为同时上传5个文件
```

---

## 📚 更多文档

- [完整功能文档](./VIDEO_MANAGEMENT_ENHANCEMENTS.md)
- [API文档](http://localhost:8000/api/docs)
- [项目README](./README.md)

---

## 🤔 常见问题

**Q: 批量上传支持的最大文件大小是多少？**
A: 默认是2GB，可以在组件的`maxSize`属性中修改。

**Q: 可以同时上传多少个文件？**
A: 默认最多10个文件，并发上传3个。可以修改`maxCount`和`concurrency`配置。

**Q: 视频预览支持哪些格式？**
A: 支持浏览器原生支持的所有格式（MP4, WebM等）。建议使用H.264或AV1编码的MP4。

**Q: 重复检测的准确度如何？**
A: 基于文件哈希的检测准确度100%。基于元数据的检测可能有误报，建议组合使用。

**Q: 如何清理过期的上传会话？**
A: 可以创建定时任务，删除超过7天且未完成的会话。

---

## 🎉 完成！

现在你已经了解如何使用所有新增的视频管理功能。

如有问题，请查看完整文档或提交Issue。
