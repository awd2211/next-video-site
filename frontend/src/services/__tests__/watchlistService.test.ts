/**
 * 观看列表服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import watchlistService from '../watchlistService'
import api from '../api'

vi.mock('../api')

describe('Watchlist Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getMyList', () => {
    it('should get user watchlist', async () => {
      const mockWatchlist = [
        {
          id: 1,
          user_id: 1,
          video_id: 10,
          position: 0,
          created_at: '2024-01-01T00:00:00Z',
          video: {
            id: 10,
            title: 'Movie 1',
            poster_url: 'poster1.jpg',
            duration: 7200,
            view_count: 1000,
            average_rating: 8.5,
            release_year: 2024,
            video_type: 'movie',
            country: { id: 1, name: 'USA', code: 'US' },
            categories: [{ id: 1, name: 'Action', slug: 'action' }],
          },
        },
        {
          id: 2,
          user_id: 1,
          video_id: 20,
          position: 1,
          created_at: '2024-01-02T00:00:00Z',
          video: {
            id: 20,
            title: 'Series 1',
            poster_url: 'poster2.jpg',
            duration: 3600,
            view_count: 500,
            average_rating: 9.0,
            video_type: 'series',
          },
        },
      ]

      mockApi.get.mockResolvedValue({ data: mockWatchlist })

      const result = await watchlistService.getMyList()

      expect(mockApi.get).toHaveBeenCalledWith('/watchlist')
      expect(result).toHaveLength(2)
      expect(result[0].video.title).toBe('Movie 1')
      expect(result[1].position).toBe(1)
    })

    it('should handle empty watchlist', async () => {
      mockApi.get.mockResolvedValue({ data: [] })

      const result = await watchlistService.getMyList()

      expect(result).toHaveLength(0)
    })

    it('should require authentication', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(watchlistService.getMyList()).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('addToList', () => {
    it('should add video to watchlist', async () => {
      mockApi.post.mockResolvedValue({ data: null })

      await watchlistService.addToList(10)

      expect(mockApi.post).toHaveBeenCalledWith('/watchlist', { video_id: 10 })
    })

    it('should handle video already in watchlist', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 409, data: { detail: 'Video already in watchlist' } },
      })

      await expect(watchlistService.addToList(10)).rejects.toMatchObject({
        response: { status: 409 },
      })
    })

    it('should handle video not found', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 404, data: { detail: 'Video not found' } },
      })

      await expect(watchlistService.addToList(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })

    it('should require authentication', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(watchlistService.addToList(10)).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('removeFromList', () => {
    it('should remove video from watchlist', async () => {
      mockApi.delete.mockResolvedValue({ data: null })

      await watchlistService.removeFromList(10)

      expect(mockApi.delete).toHaveBeenCalledWith('/watchlist/10')
    })

    it('should handle video not in watchlist', async () => {
      mockApi.delete.mockRejectedValue({
        response: { status: 404, data: { detail: 'Video not in watchlist' } },
      })

      await expect(watchlistService.removeFromList(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })

    it('should require authentication', async () => {
      mockApi.delete.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(watchlistService.removeFromList(10)).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('checkStatus', () => {
    it('should check if video is in watchlist', async () => {
      mockApi.get.mockResolvedValue({
        data: { in_watchlist: true, watchlist_id: 5 },
      })

      const result = await watchlistService.checkStatus(10)

      expect(mockApi.get).toHaveBeenCalledWith('/watchlist/check/10')
      expect(result.in_watchlist).toBe(true)
      expect(result.watchlist_id).toBe(5)
    })

    it('should return false for video not in watchlist', async () => {
      mockApi.get.mockResolvedValue({
        data: { in_watchlist: false, watchlist_id: null },
      })

      const result = await watchlistService.checkStatus(999)

      expect(result.in_watchlist).toBe(false)
      expect(result.watchlist_id).toBeNull()
    })

    it('should handle unauthorized requests', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(watchlistService.checkStatus(10)).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('reorder', () => {
    it('should reorder watchlist items', async () => {
      mockApi.put.mockResolvedValue({ data: null })

      await watchlistService.reorder([20, 10, 30])

      expect(mockApi.put).toHaveBeenCalledWith('/watchlist/reorder', {
        video_ids: [20, 10, 30],
      })
    })

    it('should handle empty video IDs array', async () => {
      mockApi.put.mockResolvedValue({ data: null })

      await watchlistService.reorder([])

      expect(mockApi.put).toHaveBeenCalledWith('/watchlist/reorder', {
        video_ids: [],
      })
    })

    it('should handle invalid video IDs', async () => {
      mockApi.put.mockRejectedValue({
        response: { status: 400, data: { detail: 'Invalid video IDs' } },
      })

      await expect(watchlistService.reorder([999, 1000])).rejects.toMatchObject({
        response: { status: 400 },
      })
    })

    it('should require authentication', async () => {
      mockApi.put.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(watchlistService.reorder([10, 20])).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('clearAll', () => {
    it('should clear entire watchlist', async () => {
      mockApi.delete.mockResolvedValue({ data: null })

      await watchlistService.clearAll()

      expect(mockApi.delete).toHaveBeenCalledWith('/watchlist')
    })

    it('should handle empty watchlist', async () => {
      mockApi.delete.mockResolvedValue({ data: null })

      await watchlistService.clearAll()

      expect(mockApi.delete).toHaveBeenCalledWith('/watchlist')
    })

    it('should require authentication', async () => {
      mockApi.delete.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(watchlistService.clearAll()).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })
})
