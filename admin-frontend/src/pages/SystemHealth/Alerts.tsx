import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Card,
  Table,
  Tag,
  Button,
  Space,
  Modal,
  Input,
  Select,
  Badge,
  Tooltip,
  Typography,
  message,
  Statistic,
  Row,
  Col,
  Descriptions,
} from 'antd';
import {
  BellOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined,
  ReloadOutlined,
  FilterOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import {
  getAlerts,
  getAlertStatistics,
  acknowledgeAlert,
  resolveAlert,
  type SystemAlert,
} from '@/services/systemHealthService';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;
const { TextArea } = Input;

const SystemAlerts = () => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [statusFilter, setStatusFilter] = useState<'active' | 'resolved' | 'all'>('active');
  const [severityFilter, setSeverityFilter] = useState<string | undefined>(undefined);
  const [alertTypeFilter, setAlertTypeFilter] = useState<string | undefined>(undefined);

  const [acknowledgeModalVisible, setAcknowledgeModalVisible] = useState(false);
  const [resolveModalVisible, setResolveModalVisible] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState<SystemAlert | null>(null);
  const [notes, setNotes] = useState('');

  // 查询告警列表
  const { data: alertsData, isLoading, refetch } = useQuery({
    queryKey: ['system-alerts', page, pageSize, statusFilter, severityFilter, alertTypeFilter],
    queryFn: () =>
      getAlerts({
        page,
        page_size: pageSize,
        status: statusFilter,
        severity: severityFilter as any,
        alert_type: alertTypeFilter,
      }),
    refetchInterval: 30000, // 每30秒刷新
  });

  // 查询告警统计
  const { data: statsData } = useQuery({
    queryKey: ['alert-statistics'],
    queryFn: getAlertStatistics,
    refetchInterval: 30000,
  });

  // 确认告警
  const acknowledgeMutation = useMutation({
    mutationFn: ({ id, notes }: { id: number; notes?: string }) => acknowledgeAlert(id, notes),
    onSuccess: () => {
      message.success(t('systemHealth.alerts.messages.acknowledgeSuccess'));
      queryClient.invalidateQueries({ queryKey: ['system-alerts'] });
      queryClient.invalidateQueries({ queryKey: ['alert-statistics'] });
      setAcknowledgeModalVisible(false);
      setNotes('');
    },
    onError: () => {
      message.error(t('systemHealth.alerts.messages.acknowledgeFailed'));
    },
  });

  // 解决告警
  const resolveMutation = useMutation({
    mutationFn: ({ id, notes }: { id: number; notes?: string }) => resolveAlert(id, notes),
    onSuccess: () => {
      message.success(t('systemHealth.alerts.messages.resolveSuccess'));
      queryClient.invalidateQueries({ queryKey: ['system-alerts'] });
      queryClient.invalidateQueries({ queryKey: ['alert-statistics'] });
      setResolveModalVisible(false);
      setNotes('');
    },
    onError: () => {
      message.error(t('systemHealth.alerts.messages.resolveFailed'));
    },
  });

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'red';
      case 'warning':
        return 'orange';
      case 'info':
        return 'blue';
      default:
        return 'default';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <CloseCircleOutlined style={{ color: '#f5222d' }} />;
      case 'warning':
        return <WarningOutlined style={{ color: '#faad14' }} />;
      case 'info':
        return <CheckCircleOutlined style={{ color: '#1890ff' }} />;
      default:
        return null;
    }
  };

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      cpu: 'blue',
      memory: 'cyan',
      disk: 'purple',
      database: 'green',
      redis: 'red',
      storage: 'orange',
      celery: 'magenta',
    };
    return colors[type] || 'default';
  };

  const columns: ColumnsType<SystemAlert> = [
    {
      title: t('systemHealth.alerts.columns.severity'),
      dataIndex: 'severity',
      key: 'severity',
      width: 100,
      render: (severity: string) => (
        <Space>
          {getSeverityIcon(severity)}
          <Tag color={getSeverityColor(severity)}>{severity.toUpperCase()}</Tag>
        </Space>
      ),
      filters: [
        { text: t('systemHealth.alerts.critical'), value: 'critical' },
        { text: t('systemHealth.alerts.severity.warning'), value: 'warning' },
        { text: t('systemHealth.alerts.severity.info'), value: 'info' },
      ],
      filteredValue: severityFilter ? [severityFilter] : null,
    },
    {
      title: t('systemHealth.alerts.columns.type'),
      dataIndex: 'alert_type',
      key: 'alert_type',
      width: 120,
      render: (type: string) => <Tag color={getTypeColor(type)}>{type.toUpperCase()}</Tag>,
      filters: [
        { text: t('systemHealth.alerts.types.cpu'), value: 'cpu' },
        { text: t('systemHealth.alerts.types.memory'), value: 'memory' },
        { text: t('systemHealth.alerts.types.disk'), value: 'disk' },
        { text: t('systemHealth.alerts.types.database'), value: 'database' },
        { text: t('systemHealth.alerts.types.redis'), value: 'redis' },
        { text: t('systemHealth.alerts.types.storage'), value: 'storage' },
        { text: t('systemHealth.alerts.types.celery'), value: 'celery' },
      ],
      filteredValue: alertTypeFilter ? [alertTypeFilter] : null,
    },
    {
      title: t('systemHealth.alerts.columns.title'),
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: t('systemHealth.alerts.columns.message'),
      dataIndex: 'message',
      key: 'message',
      ellipsis: true,
      render: (text: string) => (
        <Tooltip title={text}>
          <Text ellipsis style={{ maxWidth: 300 }}>
            {text}
          </Text>
        </Tooltip>
      ),
    },
    {
      title: t('systemHealth.alerts.columns.metric'),
      key: 'metric',
      width: 150,
      render: (_, record) =>
        record.metric_name ? (
          <Text type="secondary" style={{ fontSize: 12 }}>
            {record.metric_value?.toFixed(2)} / {record.threshold_value?.toFixed(2)}
          </Text>
        ) : (
          '-'
        ),
    },
    {
      title: t('systemHealth.labels.status'),
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string, record) => (
        <Space direction="vertical" size="small">
          <Tag color={status === 'active' ? 'red' : status === 'resolved' ? 'green' : 'default'}>
            {status.toUpperCase()}
          </Tag>
          {record.acknowledged_by && <Badge status="success" text={t('systemHealth.alerts.status.acknowledged')} />}
        </Space>
      ),
    },
    {
      title: t('systemHealth.alerts.columns.triggeredAt'),
      dataIndex: 'triggered_at',
      key: 'triggered_at',
      width: 160,
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: t('common.actions'),
      key: 'actions',
      width: 180,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          {record.status === 'active' && !record.acknowledged_by && (
            <Button
              type="link"
              size="small"
              onClick={() => {
                setSelectedAlert(record);
                setAcknowledgeModalVisible(true);
              }}
            >
              {t('systemHealth.alerts.actions.acknowledge')}
            </Button>
          )}
          {record.status === 'active' && (
            <Button
              type="link"
              size="small"
              onClick={() => {
                setSelectedAlert(record);
                setResolveModalVisible(true);
              }}
            >
              {t('systemHealth.alerts.actions.resolve')}
            </Button>
          )}
          {record.status === 'resolved' && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              {t('systemHealth.alerts.status.resolved')}
            </Text>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={2} style={{ margin: 0 }}>
          <BellOutlined /> {t('systemHealth.alerts.title')}
        </Title>
        <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
          {t('common.refresh')}
        </Button>
      </div>

      {/* Statistics */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title={t('systemHealth.alerts.activeAlerts')}
              value={statsData?.statistics.active_total || 0}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title={t('systemHealth.alerts.critical')}
              value={statsData?.statistics.critical || 0}
              valueStyle={{ color: '#f5222d' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title={t('systemHealth.alerts.warnings')}
              value={statsData?.statistics.warning || 0}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title={t('systemHealth.alerts.resolved24h')}
              value={statsData?.statistics.resolved_24h || 0}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Filters */}
      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Text strong>
            <FilterOutlined /> {t('common.filters')}
          </Text>
          <Select
            placeholder={t('systemHealth.labels.status')}
            value={statusFilter}
            onChange={setStatusFilter}
            style={{ width: 120 }}
            options={[
              { label: t('systemHealth.alerts.status.active'), value: 'active' },
              { label: t('systemHealth.alerts.status.resolved'), value: 'resolved' },
              { label: t('common.all'), value: 'all' },
            ]}
          />
          <Select
            placeholder={t('systemHealth.alerts.columns.severity')}
            value={severityFilter}
            onChange={setSeverityFilter}
            style={{ width: 120 }}
            allowClear
            options={[
              { label: t('systemHealth.alerts.critical'), value: 'critical' },
              { label: t('systemHealth.alerts.severity.warning'), value: 'warning' },
              { label: t('systemHealth.alerts.severity.info'), value: 'info' },
            ]}
          />
          <Select
            placeholder={t('systemHealth.alerts.columns.type')}
            value={alertTypeFilter}
            onChange={setAlertTypeFilter}
            style={{ width: 120 }}
            allowClear
            options={[
              { label: t('systemHealth.alerts.types.cpu'), value: 'cpu' },
              { label: t('systemHealth.alerts.types.memory'), value: 'memory' },
              { label: t('systemHealth.alerts.types.disk'), value: 'disk' },
              { label: t('systemHealth.alerts.types.database'), value: 'database' },
              { label: t('systemHealth.alerts.types.redis'), value: 'redis' },
              { label: t('systemHealth.alerts.types.storage'), value: 'storage' },
              { label: t('systemHealth.alerts.types.celery'), value: 'celery' },
            ]}
          />
        </Space>
      </Card>

      {/* Alerts Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={alertsData?.items || []}
          rowKey="id"
          loading={isLoading}
          scroll={{ x: 1200 }}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: alertsData?.total || 0,
            showSizeChanger: true,
            showTotal: (total) => t('systemHealth.alerts.pagination.total', { total }),
            onChange: (p, ps) => {
              setPage(p);
              setPageSize(ps);
            },
          }}
          expandable={{
            expandedRowRender: (record) => (
              <Descriptions column={2} size="small" bordered>
                <Descriptions.Item label={t('systemHealth.alerts.details.alertId')}>{record.id}</Descriptions.Item>
                <Descriptions.Item label={t('systemHealth.alerts.details.metricName')}>{record.metric_name || 'N/A'}</Descriptions.Item>
                <Descriptions.Item label={t('systemHealth.alerts.columns.triggeredAt')}>
                  {new Date(record.triggered_at).toLocaleString()}
                </Descriptions.Item>
                <Descriptions.Item label={t('systemHealth.alerts.details.resolvedAt')}>
                  {record.resolved_at ? new Date(record.resolved_at).toLocaleString() : 'N/A'}
                </Descriptions.Item>
                {record.acknowledged_by && (
                  <>
                    <Descriptions.Item label={t('systemHealth.alerts.details.acknowledgedBy')}>
                      Admin ID: {record.acknowledged_by}
                    </Descriptions.Item>
                    <Descriptions.Item label={t('systemHealth.alerts.details.acknowledgedAt')}>
                      {record.acknowledged_at ? new Date(record.acknowledged_at).toLocaleString() : 'N/A'}
                    </Descriptions.Item>
                  </>
                )}
                {record.notes && (
                  <Descriptions.Item label={t('systemHealth.alerts.details.notes')} span={2}>
                    {record.notes}
                  </Descriptions.Item>
                )}
                {record.context && (
                  <Descriptions.Item label={t('systemHealth.alerts.details.context')} span={2}>
                    <pre style={{ fontSize: 11, maxHeight: 200, overflow: 'auto' }}>
                      {JSON.stringify(record.context, null, 2)}
                    </pre>
                  </Descriptions.Item>
                )}
              </Descriptions>
            ),
          }}
        />
      </Card>

      {/* Acknowledge Modal */}
      <Modal
        title={t('systemHealth.alerts.modals.acknowledgeTitle')}
        open={acknowledgeModalVisible}
        onOk={() => {
          if (selectedAlert) {
            acknowledgeMutation.mutate({ id: selectedAlert.id, notes });
          }
        }}
        onCancel={() => {
          setAcknowledgeModalVisible(false);
          setNotes('');
        }}
        confirmLoading={acknowledgeMutation.isPending}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <div>
            <Text strong>{t('systemHealth.alerts.modals.alert')}</Text>
            <Text>{selectedAlert?.title}</Text>
          </div>
          <div>
            <Text strong>{t('systemHealth.alerts.modals.message')}</Text>
            <Text type="secondary">{selectedAlert?.message}</Text>
          </div>
          <TextArea
            rows={4}
            placeholder={t('systemHealth.alerts.modals.addNotes')}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </Space>
      </Modal>

      {/* Resolve Modal */}
      <Modal
        title={t('systemHealth.alerts.modals.resolveTitle')}
        open={resolveModalVisible}
        onOk={() => {
          if (selectedAlert) {
            resolveMutation.mutate({ id: selectedAlert.id, notes });
          }
        }}
        onCancel={() => {
          setResolveModalVisible(false);
          setNotes('');
        }}
        confirmLoading={resolveMutation.isPending}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <div>
            <Text strong>{t('systemHealth.alerts.modals.alert')}</Text>
            <Text>{selectedAlert?.title}</Text>
          </div>
          <div>
            <Text strong>{t('systemHealth.alerts.modals.message')}</Text>
            <Text type="secondary">{selectedAlert?.message}</Text>
          </div>
          <TextArea
            rows={4}
            placeholder={t('systemHealth.alerts.modals.addResolutionNotes')}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </Space>
      </Modal>
    </div>
  );
};

export default SystemAlerts;
