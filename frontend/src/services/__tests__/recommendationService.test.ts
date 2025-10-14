/**
 * 推荐服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { recommendationService } from '../recommendationService'
import api from '../api'

vi.mock('../api')

describe('Recommendation Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getPersonalizedRecommendations', () => {
    it('should get personalized recommendations with default limit', async () => {
      const mockVideos = [
        { id: 1, title: 'Recommended Video 1', poster_url: 'poster1.jpg' },
        { id: 2, title: 'Recommended Video 2', poster_url: 'poster2.jpg' },
      ]

      mockApi.get.mockResolvedValue({ data: mockVideos })

      const result = await recommendationService.getPersonalizedRecommendations()

      expect(mockApi.get).toHaveBeenCalledWith('/recommendations/personalized', {
        params: { limit: 20 },
      })
      expect(result).toHaveLength(2)
      expect(result[0].title).toBe('Recommended Video 1')
    })

    it('should get personalized recommendations with custom limit', async () => {
      mockApi.get.mockResolvedValue({ data: [] })

      await recommendationService.getPersonalizedRecommendations(10)

      expect(mockApi.get).toHaveBeenCalledWith('/recommendations/personalized', {
        params: { limit: 10 },
      })
    })

    it('should exclude specified video IDs', async () => {
      mockApi.get.mockResolvedValue({ data: [] })

      await recommendationService.getPersonalizedRecommendations(15, [1, 2, 3])

      expect(mockApi.get).toHaveBeenCalledWith('/recommendations/personalized', {
        params: { limit: 15, exclude_ids: '1,2,3' },
      })
    })

    it('should handle empty exclude IDs array', async () => {
      mockApi.get.mockResolvedValue({ data: [] })

      await recommendationService.getPersonalizedRecommendations(20, [])

      expect(mockApi.get).toHaveBeenCalledWith('/recommendations/personalized', {
        params: { limit: 20 },
      })
    })

    it('should handle API errors', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 500, data: { detail: 'Server error' } },
      })

      await expect(recommendationService.getPersonalizedRecommendations()).rejects.toMatchObject({
        response: { status: 500 },
      })
    })

    it('should handle unauthorized requests gracefully', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(recommendationService.getPersonalizedRecommendations()).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('getSimilarVideos', () => {
    it('should get similar videos with default limit', async () => {
      const mockSimilarVideos = [
        { id: 2, title: 'Similar Video 1', poster_url: 'similar1.jpg' },
        { id: 3, title: 'Similar Video 2', poster_url: 'similar2.jpg' },
      ]

      mockApi.get.mockResolvedValue({ data: mockSimilarVideos })

      const result = await recommendationService.getSimilarVideos(1)

      expect(mockApi.get).toHaveBeenCalledWith('/recommendations/similar/1', {
        params: { limit: 10 },
      })
      expect(result).toHaveLength(2)
      expect(result[0].title).toBe('Similar Video 1')
    })

    it('should get similar videos with custom limit', async () => {
      mockApi.get.mockResolvedValue({ data: [] })

      await recommendationService.getSimilarVideos(1, 5)

      expect(mockApi.get).toHaveBeenCalledWith('/recommendations/similar/1', {
        params: { limit: 5 },
      })
    })

    it('should handle video not found', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 404, data: { detail: 'Video not found' } },
      })

      await expect(recommendationService.getSimilarVideos(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })

    it('should handle empty similar videos', async () => {
      mockApi.get.mockResolvedValue({ data: [] })

      const result = await recommendationService.getSimilarVideos(1)

      expect(result).toHaveLength(0)
    })
  })

  describe('getForYouRecommendations', () => {
    it('should get for-you recommendations with default limit', async () => {
      const mockForYouVideos = [
        { id: 10, title: 'For You Video 1', poster_url: 'foryou1.jpg' },
        { id: 11, title: 'For You Video 2', poster_url: 'foryou2.jpg' },
        { id: 12, title: 'For You Video 3', poster_url: 'foryou3.jpg' },
      ]

      mockApi.get.mockResolvedValue({ data: mockForYouVideos })

      const result = await recommendationService.getForYouRecommendations()

      expect(mockApi.get).toHaveBeenCalledWith('/recommendations/for-you', {
        params: { limit: 20 },
      })
      expect(result).toHaveLength(3)
      expect(result[0].title).toBe('For You Video 1')
    })

    it('should get for-you recommendations with custom limit', async () => {
      mockApi.get.mockResolvedValue({ data: [] })

      await recommendationService.getForYouRecommendations(8)

      expect(mockApi.get).toHaveBeenCalledWith('/recommendations/for-you', {
        params: { limit: 8 },
      })
    })

    it('should handle empty recommendations', async () => {
      mockApi.get.mockResolvedValue({ data: [] })

      const result = await recommendationService.getForYouRecommendations()

      expect(result).toHaveLength(0)
    })

    it('should handle network errors', async () => {
      mockApi.get.mockRejectedValue(new Error('Network error'))

      await expect(recommendationService.getForYouRecommendations()).rejects.toThrow(
        'Network error'
      )
    })

    it('should handle server errors', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 503, data: { detail: 'Service unavailable' } },
      })

      await expect(recommendationService.getForYouRecommendations()).rejects.toMatchObject({
        response: { status: 503 },
      })
    })
  })
})
