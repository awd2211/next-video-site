/**
 * AI Management Service Tests
 * AI管理服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from '@/utils/axios'
import * as aiService from '../aiManagement'

vi.mock('@/utils/axios')

describe('AI Management Service', () => {
  const mockAxios = vi.mocked(axios)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  const mockProvider: aiService.AIProvider = {
    id: 1,
    name: 'OpenAI GPT-4',
    provider_type: 'openai',
    description: 'OpenAI GPT-4 model',
    api_key: 'sk-xxxxx',
    base_url: 'https://api.openai.com/v1',
    model_name: 'gpt-4',
    max_tokens: 4096,
    temperature: 0.7,
    top_p: 1.0,
    frequency_penalty: 0,
    presence_penalty: 0,
    settings: {},
    enabled: true,
    is_default: true,
    total_requests: 100,
    total_tokens: 50000,
    last_used_at: '2024-01-01T00:00:00Z',
    last_test_at: '2024-01-01T00:00:00Z',
    last_test_status: 'success',
    last_test_message: 'Connection successful',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  }

  describe('getAIProviders', () => {
    it('should fetch all providers', async () => {
      mockAxios.get.mockResolvedValue({ data: { total: 1, items: [mockProvider] } })

      const result = await aiService.getAIProviders()

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/ai/providers', { params: undefined })
      expect(result.items).toHaveLength(1)
      expect(result.items[0].provider_type).toBe('openai')
    })

    it('should filter by provider type', async () => {
      mockAxios.get.mockResolvedValue({ data: { total: 0, items: [] } })

      await aiService.getAIProviders({ provider_type: 'grok' })

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/ai/providers', {
        params: { provider_type: 'grok' },
      })
    })

    it('should filter by enabled status', async () => {
      mockAxios.get.mockResolvedValue({ data: { total: 1, items: [mockProvider] } })

      await aiService.getAIProviders({ enabled: true })

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/ai/providers', {
        params: { enabled: true },
      })
    })
  })

  describe('getAIProvider', () => {
    it('should fetch single provider', async () => {
      mockAxios.get.mockResolvedValue({ data: mockProvider })

      const result = await aiService.getAIProvider(1)

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/ai/providers/1')
      expect(result.id).toBe(1)
      expect(result.name).toBe('OpenAI GPT-4')
    })

    it('should handle 404 errors', async () => {
      mockAxios.get.mockRejectedValue({ response: { status: 404 } })

      await expect(aiService.getAIProvider(999)).rejects.toMatchObject({ response: { status: 404 } })
    })
  })

  describe('createAIProvider', () => {
    it('should create OpenAI provider', async () => {
      const createData: aiService.AIProviderCreate = {
        name: 'New OpenAI',
        provider_type: 'openai',
        api_key: 'sk-new',
        model_name: 'gpt-3.5-turbo',
        temperature: 0.8,
      }

      mockAxios.post.mockResolvedValue({ data: { ...mockProvider, ...createData } })

      const result = await aiService.createAIProvider(createData)

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/ai/providers', createData)
      expect(result.provider_type).toBe('openai')
    })

    it('should create with all optional parameters', async () => {
      const fullData: aiService.AIProviderCreate = {
        name: 'Full Provider',
        provider_type: 'google',
        api_key: 'key',
        model_name: 'gemini-pro',
        max_tokens: 2048,
        temperature: 0.5,
        top_p: 0.9,
        frequency_penalty: 0.1,
        presence_penalty: 0.2,
        settings: { extra: 'config' },
        enabled: false,
        is_default: false,
      }

      mockAxios.post.mockResolvedValue({ data: mockProvider })

      await aiService.createAIProvider(fullData)

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/ai/providers', fullData)
    })
  })

  describe('updateAIProvider', () => {
    it('should update provider', async () => {
      const updateData: aiService.AIProviderUpdate = {
        name: 'Updated Name',
        temperature: 0.9,
        enabled: false,
      }

      mockAxios.put.mockResolvedValue({ data: { ...mockProvider, ...updateData } })

      const result = await aiService.updateAIProvider(1, updateData)

      expect(mockAxios.put).toHaveBeenCalledWith('/api/v1/admin/ai/providers/1', updateData)
      expect(result.name).toBe('Updated Name')
    })

    it('should update API key', async () => {
      mockAxios.put.mockResolvedValue({ data: mockProvider })

      await aiService.updateAIProvider(1, { api_key: 'new-key' })

      expect(mockAxios.put).toHaveBeenCalledWith('/api/v1/admin/ai/providers/1', { api_key: 'new-key' })
    })
  })

  describe('deleteAIProvider', () => {
    it('should delete provider', async () => {
      mockAxios.delete.mockResolvedValue({ data: { message: 'Deleted' } })

      await aiService.deleteAIProvider(1)

      expect(mockAxios.delete).toHaveBeenCalledWith('/api/v1/admin/ai/providers/1')
    })

    it('should handle 404 errors', async () => {
      mockAxios.delete.mockRejectedValue({ response: { status: 404 } })

      await expect(aiService.deleteAIProvider(999)).rejects.toMatchObject({ response: { status: 404 } })
    })
  })

  describe('testAIProvider', () => {
    it('should test provider successfully', async () => {
      const testResponse: aiService.AITestResponse = {
        success: true,
        response: 'Test response from AI',
        tokens_used: 50,
        latency_ms: 1200,
      }

      mockAxios.post.mockResolvedValue({ data: testResponse })

      const result = await aiService.testAIProvider(1, { message: 'Hello' })

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/ai/providers/1/test', { message: 'Hello' })
      expect(result.success).toBe(true)
      expect(result.response).toBeDefined()
    })

    it('should handle test failure', async () => {
      const testResponse: aiService.AITestResponse = {
        success: false,
        error: 'Connection timeout',
      }

      mockAxios.post.mockResolvedValue({ data: testResponse })

      const result = await aiService.testAIProvider(1, { message: 'Test' })

      expect(result.success).toBe(false)
      expect(result.error).toBeDefined()
    })
  })

  describe('chatWithAI', () => {
    it('should send chat request', async () => {
      const chatResponse: aiService.AIChatResponse = {
        success: true,
        response: 'AI response',
        tokens_used: 100,
        latency_ms: 1500,
        model: 'gpt-4',
      }

      mockAxios.post.mockResolvedValue({ data: chatResponse })

      const result = await aiService.chatWithAI({
        provider_id: 1,
        messages: [{ role: 'user', content: 'Hello' }],
      })

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/ai/chat', {
        provider_id: 1,
        messages: [{ role: 'user', content: 'Hello' }],
      })
      expect(result.response).toBe('AI response')
    })

    it('should support streaming', async () => {
      mockAxios.post.mockResolvedValue({ data: { success: true } })

      await aiService.chatWithAI({
        provider_id: 1,
        messages: [{ role: 'user', content: 'Test' }],
        stream: true,
      })

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/ai/chat', expect.objectContaining({ stream: true }))
    })
  })

  describe('getAvailableModels', () => {
    it('should fetch models for provider type', async () => {
      const modelsResponse = {
        provider_type: 'openai',
        models: [
          { id: 'gpt-4', name: 'GPT-4', context_window: 8192 },
          { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', context_window: 4096 },
        ],
      }

      mockAxios.get.mockResolvedValue({ data: modelsResponse })

      const result = await aiService.getAvailableModels('openai')

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/ai/models/openai')
      expect(result.models).toHaveLength(2)
    })
  })

  describe('getAIUsageStats', () => {
    it('should fetch usage statistics', async () => {
      const statsResponse = {
        stats: [
          {
            provider_id: 1,
            provider_name: 'OpenAI',
            provider_type: 'openai',
            total_requests: 1000,
            total_tokens: 500000,
            enabled: true,
          },
        ],
        total_requests: 1000,
        total_tokens: 500000,
      }

      mockAxios.get.mockResolvedValue({ data: statsResponse })

      const result = await aiService.getAIUsageStats()

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/ai/usage')
      expect(result.total_requests).toBe(1000)
      expect(result.stats).toHaveLength(1)
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockAxios.get.mockRejectedValue(new Error('Network error'))

      await expect(aiService.getAIProviders()).rejects.toThrow('Network error')
    })

    it('should handle 401 unauthorized', async () => {
      mockAxios.get.mockRejectedValue({ response: { status: 401 } })

      await expect(aiService.getAIProvider(1)).rejects.toMatchObject({ response: { status: 401 } })
    })

    it('should handle validation errors', async () => {
      mockAxios.post.mockRejectedValue({ response: { status: 422 } })

      await expect(
        aiService.createAIProvider({
          name: '',
          provider_type: 'openai',
          api_key: '',
          model_name: '',
        })
      ).rejects.toMatchObject({ response: { status: 422 } })
    })
  })

  describe('Edge Cases', () => {
    it('should handle all provider types', async () => {
      const types: Array<'openai' | 'grok' | 'google'> = ['openai', 'grok', 'google']

      for (const type of types) {
        mockAxios.get.mockResolvedValue({ data: { total: 0, items: [] } })
        await aiService.getAIProviders({ provider_type: type })
        expect(mockAxios.get).toHaveBeenLastCalledWith('/api/v1/admin/ai/providers', { params: { provider_type: type } })
      }
    })

    it('should handle very long API keys', async () => {
      const longKey = 'sk-' + 'x'.repeat(500)
      mockAxios.post.mockResolvedValue({ data: mockProvider })

      await aiService.createAIProvider({
        name: 'Test',
        provider_type: 'openai',
        api_key: longKey,
        model_name: 'gpt-4',
      })

      expect(mockAxios.post).toHaveBeenCalled()
    })
  })
})
