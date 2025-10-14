import { useState, useMemo, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import api from '@/services/api'
import toast from 'react-hot-toast'
import OAuthButtons from '@/components/OAuthButtons'

// 密码强度计算函数
const calculatePasswordStrength = (password: string) => {
  let score = 0
  const checks = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /\d/.test(password),
    special: /[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/;'`~]/.test(password),
  }

  // 计算满足的条件数
  const passed = Object.values(checks).filter(Boolean).length
  score = (passed / 5) * 100

  return { score, checks, passed }
}

// 获取强度标签和颜色
const getStrengthInfo = (score: number) => {
  if (score < 40) return { label: '弱', color: 'bg-red-500', textColor: 'text-red-500' }
  if (score < 60) return { label: '中等', color: 'bg-yellow-500', textColor: 'text-yellow-500' }
  if (score < 80) return { label: '强', color: 'bg-blue-500', textColor: 'text-blue-500' }
  return { label: '非常强', color: 'bg-green-500', textColor: 'text-green-500' }
}

const Register = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPasswordRequirements, setShowPasswordRequirements] = useState(false)

  // 验证码状态
  const [captchaId, setCaptchaId] = useState('')
  const [captchaUrl, setCaptchaUrl] = useState('')
  const [captchaCode, setCaptchaCode] = useState('')

  // 计算密码强度
  const passwordStrength = useMemo(() => {
    if (!formData.password) return null
    return calculatePasswordStrength(formData.password)
  }, [formData.password])

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
    setError('')

    // 验证密码强度
    if (passwordStrength && passwordStrength.passed < 5) {
      setError('密码必须满足所有安全要求')
      setShowPasswordRequirements(true)
      return
    }

    if (formData.password !== formData.confirmPassword) {
      setError('两次输入的密码不一致')
      return
    }

    if (!captchaCode || captchaCode.length !== 4) {
      setError('请输入4位验证码')
      return
    }

    setLoading(true)

    try {
      await api.post('/auth/register', {
        email: formData.email,
        username: formData.username,
        password: formData.password,
        captcha_id: captchaId,
        captcha_code: captchaCode,
      })
      toast.success('注册成功！请登录')
      navigate('/login')
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || '注册失败'
      setError(errorMsg)
      toast.error(errorMsg)
      // 验证码错误时刷新验证码
      if (errorMsg.includes('验证码')) {
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
        <h1 className="text-3xl font-bold text-center mb-8">注册 VideoSite</h1>

        {error && (
          <div className="bg-red-500 bg-opacity-10 border border-red-500 text-red-500 rounded p-3 mb-4">
            {error}
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
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full bg-gray-700 text-white rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-red-600"
            />
          </div>

          <div>
            <label htmlFor="username" className="block text-sm font-medium mb-2">
              用户名
            </label>
            <input
              id="username"
              type="text"
              required
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
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
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              onFocus={() => setShowPasswordRequirements(true)}
              className="w-full bg-gray-700 text-white rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-red-600"
            />

            {/* 密码强度指示器 */}
            {formData.password && passwordStrength && (
              <div className="mt-2">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-400">密码强度</span>
                  <span className={`text-xs font-medium ${getStrengthInfo(passwordStrength.score).textColor}`}>
                    {getStrengthInfo(passwordStrength.score).label}
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${getStrengthInfo(passwordStrength.score).color}`}
                    style={{ width: `${passwordStrength.score}%` }}
                  />
                </div>
              </div>
            )}

            {/* 密码要求列表 */}
            {showPasswordRequirements && (
              <div className="mt-3 p-3 bg-gray-700 rounded text-sm space-y-1">
                <div className="font-medium text-gray-300 mb-2">密码必须包含：</div>
                <div className={`flex items-center ${passwordStrength?.checks.length ? 'text-green-400' : 'text-gray-400'}`}>
                  <span className="mr-2">{passwordStrength?.checks.length ? '✓' : '○'}</span>
                  至少 8 个字符
                </div>
                <div className={`flex items-center ${passwordStrength?.checks.uppercase ? 'text-green-400' : 'text-gray-400'}`}>
                  <span className="mr-2">{passwordStrength?.checks.uppercase ? '✓' : '○'}</span>
                  至少 1 个大写字母 (A-Z)
                </div>
                <div className={`flex items-center ${passwordStrength?.checks.lowercase ? 'text-green-400' : 'text-gray-400'}`}>
                  <span className="mr-2">{passwordStrength?.checks.lowercase ? '✓' : '○'}</span>
                  至少 1 个小写字母 (a-z)
                </div>
                <div className={`flex items-center ${passwordStrength?.checks.number ? 'text-green-400' : 'text-gray-400'}`}>
                  <span className="mr-2">{passwordStrength?.checks.number ? '✓' : '○'}</span>
                  至少 1 个数字 (0-9)
                </div>
                <div className={`flex items-center ${passwordStrength?.checks.special ? 'text-green-400' : 'text-gray-400'}`}>
                  <span className="mr-2">{passwordStrength?.checks.special ? '✓' : '○'}</span>
                  至少 1 个特殊字符 (!@#$%^&* 等)
                </div>
              </div>
            )}
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium mb-2">
              确认密码
            </label>
            <input
              id="confirmPassword"
              type="password"
              required
              value={formData.confirmPassword}
              onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
              className="w-full bg-gray-700 text-white rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-red-600"
            />
            {formData.confirmPassword && formData.password !== formData.confirmPassword && (
              <p className="text-red-400 text-sm mt-1">两次输入的密码不一致</p>
            )}
            {formData.confirmPassword && formData.password === formData.confirmPassword && (
              <p className="text-green-400 text-sm mt-1">✓ 密码匹配</p>
            )}
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
            disabled={loading || (passwordStrength?.passed ?? 0) < 5}
            className="w-full btn-primary py-3 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? t('auth.registering', '注册中...') : t('auth.register', '注册')}
          </button>
        </form>

        {/* OAuth Buttons */}
        <OAuthButtons />

        <p className="text-center mt-6 text-gray-400">
          {t('auth.hasAccount', '已有账号？')}{' '}
          <Link to="/login" className="text-red-600 hover:text-red-500">
            {t('auth.loginNow', '立即登录')}
          </Link>
        </p>
      </div>
    </div>
  )
}

export default Register
