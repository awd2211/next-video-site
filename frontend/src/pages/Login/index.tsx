import { useState, useEffect, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useTranslation } from 'react-i18next'
import api from '@/services/api'
import { useAuthStore } from '@/store/authStore'
import OAuthButtons from '@/components/OAuthButtons'
import { checkLoginRateLimit, rateLimiter } from '@/utils/rateLimit'

const Login = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [rateLimitInfo, setRateLimitInfo] = useState<{ message: string; waitTime: number } | null>(null)

  // 验证码状态
  const [captchaId, setCaptchaId] = useState('')
  const [captchaUrl, setCaptchaUrl] = useState('')
  const [captchaCode, setCaptchaCode] = useState('')

  // 使用 ref 防止 StrictMode 导致的双重执行
  const isInitialMount = useRef(true)

  // 加载验证码
  const loadCaptcha = async () => {
    try {
      // Revoke old blob URL to free memory
      if (captchaUrl) {
        URL.revokeObjectURL(captchaUrl)
      }

      const timestamp = new Date().getTime()
      const response = await fetch(`/api/v1/captcha/?t=${timestamp}`)

      // Get captcha ID from response headers
      const captchaId = response.headers.get('X-Captcha-ID')
      if (captchaId) {
        setCaptchaId(captchaId)

        // Create blob URL from image data to prevent multiple requests
        const blob = await response.blob()
        const imageUrl = URL.createObjectURL(blob)
        setCaptchaUrl(imageUrl)
      }
    } catch (err) {
      console.error('Failed to load captcha:', err)
      toast.error('验证码加载失败')
    }
  }

  // 初始加载验证码
  useEffect(() => {
    // 防止 StrictMode 双重执行导致验证码ID不匹配
    if (isInitialMount.current) {
      isInitialMount.current = false
      loadCaptcha()
    }

    // Cleanup blob URL on unmount
    return () => {
      if (captchaUrl) {
        URL.revokeObjectURL(captchaUrl)
      }
    }
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // 检查速率限制
    const rateLimit = checkLoginRateLimit()
    if (!rateLimit.allowed) {
      setRateLimitInfo({ message: rateLimit.message, waitTime: rateLimit.waitTime })
      toast.error(rateLimit.message)
      return
    }

    if (!captchaCode || captchaCode.length !== 4) {
      toast.error('请输入4位验证码')
      return
    }

    setLoading(true)
    setRateLimitInfo(null)

    try {
      const response = await api.post('/auth/login', {
        email,
        password,
        captcha_id: captchaId,
        captcha_code: captchaCode,
      })

      console.log('登录响应:', response)
      const { access_token, refresh_token, user } = response.data

      // Store tokens
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      // Update auth state
      setAuth(user, access_token)

      // 登录成功，重置速率限制
      rateLimiter.reset('login')

      toast.success(`欢迎回来，${user.username || user.email}！`)

      // Navigate after a brief delay to show toast
      console.log('准备跳转到首页...')
      setTimeout(() => {
        console.log('执行跳转...')
        navigate('/')
      }, 500)
    } catch (err: any) {
      console.error('登录错误:', err)
      const errorMessage = err.response?.data?.detail || '登录失败，请检查邮箱和密码'
      toast.error(errorMessage)
      // 验证码错误时刷新验证码
      if (errorMessage.includes('验证码')) {
        setCaptchaCode('')
        loadCaptcha()
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-gray-800 rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-center mb-8">登录 VideoSite</h1>

        {/* 速率限制警告 */}
        {rateLimitInfo && (
          <div className="bg-yellow-500 bg-opacity-10 border border-yellow-500 text-yellow-500 rounded p-3 mb-4 text-sm">
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="font-medium">{rateLimitInfo.message}</p>
                <p className="text-xs mt-1">请等待 {rateLimitInfo.waitTime} 秒后重试</p>
              </div>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="email" className="block text-sm font-medium mb-2">
              邮箱
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-gray-700 text-white rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-red-600"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium mb-2">
              密码
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-gray-700 text-white rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-red-600"
            />
          </div>

          {/* 验证码 */}
          <div>
            <label htmlFor="captcha" className="block text-sm font-medium mb-2">
              验证码
            </label>
            <div className="flex gap-2">
              <input
                id="captcha"
                type="text"
                required
                maxLength={4}
                value={captchaCode}
                onChange={(e) => setCaptchaCode(e.target.value.toUpperCase())}
                placeholder="请输入验证码"
                className="flex-1 bg-gray-700 text-white rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-red-600"
              />
              <div className="relative">
                {captchaUrl ? (
                  <img
                    src={captchaUrl}
                    alt="验证码"
                    className="h-10 cursor-pointer rounded border border-gray-600 hover:border-gray-500"
                    onClick={loadCaptcha}
                    title="点击刷新"
                  />
                ) : (
                  <div className="h-10 w-32 bg-gray-700 rounded animate-pulse" />
                )}
              </div>
            </div>
            <p className="text-xs text-gray-400 mt-1">点击图片可刷新验证码</p>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary py-3 disabled:opacity-50"
          >
            {loading ? t('auth.loggingIn', '登录中...') : t('auth.login', '登录')}
          </button>
        </form>

        {/* OAuth Buttons */}
        <OAuthButtons />

        <p className="text-center mt-6 text-gray-400">
          {t('auth.noAccount', '还没有账号？')}{' '}
          <Link to="/register" className="text-red-600 hover:text-red-500">
            {t('auth.registerNow', '立即注册')}
          </Link>
        </p>
      </div>
    </div>
  )
}

export default Login
