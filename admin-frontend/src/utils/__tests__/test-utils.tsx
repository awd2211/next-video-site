/**
 * Test Utilities
 * 可复用的测试工具函数
 *
 * 为管理后台测试提供通用的辅助函数和 React 包装器
 */

import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { vi } from 'vitest'

/**
 * 创建测试用的 QueryClient
 * 禁用重试和缓存以提高测试速度
 */
export const createTestQueryClient = () => {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
        staleTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
    logger: {
      log: vi.fn(),
      warn: vi.fn(),
      error: vi.fn(),
    },
  })
}

/**
 * 所有 Provider 的包装器
 * 包含 QueryClient 和 Router
 */
interface AllProvidersProps {
  children: React.ReactNode
  queryClient?: QueryClient
}

export const AllProviders = ({ children, queryClient }: AllProvidersProps) => {
  const client = queryClient || createTestQueryClient()

  return (
    <BrowserRouter>
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    </BrowserRouter>
  )
}

/**
 * 自定义 render 函数，自动包含所有必要的 Provider
 * 使用示例：
 *
 * const { getByText } = renderWithProviders(<MyComponent />)
 */
export const renderWithProviders = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'> & {
    queryClient?: QueryClient
  }
) => {
  const { queryClient, ...renderOptions } = options || {}

  return render(ui, {
    wrapper: ({ children }) => (
      <AllProviders queryClient={queryClient}>{children}</AllProviders>
    ),
    ...renderOptions,
  })
}

/**
 * 创建 Mock 响应数据
 * 用于模拟 API 响应
 */
export const createMockResponse = <T,>(data: T) => {
  return {
    data,
    status: 200,
    statusText: 'OK',
    headers: {},
    config: {} as any,
  }
}

/**
 * 创建 Mock 错误响应
 * 用于模拟 API 错误
 */
export const createMockError = (status: number, message: string) => {
  return {
    response: {
      status,
      data: { detail: message },
      statusText: 'Error',
      headers: {},
      config: {} as any,
    },
    message,
    isAxiosError: true,
  }
}

/**
 * 创建分页响应数据
 * 用于模拟分页 API
 */
export const createMockPaginatedResponse = <T,>(
  items: T[],
  page: number = 1,
  pageSize: number = 10,
  total?: number
) => {
  return {
    items,
    total: total !== undefined ? total : items.length,
    page,
    page_size: pageSize,
    total_pages: Math.ceil((total !== undefined ? total : items.length) / pageSize),
  }
}

/**
 * 等待 Query 完成
 * 用于异步测试
 */
export const waitForQueryToFinish = async (queryClient: QueryClient, queryKey: any[]) => {
  await queryClient.getQueryCache().find({ queryKey })?.promise
}

/**
 * Mock localStorage
 * 用于测试本地存储功能
 */
export const mockLocalStorage = () => {
  const storage: Record<string, string> = {}

  return {
    getItem: vi.fn((key: string) => storage[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      storage[key] = value
    }),
    removeItem: vi.fn((key: string) => {
      delete storage[key]
    }),
    clear: vi.fn(() => {
      Object.keys(storage).forEach((key) => delete storage[key])
    }),
    get length() {
      return Object.keys(storage).length
    },
    key: vi.fn((index: number) => Object.keys(storage)[index] || null),
  }
}

/**
 * Mock 文件对象
 * 用于测试文件上传
 */
export const createMockFile = (
  name: string,
  size: number,
  type: string,
  content: string = 'test content'
) => {
  const blob = new Blob([content], { type })
  const file = new File([blob], name, { type })
  Object.defineProperty(file, 'size', { value: size })
  return file
}

/**
 * 延迟执行
 * 用于测试异步操作
 */
export const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

/**
 * 等待下一个渲染周期
 * 用于等待 React 状态更新
 */
export const waitForNextUpdate = () => delay(0)

/**
 * Mock Ant Design message
 * 用于测试通知消息
 */
export const createMockMessage = () => ({
  success: vi.fn(),
  error: vi.fn(),
  info: vi.fn(),
  warning: vi.fn(),
  loading: vi.fn(),
  open: vi.fn(),
  destroy: vi.fn(),
  config: vi.fn(),
})

/**
 * Mock i18n 翻译函数
 * 用于测试国际化
 */
export const createMockTranslation = (translations: Record<string, string> = {}) => {
  return {
    t: (key: string, options?: any) => {
      if (translations[key]) {
        return translations[key]
      }
      // 如果有插值，返回 key + 选项
      if (options) {
        return `${key}:${JSON.stringify(options)}`
      }
      return key
    },
    i18n: {
      language: 'en',
      changeLanguage: vi.fn(),
    },
  }
}

/**
 * 创建 Mock 用户数据
 * 用于测试认证相关功能
 */
export const createMockUser = (overrides?: Partial<any>) => ({
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  full_name: 'Test User',
  is_active: true,
  is_admin: false,
  created_at: '2024-01-01T00:00:00Z',
  ...overrides,
})

/**
 * 创建 Mock 管理员数据
 * 用于测试管理员功能
 */
export const createMockAdmin = (overrides?: Partial<any>) => ({
  id: 1,
  username: 'admin',
  email: 'admin@example.com',
  full_name: 'Admin User',
  is_active: true,
  is_admin: true,
  is_superadmin: false,
  created_at: '2024-01-01T00:00:00Z',
  ...overrides,
})

/**
 * 创建 Mock 视频数据
 * 用于测试视频相关功能
 */
export const createMockVideo = (overrides?: Partial<any>) => ({
  id: 1,
  title: 'Test Video',
  description: 'Test Description',
  video_url: 'https://example.com/video.mp4',
  poster_url: 'https://example.com/poster.jpg',
  backdrop_url: 'https://example.com/backdrop.jpg',
  duration: 120,
  view_count: 1000,
  rating: 8.5,
  status: 'published',
  video_type: 'movie',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides,
})

/**
 * 断言工具：检查是否调用了正确的 API
 */
export const expectApiCall = (
  mockFn: any,
  method: 'get' | 'post' | 'put' | 'delete' | 'patch',
  url: string,
  data?: any
) => {
  if (data) {
    expect(mockFn[method]).toHaveBeenCalledWith(url, data)
  } else {
    expect(mockFn[method]).toHaveBeenCalledWith(url)
  }
}

/**
 * 断言工具：检查是否调用了包含特定数据的 API
 */
export const expectApiCallWith = (
  mockFn: any,
  method: 'get' | 'post' | 'put' | 'delete' | 'patch',
  url: string,
  matcher: any
) => {
  expect(mockFn[method]).toHaveBeenCalledWith(url, expect.objectContaining(matcher))
}

/**
 * 清空所有 mock
 * 用于测试清理
 */
export const clearAllMocks = () => {
  vi.clearAllMocks()
}

/**
 * 重置所有 mock
 * 用于测试隔离
 */
export const resetAllMocks = () => {
  vi.resetAllMocks()
}

// 导出所有工具
export * from '@testing-library/react'
export { vi } from 'vitest'
