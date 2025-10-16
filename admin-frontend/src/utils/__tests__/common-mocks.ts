/**
 * Common Mocks
 * 通用的 Mock 配置
 *
 * 集中管理常用的 mock 配置，避免重复代码
 */

import { vi } from 'vitest'

/**
 * Mock axios 实例
 * 用于所有 API 测试
 */
export const createAxiosMock = () => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  patch: vi.fn(),
  delete: vi.fn(),
  request: vi.fn(),
  head: vi.fn(),
  options: vi.fn(),
  defaults: {
    headers: {
      common: {},
    },
  },
  interceptors: {
    request: {
      use: vi.fn(),
      eject: vi.fn(),
    },
    response: {
      use: vi.fn(),
      eject: vi.fn(),
    },
  },
})

/**
 * Mock React Router 的 useNavigate
 */
export const createNavigateMock = () => {
  const navigate = vi.fn()
  return { navigate, useNavigate: () => navigate }
}

/**
 * Mock React Router 的 useParams
 */
export const createParamsMock = (params: Record<string, string> = {}) => {
  return { useParams: () => params }
}

/**
 * Mock React Router 的 useLocation
 */
export const createLocationMock = (pathname: string = '/', search: string = '') => {
  return {
    useLocation: () => ({
      pathname,
      search,
      hash: '',
      state: null,
      key: 'default',
    }),
  }
}

/**
 * Mock i18next
 */
export const createI18nMock = (translations: Record<string, string> = {}) => {
  return {
    useTranslation: () => ({
      t: (key: string) => translations[key] || key,
      i18n: {
        language: 'en',
        changeLanguage: vi.fn(),
        languages: ['en', 'zh'],
      },
    }),
    initReactI18next: {
      type: '3rdParty',
      init: vi.fn(),
    },
  }
}

/**
 * Mock Theme Context
 */
export const createThemeMock = (theme: 'light' | 'dark' = 'light') => {
  return {
    useTheme: () => ({
      theme,
      toggleTheme: vi.fn(),
      setTheme: vi.fn(),
    }),
  }
}

/**
 * Mock Auth Context
 */
export const createAuthMock = (isAuthenticated: boolean = true, user: any = null) => {
  return {
    useAuth: () => ({
      isAuthenticated,
      user,
      login: vi.fn(),
      logout: vi.fn(),
      updateUser: vi.fn(),
    }),
  }
}

/**
 * Mock Ant Design message
 */
export const createAntdMessageMock = () => ({
  success: vi.fn(),
  error: vi.fn(),
  info: vi.fn(),
  warning: vi.fn(),
  loading: vi.fn((content: string) => {
    const hide = vi.fn()
    return hide
  }),
  open: vi.fn(),
  destroy: vi.fn(),
  config: vi.fn(),
})

/**
 * Mock Ant Design modal
 */
export const createAntdModalMock = () => ({
  info: vi.fn(),
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn(),
  confirm: vi.fn((config) => {
    // 自动调用 onOk
    if (config.onOk) {
      config.onOk()
    }
    return {
      destroy: vi.fn(),
      update: vi.fn(),
    }
  }),
  destroyAll: vi.fn(),
})

/**
 * Mock Ant Design notification
 */
export const createAntdNotificationMock = () => ({
  open: vi.fn(),
  info: vi.fn(),
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn(),
  destroy: vi.fn(),
  config: vi.fn(),
})

/**
 * Mock TanStack Query Client
 */
export const createQueryClientMock = () => ({
  getQueryData: vi.fn(),
  setQueryData: vi.fn(),
  invalidateQueries: vi.fn(),
  refetchQueries: vi.fn(),
  cancelQueries: vi.fn(),
  removeQueries: vi.fn(),
  clear: vi.fn(),
  getQueryCache: vi.fn(() => ({
    find: vi.fn(),
    findAll: vi.fn(),
  })),
  getMutationCache: vi.fn(() => ({
    find: vi.fn(),
    findAll: vi.fn(),
  })),
})

/**
 * Mock @ant-design/charts 图表组件
 */
