<!-- 2b601db8-2ed1-4b87-95bd-265bef9de7ce a42fee77-50b5-46d2-83a9-69b073860e20 -->
# 前端系统优化计划

## 优化目标

提升应用性能、改善用户体验、增强代码质量和可维护性。

---

## 阶段一：关键问题修复（已完成 ✅）

### 1. VideoDetail 播放器功能恢复 ✅

**问题**：播放器缺少关键功能

- ❌ 未传递 `videoId` 导致进度无法保存
- ❌ 未从历史恢复播放位置
- ❌ 字幕无法自动加载

**修复内容**：

```tsx
// frontend/src/pages/VideoDetail/index.tsx
<VideoPlayer
  src={video.video_url}
  poster={video.backdrop_url || video.poster_url}
  videoId={video.id}  // ✅ 添加
  initialTime={initialTime}  // ✅ 从历史恢复
  autoSaveProgress={true}  // ✅ 启用自动保存
  enableSubtitles={true}  // ✅ 启用字幕
/>
```

**影响**：核心功能正常，用户体验大幅提升

---

## 阶段二：性能优化（1-2周）

### 2. React 组件优化

#### 2.1 VideoCard 组件优化

**文件**：`frontend/src/components/VideoCard/index.tsx`

**当前问题**：

- 使用了 `memo` 但没有自定义比较函数
- 每次父组件重渲染都会重新渲染所有 VideoCard

**优化方案**：

```tsx
const VideoCard: React.FC<VideoCardProps> = memo(({
  video,
  showQuickActions = true,
  enablePreview = true
}) => {
  // 组件代码
}, (prevProps, nextProps) => {
  // 自定义比较函数
  return prevProps.video.id === nextProps.video.id &&
         prevProps.video.poster_url === nextProps.video.poster_url &&
         prevProps.showQuickActions === nextProps.showQuickActions &&
         prevProps.enablePreview === nextProps.enablePreview
})
```

**预期收益**：减少 50-70% 不必要的组件重渲染

#### 2.2 虚拟滚动实现

**文件**：`frontend/src/pages/Home/index.tsx`, `frontend/src/pages/Category/index.tsx`

**当前问题**：

- 大量视频卡片同时渲染
- 滚动性能差，尤其在低端设备

**实施步骤**：

```bash
pnpm add react-window @types/react-window
```



```tsx
import { FixedSizeGrid } from 'react-window'

<FixedSizeGrid
  columnCount={6}
  columnWidth={200}
  height={600}
  rowCount={Math.ceil(videos.length / 6)}
  rowHeight={280}
  width={1200}
>
  {({ columnIndex, rowIndex, style }) => (
    <div style={style}>
      <VideoCard video={videos[rowIndex * 6 + columnIndex]} />
    </div>
  )}
</FixedSizeGrid>
```

**预期收益**：

- 初始渲染时间减少 60-80%
- 滚动 FPS 从 30 提升到 60
- 内存占用减少 50%

### 3. React Query 缓存优化

**文件**：`frontend/src/main.tsx`

**当前配置**：基础配置，缓存策略不够优化

**优化方案**：

```tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000,      // 5分钟内数据新鲜
      cacheTime: 10 * 60 * 1000,     // 缓存保留10分钟
      refetchOnMount: false,         // 避免重复获取
      refetchInterval: false,        // 禁用轮询
    },
  },
})
```

**针对不同数据的策略**：

```tsx
// 视频详情：短期缓存
useQuery(['video', id], fetchVideo, {
  staleTime: 2 * 60 * 1000,
  cacheTime: 5 * 60 * 1000,
})

// 分类列表：长期缓存
useQuery(['categories'], fetchCategories, {
  staleTime: 30 * 60 * 1000,
  cacheTime: 60 * 60 * 1000,
})

// 搜索结果：不缓存
useQuery(['search', term], fetchSearch, {
  staleTime: 0,
  cacheTime: 0,
})
```

**预期收益**：

- 减少 40-60% API 请求
- 页面切换速度提升 2-3 倍

### 4. 图片加载优化

#### 4.1 WebP 格式支持

**文件**：`frontend/src/components/LazyImage/index.tsx`

**实施方案**：

