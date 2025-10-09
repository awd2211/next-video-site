import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Form, Input, Button, Card, message, Space } from 'antd'
import { UserOutlined, LockOutlined, SafetyOutlined, ReloadOutlined } from '@ant-design/icons'
import axios from 'axios'  // Use native axios for login, not the intercepted instance

const Login = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [captchaId, setCaptchaId] = useState('')
  const [captchaUrl, setCaptchaUrl] = useState('')
  const [captchaLoading, setCaptchaLoading] = useState(false)

  // Load captcha on component mount
  useEffect(() => {
    loadCaptcha()
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
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <Card
        style={{
          width: 450,
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
          borderRadius: '16px'
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <h1 style={{ fontSize: 28, fontWeight: 'bold', color: '#1890ff', marginBottom: 8 }}>
            视频管理后台
          </h1>
          <p style={{ color: '#8c8c8c', fontSize: 14 }}>Video Site Admin Panel</p>
        </div>

        <Form name="login" onFinish={onFinish} autoComplete="off">
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
              style={{ height: 48, fontSize: 16, fontWeight: 500 }}
            >
              登 录
            </Button>
          </Form.Item>
        </Form>

        <div style={{ marginTop: 24, textAlign: 'center', fontSize: 13, color: '#8c8c8c' }}>
          <p style={{ marginBottom: 4 }}>默认账号：admin / admin123456</p>
          <p>编辑账号：editor / editor123456</p>
        </div>
      </Card>
    </div>
  )
}

export default Login
