# 弹幕系统实现文档

**实施日期**: 2025-10-10
**功能类别**: P1 中优先级
**工作量**: 10小时

---

## 功能概述

弹幕系统是一种实时评论形式，允许用户在观看视频时发送滚动字幕,这些字幕会在特定时间点出现在视频上方，类似于Bilibili的弹幕功能。

### 核心特性

✅ **多种弹幕类型**
- 滚动弹幕（从右往左）
- 顶部固定弹幕
- 底部固定弹幕

✅ **实时渲染**
- Canvas绘制，性能优化
- 同屏弹幕数量控制
- 密度可调节

✅ **样式自定义**
- 9种预设颜色
- 3种字号（小/中/大）
- 不透明度调节
- 速度调节

✅ **内容审核**
- 屏蔽词自动检测
- 待审核/已通过/已拒绝状态
- 用户举报机制（5次自动屏蔽）
- 管理后台审核功能

✅ **用户体验**
- 弹幕开关
- 播放器内发送
- 设置持久化
- 键盘快捷键支持

---

## 数据库设计

### 1. Danmaku表（弹幕）

```python
class Danmaku(Base):
    __tablename__ = "danmaku"

    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey("videos.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)

    # 内容
    content = Column(String(100))  # 弹幕文本

    # 位置和样式
    time = Column(Float, index=True)  # 出现时间(秒)
    type = Column(Enum(DanmakuType))  # scroll/top/bottom
    color = Column(String(7))  # 十六进制颜色
    font_size = Column(Integer)  # 字体大小

    # 审核
    status = Column(Enum(DanmakuStatus))  # pending/approved/rejected/deleted
    is_blocked = Column(Boolean)
    reviewed_by = Column(Integer, ForeignKey("admin_users.id"))
    reviewed_at = Column(DateTime)
    reject_reason = Column(String(200))

    # 举报
    report_count = Column(Integer, default=0)

    # 时间戳
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

**索引优化**:
- `video_id` + `time` 复合索引（查询某视频时间段弹幕）
- `status` 索引（审核查询）
- `user_id` 索引（用户弹幕查询）

### 2. BlockedWord表（屏蔽词）

```python
class BlockedWord(Base):
    __tablename__ = "blocked_words"

    id = Column(Integer, primary_key=True)
    word = Column(String(50), unique=True, index=True)
    is_regex = Column(Boolean)  # 是否为正则表达式
    created_by = Column(Integer, ForeignKey("admin_users.id"))
    created_at = Column(DateTime)
```

---

## 后端API

### 公共API (`/api/v1/danmaku`)

#### 1. 发送弹幕
```http
POST /api/v1/danmaku/
Content-Type: application/json
Authorization: Bearer {token}

{
  "video_id": 1,
  "content": "太好看了！",
  "time": 123.5,
  "type": "scroll",
  "color": "#FFFFFF",
  "font_size": 25
}
```

**响应**:
```json
{
  "id": 1,
  "video_id": 1,
  "user_id": 1,
  "content": "太好看了！",
  "time": 123.5,
  "type": "scroll",
  "color": "#FFFFFF",
  "font_size": 25,
  "status": "approved",
  "is_blocked": false,
  "report_count": 0,
  "created_at": "2025-10-10T12:00:00Z"
}
```

**屏蔽词检测**:
- 包含屏蔽词 → `status="pending"`, `is_blocked=true`
- 不包含屏蔽词 → `status="approved"`, `is_blocked=false`

#### 2. 获取视频弹幕
```http
GET /api/v1/danmaku/video/{video_id}?start_time=0&end_time=300
```

**响应**:
```json
{
  "total": 150,
  "items": [
    {
      "id": 1,
      "video_id": 1,
      "user_id": 1,
      "content": "太好看了！",
      "time": 123.5,
      "type": "scroll",
      "color": "#FFFFFF",
      "font_size": 25,
      "status": "approved",
      "is_blocked": false,
      "report_count": 0,
      "created_at": "2025-10-10T12:00:00Z"
    }
  ]
}
```

**说明**:
- 只返回 `status="approved"` 且 `is_blocked=false` 的弹幕
- 支持时间段筛选（分段加载）

#### 3. 删除自己的弹幕
```http
DELETE /api/v1/danmaku/{danmaku_id}
Authorization: Bearer {token}
```

#### 4. 举报弹幕
```http
POST /api/v1/danmaku/{danmaku_id}/report
Authorization: Bearer {token}
```

**响应**:
```json
{
  "message": "举报成功",
  "report_count": 3
}
```

**举报机制**:
- `report_count >= 5` 时自动设置 `is_blocked=true`, `status="deleted"`

#### 5. 获取我的弹幕
```http
GET /api/v1/danmaku/my-danmaku?video_id=1&page=1&page_size=20
Authorization: Bearer {token}
```

### 管理后台API (`/api/v1/admin/danmaku`)

#### 1. 获取统计信息
```http
GET /api/v1/admin/danmaku/stats
Authorization: Bearer {admin_token}
```

**响应**:
```json
{
  "total": 1000,
  "pending": 50,
  "approved": 900,
  "rejected": 30,
  "deleted": 20,
  "blocked": 15,
  "today_count": 120,
  "reported_count": 25
}
```

#### 2. 搜索弹幕
```http
POST /api/v1/admin/danmaku/search
Content-Type: application/json