```tsx
<picture>
  <source 
    srcSet={`${src}.webp`} 
    type="image/webp" 
  />
  <source 
    srcSet={src} 
    type="image/jpeg" 
  />
  <img 
    src={src} 
    alt={alt}
    loading="lazy"
    decoding="async"
  />
</picture>
```

**预期收益**：图片体积减少 25-35%

#### 4.2 渐进式加载

**添加模糊占位符**：

```tsx
const [isLoaded, setIsLoaded] = useState(false)

<div className="relative">
  {!isLoaded && (
    <div className="absolute inset-0 bg-gray-700 animate-pulse" />
  )}
  <img 
    onLoad={() => setIsLoaded(true)}
    className={`transition-opacity duration-300 ${
      isLoaded ? 'opacity-100' : 'opacity-0'
    }`}
  />
</div>
```

**预期收益**：感知加载速度提升 30-40%

### 5. 代码分割优化

#### 5.1 路由预加载

**文件**：`frontend/src/App.tsx`

**当前**：基础懒加载

**优化**：添加预加载策略

```tsx
// 预加载关键路由
useEffect(() => {
  const timer = setTimeout(() => {
    import('./pages/VideoDetail')
    import('./pages/Search')
  }, 2000)
  return () => clearTimeout(timer)
}, [])
```

#### 5.2 组件级代码分割

```tsx
// 大型组件懒加载
const HeavyComponent = lazy(() => 
  import(/* webpackChunkName: "heavy" */ './HeavyComponent')
)
```

**预期收益**：

- 首屏加载时间减少 30-40%
- FCP (First Contentful Paint) 提升 1-2 秒

---

## 阶段三：用户体验优化（2-3周）

### 6. 骨架屏替代加载动画

**创建统一的骨架屏组件**：

```tsx
// frontend/src/components/Skeleton/index.tsx

export const VideoCardSkeleton = () => (
  <div className="animate-pulse">
    <div className="aspect-video bg-gray-700 rounded-t-lg" />
    <div className="p-3 space-y-2">
      <div className="h-4 bg-gray-700 rounded w-3/4" />
      <div className="h-3 bg-gray-700 rounded w-1/2" />
    </div>
  </div>
)

export const VideoDetailSkeleton = () => (
  <div className="animate-pulse space-y-4">
    <div className="aspect-video bg-gray-700 rounded-lg" />
    <div className="h-8 bg-gray-700 rounded w-2/3" />
    <div className="h-4 bg-gray-700 rounded w-full" />
  </div>
)
```

**应用到所有加载状态**：

```tsx
// VideoDetail 页面
{isLoading ? <VideoDetailSkeleton /> : <VideoPlayer {...props} />}

// Home 页面
{isLoading ? (
  <div className="grid grid-cols-6 gap-4">
    {[...Array(12)].map((_, i) => <VideoCardSkeleton key={i} />)}
  </div>
) : (
  videos.map(v => <VideoCard video={v} />)
)}
```

**预期收益**：感知性能提升 40-50%

### 7. 错误处理增强

**文件**：`frontend/src/components/ErrorBoundary/index.tsx`

**添加功能**：

```tsx
// 1. 重试功能
handleRetry = () => {
  this.setState({ hasError: false, error: null })
  window.location.reload()
}

// 2. 错误上报
componentDidCatch(error, errorInfo) {
  if (process.env.NODE_ENV === 'production') {
    // 上报到监控服务
    logErrorToService({
      error: error.toString(),
      stack: errorInfo.componentStack,
      url: window.location.href,
      timestamp: new Date().toISOString(),
    })
  }
}

// 3. 友好的错误界面
render() {
  if (this.state.hasError) {
    return (
      <div className="error-container">
        <h2>出错了</h2>
        <p>{this.state.error?.message}</p>
        <button onClick={this.handleRetry}>重试</button>
        <button onClick={() => navigate('/')}>返回首页</button>
      </div>
    )
  }
}
```

### 8. 空状态优化

**创建统一的空状态组件**：

```tsx
// frontend/src/components/EmptyState/index.tsx
<EmptyState
  icon={<VideoOff className="w-16 h-16" />}
  title="暂无视频"
  description="这里还没有内容，去其他地方看看吧"
  action={
    <button onClick={() => navigate('/')}>
      浏览推荐
    </button>
  }
/>
```

