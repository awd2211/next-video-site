import React, { useState, useEffect } from 'react';
import {
  Table,
  Card,
  Space,
  Button,
  Modal,
  Form,
  InputNumber,
  Select,
  Switch,
  message,
  Tag,
  Progress,
  Tooltip,
  Typography,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import type { ColumnsType } from 'antd/es/table';
import {
  getQuotas,
  createQuota,
  updateQuota,
  deleteQuota,
  getGlobalQuotaStatus,
  type AIQuota,
  type QuotaCreate,
  type AIQuotaStatus,
} from '../../services/ai-logs';
import '../../styles/page-layout.css';

const { Option } = Select;
const { Text } = Typography;

const QuotaManagement: React.FC = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [quotas, setQuotas] = useState<AIQuota[]>([]);
  const [globalStatus, setGlobalStatus] = useState<AIQuotaStatus | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingQuota, setEditingQuota] = useState<AIQuota | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [quotasData, statusData] = await Promise.all([
        getQuotas(),
        getGlobalQuotaStatus(),
      ]);
      setQuotas(quotasData);
      setGlobalStatus(statusData);
    } catch (error) {
      message.error(t('message.loadFailed'));
      console.error('Failed to fetch quotas:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingQuota(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (quota: AIQuota) => {
    setEditingQuota(quota);
    form.setFieldsValue({
      ...quota,
      is_active: quota.is_active ?? true,
    });
    setModalVisible(true);
  };

  const handleDelete = (quotaId: number) => {
    Modal.confirm({
      title: t('common.confirmDelete'),
      content: t('aiManagement.confirmDeleteQuota'),
      onOk: async () => {
        try {
          await deleteQuota(quotaId);
          message.success(t('message.deleteSuccess'));
          fetchData();
        } catch (error) {
          message.error(t('message.deleteFailed'));
        }
      },
    });
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const data: QuotaCreate = {
        ...values,
      };

      if (editingQuota) {
        await updateQuota(editingQuota.id, data);
        message.success(t('message.updateSuccess'));
      } else {
        await createQuota(data);
        message.success(t('message.createSuccess'));
      }

      setModalVisible(false);
      fetchData();
    } catch (error) {
      console.error('Form validation failed:', error);
    }
  };

  const getUsagePercentage = (used: number, limit?: number) => {
    if (!limit) return 0;
    return (used / limit) * 100;
  };

  const getUsageStatus = (percentage: number): 'success' | 'exception' | 'normal' => {
    if (percentage >= 90) return 'exception';
    if (percentage >= 70) return 'normal';
    return 'success';
  };

  const columns: ColumnsType<AIQuota> = [
    {
      title: t('common.id'),
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: t('aiManagement.quotaType'),
      dataIndex: 'quota_type',
      key: 'quota_type',
      width: 120,
      render: (type: string) => {
        const colors: Record<string, string> = {
          global: 'blue',
          user: 'green',
          provider: 'orange',
        };
        return <Tag color={colors[type] || 'default'}>{type.toUpperCase()}</Tag>;
      },
    },
    {
      title: t('aiManagement.targetId'),
      dataIndex: 'target_id',
      key: 'target_id',
      width: 100,
      render: (id?: number) => id || 'N/A',
    },
    {
      title: t('aiManagement.dailyRequests'),
      key: 'daily_requests',
      width: 200,
      render: (_: any, record: AIQuota) => {
        if (!record.daily_request_limit) return 'N/A';
        const percentage = getUsagePercentage(record.daily_requests_used, record.daily_request_limit);
        return (
          <div>
            <div style={{ marginBottom: 4 }}>
              {record.daily_requests_used} / {record.daily_request_limit}
            </div>
            <Progress
              percent={percentage}
              size="small"
              status={getUsageStatus(percentage)}
              showInfo={false}
            />
          </div>
        );
      },
    },
    {
      title: t('aiManagement.monthlyRequests'),
      key: 'monthly_requests',
      width: 200,
      render: (_: any, record: AIQuota) => {
        if (!record.monthly_request_limit) return 'N/A';
        const percentage = getUsagePercentage(record.monthly_requests_used, record.monthly_request_limit);
        return (
          <div>
            <div style={{ marginBottom: 4 }}>
              {record.monthly_requests_used} / {record.monthly_request_limit}
            </div>
            <Progress
              percent={percentage}
              size="small"
              status={getUsageStatus(percentage)}
              showInfo={false}
            />
          </div>
        );
      },
    },
    {
      title: t('aiManagement.dailyCost'),
      key: 'daily_cost',
      width: 180,
      render: (_: any, record: AIQuota) => {
        if (!record.daily_cost_limit) return 'N/A';
        const percentage = getUsagePercentage(record.daily_cost_used, record.daily_cost_limit);
        return (
          <div>
            <div style={{ marginBottom: 4 }}>
              ${record.daily_cost_used.toFixed(2)} / ${record.daily_cost_limit.toFixed(2)}
            </div>
            <Progress
              percent={percentage}
              size="small"
              status={getUsageStatus(percentage)}
              showInfo={false}
            />
          </div>
        );
      },
    },
    {
      title: t('aiManagement.rateLimit'),
      key: 'rate_limit',
      width: 150,
      render: (_: any, record: AIQuota) => {
        const limits = [];
        if (record.rate_limit_per_minute) {
          limits.push(`${record.rate_limit_per_minute}/min`);
        }
        if (record.rate_limit_per_hour) {
          limits.push(`${record.rate_limit_per_hour}/hr`);
        }
        return limits.length > 0 ? limits.join(', ') : 'N/A';
      },
    },
    {
      title: t('common.status'),
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'default'}>
          {isActive ? t('common.active') : t('common.inactive')}
        </Tag>
      ),
    },
    {
      title: t('common.actions'),
      key: 'actions',
      width: 150,
      fixed: 'right',
      render: (_: any, record: AIQuota) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            {t('common.edit')}
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

  return (
    <div className="page-container">
      <div className="page-header">
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={{ margin: 0 }}>{t('aiManagement.quotaManagement')}</h2>
            <Space>
              <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                {t('aiManagement.createQuota')}
              </Button>
              <Button icon={<ReloadOutlined />} onClick={fetchData}>
                {t('common.refresh')}
              </Button>
            </Space>
          </div>

          {/* Global Quota Status */}
          {globalStatus?.has_quota && globalStatus.quota && (
            <Card size="small" title={t('aiManagement.globalQuotaStatus')}>
              <Space direction="vertical" style={{ width: '100%' }}>
                {globalStatus.is_limited && (
                  <Tag color="red" icon={<InfoCircleOutlined />}>
                    {t('aiManagement.quotaLimited')}: {globalStatus.limit_reason}
                  </Tag>
                )}
                <Space size="large" wrap>
                  {globalStatus.daily_remaining_requests !== undefined && (
                    <Tooltip title={t('aiManagement.dailyRemainingRequests')}>
                      <Text>
                        {t('aiManagement.dailyRequests')}: {globalStatus.quota.daily_requests_used} /{' '}
                        {globalStatus.quota.daily_request_limit} (
                        <Text type={globalStatus.daily_remaining_requests < 100 ? 'danger' : 'success'}>
                          {globalStatus.daily_remaining_requests} {t('common.remaining')}
                        </Text>
                        )
                      </Text>
                    </Tooltip>
                  )}
                  {globalStatus.monthly_remaining_requests !== undefined && (
                    <Tooltip title={t('aiManagement.monthlyRemainingRequests')}>
                      <Text>
                        {t('aiManagement.monthlyRequests')}: {globalStatus.quota.monthly_requests_used} /{' '}
                        {globalStatus.quota.monthly_request_limit} (
                        <Text type={globalStatus.monthly_remaining_requests < 1000 ? 'danger' : 'success'}>
                          {globalStatus.monthly_remaining_requests} {t('common.remaining')}
                        </Text>
                        )
                      </Text>
                    </Tooltip>
                  )}
                  {globalStatus.daily_remaining_cost !== undefined && (
                    <Tooltip title={t('aiManagement.dailyRemainingCost')}>
                      <Text>
                        {t('aiManagement.dailyCost')}: ${globalStatus.quota.daily_cost_used.toFixed(2)} / $
                        {globalStatus.quota.daily_cost_limit?.toFixed(2)} (
                        <Text type={globalStatus.daily_remaining_cost < 1 ? 'danger' : 'success'}>
                          ${globalStatus.daily_remaining_cost.toFixed(2)} {t('common.remaining')}
                        </Text>
                        )
                      </Text>
                    </Tooltip>
                  )}
                </Space>
              </Space>
            </Card>
          )}
        </Space>
      </div>

      <div className="page-content">
        <Table
          columns={columns}
          dataSource={quotas}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1400 }}
          pagination={false}
        />
      </div>

      <Modal
        title={editingQuota ? t('aiManagement.editQuota') : t('aiManagement.createQuota')}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={700}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label={t('aiManagement.quotaType')}
            name="quota_type"
            rules={[{ required: true }]}
          >
            <Select>
              <Option value="global">{t('aiManagement.globalQuota')}</Option>
              <Option value="user">{t('aiManagement.userQuota')}</Option>
              <Option value="provider">{t('aiManagement.providerQuota')}</Option>
            </Select>
          </Form.Item>

          <Form.Item label={t('aiManagement.targetId')} name="target_id">
            <InputNumber style={{ width: '100%' }} placeholder={t('aiManagement.targetIdPlaceholder')} />
          </Form.Item>

          <Form.Item label={t('aiManagement.dailyRequestLimit')} name="daily_request_limit">
            <InputNumber style={{ width: '100%' }} min={0} />
          </Form.Item>

          <Form.Item label={t('aiManagement.monthlyRequestLimit')} name="monthly_request_limit">
            <InputNumber style={{ width: '100%' }} min={0} />
          </Form.Item>

          <Form.Item label={t('aiManagement.dailyTokenLimit')} name="daily_token_limit">
            <InputNumber style={{ width: '100%' }} min={0} />
          </Form.Item>

          <Form.Item label={t('aiManagement.monthlyTokenLimit')} name="monthly_token_limit">
            <InputNumber style={{ width: '100%' }} min={0} />
          </Form.Item>

          <Form.Item label={t('aiManagement.dailyCostLimit')} name="daily_cost_limit">
            <InputNumber style={{ width: '100%' }} min={0} step={0.01} prefix="$" />
          </Form.Item>

          <Form.Item label={t('aiManagement.monthlyCostLimit')} name="monthly_cost_limit">
            <InputNumber style={{ width: '100%' }} min={0} step={0.01} prefix="$" />
          </Form.Item>

          <Form.Item label={t('aiManagement.rateLimitPerMinute')} name="rate_limit_per_minute">
            <InputNumber style={{ width: '100%' }} min={0} />
          </Form.Item>

          <Form.Item label={t('aiManagement.rateLimitPerHour')} name="rate_limit_per_hour">
            <InputNumber style={{ width: '100%' }} min={0} />
          </Form.Item>

          <Form.Item label={t('common.status')} name="is_active" valuePropName="checked" initialValue={true}>
            <Switch checkedChildren={t('common.active')} unCheckedChildren={t('common.inactive')} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default QuotaManagement;
