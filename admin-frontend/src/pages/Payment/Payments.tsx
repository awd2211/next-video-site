import { useState, useEffect } from 'react';
import { Table, Tag, Card, Row, Col, Statistic, Input, Select, Button, message, Popconfirm, Space, Tooltip } from 'antd';
import { DollarOutlined, ReloadOutlined, SearchOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import * as paymentService from '../../services/adminPaymentService';
import type { Payment } from '../../services/adminPaymentService';
import type { ColumnsType } from 'antd/es/table';
import RefundModal, { RefundFormData } from './components/RefundModal';

const { Search } = Input;
const { Option } = Select;

const Payments = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<Payment[]>([]);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState<any>({});
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [filterStatus, setFilterStatus] = useState<string>();
  const [filterProvider, setFilterProvider] = useState<string>();
  const [refundModalVisible, setRefundModalVisible] = useState(false);
  const [selectedPayment, setSelectedPayment] = useState<Payment | null>(null);
  const [refundLoading, setRefundLoading] = useState(false);

  useEffect(() => {
    fetchPayments();
    fetchStats();
  }, [currentPage, pageSize, filterStatus, filterProvider]);

  const fetchPayments = async () => {
    setLoading(true);
    try {
      const response = await paymentService.getPayments({
        page: currentPage,
        page_size: pageSize,
        status: filterStatus,
        payment_provider: filterProvider,
      });
      setData(response.items || []);
      setTotal(response.total || 0);
    } catch (error: any) {
      message.error(error.message || t('payment.payments.fetchError'));
      setData([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const stats = await paymentService.getPaymentStats();
      setStats(stats);
    } catch (error) {
      console.error('Failed to fetch stats', error);
    }
  };

  const handleOpenRefundModal = (payment: Payment) => {
    setSelectedPayment(payment);
    setRefundModalVisible(true);
  };

  const handleCloseRefundModal = () => {
    setRefundModalVisible(false);
    setSelectedPayment(null);
  };

  const handleRefund = async (refundData: RefundFormData) => {
    if (!selectedPayment) return;

    setRefundLoading(true);
    try {
      await paymentService.refundPayment(selectedPayment.id, {
        amount: refundData.amount,
        reason: refundData.reason,
        reason_detail: refundData.reason_detail,
        admin_note: refundData.admin_note,
      });
      message.success(t('payment.payments.refundSuccess') || '退款成功');
      fetchPayments();
      fetchStats();
      handleCloseRefundModal();
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('payment.payments.refundError') || '退款失败');
    } finally {
      setRefundLoading(false);
    }
  };

  const statusColors: Record<string, string> = {
    pending: 'processing',
    succeeded: 'success',
    failed: 'error',
    refunded: 'warning',
    canceled: 'default',
  };

  const providerColors: Record<string, string> = {
    stripe: 'blue',
    paypal: 'cyan',
    alipay: 'green',
  };

  const columns: ColumnsType<Payment> = [
    {
      title: t('payment.payments.id'),
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: t('payment.payments.user'),
      key: 'user',
      render: (_, record) => record.user ? `${record.user.username} (${record.user.email})` : '-',
    },
    {
      title: t('payment.payments.amount'),
      key: 'amount',
      render: (_, record) => `$${parseFloat(record.amount).toFixed(2)} ${record.currency.toUpperCase()}`,
    },
    {
      title: t('payment.payments.provider'),
      dataIndex: 'payment_provider',
      key: 'payment_provider',
      render: (provider) => <Tag color={providerColors[provider]}>{provider.toUpperCase()}</Tag>,
    },
    {
      title: t('common.status'),
      dataIndex: 'status',
      key: 'status',
      render: (status) => <Tag color={statusColors[status]}>{status.toUpperCase()}</Tag>,
    },
    {
      title: t('payment.payments.paidAt'),
      dataIndex: 'paid_at',
      key: 'paid_at',
      render: (date) => (date ? new Date(date).toLocaleString() : '-'),
    },
    {
      title: t('common.actions'),
      key: 'actions',
      width: 200,
      render: (_, record) => {
        const canRefund = record.status === 'succeeded' || record.status === 'partially_refunded';
        const isFullyRefunded = record.status === 'refunded';
        const refundedAmount = parseFloat(record.refund_amount || '0');
        const totalAmount = parseFloat(record.amount);
        const hasPartialRefund = refundedAmount > 0 && refundedAmount < totalAmount;

        return (
          <Space size="small" direction="vertical" style={{ width: '100%' }}>
            {canRefund && !isFullyRefunded && (
              <Button
                type="link"
                size="small"
                danger
                onClick={() => handleOpenRefundModal(record)}
              >
                {hasPartialRefund ? t('payment.payments.refundAgain') || '继续退款' : t('payment.payments.refund') || '退款'}
              </Button>
            )}
            {hasPartialRefund && (
              <Tooltip title={`${t('payment.refund.alreadyRefunded')}: $${refundedAmount.toFixed(2)}`}>
                <Tag color="orange">
                  {t('payment.payments.partiallyRefunded') || '部分退款'}
                </Tag>
              </Tooltip>
            )}
            {isFullyRefunded && record.refunded_at && (
              <Tooltip title={new Date(record.refunded_at).toLocaleString()}>
                <Tag color="red">
                  {t('payment.payments.fullyRefunded') || '已全额退款'}
                </Tag>
              </Tooltip>
            )}
            {record.refund_reason && (
              <Tooltip title={record.refund_reason}>
                <Tag color="blue" style={{ fontSize: '11px', cursor: 'pointer' }}>
                  {t('payment.refund.viewReason') || '查看原因'}
                </Tag>
              </Tooltip>
            )}
          </Space>
        );
      },
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={6}>
            <Statistic
              title={t('payment.payments.totalRevenue')}
              value={stats.total_revenue || 0}
              precision={2}
              prefix="$"
              valueStyle={{ color: '#3f8600' }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title={t('payment.payments.totalRefunded')}
              value={stats.total_refunded || 0}
              precision={2}
              prefix="$"
              valueStyle={{ color: '#cf1322' }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title={t('payment.payments.successRate')}
              value={stats.success_rate || 0}
              precision={1}
              suffix="%"
            />
          </Col>
          <Col span={6}>
            <Statistic
              title={t('payment.payments.avgTransaction')}
              value={stats.avg_transaction_value || 0}
              precision={2}
              prefix="$"
            />
          </Col>
        </Row>
      </Card>

      <Card>
        <div style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={8}>
              <Select
                style={{ width: '100%' }}
                placeholder={t('payment.payments.filterByStatus')}
                allowClear
                onChange={setFilterStatus}
              >
                <Option value="pending">{t('payment.payments.pending')}</Option>
                <Option value="succeeded">{t('payment.payments.succeeded')}</Option>
                <Option value="failed">{t('payment.payments.failed')}</Option>
                <Option value="refunded">{t('payment.payments.refunded')}</Option>
              </Select>
            </Col>
            <Col span={8}>
              <Select
                style={{ width: '100%' }}
                placeholder={t('payment.payments.filterByProvider')}
                allowClear
                onChange={setFilterProvider}
              >
                <Option value="stripe">Stripe</Option>
                <Option value="paypal">PayPal</Option>
                <Option value="alipay">Alipay</Option>
              </Select>
            </Col>
            <Col span={8}>
              <Button icon={<ReloadOutlined />} onClick={fetchPayments}>
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

      {selectedPayment && (
        <RefundModal
          visible={refundModalVisible}
          paymentAmount={parseFloat(selectedPayment.amount)}
          alreadyRefunded={parseFloat(selectedPayment.refund_amount || '0')}
          currency={selectedPayment.currency}
          onOk={handleRefund}
          onCancel={handleCloseRefundModal}
          loading={refundLoading}
        />
      )}
    </div>
  );
};

export default Payments;
