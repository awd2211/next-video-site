import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Space,
  Select,
  Button,
  message,
  Spin,
  Table,
  Typography,
} from 'antd';
import {
  ReloadOutlined,
  DollarOutlined,
  RiseOutlined,
  LineChartOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { Line, Column, Pie } from '@ant-design/charts';
import dayjs from 'dayjs';
import { getCostStats, getUsageStats, type AICostStats, type AIUsageStats } from '../../services/ai-logs';
import '../../styles/page-layout.css';

const { Option } = Select;
const { Text } = Typography;

const CostDashboard: React.FC = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [costStats, setCostStats] = useState<AICostStats | null>(null);
  const [usageStats, setUsageStats] = useState<AIUsageStats | null>(null);
  const [days, setDays] = useState(30);

  useEffect(() => {
    fetchData();
  }, [days]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [cost, usage] = await Promise.all([
        getCostStats({ days }),
        getUsageStats({}),
      ]);
      setCostStats(cost);
      setUsageStats(usage);
    } catch (error) {
      message.error(t('message.loadFailed'));
      console.error('Failed to fetch cost data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Prepare trend chart data
  const trendData = costStats?.cost_trend?.map((item) => ({
    date: dayjs(item.date).format('MM-DD'),
    cost: item.cost,
    requests: item.requests,
  })) || [];

  // Prepare cost by model chart data
  const modelCostData = costStats?.cost_by_model
    ? Object.entries(costStats.cost_by_model).map(([model, cost]) => ({
        model,
        cost,
      }))
    : [];

  // Prepare provider distribution data
  const providerCostData = usageStats?.cost_by_provider
    ? Object.entries(usageStats.cost_by_provider).map(([provider, cost]) => ({
        provider: provider.toUpperCase(),
        cost,
      }))
    : [];

  // Top users table columns
  const topUsersColumns = [
    {
      title: t('common.rank'),
      key: 'rank',
      width: 80,
      render: (_: any, __: any, index: number) => index + 1,
    },
    {
      title: t('user.username'),
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: t('aiManagement.totalCost'),
      dataIndex: 'cost',
      key: 'cost',
      render: (cost: number) => `$${cost.toFixed(4)}`,
      sorter: (a: any, b: any) => a.cost - b.cost,
    },
  ];

  // Cost trend line chart config
  const trendChartConfig = {
    data: trendData,
    xField: 'date',
    yField: 'cost',
    seriesField: 'type',
    smooth: true,
    animation: {
      appear: {
        animation: 'path-in',
        duration: 1000,
      },
    },
    tooltip: {
      formatter: (datum: any) => ({
        name: t('aiManagement.cost'),
        value: `$${datum.cost.toFixed(4)}`,
      }),
    },
    point: {
      size: 3,
      shape: 'circle',
    },
    lineStyle: {
      lineWidth: 2,
    },
  };

  // Model cost column chart config
  const modelCostChartConfig = {
    data: modelCostData,
    xField: 'model',
    yField: 'cost',
    seriesField: 'model',
    legend: false,
    label: {
      position: 'top' as const,
      formatter: (datum: any) => `$${datum.cost.toFixed(4)}`,
    },
    tooltip: {
      formatter: (datum: any) => ({
        name: datum.model,
        value: `$${datum.cost.toFixed(4)}`,
      }),
    },
    columnStyle: {
      radius: [4, 4, 0, 0],
    },
  };

  // Provider cost pie chart config
  const providerPieConfig = {
    data: providerCostData,
    angleField: 'cost',
    colorField: 'provider',
    radius: 0.8,
    innerRadius: 0.6,
    label: {
      type: 'spider',
      labelHeight: 28,
      content: '{name}\n${value}',
    },
    tooltip: {
      formatter: (datum: any) => ({
        name: datum.provider,
        value: `$${datum.cost.toFixed(4)}`,
      }),
    },
    statistic: {
      title: false,
      content: {
        style: {
          whiteSpace: 'pre-wrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        },
        content: '',
      },
    },
  };

  if (loading && !costStats) {
    return (
      <div className="page-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ margin: 0 }}>{t('aiManagement.costMonitoring')}</h2>
          <Space>
            <Select value={days} onChange={setDays} style={{ width: 150 }}>
              <Option value={7}>7 {t('common.days')}</Option>
              <Option value={30}>30 {t('common.days')}</Option>
              <Option value={90}>90 {t('common.days')}</Option>
            </Select>
            <Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading}>
              {t('common.refresh')}
            </Button>
          </Space>
        </div>
      </div>

      <div className="page-content">
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* Key Metrics */}
          <Row gutter={16}>
            <Col span={6}>
              <Card>
                <Statistic
                  title={t('aiManagement.todayCost')}
                  value={costStats?.today_cost || 0}
                  prefix={<DollarOutlined />}
                  precision={4}
                  valueStyle={{ color: '#cf1322' }}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title={t('aiManagement.monthCost')}
                  value={costStats?.this_month_cost || 0}
                  prefix={<DollarOutlined />}
                  precision={2}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title={t('aiManagement.projectedMonthlyCost')}
                  value={costStats?.projected_monthly_cost || 0}
                  prefix={<RiseOutlined />}
                  precision={2}
                  valueStyle={{ color: '#faad14' }}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title={t('aiManagement.totalRequests')}
                  value={usageStats?.total_requests || 0}
                  prefix={<LineChartOutlined />}
                  valueStyle={{ color: '#3f8600' }}
                />
              </Card>
            </Col>
          </Row>

          {/* Cost Trend Chart */}
          <Card title={t('aiManagement.costTrend')} loading={loading}>
            {trendData.length > 0 ? (
              <Line {...trendChartConfig} />
            ) : (
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <Text type="secondary">{t('common.noData')}</Text>
              </div>
            )}
          </Card>

          <Row gutter={16}>
            {/* Cost by Model */}
            <Col span={12}>
              <Card title={t('aiManagement.costByModel')} loading={loading}>
                {modelCostData.length > 0 ? (
                  <Column {...modelCostChartConfig} />
                ) : (
                  <div style={{ textAlign: 'center', padding: '40px 0' }}>
                    <Text type="secondary">{t('common.noData')}</Text>
                  </div>
                )}
              </Card>
            </Col>

            {/* Cost by Provider */}
            <Col span={12}>
              <Card title={t('aiManagement.costByProvider')} loading={loading}>
                {providerCostData.length > 0 ? (
                  <Pie {...providerPieConfig} />
                ) : (
                  <div style={{ textAlign: 'center', padding: '40px 0' }}>
                    <Text type="secondary">{t('common.noData')}</Text>
                  </div>
                )}
              </Card>
            </Col>
          </Row>

          {/* Top Cost Users */}
          {costStats?.top_cost_users && costStats.top_cost_users.length > 0 && (
            <Card title={t('aiManagement.topCostUsers')} loading={loading}>
              <Table
                columns={topUsersColumns}
                dataSource={costStats.top_cost_users}
                rowKey="user_id"
                pagination={false}
                size="small"
              />
            </Card>
          )}

          {/* Usage Statistics Summary */}
          <Card title={t('aiManagement.usageStatistics')} loading={loading}>
            <Row gutter={16}>
              <Col span={8}>
                <Statistic
                  title={t('aiManagement.totalTokens')}
                  value={usageStats?.total_tokens || 0}
                  valueStyle={{ fontSize: 20 }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title={t('aiManagement.avgResponseTime')}
                  value={usageStats?.avg_response_time || 0}
                  suffix="s"
                  precision={2}
                  valueStyle={{ fontSize: 20 }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title={t('aiManagement.successRate')}
                  value={usageStats?.success_rate || 0}
                  suffix="%"
                  precision={1}
                  valueStyle={{
                    fontSize: 20,
                    color: (usageStats?.success_rate || 0) > 90 ? '#3f8600' : '#faad14',
                  }}
                />
              </Col>
            </Row>
          </Card>
        </Space>
      </div>
    </div>
  );
};

export default CostDashboard;
