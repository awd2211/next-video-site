import { useState } from 'react'
import {
  Card,
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Switch,
  Tag,
  message,
  Tooltip,
  Drawer,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  CodeOutlined,
} from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from '@/utils/axios'
import dayjs from 'dayjs'

const { TextArea } = Input

const EmailTemplates = () => {
  const [form] = Form.useForm()
  const [modalVisible, setModalVisible] = useState(false)
  const [previewVisible, setPreviewVisible] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState<any>(null)
  const [previewHtml, setPreviewHtml] = useState('')
  const queryClient = useQueryClient()  // Fetch templates
  const { data: templates, isLoading } = useQuery({
    queryKey: ['email-templates'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/email/templates')
      return response.data
    },
  })

  // Create/Update mutation
  const saveMutation = useMutation({
    mutationFn: async (values: any) => {
      if (editingTemplate) {
        await axios.put(
          `/api/v1/admin/email/templates/${editingTemplate.id}`,
          values
        )
      } else {
        await axios.post('/api/v1/admin/email/templates', values)
      }
    },
    onSuccess: () => {
      message.success(editingTemplate ? '模板已更新' : '模板已创建')
      queryClient.invalidateQueries({ queryKey: ['email-templates'] })
      handleCloseModal()
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '操作失败')
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await axios.delete(`/api/v1/admin/email/templates/${id}`)
    },
    onSuccess: () => {
      message.success('模板已删除')
      queryClient.invalidateQueries({ queryKey: ['email-templates'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '删除失败')
    },
  })

  const handleCreate = () => {
    setEditingTemplate(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (template: any) => {
    setEditingTemplate(template)
    form.setFieldsValue(template)
    setModalVisible(true)
  }

  const handleCloseModal = () => {
    setModalVisible(false)
    setEditingTemplate(null)
    form.resetFields()
  }

  const handleDelete = (id: number, name: string) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除模板 "${name}" 吗？`,
      onOk: () => deleteMutation.mutate(id),
    })
  }

  const handlePreview = (template: any) => {
    setPreviewHtml(template.html_content)
    setPreviewVisible(true)
  }

  const onFinish = (values: any) => {
    // Convert variables from string to array
    if (values.variables && typeof values.variables === 'string') {
      values.variables = values.variables.split(',').map((v: string) => v.trim()).filter(Boolean)
    }
    saveMutation.mutate(values)
  }

  const columns = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
    },
    {
      title: 'Slug',
      dataIndex: 'slug',
      key: 'slug',
      width: 150,
      render: (slug: string) => <Tag color="blue">{slug}</Tag>,
    },
    {
      title: '主题',
      dataIndex: 'subject',
      key: 'subject',
      ellipsis: true,
    },
    {
      title: '变量',
      dataIndex: 'variables',
      key: 'variables',
      width: 200,
      render: (variables: string[]) => (
        <Space size={4} wrap>
          {variables?.map((v) => (
            <Tag key={v} color="geekblue">
              {`{{${v}}}`}
            </Tag>
          ))}
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 80,
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'default'}>{isActive ? '启用' : '禁用'}</Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right' as const,
      render: (_: any, record: any) => (
        <Space size="small">
          <Tooltip title="预览">
            <Button
              size="small"
              icon={<EyeOutlined />}
              onClick={() => handlePreview(record)}
            />
          </Tooltip>
          <Button size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Button
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id, record.name)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Card
        title="邮件模板管理"
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            创建模板
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={templates || []}
          rowKey="id"
          loading={isLoading}
          scroll={{ x: 1200 }}
          pagination={{
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>

      <Modal
        title={editingTemplate ? '编辑模板' : '创建模板'}
        open={modalVisible}
        onCancel={handleCloseModal}
        width={800}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={onFinish}>
          <Form.Item
            name="name"
            label="模板名称"
            rules={[{ required: true, message: '请输入模板名称' }]}
          >
            <Input placeholder="例如：欢迎邮件" />
          </Form.Item>

          <Form.Item
            name="slug"
            label="Slug（唯一标识）"
            rules={[
              { required: true, message: '请输入Slug' },
              {
                pattern: /^[a-z0-9-]+$/,
                message: '只能包含小写字母、数字和连字符',
              },
            ]}
          >
            <Input placeholder="例如：welcome-email" disabled={!!editingTemplate} />
          </Form.Item>

          <Form.Item
            name="subject"
            label="邮件主题"
            rules={[{ required: true, message: '请输入邮件主题' }]}
          >
            <Input placeholder="可以使用变量，例如：欢迎加入 {{site_name}}" />
          </Form.Item>

          <Form.Item
            name="html_content"
            label="HTML 内容"
            rules={[{ required: true, message: '请输入HTML内容' }]}
          >
            <TextArea
              rows={10}
              placeholder="使用变量格式：{{variable_name}}"
              style={{ fontFamily: 'monospace' }}
            />
          </Form.Item>

          <Form.Item name="text_content" label="纯文本内容（可选）">
            <TextArea rows={6} placeholder="纯文本版本，用于不支持HTML的邮件客户端" />
          </Form.Item>

          <Form.Item
            name="variables"
            label="可用变量"
            tooltip="逗号分隔，例如：user_name, video_title, link"
          >
            <Input placeholder="user_name, video_title, link" />
          </Form.Item>

          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="模板用途说明" />
          </Form.Item>

          <Form.Item name="is_active" label="启用模板" valuePropName="checked">
            <Switch defaultChecked />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={saveMutation.isPending}>
                {editingTemplate ? '更新' : '创建'}
              </Button>
              <Button onClick={handleCloseModal}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      <Drawer
        title="模板预览"
        placement="right"
        width={800}
        open={previewVisible}
        onClose={() => setPreviewVisible(false)}
      >
        <div
          style={{
            border: '1px solid #d9d9d9',
            borderRadius: 4,
            padding: 16,
            backgroundColor: '#fff',
          }}
          dangerouslySetInnerHTML={{ __html: previewHtml }}
        />
      </Drawer>
    </div>
  )
}

export default EmailTemplates
