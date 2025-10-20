import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import {
  Card,
  Tabs,
  Table,
  Space,
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
  Tag,
  Badge,
} from 'antd'
import {
  SearchOutlined,
  DeleteOutlined,
  EyeOutlined,
  ReloadOutlined,
  BarChartOutlined,
  DownloadOutlined,
  SafetyOutlined,
  LoginOutlined,
  BugOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons'
import axios from '@/utils/axios'
import dayjs from 'dayjs'
import { formatAWSDate, formatAWSNumber, AWSTag } from '@/utils/awsStyleHelpers'

const { RangePicker } = DatePicker
const { Option } = Select

interface OperationLog {
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

interface LoginLog {
  id: number
  user_type: string
  user_id?: number
  username?: string
  email?: string
  status: string
  failure_reason?: string
  ip_address: string
  user_agent: string
  location?: string
  device_type: string
  browser: string
  os: string
  created_at: string
}

interface SystemLog {
  id: number
  level: string
  category: string
  event: string
  message: string
  details?: string
  source?: string
  user_id?: number
  user_type?: string
  created_at: string
}

interface ErrorLog {
  id: number
  level: string
  error_type: string
  error_message: string
  traceback?: string
  request_method?: string
  request_url?: string
  request_data?: string
  user_id?: number
  user_type?: string
  ip_address?: string
  user_agent?: string
  status_code?: number
  resolved: boolean
  resolved_by?: number
  resolved_at?: string
  admin_notes?: string
  created_at: string
}

const Logs = () => {
  const { t } = useTranslation()

  const [activeTab, setActiveTab] = useState('operation')

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>{t('logs.tabs.system')}</h2>

      <Card>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'operation',
              label: (
                <span>
                  <FileTextOutlined />
                  {t('logs.tabs.operation')}
                </span>
              ),
              children: <OperationLogsTab />,
            },
            {
              key: 'login',
              label: (
                <span>
                  <LoginOutlined />
                  {t('logs.tabs.login')}
                </span>
              ),
              children: <LoginLogsTab />,
            },
            {
              key: 'system',
              label: (
                <span>
                  <SafetyOutlined />
                  {t('logs.tabs.system')}
                </span>
              ),
              children: <SystemLogsTab />,
            },
            {
              key: 'error',
              label: (
                <span>
                  <BugOutlined />
                  {t('logs.tabs.error')}
                </span>
              ),
              children: <ErrorLogsTab />,
            },
          ]}
        />
      </Card>
    </div>
  )
}