**应用场景**：

- 搜索无结果
- 收藏夹为空
- 观看历史为空
- 视频不存在

---

## 阶段四：SEO 和可访问性（1周）

### 9. SEO 优化

**安装依赖**：

```bash
pnpm add react-helmet-async
```

**实施方案**：

```tsx
// frontend/src/pages/VideoDetail/index.tsx
import { Helmet } from 'react-helmet-async'

<Helmet>
  <title>{video.title} - VideoSite</title>
  <meta name="description" content={video.description} />
  <meta property="og:title" content={video.title} />
  <meta property="og:description" content={video.description} />
  <meta property="og:image" content={video.poster_url} />
  <meta property="og:url" content={`https://yoursite.com/video/${video.id}`} />
  <meta property="og:type" content="video.other" />
  <meta name="twitter:card" content="player" />
  <link rel="canonical" href={`https://yoursite.com/video/${video.id}`} />
</Helmet>
```

**结构化数据**：

```tsx
<script type="application/ld+json">
{JSON.stringify({
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": video.title,
  "description": video.description,
  "thumbnailUrl": video.poster_url,
  "uploadDate": video.created_at,
  "duration": `PT${video.duration}M`,
})}
</script>
```

### 10. 可访问性改进

**键盘导航**：

```tsx
// 添加键盘快捷键提示
<div role="region" aria-label="视频播放器">
  <VideoPlayer {...props} />
</div>

// 焦点管理
useEffect(() => {
  const firstFocusable = document.querySelector('[tabindex="0"]')
  firstFocusable?.focus()
}, [])
```

**ARIA 标签**：

```tsx
<button 
  aria-label="播放视频"
  aria-pressed={isPlaying}
>
  {isPlaying ? '暂停' : '播放'}
</button>
```

---

## 阶段五：性能监控（1周）

### 11. Web Vitals 监控

**安装依赖**：

```bash
pnpm add web-vitals
```

**实施方案**：

```tsx
// frontend/src/utils/performance.ts
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'

export const initPerformanceMonitoring = () => {
  const sendToAnalytics = (metric) => {
    const body = JSON.stringify(metric)
    
    if (process.env.NODE_ENV === 'production') {
      // 发送到后端分析服务
      fetch('/api/v1/analytics/web-vitals', {
        method: 'POST',
        body,
        headers: { 'Content-Type': 'application/json' },
      })
    } else {
      console.log('Web Vital:', metric)
    }
  }

  getCLS(sendToAnalytics)
  getFID(sendToAnalytics)
  getFCP(sendToAnalytics)
  getLCP(sendToAnalytics)
  getTTFB(sendToAnalytics)
}
```

**监控指标**：

- LCP (Largest Contentful Paint): < 2.5s
- FID (First Input Delay): < 100ms
- CLS (Cumulative Layout Shift): < 0.1

### 12. 自定义性能指标

```tsx
// 页面加载时间
const measurePageLoad = () => {
  window.addEventListener('load', () => {
    const perfData = window.performance.timing
    const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart
    
    console.log('Page Load Time:', pageLoadTime, 'ms')
  })
}

// API 请求时间
const measureApiCall = async (url, options) => {
  const start = performance.now()
  const response = await fetch(url, options)
  const duration = performance.now() - start
  
  console.log(`API Call to ${url}: ${duration}ms`)
  return response
}
```

---

## 阶段六：PWA 支持（可选，1-2周）

### 13. PWA 实现

**安装插件**：

```bash
pnpm add vite-plugin-pwa -D
```

**配置**：

```tsx
// vite.config.ts
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,jpg}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.yoursite\.com\/.*$/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 300,
              },
            },
          },
        ],
      },
      manifest: {
        name: 'VideoSite',
        short_name: 'VideoSite',
        description: '在线视频平台',
        theme_color: '#E50914',
        background_color: '#141414',
        display: 'standalone',
        icons: [
          {
            src: '/pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: '/pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
          },
        ],
      },
    }),
  ],
})
```

**功能**：

- 离线访问
- 安装到桌面
- 推送通知
- 后台同步

---

## 阶段七：代码质量（持续）

### 14. TypeScript 严格模式

**配置**：

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
  }
}
```

