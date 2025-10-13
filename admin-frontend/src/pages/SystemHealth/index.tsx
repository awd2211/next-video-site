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
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import axios from '@/utils/axios';
import MetricsChart from './MetricsChart';
import { exportHealthReport } from './exportUtils';

const { Title, Text } = Typography;

interface ServiceStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  response_time_ms?: number;
  message?: string;
  error?: string;
}

interface DatabaseHealth extends ServiceStatus {
  pool_size?: number;
  checked_out?: number;
  checked_in?: number;
  overflow?: number;
  utilization_percent?: number;
}

interface RedisHealth extends ServiceStatus {
  used_memory_mb?: number;
  max_memory_mb?: number | string;
  memory_utilization_percent?: number;
  keys_count?: number;
}

interface StorageHealth extends ServiceStatus {
  bucket_exists?: boolean;
  can_read?: boolean;
}

interface SystemResources {
  cpu?: {
    usage_percent: number;
    cores: number;
    frequency_mhz?: number;
    status: 'healthy' | 'warning' | 'critical';
  };
  memory?: {
    used_gb: number;
    total_gb: number;
    available_gb: number;
    usage_percent: number;
    status: 'healthy' | 'warning' | 'critical';
  };
  disk?: {
    used_gb: number;
    total_gb: number;
    free_gb: number;
    usage_percent: number;
    status: 'healthy' | 'warning' | 'critical';
  };
  network?: {
    bytes_sent_gb: number;
    bytes_recv_gb: number;
    packets_sent: number;
    packets_recv: number;
    errors_in: number;
    errors_out: number;
    drops_in: number;
    drops_out: number;
  };
  processes?: {
    count: number;
  };
}

interface HealthData {
  timestamp: string;
  overall_status: 'healthy' | 'degraded' | 'unhealthy';
  services: {
    database: DatabaseHealth;
    redis: RedisHealth;
    storage: StorageHealth;
  };
  system_resources: SystemResources;
}

