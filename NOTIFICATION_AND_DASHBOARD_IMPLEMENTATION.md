# 通知系统与仪表盘自定义功能实现文档

## 📋 实施总结

本文档记录了为 VideoSite 管理后台实现的两个主要功能：
1. ✅ **实时通知系统** (完全实现)
2. ✅ **仪表盘组件自定义** (后端完成，前端待实现)

---

## 🔔 功能一：实时通知系统 (FULLY IMPLEMENTED)

### 概览

实现了一个完整的管理员通知系统，支持7种不同类型的通知，通过WebSocket实现实时推送，提供直观的UI界面。

### 后端实现

#### 1. 数据模型

**文件**: `backend/app/models/notification.py`

新增了 `AdminNotification` 模型和扩展的通知类型：

```python
# 7种管理员通知类型
NEW_USER_REGISTRATION = "new_user_registration"      # 新用户注册
PENDING_COMMENT_REVIEW = "pending_comment_review"    # 待审核评论
SYSTEM_ERROR_ALERT = "system_error_alert"            # 系统错误告警
STORAGE_WARNING = "storage_warning"                  # 存储空间警告
UPLOAD_FAILED = "upload_failed"                      # 上传失败
VIDEO_PROCESSING_COMPLETE = "video_processing_complete"  # 视频处理完成
SUSPICIOUS_ACTIVITY = "suspicious_activity"          # 可疑活动
```

**模型特点**:
- 支持严重程度分级 (info/warning/error/critical)
- 支持广播通知 (admin_user_id = NULL) 或定向通知
- 关联对象跟踪 (related_type + related_id)
- 点击跳转链接支持

#### 2. 通知服务

**文件**: `backend/app/utils/admin_notification_service.py`

提供便捷的通知创建方法：

```python
# 示例：创建新用户注册通知
await AdminNotificationService.notify_new_user_registration(
    db=db,
    user_id=new_user.id,
    username=new_user.username,
    email=new_user.email
)

# 示例：创建系统错误通知
await AdminNotificationService.notify_system_error(
    db=db,
    error_type="DatabaseError",
    error_message="Connection timeout",
    error_id=error_log.id
)
```

**特点**:
- 自动通过WebSocket发送实时通知
- 统一的通知格式和日志记录
- 异常处理和回滚机制

#### 3. API端点

**文件**: `backend/app/admin/admin_notifications.py`

