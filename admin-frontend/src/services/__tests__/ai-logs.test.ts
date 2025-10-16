/**
 * AI Logs Service Tests
 * AI日志服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import * as aiLogsService from '../ai-logs'

vi.mock('axios')

describe('AI Logs Service', () => {
  const mockAxios = vi.mocked(axios)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  const mockRequestLog: aiLogsService.AIRequestLog = {
    id: 1,
    provider_id: 1,
    provider_type: 'openai',
    model: 'gpt-4',
    request_type: 'chat',
    prompt: 'Hello AI',
    response: 'Hello! How can I help?',
    prompt_tokens: 10,
    completion_tokens: 20,
    total_tokens: 30,
    response_time: 1200,
    status: 'success',
    estimated_cost: 0.0015,
    user_id: 100,
    admin_user_id: 1,
    ip_address: '192.168.1.1',
    user_agent: 'Mozilla/5.0',
    created_at: '2024-01-01T00:00:00Z',
  }

  describe('getRequestLogs', () => {
    it('should fetch request logs with default parameters', async () => {
      mockAxios.get.mockResolvedValue({
        data: { items: [mockRequestLog], total: 1 },
      })

      const result = await aiLogsService.getRequestLogs()

      expect(mockAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/admin/ai-logs/request-logs'),
        { params: undefined }
      )
      expect(result.items).toHaveLength(1)
    })

    it('should fetch with filters', async () => {
      mockAxios.get.mockResolvedValue({ data: { items: [], total: 0 } })

      await aiLogsService.getRequestLogs({
        skip: 10,
        limit: 50,
        provider_type: 'openai',
        model: 'gpt-4',
        status: 'success',
      })

      expect(mockAxios.get).toHaveBeenCalledWith(expect.any(String), {
        params: expect.objectContaining({
          provider_type: 'openai',
          model: 'gpt-4',
          status: 'success',
        }),
      })
    })

    it('should filter by date range', async () => {
      mockAxios.get.mockResolvedValue({ data: { items: [], total: 0 } })

      await aiLogsService.getRequestLogs({
        start_date: '2024-01-01',
        end_date: '2024-01-31',
      })

      expect(mockAxios.get).toHaveBeenCalledWith(expect.any(String), {
        params: expect.objectContaining({
          start_date: '2024-01-01',
          end_date: '2024-01-31',
        }),
      })
    })

    it('should filter by cost range', async () => {
      mockAxios.get.mockResolvedValue({ data: { items: [], total: 0 } })

      await aiLogsService.getRequestLogs({
        min_cost: 0.001,
        max_cost: 0.01,
      })

      expect(mockAxios.get).toHaveBeenCalledWith(expect.any(String), {
        params: expect.objectContaining({
          min_cost: 0.001,
          max_cost: 0.01,
        }),
      })
    })
  })

  describe('getRequestLog', () => {
    it('should fetch single request log', async () => {
      mockAxios.get.mockResolvedValue({ data: mockRequestLog })

      const result = await aiLogsService.getRequestLog(1)

      expect(mockAxios.get).toHaveBeenCalledWith(expect.stringContaining('/request-logs/1'))
      expect(result.id).toBe(1)
    })

    it('should handle 404 errors', async () => {
      mockAxios.get.mockRejectedValue({ response: { status: 404 } })

      await expect(aiLogsService.getRequestLog(999)).rejects.toMatchObject({ response: { status: 404 } })
    })
  })

  describe('deleteRequestLog', () => {
    it('should delete request log', async () => {
      mockAxios.delete.mockResolvedValue({ data: { message: 'Deleted' } })

      await aiLogsService.deleteRequestLog(1)

      expect(mockAxios.delete).toHaveBeenCalledWith(expect.stringContaining('/request-logs/1'))
    })
  })

  describe('getUsageStats', () => {
    it('should fetch usage statistics', async () => {
      const mockStats: aiLogsService.AIUsageStats = {
        total_requests: 1000,
        total_tokens: 50000,
        total_cost: 25.5,
        avg_response_time: 1500,
        success_rate: 0.98,
        requests_by_provider: { openai: 800, grok: 200 },
        tokens_by_provider: { openai: 40000, grok: 10000 },
        cost_by_provider: { openai: 20, grok: 5.5 },
        requests_by_model: { 'gpt-4': 500, 'gpt-3.5-turbo': 500 },
        avg_response_time_by_provider: { openai: 1200, grok: 2000 },
      }

      mockAxios.get.mockResolvedValue({ data: mockStats })

      const result = await aiLogsService.getUsageStats()

      expect(mockAxios.get).toHaveBeenCalledWith(expect.stringContaining('/stats/usage'), { params: undefined })
      expect(result.total_requests).toBe(1000)
      expect(result.success_rate).toBe(0.98)
    })

    it('should fetch stats with filters', async () => {
      mockAxios.get.mockResolvedValue({
        data: {
          total_requests: 0,
          total_tokens: 0,
          total_cost: 0,
          avg_response_time: 0,
          success_rate: 0,
          requests_by_provider: {},
          tokens_by_provider: {},
          cost_by_provider: {},
          requests_by_model: {},
          avg_response_time_by_provider: {},
        },
      })

      await aiLogsService.getUsageStats({
        start_date: '2024-01-01',
        end_date: '2024-01-31',
        provider_type: 'openai',
      })

      expect(mockAxios.get).toHaveBeenCalled()
    })
  })

  describe('getCostStats', () => {
    it('should fetch cost statistics', async () => {
      const mockCostStats: aiLogsService.AICostStats = {
        today_cost: 5.5,
        this_month_cost: 150.25,
        cost_trend: [
          { date: '2024-01-01', cost: 5, requests: 100 },
          { date: '2024-01-02', cost: 6, requests: 120 },
        ],
        projected_monthly_cost: 500,
        cost_by_model: { 'gpt-4': 100, 'gpt-3.5-turbo': 50.25 },
        top_cost_users: [{ user_id: 1, username: 'user1', cost: 50 }],
      }

      mockAxios.get.mockResolvedValue({ data: mockCostStats })

      const result = await aiLogsService.getCostStats()

      expect(mockAxios.get).toHaveBeenCalledWith(expect.stringContaining('/stats/cost'), { params: undefined })
      expect(result.today_cost).toBe(5.5)
      expect(result.cost_trend).toHaveLength(2)
    })

    it('should fetch with custom days', async () => {
      mockAxios.get.mockResolvedValue({
        data: {
          today_cost: 0,
          this_month_cost: 0,
          cost_trend: [],
          projected_monthly_cost: 0,
          cost_by_model: {},
          top_cost_users: [],
        },
      })

      await aiLogsService.getCostStats({ days: 90 })

      expect(mockAxios.get).toHaveBeenCalledWith(expect.any(String), {
        params: { days: 90 },
      })
    })
  })

  describe('Quota Management', () => {
    describe('getQuotas', () => {
      it('should fetch all quotas', async () => {
        const mockQuotas: aiLogsService.AIQuota[] = [
          {
            id: 1,
            quota_type: 'global',
            daily_request_limit: 1000,
            monthly_request_limit: 30000,
            daily_requests_used: 500,
            monthly_requests_used: 15000,
            daily_tokens_used: 50000,
            monthly_tokens_used: 1500000,
            daily_cost_used: 25,
            monthly_cost_used: 750,
            is_active: true,
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
          },
        ]

        mockAxios.get.mockResolvedValue({ data: mockQuotas })

        const result = await aiLogsService.getQuotas()

        expect(mockAxios.get).toHaveBeenCalledWith(expect.stringContaining('/quotas'))
        expect(result).toHaveLength(1)
      })
    })

    describe('createQuota', () => {
      it('should create quota', async () => {
        const createData: aiLogsService.QuotaCreate = {
          quota_type: 'user',
          target_id: 100,
          daily_request_limit: 100,
          monthly_request_limit: 3000,
        }

        mockAxios.post.mockResolvedValue({ data: { id: 1, ...createData } })

        await aiLogsService.createQuota(createData)

        expect(mockAxios.post).toHaveBeenCalledWith(expect.stringContaining('/quotas'), createData)
      })
    })

    describe('updateQuota', () => {
      it('should update quota', async () => {
        mockAxios.put.mockResolvedValue({ data: { id: 1 } })

        await aiLogsService.updateQuota(1, { daily_request_limit: 200 })

        expect(mockAxios.put).toHaveBeenCalledWith(expect.stringContaining('/quotas/1'), {
          daily_request_limit: 200,
        })
      })
    })

    describe('deleteQuota', () => {
      it('should delete quota', async () => {
        mockAxios.delete.mockResolvedValue({ data: { message: 'Deleted' } })

        await aiLogsService.deleteQuota(1)

        expect(mockAxios.delete).toHaveBeenCalledWith(expect.stringContaining('/quotas/1'))
      })
    })

    describe('getGlobalQuotaStatus', () => {
      it('should fetch global quota status', async () => {
        const mockStatus: aiLogsService.AIQuotaStatus = {
          has_quota: true,
          daily_remaining_requests: 500,
          monthly_remaining_requests: 15000,
          is_limited: false,
        }

        mockAxios.get.mockResolvedValue({ data: mockStatus })

        const result = await aiLogsService.getGlobalQuotaStatus()

        expect(mockAxios.get).toHaveBeenCalledWith(expect.stringContaining('/quotas/status/global'))
        expect(result.has_quota).toBe(true)
      })
    })
  })

  describe('Template Management', () => {
    describe('getTemplates', () => {
      it('should fetch all templates', async () => {
        const mockTemplates: aiLogsService.AITemplate[] = [
          {
            id: 1,
            name: 'Summarize Text',
            category: 'text',
            prompt_template: 'Summarize: {{text}}',
            variables: ['text'],
            is_active: true,
            usage_count: 100,
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
          },
        ]

        mockAxios.get.mockResolvedValue({ data: mockTemplates })

        const result = await aiLogsService.getTemplates()

        expect(mockAxios.get).toHaveBeenCalledWith(expect.stringContaining('/templates'), { params: undefined })
        expect(result).toHaveLength(1)
      })

      it('should filter by category', async () => {
        mockAxios.get.mockResolvedValue({ data: [] })

        await aiLogsService.getTemplates({ category: 'text', is_active: true })

        expect(mockAxios.get).toHaveBeenCalledWith(expect.any(String), {
          params: { category: 'text', is_active: true },
        })
      })
    })

    describe('createTemplate', () => {
      it('should create template', async () => {
        const createData: aiLogsService.TemplateCreate = {
          name: 'New Template',
          category: 'text',
          prompt_template: 'Process: {{input}}',
          variables: ['input'],
        }

        mockAxios.post.mockResolvedValue({ data: { id: 1, ...createData } })

        await aiLogsService.createTemplate(createData)

        expect(mockAxios.post).toHaveBeenCalledWith(expect.stringContaining('/templates'), createData)
      })
    })

    describe('updateTemplate', () => {
      it('should update template', async () => {
        mockAxios.put.mockResolvedValue({ data: { id: 1 } })

        await aiLogsService.updateTemplate(1, { is_active: false })

        expect(mockAxios.put).toHaveBeenCalledWith(expect.stringContaining('/templates/1'), { is_active: false })
      })
    })

    describe('deleteTemplate', () => {
      it('should delete template', async () => {
        mockAxios.delete.mockResolvedValue({ data: { message: 'Deleted' } })

        await aiLogsService.deleteTemplate(1)

        expect(mockAxios.delete).toHaveBeenCalledWith(expect.stringContaining('/templates/1'))
      })
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockAxios.get.mockRejectedValue(new Error('Network error'))

      await expect(aiLogsService.getRequestLogs()).rejects.toThrow('Network error')
    })

    it('should handle 401 unauthorized', async () => {
      mockAxios.get.mockRejectedValue({ response: { status: 401 } })

      await expect(aiLogsService.getUsageStats()).rejects.toMatchObject({ response: { status: 401 } })
    })

    it('should handle 500 server errors', async () => {
      mockAxios.post.mockRejectedValue({ response: { status: 500 } })

      await expect(
        aiLogsService.createQuota({ quota_type: 'global' })
      ).rejects.toMatchObject({ response: { status: 500 } })
    })
  })

  describe('Edge Cases', () => {
    it('should handle very large response times', async () => {
      mockAxios.get.mockResolvedValue({
        data: { items: [{ ...mockRequestLog, response_time: 60000 }], total: 1 },
      })

      const result = await aiLogsService.getRequestLogs()

      expect(result.items[0].response_time).toBe(60000)
    })

    it('should handle zero costs', async () => {
      mockAxios.get.mockResolvedValue({
        data: {
          today_cost: 0,
          this_month_cost: 0,
          cost_trend: [],
          projected_monthly_cost: 0,
          cost_by_model: {},
          top_cost_users: [],
        },
      })

      const result = await aiLogsService.getCostStats()

      expect(result.today_cost).toBe(0)
    })

    it('should handle very long prompts', async () => {
      const longPrompt = 'A'.repeat(10000)
      mockAxios.get.mockResolvedValue({
        data: { items: [{ ...mockRequestLog, prompt: longPrompt }], total: 1 },
      })

      const result = await aiLogsService.getRequestLogs()

      expect(result.items[0].prompt?.length).toBe(10000)
    })
  })
})
