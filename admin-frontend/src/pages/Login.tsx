import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Form, Input, Button, Card, message, Space, Switch } from 'antd'
import { UserOutlined, LockOutlined, SafetyOutlined, ReloadOutlined, SunOutlined, MoonOutlined, VideoCameraOutlined } from '@ant-design/icons'
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
  const [form] = Form.useForm()

  // Load captcha and saved username on component mount
  useEffect(() => {
    loadCaptcha()
    // Load saved username
    const savedUsername = localStorage.getItem('admin_saved_username')
    if (savedUsername) {
      form.setFieldsValue({ username: savedUsername })
    }
  }, [])

  const loadCaptcha = async () => {
    setCaptchaLoading(true)
    try {
      const response = await axios.get('/api/v1/captcha/', {
        responseType: 'blob',
      })

      // Get captcha ID from response headers
      const id = response.headers['x-captcha-id']
      setCaptchaId(id)

      // Create object URL for the image
      const imageUrl = URL.createObjectURL(response.data)
      setCaptchaUrl(imageUrl)
    } catch (error) {
      message.error('加载验证码失败')
    } finally {
      setCaptchaLoading(false)
    }
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

      // Save username for next time
      localStorage.setItem('admin_saved_username', values.username)

      message.success('登录成功！')

      // Use navigate instead of window.location.href to avoid page reload
      // This ensures localStorage is properly set before navigation
      setTimeout(() => {
        navigate('/')
      }, 100)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '登录失败，请检查用户名和密码')
      // Reload captcha on error
      loadCaptcha()
      // Clear password field
      form.setFieldsValue({ captcha_code: '' })
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

      {/* Animated background particles */}
      <div className="particles">
        {[...Array(20)].map((_, i) => (
          <div key={i} className="particle" style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 20}s`,
            animationDuration: `${15 + Math.random() * 10}s`
          }} />
        ))}
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
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名！' }]}
          >
            <Input
              prefix={<UserOutlined style={{ color: '#bfbfbf' }} />}
              placeholder="用户名"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码！' }]}
          >
            <Input.Password
              prefix={<LockOutlined style={{ color: '#bfbfbf' }} />}
              placeholder="密码"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="captcha_code"
            rules={[
              { required: true, message: '请输入验证码！' },
              { len: 4, message: '验证码为4位字符！' }
            ]}
          >
            <Space.Compact style={{ width: '100%' }}>
              <Input
                prefix={<SafetyOutlined style={{ color: '#bfbfbf' }} />}
                placeholder="验证码"
                size="large"
                maxLength={4}
                style={{ width: '60%' }}
              />
              <div
                style={{
                  width: '40%',
                  height: 40,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: '1px solid #d9d9d9',
                  borderRadius: '0 6px 6px 0',
                  cursor: 'pointer',
                  position: 'relative',
                  overflow: 'hidden',
                }}
                onClick={loadCaptcha}
              >
                {captchaLoading ? (
                  <ReloadOutlined spin style={{ fontSize: 20, color: '#1890ff' }} />
                ) : captchaUrl ? (
                  <img
                    src={captchaUrl}
                    alt="验证码"
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                ) : (
                  <span style={{ color: '#bfbfbf' }}>加载中...</span>
                )}
              </div>
            </Space.Compact>
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              block
              size="large"
              loading={loading}
              className="login-button"
            >
              {loading ? '登录中...' : '登 录'}
            </Button>
          </Form.Item>
        </Form>

        {/* Default account info */}
        <div className="account-info">
          <div className="account-info-item">
            <span className="account-label">管理员：</span>
            <span className="account-value">admin / admin123456</span>
          </div>
          <div className="account-info-item">
            <span className="account-label">编辑员：</span>
            <span className="account-value">editor / editor123456</span>
          </div>
        </div>

        {/* Footer */}
        <div className="login-footer">
          <p>© 2025 Video Site. All rights reserved.</p>
        </div>
      </Card>
    </div>
  )
}

export default Login
