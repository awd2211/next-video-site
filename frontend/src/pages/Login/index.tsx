import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useTranslation } from 'react-i18next'
import api from '@/services/api'
import { useAuthStore } from '@/store/authStore'
import OAuthButtons from '@/components/OAuthButtons'

const Login = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  // 验证码状态
  const [captchaId, setCaptchaId] = useState('')
  const [captchaUrl, setCaptchaUrl] = useState('')
  const [captchaCode, setCaptchaCode] = useState('')

  // 加载验证码
  const loadCaptcha = async () => {
    try {
      const timestamp = new Date().getTime()
      const url = `/api/v1/captcha/?t=${timestamp}`
      const response = await fetch(url)
      const captchaId = response.headers.get('X-Captcha-ID')
      if (captchaId) {
        setCaptchaId(captchaId)
        setCaptchaUrl(url)
      }
    } catch (err) {
      console.error('Failed to load captcha:', err)
      toast.error('验证码加载失败')
    }
  }

  // 初始加载验证码
  useEffect(() => {
    loadCaptcha()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!captchaCode || captchaCode.length !== 4) {
      toast.error('请输入4位验证码')
      return
    }

    setLoading(true)

    try {
      const response = await api.post('/auth/login', {
        email,
        password,
        captcha_id: captchaId,
        captcha_code: captchaCode,
      })
      const { access_token, refresh_token, user } = response.data

      // Store tokens
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      // Update auth state
      setAuth(user, access_token)

      toast.success(`欢迎回来，${user.username || user.email}！`)

      // Navigate after a brief delay to show toast
      setTimeout(() => navigate('/'), 500)
    } catch (err: any) {
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