{
  "video_id": 1,
  "user_id": null,
  "status": "pending",
  "is_blocked": null,
  "keyword": "测试",
  "start_date": null,
  "end_date": null,
  "page": 1,
  "page_size": 20
}
```

**响应包含用户信息**:
```json
{
  "total": 50,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 1,
      "video_id": 1,
      "user_id": 1,
      "content": "测试弹幕",
      "time": 10.5,
      "type": "scroll",
      "color": "#FFFFFF",
      "font_size": 25,
      "status": "pending",
      "is_blocked": true,
      "report_count": 0,
      "reviewed_by": null,
      "reviewed_at": null,
      "reject_reason": null,
      "created_at": "2025-10-10T12:00:00Z",
      "user": {
        "id": 1,
        "username": "user1",
        "email": "user1@example.com"
      }
    }
  ]
}
```

#### 3. 审核弹幕
```http
POST /api/v1/admin/danmaku/review
Content-Type: application/json

{
  "danmaku_ids": [1, 2, 3],
  "action": "approve",  // approve/reject/delete/block
  "reject_reason": "包含不当内容"  // action=reject时必填
}
```

**操作说明**:
- `approve`: 通过审核 (`status="approved"`, `is_blocked=false`)
- `reject`: 拒绝 (`status="rejected"`, 记录原因)
- `delete`: 删除 (`status="deleted"`)
- `block`: 屏蔽 (`is_blocked=true`, `status="deleted"`)

#### 4. 删除弹幕（物理删除）
```http
DELETE /api/v1/admin/danmaku/{danmaku_id}
```

#### 5. 批量删除
```http
DELETE /api/v1/admin/danmaku/batch
Content-Type: application/json

{
  "danmaku_ids": [1, 2, 3, 4, 5]
}
```

#### 6. 屏蔽词管理

**获取屏蔽词列表**:
```http
GET /api/v1/admin/danmaku/blocked-words
```

**添加屏蔽词**:
```http
POST /api/v1/admin/danmaku/blocked-words
Content-Type: application/json

