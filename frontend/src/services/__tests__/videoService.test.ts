/**
 * 视频服务测试
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { videoService } from '../videoService'
import api from '../api'

// Mock api module
vi.mock('../api')

describe('Video Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getVideos', () => {
    it('should fetch videos with default parameters', async () => {
      const mockResponse = {
        data: {
          items: [
            { 
              id: 1, 
              title: 'Test Video 1', 
              slug: 'test-1',
              video_type: 'movie',
              status: 'published',
              view_count: 100,
              average_rating: 8.5,
              like_count: 10,
              favorite_count: 5,
              comment_count: 3,
              rating_count: 20,
              is_featured: false,
              is_recommended: false,
              created_at: '2024-01-01T00:00:00Z'
            },
            { 
              id: 2, 
              title: 'Test Video 2', 
              slug: 'test-2',
              video_type: 'series',
              status: 'published',
              view_count: 200,
              average_rating: 9.0,
              like_count: 20,
              favorite_count: 10,
              comment_count: 5,
              rating_count: 30,
              is_featured: false,
              is_recommended: false,
              created_at: '2024-01-02T00:00:00Z'
            },
          ],
          total: 2,
          page: 1,
          pages: 1,
          page_size: 20,
        },
      }

      mockApi.get.mockResolvedValue(mockResponse)

      const result = await videoService.getVideos()

      expect(mockApi.get).toHaveBeenCalledWith('/videos', { params: undefined })
      expect(result.items).toHaveLength(2)
      expect(result.total).toBe(2)
    })

    it('should fetch videos with custom parameters', async () => {
      const mockResponse = {
        data: {
          items: [],
          total: 0,
          page: 2,
          pages: 5,
          page_size: 10,
        },
      }

      mockApi.get.mockResolvedValue(mockResponse)

      const params = {
        page: 2,
        page_size: 10,
        video_type: 'movie',
        category_id: 5,
        year: 2024,
        sort_by: 'rating',
      }

      await videoService.getVideos(params)

      expect(mockApi.get).toHaveBeenCalledWith('/videos', { params })
    })

    it('should handle API errors', async () => {
      mockApi.get.mockRejectedValue(new Error('Network error'))

      await expect(videoService.getVideos()).rejects.toThrow('Network error')
    })
  })

  describe('getVideo', () => {
    it('should fetch single video by id', async () => {
      const mockVideo = {
        id: 1,
        title: 'Test Video',
        slug: 'test-video',
        description: 'Test description',
        duration: 120,
        video_type: 'movie',
        status: 'published',
        view_count: 100,
        average_rating: 8.5,
        like_count: 10,
        favorite_count: 5,
        comment_count: 3,
        rating_count: 20,
        is_featured: false,
        is_recommended: false,
        created_at: '2024-01-01T00:00:00Z'
      }

      mockApi.get.mockResolvedValue({ data: mockVideo })

      const result = await videoService.getVideo(1)

      expect(mockApi.get).toHaveBeenCalledWith('/videos/1')
      expect(result.id).toBe(1)
      expect(result.title).toBe('Test Video')
    })

    it('should throw error for non-existent video', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 404, data: { detail: 'Video not found' } },
      })

      await expect(videoService.getVideo(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })
  })

  describe('getTrendingVideos', () => {
    it('should fetch trending videos with default time range', async () => {
      const mockResponse = {
        data: {
          items: [
            { 
              id: 1, 
              title: 'Trending 1', 
              slug: 'trending-1',
              video_type: 'movie',
              status: 'published',
              view_count: 1000,
              average_rating: 8.5,
              like_count: 50,
              favorite_count: 30,
              comment_count: 20,
              rating_count: 100,
              is_featured: true,
              is_recommended: true,
              created_at: '2024-01-01T00:00:00Z'
            },
            { 
              id: 2, 
              title: 'Trending 2', 
              slug: 'trending-2',
              video_type: 'movie',
              status: 'published',
              view_count: 800,
              average_rating: 8.0,
              like_count: 40,
              favorite_count: 25,
              comment_count: 15,
              rating_count: 80,
              is_featured: false,
              is_recommended: true,
              created_at: '2024-01-02T00:00:00Z'
            },
          ],
          total: 2,
          page: 1,
          pages: 1,
          page_size: 20,
        },
      }

      mockApi.get.mockResolvedValue(mockResponse)

      const result = await videoService.getTrendingVideos()

      expect(mockApi.get).toHaveBeenCalledWith('/videos/trending', { params: undefined })
      expect(result.items).toHaveLength(2)
    })

    it('should fetch trending videos with custom time range', async () => {
      const mockResponse = {
        data: {
          items: [],
          total: 0,
          page: 1,
          pages: 0,
          page_size: 10,
        },
      }

      mockApi.get.mockResolvedValue(mockResponse)

      await videoService.getTrendingVideos({ time_range: 'week', page: 1, page_size: 10 })

      expect(mockApi.get).toHaveBeenCalledWith('/videos/trending', {
        params: { time_range: 'week', page: 1, page_size: 10 },
      })
    })

    it('should accept all valid time ranges', async () => {
      mockApi.get.mockResolvedValue({ data: { items: [], total: 0, page: 1, pages: 0, page_size: 20 } })

      const timeRanges: Array<'today' | 'week' | 'all' | 'rising'> = ['today', 'week', 'all', 'rising']

      for (const timeRange of timeRanges) {
        await videoService.getTrendingVideos({ time_range: timeRange })
        expect(mockApi.get).toHaveBeenLastCalledWith('/videos/trending', {
          params: { time_range: timeRange },
        })
      }
    })
  })

  describe('searchVideos', () => {
    it('should search videos by query', async () => {
      const mockResponse = {
        data: {
          items: [{ 
            id: 1, 
            title: 'Search Result',
            slug: 'search-result',
            video_type: 'movie',
            status: 'published',
            view_count: 100,
            average_rating: 8.5,
            like_count: 10,
            favorite_count: 5,
            comment_count: 3,
            rating_count: 20,
            is_featured: false,
            is_recommended: false,
            created_at: '2024-01-01T00:00:00Z'
          }],
          total: 1,
          page: 1,
          pages: 1,
          page_size: 20,
        },
      }

      mockApi.get.mockResolvedValue(mockResponse)

      const result = await videoService.searchVideos('test query')

      expect(mockApi.get).toHaveBeenCalledWith('/search', {
        params: { q: 'test query' },
      })
      expect(result.items).toHaveLength(1)
    })

    it('should search with additional filters', async () => {
      mockApi.get.mockResolvedValue({
        data: { items: [], total: 0, page: 1, pages: 0, page_size: 10 },
      })

      const params = {
        page: 2,
        page_size: 10,
        category_id: 3,
        country_id: 1,
        year: 2023,
        min_rating: 7.5,
        sort_by: 'rating',
      }

      await videoService.searchVideos('action', params)

      expect(mockApi.get).toHaveBeenCalledWith('/search', {
        params: { q: 'action', ...params },
      })
    })

    it('should handle empty search results', async () => {
      mockApi.get.mockResolvedValue({
        data: { items: [], total: 0, page: 1, pages: 0, page_size: 20 },
      })

      const result = await videoService.searchVideos('nonexistent')

      expect(result.items).toHaveLength(0)
      expect(result.total).toBe(0)
    })
  })

  describe('getRecommendedVideos', () => {
    it('should fetch recommended videos with default pagination', async () => {
      const mockResponse = {
        data: {
          items: [
            { 
              id: 1, 
              title: 'Recommended 1',
              slug: 'recommended-1',
              video_type: 'movie',
              status: 'published',
              view_count: 100,
              average_rating: 8.5,
              like_count: 10,
              favorite_count: 5,
              comment_count: 3,
              rating_count: 20,
              is_featured: false,
              is_recommended: true,
              created_at: '2024-01-01T00:00:00Z'
            },
            { 
              id: 2, 
              title: 'Recommended 2',
              slug: 'recommended-2',
              video_type: 'series',
              status: 'published',
              view_count: 200,
              average_rating: 9.0,
              like_count: 20,
              favorite_count: 10,
              comment_count: 5,
              rating_count: 30,
              is_featured: false,
              is_recommended: true,
              created_at: '2024-01-02T00:00:00Z'
            },
          ],
          total: 2,
          page: 1,
          pages: 1,
          page_size: 6,
        },
      }

      mockApi.get.mockResolvedValue(mockResponse)

      const result = await videoService.getRecommendedVideos()

      expect(mockApi.get).toHaveBeenCalledWith('/videos/recommended', {
        params: { page: 1, page_size: 6 },
      })
      expect(result.items).toHaveLength(2)
    })

    it('should fetch recommended videos with custom pagination', async () => {
      mockApi.get.mockResolvedValue({
        data: { items: [], total: 0, page: 2, pages: 3, page_size: 12 },
      })

      await videoService.getRecommendedVideos(2, 12)

      expect(mockApi.get).toHaveBeenCalledWith('/videos/recommended', {
        params: { page: 2, page_size: 12 },
      })
    })
  })

  describe('getFeaturedVideos', () => {
    it('should fetch featured videos', async () => {
      const mockResponse = {
        data: {
          items: [
            { 
              id: 1, 
              title: 'Featured 1', 
              slug: 'featured-1',
              video_type: 'movie',
              status: 'published',
              view_count: 1000,
              average_rating: 9.5,
              like_count: 100,
              favorite_count: 80,
              comment_count: 50,
              rating_count: 200,
              is_featured: true,
              is_recommended: true,
              created_at: '2024-01-01T00:00:00Z'
            },
            { 
              id: 2, 
              title: 'Featured 2', 
              slug: 'featured-2',
              video_type: 'series',
              status: 'published',
              view_count: 800,
              average_rating: 9.0,
              like_count: 80,
              favorite_count: 60,
              comment_count: 40,
              rating_count: 150,
              is_featured: true,
              is_recommended: true,
              created_at: '2024-01-02T00:00:00Z'
            },
          ],
          total: 2,
          page: 1,
          pages: 1,
          page_size: 20,
        },
      }

      mockApi.get.mockResolvedValue(mockResponse)

      const result = await videoService.getFeaturedVideos()

      expect(mockApi.get).toHaveBeenCalledWith('/videos/featured', { params: undefined })
      expect(result.items).toHaveLength(2)
      expect(result.items.every((v) => v.is_featured)).toBe(true)
    })

    it('should fetch featured videos with pagination', async () => {
      mockApi.get.mockResolvedValue({
        data: { items: [], total: 0, page: 2, pages: 5, page_size: 10 },
      })

      await videoService.getFeaturedVideos({ page: 2, page_size: 10 })

      expect(mockApi.get).toHaveBeenCalledWith('/videos/featured', {
        params: { page: 2, page_size: 10 },
      })
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors gracefully', async () => {
      mockApi.get.mockRejectedValue(new Error('Network Error'))

      await expect(videoService.getVideos()).rejects.toThrow('Network Error')
    })

    it('should handle server errors', async () => {
      mockApi.get.mockRejectedValue({
        response: {
          status: 500,
          data: { detail: 'Internal Server Error' },
        },
      })

      await expect(videoService.getVideo(1)).rejects.toMatchObject({
        response: { status: 500 },
      })
    })

    it('should handle validation errors', async () => {
      mockApi.get.mockRejectedValue({
        response: {
          status: 422,
          data: { detail: 'Validation Error' },
        },
      })

      await expect(videoService.searchVideos('')).rejects.toMatchObject({
        response: { status: 422 },
      })
    })
  })
})

