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
import { formatAWSDate } from '@/utils/awsStyleHelpers'
import { useTranslation } from 'react-i18next'
import { useTableSort } from '@/hooks/useTableSort'

const { TextArea } = Input

const ActorsList = () => {
  const { t } = useTranslation()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingActor, setEditingActor] = useState<any>(null)
  const [form] = Form.useForm()
  const queryClient = useQueryClient()

  // Table sorting
  const { handleTableChange, getSortParams } = useTableSort({
    defaultSortBy: 'created_at',
    defaultSortOrder: 'desc'
  })

  // Fetch actors
  const { data, isLoading } = useQuery({
    queryKey: ['actors', page, pageSize, ...Object.values(getSortParams())],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/actors/', {
        params: {
          page,
          page_size: pageSize,
          ...getSortParams(),
        },
      })
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
      if (editingActor) {
        return await axios.put(`/api/v1/admin/actors/${editingActor.id}/`, values)
      } else {
        return await axios.post('/api/v1/admin/actors/', values)
      }
    },
    onSuccess: () => {
      message.success(editingActor ? '更新成功' : '创建成功')
      setIsModalOpen(false)
      form.resetFields()
      setEditingActor(null)
      queryClient.invalidateQueries({ queryKey: ['actors'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '操作失败')
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await axios.delete(`/api/v1/admin/actors/${id}/`)
    },
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['actors'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '删除失败')
    },
  })

  const showModal = (actor?: any) => {
    if (actor) {
      setEditingActor(actor)
      form.setFieldsValue({
        ...actor,
        birth_date: actor.birth_date ? dayjs(actor.birth_date) : null,
      })
    } else {
      setEditingActor(null)
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
    setEditingActor(null)
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
      sorter: true,
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
      sorter: true,
    },
    {
      title: '出生日期',
      dataIndex: 'birth_date',
      key: 'birth_date',
      sorter: true,
      render: (date: string) => (date ? formatAWSDate(date, 'YYYY-MM-DD') : '-'),
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
      sorter: true,
      render: (date: string) => formatAWSDate(date, 'YYYY-MM-DD HH:mm'),
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
      title="演员管理"
      extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={() => showModal()}>
          添加演员
        </Button>
      }
    >
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
          onChange: (newPage) => setPage(newPage),
          onShowSizeChange: (current, size) => {
            setPageSize(size)
            setPage(1)
          },
          showSizeChanger: true,
          pageSizeOptions: ['10', '20', '50', '100'],
          showQuickJumper: true,
          showTotal: (total) => t('common.total', { count: total }),
        }}
      />

      <Modal
        title={editingActor ? '编辑演员' : '添加演员'}
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
            rules={[{ required: true, message: '请输入演员姓名' }]}
          >
            <Input placeholder="请输入演员姓名" />
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
            <TextArea rows={4} placeholder="请输入演员简介" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}

export default ActorsList
