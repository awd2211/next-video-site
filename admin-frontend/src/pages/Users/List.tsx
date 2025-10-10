import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Table, Tag, Space, Button, Input, message, Modal, Typography } from 'antd'
import {
  UserOutlined,
  StopOutlined,
  CheckCircleOutlined,
  CrownOutlined,
  SearchOutlined,
} from '@ant-design/icons'
import axios from '@/utils/axios'
import dayjs from 'dayjs'
import { useDebounce } from '@/hooks/useDebounce'

const { Title } = Typography

const UserList = () => {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  
  // Debounce search to reduce API calls
  const debouncedSearch = useDebounce(search, 500)

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['admin-users', page, debouncedSearch],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/users', {
        params: { page, page_size: 20, search: debouncedSearch },
      })
      return response.data
    },
  })

  const handleBanUser = async (userId: number, username: string, isActive: boolean) => {
    Modal.confirm({
      title: `确认${isActive ? '封禁' : '解封'}用户`,
      content: `您确定要${isActive ? '封禁' : '解封'}用户 "${username}" 吗？`,
      okText: '确认',
      cancelText: '取消',
      okButtonProps: { danger: isActive },
      onOk: async () => {
        try {
          await axios.put(
            `/api/v1/admin/users/${userId}/ban`,
            {}
          )
          message.success(`用户${isActive ? '封禁' : '解封'}成功`)
          refetch()
        } catch (error: any) {
          message.error(error.response?.data?.detail || '操作失败')
        }
      },
    })
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      render: (text: string) => (
        <Space>
          <UserOutlined />
          <span>{text}</span>
        </Space>
      ),
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: '全名',
      dataIndex: 'full_name',
      key: 'full_name',
      render: (text: string) => text || '-',
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (isActive: boolean) =>
        isActive ? (
          <Tag color="green" icon={<CheckCircleOutlined />}>
            正常
          </Tag>
        ) : (
          <Tag color="red" icon={<StopOutlined />}>
            已封禁
          </Tag>
        ),
    },
    {
      title: 'VIP',
      dataIndex: 'is_vip',
      key: 'is_vip',
      width: 100,
      render: (isVip: boolean, record: any) => {
        if (!isVip) return <Tag>普通</Tag>
        const isExpired = record.vip_expires_at && dayjs(record.vip_expires_at).isBefore(dayjs())
        return (
          <Tag color="gold" icon={<CrownOutlined />}>
            {isExpired ? 'VIP(已过期)' : 'VIP'}
          </Tag>
        )
      },
    },
    {
      title: '注册时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '最后登录',
      dataIndex: 'last_login_at',
      key: 'last_login_at',
      width: 180,
      render: (date: string) => (date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_: any, record: any) => (
        <Space>
          <Button
            type={record.is_active ? 'default' : 'primary'}
            danger={record.is_active}
            size="small"
            icon={record.is_active ? <StopOutlined /> : <CheckCircleOutlined />}
            onClick={() => handleBanUser(record.id, record.username, record.is_active)}
          >
            {record.is_active ? '封禁' : '解封'}
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2} style={{ margin: 0 }}>
          用户管理
        </Title>
        <Input.Search
          placeholder="搜索用户名或邮箱"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onSearch={setSearch}
          allowClear
          style={{ width: 300 }}
          prefix={<SearchOutlined />}
        />
      </div>

      <Table
        columns={columns}
        dataSource={data?.items}
        loading={isLoading}
        rowKey="id"
        pagination={{
          current: page,
          pageSize: 20,
          total: data?.total,
          onChange: setPage,
          showTotal: (total) => `共 ${total} 个用户`,
          showSizeChanger: false,
        }}
        scroll={{ x: 1200 }}
      />
    </div>
  )
}

export default UserList
