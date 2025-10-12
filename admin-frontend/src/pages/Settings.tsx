/**
 * Settings Page - Notion Style
 * Collapse Accordion + Auto-save + 0-click Editing
 * 参考: Notion、Vercel、Linear 的设置页面设计
 */

import { useState, useCallback, useEffect } from 'react';
import {
  Form,
  Collapse,
  Input,
  Switch,
  Select,
  InputNumber,
  message,
  Button,
  Space,
  Tag,
  Skeleton,
  Divider,
  Row,
  Col,
  Card,
} from 'antd';
import {
  SearchOutlined,
  CheckCircleOutlined,
  SaveOutlined,
  ReloadOutlined,
  MailOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { debounce } from 'lodash';
import axios from '@/utils/axios';
import './SettingsNotion.css';

const { Panel } = Collapse;
const { TextArea } = Input;
const { Option } = Select;

const Settings = () => {
  const [form] = Form.useForm();
  const [searchValue, setSearchValue] = useState('');
  const [savedFields, setSavedFields] = useState<Set<string>>(new Set());
  const [saving, setSaving] = useState(false);
  const queryClient = useQueryClient();

  // Fetch system settings
  const { data: settings, isLoading } = useQuery({
    queryKey: ['system-settings'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/system/settings');
      return response.data;
    },
  });

  // Update settings mutation
  const updateMutation = useMutation({
    mutationFn: async (values: any) => {
      const response = await axios.put('/api/v1/admin/system/settings', values);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['system-settings'] });
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '保存失败');
    },
  });

  // Debounced auto-save (1秒后自动保存)
  const debouncedSave = useCallback(
    debounce(async (changedValues: any, allValues: any) => {
      try {
        setSaving(true);
        await updateMutation.mutateAsync(allValues);

        // 标记字段为已保存
        const changedKeys = Object.keys(changedValues);
        setSavedFields(new Set(changedKeys));

        // 2秒后清除标记
        setTimeout(() => {
          setSavedFields(new Set());
        }, 2000);
      } catch (error) {
        // Error handled by mutation
      } finally {
        setSaving(false);
      }
    }, 1000),
    []
  );

  // 初始化表单值
  useEffect(() => {
    if (settings) {
      form.setFieldsValue(settings);
    }
  }, [settings, form]);

  // 手动保存所有
  const handleSaveAll = async () => {
    try {
      const values = await form.validateFields();
      setSaving(true);
      await updateMutation.mutateAsync(values);
      message.success('所有设置已保存');
    } catch (error) {
      message.error('请检查表单填写');
    } finally {
      setSaving(false);
    }
  };

  // 重置为默认值
  const handleReset = () => {
    if (window.confirm('确定要重置所有设置为默认值吗？此操作不可恢复。')) {
      form.resetFields();
      message.success('已重置为默认值');
    }
  };

  // 设置分组配置
  const sections = [
    {
      key: 'site',
      title: '🌐 网站与 SEO',
      keywords: '网站 site seo 搜索 优化',
      defaultOpen: true,
    },
    {
      key: 'video',
      title: '📹 视频与上传',
      keywords: '视频 上传 video upload',
      defaultOpen: true,
    },
    {
      key: 'community',
      title: '💬 用户与社区',
      keywords: '用户 评论 user comment community',
      defaultOpen: false,
    },
    {
      key: 'email',
      title: '📧 邮件服务',
      keywords: '邮件 email smtp mailgun',
      defaultOpen: false,
    },
    {
      key: 'security',
      title: '🔒 安全配置',
      keywords: '安全 security 验证码 captcha',
      defaultOpen: false,
    },
    {
      key: 'other',
      title: '⚙️ 其他设置',
      keywords: '其他 维护 other maintenance',
      defaultOpen: false,
    },
  ];

  // 搜索过滤
  const filteredSections = searchValue
    ? sections.filter((s) =>
        s.keywords.toLowerCase().includes(searchValue.toLowerCase())
      )
    : sections;

  const defaultActiveKeys = sections.filter((s) => s.defaultOpen).map((s) => s.key);

  // 渲染保存状态标签
  const renderSaveStatus = (fieldName: string) => {
    if (savedFields.has(fieldName)) {
      return (
        <Tag
          icon={<CheckCircleOutlined />}
          className="save-status-tag"
          style={{
            backgroundColor: 'rgba(29, 129, 2, 0.1)',
            color: '#1d8102',
            border: '1px solid rgba(29, 129, 2, 0.2)',
            borderRadius: '4px'
          }}
        >
          已保存
        </Tag>
      );
    }
    return null;
  };

  if (isLoading) {
    return (
      <div>
        <h2>⚙️ 系统设置</h2>
        <Skeleton active paragraph={{ rows: 10 }} />
      </div>
    );
  }

  return (
    <div className="settings-page-notion">
      {/* 页面头部 */}
      <div className="settings-header">
        <h2>⚙️ 系统设置</h2>
        <Input
          size="large"
          placeholder="搜索设置..."
          prefix={<SearchOutlined />}
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
          allowClear
          style={{ width: 320, borderRadius: 8 }}
        />
      </div>

      {/* 调试信息 */}
      {process.env.NODE_ENV === 'development' && (
        <Card
          size="small"
          style={{
            marginBottom: 16,
            background: 'var(--card-bg, rgba(0, 0, 0, 0.02))',
            borderColor: 'var(--border-color, #d9d9d9)'
          }}
        >
          <small style={{ opacity: 0.65 }}>
            Settings loaded: {settings ? '✅' : '❌'} |
            Default active: {defaultActiveKeys.join(', ')} |
            Filtered sections: {filteredSections.length}
          </small>
        </Card>
      )}

      {/* 自动保存状态提示 */}
      {saving && (
        <Card size="small" className="auto-save-indicator">
          <Space>
            <CheckCircleOutlined spin style={{ color: '#0073bb' }} />
            <span>正在保存...</span>
          </Space>
        </Card>
      )}

      {/* 主表单区域 */}
      <Form
        form={form}
        layout="vertical"
        onValuesChange={debouncedSave}
        initialValues={settings}
        className="settings-form"
      >
        <Collapse
          defaultActiveKey={defaultActiveKeys}
          expandIconPosition="end"
          className="settings-collapse"
          ghost
        >
          {/* Panel 1: 网站与 SEO */}
          {filteredSections.find((s) => s.key === 'site') && (
            <Panel header="🌐 网站与 SEO" key="site" className="settings-panel">
              <p className="panel-description">配置网站基本信息和搜索引擎优化设置</p>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    label={
                      <Space>
                        <span>网站名称</span>
                        {renderSaveStatus('site_name')}
                      </Space>
                    }
                    name="site_name"
                    rules={[{ required: true }]}
                  >
                    <Input placeholder="VideoSite" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    label={
                      <Space>
                        <span>网站URL</span>
                        {renderSaveStatus('site_url')}
                      </Space>
                    }
                    name="site_url"
                    rules={[{ required: true, type: 'url' }]}
                  >
                    <Input placeholder="https://example.com" />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item label="网站描述" name="site_description">
                <TextArea rows={3} placeholder="网站简介" />
              </Form.Item>

              <Form.Item label="关键词" name="site_keywords">
                <Input placeholder="视频,在线观看,电影" />
              </Form.Item>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item label="Logo URL" name="site_logo">
                    <Input placeholder="https://example.com/logo.png" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label="Favicon URL" name="site_favicon">
                    <Input placeholder="https://example.com/favicon.ico" />
                  </Form.Item>
                </Col>
              </Row>

              <Divider orientation="left" plain>
                SEO 优化设置
              </Divider>

              <Form.Item label="SEO 标题" name="seo_title">
                <Input placeholder="覆盖默认标题" />
              </Form.Item>

              <Form.Item label="SEO 描述" name="seo_description">
                <TextArea rows={2} placeholder="搜索引擎描述" />
              </Form.Item>

              <Form.Item label="SEO 关键词" name="seo_keywords">
                <Input placeholder="关键词1,关键词2,关键词3" />
              </Form.Item>
            </Panel>
          )}

          {/* Panel 2: 视频与上传 */}
          {filteredSections.find((s) => s.key === 'video') && (
            <Panel header="📹 视频与上传" key="video" className="settings-panel">
              <p className="panel-description">配置视频审核、清晰度、转码和上传限制</p>

              <Form.Item
                label={
                  <Space>
                    <span>自动审核通过</span>
                    {renderSaveStatus('video_auto_approve')}
                  </Space>
                }
                name="video_auto_approve"
                valuePropName="checked"
                tooltip="开启后新上传的视频自动通过审核"
              >
                <Switch />
              </Form.Item>

              <Form.Item
                label="需要人工审核"
                name="video_require_review"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item label="默认清晰度" name="video_default_quality">
                    <Select>
                      <Option value="360p">360p</Option>
                      <Option value="480p">480p</Option>
                      <Option value="720p">720p</Option>
                      <Option value="1080p">1080p</Option>
                      <Option value="4k">4K</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    label="启用转码"
                    name="video_enable_transcode"
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item label="转码格式" name="video_transcode_formats">
                <Select mode="multiple" placeholder="选择需要转码的格式">
                  <Option value="360p">360p</Option>
                  <Option value="480p">480p</Option>
                  <Option value="720p">720p</Option>
                  <Option value="1080p">1080p</Option>
                  <Option value="4k">4K</Option>
                </Select>
              </Form.Item>

              <Divider orientation="left" plain>
                上传限制设置
              </Divider>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item label="视频最大大小 (MB)" name="upload_max_size">
                    <InputNumber min={1} max={10240} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label="图片最大大小 (MB)" name="image_max_size">
                    <InputNumber min={1} max={100} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item label="允许的视频格式" name="upload_allowed_formats">
                <Select mode="tags" placeholder="输入格式后按回车">
                  <Option value="mp4">mp4</Option>
                  <Option value="avi">avi</Option>
                  <Option value="mkv">mkv</Option>
                  <Option value="webm">webm</Option>
                  <Option value="flv">flv</Option>
                </Select>
              </Form.Item>

              <Form.Item label="允许的图片格式" name="image_allowed_formats">
                <Select mode="tags" placeholder="输入格式后按回车">
                  <Option value="jpg">jpg</Option>
                  <Option value="jpeg">jpeg</Option>
                  <Option value="png">png</Option>
                  <Option value="webp">webp</Option>
                  <Option value="gif">gif</Option>
                </Select>
              </Form.Item>
            </Panel>
          )}

          {/* Panel 3: 用户与社区 */}
          {filteredSections.find((s) => s.key === 'community') && (
            <Panel header="💬 用户与社区" key="community" className="settings-panel">
              <p className="panel-description">配置用户注册、验证和评论功能</p>

              <Form.Item
                label={
                  <Space>
                    <span>允许用户注册</span>
                    {renderSaveStatus('user_enable_registration')}
                  </Space>
                }
                name="user_enable_registration"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>

              <Form.Item
                label="需要邮箱验证"
                name="user_require_email_verification"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>

              <Form.Item label="默认头像 URL" name="user_default_avatar">
                <Input placeholder="https://example.com/avatar.png" />
              </Form.Item>

              <Form.Item label="最大收藏数" name="user_max_favorites">
                <InputNumber min={100} max={10000} style={{ width: '100%' }} />
              </Form.Item>

              <Divider orientation="left" plain>
                评论设置
              </Divider>

              <Form.Item label="启用评论功能" name="comment_enable" valuePropName="checked">
                <Switch />
              </Form.Item>

              <Form.Item
                label="评论需要审核"
                name="comment_require_approval"
                valuePropName="checked"
                tooltip="开启后评论需要管理员审核才能显示"
              >
                <Switch />
              </Form.Item>

              <Form.Item
                label="允许游客评论"
                name="comment_allow_guest"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>

              <Form.Item label="评论最大长度" name="comment_max_length">
                <InputNumber
                  min={50}
                  max={5000}
                  style={{ width: '100%' }}
                  addonAfter="字符"
                />
              </Form.Item>
            </Panel>
          )}

          {/* Panel 4: 邮件服务 */}
          {filteredSections.find((s) => s.key === 'email') && (
            <Panel header="📧 邮件服务" key="email" className="settings-panel">
              <p className="panel-description">配置 SMTP 或 Mailgun 邮件服务</p>

              <Card
                size="small"
                className="info-card"
                style={{
                  marginBottom: 16,
                }}
              >
                <Space>
                  <MailOutlined className="info-icon" />
                  <span>
                    详细的邮件服务器配置（SMTP、Mailgun、邮件模板）请访问独立的邮件配置页面
                  </span>
                </Space>
              </Card>

              <Form.Item label="发件人邮箱" name="from_email">
                <Input placeholder="noreply@example.com" />
              </Form.Item>

              <Form.Item label="发件人名称" name="from_name">
                <Input placeholder="VideoSite" />
              </Form.Item>
            </Panel>
          )}

          {/* Panel 5: 安全配置 */}
          {filteredSections.find((s) => s.key === 'security') && (
            <Panel header="🔒 安全配置" key="security" className="settings-panel">
              <p className="panel-description">配置登录安全、验证码、会话超时等</p>

              <Form.Item
                label={
                  <Space>
                    <span>启用验证码</span>
                    {renderSaveStatus('security_enable_captcha')}
                  </Space>
                }
                name="security_enable_captcha"
                valuePropName="checked"
                tooltip="开启后登录时需要输入验证码"
              >
                <Switch />
              </Form.Item>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item label="登录最大尝试次数" name="security_login_max_attempts">
                    <InputNumber min={3} max={10} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    label="锁定时长 (分钟)"
                    name="security_login_lockout_duration"
                  >
                    <InputNumber min={5} max={120} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item label="会话超时 (秒)" name="security_session_timeout">
                <InputNumber
                  min={1800}
                  max={86400}
                  style={{ width: '100%' }}
                  addonAfter="秒"
                />
              </Form.Item>
            </Panel>
          )}

          {/* Panel 6: 其他设置 */}
          {filteredSections.find((s) => s.key === 'other') && (
            <Panel header="⚙️ 其他设置" key="other" className="settings-panel">
              <p className="panel-description">维护模式、统计代码、自定义样式等</p>

              <Form.Item
                label={
                  <Space>
                    <span>维护模式</span>
                    {renderSaveStatus('maintenance_mode')}
                  </Space>
                }
                name="maintenance_mode"
                valuePropName="checked"
                tooltip="开启后前台将显示维护页面"
              >
                <Switch />
              </Form.Item>

              <Form.Item label="维护提示信息" name="maintenance_message">
                <TextArea rows={2} placeholder="网站正在维护中，请稍后访问" />
              </Form.Item>

              <Divider orientation="left" plain>
                高级配置
              </Divider>

              <Form.Item label="统计代码 (Google Analytics 等)" name="analytics_code">
                <TextArea
                  rows={3}
                  placeholder="<!-- Google Analytics -->"
                  className="code-textarea"
                />
              </Form.Item>

              <Form.Item label="自定义 CSS" name="custom_css">
                <TextArea
                  rows={4}
                  placeholder=".custom { color: red; }"
                  className="code-textarea"
                />
              </Form.Item>

              <Form.Item label="自定义 JavaScript" name="custom_js">
                <TextArea
                  rows={4}
                  placeholder="console.log('custom');"
                  className="code-textarea"
                />
              </Form.Item>
            </Panel>
          )}
        </Collapse>
      </Form>

      {/* 底部保存栏 (Sticky) */}
      <div className="settings-footer">
        <Space>
          <Button
            type="primary"
            size="large"
            icon={<SaveOutlined />}
            onClick={handleSaveAll}
            loading={saving}
          >
            保存所有设置
          </Button>
          <Button size="large" danger icon={<ReloadOutlined />} onClick={handleReset}>
            重置为默认值
          </Button>
        </Space>
        <div className="auto-save-hint">
          💡 提示：修改后会自动保存，也可以点击按钮手动保存所有设置
        </div>
      </div>
    </div>
  );
};

export default Settings;
