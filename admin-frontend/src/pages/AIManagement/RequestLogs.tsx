import React, { useState, useEffect } from 'react';
import {
  Table,
  Card,
  Space,
  Tag,
  Button,
  DatePicker,
  Select,
  Input,
  message,
  Modal,
  Descriptions,
  Typography,
  Statistic,
  Row,
  Col,
  Drawer,
} from 'antd';
import {
  ReloadOutlined,
  DeleteOutlined,
  EyeOutlined,
  FilterOutlined,
  ClearOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import {
  getRequestLogs,
  getRequestLog,
  deleteRequestLog,
  type AIRequestLog,
  type RequestLogsParams,
} from '../../services/ai-logs';
import '../../styles/page-layout.css';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { Text } = Typography;

const RequestLogs: React.FC = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<AIRequestLog[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [selectedLog, setSelectedLog] = useState<AIRequestLog | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);

  // Filters
  const [filters, setFilters] = useState<RequestLogsParams>({});
  const [providerFilter, setProviderFilter] = useState<string | undefined>();
  const [modelFilter, setModelFilter] = useState<string | undefined>();
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>(null);

  useEffect(() => {
    fetchLogs();
  }, [currentPage, pageSize, filters]);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params: RequestLogsParams = {
        skip: (currentPage - 1) * pageSize,
        limit: pageSize,
        ...filters,
      };
      const data = await getRequestLogs(params);
      setLogs(data.logs || []);
      setTotal(data.total || 0);
    } catch (error) {
      message.error(t('message.loadFailed'));
      console.error('Failed to fetch logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyFilters = () => {
    const newFilters: RequestLogsParams = {};
    if (providerFilter) newFilters.provider_type = providerFilter;
    if (modelFilter) newFilters.model = modelFilter;
    if (statusFilter) newFilters.status = statusFilter;
    if (dateRange) {
      newFilters.start_date = dateRange[0].format('YYYY-MM-DD');
      newFilters.end_date = dateRange[1].format('YYYY-MM-DD');
    }
    setFilters(newFilters);
    setCurrentPage(1);
  };

  const handleClearFilters = () => {
    setProviderFilter(undefined);
    setModelFilter(undefined);
    setStatusFilter(undefined);
    setDateRange(null);
    setFilters({});
    setCurrentPage(1);
  };

  const handleViewDetail = async (logId: number) => {
    try {
      const log = await getRequestLog(logId);
      setSelectedLog(log);
      setDetailVisible(true);
    } catch (error) {
      message.error(t('message.loadFailed'));
    }
  };

  const handleDelete = (logId: number) => {
    Modal.confirm({
      title: t('common.confirmDelete'),
      content: t('aiManagement.confirmDeleteLog'),
      onOk: async () => {
        try {
          await deleteRequestLog(logId);
          message.success(t('message.deleteSuccess'));
          fetchLogs();
        } catch (error) {
          message.error(t('message.deleteFailed'));
        }
      },
    });
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      success: 'green',
      failed: 'red',
      timeout: 'orange',
    };
    return colors[status] || 'default';
  };

  const columns: ColumnsType<AIRequestLog> = [
    {
      title: t('common.time'),
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text: string) => dayjs(text).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: t('aiManagement.provider'),
      dataIndex: 'provider_type',
      key: 'provider_type',
      width: 120,
      render: (text: string) => <Tag color="blue">{text.toUpperCase()}</Tag>,
    },
    {
      title: t('aiManagement.model'),
      dataIndex: 'model',
      key: 'model',
      width: 150,
      ellipsis: true,
    },
    {
      title: t('aiManagement.requestType'),
      dataIndex: 'request_type',
      key: 'request_type',
      width: 100,
    },
    {
      title: t('aiManagement.tokens'),
      dataIndex: 'total_tokens',
      key: 'total_tokens',
      width: 100,
      render: (tokens: number, record: AIRequestLog) => (
        <span title={`${t('common.prompt')}: ${record.prompt_tokens}, ${t('common.completion')}: ${record.completion_tokens}`}>
          {tokens.toLocaleString()}
        </span>
      ),
    },
    {
      title: t('aiManagement.responseTime'),
      dataIndex: 'response_time',
      key: 'response_time',
      width: 120,
      render: (time: number) => `${time.toFixed(2)}s`,
    },
    {
      title: t('aiManagement.cost'),
      dataIndex: 'estimated_cost',
      key: 'estimated_cost',
      width: 100,
      render: (cost: number) => `$${cost.toFixed(4)}`,
    },
    {
      title: t('common.status'),
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>{status.toUpperCase()}</Tag>
      ),
    },
    {
      title: t('common.actions'),
      key: 'actions',
      width: 150,
      fixed: 'right',
      render: (_: any, record: AIRequestLog) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record.id)}
          >
            {t('common.detail')}
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            {t('common.delete')}
          </Button>
        </Space>
      ),
    },
  ];

  // Calculate statistics
  const totalCost = logs.reduce((sum, log) => sum + log.estimated_cost, 0);
  const totalTokens = logs.reduce((sum, log) => sum + log.total_tokens, 0);
  const successCount = logs.filter((log) => log.status === 'success').length;
  const successRate = logs.length > 0 ? (successCount / logs.length) * 100 : 0;

  return (
    <div className="page-container">
      <div className="page-header">
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={{ margin: 0 }}>{t('aiManagement.requestLogs')}</h2>
            <Button icon={<ReloadOutlined />} onClick={fetchLogs}>
              {t('common.refresh')}
            </Button>
          </div>

          <Row gutter={16}>
            <Col span={6}>
              <Card>
                <Statistic
                  title={t('aiManagement.totalRequests')}
                  value={total}
                  valueStyle={{ color: '#3f8600' }}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title={t('aiManagement.totalTokens')}
                  value={totalTokens}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title={t('aiManagement.totalCost')}
                  value={totalCost}
                  prefix="$"
                  precision={4}
                  valueStyle={{ color: '#cf1322' }}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title={t('aiManagement.successRate')}
                  value={successRate}
                  suffix="%"
                  precision={1}
                  valueStyle={{ color: successRate > 90 ? '#3f8600' : '#faad14' }}
                />
              </Card>
            </Col>
          </Row>

          <Card size="small">
            <Space wrap>
              <Select
                placeholder={t('aiManagement.selectProvider')}
                style={{ width: 150 }}
                allowClear
                value={providerFilter}
                onChange={setProviderFilter}
              >
                <Option value="openai">OpenAI</Option>
                <Option value="grok">Grok</Option>
                <Option value="google">Google</Option>
              </Select>

              <Input
                placeholder={t('aiManagement.modelName')}
                style={{ width: 200 }}
                allowClear
                value={modelFilter}
                onChange={(e) => setModelFilter(e.target.value)}
              />

              <Select
                placeholder={t('common.status')}
                style={{ width: 120 }}
                allowClear
                value={statusFilter}
                onChange={setStatusFilter}
              >
                <Option value="success">{t('common.success')}</Option>
                <Option value="failed">{t('common.failed')}</Option>
                <Option value="timeout">{t('common.timeout')}</Option>
              </Select>

              <RangePicker
                value={dateRange}
                onChange={(dates) => setDateRange(dates as [dayjs.Dayjs, dayjs.Dayjs] | null)}
              />

              <Button
                type="primary"
                icon={<FilterOutlined />}
                onClick={handleApplyFilters}
              >
                {t('common.filter')}
              </Button>

              <Button icon={<ClearOutlined />} onClick={handleClearFilters}>
                {t('common.clearFilters')}
              </Button>
            </Space>
          </Card>
        </Space>
      </div>

      <div className="page-content">
        <Table
          columns={columns}
          dataSource={logs}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1400 }}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => t('common.totalItems', { total }),
            onChange: (page, size) => {
              setCurrentPage(page);
              setPageSize(size);
            },
          }}
        />
      </div>

      <Drawer
        title={t('aiManagement.logDetail')}
        placement="right"
        width={720}
        open={detailVisible}
        onClose={() => setDetailVisible(false)}
      >
        {selectedLog && (
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <Descriptions title={t('aiManagement.basicInfo')} bordered column={2}>
              <Descriptions.Item label={t('common.id')}>{selectedLog.id}</Descriptions.Item>
              <Descriptions.Item label={t('common.time')}>
                {dayjs(selectedLog.created_at).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
              <Descriptions.Item label={t('aiManagement.provider')}>
                <Tag color="blue">{selectedLog.provider_type.toUpperCase()}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label={t('aiManagement.model')}>
                {selectedLog.model}
              </Descriptions.Item>
              <Descriptions.Item label={t('aiManagement.requestType')}>
                {selectedLog.request_type}
              </Descriptions.Item>
              <Descriptions.Item label={t('common.status')}>
                <Tag color={getStatusColor(selectedLog.status)}>
                  {selectedLog.status.toUpperCase()}
                </Tag>
              </Descriptions.Item>
            </Descriptions>

            <Descriptions title={t('aiManagement.usageStats')} bordered column={2}>
              <Descriptions.Item label={t('aiManagement.promptTokens')}>
                {selectedLog.prompt_tokens.toLocaleString()}
              </Descriptions.Item>
              <Descriptions.Item label={t('aiManagement.completionTokens')}>
                {selectedLog.completion_tokens.toLocaleString()}
              </Descriptions.Item>
              <Descriptions.Item label={t('aiManagement.totalTokens')}>
                {selectedLog.total_tokens.toLocaleString()}
              </Descriptions.Item>
              <Descriptions.Item label={t('aiManagement.responseTime')}>
                {selectedLog.response_time.toFixed(2)}s
              </Descriptions.Item>
              <Descriptions.Item label={t('aiManagement.estimatedCost')} span={2}>
                ${selectedLog.estimated_cost.toFixed(4)}
              </Descriptions.Item>
            </Descriptions>

            {selectedLog.prompt && (
              <Card title={t('aiManagement.prompt')} size="small">
                <Text code style={{ whiteSpace: 'pre-wrap' }}>
                  {selectedLog.prompt}
                </Text>
              </Card>
            )}

            {selectedLog.response && (
              <Card title={t('aiManagement.response')} size="small">
                <Text code style={{ whiteSpace: 'pre-wrap' }}>
                  {selectedLog.response}
                </Text>
              </Card>
            )}

            {selectedLog.error_message && (
              <Card title={t('common.error')} size="small">
                <Text type="danger">{selectedLog.error_message}</Text>
              </Card>
            )}

            {selectedLog.request_metadata && (
              <Card title={t('aiManagement.metadata')} size="small">
                <pre>{JSON.stringify(selectedLog.request_metadata, null, 2)}</pre>
              </Card>
            )}

            <Descriptions bordered column={2}>
              <Descriptions.Item label={t('aiManagement.ipAddress')}>
                {selectedLog.ip_address || 'N/A'}
              </Descriptions.Item>
              <Descriptions.Item label={t('aiManagement.userAgent')} span={2}>
                {selectedLog.user_agent || 'N/A'}
              </Descriptions.Item>
            </Descriptions>
          </Space>
        )}
      </Drawer>
    </div>
  );
};

export default RequestLogs;