### 15. ESLint 规则增强

```bash
pnpm add -D @tanstack/eslint-plugin-query eslint-plugin-react-hooks
```



```js
// .eslintrc.js
module.exports = {
  extends: [
    '@tanstack/eslint-plugin-query/recommended',
  ],
  rules: {
    'react-hooks/exhaustive-deps': 'warn',
    '@tanstack/query/exhaustive-deps': 'error',
    'no-console': ['warn', { allow: ['warn', 'error'] }],
  },
}
```

---

## 性能目标

### 当前性能（估计）：

- 首屏加载：3-5 秒
- LCP：4-6 秒
- FID：200-300ms
- 视频列表渲染：100-200 个卡片

### 目标性能：

- 首屏加载：**< 2 秒** ⬇️ 40-60%
- LCP：**< 2.5 秒** ⬇️ 38-58%
- FID：**< 100ms** ⬇️ 50-67%
- 无限滚动：**60 FPS** ⬆️ 100%

---

## 实施时间表

| 阶段 | 时间 | 优先级 |

|------|------|--------|

| 阶段一：关键修复 | ✅ 已完成 | 🔴 最高 |

| 阶段二：性能优化 | 1-2 周 | 🔴 最高 |

| 阶段三：用户体验 | 2-3 周 | 🟡 高 |

| 阶段四：SEO | 1 周 | 🟡 高 |

| 阶段五：监控 | 1 周 | 🟢 中 |

| 阶段六：PWA | 1-2 周 | 🔵 低（可选） |

| 阶段七：代码质量 | 持续 | 🟢 中 |

**总计时间：6-10 周**

---

## 验收标准

### 性能指标：

- ✅ Lighthouse 评分 > 90
- ✅ 首屏加载 < 2s
- ✅ LCP < 2.5s
- ✅ FID < 100ms
- ✅ CLS < 0.1

### 用户体验：

- ✅ 无明显卡顿
- ✅ 流畅的滚动
- ✅ 快速的页面切换
- ✅ 友好的错误提示

### 代码质量：

- ✅ 无 TypeScript 错误
- ✅ 无 ESLint 错误
- ✅ 测试覆盖率 > 60%

---

---

## 🔴 阶段零：严重安全问题修复（立即！）

### 16. 🚨 认证和安全漏洞

#### 16.1 XSS 攻击风险

**问题**：直接使用 localStorage 存储 token，容易被 XSS 攻击窃取

**当前代码** (`frontend/src/services/api.ts`):

```tsx
const token = localStorage.getItem('access_token')  // ❌ 不安全
```

**修复方案**：

```tsx
// 使用 HttpOnly Cookie 存储 token（需要后端支持）
// 或者使用加密的 sessionStorage
import CryptoJS from 'crypto-js'

const SECRET_KEY = import.meta.env.VITE_STORAGE_SECRET

const secureStorage = {
  setItem: (key: string, value: string) => {
    const encrypted = CryptoJS.AES.encrypt(value, SECRET_KEY).toString()
    sessionStorage.setItem(key, encrypted)
  },
  getItem: (key: string) => {
    const encrypted = sessionStorage.getItem(key)
    if (!encrypted) return null
    return CryptoJS.AES.decrypt(encrypted, SECRET_KEY).toString(CryptoJS.enc.Utf8)
  }
}
```

**影响**：🔴 高危 - 可能导致账号被盗

#### 16.2 Token 刷新死循环

**问题**：Token 刷新可能导致无限循环

**当前代码** (`frontend/src/services/api.ts:28`):

```tsx
const response = await axios.post('/api/v1/auth/refresh', {
  refresh_token: refreshToken,
})
// ❌ 如果 refresh 也返回 401，会无限循环
```

**修复方案**：

