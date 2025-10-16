/**
 * Unified API Error Handler
 * Provides consistent error handling across the application
 */

import { captureException, addBreadcrumb } from './sentry'

interface ApiError {
  response?: {
    status: number
    data?: {
      detail?: string
      message?: string
    }
  }
  request?: any
  message?: string
}

/**
 * Log error to monitoring service
 */
const logErrorToService = (error: any) => {
  // Log to Sentry
  captureException(error, {
    api: {
      url: window.location.href,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      status: error.response?.status,
      statusText: error.response?.statusText,
    },
  })

  // Also log to console in production
  if (process.env.NODE_ENV === 'production') {
    console.error('[Error Logged]:', {
      message: error.message,
      stack: error.stack,
      url: window.location.href,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
    })
  }
}

/**
 * Handle API errors with user-friendly messages
 */
export const handleApiError = (error: ApiError): string => {
  let errorMessage = '发生错误，请稍后重试'

  // Add breadcrumb for debugging
  addBreadcrumb({
    message: 'API Error occurred',
    category: 'api',
    level: 'error',
    data: {
      status: error.response?.status,
      url: error.request?.url,
    },
  })

  if (error.response) {
    // Server responded with error status
    const status = error.response.status
    const message = error.response.data?.detail || error.response.data?.message

    switch (status) {
      case 400:
        errorMessage = `请求错误: ${message || '无效的请求参数'}`
        break
      case 401:
        errorMessage = '未授权，请重新登录'
        break
      case 403:
        errorMessage = '权限不足，无法访问此资源'
        break
      case 404:
        errorMessage = '资源不存在'
        break
      case 422:
        errorMessage = `数据验证失败: ${message || '请检查输入'}`
        break
      case 429:
        errorMessage = '请求过于频繁，请稍后再试'
        break
      case 500:
        errorMessage = '服务器错误，请稍后重试'
        break
      case 502:
      case 503:
      case 504:
        errorMessage = '服务暂时不可用，请稍后重试'
        break
      default:
        errorMessage = message || `错误 ${status}: 请求失败`
    }
  } else if (error.request) {
    // Request made but no response received
    errorMessage = '网络错误，请检查您的网络连接'
  } else {
    // Something else happened
    errorMessage = error.message || '发生未知错误'
  }

  // Log error in production
  if (process.env.NODE_ENV === 'production') {
    logErrorToService(error)
  } else {
    console.error('API Error:', error)
  }

  return errorMessage
}

/**
 * Display error notification using toast
 */
export const showErrorNotification = (message: string) => {
  // Dynamically import toast to avoid SSR issues
  import('react-hot-toast').then(({ default: toast }) => {
    toast.error(message, {
      duration: 4000,
      position: 'top-right',
      style: {
        background: '#1f2937',
        color: '#fff',
      },
    })
  })
  
  // Also log in development
  if (process.env.NODE_ENV === 'development') {
    console.error('Error:', message)
  }
}

/**
 * Display success notification using toast
 */
export const showSuccessNotification = (message: string) => {
  import('react-hot-toast').then(({ default: toast }) => {
    toast.success(message, {
      duration: 3000,
      position: 'top-right',
      style: {
        background: '#1f2937',
        color: '#fff',
      },
    })
  })
}

/**
 * Display info notification using toast
 */
export const showInfoNotification = (message: string) => {
  import('react-hot-toast').then(({ default: toast }) => {
    toast(message, {
      duration: 3000,
      position: 'top-right',
      icon: 'ℹ️',
      style: {
        background: '#1f2937',
        color: '#fff',
      },
    })
  })
}

/**
 * Retry logic for failed requests
 */
export const shouldRetry = (error: ApiError, attemptNumber: number): boolean => {
  // Don't retry on auth errors
  if (error.response?.status && [401, 403].includes(error.response.status)) {
    return false
  }

  // Don't retry on client errors (4xx)
  if (error.response?.status && error.response.status >= 400 && error.response.status < 500) {
    return false
  }

  // Retry up to 2 times for server errors (5xx) and network errors
  return attemptNumber < 2
}

export default {
  handleApiError,
  showErrorNotification,
  showSuccessNotification,
  showInfoNotification,
  shouldRetry,
  logErrorToService,
}