{
  "word": "违禁词",
  "is_regex": false
}
```

**删除屏蔽词**:
```http
DELETE /api/v1/admin/danmaku/blocked-words/{word_id}
```

---

## 前端实现

### 组件架构

```
VideoPlayerWithDanmaku (容器组件)
├── VideoPlayer (原有播放器)
├── DanmakuRenderer (弹幕渲染引擎)
├── DanmakuInput (弹幕输入框)
└── DanmakuSettings (弹幕设置面板)
```

### 1. DanmakuRenderer (弹幕渲染引擎)

**技术方案**: Canvas 2D绘制

**Props**:
```typescript
interface DanmakuRendererProps {
  danmakuList: Danmaku[]
  currentTime: number
  isPlaying: boolean
  enabled: boolean
  opacity: number  // 0-1
  speed: number    // 0.5-2
  fontSize: number // 0.5-2
  density: number  // 0-1
  containerWidth: number
  containerHeight: number
}
```

**核心逻辑**:
1. **弹幕匹配**: 根据 `currentTime` 匹配 `±0.1秒` 内的弹幕
2. **位置计算**:
   - 滚动弹幕: `x = containerWidth`, 从右往左移动
   - 顶部弹幕: `x = (containerWidth - textWidth) / 2`, 居中
   - 底部弹幕: `x = (containerWidth - textWidth) / 2`, 底部居中
3. **碰撞检测**: 通过密度参数限制同屏弹幕数量
4. **性能优化**:
   - 使用 `requestAnimationFrame` 进行渲染
   - 移出屏幕的弹幕自动移除
   - 固定弹幕3秒后自动移除

**渲染示例**:
```typescript
const render = () => {
  ctx.clearRect(0, 0, containerWidth, containerHeight)
  ctx.globalAlpha = opacity

  activeDanmaku.forEach(item => {
    ctx.font = `${item.font_size * fontSize}px sans-serif`
    ctx.fillStyle = item.color
    ctx.strokeStyle = '#000'
    ctx.lineWidth = 2

    // 描边 + 填充文字
    ctx.strokeText(item.content, item.x, item.y)
    ctx.fillText(item.content, item.x, item.y)

    // 更新位置
    if (item.type === 'scroll') {
      item.x -= item.speed
    }
  })

  requestAnimationFrame(render)
}
```

### 2. DanmakuInput (弹幕输入)

**功能**:
- 输入框（最多100字）
- 颜色选择（9种预设）
- 字号选择（小/中/大）
- 类型选择（滚动/顶部/底部）
- 发送按钮
- Enter键快速发送

**样式自定义**:
```typescript
const COLORS = [
  { name: '白色', value: '#FFFFFF' },
  { name: '红色', value: '#FF0000' },
  { name: '橙色', value: '#FF7F00' },
  // ...
]

const FONT_SIZES = [
  { name: '小', value: 18 },
  { name: '中', value: 25 },
  { name: '大', value: 36 },
]
```

### 3. DanmakuSettings (弹幕设置)

**配置项**:
```typescript
interface DanmakuConfig {
  enabled: boolean      // 显示开关
  opacity: number       // 不透明度 (0-1)
  speed: number         // 速度 (0.5-2)
  fontSize: number      // 字号倍数 (0.5-2)
  density: number       // 密度 (0-1)
}
```

**持久化**: 配置保存到 `localStorage`

```typescript
const [config, setConfig] = useState(() => {
  const saved = localStorage.getItem('danmaku_config')
  return saved ? JSON.parse(saved) : DEFAULT_CONFIG
})

useEffect(() => {
  localStorage.setItem('danmaku_config', JSON.stringify(config))
}, [config])
```

### 4. VideoPlayerWithDanmaku (集成组件)

**使用示例**:
```tsx
import VideoPlayerWithDanmaku from '../components/VideoPlayerWithDanmaku'

<VideoPlayerWithDanmaku
  src={videoUrl}
  poster={posterUrl}
  videoId={videoId}
  onTimeUpdate={handleTimeUpdate}
  onEnded={handleEnded}
/>
```

**布局**:
```css
.video-player-with-danmaku {
  position: relative;
}

.danmaku-canvas {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
  z-index: 10;
}