```tsx
let isRefreshing = false
let failedQueue = []

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // 等待刷新完成
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        })
      }
      
      originalRequest._retry = true
      isRefreshing = true
      
      try {
        const refreshToken = secureStorage.getItem('refresh_token')
        const response = await axios.post('/api/v1/auth/refresh', {
          refresh_token: refreshToken,
        })
        
        const newToken = response.data.access_token
        secureStorage.setItem('access_token', newToken)
        
        // 处理队列中的请求
        failedQueue.forEach(prom => prom.resolve(newToken))
        failedQueue = []
        
        return api(originalRequest)
      } catch (err) {
        failedQueue.forEach(prom => prom.reject(err))
        failedQueue = []
        
        // 清除 token 并跳转
        secureStorage.clear()
        window.location.href = '/login'
        return Promise.reject(err)
      } finally {
        isRefreshing = false
      }
    }
    
    return Promise.reject(error)
  }
)
```

#### 16.3 认证状态不同步

**问题**：Header 组件直接读取 localStorage，不会在 token 变化时更新

**当前代码** (`frontend/src/components/Header/index.tsx:7`):

```tsx
const isAuthenticated = !!localStorage.getItem('access_token')  
// ❌ 只在组件挂载时读取一次
```

**修复方案**：

```tsx
// 创建认证状态管理
// frontend/src/store/authStore.ts
import { create } from 'zustand'

interface AuthState {
  isAuthenticated: boolean
  user: User | null
  setAuth: (user: User | null) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: !!secureStorage.getItem('access_token'),
  user: null,
  setAuth: (user) => set({ isAuthenticated: !!user, user }),
  logout: () => {
    secureStorage.clear()
    set({ isAuthenticated: false, user: null })
  }
}))

// 在 Header 中使用
const { isAuthenticated, logout } = useAuthStore()
```

#### 16.4 CSRF 攻击防护缺失

**问题**：没有 CSRF Token 防护

**修复方案**：

```tsx
// 添加 CSRF token
api.interceptors.request.use((config) => {
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
  if (csrfToken) {
    config.headers['X-CSRF-Token'] = csrfToken
  }
  return config
})
```

#### 16.5 API 密钥暴露

**问题**：环境变量可能在打包后暴露

**当前代码** (`frontend/src/services/downloadService.ts:7`):

```tsx
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
// ❌ VITE_ 前缀的变量会被打包进客户端代码
```

**修复方案**：

```tsx
// 不要在前端存储敏感配置
// 应该从后端 API 获取配置
const getApiConfig = async () => {
  const response = await fetch('/api/v1/config/public')
  return response.json()
}
```

### 17. 🚨 内存泄漏风险

#### 17.1 useEffect 清理不完整

**问题**：`useWatchHistory` hook 有内存泄漏

**当前代码** (`frontend/src/hooks/useWatchHistory.ts:71`):

```tsx
useEffect(() => {
  return () => {
    // ❌ 异步操作没有取消
    saveWatchProgress(currentTime, isCompleted)
  }
}, [enabled, duration, saveWatchProgress])
```

**修复方案**：

```tsx
useEffect(() => {
  let isMounted = true
  
  return () => {
    isMounted = false
    if (isMounted && enabled && playerRef.current) {
      // 只在组件仍然挂载时保存
      saveWatchProgress(currentTime, isCompleted)
    }
  }
}, [enabled, duration, saveWatchProgress])
```

#### 17.2 VideoCard 悬停定时器未清理

**当前代码** (`frontend/src/components/VideoCard/index.tsx:46`):

```tsx
hoverTimeoutRef.current = setTimeout(() => {
  setShowPreview(true)
}, 800)
// ❌ 组件卸载时可能未清理
```

**修复方案**：

```tsx
useEffect(() => {
  return () => {
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current)
    }
  }
}, [])
```

### 18. 🚨 错误处理不足

#### 18.1 API 调用缺少错误边界

**问题**：所有服务没有统一的错误处理

**修复方案**：

```tsx
// frontend/src/utils/apiErrorHandler.ts
export const handleApiError = (error: any) => {
  if (error.response) {
    // 服务器返回错误
    const status = error.response.status
    const message = error.response.data?.detail || error.response.data?.message
    
    switch (status) {
      case 400:
        toast.error(`请求错误: ${message}`)
        break
      case 401:
        toast.error('未授权，请重新登录')
        break
      case 403:
        toast.error('权限不足')
        break
      case 404:
        toast.error('资源不存在')
        break
      case 500:
        toast.error('服务器错误，请稍后重试')
        break
      default:
        toast.error(`错误: ${message || '未知错误'}`)
    }
  } else if (error.request) {
    // 请求发出但无响应
    toast.error('网络错误，请检查您的网络连接')
  } else {
    // 其他错误
    toast.error('发生错误，请稍后重试')
  }
  
  // 上报错误
  if (process.env.NODE_ENV === 'production') {
    logErrorToService(error)
  }
}
```

