import { useState, useEffect } from 'react';
import { Table, Tag, Card, Row, Col, Statistic, Button, message, Popconfirm, Space, Select } from 'antd';
import { TrophyOutlined, DollarOutlined, LineChartOutlined, UserOutlined, ReloadOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import type { ColumnsType } from 'antd/es/table';
import * as paymentService from '../../services/adminPaymentService';
import type { UserSubscription, SubscriptionStats } from '../../services/adminPaymentService';

const { Option } = Select;

const Subscriptions = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<UserSubscription[]>([]);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState<SubscriptionStats | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [filterStatus, setFilterStatus] = useState<string>();

  useEffect(() => {
    fetchSubscriptions();
    fetchStats();
  }, [currentPage, pageSize, filterStatus]);

  const fetchSubscriptions = async () => {
    setLoading(true);
    try {
      const response = await paymentService.getUserSubscriptions({
        page: currentPage,
        page_size: pageSize,
        status: filterStatus,
      });
      setData(response.items || []);
      setTotal(response.total || 0);
    } catch (error: any) {
      message.error(error.message || t('payment.subscriptions.fetchError'));
      setData([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const stats = await paymentService.getSubscriptionStats();
      setStats(stats);
    } catch (error) {
      console.error('Failed to fetch stats', error);
    }
  };

  const handleCancel = async (id: number) => {
    try {
      await paymentService.cancelUserSubscription(id, false);
      message.success(t('payment.subscriptions.cancelSuccess'));
      fetchSubscriptions();
      fetchStats();
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('payment.subscriptions.cancelError'));
    }
  };

  const handleRenew = async (id: number) => {
    try {
      await paymentService.renewUserSubscription(id);
      message.success(t('payment.subscriptions.renewSuccess'));
      fetchSubscriptions();
      fetchStats();
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('payment.subscriptions.renewError'));
    }
  };

  const statusColors: Record<string, string> = {
    active: 'success',
    canceled: 'default',
    past_due: 'warning',
    trialing: 'processing',
    expired: 'error',
  };

  const columns: ColumnsType<UserSubscription> = [
    {
      title: t('payment.subscriptions.id'),
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: t('payment.subscriptions.user'),
      key: 'user',
      render: (_, record) => record.user ? `${record.user.username} (${record.user.email})` : '-',
    },
    {
      title: t('payment.subscriptions.plan'),
      key: 'plan',
      render: (_, record) => record.plan ? (
        <div>
          <div>{record.plan.name_en}</div>
          <div style={{ fontSize: 12, color: '#999' }}>
            ${record.plan.price_usd} / {record.plan.billing_period}
          </div>
        </div>
      ) : '-',
    },
    {
      title: t('common.status'),
      dataIndex: 'status',
      key: 'status',
      render: (status) => <Tag color={statusColors[status]}>{status.toUpperCase()}</Tag>,
    },
    {
      title: t('payment.subscriptions.period'),
      key: 'period',
      render: (_, record) => (
        <div>
          <div style={{ fontSize: 12 }}>
            {new Date(record.current_period_start).toLocaleDateString()}
          </div>
          <div style={{ fontSize: 12 }}>
            → {new Date(record.current_period_end).toLocaleDateString()}
          </div>
        </div>
      ),
    },
    {
      title: t('payment.subscriptions.autoRenew'),
      dataIndex: 'auto_renew',
      key: 'auto_renew',
      render: (auto) => auto ? (
        <Tag color="green">{t('common.yes')}</Tag>
      ) : (
        <Tag>{t('common.no')}</Tag>
      ),
    },
    {
      title: t('common.actions'),
      key: 'actions',
      render: (_, record) => (
        <Space size="small">
          {record.status === 'active' && (
            <Popconfirm
              title={t('payment.subscriptions.confirmCancel')}
              onConfirm={() => handleCancel(record.id)}
              okText={t('common.yes')}
              cancelText={t('common.no')}
            >
              <Button type="link" size="small" danger>
                {t('common.cancel')}
              </Button>
            </Popconfirm>
          )}
          {record.status === 'canceled' && (
            <Button type="link" size="small" onClick={() => handleRenew(record.id)}>
              {t('payment.subscriptions.renew')}
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      {stats && (
        <Card style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={6}>
              <Statistic
                title={t('payment.subscriptions.mrr')}
                value={stats.monthly_recurring_revenue}
                precision={2}
                prefix={<DollarOutlined />}
                valueStyle={{ color: '#3f8600' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title={t('payment.subscriptions.activeSubscriptions')}
                value={stats.active_subscriptions}
                prefix={<UserOutlined />}
                valueStyle={{ color: '#1677ff' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title={t('payment.subscriptions.churnRate')}
                value={stats.churn_rate}
                precision={1}
                suffix="%"
                valueStyle={{ color: stats.churn_rate > 5 ? '#cf1322' : '#3f8600' }}
                prefix={<LineChartOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title={t('payment.subscriptions.trialingSubscriptions')}
                value={stats.trialing_subscriptions}
                prefix={<TrophyOutlined />}
              />
            </Col>
          </Row>
          <Row gutter={16} style={{ marginTop: 16 }}>
            <Col span={6}>
              <Statistic
                title={t('payment.subscriptions.totalSubscriptions')}
                value={stats.total_subscriptions}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title={t('payment.subscriptions.pastDueSubscriptions')}
                value={stats.past_due_subscriptions}
                valueStyle={{ color: '#faad14' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title={t('payment.subscriptions.canceledSubscriptions')}
                value={stats.canceled_subscriptions}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title={t('payment.subscriptions.avgSubscriptionValue')}
                value={stats.avg_subscription_value}
                precision={2}
                prefix="$"
              />
            </Col>
          </Row>
        </Card>
      )}

      <Card>
        <div style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Select
                style={{ width: '100%' }}
                placeholder={t('payment.subscriptions.filterByStatus')}
                allowClear
                onChange={setFilterStatus}
              >
                <Option value="active">{t('payment.subscriptions.active')}</Option>
                <Option value="trialing">{t('payment.subscriptions.trialing')}</Option>
                <Option value="canceled">{t('payment.subscriptions.canceled')}</Option>
                <Option value="past_due">{t('payment.subscriptions.pastDue')}</Option>
                <Option value="expired">{t('payment.subscriptions.expired')}</Option>
              </Select>
            </Col>
            <Col span={12}>
              <Button icon={<ReloadOutlined />} onClick={() => {
                fetchSubscriptions();
                fetchStats();
              }}>
                {t('common.refresh')}
              </Button>
            </Col>
          </Row>
        </div>

        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          pagination={{
            current: currentPage,
            pageSize,
            total,
            showSizeChanger: true,
            showTotal: (total) => t('common.totalItems', { total }),
            onChange: (page, size) => {
              setCurrentPage(page);
              setPageSize(size || 10);
            },
          }}
        />
      </Card>
    </div>
  );
};

export default Subscriptions;