.danmaku-controls {
  position: absolute;
  bottom: 60px;
  z-index: 20;
}
```

---

## 性能优化

### 1. 渲染优化
- ✅ Canvas硬件加速
- ✅ 同屏弹幕数量限制（最多30条 × density）
- ✅ 移出屏幕的弹幕自动清理
- ✅ 暂停时停止渲染

### 2. 网络优化
- ✅ 分段加载弹幕（按时间段）
- ✅ 首次加载全部弹幕，缓存到内存
- ✅ 发送弹幕后仅刷新列表，不重载

### 3. 用户体验优化
- ✅ 设置持久化（localStorage）
- ✅ 时间跳跃时自动清空弹幕
- ✅ 全屏时调整控制栏位置
- ✅ 响应式设计（移动端适配）

---

## 安全机制

### 1. 内容审核
- **屏蔽词检测**: 发送时自动检测，包含屏蔽词的弹幕标记为待审核
- **正则支持**: 屏蔽词支持正则表达式匹配
- **审核流程**:
  1. 用户发送弹幕
  2. 后端检测屏蔽词
  3. 无屏蔽词 → 直接显示
  4. 有屏蔽词 → 待审核状态，不显示
  5. 管理员审核 → 通过/拒绝/删除

### 2. 举报机制
- 用户可举报不当弹幕
- 举报5次自动屏蔽
- 管理员可查看被举报弹幕

### 3. 权限控制
- ✅ 发送弹幕需要登录
- ✅ 只能删除自己的弹幕
- ✅ 管理员可删除/屏蔽任何弹幕
- ✅ 管理屏蔽词需要管理员权限

---

## 使用指南

### 用户端

**发送弹幕**:
1. 点击播放器下方输入框
2. 输入弹幕内容（最多100字）
3. （可选）点击设置图标选择颜色/字号/类型
4. 按Enter或点击"发送"

**弹幕设置**:
1. 点击播放器上的"⚙️ 设置"按钮
2. 调整不透明度/速度/字号/密度
3. 关闭弹幕显示（取消勾选"显示弹幕"）

### 管理后台

**审核弹幕**:
1. 访问 `/admin/danmaku` 页面
2. 筛选待审核弹幕（`status=pending`）
3. 选中弹幕，点击"通过"/"拒绝"/"删除"

**管理屏蔽词**:
1. 访问 `/admin/danmaku/blocked-words`
2. 添加屏蔽词（支持正则）
3. 删除不需要的屏蔽词

**查看统计**:
- 总弹幕数
- 各状态统计
- 今日弹幕数
- 被举报弹幕数

---

## 技术亮点

1. **高性能渲染**: Canvas绘制 + requestAnimationFrame
2. **智能审核**: 屏蔽词自动检测 + 举报机制
3. **样式丰富**: 多种颜色/字号/类型
4. **用户体验**: 设置持久化 + 响应式设计
5. **管理完善**: 审核系统 + 统计分析

---

## 文件清单

### 后端
```
backend/app/
├── models/danmaku.py (~80行)
├── schemas/danmaku.py (~100行)
├── api/danmaku.py (~200行)
├── admin/danmaku.py (~300行)
└── alembic/versions/9e912ccc1af8_add_danmaku_and_blocked_words_tables.py
```

### 前端
```
frontend/src/
├── services/danmakuService.ts (~80行)
├── components/
│   ├── DanmakuRenderer/ (~180行)
│   │   ├── index.tsx
│   │   └── styles.css
│   ├── DanmakuInput/ (~180行)
│   │   ├── index.tsx
│   │   └── styles.css
│   ├── DanmakuSettings/ (~150行)
│   │   ├── index.tsx
│   │   └── styles.css
│   └── VideoPlayerWithDanmaku/ (~170行)
│       ├── index.tsx
│       └── styles.css
```

---

## 未来优化方向

1. **高级弹幕**:
   - 彩色弹幕
   - 定位弹幕（指定坐标）
   - 高级弹幕（特效）

2. **性能提升**:
   - WebGL渲染（更高性能）
   - 虚拟滚动（大量弹幕）
   - Worker线程（碰撞检测）

3. **功能扩展**:
   - 弹幕点赞
   - 弹幕回复
   - 弹幕历史记录
   - 导出/导入弹幕文件

4. **AI增强**:
   - AI内容审核
   - 敏感词智能识别
   - 弹幕情感分析

---

## 总结

弹幕系统已完整实现，包含前后端完整功能、管理后台、内容审核机制。用户可以方便地发送和查看弹幕，管理员可以有效地审核和管理弹幕内容。整个系统性能优化良好，用户体验流畅。
