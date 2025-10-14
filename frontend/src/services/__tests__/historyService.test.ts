/**
 * 观看历史服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { historyService } from '../historyService'
import api from '../api'

vi.mock('../api')

describe('History Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('recordHistory', () => {
    it('should record watch history', async () => {
      const mockResponse = {
        id: 1,
        user_id: 1,
        video_id: 10,
        watch_duration: 300,
        last_position: 250,
        is_completed: 0,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: null,
        video: { id: 10, title: 'Test Video' },
      }

      mockApi.post.mockResolvedValue({ data: mockResponse })

      const result = await historyService.recordHistory(10, 300, 250)

      expect(mockApi.post).toHaveBeenCalledWith('/history/', {
        video_id: 10,
        watch_duration: 300,
        last_position: 250,
        is_completed: false,
      })
      expect(result.video_id).toBe(10)
      expect(result.watch_duration).toBe(300)
    })

    it('should record completed video', async () => {
      const mockResponse = {
        id: 1,
        user_id: 1,
        video_id: 10,
        watch_duration: 7200,
        last_position: 7200,
        is_completed: 1,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: null,
        video: { id: 10, title: 'Test Video' },
      }

      mockApi.post.mockResolvedValue({ data: mockResponse })

      const result = await historyService.recordHistory(10, 7200, 7200, true)

      expect(mockApi.post).toHaveBeenCalledWith('/history/', {
        video_id: 10,
        watch_duration: 7200,
        last_position: 7200,
        is_completed: true,
      })
      expect(result.is_completed).toBe(1)
    })

    it('should require authentication', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(historyService.recordHistory(10, 100, 50)).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('getHistory', () => {
    it('should fetch watch history with default pagination', async () => {
      const mockResponse = {
        total: 2,
        page: 1,
        page_size: 20,
        items: [
          {
            id: 1,
            user_id: 1,
            video_id: 10,
            watch_duration: 300,
            last_position: 250,
            is_completed: 0,
            created_at: '2024-01-01T00:00:00Z',
            updated_at: null,
            video: { id: 10, title: 'Video 1' },
          },
        ],
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await historyService.getHistory()

      expect(mockApi.get).toHaveBeenCalledWith('/history/', {
        params: { page: 1, page_size: 20 },
      })
      expect(result.items).toHaveLength(1)
    })

    it('should fetch with custom pagination', async () => {
      mockApi.get.mockResolvedValue({
        data: { total: 0, page: 2, page_size: 10, items: [] },
      })

      await historyService.getHistory(2, 10)

      expect(mockApi.get).toHaveBeenCalledWith('/history/', {
        params: { page: 2, page_size: 10 },
      })
    })
  })

  describe('getVideoHistory', () => {
    it('should get specific video history', async () => {
      const mockResponse = {
        id: 1,
        user_id: 1,
        video_id: 10,
        watch_duration: 300,
        last_position: 250,
        is_completed: 0,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: null,
        video: { id: 10, title: 'Test Video' },
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await historyService.getVideoHistory(10)

      expect(mockApi.get).toHaveBeenCalledWith('/history/10')
      expect(result).not.toBeNull()
      expect(result?.video_id).toBe(10)
    })

    it('should return null for non-existent history', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 404, data: { detail: 'Not found' } },
      })

      const result = await historyService.getVideoHistory(999)

      expect(result).toBeNull()
    })

    it('should throw on other errors', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 500, data: { detail: 'Server error' } },
      })

      await expect(historyService.getVideoHistory(10)).rejects.toMatchObject({
        response: { status: 500 },
      })
    })
  })

  describe('updateProgress', () => {
    it('should update watch progress', async () => {
      const mockResponse = {
        id: 1,
        user_id: 1,
        video_id: 10,
        watch_duration: 350,
        last_position: 300,
        is_completed: 0,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:10:00Z',
        video: { id: 10, title: 'Test Video' },
      }

      mockApi.patch.mockResolvedValue({ data: mockResponse })

      const result = await historyService.updateProgress(10, 300, 350)

      expect(mockApi.patch).toHaveBeenCalledWith('/history/10/progress', {
        last_position: 300,
        watch_duration: 350,
        is_completed: undefined,
      })
      expect(result.last_position).toBe(300)
    })

    it('should update progress with completion status', async () => {
      mockApi.patch.mockResolvedValue({
        data: {
          id: 1,
          user_id: 1,
          video_id: 10,
          watch_duration: 7200,
          last_position: 7200,
          is_completed: 1,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T02:00:00Z',
          video: { id: 10, title: 'Test Video' },
        },
      })

      const result = await historyService.updateProgress(10, 7200, 7200, true)

      expect(result.is_completed).toBe(1)
    })
  })

  describe('deleteHistory', () => {
    it('should delete specific video history', async () => {
      mockApi.delete.mockResolvedValue({ data: null })

      await historyService.deleteHistory(10)

      expect(mockApi.delete).toHaveBeenCalledWith('/history/10')
    })

    it('should handle non-existent history', async () => {
      mockApi.delete.mockRejectedValue({
        response: { status: 404, data: { detail: 'Not found' } },
      })

      await expect(historyService.deleteHistory(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })
  })

  describe('clearHistory', () => {
    it('should clear all history', async () => {
      mockApi.delete.mockResolvedValue({ data: null })

      await historyService.clearHistory()

      expect(mockApi.delete).toHaveBeenCalledWith('/history/')
    })

    it('should require authentication', async () => {
      mockApi.delete.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(historyService.clearHistory()).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })
})

