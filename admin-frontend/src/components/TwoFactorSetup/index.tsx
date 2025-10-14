/**
 * Two-Factor Authentication Setup Wizard
 * Guides users through enabling 2FA
 */

import { CheckCircleOutlined, CopyOutlined, SafetyOutlined } from '@ant-design/icons'
import { Alert, Button, Input, message, Modal, Space, Steps, Typography } from 'antd'
import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'

import { setup2FA, verify2FA } from '@/services/twoFactorService'

const { Title, Text, Paragraph } = Typography

interface TwoFactorSetupProps {
  visible: boolean
  onClose: () => void
  onSuccess: () => void
}

const TwoFactorSetup: React.FC<TwoFactorSetupProps> = ({ visible, onClose, onSuccess }) => {
  const { t } = useTranslation()
  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [secret, setSecret] = useState('')
  const [qrCode, setQrCode] = useState('')
  const [backupCodes, setBackupCodes] = useState<string[]>([])
  const [verificationCode, setVerificationCode] = useState('')

  // Step 1: Initialize setup
  const handleSetup = async () => {
    setLoading(true)
    try {
      const response = await setup2FA()
      setSecret(response.secret)
      setQrCode(response.qr_code)
      setBackupCodes(response.backup_codes)
      setCurrentStep(1)
      message.success('2FA设置已初始化')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '初始化2FA失败')
    } finally {
      setLoading(false)
    }
  }

  // Step 2: Verify token
  const handleVerify = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      message.error('请输入6位验证码')
      return
    }

    setLoading(true)
    try {
      await verify2FA(verificationCode)
      setCurrentStep(2)
      message.success('2FA已成功启用！')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '验证失败，请检查验证码')
    } finally {
      setLoading(false)
    }
  }

  // Copy text to clipboard
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    message.success('已复制到剪贴板')
  }

  // Copy all backup codes
  const copyAllBackupCodes = () => {
    const codesText = backupCodes.join('\n')
    copyToClipboard(codesText)
  }

  // Handle close
  const handleClose = () => {
    if (currentStep === 2) {
      onSuccess()
    }
    setCurrentStep(0)
    setSecret('')
    setQrCode('')
    setBackupCodes([])
    setVerificationCode('')
    onClose()
  }

  const steps = [
    {
      title: '扫描二维码',
      icon: <SafetyOutlined />,
    },
    {
      title: '验证设置',
      icon: <SafetyOutlined />,
    },
    {
      title: '保存备份码',
      icon: <CheckCircleOutlined />,
    },
  ]

  return (
    <Modal
      title="启用双因素认证 (2FA)"
      open={visible}
      onCancel={handleClose}
      footer={null}
      width={600}
      destroyOnClose
    >
      <Steps current={currentStep} items={steps} style={{ marginBottom: 24 }} />

      {/* Step 0: Introduction */}
      {currentStep === 0 && (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Alert
            message="提升账户安全性"
            description="双因素认证 (2FA) 为您的账户增加额外的安全层。即使密码泄露，攻击者也无法访问您的账户。"
            type="info"
            showIcon
          />

          <div>
            <Title level={5}>需要准备：</Title>
            <ul>
              <li>手机上的身份验证器应用（Google Authenticator、Authy、Microsoft Authenticator 等）</li>
              <li>安全的地方保存备份码</li>
            </ul>
          </div>

          <Button type="primary" size="large" onClick={handleSetup} loading={loading} block>
            开始设置 2FA
          </Button>
        </Space>
      )}

      {/* Step 1: Scan QR Code */}
      {currentStep === 1 && (
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <Alert
            message="使用身份验证器应用扫描二维码"
            description="打开您的身份验证器应用，扫描下方二维码以添加此账户"
            type="info"
            showIcon
          />

          {/* QR Code */}
          <div style={{ textAlign: 'center', padding: '20px 0' }}>
            {qrCode && <img src={qrCode} alt="2FA QR Code" style={{ maxWidth: '250px' }} />}
          </div>

          {/* Manual Entry */}
          <div>
            <Text strong>或手动输入密钥：</Text>
            <Input.Group compact style={{ marginTop: 8 }}>
              <Input value={secret} readOnly style={{ width: 'calc(100% - 80px)' }} />
              <Button icon={<CopyOutlined />} onClick={() => copyToClipboard(secret)}>
                复制
              </Button>
            </Input.Group>
          </div>

          {/* Verification */}
          <div style={{ marginTop: 24 }}>
            <Text strong>输入验证码以完成设置：</Text>
            <Input
              placeholder="输入6位验证码"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
              maxLength={6}
              size="large"
              style={{ marginTop: 8, fontSize: '20px', letterSpacing: '4px', textAlign: 'center' }}
            />
          </div>

          <Button type="primary" size="large" onClick={handleVerify} loading={loading} disabled={verificationCode.length !== 6} block>
            验证并启用 2FA
          </Button>
        </Space>
      )}

      {/* Step 2: Backup Codes */}
      {currentStep === 2 && (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Alert
            message="2FA 已成功启用！"
            description="请务必保存以下备份码。如果您丢失手机或无法使用身份验证器应用，可以使用这些备份码登录。"
            type="success"
            showIcon
          />

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <Text strong>备份码（每个只能使用一次）：</Text>
              <Button icon={<CopyOutlined />} onClick={copyAllBackupCodes} size="small">
                复制全部
              </Button>
            </div>
            <div
              style={{
                background: '#f5f5f5',
                padding: '16px',
                borderRadius: '4px',
                fontFamily: 'monospace',
                fontSize: '14px',
              }}
            >
              {backupCodes.map((code, index) => (
                <div key={index} style={{ padding: '4px 0' }}>
                  {code}
                </div>
              ))}
            </div>
          </div>

          <Alert
            message="重要提示"
            description={
              <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
                <li>将这些备份码保存在安全的地方</li>
                <li>每个备份码只能使用一次</li>
                <li>您可以稍后在个人资料的安全设置中重新生成备份码</li>
              </ul>
            }
            type="warning"
            showIcon
          />

          <Button type="primary" size="large" onClick={handleClose} block>
            完成
          </Button>
        </Space>
      )}
    </Modal>
  )
}

export default TwoFactorSetup