const SystemHealth = () => {
  const { t } = useTranslation();
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(10000); // 10 seconds
  const [activeTab, setActiveTab] = useState('overview');

  const { data, isLoading, error, refetch } = useQuery<HealthData>({
    queryKey: ['system-health'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/system/health');
      return response.data;
    },
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
        <Col xs={24} lg={8}>
          <Card
            title={
              <Space>
                <DatabaseOutlined />
                <span>Database (PostgreSQL)</span>
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
              <Descriptions.Item label="Response Time">
                {data?.services.database.response_time_ms
                  ? `${data.services.database.response_time_ms.toFixed(2)} ms`
                  : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Pool Size">
                {data?.services.database.pool_size || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Checked Out">
                {data?.services.database.checked_out || 0}
              </Descriptions.Item>
              <Descriptions.Item label="Available">
                {data?.services.database.checked_in || 0}
              </Descriptions.Item>
              <Descriptions.Item label="Pool Utilization">
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
        <Col xs={24} lg={8}>
          <Card
            title={
              <Space>
                <ThunderboltOutlined />
                <span>Redis Cache</span>
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
              <Descriptions.Item label="Response Time">
                {data?.services.redis.response_time_ms
                  ? `${data.services.redis.response_time_ms.toFixed(2)} ms`
                  : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Used Memory">
                {data?.services.redis.used_memory_mb
                  ? `${data.services.redis.used_memory_mb.toFixed(2)} MB`
                  : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Max Memory">
                {typeof data?.services.redis.max_memory_mb === 'number'
                  ? `${data.services.redis.max_memory_mb.toFixed(2)} MB`
                  : data?.services.redis.max_memory_mb || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Keys Count">
                {data?.services.redis.keys_count?.toLocaleString() || 0}
              </Descriptions.Item>
              {data?.services.redis.memory_utilization_percent !== null &&
                data?.services.redis.memory_utilization_percent !== undefined && (
                  <Descriptions.Item label="Memory Utilization">
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
        <Col xs={24} lg={8}>
          <Card
            title={
              <Space>
                <CloudOutlined />
                <span>Object Storage (MinIO)</span>
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
              <Descriptions.Item label="Response Time">
                {data?.services.storage.response_time_ms
                  ? `${data.services.storage.response_time_ms.toFixed(2)} ms`
                  : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Bucket Exists">
                <Tag color={data?.services.storage.bucket_exists ? 'success' : 'error'}>
                  {data?.services.storage.bucket_exists ? 'YES' : 'NO'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Read Access">
                <Tag color={data?.services.storage.can_read ? 'success' : 'warning'}>
                  {data?.services.storage.can_read ? 'OK' : 'LIMITED'}
                </Tag>
              </Descriptions.Item>
            </Descriptions>
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
      </Row>

      {/* Tabs for Overview and Trends */}
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={[
          {
            key: 'overview',
            label: (
              <span>
                <ApiOutlined /> Overview
              </span>
            ),
            children: (
              <>
                {/* System Resources */}
                <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
                  <Col span={24}>
                    <Card title={<Space><HddOutlined /> System Resources</Space>}>
                      <Row gutter={[24, 24]}>
                        {/* CPU */}
                        <Col xs={24} md={6}>
                          <Card type="inner" title="CPU Usage">
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
                              {data?.system_resources.cpu?.cores || 0} cores
                              {data?.system_resources.cpu?.frequency_mhz &&
                                ` @ ${data.system_resources.cpu.frequency_mhz} MHz`}
                            </div>
                          </Card>
                        </Col>

                        {/* Memory */}
                        <Col xs={24} md={6}>
                          <Card type="inner" title="Memory Usage">
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
                          <Card type="inner" title="Disk Usage">
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
                              {data?.system_resources.disk?.free_gb?.toFixed(2) || 0} GB free
                            </div>
                          </Card>
                        </Col>

                        {/* Processes */}
                        <Col xs={24} md={6}>
                          <Card type="inner" title="Processes">
                            <Statistic
                              value={data?.system_resources.processes?.count || 0}
                              valueStyle={{ color: '#1890ff' }}
                            />
                            <div style={{ marginTop: 24, fontSize: 12, color: '#999' }}>
                              Active processes
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
                      <Card title="Network Statistics">
                        <Row gutter={[16, 16]}>
                          <Col xs={12} md={6}>
                            <Statistic
                              title="Data Sent"
                              value={data.system_resources.network.bytes_sent_gb}
                              suffix="GB"
                              precision={2}
                            />
                          </Col>
                          <Col xs={12} md={6}>
                            <Statistic
                              title="Data Received"
                              value={data.system_resources.network.bytes_recv_gb}
                              suffix="GB"
                              precision={2}
                            />
                          </Col>
                          <Col xs={12} md={6}>
                            <Statistic
                              title="Packets Sent"
                              value={data.system_resources.network.packets_sent}
                              formatter={(value) => value.toLocaleString()}
                            />
                          </Col>
                          <Col xs={12} md={6}>
                            <Statistic
                              title="Packets Received"
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
                <LineChartOutlined /> Trends
              </span>
            ),
            children: (
              <Row gutter={[16, 16]}>
                <Col xs={24} lg={12}>
                  <MetricsChart metric="cpu_usage" title="CPU Usage Trend" unit="%" />
                </Col>
                <Col xs={24} lg={12}>
                  <MetricsChart metric="memory_usage" title="Memory Usage Trend" unit="%" />
                </Col>
                <Col xs={24} lg={12}>
                  <MetricsChart metric="disk_usage" title="Disk Usage Trend" unit="%" />
                </Col>
                <Col xs={24} lg={12}>
                  <MetricsChart
                    metric="db_response_time"
                    title="Database Response Time"
                    unit=" ms"
                  />
                </Col>
                <Col xs={24} lg={12}>
                  <MetricsChart
                    metric="redis_response_time"
                    title="Redis Response Time"
                    unit=" ms"
                  />
                </Col>
                <Col xs={24} lg={12}>
                  <MetricsChart
                    metric="storage_response_time"
                    title="Storage Response Time"
                    unit=" ms"
                  />
                </Col>
              </Row>
            ),
          },
        ]}
      />
    </div>
  );
};

export default SystemHealth;
