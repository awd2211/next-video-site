/**
 * Video Service Tests (Admin Frontend)
 * 管理后台视频服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import api from '@/utils/axios'
import videoService, { type Video, type PaginatedVideoResponse } from '../videoService'

// Mock axios module
vi.mock('@/utils/axios')

describe('Video Service (Admin)', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  // Mock video data
  const mockVideo: Video = {
    id: 1,
    title: 'Test Video',
    description: 'Test description',
    video_url: 'https://example.com/video.mp4',
    poster_url: 'https://example.com/poster.jpg',
    backdrop_url: 'https://example.com/backdrop.jpg',
    duration: 120,
    view_count: 1000,
    rating: 8.5,
    status: 'published',
    created_at: '2024-01-01T00:00:00Z',
  }

  describe('getList', () => {
    it('should fetch video list with default parameters', async () => {
      const mockResponse: PaginatedVideoResponse = {
        items: [mockVideo],
        total: 1,
        page: 1,
        page_size: 20,
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await videoService.getList()

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/videos', { params: undefined })
      expect(result.items).toHaveLength(1)
      expect(result.total).toBe(1)
      expect(result.items[0].title).toBe('Test Video')
    })

    it('should fetch video list with custom parameters', async () => {
      const mockResponse: PaginatedVideoResponse = {
        items: [],
        total: 0,
        page: 2,
        page_size: 10,
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const params = {
        page: 2,
        page_size: 10,
        status: 'draft',
        search: 'test',
      }

      await videoService.getList(params)

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/videos', { params })
    })

    it('should filter by status', async () => {
      const mockResponse: PaginatedVideoResponse = {
        items: [mockVideo],
        total: 1,
        page: 1,
        page_size: 20,
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      await videoService.getList({ status: 'published' })

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/videos', {
        params: { status: 'published' },
      })
    })

    it('should search videos by query', async () => {
      const mockResponse: PaginatedVideoResponse = {
        items: [mockVideo],
        total: 1,
        page: 1,
        page_size: 20,
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      await videoService.getList({ search: 'test query' })

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/videos', {
        params: { search: 'test query' },
      })
    })

    it('should handle pagination', async () => {
      const mockResponse: PaginatedVideoResponse = {
        items: [],
        total: 50,
        page: 3,
        page_size: 15,
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      await videoService.getList({ page: 3, page_size: 15 })

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/videos', {
        params: { page: 3, page_size: 15 },
      })
    })

    it('should handle empty video list', async () => {
      const mockResponse: PaginatedVideoResponse = {
        items: [],
        total: 0,
        page: 1,
        page_size: 20,
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await videoService.getList()

      expect(result.items).toHaveLength(0)
      expect(result.total).toBe(0)
    })

    it('should handle API errors', async () => {
      mockApi.get.mockRejectedValue(new Error('Network error'))

      await expect(videoService.getList()).rejects.toThrow('Network error')
    })
  })

  describe('getDetail', () => {
    it('should fetch single video by id', async () => {
      mockApi.get.mockResolvedValue({ data: mockVideo })

      const result = await videoService.getDetail(1)

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/videos/1')
      expect(result.id).toBe(1)
      expect(result.title).toBe('Test Video')
      expect(result.video_url).toBe('https://example.com/video.mp4')
    })

    it('should fetch video with all fields', async () => {
      mockApi.get.mockResolvedValue({ data: mockVideo })

      const result = await videoService.getDetail(1)

      expect(result).toMatchObject({
        id: 1,
        title: 'Test Video',
        description: 'Test description',
        video_url: 'https://example.com/video.mp4',
        poster_url: 'https://example.com/poster.jpg',
        backdrop_url: 'https://example.com/backdrop.jpg',
        duration: 120,
        view_count: 1000,
        rating: 8.5,
        status: 'published',
      })
    })

    it('should handle video with minimal fields', async () => {
      const minimalVideo: Video = {
        id: 2,
        title: 'Minimal Video',
        video_url: 'https://example.com/minimal.mp4',
        view_count: 0,
        status: 'draft',
        created_at: '2024-01-01T00:00:00Z',
      }

      mockApi.get.mockResolvedValue({ data: minimalVideo })

      const result = await videoService.getDetail(2)

      expect(result.id).toBe(2)
      expect(result.description).toBeUndefined()
      expect(result.poster_url).toBeUndefined()
      expect(result.rating).toBeUndefined()
    })

    it('should throw error for non-existent video', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 404, data: { detail: 'Video not found' } },
      })

      await expect(videoService.getDetail(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })

    it('should handle large video IDs', async () => {
      const largeId = 999999999

      mockApi.get.mockResolvedValue({
        data: { ...mockVideo, id: largeId },
      })

      const result = await videoService.getDetail(largeId)

      expect(mockApi.get).toHaveBeenCalledWith(`/api/v1/admin/videos/${largeId}`)
      expect(result.id).toBe(largeId)
    })

    it('should handle API errors', async () => {
      mockApi.get.mockRejectedValue(new Error('Network error'))

      await expect(videoService.getDetail(1)).rejects.toThrow('Network error')
    })
  })

  describe('search', () => {
    it('should search videos by query', async () => {
      const mockResponse: PaginatedVideoResponse = {
        items: [mockVideo],
        total: 1,
        page: 1,
        page_size: 20,
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await videoService.search('test query')

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/videos', {
        params: { search: 'test query' },
      })
      expect(result.items).toHaveLength(1)
    })

    it('should search with pagination parameters', async () => {
      const mockResponse: PaginatedVideoResponse = {
        items: [],
        total: 0,
        page: 2,
        page_size: 10,
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      await videoService.search('action', { page: 2, page_size: 10 })

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/videos', {
        params: { search: 'action', page: 2, page_size: 10 },
      })
    })

    it('should handle empty search query', async () => {
      const mockResponse: PaginatedVideoResponse = {
        items: [mockVideo],
        total: 1,
        page: 1,
        page_size: 20,
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      await videoService.search('')

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/videos', {
        params: { search: '' },
      })
    })

    it('should handle empty search results', async () => {
      const mockResponse: PaginatedVideoResponse = {
        items: [],
        total: 0,
        page: 1,
        page_size: 20,
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await videoService.search('nonexistent')

      expect(result.items).toHaveLength(0)
      expect(result.total).toBe(0)
    })

    it('should handle special characters in search query', async () => {
      const specialQuery = 'test & special <characters> "quotes"'
      const mockResponse: PaginatedVideoResponse = {
        items: [],
        total: 0,
        page: 1,
        page_size: 20,
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      await videoService.search(specialQuery)

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/videos', {
        params: { search: specialQuery },
      })
    })

    it('should handle API errors', async () => {
      mockApi.get.mockRejectedValue(new Error('Search failed'))

      await expect(videoService.search('test')).rejects.toThrow('Search failed')
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockApi.get.mockRejectedValue(new Error('Network Error'))

      await expect(videoService.getList()).rejects.toThrow('Network Error')
    })

    it('should handle server errors', async () => {
      mockApi.get.mockRejectedValue({
        response: {
          status: 500,
          data: { detail: 'Internal Server Error' },
        },
      })

      await expect(videoService.getDetail(1)).rejects.toMatchObject({
        response: { status: 500 },
      })
    })

    it('should handle unauthorized access', async () => {
      mockApi.get.mockRejectedValue({
        response: {
          status: 401,
          data: { detail: 'Unauthorized' },
        },
      })

      await expect(videoService.getList()).rejects.toMatchObject({
        response: { status: 401 },
      })
    })

    it('should handle forbidden access', async () => {
      mockApi.get.mockRejectedValue({
        response: {
          status: 403,
          data: { detail: 'Forbidden' },
        },
      })

      await expect(videoService.getDetail(1)).rejects.toMatchObject({
        response: { status: 403 },
      })
    })

    it('should handle validation errors', async () => {
      mockApi.get.mockRejectedValue({
        response: {
          status: 422,
          data: { detail: 'Validation Error' },
        },
      })

      await expect(videoService.getList()).rejects.toMatchObject({
        response: { status: 422 },
      })
    })
  })

  describe('Edge Cases', () => {
    it('should handle videos with different statuses', async () => {
      const statuses = ['draft', 'published', 'archived', 'pending']

      for (const status of statuses) {
        const video = { ...mockVideo, status }
        mockApi.get.mockResolvedValue({ data: video })

        const result = await videoService.getDetail(1)

        expect(result.status).toBe(status)
      }
    })

    it('should handle videos with zero views', async () => {
      const videoWithNoViews = { ...mockVideo, view_count: 0 }

      mockApi.get.mockResolvedValue({ data: videoWithNoViews })

      const result = await videoService.getDetail(1)

      expect(result.view_count).toBe(0)
    })

    it('should handle videos with no rating', async () => {
      const videoWithoutRating = { ...mockVideo, rating: undefined }

      mockApi.get.mockResolvedValue({ data: videoWithoutRating })

      const result = await videoService.getDetail(1)

      expect(result.rating).toBeUndefined()
    })

    it('should handle very long video titles', async () => {
      const longTitle = 'A'.repeat(500)
      const videoWithLongTitle = { ...mockVideo, title: longTitle }

      mockApi.get.mockResolvedValue({ data: videoWithLongTitle })

      const result = await videoService.getDetail(1)

      expect(result.title).toBe(longTitle)
      expect(result.title.length).toBe(500)
    })

    it('should handle pagination edge cases - first page', async () => {
      const mockResponse: PaginatedVideoResponse = {
        items: [mockVideo],
        total: 100,
        page: 1,
        page_size: 20,
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await videoService.getList({ page: 1 })

      expect(result.page).toBe(1)
    })

    it('should handle pagination edge cases - last page with partial results', async () => {
      const mockResponse: PaginatedVideoResponse = {
        items: [mockVideo, { ...mockVideo, id: 2 }],
        total: 42,
        page: 5,
        page_size: 10,
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await videoService.getList({ page: 5, page_size: 10 })

      expect(result.page).toBe(5)
      expect(result.items).toHaveLength(2)
    })

    it('should handle combined filters', async () => {
      const mockResponse: PaginatedVideoResponse = {
        items: [],
        total: 0,
        page: 1,
        page_size: 20,
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const params = {
        page: 1,
        page_size: 20,
        status: 'published',
        search: 'action movies',
      }

      await videoService.getList(params)

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/videos', { params })
    })
  })
})
