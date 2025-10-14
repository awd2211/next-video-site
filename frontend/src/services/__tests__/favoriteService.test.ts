/**
 * 收藏服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { favoriteService } from '../favoriteService'
import api from '../api'

vi.mock('../api')

describe('Favorite Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('addFavorite', () => {
    it('should add video to favorites without folder', async () => {
      const mockResponse = {
        id: 1,
        user_id: 1,
        video_id: 10,
        created_at: '2024-01-01T00:00:00Z',
        video: { id: 10, title: 'Test Video' },
      }

      mockApi.post.mockResolvedValue({ data: mockResponse })

      const result = await favoriteService.addFavorite(10)

      expect(mockApi.post).toHaveBeenCalledWith('/favorites/', {
        video_id: 10,
        folder_id: undefined,
      })
      expect(result.video_id).toBe(10)
    })

    it('should add video to specific folder', async () => {
      const mockResponse = {
        id: 2,
        user_id: 1,
        video_id: 10,
        folder_id: 5,
        created_at: '2024-01-01T00:00:00Z',
        video: { id: 10, title: 'Test Video' },
      }

      mockApi.post.mockResolvedValue({ data: mockResponse })

      const result = await favoriteService.addFavorite(10, 5)

      expect(mockApi.post).toHaveBeenCalledWith('/favorites/', {
        video_id: 10,
        folder_id: 5,
      })
      expect(result.folder_id).toBe(5)
    })

    it('should handle already favorited', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 409, data: { detail: 'Already favorited' } },
      })

      await expect(favoriteService.addFavorite(10)).rejects.toMatchObject({
        response: { status: 409 },
      })
    })

    it('should require authentication', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(favoriteService.addFavorite(10)).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('removeFavorite', () => {
    it('should remove video from favorites', async () => {
      mockApi.delete.mockResolvedValue({ data: null })

      await favoriteService.removeFavorite(10)

      expect(mockApi.delete).toHaveBeenCalledWith('/favorites/10')
    })

    it('should handle not favorited', async () => {
      mockApi.delete.mockRejectedValue({
        response: { status: 404, data: { detail: 'Not in favorites' } },
      })

      await expect(favoriteService.removeFavorite(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })
  })

  describe('getFavorites', () => {
    it('should fetch favorites with default pagination', async () => {
      const mockResponse = {
        total: 2,
        page: 1,
        page_size: 20,
        items: [
          {
            id: 1,
            user_id: 1,
            video_id: 10,
            created_at: '2024-01-01T00:00:00Z',
            video: { id: 10, title: 'Video 1' },
          },
          {
            id: 2,
            user_id: 1,
            video_id: 20,
            created_at: '2024-01-02T00:00:00Z',
            video: { id: 20, title: 'Video 2' },
          },
        ],
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await favoriteService.getFavorites()

      expect(mockApi.get).toHaveBeenCalledWith('/favorites/', {
        params: { page: 1, page_size: 20 },
      })
      expect(result.items).toHaveLength(2)
    })

    it('should fetch favorites with custom pagination', async () => {
      mockApi.get.mockResolvedValue({
        data: { total: 0, page: 2, page_size: 10, items: [] },
      })

      await favoriteService.getFavorites(2, 10)

      expect(mockApi.get).toHaveBeenCalledWith('/favorites/', {
        params: { page: 2, page_size: 10 },
      })
    })

    it('should handle empty favorites', async () => {
      mockApi.get.mockResolvedValue({
        data: { total: 0, page: 1, page_size: 20, items: [] },
      })

      const result = await favoriteService.getFavorites()

      expect(result.items).toHaveLength(0)
      expect(result.total).toBe(0)
    })
  })

  describe('checkFavorite', () => {
    it('should return true for favorited video', async () => {
      mockApi.get.mockResolvedValue({ data: { is_favorited: true } })

      const result = await favoriteService.checkFavorite(10)

      expect(mockApi.get).toHaveBeenCalledWith('/favorites/check/10')
      expect(result).toBe(true)
    })

    it('should return false for non-favorited video', async () => {
      mockApi.get.mockResolvedValue({ data: { is_favorited: false } })

      const result = await favoriteService.checkFavorite(999)

      expect(result).toBe(false)
    })

    it('should handle unauthorized request', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(favoriteService.checkFavorite(10)).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })
})

