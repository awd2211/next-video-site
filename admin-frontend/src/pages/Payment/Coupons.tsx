import { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  DatePicker,
  message,
  Tag,
  Popconfirm,
  Card,
  Space,
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import dayjs from 'dayjs';
import type { ColumnsType } from 'antd/es/table';
import * as paymentService from '../../services/adminPaymentService';
import type { Coupon } from '../../services/adminPaymentService';

const { TextArea } = Input;
const { Option } = Select;
const { RangePicker } = DatePicker;

const Coupons = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<Coupon[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingCoupon, setEditingCoupon] = useState<Coupon | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchCoupons();
  }, [currentPage, pageSize]);

  const fetchCoupons = async () => {
    setLoading(true);
    try {
      const response = await paymentService.getCoupons({
        page: currentPage,
        page_size: pageSize,
      });
      setData(response.items || []);
      setTotal(response.total || 0);
    } catch (error: any) {
      message.error(error.message || t('payment.coupons.fetchError'));
      setData([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingCoupon(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: Coupon) => {
    setEditingCoupon(record);
    form.setFieldsValue({
      ...record,
      valid_dates: [dayjs(record.valid_from), record.valid_until ? dayjs(record.valid_until) : null],
    });
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await paymentService.deleteCoupon(id);
      message.success(t('payment.coupons.deleteSuccess'));
      fetchCoupons();
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('payment.coupons.deleteError'));
    }
  };

  const handleToggleStatus = async (record: Coupon) => {
    try {
      if (record.status === 'active') {
        await paymentService.deactivateCoupon(record.id);
        message.success(t('payment.coupons.deactivateSuccess'));
      } else {
        await paymentService.activateCoupon(record.id);
        message.success(t('payment.coupons.activateSuccess'));
      }
      fetchCoupons();
    } catch (error: any) {
      message.error(error.message || t('common.operationFailed'));
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const payload = {
        ...values,
        valid_from: values.valid_dates[0].toISOString(),
        valid_until: values.valid_dates[1] ? values.valid_dates[1].toISOString() : null,
      };
      delete payload.valid_dates;

      if (editingCoupon) {
        await paymentService.updateCoupon(editingCoupon.id, payload);
        message.success(t('payment.coupons.updateSuccess'));
      } else {
        await paymentService.createCoupon(payload);
        message.success(t('payment.coupons.createSuccess'));
      }
      setModalVisible(false);
      fetchCoupons();
    } catch (error: any) {
      message.error(error.message || t('common.operationFailed'));
    }
  };

  const columns: ColumnsType<Coupon> = [
    {
      title: t('payment.coupons.code'),
      dataIndex: 'code',
      key: 'code',
      render: (code) => <Tag color="blue">{code}</Tag>,
    },
    {
      title: t('payment.coupons.description'),
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: t('payment.coupons.discount'),
      key: 'discount',
      render: (_, record) =>
        record.discount_type === 'percentage'
          ? `${record.discount_value}%`
          : `$${record.discount_value}`,
    },
    {
      title: t('payment.coupons.usage'),
      key: 'usage',
      render: (_, record) => (
        <div>
          <div>
            {record.usage_count} / {record.usage_limit || '∞'}
          </div>
          <div style={{ fontSize: 12, color: '#999' }}>
            {t('payment.coupons.perUser')}: {record.usage_limit_per_user || '∞'}
          </div>
        </div>
      ),
    },
    {
      title: t('payment.coupons.validity'),
      key: 'validity',
      render: (_, record) => (
        <div>
          <div>{dayjs(record.valid_from).format('YYYY-MM-DD')}</div>
          {record.valid_until && (
            <div style={{ fontSize: 12 }}>→ {dayjs(record.valid_until).format('YYYY-MM-DD')}</div>
          )}
        </div>
      ),
    },
    {
      title: t('common.status'),
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const colors = {
          active: 'success',
          inactive: 'default',
          expired: 'error',
        };
        return <Tag color={colors[status as keyof typeof colors]}>{status.toUpperCase()}</Tag>;
      },
    },
    {
      title: t('common.actions'),
      key: 'actions',
      render: (_, record) => (
        <Space size="small">
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            {t('common.edit')}
          </Button>
          <Button type="link" size="small" onClick={() => handleToggleStatus(record)}>
            {record.status === 'active' ? t('common.deactivate') : t('common.activate')}
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
      <Card>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
          <h2>{t('payment.coupons.title')}</h2>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            {t('payment.coupons.create')}
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
        title={editingCoupon ? t('payment.coupons.edit') : t('payment.coupons.create')}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={600}
        okText={t('common.save')}
        cancelText={t('common.cancel')}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="code"
            label={t('payment.coupons.code')}
            rules={[{ required: true, message: t('common.required') }]}
          >
            <Input placeholder="SUMMER2025" />
          </Form.Item>

          <Form.Item name="description" label={t('payment.coupons.description')}>
            <TextArea rows={2} />
          </Form.Item>

          <Form.Item
            name="discount_type"
            label={t('payment.coupons.discountType')}
            rules={[{ required: true }]}
          >
            <Select>
              <Option value="percentage">{t('payment.coupons.percentage')}</Option>
              <Option value="fixed_amount">{t('payment.coupons.fixedAmount')}</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="discount_value"
            label={t('payment.coupons.discountValue')}
            rules={[{ required: true }]}
          >
            <InputNumber style={{ width: '100%' }} min={0} step={0.01} />
          </Form.Item>

          <Form.Item name="min_purchase_amount" label={t('payment.coupons.minPurchase')}>
            <InputNumber style={{ width: '100%' }} min={0} step={0.01} />
          </Form.Item>

          <Form.Item name="usage_limit" label={t('payment.coupons.usageLimit')}>
            <InputNumber style={{ width: '100%' }} min={1} />
          </Form.Item>

          <Form.Item name="usage_limit_per_user" label={t('payment.coupons.usageLimitPerUser')}>
            <InputNumber style={{ width: '100%' }} min={1} />
          </Form.Item>

          <Form.Item
            name="valid_dates"
            label={t('payment.coupons.validDates')}
            rules={[{ required: true }]}
          >
            <RangePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Coupons;
