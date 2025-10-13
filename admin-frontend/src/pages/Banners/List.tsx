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
  DatePicker,
  InputNumber,
  Upload,
  message,
  Switch,
  Image,
  Tag,
  Statistic,
  Row,
  Col,
  Tooltip,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  UploadOutlined,
  DownloadOutlined,
  EyeOutlined,
  FilterOutlined,
  ReloadOutlined,
} from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import axios from '@/utils/axios'
import dayjs from 'dayjs'
import { exportToCSV } from '@/utils/exportUtils'
import { formatAWSDate, formatAWSNumber } from '@/utils/awsStyleHelpers'
import { BannerPreviewButton } from './BannerPreview'

const { TextArea } = Input
const { Option } = Select
const { RangePicker } = DatePicker

const BannersList = () => {
  const { t } = useTranslation()
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingBanner, setEditingBanner] = useState<any>(null)
  const [form] = Form.useForm()
  const queryClient = useQueryClient()
  const [uploading, setUploading] = useState(false)
  const [imageUrl, setImageUrl] = useState<string>('')
  const [selectedRowKeys, setSelectedRowKeys] = useState<number[]>([])
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined)

  // Handle image upload
  const handleUpload = async (options: any) => {
    const { file, onSuccess, onError } = options
    const formData = new FormData()
    formData.append('file', file)

    setUploading(true)
    try {
      const response = await axios.post('/api/v1/admin/banners/banners/upload-image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      const url = response.data.image_url
      setImageUrl(url)
      form.setFieldsValue({ image_url: url })
      message.success('图片上传成功')
      onSuccess(response.data, file)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '上传失败')
      onError(error)
    } finally {
      setUploading(false)
    }
  }

  // Fetch banners
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['banners', page, pageSize, statusFilter],
    queryFn: async () => {
      let url = `/api/v1/admin/banners/banners?page=${page}&page_size=${pageSize}`
      if (statusFilter) {
        url += `&status=${statusFilter}`
      }
      const response = await axios.get(url)
      return response.data
    },
    placeholderData: (previousData) => previousData,
  })

  // Create/Update mutation
  const saveMutation = useMutation({
    mutationFn: async (values: any) => {
      if (editingBanner) {
        await axios.put(`/api/v1/admin/banners/banners/${editingBanner.id}`, values)
      } else {
        await axios.post('/api/v1/admin/banners/banners', values)
      }
    },
    onSuccess: () => {
      message.success(editingBanner ? 'Banner已更新' : 'Banner已创建')
      queryClient.invalidateQueries({ queryKey: ['banners'] })
      handleCloseModal()
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '操作失败')
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await axios.delete(`/api/v1/admin/banners/banners/${id}`)
    },
    onSuccess: () => {
      message.success('Banner已删除')
      queryClient.invalidateQueries({ queryKey: ['banners'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '删除失败')
    },
  })

  // Update status mutation
  const updateStatusMutation = useMutation({
    mutationFn: async ({ id, status }: { id: number; status: string }) => {
      await axios.put(`/api/v1/admin/banners/banners/${id}/status?status=${status}`)
    },
    onSuccess: () => {
      message.success('状态已更新')
      queryClient.invalidateQueries({ queryKey: ['banners'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '更新失败')
    },
  })

  // Batch enable mutation
  const batchEnableMutation = useMutation({
    mutationFn: async (ids: number[]) => {
      await axios.put('/api/v1/admin/banners/batch/enable', { ids })
    },
    onSuccess: () => {
      message.success(t('message.success'))
      setSelectedRowKeys([])
      queryClient.invalidateQueries({ queryKey: ['banners'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('message.failed'))
    },
  })

  // Batch disable mutation
  const batchDisableMutation = useMutation({
    mutationFn: async (ids: number[]) => {
      await axios.put('/api/v1/admin/banners/batch/disable', { ids })
    },
    onSuccess: () => {
      message.success(t('message.success'))
      setSelectedRowKeys([])
      queryClient.invalidateQueries({ queryKey: ['banners'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('message.failed'))
    },
  })

  const handleBatchEnable = () => {
    if (selectedRowKeys.length === 0) {
      message.warning(t('message.pleaseSelect'))
      return
    }
    Modal.confirm({
      title: t('banner.batchEnable'),
      content: `${t('common.confirm')} ${selectedRowKeys.length} ${t('menu.banners')}?`,
      okText: t('common.confirm'),
      cancelText: t('common.cancel'),
      onOk: () => batchEnableMutation.mutate(selectedRowKeys),
    })
  }
  
  const handleBatchDisable = () => {
    if (selectedRowKeys.length === 0) {
      message.warning(t('message.pleaseSelect'))
      return
    }
    Modal.confirm({
      title: t('banner.batchDisable'),
      content: `${t('common.confirm')} ${selectedRowKeys.length} ${t('menu.banners')}?`,
      okText: t('common.confirm'),
      cancelText: t('common.cancel'),
      onOk: () => batchDisableMutation.mutate(selectedRowKeys),
    })
  }

  // Export to CSV
  const handleExport = () => {
    if (!data?.items || data.items.length === 0) {
      message.warning(t('message.noDataToExport'))
      return
    }

    const exportData = data.items.map((item: any) => ({
      ID: item.id,
      [t('banner.title')]: item.title,
      [t('banner.status')]: item.status === 'active' ? t('banner.active') : t('banner.inactive'),
      [t('banner.sortOrder')]: item.sort_order,
      [t('table.createdAt')]: item.created_at,
    }))

    exportToCSV(exportData, 'banners')
    message.success(t('message.exportSuccess'))
  }

  const handleCreate = () => {
    setEditingBanner(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (banner: any) => {
    setEditingBanner(banner)
    setImageUrl(banner.image_url || '')
    form.setFieldsValue({
      ...banner,
      date_range: banner.start_date && banner.end_date
        ? [dayjs(banner.start_date), dayjs(banner.end_date)]
        : null,
    })
    setModalVisible(true)
  }

  const handleCloseModal = () => {
    setModalVisible(false)
    setEditingBanner(null)
    form.resetFields()
    setImageUrl('')
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      const [start_date, end_date] = values.date_range || [null, null]

      const data = {
        ...values,
        start_date: start_date?.toISOString(),
        end_date: end_date?.toISOString(),
        date_range: undefined,
      }

      saveMutation.mutate(data)
    } catch (error) {
      console.error('Validation failed:', error)
    }
  }

  const handleDelete = (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个Banner吗？此操作不可恢复。',
      okText: '确认',
      okType: 'danger',
      cancelText: '取消',
      onOk: () => deleteMutation.mutate(id),
    })
  }

  const handleToggleStatus = (id: number, currentStatus: string) => {
    const newStatus = currentStatus === 'active' ? 'inactive' : 'active'
    updateStatusMutation.mutate({ id, status: newStatus })
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
    },
    {
      title: '预览',
      dataIndex: 'image_url',
      key: 'image_url',
      width: 120,
      render: (url: string) => (
        <Image src={url} alt="banner" width={100} height={50} style={{ objectFit: 'cover' }} />
      ),
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: '链接',
      dataIndex: 'link_url',
      key: 'link_url',
      width: 150,
      ellipsis: true,
      render: (url: string) => url || '-',
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
      render: (order: number) => formatAWSNumber(order),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string, record: any) => (
        <Switch
          checked={status === 'active'}
          onChange={() => handleToggleStatus(record.id, status)}
          checkedChildren="激活"
          unCheckedChildren="停用"
        />
      ),
    },
    {
      title: '显示时间',
      key: 'date_range',
      width: 220,
      render: (_: any, record: any) => {
        if (!record.start_date && !record.end_date) {
          return <span style={{ fontFamily: 'Monaco, Menlo, Consolas, monospace', color: '#787774' }}>永久</span>
        }
        const start = record.start_date ? dayjs(record.start_date).format('YYYY-MM-DD') : '∞'
        const end = record.end_date ? dayjs(record.end_date).format('YYYY-MM-DD') : '∞'
        return (
          <span style={{ fontFamily: 'Monaco, Menlo, Consolas, monospace', color: '#37352f', fontSize: '13px' }}>
            {start} ~ {end}
          </span>
        )
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
      fixed: 'right' as const,
      render: (_: any, record: any) => (
        <Space size="small">
          <BannerPreviewButton banner={record} />
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ]

  const rowSelection = {
    selectedRowKeys,
    onChange: (keys: React.Key[]) => setSelectedRowKeys(keys as number[]),
  }

  // 统计数据
  const activeCount = data?.items?.filter((item: any) => item.status === 'active').length || 0
  const inactiveCount = data?.items?.filter((item: any) => item.status === 'inactive').length || 0

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>{t('menu.banners')}</h2>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card size="small" style={{ borderRadius: 8 }}>
            <Statistic
              title="总横幅数"
              value={data?.total || 0}
              valueStyle={{ color: '#0073bb', fontSize: 28 }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small" style={{ borderRadius: 8 }}>
            <Statistic
              title="激活状态"
              value={activeCount}
              valueStyle={{ color: '#1d8102', fontSize: 28 }}
              suffix={<Tag color="success" style={{ marginLeft: 8 }}>Active</Tag>}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small" style={{ borderRadius: 8 }}>
            <Statistic
              title="停用状态"
              value={inactiveCount}
              valueStyle={{ color: '#d13212', fontSize: 28 }}
              suffix={<Tag color="error" style={{ marginLeft: 8 }}>Inactive</Tag>}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small" style={{ borderRadius: 8 }}>
            <Statistic
              title="当前页"
              value={page}
              valueStyle={{ color: '#37352f', fontSize: 28 }}
              suffix={`/ ${data?.total_pages || 0}`}
            />
          </Card>
        </Col>
      </Row>

      {/* 筛选和操作栏 */}
      <div style={{ marginBottom: 16 }}>
        <Space>
          <Select
            placeholder="按状态筛选"
            allowClear
            style={{ width: 150 }}
            value={statusFilter}
            onChange={(value) => {
              setStatusFilter(value)
              setPage(1)
            }}
          >
            <Option value="active">
              <Tag color="success">激活</Tag>
            </Option>
            <Option value="inactive">
              <Tag color="error">停用</Tag>
            </Option>
          </Select>
          <Tooltip title="刷新数据">
            <Button
              icon={<ReloadOutlined />}
              onClick={() => refetch()}
            >
              刷新
            </Button>
          </Tooltip>
        </Space>
      </div>

      {/* Batch operations */}
      {selectedRowKeys.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <Space>
            <Button
              type="primary"
              onClick={handleBatchEnable}
            >
              {t('banner.batchEnable')} ({selectedRowKeys.length})
            </Button>
            <Button
              onClick={handleBatchDisable}
            >
              {t('banner.batchDisable')} ({selectedRowKeys.length})
            </Button>
            <Button
              icon={<DownloadOutlined />}
              onClick={handleExport}
            >
              {t('video.exportExcel')}
            </Button>
          </Space>
        </div>
      )}

      <Card
        extra={
          <Space>
            {selectedRowKeys.length === 0 && (
              <Button
                icon={<DownloadOutlined />}
                onClick={handleExport}
              >
                {t('video.exportExcel')}
              </Button>
            )}
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
              {t('common.create')} Banner
            </Button>
          </Space>
        }
      >
        <Table
          rowSelection={rowSelection}
          columns={columns}
          dataSource={data?.items || []}
          rowKey="id"
          loading={isLoading}
          scroll={{ x: 1200 }}
          sticky
          pagination={{
            current: page,
            pageSize: pageSize,
            total: data?.total || 0,
            showSizeChanger: false,
            showQuickJumper: true,
            showTotal: (total) => `${t('common.total')} ${total} ${t('common.items')}`,
            onChange: (newPage) => setPage(newPage),
          }}
        />
      </Card>

      <Modal
        title={editingBanner ? '编辑Banner' : '创建Banner'}
        open={modalVisible}
        onCancel={handleCloseModal}
        onOk={handleSubmit}
        confirmLoading={saveMutation.isPending}
        width={700}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="标题"
            name="title"
            rules={[{ required: true, message: '请输入Banner标题' }]}
          >
            <Input placeholder="请输入Banner标题" />
          </Form.Item>

          <Form.Item
            label="图片"
            name="image_url"
            rules={[{ required: true, message: '请上传或输入图片URL' }]}
            extra="建议尺寸：1920x600"
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Upload
                name="file"
                customRequest={handleUpload}
                listType="picture-card"
                showUploadList={false}
                accept="image/jpeg,image/jpg,image/png,image/webp"
              >
                {imageUrl ? (
                  <img src={imageUrl} alt="banner" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                ) : (
                  <div>
                    {uploading ? <div>上传中...</div> : <><UploadOutlined /><div>上传图片</div></>}
                  </div>
                )}
              </Upload>
              <Input
                placeholder="或直接输入图片URL: https://example.com/banner.jpg"
                value={imageUrl}
                onChange={(e) => {
                  setImageUrl(e.target.value)
                  form.setFieldsValue({ image_url: e.target.value })
                }}
              />
            </Space>
          </Form.Item>

          <Form.Item label="链接URL" name="link_url">
            <Input placeholder="https://example.com/video/123" />
          </Form.Item>

          <Form.Item label="关联视频ID" name="video_id">
            <InputNumber placeholder="输入视频ID" style={{ width: '100%' }} min={1} />
          </Form.Item>

          <Form.Item label="描述" name="description">
            <TextArea rows={3} placeholder="Banner描述" />
          </Form.Item>

          <Form.Item label="排序" name="sort_order" initialValue={0}>
            <InputNumber placeholder="数字越大越靠前" style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item label="状态" name="status" initialValue="active">
            <Select>
              <Option value="active">激活</Option>
              <Option value="inactive">停用</Option>
            </Select>
          </Form.Item>

          <Form.Item label="显示时间" name="date_range">
            <RangePicker
              style={{ width: '100%' }}
              showTime
              format="YYYY-MM-DD HH:mm:ss"
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default BannersList
