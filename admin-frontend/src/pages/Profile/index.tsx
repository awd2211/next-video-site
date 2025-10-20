/**
 * 管理员个人资料页面
 */
import { useState, useEffect } from 'react'
import { Card, Form, Input, Button, Avatar, message, Tabs, Space, Typography, Descriptions, Alert, Switch, Modal, Select } from 'antd'
import { UserOutlined, LockOutlined, MailOutlined, SaveOutlined, SafetyOutlined, CopyOutlined, SettingOutlined, GlobalOutlined, BgColorsOutlined } from '@ant-design/icons'
import profileService, { type AdminProfile, type UpdateProfileRequest } from '../../services/profileService'
import { get2FAStatus, disable2FA, regenerateBackupCodes, type TwoFactorStatus } from '../../services/twoFactorService'
import TwoFactorSetup from '../../components/TwoFactorSetup'
import { useLanguage } from '../../contexts/LanguageContext'
import { useTheme } from '../../contexts/ThemeContext'
import { useTranslation } from 'react-i18next'

const { Title, Text } = Typography
const { TabPane } = Tabs

export default function Profile() {
  const { t } = useTranslation()
  const [profileForm] = Form.useForm()
  const [passwordForm] = Form.useForm()
  const [emailForm] = Form.useForm()
  const [preferencesForm] = Form.useForm()

  const [profile, setProfile] = useState<AdminProfile | null>(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('info')

  // Context hooks for language and theme
  const { setLanguage } = useLanguage()
  const { setTheme } = useTheme()

  // 2FA state
  const [twoFactorStatus, setTwoFactorStatus] = useState<TwoFactorStatus | null>(null)
  const [showSetupModal, setShowSetupModal] = useState(false)
  const [disablePasswordModal, setDisablePasswordModal] = useState(false)
  const [disablePassword, setDisablePassword] = useState('')

  // 加载管理员资料
  const loadProfile = async () => {
    try {
      setLoading(true)
      const data = await profileService.getProfile()
      setProfile(data)
      // 设置表单初始值
      profileForm.setFieldsValue({
        full_name: data.full_name,
        avatar: data.avatar,
      })
      preferencesForm.setFieldsValue({
        timezone: data.timezone || 'UTC',
        preferred_language: data.preferred_language || 'en-US',
        preferred_theme: data.preferred_theme || 'light',
      })
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('profile.message.loadProfileFailed'))
    } finally {
      setLoading(false)
    }
  }

  // Load 2FA status
  const load2FAStatus = async () => {
    try {
      const status = await get2FAStatus()
      setTwoFactorStatus(status)
    } catch (error: any) {
      console.error('Failed to load 2FA status:', error)
    }
  }

  useEffect(() => {
    loadProfile()
    load2FAStatus()
  }, [])

  // Handle enable 2FA
  const handleEnable2FA = () => {
    setShowSetupModal(true)
  }

  // Handle disable 2FA
  const handleDisable2FA = async () => {
    if (!disablePassword) {
      message.error(t('profile.message.enterPassword'))
      return
    }

    try {
      setLoading(true)
      await disable2FA(disablePassword)
      message.success(t('profile.twoFactor.disableSuccess'))
      setDisablePasswordModal(false)
      setDisablePassword('')
      await load2FAStatus()
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('profile.twoFactor.disableFailed'))
    } finally {
      setLoading(false)
    }
  }

  // Handle regenerate backup codes
  const handleRegenerateBackupCodes = () => {
    Modal.confirm({
      title: t('profile.twoFactor.regenerateTitle'),
      content: (
        <div>
          <p>{t('profile.twoFactor.regenerateContent')}</p>
          <p>{t('profile.twoFactor.regeneratePrompt')}</p>
          <Input.Password
            placeholder={t('profile.twoFactor.regeneratePasswordPlaceholder')}
            onChange={(e) => setDisablePassword(e.target.value)}
          />
        </div>
      ),
      onOk: async () => {
        if (!disablePassword) {
          message.error(t('profile.twoFactor.regeneratePasswordRequired'))
          return Promise.reject()
        }

        try {
          const response = await regenerateBackupCodes(disablePassword)
          Modal.info({
            title: t('profile.twoFactor.newBackupCodesTitle'),
            width: 600,
            content: (
              <div>
                <Alert
                  message={t('profile.twoFactor.newBackupCodesAlert')}
                  description={t('profile.twoFactor.newBackupCodesDescription')}
                  type="warning"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
                <div
                  style={{
                    background: '#f5f5f5',
                    padding: '16px',
                    borderRadius: '4px',
                    fontFamily: 'monospace',
                    fontSize: '14px',
                  }}
                >
                  {response.backup_codes.map((code, index) => (
                    <div key={index} style={{ padding: '4px 0' }}>
                      {code}
                    </div>
                  ))}
                </div>
                <Button
                  icon={<CopyOutlined />}
                  onClick={() => {
                    navigator.clipboard.writeText(response.backup_codes.join('\n'))
                    message.success(t('profile.twoFactor.backupCodesCopied'))
                  }}
                  style={{ marginTop: 16 }}
                >
                  {t('profile.twoFactor.copyAllBackupCodes')}
                </Button>
              </div>
            ),
          })
          setDisablePassword('')
          await load2FAStatus()
        } catch (error: any) {
          message.error(error.response?.data?.detail || t('profile.twoFactor.regenerateFailed'))
          return Promise.reject()
        }
      },
    })
  }

  // 更新个人资料
  const handleUpdateProfile = async (values: UpdateProfileRequest) => {
    try {
      setLoading(true)
      const updated = await profileService.updateProfile(values)
      setProfile(updated)
      message.success(t('profile.message.profileUpdateSuccess'))
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('profile.message.profileUpdateFailed'))
    } finally {
      setLoading(false)
    }
  }

  // 修改密码
  const handleChangePassword = async (values: any) => {
    try {
      setLoading(true)
      await profileService.changePassword({
        old_password: values.old_password,
        new_password: values.new_password,
      })
      message.success(t('profile.message.passwordChangeSuccess'))
      passwordForm.resetFields()
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('profile.message.passwordChangeFailed'))
    } finally {
      setLoading(false)
    }
  }

  // 修改邮箱
  const handleChangeEmail = async (values: any) => {
    try {
      setLoading(true)
      const updated = await profileService.changeEmail({
        new_email: values.new_email,
        password: values.password,
      })
      setProfile(updated)
      message.success(t('profile.message.emailChangeSuccess'))
      emailForm.resetFields()
      setActiveTab('info')
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('profile.message.emailChangeFailed'))
    } finally {
      setLoading(false)
    }
  }

  // 更新用户偏好设置
  const handleUpdatePreferences = async (values: any) => {
    try {
      setLoading(true)
      const updated = await profileService.updatePreferences(values)
      setProfile(updated)

      // Sync language and theme changes to context (which updates localStorage)
      let needsReload = false

      if (values.preferred_language && values.preferred_language !== profile?.preferred_language) {
        setLanguage(values.preferred_language as 'zh-CN' | 'en-US')
        needsReload = true
      }

      if (values.preferred_theme && values.preferred_theme !== profile?.preferred_theme) {
        setTheme(values.preferred_theme as 'light' | 'dark')
        needsReload = true
      }

      message.success(t('profile.message.preferencesUpdateSuccess'))

      // Reload page to apply all changes
      if (needsReload) {
        message.info(t('profile.message.languageOrThemeChanged'), 2)
        setTimeout(() => {
          window.location.reload()
        }, 2000)
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('profile.message.preferencesUpdateFailed'))
    } finally {
      setLoading(false)
    }
  }

  if (!profile) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Text>{t('profile.loading')}</Text>
      </div>
    )
  }

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>{t('profile.title')}</Title>

      <Card style={{ marginTop: '24px' }}>
        {/* 头部信息卡片 */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '24px',
          padding: '24px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '8px',
          marginBottom: '24px'
        }}>
          <Avatar
            size={80}
            src={profile.avatar}
            icon={<UserOutlined />}
            style={{ border: '3px solid white' }}
          />
          <div style={{ color: 'white' }}>
            <Title level={3} style={{ color: 'white', marginBottom: '8px' }}>
              {profile.full_name || profile.username}
            </Title>
            <Space direction="vertical" size="small">
              <Text style={{ color: 'rgba(255,255,255,0.9)' }}>
                <MailOutlined /> {profile.email}
              </Text>
              <Text style={{ color: 'rgba(255,255,255,0.9)' }}>
                {profile.is_superadmin ? t('profile.role.superadmin') : t('profile.role.editor')}
              </Text>
            </Space>
          </div>
        </div>

        {/* 标签页 */}
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          {/* 基本信息标签 */}
          <TabPane tab={t('profile.tabs.basicInfo')} key="info">
            <Descriptions bordered column={2} style={{ marginBottom: '24px' }}>
              <Descriptions.Item label={t('profile.form.username')}>{profile.username}</Descriptions.Item>
              <Descriptions.Item label={t('profile.form.email')}>{profile.email}</Descriptions.Item>
              <Descriptions.Item label={t('profile.form.role')}>
                {profile.is_superadmin ? t('profile.role.superadmin') : t('profile.role.editor')}
              </Descriptions.Item>
              <Descriptions.Item label={t('profile.form.createdAt')}>
                {new Date(profile.created_at).toLocaleString('zh-CN')}
              </Descriptions.Item>
              <Descriptions.Item label={t('profile.form.lastLogin')}>
                {profile.last_login_at
                  ? new Date(profile.last_login_at).toLocaleString('zh-CN')
                  : t('profile.form.notRecorded')}
              </Descriptions.Item>
            </Descriptions>

            <Title level={4}>{t('profile.form.editProfile')}</Title>
            <Form
              form={profileForm}
              layout="vertical"
              onFinish={handleUpdateProfile}
              style={{ maxWidth: '600px' }}
            >
              <Form.Item
                label={t('profile.form.fullName')}
                name="full_name"
                rules={[{ max: 200, message: t('profile.validation.fullNameMaxLength') }]}
              >
                <Input placeholder={t('profile.placeholder.enterFullName')} prefix={<UserOutlined />} />
              </Form.Item>

              <Form.Item
                label={t('profile.form.avatarUrl')}
                name="avatar"
                rules={[
                  { max: 500, message: t('profile.validation.avatarUrlMaxLength') },
                  { type: 'url', message: t('profile.validation.validUrl') }
                ]}
              >
                <Input placeholder={t('profile.placeholder.enterAvatarUrl')} />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  icon={<SaveOutlined />}
                  style={{ background: '#0073bb' }}
                >
                  {t('profile.button.saveChanges')}
                </Button>
              </Form.Item>
            </Form>
          </TabPane>

          {/* 修改密码标签 */}
          <TabPane tab={t('profile.tabs.changePassword')} key="password">
            <Form
              form={passwordForm}
              layout="vertical"
              onFinish={handleChangePassword}
              style={{ maxWidth: '600px' }}
            >
              <Form.Item
                label={t('profile.form.currentPassword')}
                name="old_password"
                rules={[
                  { required: true, message: t('profile.validation.currentPasswordRequired') },
                  { min: 6, message: t('profile.validation.passwordMinLength') }
                ]}
              >
                <Input.Password
                  placeholder={t('profile.placeholder.enterCurrentPassword')}
                  prefix={<LockOutlined />}
                />
              </Form.Item>

              <Form.Item
                label={t('profile.form.newPassword')}
                name="new_password"
                rules={[
                  { required: true, message: t('profile.validation.newPasswordRequired') },
                  { min: 6, message: t('profile.validation.passwordMinLength') },
                  { max: 100, message: t('profile.validation.passwordMaxLength') }
                ]}
              >
                <Input.Password
                  placeholder={t('profile.placeholder.enterNewPassword')}
                  prefix={<LockOutlined />}
                />
              </Form.Item>

              <Form.Item
                label={t('profile.form.confirmPassword')}
                name="confirm_password"
                dependencies={['new_password']}
                rules={[
                  { required: true, message: t('profile.validation.confirmPasswordRequired') },
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || getFieldValue('new_password') === value) {
                        return Promise.resolve()
                      }
                      return Promise.reject(new Error(t('profile.validation.passwordMismatch')))
                    },
                  }),
                ]}
              >
                <Input.Password
                  placeholder={t('profile.placeholder.reenterNewPassword')}
                  prefix={<LockOutlined />}
                />
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={loading}
                    icon={<SaveOutlined />}
                    style={{ background: '#ff9900' }}
                  >
                    {t('profile.button.changePassword')}
                  </Button>
                  <Button onClick={() => passwordForm.resetFields()}>
                    {t('profile.button.reset')}
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </TabPane>

          {/* 修改邮箱标签 */}
          <TabPane tab={t('profile.tabs.changeEmail')} key="email">
            <Form
              form={emailForm}
              layout="vertical"
              onFinish={handleChangeEmail}
              style={{ maxWidth: '600px' }}
            >
              <Form.Item label={t('profile.form.currentEmail')}>
                <Input
                  value={profile.email}
                  disabled
                  prefix={<MailOutlined />}
                />
              </Form.Item>

              <Form.Item
                label={t('profile.form.newEmail')}
                name="new_email"
                rules={[
                  { required: true, message: t('profile.validation.newEmailRequired') },
                  { type: 'email', message: t('profile.validation.validEmail') }
                ]}
              >
                <Input
                  placeholder={t('profile.placeholder.enterNewEmail')}
                  prefix={<MailOutlined />}
                />
              </Form.Item>

              <Form.Item
                label={t('profile.form.passwordForVerification')}
                name="password"
                extra={t('profile.extra.emailVerificationRequired')}
                rules={[
                  { required: true, message: t('profile.validation.passwordRequiredForEmail') }
                ]}
              >
                <Input.Password
                  placeholder={t('profile.placeholder.enterPasswordForVerification')}
                  prefix={<LockOutlined />}
                />
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={loading}
                    icon={<SaveOutlined />}
                    style={{ background: '#1d8102' }}
                  >
                    {t('profile.button.changeEmail')}
                  </Button>
                  <Button onClick={() => emailForm.resetFields()}>
                    {t('profile.button.reset')}
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </TabPane>

          {/* 偏好设置标签 */}
          <TabPane tab={<span><SettingOutlined /> {t('profile.tabs.preferences')}</span>} key="preferences">
            <Title level={4}>{t('profile.preference.title')}</Title>
            <Alert
              message={t('profile.preference.description')}
              description={t('profile.preference.subtitle')}
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />

            <Form
              form={preferencesForm}
              layout="vertical"
              onFinish={handleUpdatePreferences}
              style={{ maxWidth: '600px' }}
            >
              <Form.Item
                label={t('profile.form.timezone')}
                name="timezone"
                extra={t('profile.preference.timezoneExtra')}
              >
                <Select
                  showSearch
                  placeholder={t('profile.placeholder.selectTimezone')}
                  optionFilterProp="children"
                  prefix={<GlobalOutlined />}
                >
                  <Select.Option value="UTC">{t('profile.timezone.utc')}</Select.Option>
                  <Select.Option value="Asia/Shanghai">{t('profile.timezone.shanghai')}</Select.Option>
                  <Select.Option value="Asia/Tokyo">{t('profile.timezone.tokyo')}</Select.Option>
                  <Select.Option value="Asia/Seoul">{t('profile.timezone.seoul')}</Select.Option>
                  <Select.Option value="Asia/Hong_Kong">{t('profile.timezone.hongKong')}</Select.Option>
                  <Select.Option value="America/New_York">{t('profile.timezone.newYork')}</Select.Option>
                  <Select.Option value="America/Los_Angeles">{t('profile.timezone.losAngeles')}</Select.Option>
                  <Select.Option value="America/Chicago">{t('profile.timezone.chicago')}</Select.Option>
                  <Select.Option value="Europe/London">{t('profile.timezone.london')}</Select.Option>
                  <Select.Option value="Europe/Paris">{t('profile.timezone.paris')}</Select.Option>
                  <Select.Option value="Europe/Berlin">{t('profile.timezone.berlin')}</Select.Option>
                  <Select.Option value="Australia/Sydney">{t('profile.timezone.sydney')}</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item
                label={t('profile.form.preferredLanguage')}
                name="preferred_language"
                extra={t('profile.preference.languageExtra')}
              >
                <Select placeholder={t('profile.placeholder.selectLanguage')}>
                  <Select.Option value="en-US">{t('profile.language.enUS')}</Select.Option>
                  <Select.Option value="zh-CN">{t('profile.language.zhCN')}</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item
                label={t('profile.form.theme')}
                name="preferred_theme"
                extra={t('profile.preference.themeExtra')}
              >
                <Select placeholder={t('profile.placeholder.selectTheme')} suffixIcon={<BgColorsOutlined />}>
                  <Select.Option value="light">{t('profile.theme.light')}</Select.Option>
                  <Select.Option value="dark">{t('profile.theme.dark')}</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={loading}
                    icon={<SaveOutlined />}
                  >
                    {t('profile.button.savePreferences')}
                  </Button>
                  <Button onClick={() => preferencesForm.resetFields()}>
                    {t('profile.button.reset')}
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </TabPane>

          {/* 安全设置标签 */}
          <TabPane tab={<span><SafetyOutlined /> {t('profile.tabs.security')}</span>} key="security">
            <Title level={4}>{t('profile.twoFactor.title')}</Title>
            <Alert
              message={t('profile.twoFactor.enhanceSecurity')}
              description={t('profile.twoFactor.description')}
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />

            {twoFactorStatus && (
              <Card style={{ maxWidth: '600px' }}>
                <Space direction="vertical" size="large" style={{ width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <Text strong>{t('profile.twoFactor.status')}</Text>
                      <Text style={{ marginLeft: 8 }}>
                        {twoFactorStatus.enabled ? (
                          <span style={{ color: '#52c41a' }}>{t('profile.twoFactor.enabled')}</span>
                        ) : (
                          <span style={{ color: '#d9d9d9' }}>{t('profile.twoFactor.disabled')}</span>
                        )}
                      </Text>
                    </div>
                    <Switch
                      checked={twoFactorStatus.enabled}
                      onChange={(checked) => {
                        if (checked) {
                          handleEnable2FA()
                        } else {
                          setDisablePasswordModal(true)
                        }
                      }}
                      checkedChildren={t('profile.twoFactor.switchEnabled')}
                      unCheckedChildren={t('profile.twoFactor.switchDisabled')}
                    />
                  </div>

                  {twoFactorStatus.enabled && (
                    <>
                      <div>
                        <Text type="secondary">{t('profile.twoFactor.enabledAt')}</Text>
                        <Text style={{ marginLeft: 8 }}>
                          {twoFactorStatus.verified_at
                            ? new Date(twoFactorStatus.verified_at).toLocaleString('zh-CN')
                            : t('profile.twoFactor.unknown')}
                        </Text>
                      </div>

                      <div>
                        <Text type="secondary">{t('profile.twoFactor.backupCodesRemaining')}</Text>
                        <Text style={{ marginLeft: 8 }}>
                          {twoFactorStatus.backup_codes_remaining}{t('profile.twoFactor.backupCodesCount')}
                        </Text>
                      </div>

                      <Button
                        onClick={handleRegenerateBackupCodes}
                        icon={<SafetyOutlined />}
                      >
                        {t('profile.twoFactor.regenerateBackupCodes')}
                      </Button>
                    </>
                  )}
                </Space>
              </Card>
            )}
          </TabPane>
        </Tabs>
      </Card>

      {/* 2FA Setup Modal */}
      <TwoFactorSetup
        visible={showSetupModal}
        onClose={() => setShowSetupModal(false)}
        onSuccess={() => {
          load2FAStatus()
          setShowSetupModal(false)
        }}
      />

      {/* Disable 2FA Modal */}
      <Modal
        title={t('profile.twoFactor.disableTitle')}
        open={disablePasswordModal}
        onOk={handleDisable2FA}
        onCancel={() => {
          setDisablePasswordModal(false)
          setDisablePassword('')
        }}
        okText={t('profile.twoFactor.disableButton')}
        cancelText={t('common.cancel')}
        okButtonProps={{ danger: true, loading }}
      >
        <Alert
          message={t('profile.twoFactor.disableWarning')}
          description={t('profile.twoFactor.disableDescription')}
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
        <Form.Item label={t('profile.twoFactor.disableConfirmLabel')}>
          <Input.Password
            placeholder={t('profile.twoFactor.disableConfirmPlaceholder')}
            value={disablePassword}
            onChange={(e) => setDisablePassword(e.target.value)}
          />
        </Form.Item>
      </Modal>
    </div>
  )
}
