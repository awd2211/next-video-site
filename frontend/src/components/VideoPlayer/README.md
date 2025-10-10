# YouTube-Style Video Player

## 概述

这是一个完全模仿 YouTube 播放器的视频播放组件，基于 Video.js 构建，包含所有 YouTube 的核心功能和交互。

## 功能清单

### ✅ 已实现的核心功能

#### 1. 视觉设计
- [x] YouTube 风格的控制栏布局（36px 高度）
- [x] 红色进度条（#ff0000）
- [x] 圆形大播放按钮（居中显示）
- [x] 自动隐藏控制栏（3秒后）
- [x] 控制栏渐变背景
- [x] YouTube 风格的菜单和按钮

#### 2. 进度条交互
- [x] 悬停时显示时间提示气泡
- [x] 悬停时进度条加粗（3px → 5px）
- [x] 拖动时的圆形滑块
- [x] 缓冲进度显示
- [x] 平滑的动画过渡

#### 3. 双击交互
- [x] 左侧 1/3 双击：快退 10 秒
- [x] 右侧 1/3 双击：快进 10 秒
- [x] 中间双击：播放/暂停
- [x] 视觉反馈动画（圆形脉动效果）
- [x] 波纹扩散动画

#### 4. 音量控制
- [x] 滚轮调整音量
- [x] 键盘↑↓调整音量
- [x] 音量调整时的屏幕提示
- [x] 音量百分比显示
- [x] 音量图标（低/中/高/静音）
- [x] 悬停展开音量滑块

#### 5. 快捷键系统

**播放控制:**
- [x] `Space / K` - 播放/暂停
- [x] `J` - 快退 10 秒
- [x] `L` - 快进 10 秒
- [x] `← 左箭头` - 快退 5 秒
- [x] `→ 右箭头` - 快进 5 秒
- [x] `0-9` - 跳转到视频 0%-90%
- [x] `, 逗号` - 逐帧后退（暂停时）
- [x] `. 句号` - 逐帧前进（暂停时）

**音量控制:**
- [x] `↑ 上箭头` - 增加音量
- [x] `↓ 下箭头` - 减少音量
- [x] `M` - 静音/取消静音
- [x] `滚轮` - 调整音量

**播放速度:**
- [x] `< Shift + ,` - 减慢播放速度
- [x] `> Shift + .` - 加快播放速度
- [x] 速度选项：0.25x, 0.5x, 0.75x, 1x, 1.25x, 1.5x, 1.75x, 2x
- [x] 非 1x 速度时显示速度指示器

**显示模式:**
- [x] `F` - 全屏/退出全屏
- [x] `T` - 剧场模式
- [x] `I` - 迷你播放器

**字幕与设置:**
- [x] `C` - 切换字幕显示

**帮助:**
- [x] `?` - 显示/隐藏快捷键列表
- [x] `Esc` - 关闭菜单或退出全屏

#### 6. 右键菜单
- [x] YouTube 风格的上下文菜单
- [x] 循环播放开关
- [x] 播放速度调整（子菜单）
- [x] 画质选择（子菜单）
- [x] 复制视频网址
- [x] 复制当前时间的视频网址
- [x] 统计信息（Stats for nerds）
- [x] 迷你播放器
- [x] 剧场模式
- [x] 全屏

#### 7. 统计信息面板
- [x] 视频 ID
- [x] 分辨率
- [x] 帧率
- [x] 视频编码
- [x] 音频编码
- [x] 视频码率
- [x] 音频码率
- [x] 缓冲健康度
- [x] 已播放时间
- [x] 总时长
- [x] 音量
- [x] 播放速度
- [x] 丢帧统计

#### 8. 显示模式
- [x] 普通模式
- [x] 剧场模式（宽屏）
- [x] 迷你播放器（画中画）
- [x] 全屏模式
- [x] 全屏时优化字幕位置和大小

#### 9. 字幕支持
- [x] 自动加载字幕
- [x] 多语言字幕支持
- [x] 字幕开关（C 键）
- [x] 字幕菜单（控制栏按钮）
- [x] 全屏时字幕优化

