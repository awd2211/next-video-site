import React, { useState } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  message,
  Modal,
  Tooltip,
  Typography,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import ConfigForm from './ConfigForm';
import {
  getSentryConfigs,
  deleteSentryConfig,
  type SentryConfig,
} from '@/services/sentryConfig';
import { useTranslation } from 'react-i18next';

const { Title, Text } = Typography;
const { confirm } = Modal;

const SentryConfigPage: React.FC = () => {
  const { t } = useTranslation();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingConfig, setEditingConfig] = useState<SentryConfig | undefined>();
  const queryClient = useQueryClient();

  // 获取配置列表
  const { data: configs, isLoading } = useQuery({
    queryKey: ['sentryConfigs'],
    queryFn: getSentryConfigs,
  });

  // 删除配置
  const deleteMutation = useMutation({
    mutationFn: deleteSentryConfig,
    onSuccess: () => {
      message.success(t('删除成功'));
      queryClient.invalidateQueries({ queryKey: ['sentryConfigs'] });
    },
    onError: () => {
      message.error(t('删除失败'));
    },
  });

  // 打开创建/编辑表单
  const handleOpenForm = (config?: SentryConfig) => {
    setEditingConfig(config);
    setIsModalOpen(true);
  };

  // 关闭表单
  const handleCloseForm = () => {
    setIsModalOpen(false);
    setEditingConfig(undefined);
  };

  // 确认删除
  const handleDelete = (id: number) => {
    confirm({
      title: t('确认删除'),
      icon: <ExclamationCircleOutlined />,
      content: t('确定要删除这个 Sentry 配置吗？此操作不可恢复。'),
      okText: t('删除'),
      okType: 'danger',
      cancelText: t('取消'),
      onOk: () => {
        deleteMutation.mutate(id);
      },
    });
  };

  // 表格列定义
  const columns: ColumnsType<SentryConfig> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: t('环境'),
      dataIndex: 'environment',
      key: 'environment',
      width: 120,
      render: (env: string) => (
        <Tag color={env === 'production' ? 'red' : env === 'staging' ? 'orange' : 'blue'}>
          {env}
        </Tag>
      ),
    },
    {
      title: 'DSN',
      dataIndex: 'dsn',
      key: 'dsn',
      ellipsis: true,
      render: (dsn: string) => (
        <Tooltip title={dsn}>
          <Text code style={{ fontSize: '12px' }}>
            {dsn.substring(0, 40)}...
          </Text>
        </Tooltip>
      ),
    },
    {
      title: t('前端状态'),
      key: 'frontend_status',
      width: 120,
      render: (_, record) => (
        <Space>
          <Tooltip title={t('用户前端')}>
            {record.frontend_enabled ? (
              <CheckCircleOutlined style={{ color: '#52c41a' }} />
            ) : (
              <ExclamationCircleOutlined style={{ color: '#d9d9d9' }} />
            )}
          </Tooltip>
          <Tooltip title={t('管理前端')}>
            {record.admin_frontend_enabled ? (
              <CheckCircleOutlined style={{ color: '#52c41a' }} />
            ) : (
              <ExclamationCircleOutlined style={{ color: '#d9d9d9' }} />
            )}
          </Tooltip>
        </Space>
      ),
    },
    {
      title: t('性能采样率'),
      dataIndex: 'traces_sample_rate',
      key: 'traces_sample_rate',
      width: 120,
      render: (rate: string) => `${(parseFloat(rate) * 100).toFixed(0)}%`,
    },
    {
      title: t('调试模式'),
      dataIndex: 'debug_mode',
      key: 'debug_mode',
      width: 100,
      render: (debug: boolean) =>
        debug ? <Tag color="orange">{t('开启')}</Tag> : <Tag>{t('关闭')}</Tag>,
    },
    {
      title: t('版本'),
      dataIndex: 'release_version',
      key: 'release_version',
      width: 120,
      render: (version: string) => version || '-',
    },
    {
      title: t('创建时间'),
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: t('操作'),
      key: 'actions',
      width: 150,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleOpenForm(record)}
          >
            {t('编辑')}
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
            loading={deleteMutation.isPending}
          >
            {t('删除')}
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Title level={4} style={{ margin: 0 }}>
              Sentry 错误监控配置
            </Title>
            <Text type="secondary" style={{ fontSize: '14px' }}>
              管理前端错误监控和性能追踪配置
            </Text>
          </div>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => handleOpenForm()}
          >
            {t('新建配置')}
          </Button>
        </div>

        <Table
          columns={columns}
          dataSource={configs}
          rowKey="id"
          loading={isLoading}
          pagination={{
            showSizeChanger: true,
            showTotal: (total) => `${t('共')} ${total} ${t('条')}`,
          }}
          scroll={{ x: 1400 }}
        />
      </Card>

      {/* 创建/编辑表单模态框 */}
      <Modal
        title={editingConfig ? t('编辑 Sentry 配置') : t('新建 Sentry 配置')}
        open={isModalOpen}
        onCancel={handleCloseForm}
        footer={null}
        width={800}
        destroyOnClose
      >
        <ConfigForm
          config={editingConfig}
          onSuccess={() => {
            handleCloseForm();
            queryClient.invalidateQueries({ queryKey: ['sentryConfigs'] });
          }}
          onCancel={handleCloseForm}
        />
      </Modal>
    </div>
  );
};

export default SentryConfigPage;
