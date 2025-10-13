# 视频管理系统增强功能文档

本文档详细说明了为VideoSite项目实现的6大视频管理增强功能。

## 📋 功能概览

1. ✅ **批量上传系统** - 支持多文件、断点续传、实时进度条
2. ✅ **列表预览功能** - 鼠标悬停弹出视频预览播放器
3. 🚧 **重复检测功能** - 基于视频哈希值或元数据检测重复
4. ⏳ **推荐算法** - 基于分类、标签、观看历史的推荐系统
5. ⏳ **视频分析页面** - 完整的数据可视化仪表板
6. ⏳ **质量评分系统** - 基于多维度指标的自动评分

---

## 1. 批量上传系统 ✅

### 功能特性
- **多文件并发上传** - 最多同时上传3个文件
- **断点续传** - 支持暂停/继续上传
- **分块上传** - 5MB分块，适合大文件
- **实时进度追踪** - 每个文件独立显示进度
- **会话持久化** - 上传状态存储在数据库

### 后端实现

#### API端点

**文件位置**: `/backend/app/admin/batch_upload.py`

```python
POST   /api/v1/admin/upload/batch/init          # 初始化批量上传
POST   /api/v1/admin/upload/batch/chunk         # 上传单个分块
POST   /api/v1/admin/upload/batch/complete/{upload_id}  # 完成上传
GET    /api/v1/admin/upload/batch/status        # 获取上传状态
DELETE /api/v1/admin/upload/batch/cancel/{upload_id}    # 取消上传
```

#### 数据模型

**文件位置**: `/backend/app/models/upload_session.py`

```python
class UploadSession(Base):
    upload_id: str              # 唯一上传ID
    filename: str               # 原始文件名
    file_size: int              # 文件大小（字节）
    chunk_size: int             # 分块大小（默认5MB）
    total_chunks: int           # 总分块数
    uploaded_chunks: list[int]  # 已上传的分块索引
    is_completed: bool          # 是否完成
    is_merged: bool             # 是否已合并
    temp_dir: str               # 临时存储目录
    expires_at: datetime        # 过期时间
```

### 前端实现

#### React组件

**文件位置**: `/admin-frontend/src/components/BatchUploader.tsx`

```tsx
import BatchUploader from '@/components/BatchUploader'

<BatchUploader
  onAllComplete={(urls) => console.log('上传完成', urls)}
  accept="video/*"
  maxSize={2048}  // MB
  maxCount={10}
  autoUpload={false}
/>
```

#### 主要功能
- 拖拽上传
- 并发控制（最多3个同时上传）
- 暂停/继续/删除
- 进度显示
- 错误处理

### 使用示例

```typescript
// 初始化批量上传
const response = await axios.post('/api/v1/admin/upload/batch/init', [
  {
    filename: 'movie1.mp4',
    file_size: 1024000000,
    mime_type: 'video/mp4',
    title: 'Movie 1'
  },
  {
    filename: 'movie2.mp4',
    file_size: 2048000000,
    mime_type: 'video/mp4',
    title: 'Movie 2'
  }
])

// 上传分块
for (let i = 0; i < totalChunks; i++) {
  const chunk = file.slice(i * CHUNK_SIZE, (i + 1) * CHUNK_SIZE)
  await uploadChunk(uploadId, chunk, i)
}

// 完成上传
const result = await completeUpload(uploadId)
```

---

## 2. 列表预览功能 ✅

### 功能特性
- **鼠标悬停触发** - 延迟300ms显示预览
- **自动播放视频** - 静音循环播放
- **完整视频信息** - 标题、评分、观看数、时长等
- **优先使用AV1** - 自动选择最佳视频格式
- **转码状态显示** - 实时显示转码进度

### 前端实现

#### React组件

**文件位置**: `/admin-frontend/src/components/VideoPreviewPopover.tsx`

```tsx
import VideoPreviewPopover from '@/components/VideoPreviewPopover'

<VideoPreviewPopover video={videoData} hoverDelay={300}>
  <div className="video-preview-trigger">
    {video.title}
  </div>
</VideoPreviewPopover>
```

#### 样式文件

**文件位置**: `/admin-frontend/src/components/VideoPreviewPopover.css`

- 16:9 视频播放器
- 流畅的淡入动画
- 深色模式支持
- 响应式设计

### 集成到视频列表

**文件位置**: `/admin-frontend/src/pages/Videos/List.tsx`

```tsx
{
  title: t('video.title'),
  dataIndex: 'title',
  key: 'title',
  render: (title: string, record: any) => (
    <VideoPreviewPopover video={record} hoverDelay={300}>
      <div className="video-preview-trigger">
        {title}
      </div>
    </VideoPreviewPopover>
  ),
}
```