// Operation Logs Tab Component
const OperationLogsTab = () => {
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [search, setSearch] = useState('')
  const [module, setModule] = useState<string | undefined>(undefined)
  const [action, setAction] = useState<string | undefined>(undefined)
  const [dateRange, setDateRange] = useState<[string, string] | undefined>(undefined)
  const [selectedLog, setSelectedLog] = useState<OperationLog | null>(null)
  const [detailVisible, setDetailVisible] = useState(false)

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['admin-operation-logs', page, pageSize, search, module, action, dateRange],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      })
      if (search) params.append('search', search)
      if (module) params.append('module', module)
      if (action) params.append('action', action)
      if (dateRange) {
        params.append('start_date', dateRange[0])
        params.append('end_date', dateRange[1])
      }
      const response = await axios.get(`/api/v1/admin/logs/operations?${params}`)
      return response.data
    },
  })

  const { data: modulesData } = useQuery({
    queryKey: ['log-modules'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/logs/operations/modules/list')
      return response.data
    },
  })

  const { data: actionsData } = useQuery({
    queryKey: ['log-actions'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/logs/operations/actions/list')
      return response.data
    },
  })

  const handleViewDetail = async (logId: number) => {
    try {
      const response = await axios.get(`/api/v1/admin/logs/operations/${logId}`)
      setSelectedLog(response.data)
      setDetailVisible(true)
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('logs.message.fetchDetailsFailed'))
    }
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: t('logs.table.admin'),
      dataIndex: ['admin_user', 'username'],
      key: 'admin_user',
      width: 120,
    },
    {
      title: t('logs.table.module'),
      dataIndex: 'module',
      key: 'module',
      width: 120,
      render: (text: string) => <AWSTag type="info">{text}</AWSTag>,
    },
    {
      title: t('logs.table.action'),
      dataIndex: 'action',
      key: 'action',
      width: 100,
      render: (text: string) => {
        const typeMap: { [key: string]: 'success' | 'warning' | 'error' | 'info' | 'default' } = {
          create: 'success',
          update: 'warning',
          delete: 'error',
          login: 'info',
        }
        return <AWSTag type={typeMap[text] || 'default'}>{text}</AWSTag>
      },
    },
    {
      title: t('logs.table.description'),
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: t('logs.table.ipAddress'),
      dataIndex: 'ip_address',
      key: 'ip_address',
      width: 140,
    },
    {
      title: t('logs.table.time'),
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => formatAWSDate(date, 'YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: t('logs.table.action'),
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
          {t('logs.table.details')}
        </Button>
      ),
    },
  ]

  return (
    <div>
      <Space direction="vertical" style={{ width: '100%', marginBottom: 16 }} size="middle">
        <Row gutter={16}>
          <Col span={8}>
            <Input
              placeholder=t('logs.search.placeholder')
              prefix={<SearchOutlined />}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              allowClear
            />
          </Col>
          <Col span={4}>
            <Select
              placeholder=t('logs.filter.selectModule')
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
              placeholder=t('logs.filter.selectAction')
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
                  setDateRange([dates[0]!.toISOString(), dates[1]!.toISOString()])
                } else {
                  setDateRange(undefined)
                }
              }}
            />
          </Col>
        </Row>

        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
            {t('common.refresh')}
          </Button>
        </Space>
      </Space>

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
          showTotal: (total) => t('common.total', { count: total }),
          onChange: (newPage) => setPage(newPage),
        }}
      />

      <Modal
        title=t('logs.modal.operationDetails')
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailVisible(false)}>
            {t('common.close')}
          </Button>,
        ]}
        width={800}
      >
        {selectedLog && (
          <Descriptions column={2} bordered>
            <Descriptions.Item label="ID">{selectedLog.id}</Descriptions.Item>
            <Descriptions.Item label=t('logs.table.admin')>
              {selectedLog.admin_user?.username || '-'}
            </Descriptions.Item>
            <Descriptions.Item label=t('logs.table.module')>{selectedLog.module}</Descriptions.Item>
            <Descriptions.Item label=t('logs.table.action')>{selectedLog.action}</Descriptions.Item>
            <Descriptions.Item label=t('logs.table.description') span={2}>
              {selectedLog.description}
            </Descriptions.Item>
            <Descriptions.Item label=t('logs.table.ipAddress')>{selectedLog.ip_address || '-'}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.requestMethod')>{selectedLog.request_method || '-'}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.requestUrl') span={2}>
              {selectedLog.request_url || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="User Agent" span={2}>
              {selectedLog.user_agent || '-'}
            </Descriptions.Item>
            <Descriptions.Item label=t('logs.details.requestData') span={2}>
              {selectedLog.request_data ? (
                <pre style={{ maxHeight: 300, overflow: 'auto', background: '#f5f5f5', padding: 8 }}>
                  {JSON.stringify(JSON.parse(selectedLog.request_data), null, 2)}
                </pre>
              ) : (
                '-'
              )}
            </Descriptions.Item>
            <Descriptions.Item label=t('logs.details.createTime') span={2}>
              {formatAWSDate(selectedLog.created_at, 'YYYY-MM-DD HH:mm:ss')}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  )
}

