import { useState, useEffect } from 'react';
import { Modal, Form, Radio, InputNumber, Select, Input, Alert, Space, Typography } from 'antd';
import { ExclamationCircleOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

const { TextArea } = Input;
const { Text } = Typography;
const { Option } = Select;

export interface RefundFormData {
  refund_type: 'full' | 'partial';
  amount?: number;
  reason?: string;
  reason_detail?: string;
  admin_note?: string;
}

interface RefundModalProps {
  visible: boolean;
  paymentAmount: number;
  alreadyRefunded: number;
  currency: string;
  onOk: (data: RefundFormData) => Promise<void>;
  onCancel: () => void;
  loading?: boolean;
}

const RefundModal: React.FC<RefundModalProps> = ({
  visible,
  paymentAmount,
  alreadyRefunded,
  currency,
  onOk,
  onCancel,
  loading = false,
}) => {
  const { t } = useTranslation();
  const [form] = Form.useForm();
  const [refundType, setRefundType] = useState<'full' | 'partial'>('full');
  const [customReason, setCustomReason] = useState(false);

  const remainingAmount = paymentAmount - alreadyRefunded;

  useEffect(() => {
    if (visible) {
      form.resetFields();
      setRefundType('full');
      setCustomReason(false);
    }
  }, [visible, form]);

  const handleRefundTypeChange = (e: any) => {
    const type = e.target.value;
    setRefundType(type);
    if (type === 'full') {
      form.setFieldsValue({ amount: remainingAmount });
    } else {
      form.setFieldsValue({ amount: undefined });
    }
  };

  const handleReasonChange = (value: string) => {
    setCustomReason(value === 'other');
    if (value !== 'other') {
      form.setFieldsValue({ reason_detail: undefined });
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();

      const refundData: RefundFormData = {
        refund_type: refundType,
        reason: values.reason,
        reason_detail: values.reason_detail,
        admin_note: values.admin_note,
      };

      if (refundType === 'partial') {
        refundData.amount = values.amount;
      }

      await onOk(refundData);
      form.resetFields();
    } catch (error) {
      console.error('Form validation failed:', error);
    }
  };

  const refundReasons = [
    { value: 'user_request', label: t('payment.refund.reasons.userRequest') || '用户申请' },
    { value: 'service_quality', label: t('payment.refund.reasons.serviceQuality') || '服务质量问题' },
    { value: 'technical_issue', label: t('payment.refund.reasons.technicalIssue') || '技术故障' },
    { value: 'duplicate_payment', label: t('payment.refund.reasons.duplicatePayment') || '重复支付' },
    { value: 'fraud', label: t('payment.refund.reasons.fraud') || '欺诈订单' },
    { value: 'other', label: t('payment.refund.reasons.other') || '其他原因' },
  ];

  return (
    <Modal
      title={
        <Space>
          <ExclamationCircleOutlined style={{ color: '#faad14' }} />
          {t('payment.refund.title') || '处理退款'}
        </Space>
      }
      open={visible}
      onOk={handleSubmit}
      onCancel={onCancel}
      confirmLoading={loading}
      okText={t('payment.refund.confirm') || '确认退款'}
      cancelText={t('common.cancel') || '取消'}
      width={600}
      okButtonProps={{ danger: true }}
    >
      <Alert
        message={t('payment.refund.warning') || '退款操作不可撤销,请谨慎操作'}
        type="warning"
        showIcon
        style={{ marginBottom: 24 }}
      />

      <div style={{ marginBottom: 16 }}>
        <Text strong>{t('payment.refund.paymentInfo') || '支付信息'}:</Text>
        <div style={{ marginTop: 8, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
          <Space direction="vertical" size={4} style={{ width: '100%' }}>
            <div>
              <Text type="secondary">{t('payment.refund.totalAmount') || '支付总额'}:</Text>{' '}
              <Text strong>${paymentAmount.toFixed(2)} {currency.toUpperCase()}</Text>
            </div>
            {alreadyRefunded > 0 && (
              <div>
                <Text type="secondary">{t('payment.refund.alreadyRefunded') || '已退款'}:</Text>{' '}
                <Text type="danger">-${alreadyRefunded.toFixed(2)} {currency.toUpperCase()}</Text>
              </div>
            )}
            <div>
              <Text type="secondary">{t('payment.refund.remainingAmount') || '可退款额'}:</Text>{' '}
              <Text strong style={{ color: '#52c41a' }}>${remainingAmount.toFixed(2)} {currency.toUpperCase()}</Text>
            </div>
          </Space>
        </div>
      </div>

      <Form
        form={form}
        layout="vertical"
        initialValues={{
          refund_type: 'full',
          amount: remainingAmount,
        }}
      >
        <Form.Item
          label={t('payment.refund.refundType') || '退款类型'}
          name="refund_type"
          rules={[{ required: true }]}
        >
          <Radio.Group onChange={handleRefundTypeChange} value={refundType}>
            <Radio value="full">{t('payment.refund.fullRefund') || '全额退款'}</Radio>
            <Radio value="partial">{t('payment.refund.partialRefund') || '部分退款'}</Radio>
          </Radio.Group>
        </Form.Item>

        {refundType === 'partial' && (
          <Form.Item
            label={t('payment.refund.refundAmount') || '退款金额'}
            name="amount"
            rules={[
              { required: true, message: t('payment.refund.amountRequired') || '请输入退款金额' },
              {
                type: 'number',
                min: 0.01,
                max: remainingAmount,
                message: t('payment.refund.amountInvalid') || `退款金额必须在 0.01 到 ${remainingAmount.toFixed(2)} 之间`,
              },
            ]}
          >
            <InputNumber
              style={{ width: '100%' }}
              prefix="$"
              precision={2}
              placeholder={t('payment.refund.enterAmount') || '请输入退款金额'}
              max={remainingAmount}
              min={0.01}
            />
          </Form.Item>
        )}

        <Form.Item
          label={t('payment.refund.reason') || '退款原因'}
          name="reason"
          rules={[{ required: true, message: t('payment.refund.reasonRequired') || '请选择退款原因' }]}
        >
          <Select placeholder={t('payment.refund.selectReason') || '请选择退款原因'} onChange={handleReasonChange}>
            {refundReasons.map((reason) => (
              <Option key={reason.value} value={reason.value}>
                {reason.label}
              </Option>
            ))}
          </Select>
        </Form.Item>

        {customReason && (
          <Form.Item
            label={t('payment.refund.reasonDetail') || '详细说明'}
            name="reason_detail"
            rules={[
              { required: true, message: t('payment.refund.reasonDetailRequired') || '请输入详细说明' },
              { max: 500, message: t('payment.refund.reasonDetailTooLong') || '详细说明不能超过500个字符' },
            ]}
          >
            <TextArea
              rows={3}
              placeholder={t('payment.refund.reasonDetailPlaceholder') || '请详细说明退款原因...'}
              maxLength={500}
              showCount
            />
          </Form.Item>
        )}

        <Form.Item
          label={t('payment.refund.adminNote') || '管理员备注 (可选)'}
          name="admin_note"
          rules={[{ max: 1000, message: t('payment.refund.adminNoteTooLong') || '备注不能超过1000个字符' }]}
        >
          <TextArea
            rows={3}
            placeholder={t('payment.refund.adminNotePlaceholder') || '内部备注,用户不可见...'}
            maxLength={1000}
            showCount
          />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default RefundModal;
