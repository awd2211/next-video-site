import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Card,
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  DatePicker,
  Tag,
  Popconfirm,
  message,
  Row,
  Col,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  PushpinOutlined,
  SoundOutlined,
} from '@ant-design/icons'
import axios from '@/utils/axios'
import dayjs from 'dayjs'
import { formatAWSDate, AWSTag } from '@/utils/awsStyleHelpers'

const { RangePicker } = DatePicker
const { TextArea } = Input

interface Announcement {
  id: number
  title: string
  content: string
  type: string
  is_active: boolean
  is_pinned: boolean
  start_date?: string
  end_date?: string
  created_at: string
  updated_at?: string
}

const AnnouncementsList = () => {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingAnnouncement, setEditingAnnouncement] = useState<Announcement | null>(null)
  const [filterType, setFilterType] = useState<string | undefined>(undefined)
  const [filterActive, setFilterActive] = useState<boolean | undefined>(undefined)
  const [form] = Form.useForm()
  const queryClient = useQueryClient()

  // Fetch announcements
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['announcements', page, pageSize, filterType, filterActive],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      })
      if (filterType) params.append('type', filterType)
      if (filterActive !== undefined) params.append('is_active', filterActive.toString())

      const response = await axios.get(`/api/v1/admin/announcements/announcements?${params}`)
      return response.data
    },
  })

  // Create/Update mutation
  const saveMutation = useMutation({
    mutationFn: async (values: any) => {
      const payload = {
        ...values,
        start_date: values.dateRange?.[0]?.toISOString() || null,
        end_date: values.dateRange?.[1]?.toISOString() || null,
      }
      delete payload.dateRange

      if (editingAnnouncement) {
        await axios.put(
          `/api/v1/admin/announcements/announcements/${editingAnnouncement.id}`,
          payload
        )
      } else {
        await axios.post('/api/v1/admin/announcements/announcements', payload)
      }
    },
    onSuccess: () => {
      message.success(editingAnnouncement ? '公告已更新' : '公告已创建')
      setModalVisible(false)
      setEditingAnnouncement(null)
      form.resetFields()
      queryClient.invalidateQueries({ queryKey: ['announcements'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '操作失败')
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await axios.delete(`/api/v1/admin/announcements/announcements/${id}`)
    },
    onSuccess: () => {
      message.success('公告已删除')
      queryClient.invalidateQueries({ queryKey: ['announcements'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '删除失败')
    },
  })

  // Toggle active mutation
  const toggleActiveMutation = useMutation({
    mutationFn: async (id: number) => {
      await axios.patch(`/api/v1/admin/announcements/announcements/${id}/toggle-active`)
    },
    onSuccess: () => {
      message.success('状态已更新')
      queryClient.invalidateQueries({ queryKey: ['announcements'] })
    },
  })

  // Toggle pinned mutation
  const togglePinnedMutation = useMutation({
    mutationFn: async (id: number) => {
      await axios.patch(`/api/v1/admin/announcements/announcements/${id}/toggle-pinned`)
    },
    onSuccess: () => {
      message.success('置顶状态已更新')
      queryClient.invalidateQueries({ queryKey: ['announcements'] })
    },
  })

  const handleEdit = (announcement: Announcement) => {
    setEditingAnnouncement(announcement)
    form.setFieldsValue({
      ...announcement,
      dateRange:
        announcement.start_date && announcement.end_date
          ? [dayjs(announcement.start_date), dayjs(announcement.end_date)]
          : null,
    })
    setModalVisible(true)
  }

  const handleAdd = () => {
    setEditingAnnouncement(null)
    form.resetFields()
    form.setFieldsValue({
      type: 'info',
      is_active: true,
      is_pinned: false,
    })
    setModalVisible(true)
  }

  const handleDelete = (id: number) => {
    deleteMutation.mutate(id)
  }

  const handleSubmit = () => {
    form.validateFields().then((values) => {
      saveMutation.mutate(values)
    })
  }

  const typeMapping: Record<string, { label: string; type: 'info' | 'warning' | 'success' | 'error' }> = {
    info: { label: '信息', type: 'info' },
    warning: { label: '警告', type: 'warning' },
    success: { label: '成功', type: 'success' },
    error: { label: '错误', type: 'error' },
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      render: (text: string, record: Announcement) => (
        <Space>
          {record.is_pinned && (
            <PushpinOutlined style={{ color: '#d13212', fontSize: 16 }} />
          )}
          {text}
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: string) => {
        const mapping = typeMapping[type]
        return <AWSTag type={mapping.type}>{mapping.label}</AWSTag>
      },
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (is_active: boolean, record: Announcement) => (
        <Switch
          checked={is_active}
          onChange={() => toggleActiveMutation.mutate(record.id)}
          checkedChildren="启用"
          unCheckedChildren="禁用"
        />
      ),
    },
    {
      title: '显示时间',
      key: 'display_period',
      width: 200,
      render: (_: any, record: Announcement) => {
        if (record.start_date && record.end_date) {
          return (
            <span style={{ fontFamily: 'Monaco, Menlo, Consolas, monospace', fontSize: '13px', color: '#37352f' }}>
              {dayjs(record.start_date).format('YYYY-MM-DD')} ~ {dayjs(record.end_date).format('YYYY-MM-DD')}
            </span>
          )
        }
        return <span style={{ fontFamily: 'Monaco, Menlo, Consolas, monospace', color: '#787774', fontSize: '13px' }}>永久</span>
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => formatAWSDate(date, 'YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_: any, record: Announcement) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<PushpinOutlined />}
            onClick={() => togglePinnedMutation.mutate(record.id)}
            style={{ color: record.is_pinned ? '#d13212' : undefined }}
          >
            {record.is_pinned ? '取消置顶' : '置顶'}
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除此公告吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Card>
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新建公告
            </Button>
          </Col>
          <Col flex="auto">
            <Space style={{ float: 'right' }}>
              <Select
                placeholder="类型"
                style={{ width: 120 }}
                allowClear
                value={filterType}
                onChange={setFilterType}
              >
                <Select.Option value="info">信息</Select.Option>
                <Select.Option value="warning">警告</Select.Option>
                <Select.Option value="success">成功</Select.Option>
                <Select.Option value="error">错误</Select.Option>
              </Select>
              <Select
                placeholder="状态"
                style={{ width: 120 }}
                allowClear
                value={filterActive}
                onChange={setFilterActive}
              >
                <Select.Option value={true}>启用</Select.Option>
                <Select.Option value={false}>禁用</Select.Option>
              </Select>
              <Button onClick={() => refetch()}>刷新</Button>
            </Space>
          </Col>
        </Row>

        <Table
          columns={columns}
          dataSource={data?.items || []}
          rowKey="id"
          loading={isLoading}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: data?.total || 0,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (newPage, newPageSize) => {
              setPage(newPage)
              setPageSize(newPageSize)
            },
          }}
        />
      </Card>

      <Modal
        title={
          <Space>
            <SoundOutlined />
            {editingAnnouncement ? '编辑公告' : '新建公告'}
          </Space>
        }
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false)
          setEditingAnnouncement(null)
          form.resetFields()
        }}
        onOk={handleSubmit}
        confirmLoading={saveMutation.isPending}
        width={700}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 24 }}>
          <Form.Item
            label="标题"
            name="title"
            rules={[{ required: true, message: '请输入标题' }]}
          >
            <Input placeholder="请输入公告标题" maxLength={200} />
          </Form.Item>

          <Form.Item
            label="内容"
            name="content"
            rules={[{ required: true, message: '请输入内容' }]}
          >
            <TextArea
              rows={6}
              placeholder="请输入公告内容"
              showCount
              maxLength={2000}
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="类型"
                name="type"
                rules={[{ required: true, message: '请选择类型' }]}
              >
                <Select>
                  <Select.Option value="info">
                    <Tag color="blue">信息</Tag>
                  </Select.Option>
                  <Select.Option value="warning">
                    <Tag color="orange">警告</Tag>
                  </Select.Option>
                  <Select.Option value="success">
                    <Tag color="green">成功</Tag>
                  </Select.Option>
                  <Select.Option value="error">
                    <Tag color="red">错误</Tag>
                  </Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="显示时间" name="dateRange">
                <RangePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="是否启用" name="is_active" valuePropName="checked">
                <Switch checkedChildren="启用" unCheckedChildren="禁用" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="是否置顶" name="is_pinned" valuePropName="checked">
                <Switch checkedChildren="置顶" unCheckedChildren="不置顶" />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  )
}

export default AnnouncementsList
