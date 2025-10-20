/**
 * Settings Page - Notion Style
 * Collapse Accordion + Auto-save + 0-click Editing
 * 参考: Notion、Vercel、Linear 的设置页面设计
 */

import { useState, useCallback, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
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
  Modal,
  Upload,
  Statistic,
  Typography,
} from 'antd';
import {
  SearchOutlined,
  CheckCircleOutlined,
  SaveOutlined,
  ReloadOutlined,
  MailOutlined,
  DownloadOutlined,
  UploadOutlined,
  ClearOutlined,
  DatabaseOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { debounce } from 'lodash';
import axios from '@/utils/axios';
import NotificationSettings from '@/components/NotificationSettings';
import PaymentGatewaySettings from '@/components/PaymentGatewaySettings';
import './SettingsNotion.css';

const { Panel } = Collapse;
const { TextArea } = Input;
const { Option } = Select;
const { Text } = Typography;

const Settings = () => {
  const { t } = useTranslation();
  const [form] = Form.useForm();
  const [searchValue, setSearchValue] = useState('');
  const [savedFields, setSavedFields] = useState<Set<string>>(new Set());
  const [saving, setSaving] = useState(false);
  const queryClient = useQueryClient();

  // 新增状态：邮件测试
  const [emailTestModalVisible, setEmailTestModalVisible] = useState(false);
  const [emailTestLoading, setEmailTestLoading] = useState(false);

  // 新增状态：缓存管理
  const [cacheStatsModalVisible, setCacheStatsModalVisible] = useState(false);
  const [cacheStats, setCacheStats] = useState<any>(null);

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
      message.error(error.response?.data?.detail || t('message.saveFailed'));
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
      message.success(t('message.allSettingsSaved'));
    } catch (error) {
      message.error(t('message.checkForm'));
    } finally {
      setSaving(false);
    }
  };

  // 重置为默认值
  const handleReset = () => {
    if (window.confirm(t('settings.actions.confirmReset'))) {
      form.resetFields();
      message.success(t('settings.resetSuccess'));
    }
  };

  // ===== 新增功能：邮件测试 =====
  const handleTestEmail = async (email: string) => {
    try {
      setEmailTestLoading(true);
      await axios.post('/api/v1/admin/system/settings/test-email', {
        to_email: email
      });
      message.success(t('settings.email.testSuccess'));
      setEmailTestModalVisible(false);
      // 刷新设置以显示最后测试状态
      queryClient.invalidateQueries({ queryKey: ['system-settings'] });
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('settings.email.testFailed'));
    } finally {
      setEmailTestLoading(false);
    }
  };

  // ===== 新增功能：缓存统计 =====
  const fetchCacheStats = async () => {
    try {
      const response = await axios.get('/api/v1/admin/system/cache/stats');
      setCacheStats(response.data);
      setCacheStatsModalVisible(true);
    } catch (error: any) {
      message.error(t('settings.cache.statsFailed'));
    }
  };

  // ===== 新增功能：清除缓存 =====
  const handleClearCache = async (patterns: string[]) => {
    try {
      const response = await axios.post('/api/v1/admin/system/cache/clear', {
        patterns
      });
      if (response.data.cleared_keys === -1) {
        message.success(t('settings.cache.allCleared'));
      } else {
        message.success(t('settings.cache.clearedCount', { count: response.data.cleared_keys }));
      }
    } catch (error: any) {
      message.error(t('settings.cache.clearFailed'));
    }
  };

  // ===== 新增功能：导出备份 =====
  const handleExportBackup = async () => {
    try {
      const response = await axios.get('/api/v1/admin/system/settings/backup');
      const dataStr = JSON.stringify(response.data.backup_data, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `settings-backup-${new Date().toISOString().split('T')[0]}.json`;
      link.click();
      URL.revokeObjectURL(url);
      message.success(t('settings.backup.downloaded'));
    } catch (error: any) {
      message.error(t('settings.backup.exportFailed'));
    }
  };

  // ===== 新增功能：恢复备份 =====
  const handleRestoreBackup = async (file: File) => {
    try {
      const text = await file.text();
      const backup_data = JSON.parse(text);

      Modal.confirm({
        title: t('settings.backup.confirmRestoreTitle'),
        content: t('settings.backup.confirmRestoreContent'),
        onOk: async () => {
          try {
            await axios.post('/api/v1/admin/system/settings/restore', {
              backup_data
            });
            message.success(t('settings.backup.restoreSuccess'));
            queryClient.invalidateQueries({ queryKey: ['system-settings'] });
          } catch (error: any) {
            message.error(t('settings.backup.restoreFailed'));
          }
        }
      });
    } catch (error: any) {
      message.error(t('settings.backup.invalidFormat'));
    }
    return false; // 阻止自动上传
  };

  // 设置分组配置
  const sections = [
    {
      key: 'site',
      title: t('settings.sections.siteAndSeo'),
      keywords: '网站 site seo 搜索 优化',
      defaultOpen: true,
    },
    {
      key: 'video',
      title: t('settings.sections.videoAndUpload'),
      keywords: '视频 上传 video upload',
      defaultOpen: true,
    },
    {
      key: 'community',
      title: t('settings.sections.userAndCommunity'),
      keywords: '用户 评论 user comment community',
      defaultOpen: false,
    },
    {
      key: 'email',
      title: t('settings.sections.emailService'),
      keywords: '邮件 email smtp mailgun',
      defaultOpen: false,
    },
    {
      key: 'security',
      title: t('settings.sections.security'),
      keywords: '安全 security 验证码 captcha',
      defaultOpen: false,
    },
    {
      key: 'notifications',
      title: t('settings.sections.notifications'),
      keywords: '通知 notifications 声音 桌面 免打扰 sound desktop',
      defaultOpen: false,
    },
    {
      key: 'cache',
      title: t('settings.sections.cacheManagement'),
      keywords: '缓存 cache redis 清除 统计',
      defaultOpen: false,
    },
    {
      key: 'backup',
      title: t('settings.sections.backupAndRestore'),
      keywords: '备份 恢复 导出 导入 backup restore',
      defaultOpen: false,
    },
    {
      key: 'payment',
      title: t('settings.sections.paymentGateway'),
      keywords: '支付 payment stripe paypal alipay 网关 gateway',
      defaultOpen: false,
    },
    {
      key: 'other',
      title: t('settings.sections.otherSettings'),
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
          {t('common.saved')}
        </Tag>
      );
    }
    return null;
  };

  if (isLoading) {
    return (
      <div>
        <h2>{t('settings.title')}</h2>
        <Skeleton active paragraph={{ rows: 10 }} />
      </div>
    );
  }

  return (
    <div className="settings-page-notion">
      {/* 页面头部 */}
      <div className="settings-header">
        <h2>{t('settings.title')}</h2>
        <Input
          size="large"
          placeholder={t('settings.searchPlaceholder')}
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
            <span>{t('common.saving')}</span>
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
            <Panel header={t('settings.sections.siteAndSeo')} key="site" className="settings-panel">
              <p className="panel-description">{t('settings.descriptions.siteAndSeo')}</p>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    label={
                      <Space>
                        <span>{t('settings.fields.siteName')}</span>
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
                        <span>{t('settings.fields.siteUrl')}</span>
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

              <Form.Item label={t('settings.fields.siteDescription')} name="site_description">
                <TextArea rows={3} placeholder={t('settings.placeholders.siteIntro')} />
              </Form.Item>

              <Form.Item label={t('settings.labels.keywords')} name="site_keywords">
                <Input placeholder={t('settings.placeholders.keywordsExample')} />
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

              <Form.Item label={t('settings.labels.seoTitle')} name="seo_title">
                <Input placeholder={t('settings.placeholders.overrideDefaultTitle')} />
              </Form.Item>

              <Form.Item label={t('settings.labels.seoDescription')} name="seo_description">
                <TextArea rows={2} placeholder={t('settings.placeholders.seDescription')} />
              </Form.Item>

              <Form.Item label={t('settings.labels.seoKeywords')} name="seo_keywords">
                <Input placeholder={t('settings.placeholders.keywordsComma')} />
              </Form.Item>
            </Panel>
          )}

          {/* Panel 2: 视频与上传 */}
          {filteredSections.find((s) => s.key === 'video') && (
            <Panel header={t('settings.sections.videoAndUpload')} key="video" className="settings-panel">
              <p className="panel-description">{t('settings.descriptions.videoAndUpload')}</p>

              <Form.Item
                label={
                  <Space>
                    <span>{t('settings.labels.autoApprove')}</span>
                    {renderSaveStatus('video_auto_approve')}
                  </Space>
                }
                name="video_auto_approve"
                valuePropName="checked"
                tooltip={t('settings.tooltips.autoApproveUploads')}
              >
                <Switch />
              </Form.Item>

              <Form.Item
                label={t('settings.labels.requireManualReview')}
                name="video_require_review"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item label={t('settings.labels.defaultQuality')} name="video_default_quality">
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
                    label={t('settings.labels.enableTranscoding')}
                    name="video_enable_transcode"
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item label={t('settings.labels.transcodeFormats')} name="video_transcode_formats">
                <Select mode="multiple" placeholder={t('settings.placeholders.selectTranscodeFormats')}>
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
                  <Form.Item label={t('settings.labels.maxVideoSize')} name="upload_max_size">
                    <InputNumber min={1} max={10240} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label={t('settings.labels.maxImageSize')} name="image_max_size">
                    <InputNumber min={1} max={100} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item label={t('settings.labels.allowedVideoFormats')} name="upload_allowed_formats">
                <Select mode="tags" placeholder={t('settings.placeholders.enterFormatAndEnter')}>
                  <Option value="mp4">mp4</Option>
                  <Option value="avi">avi</Option>
                  <Option value="mkv">mkv</Option>
                  <Option value="webm">webm</Option>
                  <Option value="flv">flv</Option>
                </Select>
              </Form.Item>

              <Form.Item label={t('settings.labels.allowedImageFormats')} name="image_allowed_formats">
                <Select mode="tags" placeholder={t('settings.placeholders.enterFormatAndEnter')}>
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
            <Panel header={t('settings.sections.userAndCommunity')} key="community" className="settings-panel">
              <p className="panel-description">{t('settings.descriptions.userAndCommunity')}</p>

              <Form.Item
                label={
                  <Space>
                    <span>{t('settings.labels.allowRegistration')}</span>
                    {renderSaveStatus('user_enable_registration')}
                  </Space>
                }
                name="user_enable_registration"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>

              <Form.Item
                label={t('settings.labels.requireEmailVerification')}
                name="user_require_email_verification"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>

              <Form.Item label={t('settings.labels.defaultAvatarUrl')} name="user_default_avatar">
                <Input placeholder="https://example.com/avatar.png" />
              </Form.Item>

              <Form.Item label={t('settings.labels.maxFavorites')} name="user_max_favorites">
                <InputNumber min={100} max={10000} style={{ width: '100%' }} />
              </Form.Item>

              <Divider orientation="left" plain>
                评论设置
              </Divider>

              <Form.Item label={t('settings.labels.enableComments')} name="comment_enable" valuePropName="checked">
                <Switch />
              </Form.Item>

              <Form.Item
                label={t('settings.labels.commentsRequireReview')}
                name="comment_require_approval"
                valuePropName="checked"
                tooltip={t('settings.tooltips.commentsModeration')}
              >
                <Switch />
              </Form.Item>

              <Form.Item
                label={t('settings.labels.allowGuestComments')}
                name="comment_allow_guest"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>

              <Form.Item label={t('settings.labels.maxCommentLength')} name="comment_max_length">
                <InputNumber
                  min={50}
                  max={5000}
                  style={{ width: '100%' }}
                  addonAfter={t('settings.units.characters')}
                />
              </Form.Item>
            </Panel>
          )}

          {/* Panel 4: 邮件服务 */}
          {filteredSections.find((s) => s.key === 'email') && (
            <Panel header={t('settings.sections.emailService')} key="email" className="settings-panel">
              <p className="panel-description">{t('settings.descriptions.emailService')}</p>

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

              <Form.Item label={t('settings.email.senderEmail')} name="from_email">
                <Input placeholder="noreply@example.com" />
              </Form.Item>

              <Form.Item label={t('settings.email.senderName')} name="from_name">
                <Input placeholder="VideoSite" />
              </Form.Item>

              <Divider orientation="left" plain>
                测试邮件配置
              </Divider>

              <Card
                size="small"
                style={{
                  marginBottom: 16,
                  background: 'var(--card-bg, #f5f5f5)'
                }}
              >
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text type="secondary">{t('settings.descriptions.sendTestEmail')}</Text>
                  <Button
                    icon={<MailOutlined />}
                    onClick={() => setEmailTestModalVisible(true)}
                  >
                    发送测试邮件
                  </Button>
                  {settings?.smtp_last_test_at && (
                    <div style={{ marginTop: 8 }}>
                      <Text type="secondary">{t('settings.labels.lastTest')}</Text>
                      <Text>{new Date(settings.smtp_last_test_at).toLocaleString()}</Text>
                      {' '}
                      <Tag color={settings.smtp_last_test_status === 'success' ? 'success' : 'error'}>
                        {settings.smtp_last_test_status === 'success' ? '成功' : '失败'}
                      </Tag>
                    </div>
                  )}
                </Space>
              </Card>
            </Panel>
          )}

          {/* Panel 5: 安全配置 */}
          {filteredSections.find((s) => s.key === 'security') && (
            <Panel header={t('settings.sections.security')} key="security" className="settings-panel">
              <p className="panel-description">{t('settings.descriptions.security')}</p>

              <Form.Item
                label={
                  <Space>
                    <span>{t('settings.labels.enableCaptcha')}</span>
                    {renderSaveStatus('security_enable_captcha')}
                  </Space>
                }
                name="security_enable_captcha"
                valuePropName="checked"
                tooltip={t('settings.tooltips.enableCaptcha')}
              >
                <Switch />
              </Form.Item>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item label={t('settings.labels.maxLoginAttempts')} name="security_login_max_attempts">
                    <InputNumber min={3} max={10} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    label={t('settings.labels.lockoutDuration')}
                    name="security_login_lockout_duration"
                  >
                    <InputNumber min={5} max={120} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item label={t('settings.labels.sessionTimeout')} name="security_session_timeout">
                <InputNumber
                  min={1800}
                  max={86400}
                  style={{ width: '100%' }}
                  addonAfter={t('settings.units.seconds')}
                />
              </Form.Item>
            </Panel>
          )}

          {/* Panel 6: 通知设置 */}
          {filteredSections.find((s) => s.key === 'notifications') && (
            <Panel header={t('settings.sections.notifications')} key="notifications" className="settings-panel">
              <p className="panel-description">{t('settings.descriptions.notifications')}</p>

              <NotificationSettings />
            </Panel>
          )}

          {/* Panel 7: 缓存管理 */}
          {filteredSections.find((s) => s.key === 'cache') && (
            <Panel header={t('settings.sections.cacheManagement')} key="cache" className="settings-panel">
              <p className="panel-description">{t('settings.descriptions.cacheManagement')}</p>

              <Card size="small" style={{ marginBottom: 16 }}>
                <Space direction="vertical" style={{ width: '100%' }} size="middle">
                  <div>
                    <Button
                      icon={<DatabaseOutlined />}
                      onClick={fetchCacheStats}
                      style={{ marginRight: 8 }}
                    >
                      查看缓存统计
                    </Button>
                    <Text type="secondary">{t('settings.descriptions.viewCacheStats')}</Text>
                  </div>

                  <Divider style={{ margin: '8px 0' }} />

                  <div>
                    <Text strong>{t('settings.actions.clearCache')}</Text>
                    <div style={{ marginTop: 8 }}>
                      <Space wrap>
                        <Button
                          danger
                          icon={<ClearOutlined />}
                          onClick={() => {
                            Modal.confirm({
                              title: '确认清除所有缓存？',
                              content: '此操作将清除Redis中的所有缓存数据',
                              onOk: () => handleClearCache(['all'])
                            });
                          }}
                        >
                          清除所有缓存
                        </Button>
                        <Button onClick={() => handleClearCache(['videos:*'])}>
                          清除视频缓存
                        </Button>
                        <Button onClick={() => handleClearCache(['categories:*'])}>
                          清除分类缓存
                        </Button>
                        <Button onClick={() => handleClearCache(['users:*'])}>
                          清除用户缓存
                        </Button>
                        <Button onClick={() => handleClearCache(['system_settings'])}>
                          清除设置缓存
                        </Button>
                      </Space>
                    </div>
                  </div>
                </Space>
              </Card>
            </Panel>
          )}

          {/* Panel 8: 备份与恢复 */}
          {filteredSections.find((s) => s.key === 'backup') && (
            <Panel header={t('settings.sections.backupAndRestore')} key="backup" className="settings-panel">
              <p className="panel-description">{t('settings.descriptions.backupAndRestore')}</p>

              <Card size="small">
                <Space direction="vertical" style={{ width: '100%' }} size="large">
                  <div>
                    <Text strong style={{ fontSize: 16 }}>{t('settings.actions.exportBackup')}</Text>
                    <div style={{ marginTop: 8 }}>
                      <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>
                        将当前所有设置导出为 JSON 文件
                      </Text>
                      <Button
                        type="primary"
                        icon={<DownloadOutlined />}
                        onClick={handleExportBackup}
                      >
                        下载备份文件
                      </Button>
                    </div>
                  </div>

                  <Divider style={{ margin: '8px 0' }} />

                  <div>
                    <Text strong style={{ fontSize: 16 }}>{t('settings.actions.importBackup')}</Text>
                    <div style={{ marginTop: 8 }}>
                      <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>
                        从备份文件恢复设置（将覆盖当前设置）
                      </Text>
                      <Upload
                        accept=".json"
                        showUploadList={false}
                        beforeUpload={handleRestoreBackup}
                      >
                        <Button icon={<UploadOutlined />}>
                          选择备份文件
                        </Button>
                      </Upload>
                    </div>
                  </div>
                </Space>
              </Card>
            </Panel>
          )}

          {/* Panel 9: 支付网关配置 */}
          {filteredSections.find((s) => s.key === 'payment') && (
            <Panel header={t('settings.sections.paymentGateway')} key="payment" className="settings-panel">
              <p className="panel-description">{t('settings.descriptions.paymentGateway')}</p>

              <Form.Item name="payment_gateway_config" noStyle>
                <PaymentGatewaySettings />
              </Form.Item>
            </Panel>
          )}

          {/* Panel 10: 其他设置 */}
          {filteredSections.find((s) => s.key === 'other') && (
            <Panel header={t('settings.sections.otherSettings')} key="other" className="settings-panel">
              <p className="panel-description">{t('settings.descriptions.otherSettings')}</p>

              <Form.Item
                label={
                  <Space>
                    <span>{t('settings.labels.maintenanceMode')}</span>
                    {renderSaveStatus('maintenance_mode')}
                  </Space>
                }
                name="maintenance_mode"
                valuePropName="checked"
                tooltip={t('settings.tooltips.maintenanceMode')}
              >
                <Switch />
              </Form.Item>

              <Form.Item label={t('settings.labels.maintenanceMessage')} name="maintenance_message">
                <TextArea rows={2} placeholder={t('settings.placeholders.maintenanceMessage')} />
              </Form.Item>

              <Divider orientation="left" plain>
                高级配置
              </Divider>

              <Form.Item label={t('settings.labels.analyticsCode')} name="analytics_code">
                <TextArea
                  rows={3}
                  placeholder="<!-- Google Analytics -->"
                  className="code-textarea"
                />
              </Form.Item>

              <Form.Item label={t('settings.labels.customCss')} name="custom_css">
                <TextArea
                  rows={4}
                  placeholder=".custom { color: red; }"
                  className="code-textarea"
                />
              </Form.Item>

              <Form.Item label={t('settings.labels.customJs')} name="custom_js">
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

      {/* 邮件测试模态框 */}
      <Modal
        title={t('settings.actions.sendTestEmail')}
        open={emailTestModalVisible}
        onCancel={() => setEmailTestModalVisible(false)}
        footer={null}
      >
        <Form onFinish={(values) => handleTestEmail(values.email)}>
          <Form.Item
            name="email"
            label={t('settings.email.address')}
            rules={[
              { required: true, message: '请输入邮箱地址' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input placeholder={t('settings.email.enterTestAddress')} />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={emailTestLoading}>
                发送测试
              </Button>
              <Button onClick={() => setEmailTestModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 缓存统计模态框 */}
      <Modal
        title={t('settings.cache.stats')}
        open={cacheStatsModalVisible}
        onCancel={() => setCacheStatsModalVisible(false)}
        footer={null}
        width={800}
      >
        {cacheStats && (
          <>
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={8}>
                <Statistic
                  title={t('settings.labels.totalHits')}
                  value={cacheStats.summary.total_hits}
                  valueStyle={{ color: '#3f8600' }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title={t('settings.labels.totalMisses')}
                  value={cacheStats.summary.total_misses}
                  valueStyle={{ color: '#cf1322' }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title={t('settings.labels.avgHitRate')}
                  value={cacheStats.summary.average_hit_rate}
                  suffix="%"
                  valueStyle={{ color: '#1890ff' }}
                  precision={2}
                />
              </Col>
            </Row>
            <Divider />
            <Text strong>{t('settings.cache.last7Days')}</Text>
            <div style={{ marginTop: 16 }}>
              {cacheStats.stats.map((stat: any) => (
                <div key={stat.date} style={{ marginBottom: 8 }}>
                  <Text>{stat.date}: </Text>
                  <Tag color="green">{stat.hits} {t('settings.labels.hits')}</Tag>
                  <Tag color="red">{stat.misses} {t('settings.labels.misses')}</Tag>
                  <Tag color="blue">{stat.hit_rate}% {t('settings.labels.hitRate')}</Tag>
                </div>
              ))}
            </div>
          </>
        )}
      </Modal>
    </div>
  );
};

export default Settings;
