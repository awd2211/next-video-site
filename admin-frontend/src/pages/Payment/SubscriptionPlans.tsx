import { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  Switch,
  message,
  Tag,
  Popconfirm,
  Card,
  Row,
  Col,
  Statistic,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  DollarOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import type { ColumnsType } from 'antd/es/table';
import * as paymentService from '../../services/adminPaymentService';
import type { SubscriptionPlan } from '../../services/adminPaymentService';

const { TextArea } = Input;
const { Option } = Select;

const SubscriptionPlans = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<SubscriptionPlan[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingPlan, setEditingPlan] = useState<SubscriptionPlan | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchPlans();
  }, [currentPage, pageSize]);

  const fetchPlans = async () => {
    setLoading(true);
    try {
      const response = await paymentService.getSubscriptionPlans({
        page: currentPage,
        page_size: pageSize,
      });
      setData(response.items || []);
      setTotal(response.total || 0);
    } catch (error: any) {
      message.error(error.message || t('payment.plans.fetchError'));
      setData([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingPlan(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: SubscriptionPlan) => {
    setEditingPlan(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await paymentService.deleteSubscriptionPlan(id);
      message.success(t('payment.plans.deleteSuccess'));
      fetchPlans();
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('payment.plans.deleteError'));
    }
  };

  const handleToggleStatus = async (record: SubscriptionPlan) => {
    try {
      if (record.is_active) {
        await paymentService.deactivateSubscriptionPlan(record.id);
        message.success(t('payment.plans.deactivateSuccess'));
      } else {
        await paymentService.activateSubscriptionPlan(record.id);
        message.success(t('payment.plans.activateSuccess'));
      }
      fetchPlans();
    } catch (error: any) {
      message.error(error.message || t('common.operationFailed'));
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingPlan) {
        await paymentService.updateSubscriptionPlan(editingPlan.id, values);
        message.success(t('payment.plans.updateSuccess'));
      } else {
        await paymentService.createSubscriptionPlan(values);
        message.success(t('payment.plans.createSuccess'));
      }
      setModalVisible(false);
      fetchPlans();
    } catch (error: any) {
      message.error(error.message || t('common.operationFailed'));
    }
  };

  const columns: ColumnsType<SubscriptionPlan> = [
    {
      title: t('payment.plans.name'),
      dataIndex: 'name_en',
      key: 'name',
      render: (text, record) => (
        <div>
          <div>{record.name_en}</div>
          <div style={{ fontSize: 12, color: '#999' }}>{record.name_zh}</div>
        </div>
      ),
    },
    {
      title: t('payment.plans.billingPeriod'),
      dataIndex: 'billing_period',
      key: 'billing_period',
      render: (period) => {
        const colors = {
          monthly: 'blue',
          quarterly: 'green',
          yearly: 'purple',
          lifetime: 'gold',
        };
        return <Tag color={colors[period as keyof typeof colors]}>{period.toUpperCase()}</Tag>;
      },
    },
    {
      title: t('payment.plans.price'),
      key: 'price',
      render: (_, record) => (
        <div>
          <div style={{ fontWeight: 600 }}>${record.price_usd}</div>
          {record.price_cny && <div style={{ fontSize: 12 }}>¥{record.price_cny}</div>}
        </div>
      ),
    },
    {
      title: t('payment.plans.features'),
      key: 'features',
      render: (_, record) => (
        <Space size={4} wrap>
          <Tag>{record.max_video_quality.toUpperCase()}</Tag>
          <Tag>{record.max_concurrent_streams} {t('payment.plans.streams')}</Tag>
          {record.allow_downloads && <Tag color="green">{t('payment.plans.downloads')}</Tag>}
          {record.ads_free && <Tag color="gold">{t('payment.plans.adsFree')}</Tag>}
        </Space>
      ),
    },
    {
      title: t('common.status'),
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive) =>
        isActive ? (
          <Tag color="success" icon={<CheckCircleOutlined />}>
            {t('common.active')}
          </Tag>
        ) : (
          <Tag color="default" icon={<CloseCircleOutlined />}>
            {t('common.inactive')}
          </Tag>
        ),
    },
    {
      title: t('payment.plans.popular'),
      dataIndex: 'is_popular',
      key: 'is_popular',
      render: (isPopular) => (isPopular ? <Tag color="red">{t('payment.plans.popular')}</Tag> : '-'),
    },
    {
      title: t('common.actions'),
      key: 'actions',
      render: (_, record) => (
        <Space size="small">
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            {t('common.edit')}
          </Button>
          <Button
            type="link"
            size="small"
            onClick={() => handleToggleStatus(record)}
          >
            {record.is_active ? t('common.deactivate') : t('common.activate')}
          </Button>
          <Popconfirm
            title={t('common.confirmDelete')}
            onConfirm={() => handleDelete(record.id)}
            okText={t('common.yes')}
            cancelText={t('common.no')}
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              {t('common.delete')}
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={6}>
            <Statistic
              title={t('payment.plans.totalPlans')}
              value={total}
              prefix={<DollarOutlined />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title={t('payment.plans.activePlans')}
              value={data.filter((p) => p.is_active).length}
              valueStyle={{ color: '#3f8600' }}
            />
          </Col>
        </Row>
      </Card>

      <Card>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
          <h2>{t('payment.plans.title')}</h2>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            {t('payment.plans.create')}
          </Button>
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

      <Modal
        title={editingPlan ? t('payment.plans.edit') : t('payment.plans.create')}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={800}
        okText={t('common.save')}
        cancelText={t('common.cancel')}
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="name_en"
                label={t('payment.plans.nameEn')}
                rules={[{ required: true, message: t('common.required') }]}
              >
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="name_zh" label={t('payment.plans.nameZh')}>
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="billing_period"
                label={t('payment.plans.billingPeriod')}
                rules={[{ required: true }]}
              >
                <Select>
                  <Option value="monthly">{t('payment.plans.monthly')}</Option>
                  <Option value="quarterly">{t('payment.plans.quarterly')}</Option>
                  <Option value="yearly">{t('payment.plans.yearly')}</Option>
                  <Option value="lifetime">{t('payment.plans.lifetime')}</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="price_usd"
                label={t('payment.plans.priceUsd')}
                rules={[{ required: true }]}
              >
                <InputNumber style={{ width: '100%' }} min={0} step={0.01} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="price_cny" label={t('payment.plans.priceCny')}>
                <InputNumber style={{ width: '100%' }} min={0} step={0.01} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="price_eur" label={t('payment.plans.priceEur')}>
                <InputNumber style={{ width: '100%' }} min={0} step={0.01} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="trial_days" label={t('payment.plans.trialDays')}>
                <InputNumber style={{ width: '100%' }} min={0} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="max_video_quality"
                label={t('payment.plans.videoQuality')}
                rules={[{ required: true }]}
              >
                <Select>
                  <Option value="sd">SD (480p)</Option>
                  <Option value="hd">HD (720p)</Option>
                  <Option value="fhd">Full HD (1080p)</Option>
                  <Option value="4k">4K (2160p)</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item
                name="max_concurrent_streams"
                label={t('payment.plans.streams')}
                rules={[{ required: true }]}
              >
                <InputNumber style={{ width: '100%' }} min={1} />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item
                name="max_devices"
                label={t('payment.plans.devices')}
                rules={[{ required: true }]}
              >
                <InputNumber style={{ width: '100%' }} min={1} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={6}>
              <Form.Item name="allow_downloads" valuePropName="checked">
                <Switch checkedChildren={t('payment.plans.downloads')} unCheckedChildren="No" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="allow_offline" valuePropName="checked">
                <Switch checkedChildren={t('payment.plans.offline')} unCheckedChildren="No" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="ads_free" valuePropName="checked">
                <Switch checkedChildren={t('payment.plans.adsFree')} unCheckedChildren="Ads" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="is_popular" valuePropName="checked">
                <Switch checkedChildren={t('payment.plans.popular')} unCheckedChildren="Normal" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="description_en" label={t('payment.plans.descriptionEn')}>
            <TextArea rows={2} />
          </Form.Item>

          <Form.Item name="description_zh" label={t('payment.plans.descriptionZh')}>
            <TextArea rows={2} />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="features_en" label={t('payment.plans.featuresEn')}>
                <TextArea rows={3} placeholder="Feature 1&#10;Feature 2&#10;Feature 3" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="features_zh" label={t('payment.plans.featuresZh')}>
                <TextArea rows={3} placeholder="功能1&#10;功能2&#10;功能3" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="sort_order" label={t('payment.plans.sortOrder')}>
                <InputNumber style={{ width: '100%' }} min={0} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="is_active" valuePropName="checked">
                <Switch checkedChildren={t('common.active')} unCheckedChildren={t('common.inactive')} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default SubscriptionPlans;
