import React from 'react';
import {
  Form,
  Input,
  InputNumber,
  Switch,
  Button,
  Space,
  message,
  Slider,
  Select,
  Collapse,
  Typography,
} from 'antd';
import { useMutation } from '@tanstack/react-query';
import {
  createSentryConfig,
  updateSentryConfig,
  type SentryConfig,
  type SentryConfigCreate,
  type SentryConfigUpdate,
} from '@/services/sentryConfig';
import { useTranslation } from 'react-i18next';

const { TextArea } = Input;
const { Text } = Typography;
const { Panel } = Collapse;

interface ConfigFormProps {
  config?: SentryConfig;
  onSuccess: () => void;
  onCancel: () => void;
}

const ConfigForm: React.FC<ConfigFormProps> = ({ config, onSuccess, onCancel }) => {
  const { t } = useTranslation();
  const [form] = Form.useForm();
  const isEditing = !!config;

  // 创建配置
  const createMutation = useMutation({
    mutationFn: createSentryConfig,
    onSuccess: () => {
      message.success(t('创建成功'));
      onSuccess();
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('创建失败'));
    },
  });

  // 更新配置
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: SentryConfigUpdate }) =>
      updateSentryConfig(id, data),
    onSuccess: () => {
      message.success(t('更新成功'));
      onSuccess();
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('更新失败'));
    },
  });

  // 表单提交
  const handleSubmit = async (values: any) => {
    // 将采样率转换为字符串
    const data = {
      ...values,
      traces_sample_rate: values.traces_sample_rate.toString(),
      replays_session_sample_rate: values.replays_session_sample_rate.toString(),
      replays_on_error_sample_rate: values.replays_on_error_sample_rate.toString(),
    };

    if (isEditing) {
      updateMutation.mutate({ id: config.id, data });
    } else {
      createMutation.mutate(data as SentryConfigCreate);
    }
  };

  // 初始值
  const initialValues = config
    ? {
        ...config,
        traces_sample_rate: parseFloat(config.traces_sample_rate),
        replays_session_sample_rate: parseFloat(config.replays_session_sample_rate),
        replays_on_error_sample_rate: parseFloat(config.replays_on_error_sample_rate),
      }
    : {
        environment: 'production',
        frontend_enabled: true,
        admin_frontend_enabled: true,
        traces_sample_rate: 1.0,
        replays_session_sample_rate: 0.1,
        replays_on_error_sample_rate: 1.0,
        debug_mode: false,
        attach_stacktrace: true,
      };

  return (
    <Form
      form={form}
      layout="vertical"
      initialValues={initialValues}
      onFinish={handleSubmit}
    >
      {/* 基础配置 */}
      <Form.Item
        label="Sentry DSN"
        name="dsn"
        rules={[
          { required: true, message: t('请输入 Sentry DSN') },
          { type: 'url', message: t('请输入有效的 URL') },
        ]}
        tooltip="从 Sentry 项目设置中获取 DSN"
      >
        <Input placeholder="https://xxx@xxx.ingest.sentry.io/xxx" />
      </Form.Item>

      <Form.Item
        label={t('环境')}
        name="environment"
        rules={[{ required: true, message: t('请选择环境') }]}
      >
        <Select>
          <Select.Option value="production">Production</Select.Option>
          <Select.Option value="staging">Staging</Select.Option>
          <Select.Option value="development">Development</Select.Option>
        </Select>
      </Form.Item>

      <Form.Item label={t('版本号')} name="release_version">
        <Input placeholder="1.0.0" />
      </Form.Item>

      {/* 启用状态 */}
      <Space size="large" style={{ marginBottom: '24px' }}>
        <Form.Item
          label={t('用户前端')}
          name="frontend_enabled"
          valuePropName="checked"
          style={{ marginBottom: 0 }}
        >
          <Switch />
        </Form.Item>

        <Form.Item
          label={t('管理前端')}
          name="admin_frontend_enabled"
          valuePropName="checked"
          style={{ marginBottom: 0 }}
        >
          <Switch />
        </Form.Item>

        <Form.Item
          label={t('调试模式')}
          name="debug_mode"
          valuePropName="checked"
          style={{ marginBottom: 0 }}
        >
          <Switch />
        </Form.Item>

        <Form.Item
          label={t('附加堆栈')}
          name="attach_stacktrace"
          valuePropName="checked"
          style={{ marginBottom: 0 }}
        >
          <Switch />
        </Form.Item>
      </Space>

      {/* 采样率配置 */}
      <Collapse defaultActiveKey={['sampling']} style={{ marginBottom: '16px' }}>
        <Panel header={t('采样率配置')} key="sampling">
          <Form.Item
            label={t('性能监控采样率')}
            name="traces_sample_rate"
            tooltip="0-1 之间，1 表示 100%"
          >
            <Slider
              min={0}
              max={1}
              step={0.1}
              marks={{ 0: '0%', 0.5: '50%', 1: '100%' }}
            />
          </Form.Item>

          <Form.Item
            label={t('会话回放采样率')}
            name="replays_session_sample_rate"
            tooltip="正常会话的回放采样率"
          >
            <Slider
              min={0}
              max={1}
              step={0.1}
              marks={{ 0: '0%', 0.5: '50%', 1: '100%' }}
            />
          </Form.Item>

          <Form.Item
            label={t('错误回放采样率')}
            name="replays_on_error_sample_rate"
            tooltip="发生错误时的回放采样率"
          >
            <Slider
              min={0}
              max={1}
              step={0.1}
              marks={{ 0: '0%', 0.5: '50%', 1: '100%' }}
            />
          </Form.Item>
        </Panel>

        {/* 过滤配置 */}
        <Panel header={t('过滤配置（高级）')} key="filters">
          <Form.Item
            label={t('忽略的错误')}
            name="ignore_errors"
            tooltip="JSON 数组格式，如：[\"ResizeObserver\", \"NetworkError\"]"
          >
            <TextArea
              rows={3}
              placeholder='["ResizeObserver loop limit exceeded", "NetworkError"]'
            />
          </Form.Item>

          <Form.Item
            label={t('允许的 URL')}
            name="allowed_urls"
            tooltip="JSON 数组格式，只上报这些 URL 的错误"
          >
            <TextArea
              rows={3}
              placeholder='["https://example.com", "https://cdn.example.com"]'
            />
          </Form.Item>

          <Form.Item
            label={t('拒绝的 URL')}
            name="denied_urls"
            tooltip="JSON 数组格式，不上报这些 URL 的错误"
          >
            <TextArea
              rows={3}
              placeholder='["https://ads.example.com", "https://tracker.com"]'
            />
          </Form.Item>
        </Panel>
      </Collapse>

      <Form.Item label={t('配置说明')} name="description">
        <TextArea rows={3} placeholder={t('可选的配置说明')} />
      </Form.Item>

      {/* 表单按钮 */}
      <Form.Item style={{ marginBottom: 0, marginTop: '24px' }}>
        <Space>
          <Button
            type="primary"
            htmlType="submit"
            loading={createMutation.isPending || updateMutation.isPending}
          >
            {isEditing ? t('更新') : t('创建')}
          </Button>
          <Button onClick={onCancel}>{t('取消')}</Button>
        </Space>
      </Form.Item>
    </Form>
  );
};

export default ConfigForm;
