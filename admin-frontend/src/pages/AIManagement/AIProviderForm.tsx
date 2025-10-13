import { useEffect, useState } from 'react';
import {
  Form,
  Input,
  Select,
  InputNumber,
  Switch,
  Button,
  Space,
  message,
  Divider,
  Slider,
  Card,
} from 'antd';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import {
  createAIProvider,
  updateAIProvider,
  getAvailableModels,
  type AIProvider,
  type AIProviderCreate,
  type AIProviderUpdate,
} from '@/services/aiManagement';

interface AIProviderFormProps {
  provider?: AIProvider;
  providerType: 'openai' | 'grok' | 'google';
  onSuccess: () => void;
  onCancel: () => void;
}

const AIProviderForm: React.FC<AIProviderFormProps> = ({
  provider,
  providerType,
  onSuccess,
  onCancel,
}) => {
  const { t } = useTranslation();
  const [form] = Form.useForm();
  const queryClient = useQueryClient();
  const [selectedProvider, setSelectedProvider] = useState(provider?.provider_type || providerType);

  // Fetch available models
  const { data: modelsData } = useQuery({
    queryKey: ['ai-models', selectedProvider],
    queryFn: () => getAvailableModels(selectedProvider),
  });

  // Create mutation
  const createMutation = useMutation({
    mutationFn: createAIProvider,
    onSuccess: () => {
      message.success(t('ai.createSuccess'));
      queryClient.invalidateQueries({ queryKey: ['ai-providers'] });
      onSuccess();
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('ai.createFailed'));
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: AIProviderUpdate }) =>
      updateAIProvider(id, data),
    onSuccess: () => {
      message.success(t('ai.updateSuccess'));
      queryClient.invalidateQueries({ queryKey: ['ai-providers'] });
      onSuccess();
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('ai.updateFailed'));
    },
  });

  useEffect(() => {
    if (provider) {
      form.setFieldsValue({
        ...provider,
        temperature: provider.temperature || 0.7,
        top_p: provider.top_p || 1.0,
        max_tokens: provider.max_tokens || 2048,
        frequency_penalty: provider.frequency_penalty || 0.0,
        presence_penalty: provider.presence_penalty || 0.0,
      });
      setSelectedProvider(provider.provider_type);
    } else {
      form.setFieldsValue({
        provider_type: providerType,
        enabled: true,
        is_default: false,
        temperature: 0.7,
        top_p: 1.0,
        max_tokens: 2048,
        frequency_penalty: 0.0,
        presence_penalty: 0.0,
      });
    }
  }, [provider, providerType, form]);

  const handleSubmit = async (values: any) => {
    if (provider) {
      await updateMutation.mutateAsync({ id: provider.id, data: values });
    } else {
      await createMutation.mutateAsync(values as AIProviderCreate);
    }
  };

  const getBaseUrlPlaceholder = (type: string) => {
    switch (type) {
      case 'openai':
        return 'https://api.openai.com/v1';
      case 'grok':
        return 'https://api.x.ai/v1';
      case 'google':
        return 'Leave empty for default';
      default:
        return '';
    }
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleSubmit}
      autoComplete="off"
      initialValues={{
        enabled: true,
        is_default: false,
        temperature: 0.7,
        top_p: 1.0,
        max_tokens: 2048,
        frequency_penalty: 0.0,
        presence_penalty: 0.0,
      }}
    >
      <Card title={t('ai.basicInfo')} size="small" style={{ marginBottom: 16 }}>
        <Form.Item
          label={t('ai.name')}
          name="name"
          rules={[{ required: true, message: t('ai.nameRequired') }]}
        >
          <Input placeholder={t('ai.namePlaceholder')} />
        </Form.Item>

        <Form.Item
          label={t('ai.providerType')}
          name="provider_type"
          rules={[{ required: true }]}
        >
          <Select
            disabled={!!provider}
            onChange={(value) => setSelectedProvider(value)}
            options={[
              { label: '🤖 OpenAI', value: 'openai' },
              { label: '⚡ Grok (xAI)', value: 'grok' },
              { label: '🔍 Google AI', value: 'google' },
            ]}
          />
        </Form.Item>

        <Form.Item label={t('ai.description')} name="description">
          <Input.TextArea
            rows={2}
            placeholder={t('ai.descriptionPlaceholder')}
            showCount
            maxLength={200}
          />
        </Form.Item>
      </Card>

      <Card title={t('ai.apiConfig')} size="small" style={{ marginBottom: 16 }}>
        <Form.Item
          label={t('ai.apiKey')}
          name="api_key"
          rules={[{ required: true, message: t('ai.apiKeyRequired') }]}
        >
          <Input.Password placeholder={t('ai.apiKeyPlaceholder')} />
        </Form.Item>

        <Form.Item label={t('ai.baseUrl')} name="base_url">
          <Input placeholder={getBaseUrlPlaceholder(selectedProvider)} />
        </Form.Item>

        <Form.Item
          label={t('ai.model')}
          name="model_name"
          rules={[{ required: true, message: t('ai.modelRequired') }]}
        >
          <Select
            showSearch
            placeholder={t('ai.modelPlaceholder')}
            options={modelsData?.models.map((model) => ({
              label: `${model.name} - ${model.description}`,
              value: model.id,
            }))}
          />
        </Form.Item>
      </Card>

      <Card title={t('ai.modelParameters')} size="small" style={{ marginBottom: 16 }}>
        <Form.Item label={t('ai.maxTokens')} name="max_tokens">
          <InputNumber
            min={1}
            max={128000}
            style={{ width: '100%' }}
            placeholder="2048"
          />
        </Form.Item>

        <Form.Item label={t('ai.temperature')} name="temperature">
          <Slider
            min={0}
            max={2}
            step={0.1}
            marks={{
              0: '0 (Focused)',
              1: '1 (Balanced)',
              2: '2 (Creative)',
            }}
          />
        </Form.Item>

        <Form.Item label={t('ai.topP')} name="top_p">
          <Slider
            min={0}
            max={1}
            step={0.1}
            marks={{
              0: '0',
              0.5: '0.5',
              1: '1',
            }}
          />
        </Form.Item>

        <Form.Item label={t('ai.frequencyPenalty')} name="frequency_penalty">
          <Slider
            min={-2}
            max={2}
            step={0.1}
            marks={{
              '-2': '-2',
              0: '0',
              2: '2',
            }}
          />
        </Form.Item>

        <Form.Item label={t('ai.presencePenalty')} name="presence_penalty">
          <Slider
            min={-2}
            max={2}
            step={0.1}
            marks={{
              '-2': '-2',
              0: '0',
              2: '2',
            }}
          />
        </Form.Item>
      </Card>

      <Card title={t('ai.settings')} size="small" style={{ marginBottom: 16 }}>
        <Space size="large">
          <Form.Item label={t('ai.enabled')} name="enabled" valuePropName="checked">
            <Switch />
          </Form.Item>

          <Form.Item label={t('ai.setAsDefault')} name="is_default" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Space>
      </Card>

      <Divider />

      <Form.Item style={{ marginBottom: 0 }}>
        <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
          <Button onClick={onCancel}>{t('common.cancel')}</Button>
          <Button
            type="primary"
            htmlType="submit"
            loading={createMutation.isPending || updateMutation.isPending}
          >
            {provider ? t('common.update') : t('common.create')}
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
};

export default AIProviderForm;
