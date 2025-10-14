import React, { useState, useEffect } from 'react';
import {
  Table,
  Card,
  Space,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  message,
  Tag,
  Typography,
  Drawer,
  Descriptions,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  EyeOutlined,
  CopyOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import {
  getTemplates,
  createTemplate,
  updateTemplate,
  deleteTemplate,
  type AITemplate,
  type TemplateCreate,
} from '../../services/ai-logs';
import '../../styles/page-layout.css';

const { Option } = Select;
const { TextArea } = Input;
const { Text } = Typography;

const TemplateManagement: React.FC = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [templates, setTemplates] = useState<AITemplate[]>([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [detailVisible, setDetailVisible] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<AITemplate | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<AITemplate | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string | undefined>();
  const [form] = Form.useForm();

  useEffect(() => {
    fetchTemplates();
  }, [categoryFilter]);

  const fetchTemplates = async () => {
    setLoading(true);
    try {
      const params = categoryFilter ? { category: categoryFilter } : {};
      const data = await getTemplates(params);
      setTemplates(data);
    } catch (error) {
      message.error(t('message.loadFailed'));
      console.error('Failed to fetch templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingTemplate(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (template: AITemplate) => {
    setEditingTemplate(template);
    form.setFieldsValue({
      ...template,
      variables: template.variables?.join(', '),
      tags: template.tags?.join(', '),
      example_variables: JSON.stringify(template.example_variables, null, 2),
      recommended_params: JSON.stringify(template.recommended_params, null, 2),
    });
    setModalVisible(true);
  };

  const handleViewDetail = (template: AITemplate) => {
    setSelectedTemplate(template);
    setDetailVisible(true);
  };

  const handleCopyPrompt = (prompt: string) => {
    navigator.clipboard.writeText(prompt);
    message.success(t('message.copied'));
  };

  const handleDelete = (templateId: number) => {
    Modal.confirm({
      title: t('common.confirmDelete'),
      content: t('aiManagement.confirmDeleteTemplate'),
      onOk: async () => {
        try {
          await deleteTemplate(templateId);
          message.success(t('message.deleteSuccess'));
          fetchTemplates();
        } catch (error) {
          message.error(t('message.deleteFailed'));
        }
      },
    });
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();

      // Parse variables and tags
      const variables = values.variables
        ? values.variables.split(',').map((v: string) => v.trim()).filter(Boolean)
        : [];
      const tags = values.tags
        ? values.tags.split(',').map((t: string) => t.trim()).filter(Boolean)
        : [];

      // Parse JSON fields
      let exampleVariables;
      let recommendedParams;

      try {
        exampleVariables = values.example_variables ? JSON.parse(values.example_variables) : undefined;
      } catch {
        message.error(t('aiManagement.invalidExampleVariablesJson'));
        return;
      }

      try {
        recommendedParams = values.recommended_params ? JSON.parse(values.recommended_params) : undefined;
      } catch {
        message.error(t('aiManagement.invalidRecommendedParamsJson'));
        return;
      }

      const data: TemplateCreate = {
        name: values.name,
        category: values.category,
        description: values.description,
        prompt_template: values.prompt_template,
        variables,
        example_variables: exampleVariables,
        recommended_provider: values.recommended_provider,
        recommended_model: values.recommended_model,
        recommended_params: recommendedParams,
        tags,
      };

      if (editingTemplate) {
        await updateTemplate(editingTemplate.id, data);
        message.success(t('message.updateSuccess'));
      } else {
        await createTemplate(data);
        message.success(t('message.createSuccess'));
      }

      setModalVisible(false);
      fetchTemplates();
    } catch (error) {
      console.error('Form validation failed:', error);
    }
  };

  const columns: ColumnsType<AITemplate> = [
    {
      title: t('common.id'),
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: t('common.name'),
      dataIndex: 'name',
      key: 'name',
      width: 200,
      ellipsis: true,
    },
    {
      title: t('aiManagement.category'),
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (category: string) => <Tag color="blue">{category}</Tag>,
    },
    {
      title: t('common.description'),
      dataIndex: 'description',
      key: 'description',
      width: 250,
      ellipsis: true,
    },
    {
      title: t('aiManagement.variables'),
      dataIndex: 'variables',
      key: 'variables',
      width: 150,
      render: (variables: string[]) => (
        <Space size="small" wrap>
          {variables?.slice(0, 3).map((v, i) => (
            <Tag key={i} color="green">
              {v}
            </Tag>
          ))}
          {variables?.length > 3 && <Tag>+{variables.length - 3}</Tag>}
        </Space>
      ),
    },
    {
      title: t('aiManagement.recommendedModel'),
      dataIndex: 'recommended_model',
      key: 'recommended_model',
      width: 180,
      ellipsis: true,
    },
    {
      title: t('aiManagement.usageCount'),
      dataIndex: 'usage_count',
      key: 'usage_count',
      width: 100,
      sorter: (a, b) => a.usage_count - b.usage_count,
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
      width: 200,
      fixed: 'right',
      render: (_: any, record: AITemplate) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            {t('common.detail')}
          </Button>
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
            <h2 style={{ margin: 0 }}>{t('aiManagement.templateManagement')}</h2>
            <Space>
              <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                {t('aiManagement.createTemplate')}
              </Button>
              <Button icon={<ReloadOutlined />} onClick={fetchTemplates}>
                {t('common.refresh')}
              </Button>
            </Space>
          </div>

          <Card size="small">
            <Space>
              <Select
                placeholder={t('aiManagement.selectCategory')}
                style={{ width: 200 }}
                allowClear
                value={categoryFilter}
                onChange={setCategoryFilter}
              >
                <Option value="content_generation">{t('aiManagement.contentGeneration')}</Option>
                <Option value="content_moderation">{t('aiManagement.contentModeration')}</Option>
                <Option value="summarization">{t('aiManagement.summarization')}</Option>
                <Option value="translation">{t('aiManagement.translation')}</Option>
                <Option value="analysis">{t('aiManagement.analysis')}</Option>
              </Select>
            </Space>
          </Card>
        </Space>
      </div>

      <div className="page-content">
        <Table
          columns={columns}
          dataSource={templates}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1500 }}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => t('common.totalItems', { total }),
          }}
        />
      </div>

      {/* Create/Edit Modal */}
      <Modal
        title={editingTemplate ? t('aiManagement.editTemplate') : t('aiManagement.createTemplate')}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={800}
      >
        <Form form={form} layout="vertical">
          <Form.Item label={t('common.name')} name="name" rules={[{ required: true }]}>
            <Input placeholder={t('aiManagement.templateNamePlaceholder')} />
          </Form.Item>

          <Form.Item label={t('aiManagement.category')} name="category" rules={[{ required: true }]}>
            <Select>
              <Option value="content_generation">{t('aiManagement.contentGeneration')}</Option>
              <Option value="content_moderation">{t('aiManagement.contentModeration')}</Option>
              <Option value="summarization">{t('aiManagement.summarization')}</Option>
              <Option value="translation">{t('aiManagement.translation')}</Option>
              <Option value="analysis">{t('aiManagement.analysis')}</Option>
            </Select>
          </Form.Item>

          <Form.Item label={t('common.description')} name="description">
            <TextArea rows={2} placeholder={t('aiManagement.templateDescriptionPlaceholder')} />
          </Form.Item>

          <Form.Item
            label={t('aiManagement.promptTemplate')}
            name="prompt_template"
            rules={[{ required: true }]}
          >
            <TextArea rows={6} placeholder={t('aiManagement.promptTemplatePlaceholder')} />
          </Form.Item>

          <Form.Item
            label={t('aiManagement.variables')}
            name="variables"
            tooltip={t('aiManagement.variablesTooltip')}
          >
            <Input placeholder="variable1, variable2, variable3" />
          </Form.Item>

          <Form.Item
            label={t('aiManagement.exampleVariables')}
            name="example_variables"
            tooltip={t('aiManagement.exampleVariablesTooltip')}
          >
            <TextArea rows={3} placeholder='{"variable1": "example value"}' />
          </Form.Item>

          <Form.Item label={t('aiManagement.recommendedProvider')} name="recommended_provider">
            <Select allowClear>
              <Option value="openai">OpenAI</Option>
              <Option value="grok">Grok</Option>
              <Option value="google">Google</Option>
            </Select>
          </Form.Item>

          <Form.Item label={t('aiManagement.recommendedModel')} name="recommended_model">
            <Input placeholder="gpt-4, grok-beta, gemini-pro" />
          </Form.Item>

          <Form.Item
            label={t('aiManagement.recommendedParams')}
            name="recommended_params"
            tooltip={t('aiManagement.recommendedParamsTooltip')}
          >
            <TextArea rows={3} placeholder='{"temperature": 0.7, "max_tokens": 1000}' />
          </Form.Item>

          <Form.Item label={t('aiManagement.tags')} name="tags">
            <Input placeholder="tag1, tag2, tag3" />
          </Form.Item>

          <Form.Item label={t('common.status')} name="is_active" valuePropName="checked" initialValue={true}>
            <Switch checkedChildren={t('common.active')} unCheckedChildren={t('common.inactive')} />
          </Form.Item>
        </Form>
      </Modal>

      {/* Detail Drawer */}
      <Drawer
        title={t('aiManagement.templateDetail')}
        placement="right"
        width={720}
        open={detailVisible}
        onClose={() => setDetailVisible(false)}
      >
        {selectedTemplate && (
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <Descriptions title={t('aiManagement.basicInfo')} bordered column={2}>
              <Descriptions.Item label={t('common.id')}>{selectedTemplate.id}</Descriptions.Item>
              <Descriptions.Item label={t('common.name')}>{selectedTemplate.name}</Descriptions.Item>
              <Descriptions.Item label={t('aiManagement.category')}>
                <Tag color="blue">{selectedTemplate.category}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label={t('common.status')}>
                <Tag color={selectedTemplate.is_active ? 'green' : 'default'}>
                  {selectedTemplate.is_active ? t('common.active') : t('common.inactive')}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label={t('aiManagement.usageCount')} span={2}>
                {selectedTemplate.usage_count}
              </Descriptions.Item>
              <Descriptions.Item label={t('common.description')} span={2}>
                {selectedTemplate.description || 'N/A'}
              </Descriptions.Item>
            </Descriptions>

            <Card
              title={t('aiManagement.promptTemplate')}
              size="small"
              extra={
                <Button
                  type="link"
                  size="small"
                  icon={<CopyOutlined />}
                  onClick={() => handleCopyPrompt(selectedTemplate.prompt_template)}
                >
                  {t('common.copy')}
                </Button>
              }
            >
              <Text code style={{ whiteSpace: 'pre-wrap' }}>
                {selectedTemplate.prompt_template}
              </Text>
            </Card>

            {selectedTemplate.variables && selectedTemplate.variables.length > 0 && (
              <Card title={t('aiManagement.variables')} size="small">
                <Space size="small" wrap>
                  {selectedTemplate.variables.map((v, i) => (
                    <Tag key={i} color="green">
                      {v}
                    </Tag>
                  ))}
                </Space>
              </Card>
            )}

            {selectedTemplate.example_variables && (
              <Card title={t('aiManagement.exampleVariables')} size="small">
                <pre>{JSON.stringify(selectedTemplate.example_variables, null, 2)}</pre>
              </Card>
            )}

            <Descriptions title={t('aiManagement.recommendations')} bordered column={2}>
              <Descriptions.Item label={t('aiManagement.provider')}>
                {selectedTemplate.recommended_provider || 'N/A'}
              </Descriptions.Item>
              <Descriptions.Item label={t('aiManagement.model')}>
                {selectedTemplate.recommended_model || 'N/A'}
              </Descriptions.Item>
            </Descriptions>

            {selectedTemplate.recommended_params && (
              <Card title={t('aiManagement.recommendedParams')} size="small">
                <pre>{JSON.stringify(selectedTemplate.recommended_params, null, 2)}</pre>
              </Card>
            )}

            {selectedTemplate.tags && selectedTemplate.tags.length > 0 && (
              <Card title={t('aiManagement.tags')} size="small">
                <Space size="small" wrap>
                  {selectedTemplate.tags.map((tag, i) => (
                    <Tag key={i}>{tag}</Tag>
                  ))}
                </Space>
              </Card>
            )}

            <Descriptions bordered column={2}>
              <Descriptions.Item label={t('common.createdAt')}>
                {dayjs(selectedTemplate.created_at).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
              <Descriptions.Item label={t('common.updatedAt')}>
                {dayjs(selectedTemplate.updated_at).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
            </Descriptions>
          </Space>
        )}
      </Drawer>
    </div>
  );
};

export default TemplateManagement;
