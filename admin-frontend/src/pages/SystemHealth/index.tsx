import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Card,
  Row,
  Col,
  Statistic,
  Progress,
  Tag,
  Space,
  Typography,
  Spin,
  Alert,
  Descriptions,
  Switch,
  Badge,
  Select,
  Tabs,
  Button,
  Modal,
  Table,
  Divider,
} from 'antd';
import {
  CheckCircleOutlined,
  WarningOutlined,
  CloseCircleOutlined,
  DatabaseOutlined,
  CloudOutlined,
  HddOutlined,
  ThunderboltOutlined,
  ReloadOutlined,
  ApiOutlined,
  LineChartOutlined,
  DownloadOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { getSystemHealth, type HealthData } from '@/services/systemHealthService';
import MetricsChart from './MetricsChart';
import { exportHealthReport } from './exportUtils';

const { Title, Text } = Typography;

const SystemHealth = () => {
  const { t } = useTranslation();
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(10000); // 10 seconds
  const [activeTab, setActiveTab] = useState('overview');
  const [celeryModalVisible, setCeleryModalVisible] = useState(false);

  const { data, isLoading, error, refetch } = useQuery<HealthData>({
    queryKey: ['system-health'],
    queryFn: () => getSystemHealth(true),
    refetchInterval: autoRefresh ? refreshInterval : false,
    refetchIntervalInBackground: true,
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'success';
      case 'degraded':
      case 'warning':
        return 'warning';
      case 'unhealthy':
      case 'critical':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'degraded':
      case 'warning':
        return <WarningOutlined style={{ color: '#faad14' }} />;
      case 'unhealthy':
      case 'critical':
        return <CloseCircleOutlined style={{ color: '#f5222d' }} />;
      default:
        return null;
    }
  };

  const getProgressStatus = (percent: number) => {
    if (percent < 60) return 'success';
    if (percent < 80) return 'normal';
    if (percent < 95) return 'exception';
    return 'exception';
  };

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip={t('common.loading')} />
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message={t('systemHealth.errors.loadFailed')}
        description={error instanceof Error ? error.message : t('systemHealth.errors.unknownError')}
        type="error"
        showIcon
      />
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Space align="center">
          <Title level={2} style={{ margin: 0 }}>
            {t('systemHealth.title')}
          </Title>
          <Badge
            status={data?.overall_status === 'healthy' ? 'success' : data?.overall_status === 'degraded' ? 'warning' : 'error'}
            text={t(`systemHealth.${data?.overall_status || 'unknown'}`).toUpperCase()}
          />
        </Space>
        <Space>
          <Button
            icon={<DownloadOutlined />}
            onClick={() => data && exportHealthReport(data, t)}
            disabled={!data}
          >
            {t('systemHealth.export.button')}
          </Button>
          <Text type="secondary">{t('systemHealth.refreshInterval')}:</Text>
          <Select
            value={refreshInterval}
            onChange={setRefreshInterval}
            style={{ width: 120 }}
            size="small"
            options={[
              { label: t('systemHealth.intervals.5seconds'), value: 5000 },
              { label: t('systemHealth.intervals.10seconds'), value: 10000 },
              { label: t('systemHealth.intervals.30seconds'), value: 30000 },
              { label: t('systemHealth.intervals.1minute'), value: 60000 },
            ]}
          />
          <Switch checked={autoRefresh} onChange={setAutoRefresh} />
          <Text type="secondary" style={{ fontSize: 12 }}>
            {t('systemHealth.lastUpdated')}: {data?.timestamp ? new Date(data.timestamp).toLocaleTimeString() : '-'}
          </Text>
          <ReloadOutlined
            spin={isLoading}
            onClick={() => refetch()}
            style={{ fontSize: 18, cursor: 'pointer', color: '#1890ff' }}
          />
        </Space>
      </div>

      {/* Overall Status */}
      {data?.overall_status !== 'healthy' && (
        <Alert
          message={t(`systemHealth.status.system${data?.overall_status === 'degraded' ? 'Degraded' : 'Unhealthy'}`)}
          description={t('systemHealth.status.issuesDetected')}
          type={data?.overall_status === 'degraded' ? 'warning' : 'error'}
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {/* Services Health */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {/* Database */}
        <Col xs={24} lg={6}>
          <Card
            title={
              <Space>
                <DatabaseOutlined />
                <span>{t('systemHealth.services.database')}</span>
                {getStatusIcon(data?.services.database.status || 'unknown')}
              </Space>
            }
            extra={
              <Tag color={getStatusColor(data?.services.database.status || 'default')}>
                {data?.services.database.status?.toUpperCase()}
              </Tag>
            }
          >
            <Descriptions column={1} size="small">
              {data?.services.database.database_name && (
                <Descriptions.Item label="Database">
                  <Text strong style={{ fontSize: 12 }}>{data.services.database.database_name}</Text>
                </Descriptions.Item>
              )}
              {data?.services.database.database_version && (
                <Descriptions.Item label="Version">
                  <Text type="secondary" style={{ fontSize: 11 }}>{data.services.database.database_version}</Text>
                </Descriptions.Item>
              )}
              <Descriptions.Item label={t('systemHealth.sla.columns.responseTime')}>
                {data?.services.database.response_time_ms
                  ? `${data.services.database.response_time_ms.toFixed(2)} ms`
                  : '-'}
              </Descriptions.Item>
              <Descriptions.Item label={t('systemHealth.labels.poolSize')}>
                {data?.services.database.pool_size || '-'}
              </Descriptions.Item>
              <Descriptions.Item label={t('systemHealth.labels.checkedOut')}>
                {data?.services.database.checked_out || 0}
              </Descriptions.Item>
              <Descriptions.Item label={t('systemHealth.labels.available')}>
                {data?.services.database.checked_in || 0}
              </Descriptions.Item>
              <Descriptions.Item label={t('systemHealth.labels.poolUtilization')}>
                <Progress
                  percent={data?.services.database.utilization_percent || 0}
                  size="small"
                  status={getProgressStatus(data?.services.database.utilization_percent || 0)}
                />
              </Descriptions.Item>
            </Descriptions>
            {data?.services.database.error && (
              <Alert
                message={data.services.database.error}
                type="error"
                showIcon
                style={{ marginTop: 8 }}
              />
            )}
          </Card>
        </Col>

        {/* Redis */}
        <Col xs={24} lg={6}>
          <Card
            title={
              <Space>
                <ThunderboltOutlined />
                <span>{t('systemHealth.services.redis')}</span>
                {getStatusIcon(data?.services.redis.status || 'unknown')}
              </Space>
            }
            extra={
              <Tag color={getStatusColor(data?.services.redis.status || 'default')}>
                {data?.services.redis.status?.toUpperCase()}
              </Tag>
            }
          >
            <Descriptions column={1} size="small">
              <Descriptions.Item label={t('systemHealth.sla.columns.responseTime')}>
                {data?.services.redis.response_time_ms
                  ? `${data.services.redis.response_time_ms.toFixed(2)} ms`
                  : '-'}
              </Descriptions.Item>
              <Descriptions.Item label={t('systemHealth.labels.usedMemory')}>
                {data?.services.redis.used_memory_mb
                  ? `${data.services.redis.used_memory_mb.toFixed(2)} MB`
                  : '-'}
              </Descriptions.Item>
              <Descriptions.Item label={t('systemHealth.labels.maxMemory')}>
                {typeof data?.services.redis.max_memory_mb === 'number'
                  ? `${data.services.redis.max_memory_mb.toFixed(2)} MB`
                  : data?.services.redis.max_memory_mb || '-'}
              </Descriptions.Item>
              <Descriptions.Item label={t('systemHealth.labels.keysCount')}>
                {data?.services.redis.keys_count?.toLocaleString() || 0}
              </Descriptions.Item>
              {data?.services.redis.memory_utilization_percent !== null &&
                data?.services.redis.memory_utilization_percent !== undefined && (
                  <Descriptions.Item label={t('systemHealth.labels.memoryUtilization')}>
                    <Progress
                      percent={data.services.redis.memory_utilization_percent}
                      size="small"
                      status={getProgressStatus(data.services.redis.memory_utilization_percent)}
                    />
                  </Descriptions.Item>
                )}
            </Descriptions>
            {data?.services.redis.error && (
              <Alert message={data.services.redis.error} type="error" showIcon style={{ marginTop: 8 }} />
            )}
          </Card>
        </Col>

        {/* Storage */}
        <Col xs={24} lg={6}>
          <Card
            title={
              <Space>
                <CloudOutlined />
                <span>{t('systemHealth.services.storage')}</span>
                {getStatusIcon(data?.services.storage.status || 'unknown')}
              </Space>
            }
            extra={
              <Tag color={getStatusColor(data?.services.storage.status || 'default')}>
                {data?.services.storage.status?.toUpperCase()}
              </Tag>
            }
          >
            <Descriptions column={1} size="small">
              <Descriptions.Item label={t('systemHealth.sla.columns.responseTime')}>
                {data?.services.storage.response_time_ms
                  ? `${data.services.storage.response_time_ms.toFixed(2)} ms`
                  : '-'}
              </Descriptions.Item>
              {data?.services.storage.used_gb !== undefined && (
                <Descriptions.Item label={t('systemHealth.labels.storageUsed')}>
                  {data.services.storage.used_gb.toFixed(2)} GB
                </Descriptions.Item>
              )}
              {data?.services.storage.object_count !== undefined && (
                <Descriptions.Item label={t('systemHealth.labels.objects')}>
                  {data.services.storage.object_count.toLocaleString()}
                </Descriptions.Item>
              )}
              {data?.services.storage.utilization_percent !== undefined && (
                <Descriptions.Item label={t('systemHealth.labels.utilization')}>
                  <Progress
                    percent={data.services.storage.utilization_percent}
                    size="small"
                    status={getProgressStatus(data.services.storage.utilization_percent)}
                  />
                </Descriptions.Item>
              )}
              <Descriptions.Item label={t('systemHealth.labels.bucketStatus')}>
                <Tag color={data?.services.storage.bucket_exists ? 'success' : 'error'}>
                  {data?.services.storage.bucket_exists ? t('systemHealth.bucket.exists') : t('systemHealth.bucket.notFound')}
                </Tag>
              </Descriptions.Item>
              {data?.services.storage.buckets_count !== undefined && (
                <Descriptions.Item label="Buckets">
                  <Badge count={data.services.storage.buckets_count} showZero style={{ backgroundColor: '#52c41a' }} />
                </Descriptions.Item>
              )}
            </Descriptions>

            {/* Buckets List */}
            {data?.services.storage.buckets && data.services.storage.buckets.length > 0 && (
              <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid #f0f0f0' }}>
                <Text type="secondary" style={{ fontSize: 12, fontWeight: 500 }}>Storage Buckets:</Text>
                {data.services.storage.buckets.map((bucket, idx) => (
                  <div key={idx} style={{ marginTop: 8, padding: '6px 8px', background: '#f5f5f5', borderRadius: 4 }}>
                    <Space direction="vertical" size={2} style={{ width: '100%' }}>
                      <Space size={4}>
                        <HddOutlined style={{ fontSize: 12, color: '#1890ff' }} />
                        <Text strong style={{ fontSize: 12 }}>{bucket.name}</Text>
                      </Space>
                      {bucket.error ? (
                        <Text type="danger" style={{ fontSize: 11 }}>{bucket.error}</Text>
                      ) : (
                        <>
                          <Text type="secondary" style={{ fontSize: 11 }}>
                            {bucket.object_count?.toLocaleString() || 0} objects • {bucket.size_gb?.toFixed(3) || 0} GB
                          </Text>
                        </>
                      )}
                    </Space>
                  </div>
                ))}
              </div>
            )}

            {data?.services.storage.error && (
              <Alert
                message={data.services.storage.error}
                type="error"
                showIcon
                style={{ marginTop: 8 }}
              />
            )}
          </Card>
        </Col>

        {/* Celery */}
        <Col xs={24} lg={6}>
          <Card
            title={
              <Space>
                <ThunderboltOutlined />
                <span>{t('systemHealth.services.celery')}</span>
                {getStatusIcon(data?.services.celery?.status || 'unknown')}
              </Space>
            }
            extra={
              <Space>
                <Tag color={getStatusColor(data?.services.celery?.status || 'default')}>
                  {data?.services.celery?.status?.toUpperCase() || 'UNKNOWN'}
                </Tag>
                <Button
                  type="link"
                  size="small"
                  icon={<EyeOutlined />}
                  onClick={() => setCeleryModalVisible(true)}
                >
                  Details
                </Button>
              </Space>
            }
          >
            <Descriptions column={1} size="small">
              <Descriptions.Item label={t('systemHealth.labels.workers')}>
                <Badge
                  count={data?.services.celery?.workers_count || 0}
                  showZero
                  style={{
                    backgroundColor:
                      (data?.services.celery?.workers_count || 0) > 0 ? '#52c41a' : '#f5222d',
                  }}
                />
              </Descriptions.Item>
              <Descriptions.Item label={t('systemHealth.labels.activeTasks')}>
                <Badge count={data?.services.celery?.active_tasks || 0} showZero style={{ backgroundColor: '#1890ff' }} />
              </Descriptions.Item>
              <Descriptions.Item label={t('systemHealth.labels.reservedTasks')}>
                {data?.services.celery?.reserved_tasks || 0}
              </Descriptions.Item>
              {data?.services.celery?.scheduled_tasks !== undefined && (
                <Descriptions.Item label="Scheduled">
                  {data.services.celery.scheduled_tasks}
                </Descriptions.Item>
              )}
              {data?.services.celery?.total_succeeded !== undefined && (
                <Descriptions.Item label="Succeeded">
                  <Text type="success">{data.services.celery.total_succeeded.toLocaleString()}</Text>
                </Descriptions.Item>
              )}
              {data?.services.celery?.total_failed !== undefined && (
                <Descriptions.Item label="Failed">
                  <Text type="danger">{data.services.celery.total_failed.toLocaleString()}</Text>
                </Descriptions.Item>
              )}
            </Descriptions>

            {/* Active Tasks List */}
            {data?.services.celery?.active_task_list && data.services.celery.active_task_list.length > 0 && (
              <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid #f0f0f0' }}>
                <Text type="secondary" style={{ fontSize: 12, fontWeight: 500 }}>Active Tasks:</Text>
                {data.services.celery.active_task_list.map((task, idx) => (
                  <div key={idx} style={{ marginTop: 8, padding: '6px 8px', background: '#e6f7ff', borderRadius: 4 }}>
                    <Space direction="vertical" size={2} style={{ width: '100%' }}>
                      <Text strong style={{ fontSize: 11 }}>{task.task_name.split('.').pop()}</Text>
                      <Text type="secondary" style={{ fontSize: 10 }}>ID: {task.task_id.substring(0, 8)}...</Text>
                    </Space>
                  </div>
                ))}
              </div>
            )}
            {data?.services.celery?.error && (
              <Alert
                message={data.services.celery.error}
                type="error"
                showIcon
                style={{ marginTop: 8 }}
              />
            )}
          </Card>
        </Col>
      </Row>

      {/* Alerts Summary */}
      {data?.alerts && data.alerts.statistics.active_total > 0 && (
        <Alert
          message={t('systemHealth.alertsSummary.title', {
            total: data.alerts.statistics.active_total,
            critical: data.alerts.statistics.critical,
            warnings: data.alerts.statistics.warning,
          })}
          description={t('systemHealth.alertsSummary.description', {
            resolved: data.alerts.statistics.resolved_24h,
          })}
          type={data.alerts.statistics.critical > 0 ? 'error' : 'warning'}
          showIcon
          style={{ marginBottom: 24 }}
          action={
            <Button size="small" type="link" href="#/system-health/alerts">
              {t('systemHealth.actions.viewDetails')}
            </Button>
          }
        />
      )}

      {/* Tabs for Overview and Trends */}
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={[
          {
            key: 'overview',
            label: (
              <span>
                <ApiOutlined /> {t('systemHealth.tabs.overview')}
              </span>
            ),
            children: (
              <>
                {/* System Resources */}
                <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
                  <Col span={24}>
                    <Card title={<Space><HddOutlined /> {t('systemHealth.resources.title')}</Space>}>
                      <Row gutter={[24, 24]}>
                        {/* CPU */}
                        <Col xs={24} md={6}>
                          <Card type="inner" title={t('systemHealth.cpu.title')}>
                            <Statistic
                              value={data?.system_resources.cpu?.usage_percent || 0}
                              suffix="%"
                              valueStyle={{
                                color:
                                  (data?.system_resources.cpu?.usage_percent || 0) < 70
                                    ? '#52c41a'
                                    : (data?.system_resources.cpu?.usage_percent || 0) < 90
                                    ? '#faad14'
                                    : '#f5222d',
                              }}
                            />
                            <Progress
                              percent={data?.system_resources.cpu?.usage_percent || 0}
                              status={getProgressStatus(data?.system_resources.cpu?.usage_percent || 0)}
                              style={{ marginTop: 16 }}
                            />
                            <div style={{ marginTop: 8, fontSize: 12, color: '#999' }}>
                              {data?.system_resources.cpu?.cores || 0} {t('common.units.cores')}
                              {data?.system_resources.cpu?.frequency_mhz &&
                                ` @ ${data.system_resources.cpu.frequency_mhz} MHz`}
                            </div>
                          </Card>
                        </Col>

                        {/* Memory */}
                        <Col xs={24} md={6}>
                          <Card type="inner" title={t('systemHealth.memory.title')}>
                            <Statistic
                              value={data?.system_resources.memory?.usage_percent || 0}
                              suffix="%"
                              valueStyle={{
                                color:
                                  (data?.system_resources.memory?.usage_percent || 0) < 70
                                    ? '#52c41a'
                                    : (data?.system_resources.memory?.usage_percent || 0) < 90
                                    ? '#faad14'
                                    : '#f5222d',
                              }}
                            />
                            <Progress
                              percent={data?.system_resources.memory?.usage_percent || 0}
                              status={getProgressStatus(data?.system_resources.memory?.usage_percent || 0)}
                              style={{ marginTop: 16 }}
                            />
                            <div style={{ marginTop: 8, fontSize: 12, color: '#999' }}>
                              {data?.system_resources.memory?.used_gb?.toFixed(2) || 0} GB /{' '}
                              {data?.system_resources.memory?.total_gb?.toFixed(2) || 0} GB
                            </div>
                          </Card>
                        </Col>

                        {/* Disk */}
                        <Col xs={24} md={6}>
                          <Card type="inner" title={t('systemHealth.disk.title')}>
                            <Statistic
                              value={data?.system_resources.disk?.usage_percent || 0}
                              suffix="%"
                              valueStyle={{
                                color:
                                  (data?.system_resources.disk?.usage_percent || 0) < 70
                                    ? '#52c41a'
                                    : (data?.system_resources.disk?.usage_percent || 0) < 90
                                    ? '#faad14'
                                    : '#f5222d',
                              }}
                            />
                            <Progress
                              percent={data?.system_resources.disk?.usage_percent || 0}
                              status={getProgressStatus(data?.system_resources.disk?.usage_percent || 0)}
                              style={{ marginTop: 16 }}
                            />
                            <div style={{ marginTop: 8, fontSize: 12, color: '#999' }}>
                              {data?.system_resources.disk?.free_gb?.toFixed(2) || 0} GB {t('common.units.free')}
                            </div>
                          </Card>
                        </Col>

                        {/* Processes */}
                        <Col xs={24} md={6}>
                          <Card type="inner" title={t('systemHealth.processes.title')}>
                            <Statistic
                              value={data?.system_resources.processes?.count || 0}
                              valueStyle={{ color: '#1890ff' }}
                            />
                            <div style={{ marginTop: 24, fontSize: 12, color: '#999' }}>
                              {t('systemHealth.processes.active')}
                            </div>
                          </Card>
                        </Col>
                      </Row>
                    </Card>
                  </Col>
                </Row>

                {/* Network Stats */}
                {data?.system_resources.network && (
                  <Row gutter={[16, 16]}>
                    <Col span={24}>
                      <Card title={t('systemHealth.network.title')}>
                        <Row gutter={[16, 16]}>
                          <Col xs={12} md={6}>
                            <Statistic
                              title={t('systemHealth.network.dataSent')}
                              value={data.system_resources.network.bytes_sent_gb}
                              suffix="GB"
                              precision={2}
                            />
                          </Col>
                          <Col xs={12} md={6}>
                            <Statistic
                              title={t('systemHealth.network.dataReceived')}
                              value={data.system_resources.network.bytes_recv_gb}
                              suffix="GB"
                              precision={2}
                            />
                          </Col>
                          <Col xs={12} md={6}>
                            <Statistic
                              title={t('systemHealth.network.packetsSent')}
                              value={data.system_resources.network.packets_sent}
                              formatter={(value) => value.toLocaleString()}
                            />
                          </Col>
                          <Col xs={12} md={6}>
                            <Statistic
                              title={t('systemHealth.network.packetsReceived')}
                              value={data.system_resources.network.packets_recv}
                              formatter={(value) => value.toLocaleString()}
                            />
                          </Col>
                        </Row>
                      </Card>
                    </Col>
                  </Row>
                )}
              </>
            ),
          },
          {
            key: 'trends',
            label: (
              <span>
                <LineChartOutlined /> {t('systemHealth.tabs.trends')}
              </span>
            ),
            children: (
              <Row gutter={[16, 16]}>
                <Col xs={24} lg={12}>
                  <MetricsChart metric="cpu_usage" title={t('systemHealth.charts.cpuTrend')} unit="%" />
                </Col>
                <Col xs={24} lg={12}>
                  <MetricsChart metric="memory_usage" title={t('systemHealth.charts.memoryTrend')} unit="%" />
                </Col>
                <Col xs={24} lg={12}>
                  <MetricsChart metric="disk_usage" title={t('systemHealth.charts.diskTrend')} unit="%" />
                </Col>
                <Col xs={24} lg={12}>
                  <MetricsChart
                    metric="db_response_time"
                    title={t('systemHealth.charts.dbResponseTime')}
                    unit=" ms"
                  />
                </Col>
                <Col xs={24} lg={12}>
                  <MetricsChart
                    metric="redis_response_time"
                    title={t('systemHealth.charts.redisResponseTime')}
                    unit=" ms"
                  />
                </Col>
                <Col xs={24} lg={12}>
                  <MetricsChart
                    metric="storage_response_time"
                    title={t('systemHealth.charts.storageResponseTime')}
                    unit=" ms"
                  />
                </Col>
              </Row>
            ),
          },
        ]}
      />

      {/* Celery Task Queue Details Modal */}
      <Modal
        title={
          <Space>
            <ThunderboltOutlined />
            <span>Celery Task Queue Details</span>
          </Space>
        }
        open={celeryModalVisible}
        onCancel={() => setCeleryModalVisible(false)}
        width={900}
        footer={[
          <Button key="close" onClick={() => setCeleryModalVisible(false)}>
            Close
          </Button>,
        ]}
      >
        {data?.services.celery && (
          <div>
            {/* Summary Statistics */}
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={6}>
                <Statistic
                  title="Workers"
                  value={data.services.celery.workers_count}
                  valueStyle={{ color: data.services.celery.workers_count > 0 ? '#3f8600' : '#cf1322' }}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Active Tasks"
                  value={data.services.celery.active_tasks || 0}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Succeeded"
                  value={data.services.celery.total_succeeded || 0}
                  valueStyle={{ color: '#3f8600' }}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Failed"
                  value={data.services.celery.total_failed || 0}
                  valueStyle={{ color: '#cf1322' }}
                />
              </Col>
            </Row>

            <Divider orientation="left">Active Tasks</Divider>
            {data.services.celery.active_task_list && data.services.celery.active_task_list.length > 0 ? (
              <Table
                dataSource={data.services.celery.active_task_list}
                columns={[
                  {
                    title: 'Task Name',
                    dataIndex: 'task_name',
                    key: 'task_name',
                    render: (text: string) => <Text code>{text.split('.').pop()}</Text>,
                  },
                  {
                    title: 'Task ID',
                    dataIndex: 'task_id',
                    key: 'task_id',
                    render: (text: string) => <Text type="secondary">{text.substring(0, 12)}...</Text>,
                  },
                  {
                    title: 'Worker',
                    dataIndex: 'worker',
                    key: 'worker',
                  },
                  {
                    title: 'Args',
                    dataIndex: 'args',
                    key: 'args',
                    render: (text: string) => <Text type="secondary" style={{ fontSize: 11 }}>{text}</Text>,
                  },
                ]}
                pagination={false}
                size="small"
                rowKey="task_id"
              />
            ) : (
              <Alert message="No active tasks" type="info" showIcon style={{ marginBottom: 16 }} />
            )}

            <Divider orientation="left">Reserved Tasks</Divider>
            {data.services.celery.reserved_task_list && data.services.celery.reserved_task_list.length > 0 ? (
              <Table
                dataSource={data.services.celery.reserved_task_list}
                columns={[
                  {
                    title: 'Task Name',
                    dataIndex: 'task_name',
                    key: 'task_name',
                    render: (text: string) => <Text code>{text.split('.').pop()}</Text>,
                  },
                  {
                    title: 'Task ID',
                    dataIndex: 'task_id',
                    key: 'task_id',
                    render: (text: string) => <Text type="secondary">{text.substring(0, 12)}...</Text>,
                  },
                  {
                    title: 'Worker',
                    dataIndex: 'worker',
                    key: 'worker',
                  },
                ]}
                pagination={false}
                size="small"
                rowKey="task_id"
              />
            ) : (
              <Alert message="No reserved tasks" type="info" showIcon style={{ marginBottom: 16 }} />
            )}

            <Divider orientation="left">Registered Tasks ({data.services.celery.registered_tasks?.length || 0})</Divider>
            {data.services.celery.registered_tasks && data.services.celery.registered_tasks.length > 0 ? (
              <div style={{ maxHeight: 300, overflow: 'auto' }}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  {data.services.celery.registered_tasks.map((task, idx) => (
                    <Tag key={idx} color="blue" style={{ margin: 4 }}>
                      {task}
                    </Tag>
                  ))}
                </Space>
              </div>
            ) : (
              <Alert message="No registered tasks" type="warning" showIcon />
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default SystemHealth;
