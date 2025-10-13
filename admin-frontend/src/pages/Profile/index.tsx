/**
 * 管理员个人资料页面
 */
import { useState, useEffect } from 'react'
import { Card, Form, Input, Button, Avatar, message, Tabs, Space, Typography, Descriptions } from 'antd'
import { UserOutlined, LockOutlined, MailOutlined, SaveOutlined } from '@ant-design/icons'
import profileService, { type AdminProfile, type UpdateProfileRequest } from '../../services/profileService'

const { Title, Text } = Typography
const { TabPane } = Tabs

export default function Profile() {
  const [profileForm] = Form.useForm()
  const [passwordForm] = Form.useForm()
  const [emailForm] = Form.useForm()

  const [profile, setProfile] = useState<AdminProfile | null>(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('info')

  // 加载管理员资料
  const loadProfile = async () => {
    try {
      setLoading(true)
      const data = await profileService.getProfile()
      setProfile(data)
      // 设置表单初始值
      profileForm.setFieldsValue({
        full_name: data.full_name,
        avatar: data.avatar,
      })
    } catch (error: any) {
      message.error(error.response?.data?.detail || '加载个人资料失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProfile()
  }, [])

  // 更新个人资料
  const handleUpdateProfile = async (values: UpdateProfileRequest) => {
    try {
      setLoading(true)
      const updated = await profileService.updateProfile(values)
      setProfile(updated)
      message.success('个人资料更新成功')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '更新个人资料失败')
    } finally {
      setLoading(false)
    }
  }

  // 修改密码
  const handleChangePassword = async (values: any) => {
    try {
      setLoading(true)
      await profileService.changePassword({
        old_password: values.old_password,
        new_password: values.new_password,
      })
      message.success('密码修改成功，建议重新登录')
      passwordForm.resetFields()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '修改密码失败')
    } finally {
      setLoading(false)
    }
  }

  // 修改邮箱
  const handleChangeEmail = async (values: any) => {
    try {
      setLoading(true)
      const updated = await profileService.changeEmail({
        new_email: values.new_email,
        password: values.password,
      })
      setProfile(updated)
      message.success('邮箱修改成功')
      emailForm.resetFields()
      setActiveTab('info')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '修改邮箱失败')
    } finally {
      setLoading(false)
    }
  }

  if (!profile) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Text>加载中...</Text>
      </div>
    )
  }

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>个人资料</Title>

      <Card style={{ marginTop: '24px' }}>
        {/* 头部信息卡片 */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '24px',
          padding: '24px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '8px',
          marginBottom: '24px'
        }}>
          <Avatar
            size={80}
            src={profile.avatar}
            icon={<UserOutlined />}
            style={{ border: '3px solid white' }}
          />
          <div style={{ color: 'white' }}>
            <Title level={3} style={{ color: 'white', marginBottom: '8px' }}>
              {profile.full_name || profile.username}
            </Title>
            <Space direction="vertical" size="small">
              <Text style={{ color: 'rgba(255,255,255,0.9)' }}>
                <MailOutlined /> {profile.email}
              </Text>
              <Text style={{ color: 'rgba(255,255,255,0.9)' }}>
                {profile.is_superadmin ? '超级管理员' : '内容编辑者'}
              </Text>
            </Space>
          </div>
        </div>

        {/* 标签页 */}
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          {/* 基本信息标签 */}
          <TabPane tab="基本信息" key="info">
            <Descriptions bordered column={2} style={{ marginBottom: '24px' }}>
              <Descriptions.Item label="用户名">{profile.username}</Descriptions.Item>
              <Descriptions.Item label="邮箱">{profile.email}</Descriptions.Item>
              <Descriptions.Item label="角色">
                {profile.is_superadmin ? '超级管理员' : '内容编辑者'}
              </Descriptions.Item>
              <Descriptions.Item label="创建时间">
                {new Date(profile.created_at).toLocaleString('zh-CN')}
              </Descriptions.Item>
              <Descriptions.Item label="最后登录">
                {profile.last_login_at
                  ? new Date(profile.last_login_at).toLocaleString('zh-CN')
                  : '未记录'}
              </Descriptions.Item>
            </Descriptions>

            <Title level={4}>编辑资料</Title>
            <Form
              form={profileForm}
              layout="vertical"
              onFinish={handleUpdateProfile}
              style={{ maxWidth: '600px' }}
            >
              <Form.Item
                label="全名"
                name="full_name"
                rules={[{ max: 200, message: '全名最多200个字符' }]}
              >
                <Input placeholder="输入您的全名" prefix={<UserOutlined />} />
              </Form.Item>

              <Form.Item
                label="头像URL"
                name="avatar"
                rules={[
                  { max: 500, message: '头像URL最多500个字符' },
                  { type: 'url', message: '请输入有效的URL' }
                ]}
              >
                <Input placeholder="输入头像图片URL" />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  icon={<SaveOutlined />}
                  style={{ background: '#0073bb' }}
                >
                  保存修改
                </Button>
              </Form.Item>
            </Form>
          </TabPane>

          {/* 修改密码标签 */}
          <TabPane tab="修改密码" key="password">
            <Form
              form={passwordForm}
              layout="vertical"
              onFinish={handleChangePassword}
              style={{ maxWidth: '600px' }}
            >
              <Form.Item
                label="当前密码"
                name="old_password"
                rules={[
                  { required: true, message: '请输入当前密码' },
                  { min: 6, message: '密码至少6个字符' }
                ]}
              >
                <Input.Password
                  placeholder="输入当前密码"
                  prefix={<LockOutlined />}
                />
              </Form.Item>

              <Form.Item
                label="新密码"
                name="new_password"
                rules={[
                  { required: true, message: '请输入新密码' },
                  { min: 6, message: '密码至少6个字符' },
                  { max: 100, message: '密码最多100个字符' }
                ]}
              >
                <Input.Password
                  placeholder="输入新密码（至少6个字符）"
                  prefix={<LockOutlined />}
                />
              </Form.Item>

              <Form.Item
                label="确认新密码"
                name="confirm_password"
                dependencies={['new_password']}
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
                  placeholder="再次输入新密码"
                  prefix={<LockOutlined />}
                />
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={loading}
                    icon={<SaveOutlined />}
                    style={{ background: '#ff9900' }}
                  >
                    修改密码
                  </Button>
                  <Button onClick={() => passwordForm.resetFields()}>
                    重置
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </TabPane>

          {/* 修改邮箱标签 */}
          <TabPane tab="修改邮箱" key="email">
            <Form
              form={emailForm}
              layout="vertical"
              onFinish={handleChangeEmail}
              style={{ maxWidth: '600px' }}
            >
              <Form.Item label="当前邮箱">
                <Input
                  value={profile.email}
                  disabled
                  prefix={<MailOutlined />}
                />
              </Form.Item>

              <Form.Item
                label="新邮箱地址"
                name="new_email"
                rules={[
                  { required: true, message: '请输入新邮箱地址' },
                  { type: 'email', message: '请输入有效的邮箱地址' }
                ]}
              >
                <Input
                  placeholder="输入新的邮箱地址"
                  prefix={<MailOutlined />}
                />
              </Form.Item>

              <Form.Item
                label="当前密码"
                name="password"
                extra="为了安全起见，修改邮箱需要验证您的当前密码"
                rules={[
                  { required: true, message: '请输入当前密码以验证身份' }
                ]}
              >
                <Input.Password
                  placeholder="输入当前密码进行验证"
                  prefix={<LockOutlined />}
                />
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={loading}
                    icon={<SaveOutlined />}
                    style={{ background: '#1d8102' }}
                  >
                    修改邮箱
                  </Button>
                  <Button onClick={() => emailForm.resetFields()}>
                    重置
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  )
}
