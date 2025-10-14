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
import { useTranslation } from 'react-i18next'
import { useTableSort } from '@/hooks/useTableSort'
import { createFormRules } from '@/utils/formRules'
import { VALIDATION_LIMITS } from '@/utils/validationConfig'
import '@/styles/page-layout.css'

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
  const { t } = useTranslation()
  const formRules = createFormRules(t)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingAnnouncement, setEditingAnnouncement] = useState<Announcement | null>(null)
  const [filterType, setFilterType] = useState<string | undefined>(undefined)
  const [filterActive, setFilterActive] = useState<boolean | undefined>(undefined)
  const [form] = Form.useForm()
  const queryClient = useQueryClient()

  // Table sorting
  const { handleTableChange, getSortParams } = useTableSort({
    defaultSortBy: 'created_at',
    defaultSortOrder: 'desc'
  })

  // Fetch announcements
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['announcements', page, pageSize, filterType, filterActive, ...Object.values(getSortParams())],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/announcements/announcements', {
        params: {
          page,
          page_size: pageSize,
          type: filterType,
          is_active: filterActive,
          ...getSortParams(),
        },
      })
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
      sorter: true,
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      sorter: true,
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
        if (!mapping) return <AWSTag type="default">{type}</AWSTag>
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
      sorter: true,
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
    <div className="page-container">
      {/* Page Header */}
      <div className="page-header">
        <div className="page-header-content">
          <div className="page-header-left">
            <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 600 }}>公告管理</h2>
            <Space style={{ marginLeft: 16 }}>
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
            </Space>
          </div>
          <div className="page-header-right">
            <Button onClick={() => refetch()}>刷新</Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新建公告
            </Button>
          </div>
        </div>
      </div>

      {/* Page Content */}
      <div className="page-content">
        <div className="table-container">
          <Table
          columns={columns}
          dataSource={data?.items || []}
          rowKey="id"
          loading={isLoading}
          onChange={(pagination, filters, sorter) => handleTableChange(sorter)}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: data?.total || 0,
            onShowSizeChange: (current, size) => {
              setPageSize(size)
              setPage(1)
            },
            showSizeChanger: true,
            pageSizeOptions: ['10', '20', '50', '100'],
            showQuickJumper: true,
            showTotal: (total) => t('common.total', { count: total }),
            onChange: (newPage) => setPage(newPage),
          }}
          />
        </div>
      </div>

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
            label={t('announcement.title')}
            name="title"
            rules={[
              formRules.required(t('announcement.title')),
              formRules.maxLength(VALIDATION_LIMITS.ANNOUNCEMENT_TITLE.max)
            ]}
          >
            <Input 
              placeholder={t('announcement.titlePlaceholder')} 
              maxLength={VALIDATION_LIMITS.ANNOUNCEMENT_TITLE.max} 
              showCount
            />
          </Form.Item>

          <Form.Item
            label={t('announcement.content')}
            name="content"
            rules={[
              formRules.required(t('announcement.content')),
              formRules.maxLength(VALIDATION_LIMITS.ANNOUNCEMENT_CONTENT.max)
            ]}
          >
            <TextArea
              rows={6}
              placeholder={t('announcement.contentPlaceholder')}
              showCount
              maxLength={VALIDATION_LIMITS.ANNOUNCEMENT_CONTENT.max}
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label={t('announcement.type')}
                name="type"
                rules={[formRules.required(t('announcement.type'))]}
              >
                <Select>
                  <Select.Option value="info">
                    <Tag color="blue">{t('announcement.info')}</Tag>
                  </Select.Option>
                  <Select.Option value="warning">
                    <Tag color="orange">{t('announcement.warning')}</Tag>
                  </Select.Option>
                  <Select.Option value="success">
                    <Tag color="green">{t('announcement.success')}</Tag>
                  </Select.Option>
                  <Select.Option value="error">
                    <Tag color="red">{t('announcement.error')}</Tag>
                  </Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label={t('announcement.displayTime')} name="dateRange">
                <RangePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label={t('announcement.isActive')} name="is_active" valuePropName="checked">
                <Switch checkedChildren={t('common.active')} unCheckedChildren={t('common.inactive')} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label={t('announcement.isPinned')} name="is_pinned" valuePropName="checked">
                <Switch checkedChildren={t('common.pinned')} unCheckedChildren={t('common.unpinned')} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  )
}

export default AnnouncementsList
