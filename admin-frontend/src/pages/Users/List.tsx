import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Table, Tag, Space, Button, Input, message, Modal, Typography, Grid } from 'antd'
import {
  UserOutlined,
  StopOutlined,
  CheckCircleOutlined,
  CrownOutlined,
  SearchOutlined,
  DownloadOutlined,
} from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import axios from '@/utils/axios'
import dayjs from 'dayjs'
import { useDebounce } from '@/hooks/useDebounce'
import { exportToCSV } from '@/utils/exportUtils'

const { Title } = Typography

const UserList = () => {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const screens = Grid.useBreakpoint()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [selectedRowKeys, setSelectedRowKeys] = useState<number[]>([])
  
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
    placeholderData: (previousData) => previousData, // Keep previous data while loading
  })

  const handleBanUser = async (userId: number, username: string, isActive: boolean) => {
    Modal.confirm({
      title: `确认${isActive ? '封禁' : '解封'}用户`,
      content: `您确定要${isActive ? '封禁' : '解封'}用户 "${username}" 吗？`,
      okText: t('common.confirm'),
      cancelText: t('common.cancel'),
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
          message.error(error.response?.data?.detail || t('message.failed'))
        }
      },
    })
  }
  
  // Batch ban mutation
  const batchBanMutation = useMutation({
    mutationFn: async (ids: number[]) => {
      await axios.put('/api/v1/admin/users/batch/ban', { ids })
    },
    onSuccess: () => {
      message.success(t('message.success'))
      setSelectedRowKeys([])
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('message.failed'))
    },
  })
  
  // Batch unban mutation
  const batchUnbanMutation = useMutation({
    mutationFn: async (ids: number[]) => {
      await axios.put('/api/v1/admin/users/batch/unban', { ids })
    },
    onSuccess: () => {
      message.success(t('message.success'))
      setSelectedRowKeys([])
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('message.failed'))
    },
  })
  
  const handleBatchBan = () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择用户')
      return
    }
    Modal.confirm({
      title: t('user.batchBan'),
      content: `确定要封禁选中的 ${selectedRowKeys.length} 个用户吗？`,
      okText: t('common.confirm'),
      okType: 'danger',
      onOk: () => batchBanMutation.mutate(selectedRowKeys),
    })
  }
  
  const handleBatchUnban = () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择用户')
      return
    }
    Modal.confirm({
      title: t('user.batchUnban'),
      content: `确定要解封选中的 ${selectedRowKeys.length} 个用户吗？`,
      onOk: () => batchUnbanMutation.mutate(selectedRowKeys),
    })
  }
  
  // Export to CSV
  const handleExport = () => {
    if (!data?.items || data.items.length === 0) {
      message.warning('没有数据可导出')
      return
    }
    
    const exportData = data.items.map((item: any) => ({
      ID: item.id,
      用户名: item.username,
      邮箱: item.email,
      全名: item.full_name || '',
      状态: item.is_active ? '正常' : '已封禁',
      注册时间: item.created_at,
    }))
    
    exportToCSV(exportData, 'users')
    message.success(t('message.success'))
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

  const rowSelection = {
    selectedRowKeys,
    onChange: (keys: React.Key[]) => setSelectedRowKeys(keys as number[]),
  }

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2} style={{ margin: 0 }}>
          {t('menu.users')}
        </Title>
        <Space>
          <Input.Search
            placeholder={t('common.search') + '...'}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onSearch={setSearch}
            loading={isLoading && !!debouncedSearch}
            allowClear
            style={{ width: 300 }}
            prefix={<SearchOutlined />}
          />
          <Button
            icon={<DownloadOutlined />}
            onClick={handleExport}
          >
            {t('video.exportExcel')}
          </Button>
        </Space>
      </div>

      {/* Batch operations */}
      {selectedRowKeys.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <Space>
            <Button
              danger
              onClick={handleBatchBan}
            >
              {t('user.batchBan')} ({selectedRowKeys.length})
            </Button>
            <Button
              type="primary"
              onClick={handleBatchUnban}
            >
              {t('user.batchUnban')} ({selectedRowKeys.length})
            </Button>
          </Space>
        </div>
      )}

      <Table
        rowSelection={rowSelection}
        columns={columns}
        dataSource={data?.items}
        loading={isLoading}
        rowKey="id"
        pagination={{
          current: page,
          pageSize: screens.xs ? 10 : 20,
          total: data?.total,
          onChange: setPage,
          showTotal: (total) => `${t('common.total')} ${total} ${t('common.items')}`,
          showSizeChanger: false,
          simple: screens.xs,
        }}
        scroll={{ x: screens.xs ? 800 : 1200 }}
        sticky
      />
    </div>
  )
}

export default UserList
