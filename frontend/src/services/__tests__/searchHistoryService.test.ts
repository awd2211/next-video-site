/**
 * 搜索历史服务测试
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { searchHistoryService } from '../searchHistoryService'
import api from '../api'

vi.mock('../api')

describe('Search History Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(console, 'warn').mockImplementation(() => {})
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('recordSearch', () => {
    it('should record search history', async () => {
      mockApi.post.mockResolvedValue({ data: null })

      await searchHistoryService.recordSearch('test query', 5)

      expect(mockApi.post).toHaveBeenCalledWith('/search/history', {
        query: 'test query',
        results_count: 5,
      })
    })

    it('should silently fail on errors', async () => {
      mockApi.post.mockRejectedValue(new Error('Network error'))

      // Should not throw
      await expect(searchHistoryService.recordSearch('test', 0)).resolves.toBeUndefined()
      
      expect(console.warn).toHaveBeenCalledWith(
        'Failed to record search history:',
        expect.any(Error)
      )
    })

    it('should handle server errors gracefully', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 500, data: { detail: 'Server error' } },
      })

      await searchHistoryService.recordSearch('query', 10)

      expect(console.warn).toHaveBeenCalled()
    })
  })

  describe('getHistory', () => {
    it('should get search history with default limit', async () => {
      const mockHistory = [
        { id: 1, query: 'query 1', results_count: 10, created_at: '2024-01-01' },
        { id: 2, query: 'query 2', results_count: 5, created_at: '2024-01-02' },
      ]

      mockApi.get.mockResolvedValue({ data: mockHistory })

      const result = await searchHistoryService.getHistory()

      expect(mockApi.get).toHaveBeenCalledWith('/search/history', {
        params: { limit: 20 },
      })
      expect(result).toHaveLength(2)
      expect(result[0].query).toBe('query 1')
    })

    it('should get search history with custom limit', async () => {
      mockApi.get.mockResolvedValue({ data: [] })

      await searchHistoryService.getHistory(10)

      expect(mockApi.get).toHaveBeenCalledWith('/search/history', {
        params: { limit: 10 },
      })
    })

    it('should return empty array on error', async () => {
      mockApi.get.mockRejectedValue(new Error('Network error'))

      const result = await searchHistoryService.getHistory()

      expect(result).toEqual([])
      expect(console.error).toHaveBeenCalledWith(
        'Failed to get search history:',
        expect.any(Error)
      )
    })

    it('should handle unauthorized access', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      const result = await searchHistoryService.getHistory()

      expect(result).toEqual([])
    })
  })

  describe('deleteItem', () => {
    it('should delete search history item', async () => {
      mockApi.delete.mockResolvedValue({ data: null })

      await searchHistoryService.deleteItem(1)

      expect(mockApi.delete).toHaveBeenCalledWith('/search/history/1')
    })

    it('should handle item not found', async () => {
      mockApi.delete.mockRejectedValue({
        response: { status: 404, data: { detail: 'Item not found' } },
      })

      await expect(searchHistoryService.deleteItem(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })

    it('should require authentication', async () => {
      mockApi.delete.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(searchHistoryService.deleteItem(1)).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('clearAll', () => {
    it('should clear all search history', async () => {
      mockApi.delete.mockResolvedValue({ data: null })

      await searchHistoryService.clearAll()

      expect(mockApi.delete).toHaveBeenCalledWith('/search/history')
    })

    it('should require authentication', async () => {
      mockApi.delete.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(searchHistoryService.clearAll()).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('getPopular', () => {
    it('should get popular searches with default parameters', async () => {
      const mockPopular = [
        { query: 'popular query 1', search_count: 100 },
        { query: 'popular query 2', search_count: 50 },
      ]

      mockApi.get.mockResolvedValue({ data: mockPopular })

      const result = await searchHistoryService.getPopular()

      expect(mockApi.get).toHaveBeenCalledWith('/search/popular', {
        params: { limit: 10, hours: 24 },
      })
      expect(result).toHaveLength(2)
      expect(result[0].search_count).toBe(100)
    })

    it('should get popular searches with custom parameters', async () => {
      mockApi.get.mockResolvedValue({ data: [] })

      await searchHistoryService.getPopular(5, 12)

      expect(mockApi.get).toHaveBeenCalledWith('/search/popular', {
        params: { limit: 5, hours: 12 },
      })
    })

    it('should return empty array on error', async () => {
      mockApi.get.mockRejectedValue(new Error('Server error'))

      const result = await searchHistoryService.getPopular()

      expect(result).toEqual([])
      expect(console.error).toHaveBeenCalledWith(
        'Failed to get popular searches:',
        expect.any(Error)
      )
    })

    it('should handle server errors gracefully', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 500, data: { detail: 'Internal server error' } },
      })

      const result = await searchHistoryService.getPopular()

      expect(result).toEqual([])
    })
  })
})
