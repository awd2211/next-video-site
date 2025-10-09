import axios from 'axios'
import { message } from 'antd'

// Create axios instance with default config
const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',  // Use relative path to leverage Vite proxy
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - Add token to all requests
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors globally
axiosInstance.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
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
