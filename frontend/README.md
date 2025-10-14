# Frontend - VideoSite 用户端

用户前端应用，提供视频浏览、播放、互动等功能的现代化 Web 界面。

## 📋 技术栈

- **框架**: React 18 + TypeScript 5
- **构建工具**: Vite 5
- **样式**: TailwindCSS 3
- **状态管理**: TanStack Query (React Query) + Zustand
- **路由**: React Router v6
- **视频播放器**: Video.js + HLS.js
- **HTTP 客户端**: Axios
- **国际化**: i18next
- **图标**: Lucide React
- **包管理器**: pnpm

## 📁 项目结构

```
frontend/
├── src/
│   ├── components/              # 可复用组件
│   │   ├── VideoPlayer/        # 视频播放器组件
│   │   │   ├── VideoPlayer.tsx
│   │   │   ├── Controls.tsx
│   │   │   └── Settings.tsx
│   │   ├── VideoCard/          # 视频卡片
│   │   ├── Header/             # 页头
│   │   ├── Footer/             # 页脚
│   │   ├── Layout/             # 布局组件
│   │   ├── SearchBar/          # 搜索栏
│   │   ├── LanguageSwitcher/   # 语言切换
│   │   └── ...
│   │
│   ├── pages/                  # 页面组件
│   │   ├── Home/               # 首页
│   │   ├── VideoDetail/        # 视频详情
│   │   ├── Category/           # 分类页
│   │   ├── Search/             # 搜索页
│   │   ├── Profile/            # 个人中心
│   │   ├── Login/              # 登录
│   │   └── Register/           # 注册
│   │
│   ├── services/               # API 服务
│   │   ├── api.ts             # Axios 配置
│   │   ├── videoService.ts    # 视频相关 API
│   │   ├── authService.ts     # 认证相关 API
│   │   ├── commentService.ts  # 评论相关 API
│   │   └── ...
│   │
│   ├── contexts/               # React Context
│   │   ├── AuthContext.tsx    # 认证上下文
│   │   ├── ThemeContext.tsx   # 主题上下文
│   │   └── LanguageContext.tsx # 语言上下文
│   │
│   ├── hooks/                  # 自定义 Hooks
│   │   ├── useAuth.ts         # 认证 Hook
│   │   ├── useVideos.ts       # 视频数据 Hook
│   │   ├── useDebounce.ts     # 防抖 Hook
│   │   └── useInfiniteScroll.ts # 无限滚动
│   │
│   ├── i18n/                   # 国际化
│   │   ├── index.ts           # i18n 配置
│   │   └── locales/           # 语言文件
│   │       ├── en-US.json     # 英文
│   │       └── zh-CN.json     # 中文
│   │
│   ├── types/                  # TypeScript 类型定义
│   │   ├── video.ts
│   │   ├── user.ts
│   │   └── ...
│   │
│   ├── utils/                  # 工具函数
│   │   ├── format.ts          # 格式化函数
│   │   ├── storage.ts         # LocalStorage 封装
│   │   └── validators.ts      # 表单验证
│   │
│   ├── App.tsx                 # 应用根组件
│   ├── main.tsx                # 应用入口
│   └── vite-env.d.ts           # Vite 类型声明
│
├── public/                     # 静态资源
│   ├── favicon.ico
│   └── images/
│
├── index.html                  # HTML 模板
├── vite.config.ts              # Vite 配置
├── tailwind.config.js          # TailwindCSS 配置
├── tsconfig.json               # TypeScript 配置
├── package.json                # 依赖管理
└── .env.example               # 环境变量示例
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
cd .. && make frontend-run
```

访问 http://localhost:5173（Vite 自动代理到 :3000）

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

## 🎨 主要功能

### 视频浏览

- **首页**: 推荐视频、热门视频、最新视频
- **分类浏览**: 按分类、国家、年份筛选
- **搜索**: 全文搜索、自动完成
- **无限滚动**: 自动加载更多内容

### 视频播放

- **Video.js 播放器**: YouTube 风格的控制界面
- **HLS 支持**: 自适应码率流媒体
- **键盘快捷键**: 空格暂停/播放、方向键快进/快退
- **记忆播放**: 断点续播功能
- **全屏支持**: 网页全屏和浏览器全屏
- **倍速播放**: 0.5x - 2.0x 速度调节

### 用户互动

- **评论系统**: 发表评论、回复、点赞
- **评分**: 5 星评分系统
- **收藏**: 添加到收藏夹
- **观看历史**: 自动记录观看进度
- **弹幕**: 实时弹幕显示（B 站风格）

### 用户中心

