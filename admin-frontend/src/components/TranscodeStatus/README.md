# TranscodeStatus 组件

转码状态显示组件,用于管理后台视频列表中实时显示视频转码进度。

## 功能特性

- ✅ 实时显示转码状态 (pending/processing/completed/failed)
- ✅ 进度条动画显示转码进度 (0-100%)
- ✅ 自动轮询刷新 (转码中时每5秒刷新)
- ✅ 支持转码失败重试
- ✅ 显示H.264和AV1转码完成时间
- ✅ 错误信息提示
- ✅ 自定义刷新间隔

## 使用方法

### 基础用法

```tsx
import TranscodeStatus from '@/components/TranscodeStatus'

<TranscodeStatus videoId={123} />
```

### 完整配置

```tsx
<TranscodeStatus
  videoId={123}
  initialStatus="processing"
  initialProgress={45}
  autoRefresh={true}
  refreshInterval={5000}
  onRetry={() => {
    console.log('转码重试')
  }}
/>
```

### 在表格中使用

```tsx
import { Table } from 'antd'
import TranscodeStatus from '@/components/TranscodeStatus'

const columns = [
  {
    title: '标题',
    dataIndex: 'title',
  },
  {
    title: '转码状态',
    dataIndex: 'id',
    render: (id: number, record: any) => (
      <TranscodeStatus
        videoId={id}
        initialStatus={record.transcode_status}
        initialProgress={record.transcode_progress}
      />
    ),
  },
]

<Table columns={columns} dataSource={videos} />
```

## Props

| 参数 | 说明 | 类型 | 默认值 | 必填 |
|------|------|------|--------|------|
| videoId | 视频ID | number | - | ✅ |
| initialStatus | 初始状态 | 'pending' \| 'processing' \| 'completed' \| 'failed' | 'pending' | ❌ |
| initialProgress | 初始进度 | number | 0 | ❌ |
| autoRefresh | 是否自动刷新 | boolean | true | ❌ |
| refreshInterval | 刷新间隔(毫秒) | number | 5000 | ❌ |
| onRetry | 重试回调函数 | () => void | - | ❌ |

## 状态说明

### pending (等待转码)
- 显示: 灰色标签 + 0%进度条
- 特点: 转码任务已创建,等待Celery worker处理

### processing (转码中)
- 显示: 蓝色旋转标签 + 动态进度条
- 特点: 每5秒自动刷新进度
- 进度阶段:
  - 0-10%: 准备阶段
  - 10-80%: 转码阶段 (线性增长)
  - 80-100%: 上传阶段

### completed (已完成)
- 显示: 绿色成功标签 + 100%进度条
- 特点: 显示H.264和AV1转码完成时间
- 停止自动刷新

### failed (转码失败)
- 显示: 红色失败标签 + 错误进度条 + 重试按钮
- 特点: 显示错误信息,支持一键重试
- 停止自动刷新

## 转码格式标签

- **H.264**: 蓝色标签,鼠标悬停显示完成时间
- **AV1**: 绿色标签,鼠标悬停显示完成时间

## API端点

组件使用以下API端点:

### 获取转码状态
```
GET /api/v1/admin/videos/{video_id}/transcode-status
```

响应:
```json
{
  "video_id": 123,
  "status": "processing",
  "progress": 45,
  "error": null,
  "h264_transcode_at": "2025-10-10T10:30:00Z",
  "av1_transcode_at": null,
  "is_av1_available": false
}
```

### 重试转码
```
POST /api/v1/admin/videos/{video_id}/retry-transcode
```

## 性能优化

1. **条件刷新**: 只在转码进行中时自动刷新
2. **防抖处理**: 重试操作带loading状态
3. **内存清理**: 组件卸载时清除定时器
4. **错误容错**: API失败不影响组件显示

## 样式定制

组件使用Ant Design的Progress和Tag组件,可通过全局主题定制样式。

## 注意事项

1. 确保后端API已实现转码状态端点
2. 自动刷新会增加服务器负载,建议控制刷新频率
3. 大量视频列表时,考虑使用虚拟滚动优化性能
4. 转码失败时,检查Celery日志排查问题

## 示例截图

```
┌─────────────────────────────────────┐
│ 🔵 转码中  H.264                    │
│ ████████████░░░░░░░░░░ 60%         │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ ✅ 已完成  H.264  AV1               │
│ ████████████████████████ 100%      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ ❌ 转码失败                          │
│ ██████████░░░░░░░░░░░░░░ 42%       │
│ 错误: FFmpeg process failed...     │
│ [重试转码]                          │
└─────────────────────────────────────┘
```

## 更新日志

- v1.0.0 (2025-10-10): 初始版本
  - 支持4种转码状态
  - 自动刷新功能
  - 重试功能
  - H.264/AV1格式标签