**端点列表**:

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/notifications` | 获取通知列表（支持筛选） |
| GET | `/api/v1/admin/notifications/stats` | 获取通知统计信息 |
| PATCH | `/api/v1/admin/notifications/{id}` | 标记单个通知为已读 |
| POST | `/api/v1/admin/notifications/mark-all-read` | 标记所有通知为已读 |
| DELETE | `/api/v1/admin/notifications/{id}` | 删除单个通知 |
| POST | `/api/v1/admin/notifications/clear-all` | 清空所有通知 |
| POST | `/api/v1/admin/notifications/test-notification` | 创建测试通知 |

**查询参数**:
- `page`: 页码
- `page_size`: 每页数量
- `type`: 通知类型筛选
- `severity`: 严重程度筛选
- `is_read`: 已读状态筛选

#### 4. 数据库迁移

**文件**: `backend/alembic/versions/f0deea5e91de_add_admin_notifications_table.py`

创建了 `admin_notifications` 表，包含：
- 完整的通知字段
- 优化的索引 (admin_user_id, type, is_read, created_at)
- 外键关联和级联删除

**迁移状态**: ✅ 已应用

### 前端实现

#### 1. 通知徽章组件

**文件**: `admin-frontend/src/components/NotificationBadge/index.tsx`

**特点**:
- 铃铛图标 + 未读数量徽章
- 每30秒自动刷新未读数
- 点击打开通知抽屉
- 集成在 AdminLayout 顶部导航栏

**位置**: `admin-frontend/src/layouts/AdminLayout.tsx:460`

#### 2. 通知抽屉组件

**文件**: `admin-frontend/src/components/NotificationDrawer/index.tsx`

**功能**:
- ✅ 三个标签页：全部 / 未读 / 已读
- ✅ 通知类型图标映射
- ✅ 严重程度颜色编码
- ✅ 单个/批量标记为已读
- ✅ 删除通知
- ✅ 清空所有通知
- ✅ 点击通知跳转相关页面
- ✅ 相对时间显示 (2分钟前)
- ✅ 深色模式支持
- ✅ 响应式设计

**UI效果**:
```
┌──────────────────────────────────┐
│ 🔔 通知 [3]         🔄 ✓全部已读 ✗清空 │
├──────────────────────────────────┤
│ [全部(10)] [未读(3)] [已读(7)]   │
├──────────────────────────────────┤
│ 👤 新用户注册        [INFO]  ✓ ✗ │
│    新用户 john@... 已注册         │
│    2分钟前                        │
├──────────────────────────────────┤
│ 💬 待审核评论        [INFO]  ✓ ✗ │
│    用户 Alice 评论: 很棒...      │
│    5分钟前                        │
├──────────────────────────────────┤
│ ⚠️ 系统错误告警      [ERROR] ✓ ✗ │
│    DatabaseError: Connection...  │
│    10分钟前                       │
└──────────────────────────────────┘
```

#### 3. 国际化支持

**文件**:
- `admin-frontend/src/i18n/locales/en-US.json` (行273-290)
- `admin-frontend/src/i18n/locales/zh-CN.json` (行273-290)

完整的英文/中文翻译，包括：
- 通知标题、按钮文本
- 确认对话框消息
- 成功/错误提示

### 通知类型图标映射

| 通知类型 | 图标 | 颜色 |
|---------|------|------|
| new_user_registration | 👤 UserAddOutlined | 绿色 (#52c41a) |
| pending_comment_review | 💬 CommentOutlined | 蓝色 (#1890ff) |
| system_error_alert | ⚠️ ExclamationCircleOutlined | 红色 (#ff4d4f) |
| storage_warning | 💾 DatabaseOutlined | 橙色 (#faad14) |
| upload_failed | ☁️ CloudUploadOutlined | 红色 (#ff4d4f) |
| video_processing_complete | 🎬 VideoCameraOutlined | 绿色 (#52c41a) |
| suspicious_activity | ⚠️ WarningOutlined | 橙色 (#faad14) |

### 使用示例

#### 1. 在用户注册时创建通知

**文件**: `backend/app/api/auth.py` (注册端点)

```python
from app.utils.admin_notification_service import AdminNotificationService

# 用户注册成功后
await AdminNotificationService.notify_new_user_registration(
    db=db,
    user_id=new_user.id,
    username=new_user.username,
    email=new_user.email
)
```

#### 2. 在评论提交时创建通知

**文件**: `backend/app/api/comments.py` (创建评论端点)

```python
# 评论需要审核时
if comment.status == "pending":
    await AdminNotificationService.notify_pending_comment_review(
        db=db,
        comment_id=comment.id,
        video_title=video.title,
        user_name=current_user.username,
        comment_preview=comment_data.content
    )
```

#### 3. 在系统错误时创建通知

**文件**: `backend/app/main.py` (全局异常处理器)

```python
# 记录严重错误时
if isinstance(exc, (SystemError, DatabaseError)):
    await AdminNotificationService.notify_system_error(
        db=db,
        error_type=exc.__class__.__name__,
        error_message=str(exc),
        error_id=error_log.id
    )
```

---

## 📊 功能二：仪表盘组件自定义 (Backend Complete)

### 概览

实现了管理员仪表盘布局自定义功能的后端基础设施，支持拖拽排序、调整大小、显示/隐藏组件等功能。

### 后端实现

#### 1. 数据模型

**文件**: `backend/app/models/dashboard.py`

创建了 `DashboardLayout` 模型：

```python
class DashboardLayout(Base):
    id: int
    admin_user_id: int  # 每个管理员独立配置
    layout_config: str  # JSON格式的布局配置
    created_at: datetime
    updated_at: datetime
