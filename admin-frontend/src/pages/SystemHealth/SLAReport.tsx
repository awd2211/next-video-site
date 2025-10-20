import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Card,
  Table,
  Button,
  Space,
  Select,
  Typography,
  message,
  Statistic,
  Row,
  Col,
  Progress,
  Tag,
  Tabs,
  DatePicker,
} from 'antd';
import {
  LineChartOutlined,
  ReloadOutlined,
  DownloadOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ThunderboltOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import { Line } from '@ant-design/charts';
import { useTranslation } from 'react-i18next';
import {
  getSLAReport,
  getSLASummary,
  getCurrentSLA,
  generateSLAReport,
  type SLARecord,
} from '@/services/systemHealthService';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

const SLAReportPage = () => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const [periodType, setPeriodType] = useState<'hourly' | 'daily' | 'weekly' | 'monthly'>('daily');
  const [limit, setLimit] = useState(30);
  const [summaryDays, setSummaryDays] = useState(30);

  // 查询SLA报告
  const { data: reportData, isLoading: reportLoading, refetch: refetchReport } = useQuery({
    queryKey: ['sla-report', periodType, limit],
    queryFn: () => getSLAReport({ period_type: periodType, limit }),
  });

  // 查询SLA汇总
  const { data: summaryData, isLoading: summaryLoading } = useQuery({
    queryKey: ['sla-summary', summaryDays],
    queryFn: () => getSLASummary(summaryDays),
  });

  // 查询当前SLA
  const { data: currentSLA } = useQuery({
    queryKey: ['current-sla'],
    queryFn: getCurrentSLA,
    refetchInterval: 60000, // 每分钟刷新
  });

  // 生成SLA报告
  const generateMutation = useMutation({
    mutationFn: (type: 'hourly' | 'daily') => generateSLAReport(type),
    onSuccess: () => {
      message.success(t('systemHealth.sla.messages.generateSuccess'));
      queryClient.invalidateQueries({ queryKey: ['sla-report'] });
      queryClient.invalidateQueries({ queryKey: ['sla-summary'] });
    },
    onError: () => {
      message.error(t('systemHealth.sla.messages.generateFailed'));
    },
  });

  const getUptimeColor = (uptime: number) => {
    if (uptime >= 99.9) return '#52c41a';
    if (uptime >= 99.0) return '#faad14';
    return '#f5222d';
  };

  const getUptimeStatus = (uptime: number): 'success' | 'normal' | 'exception' => {
    if (uptime >= 99.9) return 'success';
    if (uptime >= 99.0) return 'normal';
    return 'exception';
  };

  const columns: ColumnsType<SLARecord> = [
    {
      title: t('systemHealth.sla.columns.period'),
      key: 'period',
      render: (_, record) => (
        <Space direction="vertical" size="small">
          <Text strong>{new Date(record.period_start).toLocaleDateString()}</Text>
          <Text type="secondary" style={{ fontSize: 12 }}>
            {new Date(record.period_start).toLocaleTimeString()} -{' '}
            {new Date(record.period_end).toLocaleTimeString()}
          </Text>
        </Space>
      ),
    },
    {
      title: t('systemHealth.sla.uptime'),
      key: 'uptime',
      width: 200,
      render: (_, record) => (
        <Space direction="vertical" style={{ width: '100%' }}>
          <Text strong style={{ color: getUptimeColor(record.uptime_percentage) }}>
            {record.uptime_percentage.toFixed(4)}%
          </Text>
          <Progress
            percent={record.uptime_percentage}
            status={getUptimeStatus(record.uptime_percentage)}
            size="small"
            showInfo={false}
          />
        </Space>
      ),
      sorter: (a, b) => a.uptime_percentage - b.uptime_percentage,
    },
    {
      title: t('systemHealth.sla.columns.responseTime'),
      children: [
        {
          title: t('systemHealth.sla.columns.avg'),
          dataIndex: 'avg_response_time_ms',
          width: 80,
          render: (val: number) => (val ? `${val.toFixed(1)}ms` : 'N/A'),
        },
        {
          title: 'P95',
          dataIndex: 'p95_response_time_ms',
          width: 80,
          render: (val: number) => (val ? `${val.toFixed(1)}ms` : 'N/A'),
        },
        {
          title: 'P99',
          dataIndex: 'p99_response_time_ms',
          width: 80,
          render: (val: number) => (val ? `${val.toFixed(1)}ms` : 'N/A'),
        },
      ],
    },
    {
      title: t('systemHealth.sla.columns.alerts'),
      children: [
        {
          title: t('systemHealth.sla.columns.total'),
          dataIndex: 'total_alerts',
          width: 70,
          render: (val: number) => <Tag>{val}</Tag>,
        },
        {
          title: t('systemHealth.alerts.critical'),
          dataIndex: 'critical_alerts',
          width: 80,
          render: (val: number) => (val > 0 ? <Tag color="red">{val}</Tag> : <Tag>0</Tag>),
        },
        {
          title: t('systemHealth.alerts.severity.warning'),
          dataIndex: 'warning_alerts',
          width: 80,
          render: (val: number) => (val > 0 ? <Tag color="orange">{val}</Tag> : <Tag>0</Tag>),
        },
      ],
    },
    {
      title: t('systemHealth.sla.columns.resourceUsage'),
      children: [
        {
          title: t('systemHealth.alerts.types.cpu'),
          dataIndex: 'avg_cpu_usage',
          width: 80,
          render: (val: number) => (val ? `${val.toFixed(1)}%` : 'N/A'),
        },
        {
          title: t('systemHealth.alerts.types.memory'),
          dataIndex: 'avg_memory_usage',
          width: 80,
          render: (val: number) => (val ? `${val.toFixed(1)}%` : 'N/A'),
        },
        {
          title: t('systemHealth.alerts.types.disk'),
          dataIndex: 'avg_disk_usage',
          width: 80,
          render: (val: number) => (val ? `${val.toFixed(1)}%` : 'N/A'),
        },
      ],
    },
  ];

  // 准备图表数据
  const uptimeChartData =
    reportData?.records.map((record) => ({
      date: new Date(record.period_start).toLocaleDateString(),
      uptime: record.uptime_percentage,
    })) || [];

  const responseTimeChartData =
    reportData?.records.flatMap((record) => [
      {
        date: new Date(record.period_start).toLocaleDateString(),
        type: 'Average',
        value: record.avg_response_time_ms || 0,
      },
      {
        date: new Date(record.period_start).toLocaleDateString(),
        type: 'P95',
        value: record.p95_response_time_ms || 0,
      },
      {
        date: new Date(record.period_start).toLocaleDateString(),
        type: 'P99',
        value: record.p99_response_time_ms || 0,
      },
    ]) || [];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={2} style={{ margin: 0 }}>
          <LineChartOutlined /> {t('systemHealth.sla.title')}
        </Title>
        <Space>
          <Button
            icon={<ThunderboltOutlined />}
            onClick={() => generateMutation.mutate('hourly')}
            loading={generateMutation.isPending}
          >
            {t('systemHealth.sla.actions.generateHourly')}
          </Button>
          <Button
            icon={<ThunderboltOutlined />}
            onClick={() => generateMutation.mutate('daily')}
            loading={generateMutation.isPending}
          >
            {t('systemHealth.sla.actions.generateDaily')}
          </Button>
          <Button icon={<ReloadOutlined />} onClick={() => refetchReport()}>
            {t('common.refresh')}
          </Button>
        </Space>
      </div>

      {/* Current SLA Status */}
      {currentSLA && (
        <Card style={{ marginBottom: 24 }} title={<Text strong>{t('systemHealth.sla.todayTitle')}</Text>}>
          <Row gutter={16}>
            <Col xs={24} sm={6}>
              <Statistic
                title={t('systemHealth.sla.uptime')}
                value={currentSLA.uptime_percentage}
                suffix="%"
                precision={4}
                valueStyle={{ color: getUptimeColor(currentSLA.uptime_percentage) }}
                prefix={<CheckCircleOutlined />}
              />
            </Col>
            <Col xs={24} sm={6}>
              <Statistic
                title={t('systemHealth.sla.elapsedTime')}
                value={currentSLA.elapsed_hours}
                suffix={t('common.units.hours')}
                precision={1}
                prefix={<ClockCircleOutlined />}
              />
            </Col>
            <Col xs={24} sm={6}>
              <Statistic
                title={t('systemHealth.sla.avgResponseTime')}
                value={currentSLA.avg_db_response_time_ms || 0}
                suffix="ms"
                precision={2}
                prefix={<ThunderboltOutlined />}
              />
            </Col>
            <Col xs={24} sm={6}>
              <Statistic
                title={t('systemHealth.alerts.activeAlerts')}
                value={currentSLA.total_alerts}
                valueStyle={{ color: currentSLA.critical_alerts > 0 ? '#f5222d' : '#52c41a' }}
                prefix={<WarningOutlined />}
              />
            </Col>
          </Row>
          <div style={{ marginTop: 16 }}>
            <Tag color={currentSLA.status === 'healthy' ? 'green' : currentSLA.status === 'degraded' ? 'orange' : 'red'}>
              {currentSLA.status.toUpperCase()}
            </Tag>
            <Text type="secondary" style={{ marginLeft: 8 }}>
              {t('systemHealth.metricsCollected', { count: currentSLA.metrics_collected })}
            </Text>
          </div>
        </Card>
      )}

      {/* Summary Statistics */}
      {summaryData && (
        <Card style={{ marginBottom: 24 }} title={<Text strong>{t('systemHealth.sla.summaryTitle', { days: summaryDays })}</Text>}>
          <Row gutter={16}>
            <Col xs={24} sm={6}>
              <Statistic
                title={t('systemHealth.sla.averageUptime')}
                value={summaryData.avg_uptime_percentage}
                suffix="%"
                precision={4}
                valueStyle={{ color: getUptimeColor(summaryData.avg_uptime_percentage) }}
              />
            </Col>
            <Col xs={24} sm={6}>
              <Statistic
                title={t('systemHealth.sla.totalDowntime')}
                value={summaryData.total_downtime_seconds / 60}
                suffix={t('common.units.minutes')}
                precision={0}
              />
            </Col>
            <Col xs={24} sm={6}>
              <Statistic
                title={t('systemHealth.sla.totalAlerts')}
                value={summaryData.total_alerts}
                valueStyle={{ color: summaryData.critical_alerts > 0 ? '#f5222d' : '#1890ff' }}
              />
            </Col>
            <Col xs={24} sm={6}>
              <Statistic
                title={t('systemHealth.sla.avgResponseTime')}
                value={summaryData.avg_response_time_ms || 0}
                suffix="ms"
                precision={2}
              />
            </Col>
          </Row>
        </Card>
      )}

      {/* Tabs */}
      <Tabs
        items={[
          {
            key: 'table',
            label: t('systemHealth.sla.tabs.tableView'),
            children: (
              <>
                {/* Filters */}
                <Card style={{ marginBottom: 16 }}>
                  <Space wrap>
                    <Text strong>{t('systemHealth.sla.periodTypeLabel')}</Text>
                    <Select
                      value={periodType}
                      onChange={setPeriodType}
                      style={{ width: 120 }}
                      options={[
                        { label: t('systemHealth.sla.periodTypes.hourly'), value: 'hourly' },
                        { label: t('systemHealth.sla.periodTypes.daily'), value: 'daily' },
                        { label: t('systemHealth.sla.periodTypes.weekly'), value: 'weekly' },
                        { label: t('systemHealth.sla.periodTypes.monthly'), value: 'monthly' },
                      ]}
                    />
                    <Text strong>{t('systemHealth.sla.limitLabel')}</Text>
                    <Select
                      value={limit}
                      onChange={setLimit}
                      style={{ width: 100 }}
                      options={[
                        { label: '10', value: 10 },
                        { label: '30', value: 30 },
                        { label: '60', value: 60 },
                        { label: '90', value: 90 },
                      ]}
                    />
                  </Space>
                </Card>

                {/* Table */}
                <Card>
                  <Table
                    columns={columns}
                    dataSource={reportData?.records || []}
                    rowKey="id"
                    loading={reportLoading}
                    scroll={{ x: 1400 }}
                    pagination={{
                      pageSize: 10,
                      showTotal: (total) => t('systemHealth.sla.pagination.total', { total }),
                    }}
                  />
                </Card>
              </>
            ),
          },
          {
            key: 'charts',
            label: t('systemHealth.sla.tabs.charts'),
            children: (
              <Space direction="vertical" style={{ width: '100%' }} size="large">
                {/* Uptime Trend */}
                <Card title={t('systemHealth.sla.charts.uptimeTrend')}>
                  <Line
                    data={uptimeChartData.reverse()}
                    xField="date"
                    yField="uptime"
                    yAxis={{
                      min: 98,
                      max: 100,
                      label: {
                        formatter: (v) => `${v}%`,
                      },
                    }}
                    point={{
                      size: 4,
                      shape: 'circle',
                    }}
                    smooth
                    color="#52c41a"
                    annotations={[
                      {
                        type: 'line',
                        start: ['min', 99.9],
                        end: ['max', 99.9],
                        style: {
                          stroke: '#52c41a',
                          lineDash: [4, 4],
                        },
                        text: {
                          content: t('systemHealth.sla.charts.target'),
                          position: 'end',
                          style: { fill: '#52c41a' },
                        },
                      },
                    ]}
                  />
                </Card>

                {/* Response Time Trend */}
                <Card title={t('systemHealth.sla.charts.responseTimeTrend')}>
                  <Line
                    data={responseTimeChartData.reverse()}
                    xField="date"
                    yField="value"
                    seriesField="type"
                    yAxis={{
                      label: {
                        formatter: (v) => `${v}ms`,
                      },
                    }}
                    point={{
                      size: 3,
                      shape: 'circle',
                    }}
                    smooth
                  />
                </Card>
              </Space>
            ),
          },
        ]}
      />
    </div>
  );
};

export default SLAReportPage;
