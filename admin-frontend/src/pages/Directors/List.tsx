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
  message,
  Popconfirm,
  DatePicker,
  Select,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
} from '@ant-design/icons'
import axios from '@/utils/axios'
import dayjs from 'dayjs'

const { TextArea } = Input

const DirectorsList = () => {
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingDirector, setEditingDirector] = useState<any>(null)
  const [form] = Form.useForm()
  const queryClient = useQueryClient()

  // Fetch directors
  const { data, isLoading } = useQuery({
    queryKey: ['directors', page, pageSize],
    queryFn: async () => {
      const response = await axios.get(
        `/api/v1/admin/directors/?page=${page}&page_size=${pageSize}`
      )
      return response.data
    },
  })

  // Fetch countries for select
  const { data: countries } = useQuery({
    queryKey: ['countries'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/countries')
      return response.data
    },
  })

  // Create/Update mutation
  const saveMutation = useMutation({
    mutationFn: async (values: any) => {
      if (editingDirector) {
        return await axios.put(`/api/v1/admin/directors/${editingDirector.id}/`, values)
      } else {
        return await axios.post('/api/v1/admin/directors/', values)
      }
    },
    onSuccess: () => {
      message.success(editingDirector ? '更新成功' : '创建成功')
      setIsModalOpen(false)
      form.resetFields()
      setEditingDirector(null)
      queryClient.invalidateQueries({ queryKey: ['directors'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '操作失败')
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await axios.delete(`/api/v1/admin/directors/${id}/`)
    },
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['directors'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '删除失败')
    },
  })

  const showModal = (director?: any) => {
    if (director) {
      setEditingDirector(director)
      form.setFieldsValue({
        ...director,
        birth_date: director.birth_date ? dayjs(director.birth_date) : null,
      })
    } else {
      setEditingDirector(null)
      form.resetFields()
    }
    setIsModalOpen(true)
  }

  const handleOk = () => {
    form.validateFields().then((values) => {
      const submitData = {
        ...values,
        birth_date: values.birth_date ? values.birth_date.format('YYYY-MM-DD') : null,
      }
      saveMutation.mutate(submitData)
    })
  }

  const handleCancel = () => {
    setIsModalOpen(false)
    form.resetFields()
    setEditingDirector(null)
  }

  const handleDelete = (id: number) => {
    deleteMutation.mutate(id)
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '头像',
      dataIndex: 'avatar',
      key: 'avatar',
      width: 80,
      render: (avatar: string, record: any) => (
        avatar ? (
          <img src={avatar} alt={record.name} className="w-12 h-12 rounded-full object-cover" />
        ) : (
          <div className="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center">
            <span className="text-gray-400 text-xs">无</span>
          </div>
        )
      ),
    },
    {
      title: '姓名',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '出生日期',
      dataIndex: 'birth_date',
      key: 'birth_date',
      render: (date: string) => (date ? dayjs(date).format('YYYY-MM-DD') : '-'),
    },
    {
      title: '国籍',
      dataIndex: 'country_id',
      key: 'country_id',
      render: (countryId: number) => {
        const country = countries?.find((c: any) => c.id === countryId)
        return country?.name || '-'
      },
    },
    {
      title: '简介',
      dataIndex: 'biography',
      key: 'biography',
      ellipsis: true,
      render: (bio: string) => bio || '-',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: any) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => showModal(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <Card
      title="导演管理"
      extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={() => showModal()}>
          添加导演
        </Button>
      }
    >
      <Table
        columns={columns}
        dataSource={data?.items || []}
        rowKey="id"
        loading={isLoading}
        pagination={{
          current: page,
          pageSize,
          total: data?.total || 0,
          onChange: (newPage) => setPage(newPage),
          showSizeChanger: false,
          showTotal: (total) => `共 ${total} 条`,
        }}
      />

      <Modal
        title={editingDirector ? '编辑导演' : '添加导演'}
        open={isModalOpen}
        onOk={handleOk}
        onCancel={handleCancel}
        confirmLoading={saveMutation.isPending}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="姓名"
            rules={[{ required: true, message: '请输入导演姓名' }]}
          >
            <Input placeholder="请输入导演姓名" />
          </Form.Item>

          <Form.Item name="avatar" label="头像URL">
            <Input placeholder="请输入头像图片链接" />
          </Form.Item>

          <Form.Item name="birth_date" label="出生日期">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item name="country_id" label="国籍">
            <Select placeholder="请选择国籍" allowClear>
              {countries?.map((country: any) => (
                <Select.Option key={country.id} value={country.id}>
                  {country.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="biography" label="简介">
            <TextArea rows={4} placeholder="请输入导演简介" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}

export default DirectorsList
