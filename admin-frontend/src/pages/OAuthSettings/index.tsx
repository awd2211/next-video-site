import { useState, useEffect } from 'react'
import {
  Card,
  Tabs,
  Form,
  Input,
  Switch,
  Button,
  Space,
  message,
  Alert,
  Divider,
  Tag,
  Typography,
  Spin,
  Modal
} from 'antd'
import {
  GoogleOutlined,
  FacebookOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  SaveOutlined,
  ReloadOutlined
} from '@ant-design/icons'
import axios from 'axios'

const { Title, Paragraph, Text, Link } = Typography
const { TextArea } = Input

interface OAuthConfig {
  id?: number
  provider: string
  client_id: string
  client_secret: string
  redirect_uri: string
  scopes: string[]
  enabled: boolean
  authorization_url?: string
  token_url?: string
  userinfo_url?: string
  test_status?: string
  test_message?: string
}

const OAuthSettings = () => {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)
  const [googleConfig, setGoogleConfig] = useState<OAuthConfig | null>(null)
  const [facebookConfig, setFacebookConfig] = useState<OAuthConfig | null>(null)
  const [googleForm] = Form.useForm()
  const [facebookForm] = Form.useForm()

  // Fetch OAuth configurations
  const fetchConfigs = async () => {
    setLoading(true)
    try {
      const response = await axios.get('/api/v1/admin/oauth/configs', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      })
      const configs = response.data
      const google = configs.find((c: OAuthConfig) => c.provider === 'google')
      const facebook = configs.find((c: OAuthConfig) => c.provider === 'facebook')

      if (google) {
        setGoogleConfig(google)
        googleForm.setFieldsValue({
          ...google,
          scopes: google.scopes.join(', ')
        })
      }
      if (facebook) {
        setFacebookConfig(facebook)
        facebookForm.setFieldsValue({
          ...facebook,
          scopes: facebook.scopes.join(', ')
        })
      }
    } catch (error: any) {
      console.error('Failed to fetch OAuth configs:', error)
      message.error('获取 OAuth 配置失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchConfigs()
  }, [])

  // Save OAuth configuration
  const saveConfig = async (provider: string, values: any) => {
    setSaving(true)
    try {
      const payload = {
        provider,
        client_id: values.client_id,
        client_secret: values.client_secret,
        redirect_uri: values.redirect_uri || `${window.location.origin}/oauth/${provider}/callback`,
        scopes: values.scopes.split(',').map((s: string) => s.trim()),
        enabled: values.enabled ?? false,
        authorization_url: values.authorization_url,
        token_url: values.token_url,
        userinfo_url: values.userinfo_url
      }

      const config = provider === 'google' ? googleConfig : facebookConfig

      if (config?.id) {
        // Update existing config
        await axios.put(`/api/v1/admin/oauth/configs/${provider}`, payload, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        })
        message.success(`${provider} OAuth 配置已更新`)
      } else {
        // Create new config
        await axios.post('/api/v1/admin/oauth/configs', payload, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        })
        message.success(`${provider} OAuth 配置已创建`)
      }

      // Refresh configs
      await fetchConfigs()
    } catch (error: any) {
      console.error('Failed to save OAuth config:', error)
      message.error(error.response?.data?.detail || '保存配置失败')
    } finally {
      setSaving(false)
    }
  }

  // Test OAuth configuration
  const testConfig = async (provider: string) => {
    setTesting(true)
    try {
      const response = await axios.post(
        `/api/v1/admin/oauth/configs/${provider}/test`,
        {},
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      )

      if (response.data.status === 'success') {
        Modal.success({
          title: '测试成功',
          content: response.data.message
        })
      } else {
        Modal.error({
          title: '测试失败',
          content: response.data.message
        })
      }
    } catch (error: any) {
      console.error('Failed to test OAuth config:', error)
      Modal.error({
        title: '测试失败',
        content: error.response?.data?.detail || '测试配置失败'
      })
    } finally {
      setTesting(false)
    }
  }

  // Google OAuth setup guide
  const GoogleGuide = () => (
    <Card size="small" style={{ marginBottom: 16 }}>
      <Title level={5}>Google OAuth 配置指南</Title>
      <Paragraph>
        <ol>
          <li>访问 <Link href="https://console.cloud.google.com" target="_blank">Google Cloud Console</Link></li>
          <li>创建或选择一个项目</li>
          <li>启用 Google+ API</li>
          <li>前往"凭据"页面，创建 OAuth 2.0 客户端 ID</li>
          <li>设置授权重定向 URI: <Text code>{window.location.origin}/oauth/google/callback</Text></li>
          <li>复制 Client ID 和 Client Secret 到下方表单</li>
        </ol>
      </Paragraph>
      <Paragraph>
        <Text strong>推荐的权限范围:</Text>
        <br />
        <Text code>openid, email, profile</Text>
      </Paragraph>
    </Card>
  )

  // Facebook OAuth setup guide
  const FacebookGuide = () => (
    <Card size="small" style={{ marginBottom: 16 }}>
      <Title level={5}>Facebook OAuth 配置指南</Title>
      <Paragraph>
        <ol>
          <li>访问 <Link href="https://developers.facebook.com" target="_blank">Facebook Developers</Link></li>
          <li>创建或选择一个应用</li>
          <li>添加 Facebook Login 产品</li>
          <li>在 Facebook Login 设置中，添加有效的 OAuth 重定向 URI: <Text code>{window.location.origin}/oauth/facebook/callback</Text></li>
          <li>在"设置" {">"} "基本"中找到应用编号（App ID）和应用密钥（App Secret）</li>
          <li>复制到下方表单</li>
        </ol>
      </Paragraph>
      <Paragraph>
        <Text strong>推荐的权限范围:</Text>
        <br />
        <Text code>email, public_profile</Text>
      </Paragraph>
    </Card>
  )

  // Render OAuth form
  const renderOAuthForm = (
    provider: 'google' | 'facebook',
    form: any,
    config: OAuthConfig | null,
    guide: React.ReactNode
  ) => {
    const providerName = provider === 'google' ? 'Google' : 'Facebook'
    const icon = provider === 'google' ? <GoogleOutlined /> : <FacebookOutlined />

    return (
      <Spin spinning={loading}>
        {guide}

        <Card>
          <Form
            form={form}
            layout="vertical"
            onFinish={(values) => saveConfig(provider, values)}
          >
            <Form.Item
              label="启用状态"
              name="enabled"
              valuePropName="checked"
            >
              <Switch
                checkedChildren="已启用"
                unCheckedChildren="已禁用"
              />
            </Form.Item>

            {config && config.test_status && (
              <Alert
                message={config.test_status === 'success' ? '配置测试成功' : '配置测试失败'}
                description={config.test_message}
                type={config.test_status === 'success' ? 'success' : 'error'}
                icon={config.test_status === 'success' ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />}
                showIcon
                style={{ marginBottom: 16 }}
              />
            )}

            <Form.Item
              label="Client ID"
              name="client_id"
              rules={[{ required: true, message: '请输入 Client ID' }]}
            >
              <Input placeholder={`输入 ${providerName} Client ID`} />
            </Form.Item>

            <Form.Item
              label="Client Secret"
              name="client_secret"
              rules={[{ required: true, message: '请输入 Client Secret' }]}
              extra="出于安全考虑，保存后只显示部分内容"
            >
              <Input.Password placeholder={`输入 ${providerName} Client Secret`} />
            </Form.Item>

            <Form.Item
              label="Redirect URI"
              name="redirect_uri"
              extra={`默认: ${window.location.origin}/oauth/${provider}/callback`}
            >
              <Input placeholder="自定义重定向 URI（可选）" />
            </Form.Item>

            <Form.Item
              label="权限范围 (Scopes)"
              name="scopes"
              rules={[{ required: true, message: '请输入权限范围' }]}
              extra="多个范围用逗号分隔"
            >
              <Input placeholder={provider === 'google' ? 'openid, email, profile' : 'email, public_profile'} />
            </Form.Item>

            <Divider orientation="left">高级设置（可选）</Divider>

            <Form.Item
              label="Authorization URL"
              name="authorization_url"
              extra="留空使用默认值"
            >
              <Input placeholder={`${providerName} 授权端点 URL`} />
            </Form.Item>

            <Form.Item
              label="Token URL"
              name="token_url"
              extra="留空使用默认值"
            >
              <Input placeholder={`${providerName} 令牌端点 URL`} />
            </Form.Item>

            <Form.Item
              label="UserInfo URL"
              name="userinfo_url"
              extra="留空使用默认值"
            >
              <Input placeholder={`${providerName} 用户信息端点 URL`} />
            </Form.Item>

            <Form.Item>
              <Space>
                <Button
                  type="primary"
                  htmlType="submit"
                  icon={<SaveOutlined />}
                  loading={saving}
                >
                  保存配置
                </Button>
                <Button
                  onClick={() => testConfig(provider)}
                  icon={<ReloadOutlined />}
                  loading={testing}
                  disabled={!config?.id}
                >
                  测试配置
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>
      </Spin>
    )
  }

  const tabItems = [
    {
      key: 'google',
      label: (
        <span>
          <GoogleOutlined /> Google OAuth
          {googleConfig?.enabled && <Tag color="green" style={{ marginLeft: 8 }}>已启用</Tag>}
        </span>
      ),
      children: renderOAuthForm('google', googleForm, googleConfig, <GoogleGuide />)
    },
    {
      key: 'facebook',
      label: (
        <span>
          <FacebookOutlined /> Facebook OAuth
          {facebookConfig?.enabled && <Tag color="green" style={{ marginLeft: 8 }}>已启用</Tag>}
        </span>
      ),
      children: renderOAuthForm('facebook', facebookForm, facebookConfig, <FacebookGuide />)
    }
  ]

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>OAuth 登录配置</Title>
      <Paragraph>
        配置 Google 和 Facebook OAuth 登录，允许用户使用社交账号快速注册和登录。
      </Paragraph>

      <Alert
        message="安全提示"
        description="请妥善保管 Client Secret，不要在客户端代码中暴露。所有 OAuth 配置仅对超级管理员可见。"
        type="warning"
        showIcon
        style={{ marginBottom: 24 }}
      />

      <Tabs items={tabItems} />
    </div>
  )
}

export default OAuthSettings