#### 18.2 React Query 错误处理缺失

**问题**：没有全局错误处理器

**修复方案**：

```tsx
// frontend/src/main.tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error: any) => {
        // 401/403 不重试
        if ([401, 403].includes(error?.response?.status)) {
          return false
        }
        return failureCount < 2
      },
      onError: (error) => {
        handleApiError(error)
      },
    },
    mutations: {
      onError: (error) => {
        handleApiError(error)
      },
    },
  },
})
```

### 19. 🚨 类型安全问题

#### 19.1 过度使用 any 类型

**问题**：大量使用 `any` 类型，失去类型检查

**修复位置**：

- `frontend/src/pages/VideoDetail/index.tsx:20` - `playerRef.current: any`
- `frontend/src/components/VideoPlayer/index.tsx:34` - `playerRef.current: any`

**修复方案**：

```tsx
// 定义 Video.js Player 类型
import type Player from 'video.js/dist/types/player'

const playerRef = useRef<Player | null>(null)
```

#### 19.2 缺少 API 响应类型验证

**问题**：API 响应没有运行时验证

**修复方案**：

```bash
pnpm add zod
```



```tsx
// frontend/src/types/schemas.ts
import { z } from 'zod'

export const VideoSchema = z.object({
  id: z.number(),
  title: z.string(),
  video_url: z.string().url(),
  poster_url: z.string().url().optional(),
  duration: z.number().optional(),
  // ...
})

export type Video = z.infer<typeof VideoSchema>

// 在 service 中使用
export const getVideo = async (id: number): Promise<Video> => {
  const response = await api.get(`/videos/${id}`)
  return VideoSchema.parse(response.data)
}
```

### 20. 🚨 性能陷阱

#### 20.1 无限滚动内存泄漏

**问题**：Home 页面无限滚动累积大量 DOM 节点

**修复方案**：参考阶段二的虚拟滚动方案

#### 20.2 重复的 API 请求

**问题**：VideoDetail 页面同时发起多个请求获取相同数据

**修复方案**：

```tsx
// 使用 React Query 的 suspense 模式
const { data: video } = useQuery({
  queryKey: ['video', id],
  queryFn: () => videoService.getVideo(Number(id)),
  suspense: true,  // 启用 suspense
})
```

---

## 风险和注意事项

1. **向后兼容性**：确保优化不破坏现有功能
2. **浏览器支持**：测试主流浏览器兼容性
3. **移动端适配**：特别关注触摸交互
4. **SEO 影响**：确保 CSR 不影响搜索引擎抓取
5. **CDN 配置**：优化静态资源分发
6. **🔴 安全第一**：必须先修复所有安全问题再进行其他优化

### To-dos

- [ ] 修复 StatsPanel 和 ContextMenu 的接口不匹配问题
- [ ] 增强进度条交互：时间气泡、悬停加粗、章节支持
- [ ] 创建 SeekFeedback 组件实现双击视觉反馈
- [ ] 创建 VolumeIndicator 组件显示音量调整反馈
- [ ] 完善快捷键系统：添加 j/l/t/i/,/./</> 等键
- [ ] 创建 KeyboardShortcuts 帮助面板组件（? 键触发）
- [ ] 优化控制栏布局，精确匹配 YouTube 规格
- [ ] 添加缓冲和加载状态的视觉反馈
- [ ] 改进设置菜单（画质选择器）的交互和样式
- [ ] 添加非1x速度时的速度显示提示
- [ ] 优化全屏体验和状态恢复
- [ ] 精确匹配 YouTube 的颜色、动画和过渡效果
- [ ] 性能优化：useCallback/useMemo/防抖节流
- [ ] 全面功能测试和跨浏览器验证