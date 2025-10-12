import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Form, Input, Button, Card, message, Space, Switch, Checkbox, Divider, Modal, Steps, Progress } from 'antd'
import { UserOutlined, LockOutlined, SafetyOutlined, ReloadOutlined, SunOutlined, MoonOutlined, VideoCameraOutlined, MailOutlined, ClockCircleOutlined, CheckCircleOutlined } from '@ant-design/icons'
import axios from 'axios'  // Use native axios for login, not the intercepted instance
import { useTheme } from '../contexts/ThemeContext'
import './Login.css'

const Login = () => {
  const navigate = useNavigate()
  const { theme, toggleTheme } = useTheme()
  const [loading, setLoading] = useState(false)
  const [captchaId, setCaptchaId] = useState('')
  const [captchaUrl, setCaptchaUrl] = useState('')
  const [captchaLoading, setCaptchaLoading] = useState(false)
  const [rememberMe, setRememberMe] = useState(false)
  const [forgotPasswordVisible, setForgotPasswordVisible] = useState(false)
  const [resetStep, setResetStep] = useState(1) // 1: 输入邮箱, 2: 输入验证码和新密码
  const [resetEmail, setResetEmail] = useState('')
  const [resetLoading, setResetLoading] = useState(false)
  const [countdown, setCountdown] = useState(0) // 重新发送验证码倒计时
  const [passwordStrength, setPasswordStrength] = useState(0) // 密码强度 0-100
  const [form] = Form.useForm()
  const [resetForm] = Form.useForm()
  const emailInputRef = useRef<any>(null)
  const codeInputRef = useRef<any>(null)

  // Load captcha and saved username on component mount
  useEffect(() => {
    loadCaptcha()
    // Load saved username
    const savedUsername = localStorage.getItem('admin_saved_username')
    if (savedUsername) {
      form.setFieldsValue({ username: savedUsername })
      setRememberMe(true)
    }
  }, [])

  // Countdown timer for resend verification code
  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000)
      return () => clearTimeout(timer)
    }
    return undefined
  }, [countdown])

  // Auto focus on input when modal opens or step changes
  useEffect(() => {
    if (forgotPasswordVisible) {
      setTimeout(() => {
        if (resetStep === 1 && emailInputRef.current) {
          emailInputRef.current.focus()
        } else if (resetStep === 2 && codeInputRef.current) {
          codeInputRef.current.focus()
        }
      }, 100)
    }
  }, [forgotPasswordVisible, resetStep])

  // Calculate password strength
  const calculatePasswordStrength = (password: string): number => {
    if (!password) return 0

    let strength = 0
    // Length
    if (password.length >= 8) strength += 25
    if (password.length >= 12) strength += 15

    // Contains lowercase
    if (/[a-z]/.test(password)) strength += 15
    // Contains uppercase
    if (/[A-Z]/.test(password)) strength += 15
    // Contains numbers
    if (/[0-9]/.test(password)) strength += 15
    // Contains special characters
    if (/[^a-zA-Z0-9]/.test(password)) strength += 15

    return Math.min(100, strength)
  }

  // Handle password change for strength indicator
  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const password = e.target.value
    setPasswordStrength(calculatePasswordStrength(password))
  }

  const loadCaptcha = async () => {
    setCaptchaLoading(true)
    try {
      const response = await axios.get('/api/v1/captcha/', {
        responseType: 'blob',
        timeout: 10000, // 10 second timeout
      })

      // Get captcha ID from response headers
      const id = response.headers['x-captcha-id']
      setCaptchaId(id)

      // Create object URL for the image
      const imageUrl = URL.createObjectURL(response.data)
      setCaptchaUrl(imageUrl)
    } catch (error: any) {
      const errorMsg = error.code === 'ECONNABORTED'
        ? '验证码加载超时，请重试'
        : '验证码加载失败，请刷新重试'
      message.error({
        content: errorMsg,
        duration: 3,
      })
      console.error('Captcha load error:', error)
    } finally {
      setCaptchaLoading(false)
    }
  }

  // Handle forgot password - Step 1: Send verification email
  const handleSendResetEmail = async (values: { email: string }) => {
    setResetLoading(true)
    try {
      await axios.post('/api/v1/auth/admin/password-reset/request', { email: values.email })

      setResetEmail(values.email)
      setResetStep(2)
      setCountdown(60) // Start 60 second countdown
      message.success({
        content: '验证码已发送到您的邮箱，请查收',
        duration: 3,
      })
    } catch (error: any) {
      let errorMsg = '发送失败，请检查邮箱地址'
      if (error.response?.status === 503) {
        errorMsg = '邮件服务未配置，请联系管理员'
      } else if (error.response?.status === 500) {
        errorMsg = '邮件发送失败，请稍后重试'
      } else if (error.response?.data?.detail) {
        errorMsg = error.response.data.detail
      }

      message.error({
        content: errorMsg,
        duration: 4,
      })
    } finally {
      setResetLoading(false)
    }
  }

  // Resend verification code
  const handleResendCode = async () => {
    if (countdown > 0) return

    setResetLoading(true)
    try {
      await axios.post('/api/v1/auth/admin/password-reset/request', { email: resetEmail })

      setCountdown(60)
      message.success({
        content: '验证码已重新发送',
        duration: 2,
      })
    } catch (error: any) {
      message.error({
        content: '发送失败，请稍后重试',
        duration: 3,
      })
    } finally {
      setResetLoading(false)
    }
  }

  // Handle forgot password - Step 2: Reset password with verification code
  const handleResetPassword = async (values: { code: string; new_password: string; confirm_password: string }) => {
    if (values.new_password !== values.confirm_password) {
      message.error('两次输入的密码不一致')
      return
    }

    setResetLoading(true)
    try {
      await axios.post('/api/v1/auth/admin/password-reset/confirm', {
        email: resetEmail,
        code: values.code,
        new_password: values.new_password,
      })

      message.success({
        content: '密码重置成功！请使用新密码登录',
        duration: 3,
      })

      // Close modal and reset state
      setForgotPasswordVisible(false)
      setResetStep(1)
      setResetEmail('')
      resetForm.resetFields()
    } catch (error: any) {
      let errorMsg = '重置失败，请检查验证码是否正确'
      if (error.response?.status === 400) {
        errorMsg = '验证码错误或已过期'
      } else if (error.response?.status === 404) {
        errorMsg = '用户不存在'
      } else if (error.response?.status === 403) {
        errorMsg = '账户已被禁用'
      } else if (error.response?.data?.detail) {
        errorMsg = error.response.data.detail
      }

      message.error({
        content: errorMsg,
        duration: 4,
      })
    } finally {
      setResetLoading(false)
    }
  }

  // Handle modal cancel
  const handleResetCancel = () => {
    setForgotPasswordVisible(false)
    setResetStep(1)
    setResetEmail('')
    setCountdown(0)
    setPasswordStrength(0)
    resetForm.resetFields()
  }

  const onFinish = async (values: any) => {
    setLoading(true)
    try {
      const response = await axios.post('/api/v1/auth/admin/login', {
        ...values,
        captcha_id: captchaId,
      })

      // Save tokens to localStorage
      localStorage.setItem('admin_access_token', response.data.access_token)
      localStorage.setItem('admin_refresh_token', response.data.refresh_token)

      // Save username if remember me is checked
      if (rememberMe) {
        localStorage.setItem('admin_saved_username', values.username)
      } else {
        localStorage.removeItem('admin_saved_username')
      }

      message.success({
        content: '登录成功！正在跳转...',
        duration: 2,
      })

      // Use navigate instead of window.location.href to avoid page reload
      // This ensures localStorage is properly set before navigation
      setTimeout(() => {
        navigate('/')
      }, 300)
    } catch (error: any) {
      // Determine error message
      let errorMsg = '登录失败，请检查用户名和密码'
      if (error.response?.status === 401) {
        errorMsg = '用户名或密码错误'
      } else if (error.response?.status === 400) {
        errorMsg = error.response?.data?.detail || '验证码错误或已过期'
      } else if (error.response?.status === 429) {
        errorMsg = '登录尝试过多，请稍后再试'
      } else if (error.code === 'ECONNABORTED' || error.code === 'ERR_NETWORK') {
        errorMsg = '网络连接失败，请检查网络'
      }

      message.error({
        content: errorMsg,
        duration: 4,
      })

      // Reload captcha on error
      loadCaptcha()
      // Clear captcha field
      form.setFieldsValue({ captcha_code: '' })

      console.error('Login error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={`login-container ${theme}`}>
      {/* Theme toggle button */}
      <div className="theme-toggle">
        <Switch
          checked={theme === 'dark'}
          onChange={toggleTheme}
          checkedChildren={<MoonOutlined />}
          unCheckedChildren={<SunOutlined />}
        />
      </div>

      <Card className="login-card">
        {/* Logo and Title */}
        <div className="login-header">
          <div className="logo-container">
            <VideoCameraOutlined className="logo-icon" />
          </div>
          <h1 className="login-title">视频管理后台</h1>
          <p className="login-subtitle">Video Site Admin Panel</p>
        </div>

        <Form
          form={form}
          name="login"
          onFinish={onFinish}
          autoComplete="off"
          className="login-form"
          layout="vertical"
        >
          <Form.Item
            name="username"
            label="用户名"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="请输入用户名"
              autoComplete="username"
            />
          </Form.Item>

          <Form.Item
            name="password"
            label="密码"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="请输入密码"
              autoComplete="current-password"
            />
          </Form.Item>

          <Form.Item
            name="captcha_code"
            label="验证码"
            rules={[
              { required: true, message: '请输入验证码' },
              { len: 4, message: '验证码为4位字符' }
            ]}
          >
            <Space.Compact style={{ width: '100%' }}>
              <Input
                prefix={<SafetyOutlined />}
                placeholder="请输入4位验证码"
                maxLength={4}
                style={{ width: '60%' }}
                autoComplete="off"
              />
              <div
                className="captcha-image-container"
                onClick={loadCaptcha}
                title="点击刷新验证码"
              >
                {captchaLoading ? (
                  <ReloadOutlined spin style={{ fontSize: 18, color: '#0073bb' }} />
                ) : captchaUrl ? (
                  <img
                    src={captchaUrl}
                    alt="验证码"
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                ) : (
                  <span style={{ color: '#879596', fontSize: 12 }}>加载中...</span>
                )}
              </div>
            </Space.Compact>
          </Form.Item>

          <Form.Item className="remember-me-item">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Checkbox
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
              >
                记住用户名
              </Checkbox>
              <a
                className="forgot-password-link"
                onClick={() => setForgotPasswordVisible(true)}
              >
                忘记密码？
              </a>
            </div>
          </Form.Item>

          <Form.Item style={{ marginBottom: 0 }}>
            <Button
              type="primary"
              htmlType="submit"
              block
              loading={loading}
              className="login-button"
            >
              {loading ? '登录中...' : '登录'}
            </Button>
          </Form.Item>
        </Form>

        <Divider className="login-divider" />

        {/* Default account info */}
        <div className="account-info">
          <div className="account-info-title">测试账号</div>
          <div className="account-info-item">
            <span className="account-label">管理员</span>
            <span className="account-value">admin / admin123456</span>
          </div>
          <div className="account-info-item">
            <span className="account-label">编辑员</span>
            <span className="account-value">editor / editor123456</span>
          </div>
        </div>

        {/* Footer */}
        <div className="login-footer">
          <p>© 2025 Video Site. All rights reserved.</p>
        </div>
      </Card>

      {/* Forgot Password Modal */}
      <Modal
        title={
          <div className="reset-modal-header">
            <span className="reset-modal-title">密码重置</span>
            <Steps
              current={resetStep - 1}
              size="small"
              className="reset-steps"
              items={[
                { title: '验证邮箱', icon: <MailOutlined /> },
                { title: '重置密码', icon: <LockOutlined /> },
              ]}
            />
          </div>
        }
        open={forgotPasswordVisible}
        onCancel={handleResetCancel}
        footer={null}
        className="forgot-password-modal"
        width={520}
        centered
        destroyOnClose
      >
        {resetStep === 1 ? (
          // Step 1: Enter email
          <Form
            form={resetForm}
            layout="vertical"
            onFinish={handleSendResetEmail}
          >
            <div className="reset-step-description">
              <MailOutlined className="desc-icon" />
              <span>请输入您注册时使用的邮箱地址，我们将向您发送6位数字验证码</span>
            </div>

            <Form.Item
              name="email"
              label="邮箱地址"
              rules={[
                { required: true, message: '请输入邮箱地址' },
                { type: 'email', message: '请输入有效的邮箱地址' }
              ]}
            >
              <Input
                ref={emailInputRef}
                prefix={<MailOutlined />}
                placeholder="admin@example.com"
                size="large"
                autoFocus
              />
            </Form.Item>

            <Form.Item style={{ marginBottom: 0 }}>
              <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
                <Button onClick={handleResetCancel} size="large">
                  取消
                </Button>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={resetLoading}
                  className="reset-button"
                  size="large"
                  icon={!resetLoading && <MailOutlined />}
                >
                  {resetLoading ? '发送中...' : '发送验证码'}
                </Button>
              </Space>
            </Form.Item>
          </Form>
        ) : (
          // Step 2: Enter verification code and new password
          <Form
            form={resetForm}
            layout="vertical"
            onFinish={handleResetPassword}
          >
            <div className="reset-step-description">
              <CheckCircleOutlined className="desc-icon success" />
              <span>
                验证码已发送到 <strong>{resetEmail}</strong>
                <br />
                <small>有效期15分钟，请及时查收邮件</small>
              </span>
            </div>

            <Form.Item
              name="code"
              label={
                <span>
                  验证码
                  {countdown > 0 && (
                    <span className="countdown-text">
                      <ClockCircleOutlined /> {countdown}秒后可重新发送
                    </span>
                  )}
                </span>
              }
              rules={[
                { required: true, message: '请输入验证码' },
                { len: 6, message: '验证码为6位数字' },
                { pattern: /^\d{6}$/, message: '验证码必须是6位数字' }
              ]}
            >
              <Space.Compact style={{ width: '100%' }}>
                <Input
                  ref={codeInputRef}
                  prefix={<SafetyOutlined />}
                  placeholder="请输入6位验证码"
                  maxLength={6}
                  size="large"
                  style={{ width: '70%' }}
                  autoFocus
                />
                <Button
                  size="large"
                  onClick={handleResendCode}
                  disabled={countdown > 0}
                  loading={resetLoading}
                  style={{ width: '30%' }}
                >
                  {countdown > 0 ? `${countdown}秒` : '重新发送'}
                </Button>
              </Space.Compact>
            </Form.Item>

            <Form.Item
              name="new_password"
              label="新密码"
              rules={[
                { required: true, message: '请输入新密码' },
                { min: 8, message: '密码长度至少8位' }
              ]}
            >
              <div>
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="请输入新密码（至少8位）"
                  size="large"
                  onChange={handlePasswordChange}
                />
                {passwordStrength > 0 && (
                  <div className="password-strength">
                    <Progress
                      percent={passwordStrength}
                      size="small"
                      strokeColor={
                        passwordStrength < 40
                          ? '#d13212'
                          : passwordStrength < 70
                          ? '#ff9900'
                          : '#1d8102'
                      }
                      showInfo={false}
                    />
                    <span className={`strength-text strength-${
                      passwordStrength < 40 ? 'weak' : passwordStrength < 70 ? 'medium' : 'strong'
                    }`}>
                      {passwordStrength < 40 ? '弱' : passwordStrength < 70 ? '中等' : '强'}
                    </span>
                  </div>
                )}
              </div>
            </Form.Item>

            <Form.Item
              name="confirm_password"
              label="确认密码"
              rules={[
                { required: true, message: '请确认新密码' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('new_password') === value) {
                      return Promise.resolve()
                    }
                    return Promise.reject(new Error('两次输入的密码不一致'))
                  },
                }),
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="请再次输入新密码"
                size="large"
              />
            </Form.Item>

            <Form.Item style={{ marginBottom: 0 }}>
              <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                <Button onClick={() => { setResetStep(1); setPasswordStrength(0) }} size="large">
                  返回上一步
                </Button>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={resetLoading}
                  className="reset-button"
                  size="large"
                  icon={!resetLoading && <CheckCircleOutlined />}
                >
                  {resetLoading ? '重置中...' : '确认重置'}
                </Button>
              </Space>
            </Form.Item>
          </Form>
        )}
      </Modal>
    </div>
  )
}

export default Login
