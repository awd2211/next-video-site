import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Card,
  Table,
  Space,
  Tag,
  Input,
  Select,
  DatePicker,
  Button,
  Modal,
  Descriptions,
  message,
  Row,
  Col,
  Statistic,
  Tooltip,
} from 'antd'
import {
  SearchOutlined,
  DeleteOutlined,
  EyeOutlined,
  ReloadOutlined,
  BarChartOutlined,
  DownloadOutlined,
} from '@ant-design/icons'
import axios from '@/utils/axios'
import dayjs from 'dayjs'

const { RangePicker } = DatePicker
const { Option } = Select

interface LogDetail {
  id: number
  admin_user_id: number
  admin_user?: {
    username: string
    email: string
  }
  module: string
  action: string
  description: string
  ip_address: string
  user_agent: string
  request_method: string
  request_url: string
  request_data: string
  created_at: string
}

const Logs = () => {
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [search, setSearch] = useState('')
  const [module, setModule] = useState<string | undefined>(undefined)
  const [action, setAction] = useState<string | undefined>(undefined)
  const [adminUserId, setAdminUserId] = useState<number | undefined>(undefined)
  const [dateRange, setDateRange] = useState<[string, string] | undefined>(undefined)
  const [selectedLog, setSelectedLog] = useState<LogDetail | null>(null)
  const [detailVisible, setDetailVisible] = useState(false)
  const [statsVisible, setStatsVisible] = useState(false)  // Fetch logs
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['admin-logs', page, pageSize, search, module, action, adminUserId, dateRange],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      })
      if (search) params.append('search', search)
      if (module) params.append('module', module)
      if (action) params.append('action', action)
      if (adminUserId) params.append('admin_user_id', adminUserId.toString())
      if (dateRange) {
        params.append('start_date', dateRange[0])
        params.append('end_date', dateRange[1])
      }

      const response = await axios.get(`/api/v1/admin/logs/operations?${params}`)
      return response.data
    },
  })

  // Fetch available modules
  const { data: modulesData } = useQuery({
    queryKey: ['log-modules'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/logs/operations/modules/list')
      return response.data
    },
  })

  // Fetch available actions
  const { data: actionsData } = useQuery({
    queryKey: ['log-actions'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/logs/operations/actions/list')
      return response.data
    },
  })

  // Fetch statistics
  const { data: statsData } = useQuery({
    queryKey: ['log-stats'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/logs/operations/stats/summary?days=7')
      return response.data
    },
    enabled: statsVisible,
  })

  const handleViewDetail = async (logId: number) => {
    try {
      const response = await axios.get(`/api/v1/admin/logs/operations/${logId}`)
      setSelectedLog(response.data)
      setDetailVisible(true)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取日志详情失败')
    }
  }

  const handleCleanup = () => {
    Modal.confirm({
      title: '清理旧日志',
      content: (
        <div>
          <p>此操作将删除 90 天前的操作日志，此操作不可恢复。</p>
          <p>请确认是否继续？</p>
        </div>
      ),
      okText: '确认清理',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          const response = await axios.delete('/api/v1/admin/logs/operations/cleanup?days=90')
          message.success(response.data.message)
          refetch()
        } catch (error: any) {
          message.error(error.response?.data?.detail || '清理失败')
        }
      },
    })
  }

  const handleReset = () => {
    setSearch('')
    setModule(undefined)
    setAction(undefined)
    setAdminUserId(undefined)
    setDateRange(undefined)
    setPage(1)
  }

  const handleExport = () => {
    // 构建导出URL
    const params = new URLSearchParams()
    if (search) params.append('search', search)
    if (module) params.append('module', module)
    if (action) params.append('action', action)
    if (adminUserId) params.append('admin_user_id', adminUserId.toString())
    if (dateRange) {
      params.append('start_date', dateRange[0])
      params.append('end_date', dateRange[1])
    }

    // 获取token
    const token = localStorage.getItem('admin_access_token')
    if (!token) {
      message.error('请先登录')
      return
    }

    // 创建一个临时的a标签下载
    const exportUrl = `/api/v1/admin/logs/operations/export?${params.toString()}`
    const link = document.createElement('a')
    link.href = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'}${exportUrl}`
    link.download = `operation_logs_${new Date().getTime()}.csv`

    // 使用fetch下载文件
    fetch(link.href, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
      .then(response => response.blob())
      .then(blob => {
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `operation_logs_${new Date().getTime()}.csv`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        message.success('导出成功')
      })
      .catch(error => {
        console.error('Export error:', error)
        message.error('导出失败')
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
      title: '管理员',
      dataIndex: ['admin_user', 'username'],
      key: 'admin_user',
      width: 120,
      render: (username: string, record: any) => (
        <Tooltip title={record.admin_user?.email}>
          <span>{username || '-'}</span>
        </Tooltip>
      ),
    },
    {
      title: '模块',
      dataIndex: 'module',
      key: 'module',
      width: 120,
      render: (text: string) => <Tag color="blue">{text}</Tag>,
    },
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
      width: 100,
      render: (text: string) => {
        const colorMap: { [key: string]: string } = {
          create: 'green',
          update: 'orange',
          delete: 'red',
          login: 'cyan',
          logout: 'default',
          view: 'geekblue',
          cleanup: 'purple',
        }
        return <Tag color={colorMap[text] || 'default'}>{text}</Tag>
      },
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (text: string) => (
        <Tooltip title={text}>
          <span>{text}</span>
        </Tooltip>
      ),
    },
    {
      title: 'IP地址',
      dataIndex: 'ip_address',
      key: 'ip_address',
      width: 140,
      render: (text: string) => text || '-',
    },
    {
      title: '请求方法',
      dataIndex: 'request_method',
      key: 'request_method',
      width: 100,
      render: (text: string) => {
        const colorMap: { [key: string]: string } = {
          GET: 'default',
          POST: 'green',
          PUT: 'orange',
          DELETE: 'red',
          PATCH: 'purple',
        }
        return text ? <Tag color={colorMap[text] || 'default'}>{text}</Tag> : '-'
      },
    },
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 100,
      fixed: 'right' as const,
      render: (_: any, record: any) => (
        <Button
          type="link"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => handleViewDetail(record.id)}
        >
          详情
        </Button>
      ),
    },
  ]

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>操作日志</h2>

      <Card style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <Row gutter={16}>
            <Col span={8}>
              <Input
                placeholder="搜索描述或IP地址"
                prefix={<SearchOutlined />}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                allowClear
              />
            </Col>
            <Col span={4}>
              <Select
                placeholder="选择模块"
                style={{ width: '100%' }}
                value={module}
                onChange={setModule}
                allowClear
              >
                {modulesData?.modules?.map((m: string) => (
                  <Option key={m} value={m}>
                    {m}
                  </Option>
                ))}
              </Select>
            </Col>
            <Col span={4}>
              <Select
                placeholder="选择操作"
                style={{ width: '100%' }}
                value={action}
                onChange={setAction}
                allowClear
              >
                {actionsData?.actions?.map((a: string) => (
                  <Option key={a} value={a}>
                    {a}
                  </Option>
                ))}
              </Select>
            </Col>
            <Col span={8}>
              <RangePicker
                style={{ width: '100%' }}
                value={dateRange ? [dayjs(dateRange[0]), dayjs(dateRange[1])] : null}
                onChange={(dates) => {
                  if (dates) {
                    setDateRange([
                      dates[0]!.toISOString(),
                      dates[1]!.toISOString(),
                    ])
                  } else {
                    setDateRange(undefined)
                  }
                }}
              />
            </Col>
          </Row>

          <Space>
            <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
              刷新
            </Button>
            <Button onClick={handleReset}>重置筛选</Button>
            <Button
              icon={<BarChartOutlined />}
              onClick={() => setStatsVisible(true)}
            >
              查看统计
            </Button>
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={handleExport}
            >
              导出CSV
            </Button>
            <Button
              danger
              icon={<DeleteOutlined />}
              onClick={handleCleanup}
            >
              清理旧日志
            </Button>
          </Space>
        </Space>
      </Card>

      <Card>
        <Table
          columns={columns}
          dataSource={data?.items || []}
          rowKey="id"
          loading={isLoading}
          scroll={{ x: 1400 }}
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

      {/* Log Detail Modal */}
      <Modal
        title="操作日志详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailVisible(false)}>
            关闭
          </Button>,
        ]}
        width={800}
      >
        {selectedLog && (
          <Descriptions column={2} bordered>
            <Descriptions.Item label="ID">{selectedLog.id}</Descriptions.Item>
            <Descriptions.Item label="管理员">
              {selectedLog.admin_user?.username || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="模块">{selectedLog.module}</Descriptions.Item>
            <Descriptions.Item label="操作">{selectedLog.action}</Descriptions.Item>
            <Descriptions.Item label="描述" span={2}>
              {selectedLog.description}
            </Descriptions.Item>
            <Descriptions.Item label="IP地址">
              {selectedLog.ip_address || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="请求方法">
              {selectedLog.request_method || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="请求URL" span={2}>
              {selectedLog.request_url || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="User Agent" span={2}>
              {selectedLog.user_agent || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="请求数据" span={2}>
              {selectedLog.request_data ? (
                <pre style={{ maxHeight: 300, overflow: 'auto', background: '#f5f5f5', padding: 8 }}>
                  {JSON.stringify(JSON.parse(selectedLog.request_data), null, 2)}
                </pre>
              ) : (
                '-'
              )}
            </Descriptions.Item>
            <Descriptions.Item label="创建时间" span={2}>
              {dayjs(selectedLog.created_at).format('YYYY-MM-DD HH:mm:ss')}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>

      {/* Statistics Modal */}
      <Modal
        title="操作日志统计（最近7天）"
        open={statsVisible}
        onCancel={() => setStatsVisible(false)}
        footer={[
          <Button key="close" onClick={() => setStatsVisible(false)}>
            关闭
          </Button>,
        ]}
        width={1000}
      >
        {statsData && (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <Card title="按模块统计">
              <Row gutter={16}>
                {statsData.module_stats?.map((item: any) => (
                  <Col span={6} key={item.module}>
                    <Statistic title={item.module} value={item.count} />
                  </Col>
                ))}
              </Row>
            </Card>

            <Card title="按操作类型统计">
              <Row gutter={16}>
                {statsData.action_stats?.map((item: any) => (
                  <Col span={6} key={item.action}>
                    <Statistic title={item.action} value={item.count} />
                  </Col>
                ))}
              </Row>
            </Card>

            <Card title="按管理员统计（Top 10）">
              <Row gutter={16}>
                {statsData.admin_stats?.map((item: any) => (
                  <Col span={6} key={item.admin_user_id}>
                    <Statistic title={`管理员 #${item.admin_user_id}`} value={item.count} />
                  </Col>
                ))}
              </Row>
            </Card>

            <Card title="每日操作趋势">
              <Table
                dataSource={statsData.daily_stats}
                columns={[
                  { title: '日期', dataIndex: 'date', key: 'date' },
                  { title: '操作数', dataIndex: 'count', key: 'count' },
                ]}
                pagination={false}
                size="small"
              />
            </Card>
          </Space>
        )}
      </Modal>
    </div>
  )
}

export default Logs
