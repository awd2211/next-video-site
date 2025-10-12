/**
 * IP黑名单管理页面
 */
import React, { useState, useEffect } from 'react'
import {
  Card,
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  InputNumber,
  message,
  Popconfirm,
  Statistic,
  Row,
  Col,
  Select,
  Tooltip,
} from 'antd'
import {
  DeleteOutlined,
  PlusOutlined,
  ReloadOutlined,
  SearchOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import ipBlacklistService, {
  IPBlacklistItem,
  AddIPBlacklistRequest,
} from '@/services/ipBlacklistService'
import { formatAWSDate, AWSTag } from '@/utils/awsStyleHelpers'

const IPBlacklist: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [dataSource, setDataSource] = useState<IPBlacklistItem[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [searchText, setSearchText] = useState('')
  const [addModalVisible, setAddModalVisible] = useState(false)
  const [selectedRows, setSelectedRows] = useState<IPBlacklistItem[]>([])
  const [stats, setStats] = useState({
    total_blacklisted: 0,
    permanent_count: 0,
    temporary_count: 0,
    auto_banned_count: 0,
  })
  const [form] = Form.useForm()

  // 加载数据
  const loadData = async () => {
    setLoading(true)
    try {
      const response = await ipBlacklistService.getList({
        page,
        page_size: pageSize,
        search: searchText || undefined,
      })
      setDataSource(response.items)
      setTotal(response.total)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '加载失败')
    } finally {
      setLoading(false)
    }
  }

  // 加载统计数据
  const loadStats = async () => {
    try {
      const data = await ipBlacklistService.getStats()
      setStats(data)
    } catch (error) {
      console.error('加载统计失败:', error)
    }
  }

  useEffect(() => {
    loadData()
    loadStats()
  }, [page, pageSize, searchText])

  // 处理添加
  const handleAdd = async (values: AddIPBlacklistRequest) => {
    try {
      await ipBlacklistService.add(values)
      message.success('添加成功')
      setAddModalVisible(false)
      form.resetFields()
      loadData()
      loadStats()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '添加失败')
    }
  }

  // 处理删除
  const handleDelete = async (ip: string) => {
    try {
      await ipBlacklistService.remove(ip)
      message.success('移除成功')
      loadData()
      loadStats()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '移除失败')
    }
  }

  // 处理批量删除
  const handleBatchDelete = async () => {
    if (selectedRows.length === 0) {
      message.warning('请选择要移除的IP')
      return
    }

    Modal.confirm({
      title: '确认批量移除',
      icon: <ExclamationCircleOutlined />,
      content: `确定要移除选中的 ${selectedRows.length} 个IP吗？`,
      onOk: async () => {
        try {
          const ips = selectedRows.map((row) => row.ip)
          const result = await ipBlacklistService.batchRemove(ips)
          message.success(`成功移除 ${result.success} 个IP`)
          setSelectedRows([])
          loadData()
          loadStats()
        } catch (error: any) {
          message.error(error.response?.data?.detail || '批量移除失败')
        }
      },
    })
  }

  // 计算剩余时间
  const getRemainingTime = (expiresAt: string) => {
    const now = Math.floor(Date.now() / 1000)
    const expires = parseInt(expiresAt)
    const remaining = expires - now

    if (remaining <= 0) return '已过期'

    const hours = Math.floor(remaining / 3600)
    const minutes = Math.floor((remaining % 3600) / 60)

    if (hours > 24) {
      const days = Math.floor(hours / 24)
      return `${days}天${hours % 24}小时`
    }

    return `${hours}小时${minutes}分钟`
  }

  const columns: ColumnsType<IPBlacklistItem> = [
    {
      title: 'IP地址',
      dataIndex: 'ip',
      key: 'ip',
      width: 150,
      fixed: 'left',
      render: (ip: string) => (
        <span style={{ fontFamily: 'Monaco, Menlo, Consolas, monospace', fontSize: '13px', color: '#37352f' }}>
          {ip}
        </span>
      ),
    },
    {
      title: '封禁原因',
      dataIndex: 'reason',
      key: 'reason',
      ellipsis: true,
    },
    {
      title: '封禁类型',
      key: 'type',
      width: 120,
      render: (_, record) =>
        record.is_permanent ? (
          <AWSTag type="error">永久封禁</AWSTag>
        ) : (
          <AWSTag type="warning">临时封禁</AWSTag>
        ),
    },
    {
      title: '封禁时间',
      dataIndex: 'banned_at',
      key: 'banned_at',
      width: 180,
      render: (timestamp: string) => {
        const date = new Date(parseInt(timestamp) * 1000)
        return formatAWSDate(date.toISOString(), 'YYYY-MM-DD HH:mm:ss')
      },
    },
    {
      title: '剩余时间',
      key: 'remaining',
      width: 150,
      render: (_, record) => {
        if (record.is_permanent) {
          return <span style={{ color: '#d13212', fontFamily: 'Monaco, Menlo, Consolas, monospace', fontSize: '13px' }}>永久</span>
        }
        if (record.expires_at) {
          const remaining = getRemainingTime(record.expires_at)
          const date = new Date(parseInt(record.expires_at) * 1000)
          return (
            <Tooltip title={`到期时间: ${formatAWSDate(date.toISOString(), 'YYYY-MM-DD HH:mm:ss')}`}>
              <span style={{ color: '#ff9900', fontFamily: 'Monaco, Menlo, Consolas, monospace', fontSize: '13px' }}>{remaining}</span>
            </Tooltip>
          )
        }
        return '-'
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Popconfirm
            title="确定要移除此IP吗？"
            onConfirm={() => handleDelete(record.ip)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger size="small" icon={<DeleteOutlined />}>
              移除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div style={{ padding: '24px' }}>
      <h2>IP黑名单管理</h2>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总封禁数"
              value={stats.total_blacklisted}
              prefix={<ExclamationCircleOutlined style={{ color: '#d13212', fontSize: 24 }} />}
              valueStyle={{ color: '#d13212', fontFamily: 'Monaco, Menlo, Consolas, monospace' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="永久封禁"
              value={stats.permanent_count}
              prefix={<CheckCircleOutlined style={{ color: '#d13212', fontSize: 24 }} />}
              valueStyle={{ color: '#d13212', fontFamily: 'Monaco, Menlo, Consolas, monospace' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="临时封禁"
              value={stats.temporary_count}
              prefix={<ClockCircleOutlined style={{ color: '#ff9900', fontSize: 24 }} />}
              valueStyle={{ color: '#ff9900', fontFamily: 'Monaco, Menlo, Consolas, monospace' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="自动封禁(7天)"
              value={stats.auto_banned_count}
              valueStyle={{ color: '#0073bb', fontFamily: 'Monaco, Menlo, Consolas, monospace' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Space style={{ marginBottom: 16 }}>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setAddModalVisible(true)}
          >
            添加IP
          </Button>
          <Button
            danger
            icon={<DeleteOutlined />}
            onClick={handleBatchDelete}
            disabled={selectedRows.length === 0}
          >
            批量移除 ({selectedRows.length})
          </Button>
          <Button icon={<ReloadOutlined />} onClick={loadData}>
            刷新
          </Button>
        </Space>

        <Input.Search
          placeholder="搜索IP地址"
          allowClear
          enterButton={<SearchOutlined />}
          onSearch={(value) => {
            setSearchText(value)
            setPage(1)
          }}
          style={{ width: 300 }}
        />
      </Card>

      {/* 数据表格 */}
      <Card>
        <Table
          columns={columns}
          dataSource={dataSource}
          rowKey="ip"
          loading={loading}
          scroll={{ x: 1200 }}
          rowSelection={{
            selectedRowKeys: selectedRows.map((row) => row.ip),
            onChange: (_, rows) => setSelectedRows(rows),
          }}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => {
              setPage(page)
              setPageSize(pageSize)
            },
          }}
        />
      </Card>

      {/* 添加IP Modal */}
      <Modal
        title="添加IP到黑名单"
        open={addModalVisible}
        onOk={() => form.submit()}
        onCancel={() => {
          setAddModalVisible(false)
          form.resetFields()
        }}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleAdd}
          initialValues={{ duration_type: 'permanent' }}
        >
          <Form.Item
            name="ip"
            label="IP地址"
            rules={[
              { required: true, message: '请输入IP地址' },
              {
                pattern: /^(?:\d{1,3}\.){3}\d{1,3}$/,
                message: '请输入有效的IPv4地址',
              },
            ]}
          >
            <Input placeholder="例如: 192.168.1.100" />
          </Form.Item>

          <Form.Item
            name="reason"
            label="封禁原因"
            rules={[{ required: true, message: '请输入封禁原因' }]}
          >
            <Input.TextArea
              rows={3}
              placeholder="请说明封禁原因，如：恶意攻击、滥用API等"
            />
          </Form.Item>

          <Form.Item name="duration_type" label="封禁时长">
            <Select
              onChange={(value) => {
                if (value === 'permanent') {
                  form.setFieldValue('duration', undefined)
                }
              }}
            >
              <Select.Option value="permanent">永久封禁</Select.Option>
              <Select.Option value="temporary">临时封禁</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item noStyle shouldUpdate={(prev, curr) => prev.duration_type !== curr.duration_type}>
            {({ getFieldValue }) =>
              getFieldValue('duration_type') === 'temporary' && (
                <Form.Item
                  name="duration"
                  label="封禁时长(秒)"
                  rules={[{ required: true, message: '请输入封禁时长' }]}
                >
                  <InputNumber
                    min={60}
                    style={{ width: '100%' }}
                    placeholder="单位: 秒 (最少60秒)"
                    addonAfter={
                      <span>
                        常用: 1小时=3600, 1天=86400, 1周=604800
                      </span>
                    }
                  />
                </Form.Item>
              )
            }
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default IPBlacklist
