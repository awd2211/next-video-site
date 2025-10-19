import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Form, Input, Button, Card, Space, Switch, Checkbox, Divider, Modal, Steps, Progress, App } from 'antd'
import { UserOutlined, LockOutlined, SafetyOutlined, ReloadOutlined, SunOutlined, MoonOutlined, VideoCameraOutlined, MailOutlined, ClockCircleOutlined, CheckCircleOutlined } from '@ant-design/icons'
import axios from 'axios'  // Use native axios for login, not the intercepted instance
import { useTheme } from '../contexts/ThemeContext'
import { useLanguage } from '../contexts/LanguageContext'
import { useTranslation } from 'react-i18next'
import { getColor, getTextColor } from '../utils/awsColorHelpers'
import './Login.css'

const Login = () => {
  const navigate = useNavigate()
  const { theme, toggleTheme } = useTheme()
  const { language } = useLanguage()
  const { t } = useTranslation()
  const { message } = App.useApp()
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

  // 2FA state
  const [requires2FA, setRequires2FA] = useState(false)
  const [loginCredentials, setLoginCredentials] = useState<any>(null)

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
        ? t('auth.captchaTimeout')
        : t('auth.captchaLoadFailed')
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
        content: t('auth.codeSentSuccess'),
        duration: 3,
      })
    } catch (error: any) {
      let errorMsg = t('auth.sendFailed')
      if (error.response?.status === 503) {
        errorMsg = t('auth.emailNotConfigured')
      } else if (error.response?.status === 500) {
        errorMsg = t('auth.emailSendFailed')
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
        content: t('auth.codeResent'),
        duration: 2,
      })
    } catch (error: any) {
      message.error({
        content: t('auth.resendFailed'),
        duration: 3,
      })
    } finally {
      setResetLoading(false)
    }
  }

  // Handle forgot password - Step 2: Reset password with verification code
  const handleResetPassword = async (values: { code: string; new_password: string; confirm_password: string }) => {
    if (values.new_password !== values.confirm_password) {
      message.error(t('auth.passwordMismatch'))
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
        content: t('auth.resetSuccess'),
        duration: 3,
      })

      // Close modal and reset state
      setForgotPasswordVisible(false)
      setResetStep(1)
      setResetEmail('')
      resetForm.resetFields()
    } catch (error: any) {
      let errorMsg = t('auth.resetFailed')
      if (error.response?.status === 400) {
        errorMsg = t('auth.codeInvalidOrExpired')
      } else if (error.response?.status === 404) {
        errorMsg = t('auth.userNotFound')
      } else if (error.response?.status === 403) {
        errorMsg = t('auth.accountDisabled')
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

      // Check if 2FA is required
      if (response.data.requires_2fa) {
        // Store credentials for 2FA verification
        setLoginCredentials(values)
        setRequires2FA(true)
        message.info({
          content: t('auth.enter2FACode'),
          duration: 3,
        })
        return
      }

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
        content: t('auth.loginSuccess'),
        duration: 2,
      })

      // Use navigate instead of window.location.href to avoid page reload
      // This ensures localStorage is properly set before navigation
      setTimeout(() => {
        navigate('/')
      }, 300)
    } catch (error: any) {
      // Determine error message
      let errorMsg = t('auth.loginFailed')
      if (error.response?.status === 401) {
        errorMsg = t('auth.wrongCredentials')
      } else if (error.response?.status === 400) {
        errorMsg = error.response?.data?.detail || t('auth.captchaInvalid')
      } else if (error.response?.status === 429) {
        errorMsg = t('auth.tooManyAttempts')
      } else if (error.code === 'ECONNABORTED' || error.code === 'ERR_NETWORK') {
        errorMsg = t('auth.networkError')
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

  // Handle 2FA verification
  const handle2FAVerification = async (values: { twofa_code: string }) => {
    if (!loginCredentials) {
      message.error(t('auth.sessionExpired'))
      setRequires2FA(false)
      return
    }

    setLoading(true)
    try {
      // Get fresh captcha for 2FA verification
      const captchaResponse = await axios.get('/api/v1/captcha/', {
        responseType: 'blob',
      })
      const newCaptchaId = captchaResponse.headers['x-captcha-id']

      // Send 2FA verification request
      const response = await axios.post('/api/v1/admin/2fa/login-verify', {
        email: loginCredentials.username, // Backend expects email but we pass username
        password: loginCredentials.password,
        token: values.twofa_code,
        captcha_id: newCaptchaId,
        captcha_code: values.twofa_code.slice(0, 4), // Use first 4 chars as dummy captcha
      })

      // Save tokens
      localStorage.setItem('admin_access_token', response.data.access_token)
      localStorage.setItem('admin_refresh_token', response.data.refresh_token)

      // Save username if remember me is checked
      if (rememberMe) {
        localStorage.setItem('admin_saved_username', loginCredentials.username)
      } else {
        localStorage.removeItem('admin_saved_username')
      }

      message.success({
        content: t('auth.loginSuccess'),
        duration: 2,
      })

      setTimeout(() => {
        navigate('/')
      }, 300)
    } catch (error: any) {
      let errorMsg = t('auth.twoFactorFailed')
      if (error.response?.status === 401) {
        errorMsg = t('auth.twoFactorInvalid')
      } else if (error.response?.data?.detail) {
        errorMsg = error.response.data.detail
      }

      message.error({
        content: errorMsg,
        duration: 4,
      })
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
          <h1 className="login-title">{t('auth.pageTitle')}</h1>
          <p className="login-subtitle">{t('auth.pageSubtitle')}</p>
        </div>

        {!requires2FA ? (
          // Normal login form
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
              label={t('auth.username')}
              rules={[{ required: true, message: t('auth.usernamePlaceholder') }]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder={t('auth.usernamePlaceholder')}
                autoComplete="username"
              />
            </Form.Item>

            <Form.Item
              name="password"
              label={t('auth.password')}
              rules={[{ required: true, message: t('auth.passwordPlaceholder') }]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder={t('auth.passwordPlaceholder')}
                autoComplete="current-password"
              />
            </Form.Item>

            <Form.Item
              name="captcha_code"
              label={t('auth.captcha')}
              rules={[
                { required: true, message: t('auth.captchaPlaceholder') },
                { len: 4, message: t('auth.captchaLength') }
              ]}
            >
              <Space.Compact style={{ width: '100%' }}>
                <Input
                  prefix={<SafetyOutlined />}
                  placeholder={t('auth.captchaPlaceholder')}
                  maxLength={4}
                  style={{ width: '60%' }}
                  autoComplete="off"
                />
                <div
                  className="captcha-image-container"
                  onClick={loadCaptcha}
                  title={t('auth.clickToRefresh')}
                >
                  {captchaLoading ? (
                    <ReloadOutlined spin style={{ fontSize: 18, color: getColor('primary', theme) }} />
                  ) : captchaUrl ? (
                    <img
                      src={captchaUrl}
                      alt="验证码"
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  ) : (
                    <span style={{ color: getTextColor('disabled', theme), fontSize: 12 }}>{t('auth.captchaLoading')}</span>
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
                  {t('auth.rememberMe')}
                </Checkbox>
                <a
                  className="forgot-password-link"
                  onClick={() => setForgotPasswordVisible(true)}
                >
                  {t('auth.forgotPassword')}
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
                {loading ? t('auth.loggingIn') : t('auth.login')}
              </Button>
            </Form.Item>
          </Form>
        ) : (
          // 2FA verification form
          <Form
            name="twofa"
            onFinish={handle2FAVerification}
            autoComplete="off"
            className="login-form"
            layout="vertical"
          >
            <div style={{ textAlign: 'center', marginBottom: 24 }}>
              <SafetyOutlined style={{ fontSize: 48, color: getColor('primary', theme) }} />
              <h3 style={{ marginTop: 16, marginBottom: 8 }}>{t('auth.twoFactorAuth')}</h3>
              <p style={{ color: getTextColor('secondary', theme) }}>
                {t('auth.twoFactorDescription')}
                <br />
                <small>{t('auth.twoFactorBackupHint')}</small>
              </p>
            </div>

            <Form.Item
              name="twofa_code"
              rules={[
                { required: true, message: t('auth.twoFactorCodeRequired') },
                {
                  pattern: /^(\d{6}|[A-Z0-9]{4}-[A-Z0-9]{4})$/i,
                  message: t('auth.twoFactorCodeFormat')
                }
              ]}
            >
              <Input
                prefix={<SafetyOutlined />}
                placeholder={t('auth.twoFactorPlaceholder')}
                maxLength={9}
                size="large"
                style={{
                  fontSize: '20px',
                  letterSpacing: '4px',
                  textAlign: 'center',
                  textTransform: 'uppercase'
                }}
                autoFocus
              />
            </Form.Item>

            <Form.Item style={{ marginBottom: 8 }}>
              <Button
                type="primary"
                htmlType="submit"
                block
                loading={loading}
                size="large"
                className="login-button"
              >
                {loading ? t('auth.verifying') : t('auth.verify')}
              </Button>
            </Form.Item>

            <Form.Item style={{ marginBottom: 0 }}>
              <Button
                block
                onClick={() => {
                  setRequires2FA(false)
                  setLoginCredentials(null)
                  form.resetFields()
                }}
                size="large"
              >
                {t('auth.backToLogin')}
              </Button>
            </Form.Item>
          </Form>
        )}

        <Divider className="login-divider" />

        {/* Default account info */}
        <div className="account-info">
          <div className="account-info-title">{t('auth.testAccount')}</div>
          <div className="account-info-item">
            <span className="account-label">{t('auth.adminAccount')}</span>
            <span className="account-value">admin / admin123456</span>
          </div>
          <div className="account-info-item">
            <span className="account-label">{t('auth.editorAccount')}</span>
            <span className="account-value">editor / editor123456</span>
          </div>
        </div>

        {/* Footer */}
        <div className="login-footer">
          <p>{t('auth.footerText')}</p>
        </div>
      </Card>

      {/* Forgot Password Modal */}
      <Modal
        title={
          <div className="reset-modal-header">
            <span className="reset-modal-title">{t('auth.passwordReset')}</span>
            <Steps
              current={resetStep - 1}
              size="small"
              className="reset-steps"
              items={[
                { title: t('auth.verifyEmail'), icon: <MailOutlined /> },
                { title: t('auth.resetPassword'), icon: <LockOutlined /> },
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
              <span>{t('auth.resetEmailDescription')}</span>
            </div>

            <Form.Item
              name="email"
              label={t('auth.emailAddress')}
              rules={[
                { required: true, message: t('auth.emailRequired') },
                { type: 'email', message: t('auth.emailInvalid') }
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
                  {t('auth.cancel')}
                </Button>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={resetLoading}
                  className="reset-button"
                  size="large"
                  icon={!resetLoading && <MailOutlined />}
                >
                  {resetLoading ? t('auth.sending') : t('auth.sendCode')}
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
                {t('auth.codeSentTo')} <strong>{resetEmail}</strong>
                <br />
                <small>{t('auth.codeExpiry')}</small>
              </span>
            </div>

            <Form.Item
              name="code"
              label={
                <span>
                  {t('auth.verificationCode')}
                  {countdown > 0 && (
                    <span className="countdown-text">
                      <ClockCircleOutlined /> {countdown}{t('auth.resendAfter')}
                    </span>
                  )}
                </span>
              }
              rules={[
                { required: true, message: t('auth.codeRequired') },
                { len: 6, message: t('auth.codeLength') },
                { pattern: /^\d{6}$/, message: t('auth.codeDigitsOnly') }
              ]}
            >
              <Space.Compact style={{ width: '100%' }}>
                <Input
                  ref={codeInputRef}
                  prefix={<SafetyOutlined />}
                  placeholder={t('auth.codePlaceholder')}
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
                  {countdown > 0 ? `${countdown}${t('auth.seconds')}` : t('auth.resend')}
                </Button>
              </Space.Compact>
            </Form.Item>

            <Form.Item
              name="new_password"
              label={t('auth.newPassword')}
              rules={[
                { required: true, message: t('auth.newPasswordRequired') },
                { min: 8, message: t('auth.passwordMinLength') }
              ]}
            >
              <div>
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder={t('auth.newPasswordPlaceholder')}
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
                          ? getColor('error', theme)
                          : passwordStrength < 70
                          ? getColor('warning', theme)
                          : getColor('success', theme)
                      }
                      showInfo={false}
                    />
                    <span className={`strength-text strength-${
                      passwordStrength < 40 ? 'weak' : passwordStrength < 70 ? 'medium' : 'strong'
                    }`}>
                      {passwordStrength < 40 ? t('auth.weak') : passwordStrength < 70 ? t('auth.medium') : t('auth.strong')}
                    </span>
                  </div>
                )}
              </div>
            </Form.Item>

            <Form.Item
              name="confirm_password"
              label={t('auth.confirmPassword')}
              rules={[
                { required: true, message: t('auth.confirmPasswordRequired') },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('new_password') === value) {
                      return Promise.resolve()
                    }
                    return Promise.reject(new Error(t('auth.passwordMismatch')))
                  },
                }),
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder={t('auth.confirmPasswordPlaceholder')}
                size="large"
              />
            </Form.Item>

            <Form.Item style={{ marginBottom: 0 }}>
              <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                <Button onClick={() => { setResetStep(1); setPasswordStrength(0) }} size="large">
                  {t('auth.previousStep')}
                </Button>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={resetLoading}
                  className="reset-button"
                  size="large"
                  icon={!resetLoading && <CheckCircleOutlined />}
                >
                  {resetLoading ? t('auth.resetting') : t('auth.confirmReset')}
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
