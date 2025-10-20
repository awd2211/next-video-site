import React, { useState } from 'react'
import {
  Card,
  Tabs,
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  InputNumber,
  Switch,
  Select,
  message,
  Popconfirm,
  Tag,
  Typography,
  Row,
  Col,
  Alert,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  MailOutlined,
  EyeOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { emailService, EmailConfiguration, EmailTemplate } from '@/services/email'
import { useTranslation } from 'react-i18next'
import ReactCodeMirror from '@uiw/react-codemirror'
import { html } from '@codemirror/lang-html'
import dayjs from 'dayjs'
import '@/styles/page-layout.css'

const { Title, Text, Paragraph } = Typography
const { Option } = Select
const { TextArea } = Input

const EmailManagement: React.FC = () => {
  const { t } = useTranslation()
  const [form] = Form.useForm()
  const [templateForm] = Form.useForm()
  const queryClient = useQueryClient()

  const [configPageSize, setConfigPageSize] = useState(20)
  const [templatePageSize, setTemplatePageSize] = useState(20)
  const [configModalVisible, setConfigModalVisible] = useState(false)
  const [templateModalVisible, setTemplateModalVisible] = useState(false)
  const [previewModalVisible, setPreviewModalVisible] = useState(false)
  const [testEmailModalVisible, setTestEmailModalVisible] = useState(false)
  const [editingConfig, setEditingConfig] = useState<EmailConfiguration | null>(null)
  const [editingTemplate, setEditingTemplate] = useState<EmailTemplate | null>(null)
  const [testConfigId, setTestConfigId] = useState<number | null>(null)
  const [previewContent, setPreviewContent] = useState<{
    subject: string
    html_content: string
  } | null>(null)
  const [htmlContent, setHtmlContent] = useState('')
  const [provider, setProvider] = useState<'smtp' | 'mailgun'>('smtp')

  // Fetch configurations
  const { data: configurations, isLoading: loadingConfigs } = useQuery({
    queryKey: ['email-configurations'],
    queryFn: emailService.getConfigurations,
  })

  // Fetch templates
  const { data: templates, isLoading: loadingTemplates } = useQuery({
    queryKey: ['email-templates'],
    queryFn: emailService.getTemplates,
  })

  // Create/Update Configuration
  const saveConfigMutation = useMutation({
    mutationFn: async (values: any) => {
      if (editingConfig) {
        return emailService.updateConfiguration(editingConfig.id, values)
      }
      return emailService.createConfiguration(values)
    },
    onSuccess: () => {
      message.success(
        editingConfig
          ? t('common.updateSuccess') || '更新成功'
          : t('common.createSuccess') || '创建成功'
      )
      queryClient.invalidateQueries({ queryKey: ['email-configurations'] })
      setConfigModalVisible(false)
      setEditingConfig(null)
      form.resetFields()
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('common.operationFailed'))
    },
  })

  // Delete Configuration
  const deleteConfigMutation = useMutation({
    mutationFn: emailService.deleteConfiguration,
    onSuccess: () => {
      message.success(t('common.deleteSuccess') || '删除成功')
      queryClient.invalidateQueries({ queryKey: ['email-configurations'] })
    },
  })

  // Test Configuration
  const testConfigMutation = useMutation({
    mutationFn: ({ id, email }: { id: number; email: string }) =>
      emailService.testConfiguration(id, email),
    onSuccess: () => {
      message.success(t('email.testEmailSent') || '测试邮件已发送')
      setTestEmailModalVisible(false)
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('email.testEmailFailed'))
    },
  })

  // Create/Update Template
  const saveTemplateMutation = useMutation({
    mutationFn: async (values: any) => {
      if (editingTemplate) {
        return emailService.updateTemplate(editingTemplate.id, values)
      }
      return emailService.createTemplate(values)
    },
    onSuccess: () => {
      message.success(
        editingTemplate ? t('common.updateSuccess') : t('common.createSuccess')
      )
      queryClient.invalidateQueries({ queryKey: ['email-templates'] })
      setTemplateModalVisible(false)
      setEditingTemplate(null)
      templateForm.resetFields()
      setHtmlContent('')
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('common.operationFailed'))
    },
  })

  // Delete Template
  const deleteTemplateMutation = useMutation({
    mutationFn: emailService.deleteTemplate,
    onSuccess: () => {
      message.success(t('common.deleteSuccess'))
      queryClient.invalidateQueries({ queryKey: ['email-templates'] })
    },
  })

  // Configuration Table Columns
  const configColumns = [
    {
      title: t('email.provider') || '提供商',
      dataIndex: 'provider',
      key: 'provider',
      width: 100,
      render: (provider: string) => (
        <Tag color={provider === 'smtp' ? 'blue' : 'green'}>{provider.toUpperCase()}</Tag>
      ),
    },
    {
      title: t('email.fromEmail') || '发件人邮箱',
      dataIndex: 'from_email',
      key: 'from_email',
    },
    {
      title: t('email.fromName') || '发件人名称',
      dataIndex: 'from_name',
      key: 'from_name',
    },
    {
      title: t('common.status') || '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (isActive: boolean) =>
        isActive ? (
          <Tag icon={<CheckCircleOutlined />} color="success">
            {t('common.active') || '启用'}
          </Tag>
        ) : (
          <Tag icon={<CloseCircleOutlined />} color="default">
            {t('common.inactive') || '禁用'}
          </Tag>
        ),
    },
    {
      title: t('common.createdAt') || '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: t('common.actions') || '操作',
      key: 'actions',
      width: 200,
      render: (_: any, record: EmailConfiguration) => (
        <Space>
          <Button
            size="small"
            icon={<MailOutlined />}
            onClick={() => {
              setTestConfigId(record.id)
              setTestEmailModalVisible(true)
            }}
          >
            {t('email.test') || '测试'}
          </Button>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => {
              setEditingConfig(record)
              setProvider(record.provider as 'smtp' | 'mailgun')
              form.setFieldsValue(record)
              setConfigModalVisible(true)
            }}
          >
            {t('common.edit')}
          </Button>
          <Popconfirm
            title={t('common.confirmDelete')}
            onConfirm={() => deleteConfigMutation.mutate(record.id)}
          >
            <Button size="small" danger icon={<DeleteOutlined />}>
              {t('common.delete')}
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  // Template Table Columns
  const templateColumns = [
    {
      title: t('email.templateName') || '模板名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: t('email.slug') || '标识符',
      dataIndex: 'slug',
      key: 'slug',
      render: (slug: string) => <Tag>{slug}</Tag>,
    },
    {
      title: t('email.subject') || '邮件主题',
      dataIndex: 'subject',
      key: 'subject',
      ellipsis: true,
    },
    {
      title: t('email.variables') || '变量',
      dataIndex: 'variables',
      key: 'variables',
      render: (variables: string[]) =>
        variables?.map((v) => <Tag key={v}>{`{{${v}}}`}</Tag>) || '-',
    },
    {
      title: t('common.status') || '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (isActive: boolean) =>
        isActive ? (
          <Tag icon={<CheckCircleOutlined />} color="success">
            {t('common.active')}
          </Tag>
        ) : (
          <Tag icon={<CloseCircleOutlined />} color="default">
            {t('common.inactive')}
          </Tag>
        ),
    },
    {
      title: t('common.actions') || '操作',
      key: 'actions',
      width: 200,
      render: (_: any, record: EmailTemplate) => (
        <Space>
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={async () => {
              try {
                const sampleVariables: Record<string, string> = {}
                record.variables?.forEach((v) => {
                  sampleVariables[v] = `{${v} ${t('email.sampleValue')}}`
                })
                const preview = await emailService.previewTemplate(
                  record.id,
                  sampleVariables
                )
                setPreviewContent(preview)
                setPreviewModalVisible(true)
              } catch (error: any) {
                message.error(t('email.previewFailed') || '预览失败')
              }
            }}
          >
            {t('common.preview') || '预览'}
          </Button>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => {
              setEditingTemplate(record)
              setHtmlContent(record.html_content)
              templateForm.setFieldsValue(record)
              setTemplateModalVisible(true)
            }}
          >
            {t('common.edit')}
          </Button>
          <Popconfirm
            title={t('common.confirmDelete')}
            onConfirm={() => deleteTemplateMutation.mutate(record.id)}
          >
            <Button size="small" danger icon={<DeleteOutlined />}>
              {t('common.delete')}
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  // Handle Configuration Save
  const handleConfigSave = async () => {
    try {
      const values = await form.validateFields()
      values.provider = provider
      await saveConfigMutation.mutateAsync(values)
    } catch (error) {
      console.error('Validation failed:', error)
    }
  }

  // Handle Template Save
  const handleTemplateSave = async () => {
    try {
      const values = await templateForm.validateFields()
      values.html_content = htmlContent
      await saveTemplateMutation.mutateAsync(values)
    } catch (error) {
      console.error('Validation failed:', error)
    }
  }

  // Handle Test Email
  const handleTestEmail = async (values: { test_email: string }) => {
    if (testConfigId) {
      await testConfigMutation.mutateAsync({
        id: testConfigId,
        email: values.test_email,
      })
    }
  }

  return (
    <div className="page-container">
      {/* Page Header */}
      <div className="page-header">
        <div className="page-header-content">
          <div className="page-header-left">
            <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 600 }}>{t('menu.emailManagement') || '邮件管理'}</h2>
            <Text type="secondary" style={{ marginLeft: 16 }}>
              {t('email.description') || '配置邮件服务器和管理邮件模板'}
            </Text>
          </div>
        </div>
      </div>

      {/* Page Content */}
      <div className="page-content">
        <Tabs
          defaultActiveKey="configuration"
          items={[
            {
              key: 'configuration',
              label: t('email.configuration') || '邮件配置',
              children: (
                <div>
                  <Row justify="space-between" style={{ marginBottom: 16 }}>
                    <Col>
                      <Alert
                        message={t('email.configInfo') || '邮件配置信息'}
                        description={
                          t('email.configDescription') ||
                          '配置SMTP或Mailgun服务来发送系统邮件。同时只能启用一个配置。'
                        }
                        type="info"
                        showIcon
                        style={{ marginBottom: 16 }}
                      />
                    </Col>
                  </Row>
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={() => {
                      setEditingConfig(null)
                      setProvider('smtp')
                      form.resetFields()
                      setConfigModalVisible(true)
                    }}
                    style={{ marginBottom: 16 }}
                  >
                    {t('email.addConfiguration') || '添加配置'}
                  </Button>
                  <Table
                    dataSource={configurations}
                    columns={configColumns}
                    rowKey="id"
                    loading={loadingConfigs}
                    pagination={{
                      pageSize: configPageSize,
                      onShowSizeChange: (current, size) => setConfigPageSize(size),
                      showSizeChanger: true,
                      pageSizeOptions: ['10', '20', '50', '100'],
                      showQuickJumper: true,
                      showTotal: (total) => t('common.total', { count: total }),
                    }}
                  />
                </div>
              ),
            },
            {
              key: 'templates',
              label: t('email.templates') || '邮件模板',
              children: (
                <div>
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={() => {
                      setEditingTemplate(null)
                      setHtmlContent('')
                      templateForm.resetFields()
                      setTemplateModalVisible(true)
                    }}
                    style={{ marginBottom: 16 }}
                  >
                    {t('email.addTemplate') || '添加模板'}
                  </Button>
                  <Table
                    dataSource={templates}
                    columns={templateColumns}
                    rowKey="id"
                    loading={loadingTemplates}
                    pagination={{
                      pageSize: templatePageSize,
                      onShowSizeChange: (current, size) => setTemplatePageSize(size),
                      showSizeChanger: true,
                      pageSizeOptions: ['10', '20', '50', '100'],
                      showQuickJumper: true,
                      showTotal: (total) => t('common.total', { count: total }),
                    }}
                  />
                </div>
              ),
            },
          ]}
        />
      </div>

      {/* Configuration Modal */}
      <Modal
        title={
          editingConfig
            ? t('email.editConfiguration') || '编辑邮件配置'
            : t('email.addConfiguration') || '添加邮件配置'
        }
        open={configModalVisible}
        onOk={handleConfigSave}
        onCancel={() => {
          setConfigModalVisible(false)
          setEditingConfig(null)
          form.resetFields()
        }}
        width={700}
        confirmLoading={saveConfigMutation.isPending}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item label={t('email.provider') || '提供商'}>
            <Select
              value={provider}
              onChange={setProvider}
              disabled={!!editingConfig}
            >
              <Option value="smtp">SMTP</Option>
              <Option value="mailgun">Mailgun</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="from_email"
            label={t('email.fromEmail') || '发件人邮箱'}
            rules={[
              { required: true, message: t('common.required') },
              { type: 'email', message: t('email.invalidEmail') },
            ]}
          >
            <Input placeholder={t('email.fromEmailPlaceholder')} />
          </Form.Item>

          <Form.Item
            name="from_name"
            label={t('email.fromName') || '发件人名称'}
            rules={[{ required: true, message: t('common.required') }]}
          >
            <Input placeholder={t('email.fromNamePlaceholder')} />
          </Form.Item>

          {provider === 'smtp' ? (
            <>
              <Form.Item
                name="smtp_host"
                label={t('email.smtpHost') || 'SMTP 主机'}
                rules={[{ required: true, message: t('common.required') }]}
              >
                <Input placeholder={t('email.smtpHostPlaceholder')} />
              </Form.Item>

              <Form.Item
                name="smtp_port"
                label={t('email.smtpPort') || 'SMTP 端口'}
                rules={[{ required: true, message: t('common.required') }]}
              >
                <InputNumber style={{ width: '100%' }} placeholder={t('email.smtpPortPlaceholder')} />
              </Form.Item>

              <Form.Item
                name="smtp_username"
                label={t('email.smtpUsername') || 'SMTP 用户名'}
                rules={[{ required: true, message: t('common.required') }]}
              >
                <Input placeholder={t('email.smtpUsernamePlaceholder')} />
              </Form.Item>

              <Form.Item
                name="smtp_password"
                label={t('email.smtpPassword') || 'SMTP 密码'}
                rules={[{ required: !editingConfig, message: t('common.required') }]}
              >
                <Input.Password
                  placeholder={editingConfig ? t('email.leaveEmptyIfNotChange') : t('email.enterPassword')}
                />
              </Form.Item>

              <Form.Item name="smtp_use_tls" label={t('email.useTLS')} valuePropName="checked">
                <Switch defaultChecked />
              </Form.Item>

              <Form.Item name="smtp_use_ssl" label={t('email.useSSL')} valuePropName="checked">
                <Switch />
              </Form.Item>
            </>
          ) : (
            <>
              <Form.Item
                name="mailgun_api_key"
                label="Mailgun API Key"
                rules={[{ required: !editingConfig, message: t('common.required') }]}
              >
                <Input.Password
                  placeholder={editingConfig ? t('email.leaveEmptyIfNotChange') : t('email.enterAPIKey')}
                />
              </Form.Item>

              <Form.Item
                name="mailgun_domain"
                label="Mailgun Domain"
                rules={[{ required: true, message: t('common.required') }]}
              >
                <Input placeholder={t('email.mailgunDomainPlaceholder')} />
              </Form.Item>

              <Form.Item name="mailgun_base_url" label="Mailgun Base URL">
                <Input placeholder={t('email.mailgunBaseUrlPlaceholder')} />
              </Form.Item>
            </>
          )}

          <Form.Item name="is_active" label={t('common.active')} valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>

      {/* Template Modal */}
      <Modal
        title={
          editingTemplate
            ? t('email.editTemplate') || '编辑邮件模板'
            : t('email.addTemplate') || '添加邮件模板'
        }
        open={templateModalVisible}
        onOk={handleTemplateSave}
        onCancel={() => {
          setTemplateModalVisible(false)
          setEditingTemplate(null)
          templateForm.resetFields()
          setHtmlContent('')
        }}
        width={900}
        confirmLoading={saveTemplateMutation.isPending}
      >
        <Form form={templateForm} layout="vertical" style={{ marginTop: 16 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="name"
                label={t('email.templateName') || '模板名称'}
                rules={[{ required: true, message: t('common.required') }]}
              >
                <Input placeholder={t('email.templateNamePlaceholder')} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="slug"
                label={t('email.slug') || '标识符'}
                rules={[{ required: true, message: t('common.required') }]}
                tooltip={t('email.slugTooltip')}
              >
                <Input
                  placeholder={t('email.slugPlaceholder')}
                  disabled={!!editingTemplate}
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="subject"
            label={t('email.subject') || '邮件主题'}
            rules={[{ required: true, message: t('common.required') }]}
          >
            <Input placeholder={t('email.subjectPlaceholder')} />
          </Form.Item>

          <Form.Item name="description" label={t('common.description') || '描述'}>
            <TextArea rows={2} placeholder={t('email.descriptionPlaceholder')} />
          </Form.Item>

          <Form.Item
            label={t('email.htmlContent') || 'HTML 内容'}
            required
            tooltip={t('email.htmlContentTooltip')}
          >
            <ReactCodeMirror
              value={htmlContent}
              height="300px"
              extensions={[html()]}
              onChange={(value) => setHtmlContent(value)}
              theme="light"
            />
          </Form.Item>

          <Form.Item name="text_content" label={t('email.textContent') || '纯文本内容'}>
            <TextArea rows={4} placeholder={t('email.textContentPlaceholder')} />
          </Form.Item>

          <Form.Item
            name="variables"
            label={t('email.variables') || '变量列表'}
            tooltip={t('email.variablesTooltip')}
          >
            <Select mode="tags" placeholder={t('email.variablesPlaceholder')} />
          </Form.Item>

          <Form.Item name="is_active" label={t('common.active')} valuePropName="checked">
            <Switch defaultChecked />
          </Form.Item>
        </Form>
      </Modal>

      {/* Test Email Modal */}
      <Modal
        title={t('email.sendTestEmail') || '发送测试邮件'}
        open={testEmailModalVisible}
        onOk={() => {
          form
            .validateFields(['test_email'])
            .then(handleTestEmail)
            .catch(() => {})
        }}
        onCancel={() => setTestEmailModalVisible(false)}
        confirmLoading={testConfigMutation.isPending}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item
            name="test_email"
            label={t('email.testEmail') || '测试邮箱地址'}
            rules={[
              { required: true, message: t('common.required') },
              { type: 'email', message: t('email.invalidEmail') },
            ]}
          >
            <Input placeholder={t('email.testEmailPlaceholder')} />
          </Form.Item>
        </Form>
      </Modal>

      {/* Preview Modal */}
      <Modal
        title={t('email.preview') || '邮件预览'}
        open={previewModalVisible}
        onCancel={() => setPreviewModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setPreviewModalVisible(false)}>
            {t('common.close') || '关闭'}
          </Button>,
        ]}
        width={800}
      >
        {previewContent && (
          <div>
            <div style={{ marginBottom: 16 }}>
              <Text strong>{t('email.subject')}: </Text>
              <Text>{previewContent.subject}</Text>
            </div>
            <div>
              <Text strong>{t('email.content')}: </Text>
              <div
                style={{
                  border: '1px solid #d9d9d9',
                  padding: 16,
                  borderRadius: 4,
                  marginTop: 8,
                  maxHeight: 500,
                  overflow: 'auto',
                }}
                dangerouslySetInnerHTML={{ __html: previewContent.html_content }}
              />
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default EmailManagement
