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
  EyeOutlined,
} from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import axios from '@/utils/axios'
import dayjs from 'dayjs'
import { useDebounce } from '@/hooks/useDebounce'
import { exportToCSV } from '@/utils/exportUtils'
import { useTheme } from '@/contexts/ThemeContext'
import { getTagStyle, getTextColor } from '@/utils/awsColorHelpers'

const { Title } = Typography

const UserList = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const screens = Grid.useBreakpoint()
  const { theme } = useTheme()
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
    const action = isActive ? t('user.batchBan') : t('user.batchUnban')
    Modal.confirm({
      title: action,
      content: `${t('common.confirm')} "${username}"?`,
      okText: t('common.confirm'),
      cancelText: t('common.cancel'),
      okButtonProps: { danger: isActive },
      onOk: async () => {
        try {
          await axios.put(
            `/api/v1/admin/users/${userId}/ban`,
            {}
          )
          message.success(t('message.success'))
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
      message.warning(t('message.pleaseSelect'))
      return
    }
    Modal.confirm({
      title: t('user.batchBan'),
      content: `${t('common.confirm')} ${selectedRowKeys.length} ${t('menu.users')}?`,
      okText: t('common.confirm'),
      okType: 'danger',
      cancelText: t('common.cancel'),
      onOk: () => batchBanMutation.mutate(selectedRowKeys),
    })
  }
  
  const handleBatchUnban = () => {
    if (selectedRowKeys.length === 0) {
      message.warning(t('message.pleaseSelect'))
      return
    }
    Modal.confirm({
      title: t('user.batchUnban'),
      content: `${t('common.confirm')} ${selectedRowKeys.length} ${t('menu.users')}?`,
      okText: t('common.confirm'),
      cancelText: t('common.cancel'),
      onOk: () => batchUnbanMutation.mutate(selectedRowKeys),
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
      [t('user.username')]: item.username,
      [t('user.email')]: item.email,
      [t('user.status')]: item.is_active ? t('user.active') : t('user.banned'),
      [t('user.createdAt')]: item.created_at,
    }))
    
    exportToCSV(exportData, 'users')
    message.success(t('message.exportSuccess'))
  }

  const columns = [
    {
      title: t('table.id'),
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: t('user.username'),
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
      title: t('user.email'),
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: t('user.fullName'),
      dataIndex: 'full_name',
      key: 'full_name',
      render: (text: string) => text || '-',
    },
    {
      title: t('user.status'),
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (isActive: boolean) =>
        isActive ? (
          <Tag
            icon={<CheckCircleOutlined />}
            style={getTagStyle('success', theme)}
          >
            {t('user.active')}
          </Tag>
        ) : (
          <Tag
            icon={<StopOutlined />}
            style={getTagStyle('error', theme)}
          >
            {t('user.banned')}
          </Tag>
        ),
    },
    {
      title: t('user.vip'),
      dataIndex: 'is_vip',
      key: 'is_vip',
      width: 100,
      render: (isVip: boolean, record: any) => {
        if (!isVip) return (
          <Tag style={getTagStyle('neutral', theme)}>
            {t('user.normal')}
          </Tag>
        )
        const isExpired = record.vip_expires_at && dayjs(record.vip_expires_at).isBefore(dayjs())
        return (
          <Tag
            icon={<CrownOutlined />}
            style={getTagStyle('warning', theme)}
          >
            {isExpired ? t('user.vipExpired') : t('user.vip')}
          </Tag>
        )
      },
    },
    {
      title: t('user.createdAt'),
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => (
        <span style={{
          fontFamily: 'Monaco, Menlo, Consolas, monospace',
          color: getTextColor('primary', theme),
          fontSize: '13px'
        }}>
          {dayjs(date).format('YYYY-MM-DD HH:mm')}
        </span>
      ),
    },
    {
      title: t('user.lastLogin'),
      dataIndex: 'last_login_at',
      key: 'last_login_at',
      width: 180,
      render: (date: string) => (
        <span style={{
          fontFamily: 'Monaco, Menlo, Consolas, monospace',
          color: getTextColor('primary', theme),
          fontSize: '13px'
        }}>
          {date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'}
        </span>
      ),
    },
    {
      title: t('user.actions'),
      key: 'actions',
      width: 200,
      fixed: 'right' as const,
      render: (_: any, record: any) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/users/${record.id}`)}
          >
            {t('common.view')}
          </Button>
          <Button
            type={record.is_active ? 'default' : 'primary'}
            danger={record.is_active}
            size="small"
            icon={record.is_active ? <StopOutlined /> : <CheckCircleOutlined />}
            onClick={() => handleBanUser(record.id, record.username, record.is_active)}
          >
            {record.is_active ? t('user.ban') : t('user.unban')}
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
          showTotal: (total) => t('common.total', { count: total }),
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