// Login Logs Tab Component
const LoginLogsTab = () => {
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [search, setSearch] = useState('')
  const [userType, setUserType] = useState<string | undefined>(undefined)
  const [status, setStatus] = useState<string | undefined>(undefined)
  const [dateRange, setDateRange] = useState<[string, string] | undefined>(undefined)
  const [selectedLog, setSelectedLog] = useState<LoginLog | null>(null)
  const [detailVisible, setDetailVisible] = useState(false)

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['admin-login-logs', page, pageSize, search, userType, status, dateRange],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      })
      if (search) params.append('search', search)
      if (userType) params.append('user_type', userType)
      if (status) params.append('status', status)
      if (dateRange) {
        params.append('start_date', dateRange[0])
        params.append('end_date', dateRange[1])
      }
      const response = await axios.get(`/api/v1/admin/logs/logins?${params}`)
      return response.data
    },
  })

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: t('logs.details.userType'),
      dataIndex: 'user_type',
      key: 'user_type',
      width: 100,
      render: (text: string) => (
        <Tag color={text === 'admin' ? 'red' : 'blue'}>{text}</Tag>
      ),
    },
    {
      title: t('logs.details.username'),
      dataIndex: 'username',
      key: 'username',
      width: 120,
      render: (text: string) => text || '-',
    },
    {
      title: t('logs.details.email'),
      dataIndex: 'email',
      key: 'email',
      width: 180,
      ellipsis: true,
    },
    {
      title: t('logs.details.status'),
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const colorMap: { [key: string]: string } = {
          success: 'success',
          failed: 'error',
          blocked: 'warning',
        }
        return <Tag color={colorMap[status]}>{status}</Tag>
      },
    },
    {
      title: t('logs.details.failureReason'),
      dataIndex: 'failure_reason',
      key: 'failure_reason',
      ellipsis: true,
      render: (text: string) => text || '-',
    },
    {
      title: t('logs.table.ipAddress'),
      dataIndex: 'ip_address',
      key: 'ip_address',
      width: 140,
    },
    {
      title: t('logs.table.device'),
      dataIndex: 'device_type',
      key: 'device_type',
      width: 100,
    },
    {
      title: t('logs.table.time'),
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => formatAWSDate(date, 'YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: t('logs.table.action'),
      key: 'actions',
      width: 100,
      fixed: 'right' as const,
      render: (_: any, record: any) => (
        <Button
          type="link"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => {
            setSelectedLog(record)
            setDetailVisible(true)
          }}
        >
          {t('logs.table.details')}
        </Button>
      ),
    },
  ]

  return (
    <div>
      <Space direction="vertical" style={{ width: '100%', marginBottom: 16 }} size="middle">
        <Row gutter={16}>
          <Col span={8}>
            <Input
              placeholder=t('logs.search.usernameOrEmail')
              prefix={<SearchOutlined />}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              allowClear
            />
          </Col>
          <Col span={4}>
            <Select
              placeholder=t('logs.details.userType')
              style={{ width: '100%' }}
              value={userType}
              onChange={setUserType}
              allowClear
            >
              <Option value="user">{t('logs.details.user')}</Option>
              <Option value="admin">{t('logs.table.admin')}</Option>
            </Select>
          </Col>
          <Col span={4}>
            <Select
              placeholder=t('logs.details.status')
              style={{ width: '100%' }}
              value={status}
              onChange={setStatus}
              allowClear
            >
              <Option value="success">{t('logs.status.success')}</Option>
              <Option value="failed">{t('logs.status.failed')}</Option>
              <Option value="blocked">{t('logs.status.blocked')}</Option>
            </Select>
          </Col>
          <Col span={8}>
            <RangePicker
              style={{ width: '100%' }}
              value={dateRange ? [dayjs(dateRange[0]), dayjs(dateRange[1])] : null}
              onChange={(dates) => {
                if (dates) {
                  setDateRange([dates[0]!.toISOString(), dates[1]!.toISOString()])
                } else {
                  setDateRange(undefined)
                }
              }}
            />
          </Col>
        </Row>

        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
            {t('common.refresh')}
          </Button>
        </Space>
      </Space>

      <Table
        columns={columns}
        dataSource={data?.items || []}
        rowKey="id"
        loading={isLoading}
        scroll={{ x: 1600 }}
        pagination={{
          current: page,
          pageSize: pageSize,
          total: data?.total || 0,
          showSizeChanger: false,
          showQuickJumper: true,
          showTotal: (total) => t('common.total', { count: total }),
          onChange: (newPage) => setPage(newPage),
        }}
      />

      <Modal
        title=t('logs.modal.loginDetails')
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailVisible(false)}>
            {t('common.close')}
          </Button>,
        ]}
        width={800}
      >
        {selectedLog && (
          <Descriptions column={2} bordered>
            <Descriptions.Item label="ID">{selectedLog.id}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.userType')>{selectedLog.user_type}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.username')>{selectedLog.username || '-'}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.email')>{selectedLog.email || '-'}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.status')>{selectedLog.status}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.failureReason')>{selectedLog.failure_reason || '-'}</Descriptions.Item>
            <Descriptions.Item label=t('logs.table.ipAddress')>{selectedLog.ip_address}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.location')>{selectedLog.location || '-'}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.deviceType')>{selectedLog.device_type}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.browser')>{selectedLog.browser}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.os') span={2}>{selectedLog.os}</Descriptions.Item>
            <Descriptions.Item label="User Agent" span={2}>
              {selectedLog.user_agent}
            </Descriptions.Item>
            <Descriptions.Item label=t('logs.table.time') span={2}>
              {formatAWSDate(selectedLog.created_at, 'YYYY-MM-DD HH:mm:ss')}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  )
}