- **个人信息**: 查看和编辑个人资料
- **观看历史**: 查看观看记录
- **收藏夹**: 管理收藏的视频
- **评论管理**: 查看和管理自己的评论

### 主题和国际化

- **深色/浅色主题**: 自动切换或手动选择
- **多语言支持**: 中文、英文
- **响应式设计**: 适配移动端、平板、桌面

## 🛠️ 开发指南

### 添加新页面

1. 在 `src/pages/` 创建页面组件
2. 在 `src/App.tsx` 中添加路由
3. 更新导航菜单（如需要）

```tsx
// src/pages/NewPage/index.tsx
export default function NewPage() {
  return <div>New Page</div>;
}

// src/App.tsx
import NewPage from './pages/NewPage';

<Route path="/new-page" element={<NewPage />} />;
```

### 调用 API

使用 TanStack Query 进行数据获取：

```tsx
import { useQuery } from '@tanstack/react-query';
import { videoService } from '@/services/videoService';

function VideoList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['videos', { page: 1 }],
    queryFn: () => videoService.getVideos({ page: 1 }),
  });

  if (isLoading) return <div>加载中...</div>;
  if (error) return <div>错误: {error.message}</div>;

  return (
    <div>
      {data.items.map((video) => (
        <VideoCard key={video.id} video={video} />
      ))}
    </div>
  );
}
```

### 添加国际化文本

1. 在 `src/i18n/locales/zh-CN.json` 添加中文文本
2. 在 `src/i18n/locales/en-US.json` 添加英文文本
3. 在组件中使用 `useTranslation` Hook

```tsx
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();

  return <h1>{t('common.welcome')}</h1>;
}
```

### 状态管理

使用 TanStack Query 管理服务器状态：

```tsx
// 获取数据
const { data } = useQuery({ queryKey: ['key'], queryFn: fetchData });

// 更新数据
const mutation = useMutation({
  mutationFn: updateData,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['key'] });
  },
});
```

使用 Zustand 管理客户端状态（如需要）：

```tsx
import create from 'zustand';

const useStore = create((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}));
```

### 样式开发

使用 TailwindCSS 实用类：

```tsx
<div className="flex items-center justify-between p-4 bg-white dark:bg-gray-800">
  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">标题</h1>
</div>
```

自定义样式（如需要）：

```css
/* src/styles/custom.css */
.custom-class {
  /* 自定义样式 */
}
```

## 🔑 核心概念

### 认证流程

1. 用户登录，获取 access_token 和 refresh_token
2. 将令牌存储在 localStorage
3. 在 Axios 拦截器中自动添加 Authorization 头
4. 令牌过期时自动刷新

### API 代理配置

开发环境中，Vite 配置了代理避免 CORS 问题：

```ts
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

### 路由保护

使用 `ProtectedRoute` 组件保护需要认证的路由：

```tsx
<Route
  path="/profile"
  element={
    <ProtectedRoute>
      <Profile />
    </ProtectedRoute>
  }
/>
```

## 📱 响应式断点

TailwindCSS 断点：

- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px
- `2xl`: 1536px

```tsx
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
  {/* 移动端 1 列，小屏 2 列，大屏 4 列 */}
</div>
```

## 🎨 主题配置

主题由 ThemeContext 管理：

```tsx
import { useTheme } from '@/contexts/ThemeContext';

function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return <button onClick={toggleTheme}>{theme === 'dark' ? '🌙' : '☀️'}</button>;
}
```

## 🐛 常见问题

### API 请求失败

检查：

1. 后端是否已启动 (http://localhost:8000)
2. `.env` 中的 API 地址是否正确
3. 浏览器控制台查看具体错误

### 热重载不工作

```bash
# 清除缓存重新启动
rm -rf node_modules/.vite
pnpm run dev
```

### TypeScript 类型错误

```bash
# 运行类型检查
pnpm run type-check

# 重启 TypeScript 服务器（VSCode）
Cmd/Ctrl + Shift + P -> "TypeScript: Restart TS Server"
```

## 📚 相关文档

- [React 官方文档](https://react.dev/)
- [Vite 文档](https://vitejs.dev/)
- [TailwindCSS 文档](https://tailwindcss.com/)
- [TanStack Query 文档](https://tanstack.com/query/latest)
- [React Router 文档](https://reactrouter.com/)
- [Video.js 文档](https://videojs.com/)
- [项目开发指南](../CLAUDE.md)

## 🤝 贡献指南

请参考项目根目录的 [CONTRIBUTING.md](../CONTRIBUTING.md)。

## 📄 许可证

MIT License - 详见 [LICENSE](../LICENSE)
