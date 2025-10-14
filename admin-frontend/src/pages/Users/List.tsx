import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Table, Tag, Space, Button, Input, message, Modal, Typography, Grid, Select, DatePicker, Card, Row, Col, Statistic } from 'antd'
import {
  UserOutlined,
  StopOutlined,
  CheckCircleOutlined,
  CrownOutlined,
  SearchOutlined,
  DownloadOutlined,
  EyeOutlined,
  FilterOutlined,
} from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import axios from '@/utils/axios'
import dayjs from 'dayjs'
import { useDebounce } from '@/hooks/useDebounce'
import { useTableSort } from '@/hooks/useTableSort'
import { exportToCSV } from '@/utils/exportUtils'
import { useTheme } from '@/contexts/ThemeContext'
import { getTagStyle, getTextColor } from '@/utils/awsColorHelpers'
import '@/styles/page-layout.css'

const { Title } = Typography

const UserList = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const screens = Grid.useBreakpoint()
  const { theme } = useTheme()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState('')
  const [selectedRowKeys, setSelectedRowKeys] = useState<number[]>([])
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [vipFilter, setVipFilter] = useState<string>('all')

  // Debounce search to reduce API calls
  const debouncedSearch = useDebounce(search, 500)

  // Table sorting
  const { handleTableChange, getSortParams } = useTableSort({
    defaultSortBy: 'created_at',
    defaultSortOrder: 'desc'
  })

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['admin-users', page, pageSize, debouncedSearch, statusFilter, vipFilter, ...Object.values(getSortParams())],
    queryFn: async () => {
      const params: any = {
        page,
        page_size: pageSize,
        ...getSortParams(),
      }
      if (debouncedSearch) params.search = debouncedSearch
      if (statusFilter !== 'all') params.status = statusFilter
      if (vipFilter !== 'all') params.is_vip = vipFilter === 'vip'

      const response = await axios.get('/api/v1/admin/users', { params })
      return response.data
    },
    placeholderData: (previousData) => previousData, // Keep previous data while loading
  })

  // Fetch user statistics
  const { data: stats } = useQuery({
    queryKey: ['admin-user-stats'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/users/stats')
      return response.data
    },
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
  
  // VIP management mutation
  const updateVIPMutation = useMutation({
    mutationFn: async ({ userId, isVip, expiresAt }: { userId: number; isVip: boolean; expiresAt?: string }) => {
      await axios.put(`/api/v1/admin/users/${userId}/vip`, {
        is_vip: isVip,
        vip_expires_at: expiresAt,
      })
    },
    onSuccess: () => {
      message.success(t('message.success'))
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('message.failed'))
    },
  })

  const handleVIPToggle = (userId: number, username: string, isVip: boolean) => {
    if (isVip) {
      // Remove VIP
      Modal.confirm({
        title: t('user.removeVip'),
        content: `${t('common.confirm')} "${username}"?`,
        okText: t('common.confirm'),
        cancelText: t('common.cancel'),
        okType: 'danger',
        onOk: () => updateVIPMutation.mutate({ userId, isVip: false }),
      })
    } else {
      // Grant VIP with expiry date picker
      let expiryDate: string | undefined
      Modal.confirm({
        title: t('user.grantVip'),
        content: (
          <div style={{ marginTop: 16 }}>
            <p>{`${t('common.confirm')} "${username}"?`}</p>
            <Space direction="vertical" style={{ width: '100%' }}>
              <span>{t('user.vipExpiryDate')}:</span>
              <DatePicker
                style={{ width: '100%' }}
                onChange={(date) => {
                  expiryDate = date ? date.toISOString() : undefined
                }}
                disabledDate={(current) => current && current < dayjs().endOf('day')}
              />
            </Space>
          </div>
        ),
        okText: t('common.confirm'),
        cancelText: t('common.cancel'),
        onOk: () => updateVIPMutation.mutate({ userId, isVip: true, expiresAt: expiryDate }),
      })
    }
  }

  // Batch VIP management mutations
  const batchGrantVIPMutation = useMutation({
    mutationFn: async ({ ids, expiresAt }: { ids: number[]; expiresAt?: string }) => {
      const params = new URLSearchParams({ is_vip: 'true' })
      if (expiresAt) params.append('vip_expires_at', expiresAt)
      await axios.put(`/api/v1/admin/users/batch/vip?${params.toString()}`, { ids })
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

  const batchRemoveVIPMutation = useMutation({
    mutationFn: async (ids: number[]) => {
      await axios.put('/api/v1/admin/users/batch/vip?is_vip=false', { ids })
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

  const handleBatchGrantVIP = () => {
    if (selectedRowKeys.length === 0) {
      message.warning(t('message.pleaseSelect'))
      return
    }

    let expiryDate: string | undefined
    Modal.confirm({
      title: t('user.batchGrantVip'),
      content: (
        <div style={{ marginTop: 16 }}>
          <p>{`${t('common.confirm')} ${selectedRowKeys.length} ${t('menu.users')}?`}</p>
          <Space direction="vertical" style={{ width: '100%', marginTop: 12 }}>
            <span>{t('user.vipExpiryDate')} ({t('common.optional')}):</span>
            <DatePicker
              style={{ width: '100%' }}
              onChange={(date) => {
                expiryDate = date ? date.toISOString() : undefined
              }}
              disabledDate={(current) => current && current < dayjs().endOf('day')}
            />
          </Space>
        </div>
      ),
      okText: t('common.confirm'),
      cancelText: t('common.cancel'),
      onOk: () => batchGrantVIPMutation.mutate({ ids: selectedRowKeys, expiresAt: expiryDate }),
    })
  }

  const handleBatchRemoveVIP = () => {
    if (selectedRowKeys.length === 0) {
      message.warning(t('message.pleaseSelect'))
      return
    }
    Modal.confirm({
      title: t('user.batchRemoveVip'),
      content: `${t('common.confirm')} ${selectedRowKeys.length} ${t('menu.users')}?`,
      okText: t('common.confirm'),
      okType: 'danger',
      cancelText: t('common.cancel'),
      onOk: () => batchRemoveVIPMutation.mutate(selectedRowKeys),
    })
  }

  // Export to CSV (now using server-side export)
  const handleExport = async () => {
    try {
      const params = new URLSearchParams()
      if (debouncedSearch) params.append('search', debouncedSearch)
      if (statusFilter !== 'all') params.append('status', statusFilter)
      if (vipFilter !== 'all') params.append('is_vip', vipFilter === 'vip' ? 'true' : 'false')

      const response = await axios.get(`/api/v1/admin/users/export?${params.toString()}`, {
        responseType: 'blob',
      })

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `users_export_${new Date().toISOString().split('T')[0]}.csv`)
      document.body.appendChild(link)
      link.click()
      link.remove()

      message.success(t('message.exportSuccess'))
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('message.exportFailed'))
    }
  }

  const columns = [
    {
      title: t('table.id'),
      dataIndex: 'id',
      key: 'id',
      width: 80,
      sorter: true,
    },
    {
      title: t('user.username'),
      dataIndex: 'username',
      key: 'username',
      sorter: true,
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
      sorter: true,
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
      sorter: true,
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
      sorter: true,
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
      width: 280,
      fixed: 'right' as const,
      render: (_: any, record: any) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/users/${record.id}`)}
          >
            {t('common.view')}
          </Button>
          <Button
            type={record.is_vip ? 'default' : 'primary'}
            size="small"
            icon={<CrownOutlined />}
            onClick={() => handleVIPToggle(record.id, record.username, record.is_vip)}
            style={{ color: record.is_vip ? '#faad14' : undefined }}
          >
            {record.is_vip ? t('user.removeVip') : t('user.grantVip')}
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
    <div className="page-container">
      {/* Page Header */}
      <div className="page-header">
        <div className="page-header-content">
          <div className="page-header-left">
            <Input.Search
              placeholder={t('common.search') + '...'}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onSearch={setSearch}
              loading={isLoading && !!debouncedSearch}
              allowClear
              style={{ width: 250 }}
              prefix={<SearchOutlined />}
            />
            <Select
              value={statusFilter}
              onChange={setStatusFilter}
              style={{ width: 120 }}
              options={[
                { label: t('user.allStatus'), value: 'all' },
                { label: t('user.active'), value: 'active' },
                { label: t('user.banned'), value: 'banned' },
              ]}
            />
            <Select
              value={vipFilter}
              onChange={setVipFilter}
              style={{ width: 120 }}
              options={[
                { label: t('user.allUsers'), value: 'all' },
                { label: 'VIP', value: 'vip' },
                { label: t('user.normal'), value: 'normal' },
              ]}
            />
          </div>
          <div className="page-header-right">
            <Button
              icon={<DownloadOutlined />}
              onClick={handleExport}
            >
              {t('video.exportExcel')}
            </Button>
          </div>
        </div>
      </div>

      {/* Batch operations */}
      {selectedRowKeys.length > 0 && (
        <div className="batch-operations">
          <Space wrap>
            <span style={{ fontWeight: 500 }}>
              {t('common.selected')}: {selectedRowKeys.length} {t('menu.users')}
            </span>
            <Button
              icon={<CrownOutlined />}
              onClick={handleBatchGrantVIP}
              style={{ color: '#faad14', borderColor: '#faad14' }}
            >
              {t('user.batchGrantVip')}
            </Button>
            <Button
              icon={<CrownOutlined />}
              onClick={handleBatchRemoveVIP}
            >
              {t('user.batchRemoveVip')}
            </Button>
            <Button
              danger
              icon={<StopOutlined />}
              onClick={handleBatchBan}
            >
              {t('user.batchBan')}
            </Button>
            <Button
              type="primary"
              icon={<CheckCircleOutlined />}
              onClick={handleBatchUnban}
            >
              {t('user.batchUnban')}
            </Button>
          </Space>
        </div>
      )}

      {/* Page Content */}
      <div className="page-content">
        {/* Statistics Cards */}
        {stats && (
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title={t('user.totalUsers')}
                  value={stats.total_users}
                  prefix={<UserOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title={t('user.activeUsers')}
                  value={stats.active_users}
                  prefix={<CheckCircleOutlined />}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title={t('user.vipUsers')}
                  value={stats.vip_users}
                  prefix={<CrownOutlined />}
                  valueStyle={{ color: '#faad14' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title={t('user.bannedUsers')}
                  value={stats.banned_users}
                  prefix={<StopOutlined />}
                  valueStyle={{ color: '#f5222d' }}
                />
              </Card>
            </Col>
          </Row>
        )}

        <div className="table-container">
          <Table
            rowSelection={rowSelection}
            columns={columns}
            dataSource={data?.items}
            loading={isLoading}
            rowKey="id"
            onChange={(pagination, filters, sorter) => handleTableChange(sorter)}
            pagination={{
              current: page,
              pageSize: pageSize,
              total: data?.total,
              onChange: setPage,
              onShowSizeChange: (current, size) => {
                setPageSize(size)
                setPage(1)
              },
              showSizeChanger: true,
              pageSizeOptions: ['10', '20', '50', '100'],
              showTotal: (total) => t('common.total', { count: total }),
              simple: screens.xs,
            }}
            scroll={{ x: screens.xs ? 800 : 1200 }}
            sticky
          />
        </div>
      </div>
    </div>
  )
}

export default UserList
