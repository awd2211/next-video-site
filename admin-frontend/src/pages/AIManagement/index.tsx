import { useState } from 'react';
import {
  Card,
  Tabs,
  Button,
  Table,
  Space,
  Tag,
  Modal,
  message,
  Popconfirm,
  Badge,
  Statistic,
  Row,
  Col,
  Tooltip,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ThunderboltOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ApiOutlined,
  RobotOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import {
  getAIProviders,
  deleteAIProvider,
  getAIUsageStats,
  type AIProvider,
} from '@/services/aiManagement';
import AIProviderForm from './AIProviderForm';
import AITestPanel from './AITestPanel';
import './styles.css';

const AIManagement = () => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [selectedTab, setSelectedTab] = useState<string>('openai');
  const [formVisible, setFormVisible] = useState(false);
  const [testVisible, setTestVisible] = useState(false);
  const [editingProvider, setEditingProvider] = useState<AIProvider | undefined>();
  const [testingProvider, setTestingProvider] = useState<AIProvider | undefined>();

  // Fetch providers
  const { data: providersData, isLoading } = useQuery({
    queryKey: ['ai-providers', selectedTab],
    queryFn: () => getAIProviders({ provider_type: selectedTab }),
  });

  // Fetch usage stats
  const { data: usageStats } = useQuery({
    queryKey: ['ai-usage-stats'],
    queryFn: getAIUsageStats,
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: deleteAIProvider,
    onSuccess: () => {
      message.success(t('ai.deleteSuccess'));
      queryClient.invalidateQueries({ queryKey: ['ai-providers'] });
      queryClient.invalidateQueries({ queryKey: ['ai-usage-stats'] });
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('ai.deleteFailed'));
    },
  });

  const handleEdit = (provider: AIProvider) => {
    setEditingProvider(provider);
    setFormVisible(true);
  };

  const handleDelete = async (id: number) => {
    await deleteMutation.mutateAsync(id);
  };

  const handleTest = (provider: AIProvider) => {
    setTestingProvider(provider);
    setTestVisible(true);
  };

  const handleFormClose = () => {
    setFormVisible(false);
    setEditingProvider(undefined);
  };

  const handleTestClose = () => {
    setTestVisible(false);
    setTestingProvider(undefined);
  };

  const getProviderIcon = (type: string) => {
    switch (type) {
      case 'openai':
        return '🤖';
      case 'grok':
        return '⚡';
      case 'google':
        return '🔍';
      default:
        return '🤖';
    }
  };

  const columns = [
    {
      title: t('ai.name'),
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: AIProvider) => (
        <Space>
          <span style={{ fontSize: 20 }}>{getProviderIcon(record.provider_type)}</span>
          <div>
            <div style={{ fontWeight: 500 }}>{text}</div>
            {record.description && (
              <div style={{ fontSize: 12, color: '#999' }}>{record.description}</div>
            )}
          </div>
        </Space>
      ),
    },
    {
      title: t('ai.model'),
      dataIndex: 'model_name',
      key: 'model_name',
      render: (text: string) => <Tag color="blue">{text}</Tag>,
    },
    {
      title: t('ai.status'),
      key: 'status',
      width: 120,
      render: (record: AIProvider) => (
        <Space direction="vertical" size="small">
          <Tag color={record.enabled ? 'success' : 'default'}>
            {record.enabled ? t('ai.enabled') : t('ai.disabled')}
          </Tag>
          {record.is_default && <Tag color="gold">{t('ai.default')}</Tag>}
        </Space>
      ),
    },
    {
      title: t('ai.usage'),
      key: 'usage',
      width: 150,
      render: (record: AIProvider) => (
        <Space direction="vertical" size="small" style={{ fontSize: 12 }}>
          <div>
            {t('ai.requests')}: <strong>{record.total_requests}</strong>
          </div>
          <div>
            {t('ai.tokens')}: <strong>{record.total_tokens.toLocaleString()}</strong>
          </div>
        </Space>
      ),
    },
    {
      title: t('ai.lastTest'),
      key: 'last_test',
      width: 120,
      render: (record: AIProvider) => {
        if (!record.last_test_at) return <span style={{ color: '#999' }}>-</span>;
        return (
          <Tooltip title={record.last_test_message}>
            <Space>
              {record.last_test_status === 'success' ? (
                <CheckCircleOutlined style={{ color: '#52c41a' }} />
              ) : (
                <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
              )}
              <span style={{ fontSize: 11 }}>
                {new Date(record.last_test_at).toLocaleString()}
              </span>
            </Space>
          </Tooltip>
        );
      },
    },
    {
      title: t('common.actions'),
      key: 'actions',
      width: 180,
      fixed: 'right' as const,
      render: (record: AIProvider) => (
        <Space size="small">
          <Tooltip title={t('ai.test')}>
            <Button
              type="text"
              size="small"
              icon={<ThunderboltOutlined />}
              onClick={() => handleTest(record)}
            />
          </Tooltip>
          <Tooltip title={t('common.edit')}>
            <Button
              type="text"
              size="small"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          <Popconfirm
            title={t('ai.deleteConfirm')}
            onConfirm={() => handleDelete(record.id)}
            okText={t('common.confirm')}
            cancelText={t('common.cancel')}
          >
            <Tooltip title={t('common.delete')}>
              <Button
                type="text"
                size="small"
                danger
                icon={<DeleteOutlined />}
                loading={deleteMutation.isPending}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const tabItems = [
    {
      key: 'openai',
      label: (
        <Space>
          <span>🤖</span>
          <span>OpenAI</span>
          <Badge
            count={providersData?.items.filter((p) => p.provider_type === 'openai').length || 0}
            showZero
            style={{ backgroundColor: '#52c41a' }}
          />
        </Space>
      ),
    },
    {
      key: 'grok',
      label: (
        <Space>
          <span>⚡</span>
          <span>Grok (xAI)</span>
          <Badge
            count={providersData?.items.filter((p) => p.provider_type === 'grok').length || 0}
            showZero
            style={{ backgroundColor: '#52c41a' }}
          />
        </Space>
      ),
    },
    {
      key: 'google',
      label: (
        <Space>
          <span>🔍</span>
          <span>Google AI</span>
          <Badge
            count={providersData?.items.filter((p) => p.provider_type === 'google').length || 0}
            showZero
            style={{ backgroundColor: '#52c41a' }}
          />
        </Space>
      ),
    },
  ];

  return (
    <div className="ai-management-page">
      <div className="page-header" style={{ marginBottom: 24 }}>
        <div className="header-content">
          <div className="header-title">
            <RobotOutlined style={{ fontSize: 28, marginRight: 12 }} />
            <div>
              <h2 style={{ margin: 0 }}>{t('ai.title')}</h2>
              <p style={{ margin: 0, color: '#999', fontSize: 14 }}>{t('ai.subtitle')}</p>
            </div>
          </div>
          <Button
            type="primary"
            size="large"
            icon={<PlusOutlined />}
            onClick={() => setFormVisible(true)}
          >
            {t('ai.addProvider')}
          </Button>
        </div>
      </div>

      {/* Usage Statistics */}
      {usageStats && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={8}>
            <Card bordered={false}>
              <Statistic
                title={t('ai.totalRequests')}
                value={usageStats.total_requests}
                prefix={<ApiOutlined />}
                valueStyle={{ color: '#3f8600' }}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card bordered={false}>
              <Statistic
                title={t('ai.totalTokens')}
                value={usageStats.total_tokens}
                prefix={<RobotOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card bordered={false}>
              <Statistic
                title={t('ai.activeProviders')}
                value={usageStats.stats.filter((s) => s.enabled).length}
                suffix={`/ ${usageStats.stats.length}`}
                valueStyle={{ color: '#cf1322' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* Providers Table */}
      <Card bordered={false}>
        <Tabs
          activeKey={selectedTab}
          onChange={setSelectedTab}
          items={tabItems}
          tabBarStyle={{ marginBottom: 16 }}
        />
        <Table
          columns={columns}
          dataSource={providersData?.items || []}
          rowKey="id"
          loading={isLoading}
          pagination={{
            pageSize: 10,
            showTotal: (total) => t('common.total', { count: total }),
          }}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* Provider Form Modal */}
      <Modal
        title={editingProvider ? t('ai.editProvider') : t('ai.addProvider')}
        open={formVisible}
        onCancel={handleFormClose}
        footer={null}
        width={800}
        destroyOnClose
      >
        <AIProviderForm
          provider={editingProvider}
          providerType={selectedTab as 'openai' | 'grok' | 'google'}
          onSuccess={handleFormClose}
          onCancel={handleFormClose}
        />
      </Modal>

      {/* Test Panel Modal */}
      <Modal
        title={t('ai.testProvider')}
        open={testVisible}
        onCancel={handleTestClose}
        footer={null}
        width={900}
        destroyOnClose
      >
        {testingProvider && <AITestPanel provider={testingProvider} />}
      </Modal>
    </div>
  );
};

export default AIManagement;