// System Logs Tab Component
const SystemLogsTab = () => {
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [search, setSearch] = useState('')
  const [level, setLevel] = useState<string | undefined>(undefined)
  const [category, setCategory] = useState<string | undefined>(undefined)
  const [dateRange, setDateRange] = useState<[string, string] | undefined>(undefined)
  const [selectedLog, setSelectedLog] = useState<SystemLog | null>(null)
  const [detailVisible, setDetailVisible] = useState(false)

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['admin-system-logs', page, pageSize, search, level, category, dateRange],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      })
      if (search) params.append('search', search)
      if (level) params.append('level', level)
      if (category) params.append('category', category)
      if (dateRange) {
        params.append('start_date', dateRange[0])
        params.append('end_date', dateRange[1])
      }
      const response = await axios.get(`/api/v1/admin/logs/system?${params}`)
      return response.data
    },
  })

  const { data: categoriesData } = useQuery({
    queryKey: ['system-log-categories'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/logs/system/categories')
      return response.data
    },
  })

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: t('logs.details.level'),
      dataIndex: 'level',
      key: 'level',
      width: 100,
      render: (level: string) => {
        const colorMap: { [key: string]: string } = {
          info: 'blue',
          warning: 'orange',
          error: 'red',
          critical: 'purple',
        }
        return <Tag color={colorMap[level]}>{level.toUpperCase()}</Tag>
      },
    },
    {
      title: t('logs.details.category'),
      dataIndex: 'category',
      key: 'category',
      width: 120,
    },
    {
      title: t('logs.details.event'),
      dataIndex: 'event',
      key: 'event',
      width: 150,
    },
    {
      title: t('logs.details.message'),
      dataIndex: 'message',
      key: 'message',
      ellipsis: true,
    },
    {
      title: t('logs.details.source'),
      dataIndex: 'source',
      key: 'source',
      width: 150,
      render: (text: string) => text || '-',
    },
    {
      title: t('logs.table.time'),
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => formatAWSDate(date, 'YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: t('logs.table.action'),
      key: 'actions',
      width: 100,
      fixed: 'right' as const,
      render: (_: any, record: any) => (
        <Button
          type="link"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => {
            setSelectedLog(record)
            setDetailVisible(true)
          }}
        >
          {t('logs.table.details')}
        </Button>
      ),
    },
  ]

  return (
    <div>
      <Space direction="vertical" style={{ width: '100%', marginBottom: 16 }} size="middle">
        <Row gutter={16}>
          <Col span={8}>
            <Input
              placeholder=t('logs.search.eventOrMessage')
              prefix={<SearchOutlined />}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              allowClear
            />
          </Col>
          <Col span={4}>
            <Select
              placeholder=t('logs.details.level')
              style={{ width: '100%' }}
              value={level}
              onChange={setLevel}
              allowClear
            >
              <Option value="info">INFO</Option>
              <Option value="warning">WARNING</Option>
              <Option value="error">ERROR</Option>
              <Option value="critical">CRITICAL</Option>
            </Select>
          </Col>
          <Col span={4}>
            <Select
              placeholder=t('logs.details.category')
              style={{ width: '100%' }}
              value={category}
              onChange={setCategory}
              allowClear
            >
              {categoriesData?.categories?.map((c: string) => (
                <Option key={c} value={c}>
                  {c}
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
                  setDateRange([dates[0]!.toISOString(), dates[1]!.toISOString()])
                } else {
                  setDateRange(undefined)
                }
              }}
            />
          </Col>
        </Row>

        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
            {t('common.refresh')}
          </Button>
        </Space>
      </Space>

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
          showTotal: (total) => t('common.total', { count: total }),
          onChange: (newPage) => setPage(newPage),
        }}
      />

      <Modal
        title=t('logs.modal.systemDetails')
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailVisible(false)}>
            {t('common.close')}
          </Button>,
        ]}
        width={800}
      >
        {selectedLog && (
          <Descriptions column={2} bordered>
            <Descriptions.Item label="ID">{selectedLog.id}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.level')>{selectedLog.level.toUpperCase()}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.category')>{selectedLog.category}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.event')>{selectedLog.event}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.message') span={2}>{selectedLog.message}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.source') span={2}>{selectedLog.source || '-'}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.detailedInfo') span={2}>
              {selectedLog.details ? (
                <pre style={{ maxHeight: 300, overflow: 'auto', background: '#f5f5f5', padding: 8 }}>
                  {JSON.stringify(JSON.parse(selectedLog.details), null, 2)}
                </pre>
              ) : (
                '-'
              )}
            </Descriptions.Item>
            <Descriptions.Item label=t('logs.table.time') span={2}>
              {formatAWSDate(selectedLog.created_at, 'YYYY-MM-DD HH:mm:ss')}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  )
}

