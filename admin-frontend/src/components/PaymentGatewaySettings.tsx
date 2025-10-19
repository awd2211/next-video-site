import { useState } from 'react';
import { Form, Input, Switch, Button, Card, Space, Divider, message, Alert, Tag, Modal } from 'antd';
import {
  CreditCardOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ApiOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import axios from '@/utils/axios';

const { TextArea } = Input;

interface PaymentGatewaySettingsProps {
  value?: any;
  onChange?: (value: any) => void;
}

const PaymentGatewaySettings: React.FC<PaymentGatewaySettingsProps> = ({ value = {}, onChange }) => {
  const { t } = useTranslation();
  const [testingGateway, setTestingGateway] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<Record<string, any>>({});

  // 默认值
  const config = value || {
    stripe: { enabled: false, secret_key: '', publishable_key: '', webhook_secret: '', environment: 'test' },
    paypal: { enabled: false, client_id: '', client_secret: '', environment: 'sandbox' },
    alipay: { enabled: false, app_id: '', private_key: '', public_key: '', gateway_url: 'https://openapi.alipaydev.com/gateway.do' },
  };

  const updateConfig = (gateway: string, field: string, val: any) => {
    const newConfig = {
      ...config,
      [gateway]: {
        ...config[gateway],
        [field]: val,
      },
    };
    onChange?.(newConfig);
  };

  const testGatewayConnection = async (gateway: string) => {
    setTestingGateway(gateway);
    try {
      const response = await axios.post('/api/v1/admin/system/settings/test-payment-gateway', {
        gateway,
        config: config[gateway],
      });

      setTestResults({
        ...testResults,
        [gateway]: response.data,
      });

      if (response.data.success) {
        message.success(response.data.message);
      } else {
        message.error(response.data.message);
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || t('settings.payment.testFailed');
      message.error(errorMsg);
      setTestResults({
        ...testResults,
        [gateway]: {
          success: false,
          message: errorMsg,
        },
      });
    } finally {
      setTestingGateway(null);
    }
  };

  const renderTestResult = (gateway: string) => {
    const result = testResults[gateway];
    if (!result) return null;

    return (
      <Alert
        type={result.success ? 'success' : 'error'}
        message={result.message}
        icon={result.success ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
        showIcon
        closable
        onClose={() => {
          const { [gateway]: _, ...rest } = testResults;
          setTestResults(rest);
        }}
        style={{ marginTop: 12 }}
      />
    );
  };

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      {/* Stripe 配置 */}
      <Card
        title={
          <Space>
            <CreditCardOutlined style={{ color: '#635bff' }} />
            <span>Stripe</span>
            {config.stripe?.enabled && <Tag color="success">{t('common.enabled')}</Tag>}
          </Space>
        }
        size="small"
      >
        <Form layout="vertical">
          <Form.Item label={t('settings.payment.enableGateway')}>
            <Switch
              checked={config.stripe?.enabled}
              onChange={(checked) => updateConfig('stripe', 'enabled', checked)}
            />
          </Form.Item>

          <Form.Item label={t('settings.payment.environment')}>
            <Input
              value={config.stripe?.environment}
              onChange={(e) => updateConfig('stripe', 'environment', e.target.value)}
              placeholder="test / live"
              disabled={!config.stripe?.enabled}
            />
          </Form.Item>

          <Form.Item label="Secret Key">
            <Input.Password
              value={config.stripe?.secret_key}
              onChange={(e) => updateConfig('stripe', 'secret_key', e.target.value)}
              placeholder="sk_test_..."
              disabled={!config.stripe?.enabled}
            />
          </Form.Item>

          <Form.Item label="Publishable Key">
            <Input
              value={config.stripe?.publishable_key}
              onChange={(e) => updateConfig('stripe', 'publishable_key', e.target.value)}
              placeholder="pk_test_..."
              disabled={!config.stripe?.enabled}
            />
          </Form.Item>

          <Form.Item label="Webhook Secret">
            <Input.Password
              value={config.stripe?.webhook_secret}
              onChange={(e) => updateConfig('stripe', 'webhook_secret', e.target.value)}
              placeholder="whsec_..."
              disabled={!config.stripe?.enabled}
            />
          </Form.Item>

          <Button
            type="primary"
            icon={<ApiOutlined />}
            onClick={() => testGatewayConnection('stripe')}
            loading={testingGateway === 'stripe'}
            disabled={!config.stripe?.enabled || !config.stripe?.secret_key}
          >
            {t('settings.payment.testConnection')}
          </Button>

          {renderTestResult('stripe')}
        </Form>
      </Card>

      {/* PayPal 配置 */}
      <Card
        title={
          <Space>
            <CreditCardOutlined style={{ color: '#0070ba' }} />
            <span>PayPal</span>
            {config.paypal?.enabled && <Tag color="success">{t('common.enabled')}</Tag>}
          </Space>
        }
        size="small"
      >
        <Form layout="vertical">
          <Form.Item label={t('settings.payment.enableGateway')}>
            <Switch
              checked={config.paypal?.enabled}
              onChange={(checked) => updateConfig('paypal', 'enabled', checked)}
            />
          </Form.Item>

          <Form.Item label={t('settings.payment.environment')}>
            <Input
              value={config.paypal?.environment}
              onChange={(e) => updateConfig('paypal', 'environment', e.target.value)}
              placeholder="sandbox / live"
              disabled={!config.paypal?.enabled}
            />
          </Form.Item>

          <Form.Item label="Client ID">
            <Input
              value={config.paypal?.client_id}
              onChange={(e) => updateConfig('paypal', 'client_id', e.target.value)}
              placeholder="AY..."
              disabled={!config.paypal?.enabled}
            />
          </Form.Item>

          <Form.Item label="Client Secret">
            <Input.Password
              value={config.paypal?.client_secret}
              onChange={(e) => updateConfig('paypal', 'client_secret', e.target.value)}
              placeholder="E..."
              disabled={!config.paypal?.enabled}
            />
          </Form.Item>

          <Button
            type="primary"
            icon={<ApiOutlined />}
            onClick={() => testGatewayConnection('paypal')}
            loading={testingGateway === 'paypal'}
            disabled={!config.paypal?.enabled || !config.paypal?.client_id}
          >
            {t('settings.payment.testConnection')}
          </Button>

          {renderTestResult('paypal')}
        </Form>
      </Card>

      {/* Alipay 配置 */}
      <Card
        title={
          <Space>
            <CreditCardOutlined style={{ color: '#1677ff' }} />
            <span>支付宝 (Alipay)</span>
            {config.alipay?.enabled && <Tag color="success">{t('common.enabled')}</Tag>}
          </Space>
        }
        size="small"
      >
        <Form layout="vertical">
          <Form.Item label={t('settings.payment.enableGateway')}>
            <Switch
              checked={config.alipay?.enabled}
              onChange={(checked) => updateConfig('alipay', 'enabled', checked)}
            />
          </Form.Item>

          <Form.Item label="App ID">
            <Input
              value={config.alipay?.app_id}
              onChange={(e) => updateConfig('alipay', 'app_id', e.target.value)}
              placeholder="2021..."
              disabled={!config.alipay?.enabled}
            />
          </Form.Item>

          <Form.Item label={t('settings.payment.privateKey')}>
            <TextArea
              value={config.alipay?.private_key}
              onChange={(e) => updateConfig('alipay', 'private_key', e.target.value)}
              placeholder="MII..."
              rows={3}
              disabled={!config.alipay?.enabled}
            />
          </Form.Item>

          <Form.Item label={t('settings.payment.publicKey')}>
            <TextArea
              value={config.alipay?.public_key}
              onChange={(e) => updateConfig('alipay', 'public_key', e.target.value)}
              placeholder="MII..."
              rows={3}
              disabled={!config.alipay?.enabled}
            />
          </Form.Item>

          <Form.Item label={t('settings.payment.gatewayUrl')}>
            <Input
              value={config.alipay?.gateway_url}
              onChange={(e) => updateConfig('alipay', 'gateway_url', e.target.value)}
              placeholder="https://openapi.alipay.com/gateway.do"
              disabled={!config.alipay?.enabled}
            />
          </Form.Item>

          <Button
            type="primary"
            icon={<ApiOutlined />}
            onClick={() => testGatewayConnection('alipay')}
            loading={testingGateway === 'alipay'}
            disabled={!config.alipay?.enabled || !config.alipay?.app_id}
          >
            {t('settings.payment.testConnection')}
          </Button>

          {renderTestResult('alipay')}
        </Form>
      </Card>
    </Space>
  );
};

export default PaymentGatewaySettings;