### 显示内容

预览弹窗包含：
1. **视频播放器** - 自动播放视频片段
2. **基本信息** - 标题、原标题
3. **统计数据** - 观看数、评分、点赞数、时长
4. **分类标签** - 前3个分类
5. **描述** - 截断到100字符
6. **状态标签** - 发布状态、AV1标记、转码状态

---

## 3. 重复检测功能 🚧

### 功能特性
- **多种哈希算法** - MD5、SHA256、部分哈希
- **元数据比对** - 基于标题+时长+文件大小
- **流式计算** - 支持大文件
- **感知哈希** - 检测相似视频（未来实现）

### 后端实现

#### 哈希工具

**文件位置**: `/backend/app/utils/video_hash.py`

```python
from app.utils.video_hash import (
    calculate_file_hash,
    calculate_partial_hash,
    calculate_metadata_hash,
    calculate_video_fingerprint,
    check_duplicate_video
)

# 计算完整指纹
fingerprint = calculate_video_fingerprint(
    file_content=video_bytes,
    title="Movie Title",
    duration=7200  # 秒
)

# 检查重复
is_duplicate, video_id = await check_duplicate_video(
    db,
    file_hash=fingerprint['file_hash_md5'],
    partial_hash=fingerprint['partial_hash'],
    metadata_hash=fingerprint['metadata_hash']
)
```

### 需要的数据库迁移

```python
# 在Video模型中添加字段
file_hash: str           # 完整文件MD5哈希
file_hash_sha256: str    # SHA256哈希
partial_hash: str        # 部分哈希（头+尾）
metadata_hash: str       # 元数据哈希
```

### 使用场景

1. **上传时检测** - 在批量上传完成前检查重复
2. **手动检测** - 提供管理界面检测现有视频重复
3. **自动清理** - 定期任务查找并标记重复视频

---

## 4. 推荐算法 ⏳ (待实现)

### 计划实现的功能

#### 基于内容的推荐
- 相同分类的视频
- 相同标签的视频
- 相同演员/导演的视频
- 相同国家/语言的视频

#### 协同过滤推荐
- 基于用户观看历史
- "看过A的用户也看过B"
- 相似用户的喜好

#### 混合推荐算法
```python
score = (
    0.3 * content_similarity +
    0.3 * collaborative_filtering +
    0.2 * popularity_score +
    0.1 * recency_score +
    0.1 * user_preference
)
```

### API端点（计划）

```python
GET /api/v1/videos/{video_id}/related          # 相关视频
GET /api/v1/recommendations/for-you            # 个性化推荐
GET /api/v1/recommendations/trending           # 热门推荐
GET /api/v1/recommendations/similar/{video_id} # 相似视频
```

---

## 5. 视频分析页面 ⏳ (待实现)

### 计划实现的功能

#### 观看趋势分析
- 每日/每周/每月观看数趋势图
- 峰值观看时段分析
- 地理分布热图

#### 完播率分析
```python
completion_rate = {
    '0-25%': 150,    # 150人只看了0-25%
    '25-50%': 80,
    '50-75%': 120,
    '75-100%': 650   # 650人看完全片
}
```

#### 观众留存曲线
- 显示每个时间点的观众数量
- 识别流失高峰点
- 优化建议

#### 互动数据
- 评论时间分布
- 点赞/收藏转化率
- 分享传播分析

### 数据可视化组件

```tsx
import { Line, Bar, Pie, Heatmap } from '@ant-design/charts'

<Line data={viewTrends} xField="date" yField="views" />
<Pie data={completionRate} angleField="value" colorField="type" />
<Heatmap data={geoDistribution} xField="hour" yField="day" />
```

---

## 6. 质量评分系统 ⏳ (待实现)

### 评分维度

```python
video_quality_score = calculate_quality_score({
    'technical': {
        'resolution': 1080,           # 分辨率 (权重: 20%)
        'bitrate': 5000,              # 比特率 (权重: 15%)
        'codec': 'av1',               # 编码格式 (权重: 10%)
        'audio_quality': 'aac-192'    # 音频质量 (权重: 10%)
    },
    'metadata': {
        'has_description': True,      # 有描述 (权重: 5%)
        'has_poster': True,           # 有封面 (权重: 5%)
        'has_subtitles': True,        # 有字幕 (权重: 5%)
        'metadata_completeness': 0.8  # 元数据完整度 (权重: 5%)
    },
    'engagement': {
        'view_count': 10000,          # 观看数 (权重: 10%)
        'average_rating': 4.5,        # 平均评分 (权重: 15%)
        'completion_rate': 0.75       # 完播率 (权重: 10%)
    }
})
```

