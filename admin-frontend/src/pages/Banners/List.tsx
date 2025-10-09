import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
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
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  UploadOutlined,
} from '@ant-design/icons'
import axios from '@/utils/axios'
import dayjs from 'dayjs'

const { TextArea } = Input
const { Option } = Select
const { RangePicker } = DatePicker

const BannersList = () => {
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingBanner, setEditingBanner] = useState<any>(null)
  const [form] = Form.useForm()
  const queryClient = useQueryClient()
  const [uploading, setUploading] = useState(false)
  const [imageUrl, setImageUrl] = useState<string>('')

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
    queryKey: ['banners', page, pageSize],
    queryFn: async () => {
      const response = await axios.get(
        `/api/v1/admin/banners/banners?page=${page}&page_size=${pageSize}`
      )
      return response.data
    },
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
      width: 200,
      render: (_: any, record: any) => {
        if (!record.start_date && !record.end_date) return '永久'
        const start = record.start_date ? dayjs(record.start_date).format('YYYY-MM-DD') : '∞'
        const end = record.end_date ? dayjs(record.end_date).format('YYYY-MM-DD') : '∞'
        return `${start} ~ ${end}`
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      fixed: 'right' as const,
      render: (_: any, record: any) => (
        <Space>
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

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>Banner管理</h2>

      <Card
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            创建Banner
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={data?.items || []}
          rowKey="id"
          loading={isLoading}
          scroll={{ x: 1200 }}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: data?.total || 0,
            showSizeChanger: false,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
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
