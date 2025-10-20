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
        label={t('sentry.dsn')}
        name="dsn"
        rules={[
          { required: true, message: t('sentry.dsnRequired') },
          { type: 'url', message: t('sentry.validUrl') },
        ]}
        tooltip={t('sentry.dsnTooltip')}
      >
        <Input placeholder={t('sentry.dsnPlaceholder')} />
      </Form.Item>

      <Form.Item
        label={t('环境')}
        name="environment"
        rules={[{ required: true, message: t('sentry.selectEnvironment') }]}
      >
        <Select>
          <Select.Option value="production">Production</Select.Option>
          <Select.Option value="staging">Staging</Select.Option>
          <Select.Option value="development">Development</Select.Option>
        </Select>
      </Form.Item>

      <Form.Item label={t('sentry.versionNumber')} name="release_version">
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
          label={t('sentry.attachStacktrace')}
          name="attach_stacktrace"
          valuePropName="checked"
          style={{ marginBottom: 0 }}
        >
          <Switch />
        </Form.Item>
      </Space>

      {/* 采样率配置 */}
      <Collapse defaultActiveKey={['sampling']} style={{ marginBottom: '16px' }}>
        <Panel header={t('sentry.samplingConfig')} key="sampling">
          <Form.Item
            label={t('sentry.performanceSamplingRate')}
            name="traces_sample_rate"
            tooltip={t('sentry.performanceSamplingTooltip')}
          >
            <Slider
              min={0}
              max={1}
              step={0.1}
              marks={{ 0: '0%', 0.5: '50%', 1: '100%' }}
            />
          </Form.Item>

          <Form.Item
            label={t('sentry.sessionReplaySamplingRate')}
            name="replays_session_sample_rate"
            tooltip={t('sentry.sessionReplayTooltip')}
          >
            <Slider
              min={0}
              max={1}
              step={0.1}
              marks={{ 0: '0%', 0.5: '50%', 1: '100%' }}
            />
          </Form.Item>

          <Form.Item
            label={t('sentry.errorReplaySamplingRate')}
            name="replays_on_error_sample_rate"
            tooltip={t('sentry.errorReplayTooltip')}
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
        <Panel header={t('sentry.filterConfig')} key="filters">
          <Form.Item
            label={t('sentry.ignoreErrors')}
            name="ignore_errors"
            tooltip={t('sentry.ignoreErrorsTooltip')}
          >
            <TextArea
              rows={3}
              placeholder={t('sentry.ignoreErrorsPlaceholder')}
            />
          </Form.Item>

          <Form.Item
            label={t('sentry.allowedUrls')}
            name="allowed_urls"
            tooltip={t('sentry.allowedUrlsTooltip')}
          >
            <TextArea
              rows={3}
              placeholder={t('sentry.allowedUrlsPlaceholder')}
            />
          </Form.Item>

          <Form.Item
            label={t('sentry.deniedUrls')}
            name="denied_urls"
            tooltip={t('sentry.deniedUrlsTooltip')}
          >
            <TextArea
              rows={3}
              placeholder={t('sentry.deniedUrlsPlaceholder')}
            />
          </Form.Item>
        </Panel>
      </Collapse>

      <Form.Item label={t('sentry.configDescription')} name="description">
        <TextArea rows={3} placeholder={t('sentry.optionalDescription')} />
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
