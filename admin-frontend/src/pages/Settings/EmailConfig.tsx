import { useState } from 'react'
import {
  Card,
  Form,
  Input,
  InputNumber,
  Button,
  Switch,
  Select,
  message,
  Tabs,
  Space,
  Modal,
  List,
  Tag,
} from 'antd'
import { SaveOutlined, SendOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from '@/utils/axios'

const { Option } = Select
const { TabPane } = Tabs

const EmailConfig = () => {
  const [form] = Form.useForm()
  const [provider, setProvider] = useState<'smtp' | 'mailgun'>('smtp')
  const [testEmailModal, setTestEmailModal] = useState(false)
  const [testEmail, setTestEmail] = useState('')
  const [selectedConfigId, setSelectedConfigId] = useState<number>()
  const queryClient = useQueryClient()  // Fetch email configurations
  const { data: configs, isLoading } = useQuery({
    queryKey: ['email-configs'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/email/config')
      return response.data
    },
  })

  // Create/Update mutation
  const saveMutation = useMutation({
    mutationFn: async (values: any) => {
      if (selectedConfigId) {
        // Update
        await axios.put(`/api/v1/admin/email/config/${selectedConfigId}`, values)
      } else {
        // Create
        await axios.post('/api/v1/admin/email/config', values)
      }
    },
    onSuccess: () => {
      message.success('邮件配置保存成功')
      queryClient.invalidateQueries({ queryKey: ['email-configs'] })
      form.resetFields()
      setSelectedConfigId(undefined)
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '保存失败')
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await axios.delete(`/api/v1/admin/email/config/${id}`)
    },
    onSuccess: () => {
      message.success('配置已删除')
      queryClient.invalidateQueries({ queryKey: ['email-configs'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '删除失败')
    },
  })

  // Test email mutation
  const testEmailMutation = useMutation({
    mutationFn: async ({ configId, email }: { configId: number; email: string }) => {
      await axios.post(
        `/api/v1/admin/email/config/${configId}/test`,
        { test_email: email }
      )
    },
    onSuccess: () => {
      message.success('测试邮件已发送，请检查收件箱')
      setTestEmailModal(false)
      setTestEmail('')
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '发送失败')
    },
  })

  const handleEdit = (config: any) => {
    setSelectedConfigId(config.id)
    setProvider(config.provider)
    form.setFieldsValue(config)
  }

  const handleDelete = (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个邮件配置吗？',
      onOk: () => deleteMutation.mutate(id),
    })
  }

  const handleTestEmail = (configId: number) => {
    setSelectedConfigId(configId)
    setTestEmailModal(true)
  }

  const onFinish = (values: any) => {
    saveMutation.mutate({ ...values, provider })
  }

  return (
    <div>
      <Card title="邮件服务器配置" style={{ marginBottom: 24 }}>
        <Tabs activeKey={provider} onChange={(key) => setProvider(key as any)}>
          <TabPane tab="SMTP 配置" key="smtp">
            <Form form={form} layout="vertical" onFinish={onFinish}>
              <Form.Item name="provider" initialValue="smtp" hidden>
                <Input />
              </Form.Item>

              <Form.Item
                name="smtp_host"
                label="SMTP 服务器地址"
                rules={[{ required: true, message: '请输入SMTP服务器地址' }]}
              >
                <Input placeholder="smtp.example.com" />
              </Form.Item>

              <Form.Item
                name="smtp_port"
                label="SMTP 端口"
                rules={[{ required: true, message: '请输入端口号' }]}
              >
                <InputNumber style={{ width: '100%' }} placeholder="587" />
              </Form.Item>

              <Form.Item
                name="smtp_username"
                label="用户名"
                rules={[{ required: true, message: '请输入用户名' }]}
              >
                <Input placeholder="your-email@example.com" />
              </Form.Item>

              <Form.Item
                name="smtp_password"
                label="密码"
                rules={[{ required: true, message: '请输入密码' }]}
              >
                <Input.Password placeholder="密码或授权码" />
              </Form.Item>

              <Space size="large">
                <Form.Item name="smtp_use_tls" label="使用 TLS" valuePropName="checked">
                  <Switch defaultChecked />
                </Form.Item>

                <Form.Item name="smtp_use_ssl" label="使用 SSL" valuePropName="checked">
                  <Switch />
                </Form.Item>
              </Space>

              <Form.Item
                name="from_email"
                label="发件人邮箱"
                rules={[
                  { required: true, message: '请输入发件人邮箱' },
                  { type: 'email', message: '请输入有效的邮箱地址' },
                ]}
              >
                <Input placeholder="noreply@example.com" />
              </Form.Item>

              <Form.Item
                name="from_name"
                label="发件人名称"
                rules={[{ required: true, message: '请输入发件人名称' }]}
              >
                <Input placeholder="视频平台" />
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button
                    type="primary"
                    htmlType="submit"
                    icon={<SaveOutlined />}
                    loading={saveMutation.isPending}
                  >
                    保存配置
                  </Button>
                  {selectedConfigId && (
                    <Button
                      onClick={() => {
                        form.resetFields()
                        setSelectedConfigId(undefined)
                      }}
                    >
                      取消编辑
                    </Button>
                  )}
                </Space>
              </Form.Item>
            </Form>
          </TabPane>

          <TabPane tab="Mailgun 配置" key="mailgun">
            <Form form={form} layout="vertical" onFinish={onFinish}>
              <Form.Item name="provider" initialValue="mailgun" hidden>
                <Input />
              </Form.Item>

              <Form.Item
                name="mailgun_api_key"
                label="Mailgun API Key"
                rules={[{ required: true, message: '请输入API Key' }]}
              >
                <Input.Password placeholder="key-xxxxxxxxxxxxxxxxxxxxxxxx" />
              </Form.Item>

              <Form.Item
                name="mailgun_domain"
                label="Mailgun Domain"
                rules={[{ required: true, message: '请输入Domain' }]}
              >
                <Input placeholder="mg.example.com" />
              </Form.Item>

              <Form.Item name="mailgun_base_url" label="Base URL" initialValue="https://api.mailgun.net/v3">
                <Input placeholder="https://api.mailgun.net/v3" />
              </Form.Item>

              <Form.Item
                name="from_email"
                label="发件人邮箱"
                rules={[
                  { required: true, message: '请输入发件人邮箱' },
                  { type: 'email', message: '请输入有效的邮箱地址' },
                ]}
              >
                <Input placeholder="noreply@example.com" />
              </Form.Item>

              <Form.Item
                name="from_name"
                label="发件人名称"
                rules={[{ required: true, message: '请输入发件人名称' }]}
              >
                <Input placeholder="视频平台" />
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button
                    type="primary"
                    htmlType="submit"
                    icon={<SaveOutlined />}
                    loading={saveMutation.isPending}
                  >
                    保存配置
                  </Button>
                  {selectedConfigId && (
                    <Button
                      onClick={() => {
                        form.resetFields()
                        setSelectedConfigId(undefined)
                      }}
                    >
                      取消编辑
                    </Button>
                  )}
                </Space>
              </Form.Item>
            </Form>
          </TabPane>
        </Tabs>
      </Card>

      <Card title="已保存的配置" loading={isLoading}>
        <List
          dataSource={configs || []}
          renderItem={(config: any) => (
            <List.Item
              actions={[
                <Button size="small" onClick={() => handleEdit(config)}>
                  编辑
                </Button>,
                <Button
                  size="small"
                  icon={<SendOutlined />}
                  onClick={() => handleTestEmail(config.id)}
                >
                  测试
                </Button>,
                <Button
                  size="small"
                  danger
                  icon={<DeleteOutlined />}
                  onClick={() => handleDelete(config.id)}
                >
                  删除
                </Button>,
              ]}
            >
              <List.Item.Meta
                title={
                  <Space>
                    <span>{config.provider.toUpperCase()}</span>
                    {config.is_active && <Tag color="green">活跃</Tag>}
                  </Space>
                }
                description={
                  <div>
                    <div>发件人: {config.from_name} &lt;{config.from_email}&gt;</div>
                    {config.provider === 'smtp' && (
                      <div>服务器: {config.smtp_host}:{config.smtp_port}</div>
                    )}
                    {config.provider === 'mailgun' && (
                      <div>Domain: {config.mailgun_domain}</div>
                    )}
                  </div>
                }
              />
            </List.Item>
          )}
        />
      </Card>

      <Modal
        title="发送测试邮件"
        open={testEmailModal}
        onOk={() => {
          if (selectedConfigId && testEmail) {
            testEmailMutation.mutate({ configId: selectedConfigId, email: testEmail })
          }
        }}
        onCancel={() => {
          setTestEmailModal(false)
          setTestEmail('')
        }}
        confirmLoading={testEmailMutation.isPending}
      >
        <Input
          placeholder="请输入接收测试邮件的邮箱地址"
          value={testEmail}
          onChange={(e) => setTestEmail(e.target.value)}
          type="email"
        />
      </Modal>
    </div>
  )
}

export default EmailConfig
