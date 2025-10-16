/**
 * Series Service Tests (Admin)
 * 专辑/系列服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import api from '@/utils/axios'
import seriesService from '../seriesService'
import type {
  SeriesListItem,
  SeriesDetail,
  PaginatedSeriesResponse,
  SeriesCreateRequest,
  SeriesUpdateRequest,
  AddVideosRequest,
  RemoveVideosRequest,
  UpdateVideoOrderRequest,
} from '../seriesService'

// Mock axios module
vi.mock('@/utils/axios')

describe('Series Service (Admin)', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  // Mock data
  const mockSeriesItem: SeriesListItem = {
    id: 1,
    title: 'Test Series',
    description: 'A test series description',
    cover_image: 'https://example.com/cover.jpg',
    type: 'series',
    status: 'published',
    total_episodes: 10,
    total_views: 5000,
    total_favorites: 200,
    is_featured: true,
    created_at: '2024-01-01T00:00:00Z',
  }

  const mockSeriesDetail: SeriesDetail = {
    ...mockSeriesItem,
    display_order: 1,
    updated_at: '2024-01-02T00:00:00Z',
    videos: [
      {
        video_id: 1,
        episode_number: 1,
        title: 'Episode 1',
        poster_url: 'https://example.com/ep1.jpg',
        duration: 1800,
        view_count: 500,
        added_at: '2024-01-01T00:00:00Z',
      },
      {
        video_id: 2,
        episode_number: 2,
        title: 'Episode 2',
        duration: 1900,
        view_count: 450,
        added_at: '2024-01-01T01:00:00Z',
      },
    ],
  }

  describe('getList', () => {
    it('should fetch series list with default parameters', async () => {
      const mockResponse: PaginatedSeriesResponse = {
        items: [mockSeriesItem],
        total: 1,
        page: 1,
        page_size: 20,
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await seriesService.getList({})

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/series', { params: {} })
      expect(result.items).toHaveLength(1)
      expect(result.items[0].title).toBe('Test Series')
    })

    it('should fetch with pagination', async () => {
      mockApi.get.mockResolvedValue({
        data: { items: [], total: 0, page: 2, page_size: 10 },
      })

      await seriesService.getList({ page: 2, page_size: 10 })

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/series', {
        params: { page: 2, page_size: 10 },
      })
    })

    it('should filter by status', async () => {
      mockApi.get.mockResolvedValue({
        data: { items: [mockSeriesItem], total: 1, page: 1, page_size: 20 },
      })

      await seriesService.getList({ status: 'published' })

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/series', {
        params: { status: 'published' },
      })
    })

    it('should filter by type', async () => {
      const types: Array<'series' | 'collection' | 'franchise'> = [
        'series',
        'collection',
        'franchise',
      ]

      for (const type of types) {
        mockApi.get.mockResolvedValue({
          data: { items: [], total: 0, page: 1, page_size: 20 },
        })

        await seriesService.getList({ type })

        expect(mockApi.get).toHaveBeenLastCalledWith('/api/v1/admin/series', {
          params: { type },
        })
      }
    })

    it('should search series', async () => {
      mockApi.get.mockResolvedValue({
        data: { items: [mockSeriesItem], total: 1, page: 1, page_size: 20 },
      })

      await seriesService.getList({ search: 'test' })

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/series', {
        params: { search: 'test' },
      })
    })
  })

  describe('getDetail', () => {
    it('should fetch series detail with videos', async () => {
      mockApi.get.mockResolvedValue({ data: mockSeriesDetail })

      const result = await seriesService.getDetail(1)

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/series/1')
      expect(result.id).toBe(1)
      expect(result.videos).toHaveLength(2)
      expect(result.videos[0].episode_number).toBe(1)
    })

    it('should handle series with no videos', async () => {
      mockApi.get.mockResolvedValue({
        data: { ...mockSeriesDetail, videos: [], total_episodes: 0 },
      })

      const result = await seriesService.getDetail(1)

      expect(result.videos).toHaveLength(0)
    })

    it('should handle 404 errors', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 404, data: { detail: 'Series not found' } },
      })

      await expect(seriesService.getDetail(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })
  })

  describe('create', () => {
    it('should create new series', async () => {
      const createData: SeriesCreateRequest = {
        title: 'New Series',
        description: 'A new series',
        cover_image: 'https://example.com/cover.jpg',
        type: 'series',
        status: 'draft',
        display_order: 1,
        is_featured: false,
      }

      mockApi.post.mockResolvedValue({
        data: { ...mockSeriesDetail, ...createData, id: 2 },
      })

      const result = await seriesService.create(createData)

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/admin/series', createData)
      expect(result.title).toBe('New Series')
      expect(result.status).toBe('draft')
    })

    it('should create minimal series', async () => {
      const minimalData: SeriesCreateRequest = {
        title: 'Minimal Series',
        type: 'collection',
        status: 'draft',
      }

      mockApi.post.mockResolvedValue({
        data: { ...mockSeriesDetail, ...minimalData },
      })

      const result = await seriesService.create(minimalData)

      expect(result.title).toBe('Minimal Series')
    })

    it('should handle validation errors', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 422, data: { detail: 'Title is required' } },
      })

      await expect(
        seriesService.create({
          title: '',
          type: 'series',
          status: 'draft',
        })
      ).rejects.toMatchObject({
        response: { status: 422 },
      })
    })
  })

  describe('update', () => {
    it('should update series', async () => {
      const updateData: SeriesUpdateRequest = {
        title: 'Updated Series Title',
        description: 'Updated description',
        status: 'published',
      }

      mockApi.put.mockResolvedValue({
        data: { ...mockSeriesDetail, ...updateData },
      })

      const result = await seriesService.update(1, updateData)

      expect(mockApi.put).toHaveBeenCalledWith('/api/v1/admin/series/1', updateData)
      expect(result.title).toBe('Updated Series Title')
    })

    it('should update featured status', async () => {
      mockApi.put.mockResolvedValue({
        data: { ...mockSeriesDetail, is_featured: false },
      })

      const result = await seriesService.update(1, { is_featured: false })

      expect(result.is_featured).toBe(false)
    })

    it('should update display order', async () => {
      mockApi.put.mockResolvedValue({
        data: { ...mockSeriesDetail, display_order: 5 },
      })

      const result = await seriesService.update(1, { display_order: 5 })

      expect(result.display_order).toBe(5)
    })
  })

  describe('delete', () => {
    it('should delete series', async () => {
      mockApi.delete.mockResolvedValue({ data: { message: 'Series deleted' } })

      await seriesService.delete(1)

      expect(mockApi.delete).toHaveBeenCalledWith('/api/v1/admin/series/1')
    })

    it('should handle 404 errors', async () => {
      mockApi.delete.mockRejectedValue({
        response: { status: 404 },
      })

      await expect(seriesService.delete(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })
  })

  describe('addVideos', () => {
    it('should add videos to series', async () => {
      const addData: AddVideosRequest = {
        video_ids: [3, 4, 5],
        start_episode_number: 3,
      }

      mockApi.post.mockResolvedValue({
        data: { message: 'Added 3 videos', count: 3 },
      })

      const result = await seriesService.addVideos(1, addData)

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/admin/series/1/videos', addData)
      expect(result.count).toBe(3)
    })

    it('should add videos without episode numbers', async () => {
      mockApi.post.mockResolvedValue({ data: { count: 2 } })

      await seriesService.addVideos(1, { video_ids: [6, 7] })

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/admin/series/1/videos', {
        video_ids: [6, 7],
      })
    })

    it('should handle duplicate videos', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 409, data: { detail: 'Video already in series' } },
      })

      await expect(seriesService.addVideos(1, { video_ids: [1] })).rejects.toMatchObject({
        response: { status: 409 },
      })
    })
  })

  describe('removeVideos', () => {
    it('should remove videos from series', async () => {
      const removeData: RemoveVideosRequest = {
        video_ids: [1, 2],
      }

      mockApi.delete.mockResolvedValue({
        data: { message: 'Removed 2 videos', count: 2 },
      })

      const result = await seriesService.removeVideos(1, removeData)

      expect(mockApi.delete).toHaveBeenCalledWith('/api/v1/admin/series/1/videos', {
        data: removeData,
      })
      expect(result.count).toBe(2)
    })

    it('should handle non-existent videos', async () => {
      mockApi.delete.mockRejectedValue({
        response: { status: 404, data: { detail: 'Video not in series' } },
      })

      await expect(seriesService.removeVideos(1, { video_ids: [999] })).rejects.toMatchObject({
        response: { status: 404 },
      })
    })
  })

  describe('updateVideoOrder', () => {
    it('should update video order', async () => {
      const orderData: UpdateVideoOrderRequest = {
        video_order: [
          { video_id: 2, episode_number: 1 },
          { video_id: 1, episode_number: 2 },
        ],
      }

      mockApi.put.mockResolvedValue({
        data: { message: 'Order updated', count: 2 },
      })

      const result = await seriesService.updateVideoOrder(1, orderData)

      expect(mockApi.put).toHaveBeenCalledWith('/api/v1/admin/series/1/videos/order', orderData)
      expect(result.count).toBe(2)
    })
  })

  describe('getStats', () => {
    it('should fetch series statistics', async () => {
      const mockStats = {
        total_series: 50,
        total_episodes: 500,
        total_views: 100000,
        by_type: { series: 30, collection: 15, franchise: 5 },
        by_status: { published: 40, draft: 8, archived: 2 },
      }

      mockApi.get.mockResolvedValue({ data: mockStats })

      const result = await seriesService.getStats()

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/series/stats')
      expect(result.total_series).toBe(50)
    })
  })

  describe('Batch Operations', () => {
    describe('batchPublish', () => {
      it('should batch publish series', async () => {
        mockApi.post.mockResolvedValue({
          data: { message: 'Published 3 series', count: 3 },
        })

        const result = await seriesService.batchPublish([1, 2, 3])

        expect(mockApi.post).toHaveBeenCalledWith('/api/v1/admin/series/batch/publish', [1, 2, 3])
        expect(result.count).toBe(3)
      })
    })

    describe('batchArchive', () => {
      it('should batch archive series', async () => {
        mockApi.post.mockResolvedValue({ data: { count: 2 } })

        const result = await seriesService.batchArchive([1, 2])

        expect(mockApi.post).toHaveBeenCalledWith('/api/v1/admin/series/batch/archive', [1, 2])
        expect(result.count).toBe(2)
      })
    })

    describe('batchDelete', () => {
      it('should batch delete series', async () => {
        mockApi.post.mockResolvedValue({ data: { count: 5 } })

        const result = await seriesService.batchDelete([1, 2, 3, 4, 5])

        expect(mockApi.post).toHaveBeenCalledWith('/api/v1/admin/series/batch/delete', [
          1, 2, 3, 4, 5,
        ])
        expect(result.count).toBe(5)
      })

      it('should handle partial failures', async () => {
        mockApi.post.mockResolvedValue({
          data: { count: 2, failed: [3], message: 'Deleted 2, failed 1' },
        })

        const result = await seriesService.batchDelete([1, 2, 3])

        expect(result.count).toBe(2)
        expect(result.failed).toEqual([3])
      })
    })

    describe('batchFeature', () => {
      it('should batch set featured status to true', async () => {
        mockApi.post.mockResolvedValue({ data: { count: 3 } })

        const result = await seriesService.batchFeature([1, 2, 3], true)

        expect(mockApi.post).toHaveBeenCalledWith('/api/v1/admin/series/batch/feature', {
          series_ids: [1, 2, 3],
          is_featured: true,
        })
        expect(result.count).toBe(3)
      })

      it('should batch set featured status to false', async () => {
        mockApi.post.mockResolvedValue({ data: { count: 2 } })

        await seriesService.batchFeature([1, 2], false)

        expect(mockApi.post).toHaveBeenCalledWith('/api/v1/admin/series/batch/feature', {
          series_ids: [1, 2],
          is_featured: false,
        })
      })
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockApi.get.mockRejectedValue(new Error('Network error'))

      await expect(seriesService.getList({})).rejects.toThrow('Network error')
    })

    it('should handle 401 unauthorized', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(seriesService.getDetail(1)).rejects.toMatchObject({
        response: { status: 401 },
      })
    })

    it('should handle 500 server errors', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 500, data: { detail: 'Internal Server Error' } },
      })

      await expect(
        seriesService.create({
          title: 'Test',
          type: 'series',
          status: 'draft',
        })
      ).rejects.toMatchObject({
        response: { status: 500 },
      })
    })
  })

  describe('Edge Cases', () => {
    it('should handle very long titles', async () => {
      const longTitle = 'A'.repeat(500)

      mockApi.post.mockResolvedValue({
        data: { ...mockSeriesDetail, title: longTitle },
      })

      const result = await seriesService.create({
        title: longTitle,
        type: 'series',
        status: 'draft',
      })

      expect(result.title.length).toBe(500)
    })

    it('should handle series with hundreds of videos', async () => {
      const manyVideos = Array.from({ length: 200 }, (_, i) => ({
        video_id: i + 1,
        episode_number: i + 1,
        title: `Episode ${i + 1}`,
        view_count: 100,
        added_at: '2024-01-01T00:00:00Z',
      }))

      mockApi.get.mockResolvedValue({
        data: { ...mockSeriesDetail, videos: manyVideos, total_episodes: 200 },
      })

      const result = await seriesService.getDetail(1)

      expect(result.videos).toHaveLength(200)
    })

    it('should handle empty batch operations', async () => {
      mockApi.post.mockResolvedValue({ data: { count: 0 } })

      const result = await seriesService.batchPublish([])

      expect(result.count).toBe(0)
    })

    it('should handle special characters in title', async () => {
      const specialTitle = 'Series™ & Friends © 2024: "The Journey"'

      mockApi.post.mockResolvedValue({
        data: { ...mockSeriesDetail, title: specialTitle },
      })

      const result = await seriesService.create({
        title: specialTitle,
        type: 'series',
        status: 'draft',
      })

      expect(result.title).toBe(specialTitle)
    })
  })
})
