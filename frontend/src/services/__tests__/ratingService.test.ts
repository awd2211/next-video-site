/**
 * 评分服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ratingService } from '../ratingService'
import api from '../api'

vi.mock('../api')

describe('Rating Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('rateVideo', () => {
    it('should rate video with valid score', async () => {
      const mockResponse = {
        id: 1,
        video_id: 10,
        user_id: 1,
        score: 8.5,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: null,
      }

      mockApi.post.mockResolvedValue({ data: mockResponse })

      const result = await ratingService.rateVideo(10, 8.5)

      expect(mockApi.post).toHaveBeenCalledWith('/ratings/', {
        video_id: 10,
        score: 8.5,
      })
      expect(result.score).toBe(8.5)
    })

    it('should update existing rating', async () => {
      const mockResponse = {
        id: 1,
        video_id: 10,
        user_id: 1,
        score: 9.0,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
      }

      mockApi.post.mockResolvedValue({ data: mockResponse })

      const result = await ratingService.rateVideo(10, 9.0)

      expect(result.score).toBe(9.0)
      expect(result.updated_at).not.toBeNull()
    })

    it('should handle invalid score', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 422, data: { detail: 'Score must be between 0 and 10' } },
      })

      await expect(ratingService.rateVideo(10, 15)).rejects.toMatchObject({
        response: { status: 422 },
      })
    })

    it('should require authentication', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(ratingService.rateVideo(10, 8.0)).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('getVideoRatingStats', () => {
    it('should get rating statistics', async () => {
      const mockStats = {
        video_id: 10,
        average_rating: 8.5,
        rating_count: 100,
        user_rating: 9.0,
      }

      mockApi.get.mockResolvedValue({ data: mockStats })

      const result = await ratingService.getVideoRatingStats(10)

      expect(mockApi.get).toHaveBeenCalledWith('/ratings/video/10/stats')
      expect(result.average_rating).toBe(8.5)
      expect(result.rating_count).toBe(100)
      expect(result.user_rating).toBe(9.0)
    })

    it('should return null user_rating when not rated', async () => {
      const mockStats = {
        video_id: 10,
        average_rating: 7.5,
        rating_count: 50,
        user_rating: null,
      }

      mockApi.get.mockResolvedValue({ data: mockStats })

      const result = await ratingService.getVideoRatingStats(10)

      expect(result.user_rating).toBeNull()
    })

    it('should handle video with no ratings', async () => {
      const mockStats = {
        video_id: 999,
        average_rating: 0,
        rating_count: 0,
        user_rating: null,
      }

      mockApi.get.mockResolvedValue({ data: mockStats })

      const result = await ratingService.getVideoRatingStats(999)

      expect(result.rating_count).toBe(0)
      expect(result.average_rating).toBe(0)
    })
  })

  describe('getMyRating', () => {
    it('should get user\'s rating for video', async () => {
      const mockRating = {
        id: 1,
        video_id: 10,
        user_id: 1,
        score: 8.5,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: null,
      }

      mockApi.get.mockResolvedValue({ data: mockRating })

      const result = await ratingService.getMyRating(10)

      expect(mockApi.get).toHaveBeenCalledWith('/ratings/video/10/my-rating')
      expect(result).not.toBeNull()
      expect(result?.score).toBe(8.5)
    })

    it('should return null when not rated', async () => {
      mockApi.get.mockResolvedValue({ data: null })

      const result = await ratingService.getMyRating(999)

      expect(result).toBeNull()
    })

    it('should require authentication', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(ratingService.getMyRating(10)).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('deleteRating', () => {
    it('should delete rating', async () => {
      mockApi.delete.mockResolvedValue({ data: null })

      await ratingService.deleteRating(10)

      expect(mockApi.delete).toHaveBeenCalledWith('/ratings/video/10')
    })

    it('should handle non-existent rating', async () => {
      mockApi.delete.mockRejectedValue({
        response: { status: 404, data: { detail: 'Rating not found' } },
      })

      await expect(ratingService.deleteRating(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })

    it('should require authentication', async () => {
      mockApi.delete.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(ratingService.deleteRating(10)).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })
})

