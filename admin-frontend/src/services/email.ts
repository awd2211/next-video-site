import axios from '@/utils/axios'

export interface EmailConfiguration {
  id: number
  provider: 'smtp' | 'mailgun'
  is_active: boolean
  smtp_host?: string
  smtp_port?: number
  smtp_username?: string
  smtp_use_tls?: boolean
  smtp_use_ssl?: boolean
  mailgun_domain?: string
  mailgun_base_url?: string
  from_email: string
  from_name: string
  created_at: string
  updated_at?: string
}

export interface EmailTemplate {
  id: number
  name: string
  slug: string
  subject: string
  html_content: string
  text_content?: string
  variables?: string[]
  description?: string
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface CreateEmailConfigSMTP {
  provider: 'smtp'
  smtp_host: string
  smtp_port: number
  smtp_username: string
  smtp_password: string
  smtp_use_tls?: boolean
  smtp_use_ssl?: boolean
  from_email: string
  from_name: string
}

export interface CreateEmailConfigMailgun {
  provider: 'mailgun'
  mailgun_api_key: string
  mailgun_domain: string
  mailgun_base_url?: string
  from_email: string
  from_name: string
}

export interface UpdateEmailConfig {
  provider?: string
  is_active?: boolean
  smtp_host?: string
  smtp_port?: number
  smtp_username?: string
  smtp_password?: string
  smtp_use_tls?: boolean
  smtp_use_ssl?: boolean
  mailgun_api_key?: string
  mailgun_domain?: string
  mailgun_base_url?: string
  from_email?: string
  from_name?: string
}

export interface CreateEmailTemplate {
  name: string
  slug: string
  subject: string
  html_content: string
  text_content?: string
  variables?: string[]
  description?: string
  is_active?: boolean
}

export interface UpdateEmailTemplate {
  name?: string
  subject?: string
  html_content?: string
  text_content?: string
  variables?: string[]
  description?: string
  is_active?: boolean
}

export const emailService = {
  // Email Configuration
  getConfigurations: async () => {
    const response = await axios.get<EmailConfiguration[]>('/api/v1/admin/email/config')
    return response.data
  },

  createConfiguration: async (data: CreateEmailConfigSMTP | CreateEmailConfigMailgun) => {
    const response = await axios.post<EmailConfiguration>(
      '/api/v1/admin/email/config',
      data
    )
    return response.data
  },

  updateConfiguration: async (id: number, data: UpdateEmailConfig) => {
    const response = await axios.put<EmailConfiguration>(
      `/api/v1/admin/email/config/${id}`,
      data
    )
    return response.data
  },

  deleteConfiguration: async (id: number) => {
    await axios.delete(`/api/v1/admin/email/config/${id}`)
  },

  testConfiguration: async (id: number, testEmail: string) => {
    const response = await axios.post(`/api/v1/admin/email/config/${id}/test`, {
      test_email: testEmail,
    })
    return response.data
  },

  // Email Templates
  getTemplates: async () => {
    const response = await axios.get<EmailTemplate[]>('/api/v1/admin/email/templates')
    return response.data
  },

  getTemplate: async (id: number) => {
    const response = await axios.get<EmailTemplate>(`/api/v1/admin/email/templates/${id}`)
    return response.data
  },

  createTemplate: async (data: CreateEmailTemplate) => {
    const response = await axios.post<EmailTemplate>(
      '/api/v1/admin/email/templates',
      data
    )
    return response.data
  },

  updateTemplate: async (id: number, data: UpdateEmailTemplate) => {
    const response = await axios.put<EmailTemplate>(
      `/api/v1/admin/email/templates/${id}`,
      data
    )
    return response.data
  },

  deleteTemplate: async (id: number) => {
    await axios.delete(`/api/v1/admin/email/templates/${id}`)
  },

  previewTemplate: async (id: number, variables: Record<string, any>) => {
    const response = await axios.post<{
      subject: string
      html_content: string
      text_content?: string
    }>(`/api/v1/admin/email/templates/${id}/preview`, variables)
    return response.data
  },
}