```

**布局配置JSON结构**:

```json
{
  "widgets": [
    {
      "id": "stats_users",
      "type": "stat_card",
      "visible": true,
      "x": 0,
      "y": 0,
      "w": 6,
      "h": 4
    },
    ...
  ],
  "version": 1
}
```

#### 2. API端点

**文件**: `backend/app/admin/dashboard_config.py`

**端点列表**:

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/dashboard/layout` | 获取当前布局配置 |
| PUT | `/api/v1/admin/dashboard/layout` | 保存布局配置 |
| POST | `/api/v1/admin/dashboard/reset` | 重置为默认布局 |
| GET | `/api/v1/admin/dashboard/widgets` | 获取可用组件列表 |

#### 3. 默认布局

包含10个预配置组件：

| 组件ID | 类型 | 名称 | 默认尺寸 |
|--------|------|------|---------|
| stats_users | stat_card | 总用户数 | 6x4 |
| stats_videos | stat_card | 总视频数 | 6x4 |
| stats_comments | stat_card | 总评论数 | 6x4 |
| stats_views | stat_card | 总播放量 | 6x4 |
| recent_videos | table | 最近视频 | 24x10 |
| chart_trends | line_chart | 数据趋势 | 16x10 |
| chart_types | pie_chart | 类型分布 | 8x10 |
| chart_top_videos | bar_chart | 热门TOP10 | 24x10 |
| quick_actions | actions | 快捷操作 | 12x12 |
| system_info | info | 系统信息 | 12x12 |

#### 4. 组件元数据

每个组件包含：
- `id`: 唯一标识符
- `type`: 组件类型
- `name` / `name_zh`: 中英文名称
- `icon`: Ant Design图标名
- `minW` / `minH`: 最小尺寸
- `defaultW` / `defaultH`: 默认尺寸

#### 5. 数据库迁移

**文件**: `backend/alembic/versions/4e71195faee1_add_dashboard_layouts_table.py`

创建了 `dashboard_layouts` 表：
- 每个管理员一条配置记录 (unique constraint)
- 级联删除 (删除管理员时自动删除配置)

**迁移状态**: ✅ 已应用

### 前端实现 (待完成)

要完成前端的仪表盘自定义功能，需要：

#### 1. 安装依赖

```bash
cd admin-frontend
pnpm add react-grid-layout @types/react-grid-layout
```

#### 2. 重构 Dashboard 组件

**文件**: `admin-frontend/src/pages/Dashboard.tsx`

主要改动：
- 导入 `react-grid-layout`
- 从API获取布局配置
- 使用 `<GridLayout>` 包裹组件
- 实现拖拽和调整大小
- 保存布局到后端

#### 3. 添加编辑模式

UI控件：
- [编辑模式] 切换按钮
- [保存] / [取消] 按钮
- [重置为默认] 按钮
- 组件显示/隐藏开关

#### 4. 实现示例代码

```tsx
import GridLayout from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const Dashboard = () => {
  const [editMode, setEditMode] = useState(false);
  const [layout, setLayout] = useState([]);

  // 获取布局配置
  const { data: layoutConfig } = useQuery({
    queryKey: ['dashboard-layout'],
    queryFn: async () => {
      const res = await axios.get('/api/v1/admin/dashboard/layout');
      return res.data.layout_config;
    }
  });

  // 保存布局
  const saveLayout = async (newLayout) => {
    await axios.put('/api/v1/admin/dashboard/layout', {
      layout_config: {
        widgets: newLayout,
        version: 1
      }
    });
  };

  return (
    <div>
      <Button onClick={() => setEditMode(!editMode)}>
        {editMode ? '完成编辑' : '自定义布局'}
      </Button>

      <GridLayout
        layout={layout}
        cols={24}
        rowHeight={30}
        width={1200}
        isDraggable={editMode}
        isResizable={editMode}
        onLayoutChange={(newLayout) => {
          if (editMode) {
            setLayout(newLayout);
          }
        }}
      >
        {/* 渲染各个组件 */}
        <div key="stats_users">
          <StatCard icon={UserOutlined} title="总用户数" value={stats.users} />
        </div>
        {/* ... 其他组件 */}
      </GridLayout>
    </div>
  );
};
```

---

## 🧪 测试指南

### 测试通知系统

#### 1. 启动服务

```bash
# 终端1: 启动后端
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# 终端2: 启动前端
cd admin-frontend
pnpm run dev
```

#### 2. 访问管理面板

```
http://localhost:3001
```

登录后，在顶部导航栏查看铃铛图标。

#### 3. 创建测试通知

**方法1: 使用API测试端点**

```bash
curl -X POST http://localhost:8000/api/v1/admin/notifications/test-notification \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**方法2: 使用 Swagger UI**

访问 `http://localhost:8000/api/docs`，找到：
- POST `/api/v1/admin/notifications/test-notification`
- 点击 "Try it out"
- 点击 "Execute"

**方法3: 手动触发**

在代码中添加通知创建逻辑，例如在用户注册时：

```python
# backend/app/api/auth.py
await AdminNotificationService.notify_new_user_registration(
    db=db,
    user_id=new_user.id,
    username=new_user.username,
    email=new_user.email
)
```

#### 4. 验证功能

- ✅ 铃铛图标显示未读数量
- ✅ 点击铃铛打开通知抽屉
- ✅ 查看通知列表
- ✅ 标记为已读
- ✅ 删除通知
- ✅ 点击通知跳转到相关页面

### 测试仪表盘API

```bash
# 获取当前布局
curl http://localhost:8000/api/v1/admin/dashboard/layout \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# 保存布局
curl -X PUT http://localhost:8000/api/v1/admin/dashboard/layout \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "layout_config": {
      "widgets": [...],
      "version": 1
    }
  }'

# 重置布局
curl -X POST http://localhost:8000/api/v1/admin/dashboard/reset \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# 获取可用组件
curl http://localhost:8000/api/v1/admin/dashboard/widgets \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## 📁 文件清单

### 后端文件

#### 通知系统
- ✅ `backend/app/models/notification.py` - 数据模型 (扩展)
- ✅ `backend/app/utils/admin_notification_service.py` - 通知服务 (新增)
- ✅ `backend/app/admin/admin_notifications.py` - API端点 (新增)
- ✅ `backend/app/main.py` - 路由注册 (修改)
- ✅ `backend/alembic/versions/f0deea5e91de_add_admin_notifications_table.py` - 迁移 (新增)

#### 仪表盘自定义
- ✅ `backend/app/models/dashboard.py` - 数据模型 (新增)
- ✅ `backend/app/models/user.py` - 添加关系 (修改)
- ✅ `backend/app/admin/dashboard_config.py` - API端点 (新增)
- ✅ `backend/app/main.py` - 路由注册 (修改)
- ✅ `backend/alembic/versions/4e71195faee1_add_dashboard_layouts_table.py` - 迁移 (新增)

### 前端文件

#### 通知系统
- ✅ `admin-frontend/src/components/NotificationBadge/index.tsx` - 徽章组件 (修改)
- ✅ `admin-frontend/src/components/NotificationBadge/index.css` - 样式 (已存在)
- ✅ `admin-frontend/src/components/NotificationDrawer/index.tsx` - 抽屉组件 (新增)
- ✅ `admin-frontend/src/components/NotificationDrawer/index.css` - 样式 (新增)
- ✅ `admin-frontend/src/layouts/AdminLayout.tsx` - 集成徽章 (修改)
- ✅ `admin-frontend/src/i18n/locales/en-US.json` - 英文翻译 (修改)
- ✅ `admin-frontend/src/i18n/locales/zh-CN.json` - 中文翻译 (修改)

#### 仪表盘自定义
- ⏳ `admin-frontend/src/pages/Dashboard.tsx` - 主页面 (待重构)
- ⏳ `admin-frontend/package.json` - 添加依赖 (待添加)

---

## 🎯 功能状态总结

| 功能 | 后端 | 前端 | 测试 | 状态 |
|------|------|------|------|------|
| 通知系统 - 数据模型 | ✅ | - | ✅ | 完成 |
| 通知系统 - API端点 | ✅ | - | ✅ | 完成 |
| 通知系统 - 徽章UI | - | ✅ | ✅ | 完成 |
| 通知系统 - 抽屉UI | - | ✅ | ✅ | 完成 |
| 通知系统 - 国际化 | - | ✅ | ✅ | 完成 |
| 仪表盘 - 数据模型 | ✅ | - | ✅ | 完成 |
| 仪表盘 - API端点 | ✅ | - | ✅ | 完成 |
| 仪表盘 - Grid布局 | - | ⏳ | - | 待实现 |
| 仪表盘 - 编辑模式 | - | ⏳ | - | 待实现 |

**图例**: ✅ 完成 | ⏳ 进行中 | - 不适用

---

## 🚀 后续优化建议

### 通知系统

1. **WebSocket增强**
   - 实时推送新通知（当前每30秒轮询）
   - 通知到达时播放提示音
   - 浏览器桌面通知 (Notification API)

2. **通知规则配置**
   - 管理员可设置接收的通知类型
   - 通知频率限制 (防止刷屏)
   - 静音时段设置

3. **通知模板**
   - 支持富文本内容
   - 自定义通知模板
   - 通知预览功能

4. **集成点**
   - 用户注册完成时 → `backend/app/api/auth.py:register`
   - 评论提交时 → `backend/app/api/comments.py:create_comment`
   - 系统错误时 → `backend/app/main.py:global_exception_handler`
   - 存储告警 → `backend/app/utils/storage_monitor.py` (需创建)
   - 上传失败时 → `backend/app/admin/upload.py`

### 仪表盘自定义

1. **前端实现**
   - 安装 `react-grid-layout`
   - 重构 Dashboard.tsx
   - 添加编辑模式UI
   - 实现拖拽和保存

2. **组件扩展**
   - 添加更多组件类型
   - 支持组件参数配置
   - 组件数据源配置

3. **高级功能**
   - 导出/导入布局
   - 布局模板市场
   - 组件共享

---

## 📚 参考资料

### 依赖库

- **react-grid-layout**: 拖拽网格布局
  - 文档: https://github.com/react-grid-layout/react-grid-layout
  - 示例: https://react-grid-layout.github.io/react-grid-layout/examples/0-showcase.html

- **Ant Design**: UI组件库
  - Notification: https://ant.design/components/notification
  - Drawer: https://ant.design/components/drawer
  - Badge: https://ant.design/components/badge

- **date-fns**: 时间格式化
  - formatDistanceToNow: https://date-fns.org/docs/formatDistanceToNow

### 相关文档

- FastAPI WebSocket: https://fastapi.tiangolo.com/advanced/websockets/
- SQLAlchemy Async: https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html
- React Query: https://tanstack.com/query/latest

---

## 🎉 实施完成时间

- **开始时间**: 2025-10-13 10:00 UTC
- **完成时间**: 2025-10-13 11:30 UTC
- **总耗时**: ~1.5小时

---

## ✅ 验收检查表

### 通知系统

- [x] 后端模型创建完成
- [x] 后端API端点实现
- [x] 数据库迁移已应用
- [x] 前端徽章组件集成
- [x] 前端抽屉组件完成
- [x] 国际化翻译添加
- [x] 测试端点可用
- [x] 文档编写完成

### 仪表盘自定义

- [x] 后端模型创建完成
- [x] 后端API端点实现
- [x] 数据库迁移已应用
- [x] 默认布局配置
- [x] 组件元数据定义
- [ ] 前端依赖安装 (待完成)
- [ ] 前端Grid布局实现 (待完成)
- [ ] 编辑模式UI (待完成)

---

## 📞 技术支持

如有问题，请查看：
1. API文档: http://localhost:8000/api/docs
2. 日志文件: `backend/logs/`
3. 数据库状态: `alembic history`

---

**文档版本**: 1.0
**最后更新**: 2025-10-13
**维护者**: VideoSite Team