// Error Logs Tab Component
const ErrorLogsTab = () => {
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [search, setSearch] = useState('')
  const [level, setLevel] = useState<string | undefined>(undefined)
  const [errorType, setErrorType] = useState<string | undefined>(undefined)
  const [resolved, setResolved] = useState<boolean | undefined>(undefined)
  const [dateRange, setDateRange] = useState<[string, string] | undefined>(undefined)
  const [selectedLog, setSelectedLog] = useState<ErrorLog | null>(null)
  const [detailVisible, setDetailVisible] = useState(false)
  const [resolveVisible, setResolveVisible] = useState(false)
  const [adminNotes, setAdminNotes] = useState('')

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['admin-error-logs', page, pageSize, search, level, errorType, resolved, dateRange],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      })
      if (search) params.append('search', search)
      if (level) params.append('level', level)
      if (errorType) params.append('error_type', errorType)
      if (resolved !== undefined) params.append('resolved', resolved.toString())
      if (dateRange) {
        params.append('start_date', dateRange[0])
        params.append('end_date', dateRange[1])
      }
      const response = await axios.get(`/api/v1/admin/logs/errors?${params}`)
      return response.data
    },
  })

  const { data: errorTypesData } = useQuery({
    queryKey: ['error-log-types'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/logs/errors/types')
      return response.data
    },
  })

  const handleResolve = async () => {
    if (!selectedLog) return
    try {
      await axios.put(`/api/v1/admin/logs/errors/${selectedLog.id}/resolve`, {
        admin_notes: adminNotes,
      })
      message.success(t('logs.message.markedResolved'))
      setResolveVisible(false)
      setAdminNotes('')
      refetch()
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('logs.message.operationFailed'))
    }
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: t('logs.details.level'),
      dataIndex: 'level',
      key: 'level',
      width: 100,
      render: (level: string) => {
        const colorMap: { [key: string]: string } = {
          error: 'red',
          critical: 'purple',
        }
        return <Tag color={colorMap[level]}>{level.toUpperCase()}</Tag>
      },
    },
    {
      title: t('logs.details.errorType'),
      dataIndex: 'error_type',
      key: 'error_type',
      width: 150,
    },
    {
      title: t('logs.table.errorMessage'),
      dataIndex: 'error_message',
      key: 'error_message',
      ellipsis: true,
    },
    {
      title: t('logs.details.requestUrl'),
      dataIndex: 'request_url',
      key: 'request_url',
      width: 200,
      ellipsis: true,
      render: (text: string) => text || '-',
    },
    {
      title: t('logs.details.statusCode'),
      dataIndex: 'status_code',
      key: 'status_code',
      width: 100,
      render: (code: number) => code || '-',
    },
    {
      title: t('logs.details.resolveStatus'),
      dataIndex: 'resolved',
      key: 'resolved',
      width: 100,
      render: (resolved: boolean) => (
        resolved ? (
          <Badge status="success" text=t('logs.status.resolved') />
        ) : (
          <Badge status="error" text=t('logs.status.unresolved') />
        )
      ),
    },
    {
      title: t('logs.table.time'),
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => formatAWSDate(date, 'YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: t('logs.table.action'),
      key: 'actions',
      width: 150,
      fixed: 'right' as const,
      render: (_: any, record: any) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => {
              setSelectedLog(record)
              setDetailVisible(true)
            }}
          >
            {t('logs.table.details')}
          </Button>
          {!record.resolved && (
            <Button
              type="link"
              size="small"
              icon={<CheckCircleOutlined />}
              onClick={() => {
                setSelectedLog(record)
                setResolveVisible(true)
              }}
            >
              {t('logs.actions.resolve')}
            </Button>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Space direction="vertical" style={{ width: '100%', marginBottom: 16 }} size="middle">
        <Row gutter={16}>
          <Col span={6}>
            <Input
              placeholder=t('logs.search.errorMessage')
              prefix={<SearchOutlined />}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              allowClear
            />
          </Col>
          <Col span={3}>
            <Select
              placeholder=t('logs.details.level')
              style={{ width: '100%' }}
              value={level}
              onChange={setLevel}
              allowClear
            >
              <Option value="error">ERROR</Option>
              <Option value="critical">CRITICAL</Option>
            </Select>
          </Col>
          <Col span={4}>
            <Select
              placeholder=t('logs.details.errorType')
              style={{ width: '100%' }}
              value={errorType}
              onChange={setErrorType}
              allowClear
            >
              {errorTypesData?.error_types?.map((t: string) => (
                <Option key={t} value={t}>
                  {t}
                </Option>
              ))}
            </Select>
          </Col>
          <Col span={3}>
            <Select
              placeholder=t('logs.details.resolveStatus')
              style={{ width: '100%' }}
              value={resolved}
              onChange={setResolved}
              allowClear
            >
              <Option value={true}>{t('logs.status.resolved')}</Option>
              <Option value={false}>{t('logs.status.unresolved')}</Option>
            </Select>
          </Col>
          <Col span={8}>
            <RangePicker
              style={{ width: '100%' }}
              value={dateRange ? [dayjs(dateRange[0]), dayjs(dateRange[1])] : null}
              onChange={(dates) => {
                if (dates) {
                  setDateRange([dates[0]!.toISOString(), dates[1]!.toISOString()])
                } else {
                  setDateRange(undefined)
                }
              }}
            />
          </Col>
        </Row>

        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
            {t('common.refresh')}
          </Button>
        </Space>
      </Space>

      <Table
        columns={columns}
        dataSource={data?.items || []}
        rowKey="id"
        loading={isLoading}
        scroll={{ x: 1800 }}
        pagination={{
          current: page,
          pageSize: pageSize,
          total: data?.total || 0,
          showSizeChanger: false,
          showQuickJumper: true,
          showTotal: (total) => t('common.total', { count: total }),
          onChange: (newPage) => setPage(newPage),
        }}
      />

      <Modal
        title=t('logs.modal.errorDetails')
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailVisible(false)}>
            {t('common.close')}
          </Button>,
        ]}
        width={1000}
      >
        {selectedLog && (
          <Descriptions column={2} bordered>
            <Descriptions.Item label="ID">{selectedLog.id}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.level')>{selectedLog.level.toUpperCase()}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.errorType')>{selectedLog.error_type}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.statusCode')>{selectedLog.status_code || '-'}</Descriptions.Item>
            <Descriptions.Item label=t('logs.table.errorMessage') span={2}>{selectedLog.error_message}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.requestMethod')>{selectedLog.request_method || '-'}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.requestUrl')>{selectedLog.request_url || '-'}</Descriptions.Item>
            <Descriptions.Item label=t('logs.table.ipAddress')>{selectedLog.ip_address || '-'}</Descriptions.Item>
            <Descriptions.Item label="User Agent">{selectedLog.user_agent || '-'}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.resolveStatus')>{selectedLog.resolved ? t('logs.status.resolved') : t('logs.status.unresolved')}</Descriptions.Item>
            <Descriptions.Item label=t('logs.details.resolveTime')>
              {selectedLog.resolved_at ? formatAWSDate(selectedLog.resolved_at, 'YYYY-MM-DD HH:mm:ss') : '-'}
            </Descriptions.Item>
            <Descriptions.Item label=t('logs.details.adminNote') span={2}>
              {selectedLog.admin_notes || '-'}
            </Descriptions.Item>
            <Descriptions.Item label=t('logs.details.stackTrace') span={2}>
              {selectedLog.traceback ? (
                <pre style={{ maxHeight: 400, overflow: 'auto', background: '#f5f5f5', padding: 8, fontSize: 12 }}>
                  {selectedLog.traceback}
                </pre>
              ) : (
                '-'
              )}
            </Descriptions.Item>
            <Descriptions.Item label=t('logs.details.createTime') span={2}>
              {formatAWSDate(selectedLog.created_at, 'YYYY-MM-DD HH:mm:ss')}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>

      <Modal
        title=t('logs.actions.markResolved')
        open={resolveVisible}
        onCancel={() => {
          setResolveVisible(false)
          setAdminNotes('')
        }}
        onOk={handleResolve}
        okText=t('common.confirm')
        cancelText=t('common.cancel')
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <label>{t('logs.details.adminNoteOptional')}</label>
            <Input.TextArea
              rows={4}
              value={adminNotes}
              onChange={(e) => setAdminNotes(e.target.value)}
              placeholder={t('logs.placeholder.addNote')}
            />
          </div>
        </Space>
      </Modal>
    </div>
  )
}

export default Logs