export const createChartsMock = () => ({
  Line: ({ data }: any) => (
    <div data-testid="line-chart">{JSON.stringify(data)}</div>
  ),
  Column: ({ data }: any) => (
    <div data-testid="column-chart">{JSON.stringify(data)}</div>
  ),
  Pie: ({ data }: any) => (
    <div data-testid="pie-chart">{JSON.stringify(data)}</div>
  ),
  Bar: ({ data }: any) => (
    <div data-testid="bar-chart">{JSON.stringify(data)}</div>
  ),
  Area: ({ data }: any) => (
    <div data-testid="area-chart">{JSON.stringify(data)}</div>
  ),
  Radar: ({ data }: any) => (
    <div data-testid="radar-chart">{JSON.stringify(data)}</div>
  ),
  DualAxes: ({ data }: any) => (
    <div data-testid="dual-axes-chart">{JSON.stringify(data)}</div>
  ),
})

/**
 * Mock AWS Color Helpers
 */
export const createAwsColorHelpersMock = () => ({
  getTagStyle: vi.fn(() => ({ color: '#000' })),
  getTextColor: vi.fn(() => '#000'),
  getColor: vi.fn(() => '#0073bb'),
  getBackgroundColor: vi.fn(() => '#ffffff'),
})

/**
 * Mock File Reader
 */
export const createFileReaderMock = () => {
  const fileReader = {
    readAsDataURL: vi.fn(function (this: any) {
      this.onload?.({ target: { result: 'data:image/png;base64,mock' } })
    }),
    readAsText: vi.fn(function (this: any) {
      this.onload?.({ target: { result: 'mock text content' } })
    }),
    readAsArrayBuffer: vi.fn(function (this: any) {
      this.onload?.({ target: { result: new ArrayBuffer(8) } })
    }),
    abort: vi.fn(),
    onload: null as any,
    onerror: null as any,
    onprogress: null as any,
    result: null as any,
    error: null as any,
    readyState: 0,
  }

  global.FileReader = vi.fn(() => fileReader) as any

  return fileReader
}

/**
 * Mock Blob
 */
export const createBlobMock = () => {
  global.URL.createObjectURL = vi.fn(() => 'blob:mock-url')
  global.URL.revokeObjectURL = vi.fn()
}

/**
 * Mock IntersectionObserver
 */
export const createIntersectionObserverMock = () => {
  global.IntersectionObserver = vi.fn(function (callback: any) {
    return {
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
      takeRecords: vi.fn(() => []),
    }
  }) as any
}

/**
 * Mock ResizeObserver
 */
export const createResizeObserverMock = () => {
  global.ResizeObserver = vi.fn(function (callback: any) {
    return {
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }
  }) as any
}

/**
 * Mock clipboard API
 */
export const createClipboardMock = () => {
  const clipboard = {
    writeText: vi.fn(() => Promise.resolve()),
    readText: vi.fn(() => Promise.resolve('mock text')),
    write: vi.fn(() => Promise.resolve()),
    read: vi.fn(() => Promise.resolve([])),
  }

  Object.defineProperty(navigator, 'clipboard', {
    value: clipboard,
    writable: true,
  })

  return clipboard
}

/**
 * 预设的常用 mock 配置组合
 */
export const commonMocks = {
  antd: () => ({
    message: createAntdMessageMock(),
    Modal: createAntdModalMock(),
    notification: createAntdNotificationMock(),
  }),
  router: () => ({
    ...createNavigateMock(),
    ...createParamsMock(),
    ...createLocationMock(),
  }),
  i18n: (translations?: Record<string, string>) => createI18nMock(translations),
  theme: (theme?: 'light' | 'dark') => createThemeMock(theme),
  auth: (isAuthenticated?: boolean, user?: any) => createAuthMock(isAuthenticated, user),
  charts: () => createChartsMock(),
  browser: () => {
    createBlobMock()
    createIntersectionObserverMock()
    createResizeObserverMock()
    createClipboardMock()
  },
}

/**
 * 快速设置所有常用 mock
 */
export const setupCommonMocks = () => {
  commonMocks.browser()
  return {
    antd: commonMocks.antd(),
    router: commonMocks.router(),
    i18n: commonMocks.i18n(),
    theme: commonMocks.theme(),
    charts: commonMocks.charts(),
  }
}
