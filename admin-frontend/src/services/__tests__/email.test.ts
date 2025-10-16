/**
 * Email Service Tests
 * 邮件服务测试 - 邮件配置和模板管理
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from '@/utils/axios'
import { emailService } from '../email'
import type {
  EmailConfiguration,
  EmailTemplate,
  CreateEmailConfigSMTP,
  CreateEmailConfigMailgun,
  UpdateEmailConfig,
  CreateEmailTemplate,
  UpdateEmailTemplate,
} from '../email'

// Mock axios module
vi.mock('@/utils/axios')

describe('Email Service', () => {
  const mockAxios = vi.mocked(axios)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  // Mock data
  const mockSMTPConfig: EmailConfiguration = {
    id: 1,
    provider: 'smtp',
    is_active: true,
    smtp_host: 'smtp.example.com',
    smtp_port: 587,
    smtp_username: 'test@example.com',
    smtp_use_tls: true,
    smtp_use_ssl: false,
    from_email: 'noreply@example.com',
    from_name: 'VideoSite',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  }

  const mockMailgunConfig: EmailConfiguration = {
    id: 2,
    provider: 'mailgun',
    is_active: false,
    mailgun_domain: 'mg.example.com',
    mailgun_base_url: 'https://api.mailgun.net/v3',
    from_email: 'noreply@example.com',
    from_name: 'VideoSite',
    created_at: '2024-01-01T00:00:00Z',
  }

  const mockTemplate: EmailTemplate = {
    id: 1,
    name: 'Welcome Email',
    slug: 'welcome',
    subject: 'Welcome to {{site_name}}',
    html_content: '<h1>Welcome {{user_name}}</h1>',
    text_content: 'Welcome {{user_name}}',
    variables: ['site_name', 'user_name'],
    description: 'Welcome email for new users',
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  }

  describe('getConfigurations', () => {
    it('should fetch all email configurations', async () => {
      mockAxios.get.mockResolvedValue({ data: [mockSMTPConfig, mockMailgunConfig] })

      const result = await emailService.getConfigurations()

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/email/config')
      expect(result).toHaveLength(2)
      expect(result[0].provider).toBe('smtp')
      expect(result[1].provider).toBe('mailgun')
    })

    it('should handle empty configurations', async () => {
      mockAxios.get.mockResolvedValue({ data: [] })

      const result = await emailService.getConfigurations()

      expect(result).toHaveLength(0)
    })

    it('should handle API errors', async () => {
      mockAxios.get.mockRejectedValue(new Error('Network error'))

      await expect(emailService.getConfigurations()).rejects.toThrow('Network error')
    })
  })

  describe('createConfiguration', () => {
    it('should create SMTP configuration', async () => {
      const smtpData: CreateEmailConfigSMTP = {
        provider: 'smtp',
        smtp_host: 'smtp.example.com',
        smtp_port: 587,
        smtp_username: 'test@example.com',
        smtp_password: 'secret123',
        smtp_use_tls: true,
        smtp_use_ssl: false,
        from_email: 'noreply@example.com',
        from_name: 'VideoSite',
      }

      mockAxios.post.mockResolvedValue({ data: mockSMTPConfig })

      const result = await emailService.createConfiguration(smtpData)

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/email/config', smtpData)
      expect(result.provider).toBe('smtp')
      expect(result.smtp_host).toBe('smtp.example.com')
    })

    it('should create Mailgun configuration', async () => {
      const mailgunData: CreateEmailConfigMailgun = {
        provider: 'mailgun',
        mailgun_api_key: 'key-123456',
        mailgun_domain: 'mg.example.com',
        mailgun_base_url: 'https://api.mailgun.net/v3',
        from_email: 'noreply@example.com',
        from_name: 'VideoSite',
      }

      mockAxios.post.mockResolvedValue({ data: mockMailgunConfig })

      const result = await emailService.createConfiguration(mailgunData)

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/email/config', mailgunData)
      expect(result.provider).toBe('mailgun')
      expect(result.mailgun_domain).toBe('mg.example.com')
    })

    it('should handle validation errors', async () => {
      mockAxios.post.mockRejectedValue({
        response: { status: 422, data: { detail: 'Invalid SMTP configuration' } },
      })

      await expect(
        emailService.createConfiguration({
          provider: 'smtp',
          smtp_host: '',
          smtp_port: 587,
          smtp_username: '',
          smtp_password: '',
          from_email: 'invalid-email',
          from_name: '',
        })
      ).rejects.toMatchObject({
        response: { status: 422 },
      })
    })
  })

  describe('updateConfiguration', () => {
    it('should update email configuration', async () => {
      const updateData: UpdateEmailConfig = {
        is_active: false,
        smtp_host: 'smtp2.example.com',
        from_name: 'VideoSite Updated',
      }

      mockAxios.put.mockResolvedValue({
        data: { ...mockSMTPConfig, ...updateData },
      })

      const result = await emailService.updateConfiguration(1, updateData)

      expect(mockAxios.put).toHaveBeenCalledWith('/api/v1/admin/email/config/1', updateData)
      expect(result.is_active).toBe(false)
      expect(result.smtp_host).toBe('smtp2.example.com')
    })

    it('should update password', async () => {
      const updateData: UpdateEmailConfig = {
        smtp_password: 'new-password',
      }

      mockAxios.put.mockResolvedValue({ data: mockSMTPConfig })

      await emailService.updateConfiguration(1, updateData)

      expect(mockAxios.put).toHaveBeenCalledWith('/api/v1/admin/email/config/1', updateData)
    })

    it('should toggle active status', async () => {
      mockAxios.put.mockResolvedValue({
        data: { ...mockSMTPConfig, is_active: false },
      })

      const result = await emailService.updateConfiguration(1, { is_active: false })

      expect(result.is_active).toBe(false)
    })

    it('should handle 404 errors', async () => {
      mockAxios.put.mockRejectedValue({
        response: { status: 404, data: { detail: 'Configuration not found' } },
      })

      await expect(emailService.updateConfiguration(999, {})).rejects.toMatchObject({
        response: { status: 404 },
      })
    })
  })

  describe('deleteConfiguration', () => {
    it('should delete configuration', async () => {
      mockAxios.delete.mockResolvedValue({ data: { message: 'Deleted successfully' } })

      await emailService.deleteConfiguration(1)

      expect(mockAxios.delete).toHaveBeenCalledWith('/api/v1/admin/email/config/1')
    })

    it('should handle 404 errors', async () => {
      mockAxios.delete.mockRejectedValue({
        response: { status: 404 },
      })

      await expect(emailService.deleteConfiguration(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })
  })

  describe('testConfiguration', () => {
    it('should test email configuration successfully', async () => {
      mockAxios.post.mockResolvedValue({
        data: { success: true, message: 'Test email sent successfully' },
      })

      const result = await emailService.testConfiguration(1, 'test@example.com')

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/email/config/1/test', {
        test_email: 'test@example.com',
      })
      expect(result.success).toBe(true)
    })

    it('should handle test failure', async () => {
      mockAxios.post.mockResolvedValue({
        data: { success: false, message: 'Failed to send test email', error: 'SMTP error' },
      })

      const result = await emailService.testConfiguration(1, 'test@example.com')

      expect(result.success).toBe(false)
      expect(result.error).toBeDefined()
    })

    it('should validate email format', async () => {
      mockAxios.post.mockRejectedValue({
        response: { status: 422, data: { detail: 'Invalid email address' } },
      })

      await expect(emailService.testConfiguration(1, 'invalid-email')).rejects.toMatchObject({
        response: { status: 422 },
      })
    })
  })

  describe('getTemplates', () => {
    it('should fetch all email templates', async () => {
      mockAxios.get.mockResolvedValue({ data: [mockTemplate] })

      const result = await emailService.getTemplates()

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/email/templates')
      expect(result).toHaveLength(1)
      expect(result[0].slug).toBe('welcome')
    })

    it('should handle empty templates', async () => {
      mockAxios.get.mockResolvedValue({ data: [] })

      const result = await emailService.getTemplates()

      expect(result).toHaveLength(0)
    })
  })

  describe('getTemplate', () => {
    it('should fetch single template', async () => {
      mockAxios.get.mockResolvedValue({ data: mockTemplate })

      const result = await emailService.getTemplate(1)

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/email/templates/1')
      expect(result.id).toBe(1)
      expect(result.name).toBe('Welcome Email')
    })

    it('should handle 404 errors', async () => {
      mockAxios.get.mockRejectedValue({
        response: { status: 404, data: { detail: 'Template not found' } },
      })

      await expect(emailService.getTemplate(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })
  })

  describe('createTemplate', () => {
    it('should create email template', async () => {
      const createData: CreateEmailTemplate = {
        name: 'Password Reset',
        slug: 'password-reset',
        subject: 'Reset your password',
        html_content: '<p>Click here to reset: {{reset_link}}</p>',
        text_content: 'Reset link: {{reset_link}}',
        variables: ['reset_link'],
        description: 'Password reset email',
        is_active: true,
      }

      mockAxios.post.mockResolvedValue({
        data: { id: 2, ...createData, created_at: '2024-01-01T00:00:00Z' },
      })

      const result = await emailService.createTemplate(createData)

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/email/templates', createData)
      expect(result.slug).toBe('password-reset')
    })

    it('should handle duplicate slug', async () => {
      mockAxios.post.mockRejectedValue({
        response: { status: 409, data: { detail: 'Template slug already exists' } },
      })

      await expect(
        emailService.createTemplate({
          name: 'Test',
          slug: 'welcome',
          subject: 'Test',
          html_content: '<p>Test</p>',
        })
      ).rejects.toMatchObject({
        response: { status: 409 },
      })
    })
  })

  describe('updateTemplate', () => {
    it('should update email template', async () => {
      const updateData: UpdateEmailTemplate = {
        subject: 'Welcome to {{site_name}} - Updated',
        html_content: '<h1>Welcome {{user_name}}!</h1><p>Updated content</p>',
      }

      mockAxios.put.mockResolvedValue({
        data: { ...mockTemplate, ...updateData },
      })

      const result = await emailService.updateTemplate(1, updateData)

      expect(mockAxios.put).toHaveBeenCalledWith('/api/v1/admin/email/templates/1', updateData)
      expect(result.subject).toContain('Updated')
    })

    it('should update variables list', async () => {
      mockAxios.put.mockResolvedValue({
        data: { ...mockTemplate, variables: ['site_name', 'user_name', 'new_var'] },
      })

      const result = await emailService.updateTemplate(1, {
        variables: ['site_name', 'user_name', 'new_var'],
      })

      expect(result.variables).toHaveLength(3)
    })

    it('should toggle active status', async () => {
      mockAxios.put.mockResolvedValue({
        data: { ...mockTemplate, is_active: false },
      })

      const result = await emailService.updateTemplate(1, { is_active: false })

      expect(result.is_active).toBe(false)
    })
  })

  describe('deleteTemplate', () => {
    it('should delete email template', async () => {
      mockAxios.delete.mockResolvedValue({ data: { message: 'Template deleted' } })

      await emailService.deleteTemplate(1)

      expect(mockAxios.delete).toHaveBeenCalledWith('/api/v1/admin/email/templates/1')
    })

    it('should handle protected templates', async () => {
      mockAxios.delete.mockRejectedValue({
        response: { status: 403, data: { detail: 'Cannot delete system template' } },
      })

      await expect(emailService.deleteTemplate(1)).rejects.toMatchObject({
        response: { status: 403 },
      })
    })
  })

  describe('previewTemplate', () => {
    it('should preview template with variables', async () => {
      const variables = {
        site_name: 'VideoSite',
        user_name: 'John Doe',
      }

      const mockPreview = {
        subject: 'Welcome to VideoSite',
        html_content: '<h1>Welcome John Doe</h1>',
        text_content: 'Welcome John Doe',
      }

      mockAxios.post.mockResolvedValue({ data: mockPreview })

      const result = await emailService.previewTemplate(1, variables)

      expect(mockAxios.post).toHaveBeenCalledWith(
        '/api/v1/admin/email/templates/1/preview',
        variables
      )
      expect(result.subject).toBe('Welcome to VideoSite')
      expect(result.html_content).toContain('John Doe')
    })

    it('should handle missing variables', async () => {
      mockAxios.post.mockResolvedValue({
        data: {
          subject: 'Welcome to {{site_name}}',
          html_content: '<h1>Welcome {{user_name}}</h1>',
        },
      })

      const result = await emailService.previewTemplate(1, {})

      // Variables not replaced
      expect(result.subject).toContain('{{site_name}}')
    })

    it('should handle HTML special characters', async () => {
      const variables = {
        user_name: '<script>alert("xss")</script>',
      }

      mockAxios.post.mockResolvedValue({
        data: {
          subject: 'Test',
          html_content: '<h1>Welcome &lt;script&gt;alert("xss")&lt;/script&gt;</h1>',
        },
      })

      const result = await emailService.previewTemplate(1, variables)

      // Should be escaped
      expect(result.html_content).not.toContain('<script>')
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockAxios.get.mockRejectedValue(new Error('Network Error'))

      await expect(emailService.getConfigurations()).rejects.toThrow('Network Error')
    })

    it('should handle 401 unauthorized', async () => {
      mockAxios.get.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(emailService.getTemplates()).rejects.toMatchObject({
        response: { status: 401 },
      })
    })

    it('should handle 500 server errors', async () => {
      mockAxios.post.mockRejectedValue({
        response: { status: 500, data: { detail: 'Internal Server Error' } },
      })

      await expect(
        emailService.createConfiguration({
          provider: 'smtp',
          smtp_host: 'test',
          smtp_port: 587,
          smtp_username: 'test',
          smtp_password: 'test',
          from_email: 'test@test.com',
          from_name: 'Test',
        })
      ).rejects.toMatchObject({
        response: { status: 500 },
      })
    })
  })

  describe('Edge Cases', () => {
    it('should handle very long template content', async () => {
      const longContent = '<p>' + 'A'.repeat(10000) + '</p>'

      mockAxios.post.mockResolvedValue({
        data: { ...mockTemplate, html_content: longContent },
      })

      const result = await emailService.createTemplate({
        name: 'Long Template',
        slug: 'long-template',
        subject: 'Test',
        html_content: longContent,
      })

      expect(result.html_content.length).toBeGreaterThan(10000)
    })

    it('should handle special characters in from_name', async () => {
      mockAxios.post.mockResolvedValue({
        data: { ...mockSMTPConfig, from_name: 'Video Site™ © 2024' },
      })

      const result = await emailService.createConfiguration({
        provider: 'smtp',
        smtp_host: 'smtp.test.com',
        smtp_port: 587,
        smtp_username: 'test',
        smtp_password: 'test',
        from_email: 'test@test.com',
        from_name: 'Video Site™ © 2024',
      })

      expect(result.from_name).toContain('™')
    })

    it('should handle multiple configurations with same provider', async () => {
      mockAxios.get.mockResolvedValue({
        data: [mockSMTPConfig, { ...mockSMTPConfig, id: 2, is_active: false }],
      })

      const result = await emailService.getConfigurations()

      expect(result).toHaveLength(2)
      expect(result.filter((c) => c.provider === 'smtp')).toHaveLength(2)
    })
  })
})