### 评分等级

```python
quality_grades = {
    'S': (90, 100),   # 优秀
    'A': (80, 90),    # 良好
    'B': (70, 80),    # 中等
    'C': (60, 70),    # 及格
    'D': (0, 60)      # 不及格
}
```

### 自动优化建议

```python
suggestions = [
    {
        'issue': 'low_resolution',
        'current': 720,
        'recommended': 1080,
        'impact': '+15分'
    },
    {
        'issue': 'missing_description',
        'action': '添加详细描述',
        'impact': '+5分'
    }
]
```

---

## 🚀 部署说明

### 1. 后端部署

#### 数据库迁移

```bash
cd backend

# 如果还未创建哈希字段的迁移
alembic revision --autogenerate -m "add video hash fields for duplicate detection"
alembic upgrade head
```

#### 安装依赖

后端无需额外依赖，已使用Python标准库的`hashlib`。

### 2. 前端部署

#### 安装依赖

```bash
cd admin-frontend
pnpm install
```

#### 构建

```bash
pnpm run build
```

### 3. 验证功能

#### 测试批量上传

```bash
# 访问管理后台
# 导航到视频管理页面
# 点击"批量上传"按钮
# 选择多个视频文件
# 观察上传进度
```

#### 测试预览功能

```bash
# 访问视频列表页面
# 鼠标悬停在视频标题上
# 应该看到预览弹窗和视频自动播放
```

---

## 📊 性能优化

### 批量上传优化
- ✅ 使用并发限制（最多3个）避免带宽饱和
- ✅ 分块大小5MB平衡速度和内存
- ✅ 临时文件自动清理
- ✅ 会话过期机制（7天）

### 预览功能优化
- ✅ 延迟加载（300ms）避免意外触发
- ✅ 视频预加载策略
- ✅ 自动停止播放（鼠标离开时）
- ✅ 优先使用AV1格式节省带宽

### 重复检测优化
- ✅ 部分哈希（头+尾）快速检测大文件
- ✅ 流式计算适合超大文件
- ⏳ 异步任务处理（后台检测）
- ⏳ 缓存哈希结果

---

## 🐛 已知问题

### 批量上传
- [ ] 浏览器刷新后无法恢复上传会话（需要使用localStorage）
- [ ] 大于2GB文件可能超时（需要调整超时设置）

### 预览功能
- [ ] 某些视频格式可能无法预览（需要转码支持）
- [ ] 移动端性能待优化

### 重复检测
- [ ] 感知哈希需要额外库支持（如OpenCV）
- [ ] 大规模检测需要优化数据库索引

---

## 📝 后续开发计划

### 短期（1-2周）
1. ✅ 完成批量上传和预览功能
2. 🚧 实现重复检测API和UI
3. ⏳ 添加相关视频推荐

### 中期（1个月）
4. ⏳ 实现视频分析仪表板
5. ⏳ 构建质量评分系统
6. ⏳ 优化推荐算法

### 长期（2-3个月）
7. ⏳ 机器学习推荐引擎
8. ⏳ 高级视频分析（AI识别内容）
9. ⏳ 自动化内容审核

---

## 🔗 相关文件

### 后端
- `/backend/app/admin/batch_upload.py` - 批量上传API
- `/backend/app/admin/upload.py` - 原有上传API
- `/backend/app/models/upload_session.py` - 上传会话模型
- `/backend/app/models/video.py` - 视频模型
- `/backend/app/utils/video_hash.py` - 视频哈希工具
- `/backend/app/utils/minio_client.py` - MinIO客户端

### 前端
- `/admin-frontend/src/components/BatchUploader.tsx` - 批量上传组件
- `/admin-frontend/src/components/VideoPreviewPopover.tsx` - 预览弹窗组件
- `/admin-frontend/src/components/VideoPreviewPopover.css` - 预览样式
- `/admin-frontend/src/components/ChunkedUploader.tsx` - 分块上传组件
- `/admin-frontend/src/pages/Videos/List.tsx` - 视频列表页面

---

## 💡 使用建议

1. **批量上传**: 建议一次不超过10个文件，每个文件不超过2GB
2. **预览功能**: 确保视频已转码完成，否则可能无法预览
3. **重复检测**: 上传前先检测，避免浪费存储空间
4. **性能监控**: 定期检查上传会话表，清理过期数据

---

## 🤝 贡献

如有问题或建议，请提交Issue或Pull Request。

## 📄 许可证

与主项目相同