#### 10. 自动保存进度
- [x] 每 10 秒自动保存观看进度
- [x] 视频结束时标记为已完成
- [x] 从上次位置继续播放

#### 11. 画质选择
- [x] HLS 自适应流支持
- [x] 手动画质选择（自动/1080p/720p/480p/360p）
- [x] 画质菜单按钮（齿轮图标）
- [x] 当前画质显示

#### 12. 缓冲和加载状态
- [x] 加载 Spinner 动画
- [x] 缓冲进度显示
- [x] 缓冲事件监听
- [x] 缓冲健康度统计

#### 13. 视觉反馈
- [x] 快进/快退视觉反馈（SeekFeedback 组件）
- [x] 音量调整视觉反馈（VolumeIndicator 组件）
- [x] 播放速度变化提示（PlaybackRateIndicator 组件）
- [x] 键盘快捷键帮助面板（KeyboardShortcuts 组件）

#### 14. 性能优化
- [x] useCallback 优化事件处理函数
- [x] React.memo 优化子组件渲染
- [x] 防止不必要的重渲染
- [x] 高效的状态管理

#### 15. 响应式设计
- [x] 桌面端优化
- [x] 移动端适配
- [x] 触摸优化
- [x] 不同屏幕尺寸适配

## 组件结构

```
VideoPlayer/
├── index.tsx                      # 主播放器组件
├── VideoPlayer.css                # 基础样式
├── VideoPlayer-YouTube.css        # YouTube 风格样式
├── ContextMenu.tsx                # 右键菜单
├── ContextMenu.css
├── StatsPanel.tsx                 # 统计信息面板
├── StatsPanel.css
├── SeekFeedback.tsx               # 快进/快退视觉反馈
├── SeekFeedback.css
├── VolumeIndicator.tsx            # 音量指示器
├── VolumeIndicator.css
├── KeyboardShortcuts.tsx          # 快捷键帮助面板
├── KeyboardShortcuts.css
├── PlaybackRateIndicator.tsx     # 播放速度指示器
├── AV1Player.tsx                  # AV1 播放器（可选）
└── README.md                      # 本文档
```

## 使用方法

```tsx
import VideoPlayer from '@/components/VideoPlayer'

function VideoPage() {
  return (
    <VideoPlayer
      src="https://example.com/video.m3u8"
      poster="https://example.com/poster.jpg"
      videoId={123}
      autoSaveProgress={true}
      enableSubtitles={true}
      initialTime={0}
      onTimeUpdate={(time) => console.log('Current time:', time)}
      onEnded={() => console.log('Video ended')}
    />
  )
}
```

## Props

| Prop | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `src` | `string` | 必填 | 视频源 URL（支持 HLS/MP4） |
| `poster` | `string` | 可选 | 视频封面图片 URL |
| `videoId` | `number` | 可选 | 视频 ID（用于保存进度和加载字幕） |
| `initialTime` | `number` | `0` | 初始播放位置（秒） |
| `autoSaveProgress` | `boolean` | `true` | 是否自动保存播放进度 |
| `enableSubtitles` | `boolean` | `true` | 是否启用字幕加载 |
| `onTimeUpdate` | `(time: number) => void` | 可选 | 时间更新回调 |
| `onEnded` | `() => void` | 可选 | 播放结束回调 |

## 样式定制

所有样式都使用 CSS 变量，可以通过覆盖这些变量来定制外观：

```css
.video-js {
  --primary-color: #ff0000;          /* 主色调 */
  --control-bar-height: 36px;        /* 控制栏高度 */
  --progress-height: 3px;            /* 进度条高度 */
  --progress-height-hover: 5px;      /* 悬停时进度条高度 */
}
```

## 浏览器支持

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Opera 76+

## 性能特性

1. **懒加载**: 播放器组件支持 React.lazy 懒加载
2. **内存优化**: 组件卸载时自动清理播放器实例
3. **事件节流**: 使用 useCallback 避免不必要的重渲染
4. **高效渲染**: 仅在必要时更新 DOM

## 已知问题

无

## 未来改进

- [ ] 章节标记支持
- [ ] 播放列表自动播放
- [ ] 360° 视频支持
- [ ] VR 模式
- [ ] 更多字幕样式选项

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT

