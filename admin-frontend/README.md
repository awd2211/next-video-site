# Admin Frontend - VideoSite 管理后台

管理后台应用，提供视频管理、用户管理、数据分析、系统配置等功能的企业级管理界面。

## 📋 技术栈

- **框架**: React 18 + TypeScript 5
- **构建工具**: Vite 5
- **UI 库**: Ant Design 5
- **图表**: Ant Design Charts (基于 G2)
- **状态管理**: React Query + React Context
- **路由**: React Router v6
- **HTTP 客户端**: Axios
- **国际化**: i18next
- **表单管理**: Ant Design Form
- **拖拽布局**: React Grid Layout
- **包管理器**: pnpm

## 📁 项目结构

```
admin-frontend/
├── src/
│   ├── pages/                      # 页面组件
│   │   ├── Dashboard/             # 数据仪表板
│   │   │   ├── index.tsx
│   │   │   └── DashboardWidget.tsx
│   │   ├── Videos/                # 视频管理
│   │   │   ├── VideoList.tsx
│   │   │   ├── VideoEdit.tsx
│   │   │   └── BatchUploader.tsx
│   │   ├── Users/                 # 用户管理
│   │   │   ├── UserList.tsx
│   │   │   └── UserDetail.tsx
│   │   ├── Comments/              # 评论审核
│   │   ├── Categories/            # 分类管理
│   │   ├── Banners/               # Banner 管理
│   │   ├── Announcements/         # 公告管理
│   │   ├── Settings/              # 系统设置
│   │   │   ├── General.tsx
│   │   │   ├── Email.tsx
│   │   │   ├── Security.tsx
│   │   │   └── Advanced.tsx
│   │   ├── Logs/                  # 日志管理
│   │   │   ├── OperationLogs.tsx
│   │   │   ├── LoginLogs.tsx
│   │   │   └── ErrorLogs.tsx
│   │   ├── AIManagement/          # AI 配置管理
│   │   ├── SystemHealth/          # 系统健康监控
│   │   ├── Reports/               # 报表分析
│   │   └── Login/                 # 登录页
│   │
│   ├── components/                # 可复用组件
│   │   ├── Layout/                # 布局组件
│   │   │   ├── AdminLayout.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Header.tsx
│   │   ├── NotificationBadge/     # 通知徽章
│   │   ├── NotificationDrawer/    # 通知抽屉
│   │   ├── DashboardWidget/       # 仪表板小部件
│   │   ├── VideoPreviewPopover/   # 视频预览弹窗
│   │   ├── BatchUploader/         # 批量上传组件
│   │   ├── Breadcrumb/            # 面包屑导航
│   │   └── ...
│   │
│   ├── services/                  # API 服务
│   │   ├── api.ts                 # Axios 配置
│   │   ├── adminAuthService.ts    # 管理员认证
│   │   ├── videoService.ts        # 视频管理 API
│   │   ├── userService.ts         # 用户管理 API
│   │   ├── statsService.ts        # 统计数据 API
│   │   ├── systemHealthService.ts # 系统健康 API
│   │   └── ...
│   │
│   ├── contexts/                  # React Context
│   │   ├── AuthContext.tsx        # 认证上下文
│   │   ├── ThemeContext.tsx       # 主题上下文
│   │   └── LanguageContext.tsx    # 语言上下文
│   │
│   ├── hooks/                     # 自定义 Hooks
│   │   ├── useAuth.ts            # 认证 Hook
│   │   ├── useNotifications.ts   # 通知 Hook
│   │   ├── useWebSocket.ts       # WebSocket Hook
│   │   └── ...
│   │
│   ├── i18n/                      # 国际化
│   │   ├── index.ts              # i18n 配置
│   │   └── locales/              # 语言文件
│   │       ├── en-US.json        # 英文
│   │       └── zh-CN.json        # 中文
│   │
│   ├── types/                     # TypeScript 类型定义
│   │   ├── video.ts
│   │   ├── user.ts
│   │   ├── stats.ts
│   │   └── ...
│   │
│   ├── utils/                     # 工具函数
│   │   ├── format.ts             # 格式化函数
│   │   ├── validators.ts         # 表单验证
│   │   ├── export.ts             # 导出功能
│   │   └── ...
│   │
│   ├── App.tsx                    # 应用根组件
│   ├── main.tsx                   # 应用入口
│   └── vite-env.d.ts             # Vite 类型声明
│
├── public/                        # 静态资源
├── index.html                     # HTML 模板
├── vite.config.ts                 # Vite 配置
├── tsconfig.json                  # TypeScript 配置
├── package.json                   # 依赖管理
└── .env.example                  # 环境变量示例
```

## 🚀 快速开始

### 环境要求

- Node.js 18+
- pnpm 8+

### 安装依赖

```bash
# 使用 pnpm（推荐）
pnpm install

# 或使用 npm
npm install
```

### 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件
# VITE_API_BASE_URL=http://localhost:8000
```

### 启动开发服务器

```bash
# 开发模式（热重载）
pnpm run dev

# 或使用 Make 命令（从项目根目录）
cd .. && make admin-run
```

访问 http://localhost:5173（Vite 自动代理到 :3001）

### 默认管理员账户

```
邮箱: admin@example.com
密码: admin123
```

（请在后端创建管理员账户后使用）

### 构建生产版本

```bash
# 构建
pnpm run build

# 预览构建结果
pnpm run preview
```

### 代码检查

```bash
# 运行 ESLint
pnpm run lint

# 类型检查
pnpm run type-check
```

## 🎯 主要功能

### 数据仪表板

- **实时统计**: 视频数、用户数、观看次数、评论数
- **趋势图表**: 用户增长、视频上传、观看趋势
- **热门内容**: 热门视频、热门分类、活跃用户
- **可定制布局**: 拖拽调整小部件位置和大小
- **数据导出**: 导出图表和统计数据

### 视频管理

- **视频列表**: 分页、搜索、筛选、排序
- **批量操作**: 批量删除、批量修改状态、批量分类
- **视频编辑**: 编辑标题、描述、分类、标签等
- **视频上传**: 单个/批量上传，进度跟踪
- **视频预览**: 悬停预览视频信息
- **视频分析**: 播放量、点赞数、评论数统计
- **缩略图管理**: 上传和管理视频封面

### 用户管理

- **用户列表**: 查看所有用户，支持搜索和筛选
- **用户详情**: 查看用户详细信息和活动历史
- **用户封禁**: 封禁/解封用户
- **用户统计**: 注册趋势、活跃度分析
- **批量操作**: 批量封禁、批量删除

### 评论审核

- **评论列表**: 查看所有评论，支持筛选
- **审核操作**: 通过、拒绝、删除评论
- **批量审核**: 批量操作多个评论
- **敏感词过滤**: 自动标记包含敏感词的评论
- **用户评论历史**: 查看用户所有评论

### 系统设置

- **基本设置**: 网站名称、描述、关键词
- **邮件配置**: SMTP 设置、邮件模板
- **安全设置**: IP 黑名单、访问限制
- **高级设置**: 缓存配置、存储配置
- **AI 配置**: AI 服务提供商配置和管理

### 日志管理

- **操作日志**: 记录所有管理员操作
- **登录日志**: 登录历史和安全审计
- **错误日志**: 系统错误记录和追踪
- **日志导出**: 导出日志数据（CSV/Excel）
- **日志搜索**: 按时间、用户、操作类型筛选

### 系统监控

- **实时健康**: CPU、内存、磁盘使用率
- **服务状态**: 数据库、Redis、MinIO 连接状态
- **存储监控**: 对象存储使用情况
- **性能监控**: API 响应时间、慢查询
- **告警通知**: 异常情况实时通知

### 内容管理

- **Banner 管理**: 首页轮播图管理
- **公告管理**: 系统公告发布和管理
- **分类管理**: 视频分类、国家、标签管理
- **推荐管理**: 推荐视频配置

## 🛠️ 开发指南

### 添加新页面

1. 在 `src/pages/` 创建页面组件
2. 在 `src/App.tsx` 中添加路由
3. 在侧边栏菜单中添加入口

```tsx
// src/pages/NewPage/index.tsx
import { Card } from 'antd'

export default function NewPage() {
  return <Card title="新页面">内容</Card>
}

// src/App.tsx
;<Route path="/new-page" element={<NewPage />} />
```

### 使用 Ant Design 组件

```tsx
import { Table, Button, Space, Tag } from 'antd'
import { EditOutlined, DeleteOutlined } from '@ant-design/icons'

function MyTable() {
  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id' },
    { title: '名称', dataIndex: 'name', key: 'name' },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button icon={<EditOutlined />} size="small">
            编辑
          </Button>
          <Button icon={<DeleteOutlined />} size="small" danger>
            删除
          </Button>
        </Space>
      ),
    },
  ]

  return <Table columns={columns} dataSource={data} />
}
```

### 调用 API

使用 React Query 进行数据获取：

```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { videoService } from '@/services/videoService'
import { message } from 'antd'

function VideoManagement() {
  const queryClient = useQueryClient()

  // 获取数据
  const { data, isLoading } = useQuery({
    queryKey: ['admin-videos', { page: 1 }],
    queryFn: () => videoService.getAdminVideos({ page: 1 }),
  })

  // 更新数据
  const deleteMutation = useMutation({
    mutationFn: videoService.deleteVideo,
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['admin-videos'] })
    },
  })

  return <div>{/* 组件内容 */}</div>
}
```

### 添加图表

使用 Ant Design Charts：

```tsx
import { Line, Column, Pie } from '@ant-design/charts'

function StatisticsChart() {
  const config = {
    data: chartData,
    xField: 'date',
    yField: 'value',
    smooth: true,
  }

  return <Line {...config} />
}
```

### 表单处理

```tsx
import { Form, Input, Button, message } from 'antd'

function MyForm() {
  const [form] = Form.useForm()

  const onFinish = async (values: any) => {
    try {
      await submitData(values)
      message.success('提交成功')
      form.resetFields()
    } catch (error) {
      message.error('提交失败')
    }
  }

  return (
    <Form form={form} onFinish={onFinish} layout="vertical">
      <Form.Item label="标题" name="title" rules={[{ required: true, message: '请输入标题' }]}>
        <Input />
      </Form.Item>
      <Form.Item>
        <Button type="primary" htmlType="submit">
          提交
        </Button>
      </Form.Item>
    </Form>
  )
}
```

### 国际化

```tsx
import { useTranslation } from 'react-i18next'

function MyComponent() {
  const { t } = useTranslation()

  return (
    <div>
      <h1>{t('dashboard.title')}</h1>
      <p>{t('dashboard.description')}</p>
    </div>
  )
}
```

## 🎨 主题配置

### 切换主题

```tsx
import { useTheme } from '@/contexts/ThemeContext'
import { Switch } from 'antd'

function ThemeSwitch() {
  const { theme, toggleTheme } = useTheme()

  return (
    <Switch
      checked={theme === 'dark'}
      onChange={toggleTheme}
      checkedChildren="🌙"
      unCheckedChildren="☀️"
    />
  )
}
```

### 自定义主题色

在 `vite.config.ts` 中配置 Ant Design 主题：

```ts
export default defineConfig({
  css: {
    preprocessorOptions: {
      less: {
        modifyVars: {
          'primary-color': '#1890ff',
          'link-color': '#1890ff',
          'border-radius-base': '4px',
        },
      },
    },
  },
})
```

## 🔐 权限管理

### 角色权限

- **超级管理员 (Superadmin)**: 完全访问权限
- **管理员 (Admin)**: 基本管理权限
- **编辑 (Editor)**: 内容管理权限（计划中）

### 路由保护

```tsx
import { Navigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'

function ProtectedRoute({ children, requireSuperadmin = false }) {
  const { user, isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    return <Navigate to="/login" />
  }

  if (requireSuperadmin && !user.is_superadmin) {
    return <Navigate to="/403" />
  }

  return children
}
```

## 📊 数据导出

支持导出格式：

- **CSV**: 文本格式，兼容性好
- **Excel**: 二进制格式，功能丰富
- **JSON**: 程序处理友好

```tsx
import { exportToCSV, exportToExcel } from '@/utils/export'

function ExportButton({ data }) {
  const handleExport = () => {
    exportToCSV(data, 'filename.csv')
    // 或
    exportToExcel(data, 'filename.xlsx')
  }

  return <Button onClick={handleExport}>导出数据</Button>
}
```

## 🔔 通知系统

### 实时通知

使用 WebSocket 接收实时通知：

```tsx
import { useNotifications } from '@/hooks/useNotifications'

function NotificationCenter() {
  const { notifications, unreadCount, markAsRead } = useNotifications()

  return (
    <Badge count={unreadCount}>
      <BellOutlined />
    </Badge>
  )
}
```

## 🐛 常见问题

### API 请求 401 错误

检查：

1. 管理员账户是否已创建
2. 登录凭证是否正确
3. Token 是否已过期（自动刷新应该处理）

### Ant Design 样式不生效

```bash
# 清除缓存
rm -rf node_modules/.vite
pnpm install
pnpm run dev
```

### 图表不显示

1. 检查数据格式是否正确
2. 确认 `@ant-design/charts` 已正确安装
3. 查看浏览器控制台错误信息

## 📚 相关文档

- [Ant Design 文档](https://ant.design/)
- [Ant Design Charts 文档](https://charts.ant.design/)
- [React 官方文档](https://react.dev/)
- [Vite 文档](https://vitejs.dev/)
- [React Query 文档](https://tanstack.com/query/latest)
- [项目开发指南](../CLAUDE.md)

## 🤝 贡献指南

请参考项目根目录的 [CONTRIBUTING.md](../CONTRIBUTING.md)。

## 📄 许可证

MIT License - 详见 [LICENSE](../LICENSE)
