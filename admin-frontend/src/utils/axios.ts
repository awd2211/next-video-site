import axios from 'axios'
import { message } from 'antd'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// Configure NProgress
NProgress.configure({ showSpinner: false, trickleSpeed: 200 })

// Create axios instance with default config
const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',  // Use relative path to leverage Vite proxy
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  // ✅ 修复：配置params序列化，支持FastAPI的数组格式
  paramsSerializer: {
    serialize: (params) => {
      const searchParams = new URLSearchParams()
      Object.entries(params).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          // 数组参数：使用重复的参数名（FastAPI标准）
          // 例如：media_ids=1&media_ids=2&media_ids=3
          value.forEach(item => searchParams.append(key, String(item)))
        } else if (value !== null && value !== undefined) {
          // 普通参数
          searchParams.append(key, String(value))
        }
      })
      return searchParams.toString()
    }
  }
})

// Request interceptor - Add token to all requests
axiosInstance.interceptors.request.use(
  (config) => {
    // Start progress bar
    NProgress.start()
    
    const token = localStorage.getItem('admin_access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Add language header for multilingual support
    const language = localStorage.getItem('language') || navigator.language || 'zh-CN'
    config.headers['X-Language'] = language
    config.headers['Accept-Language'] = language
    
    return config
  },
  (error) => {
    NProgress.done()
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors globally
axiosInstance.interceptors.response.use(
  (response) => {
    // Complete progress bar
    NProgress.done()
    return response
  },
  async (error) => {
    // Complete progress bar on error
    NProgress.done()
    const originalRequest = error.config

    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      // Clear token and redirect to login
      localStorage.removeItem('admin_access_token')
      localStorage.removeItem('admin_user')

      message.error('登录已过期，请重新登录')

      // Redirect to login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }

      return Promise.reject(error)
    }

    // Handle 403 Forbidden
    if (error.response?.status === 403) {
      message.error('没有权限访问此资源')
      return Promise.reject(error)
    }

    // Handle 404 Not Found
    if (error.response?.status === 404) {
      message.error('请求的资源不存在')
      return Promise.reject(error)
    }

    // Handle 422 Validation Error
    if (error.response?.status === 422) {
      const detail = error.response?.data?.detail
      if (Array.isArray(detail)) {
        const errors = detail.map((err: any) => err.msg).join(', ')
        message.error(`验证错误: ${errors}`)
      } else {
        message.error(detail || '数据验证失败')
      }
      return Promise.reject(error)
    }

    // Handle 500 Server Error
    if (error.response?.status === 500) {
      message.error('服务器错误，请稍后重试')
      return Promise.reject(error)
    }

    // Handle network errors
    if (!error.response) {
      message.error('网络错误，请检查您的网络连接')
      return Promise.reject(error)
    }

    // Handle other errors
    const errorMessage = error.response?.data?.detail || error.message || '请求失败'
    message.error(errorMessage)

    return Promise.reject(error)
  }
)

export default axiosInstance
