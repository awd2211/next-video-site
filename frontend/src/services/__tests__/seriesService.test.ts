/**
 * 系列服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import seriesService from '../seriesService'
import api from '../api'

vi.mock('../api')

describe('Series Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getList', () => {
    it('should fetch series list with default parameters', async () => {
      const mockResponse = {
        total: 2,
        page: 1,
        page_size: 20,
        pages: 1,
        items: [
          {
            id: 1,
            title: 'Series 1',
            description: 'Description 1',
            cover_image: 'cover1.jpg',
            type: 'series',
            status: 'published',
            total_episodes: 10,
            total_views: 1000,
            total_favorites: 50,
            is_featured: true,
            created_at: '2024-01-01',
          },
        ],
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await seriesService.getList({})

      expect(mockApi.get).toHaveBeenCalledWith('/series', { params: {} })
      expect(result.items).toHaveLength(1)
    })

    it('should fetch series with filters', async () => {
      mockApi.get.mockResolvedValue({
        data: { total: 0, page: 1, page_size: 10, pages: 0, items: [] },
      })

      const params = {
        page: 2,
        page_size: 10,
        type: 'collection' as const,
        is_featured: true,
      }

      await seriesService.getList(params)

      expect(mockApi.get).toHaveBeenCalledWith('/series', { params })
    })
  })

  describe('getDetail', () => {
    it('should fetch series detail', async () => {
      const mockSeries = {
        id: 1,
        title: 'MCU Phase 4',
        description: 'Marvel Cinematic Universe Phase 4',
        cover_image: 'mcu.jpg',
        type: 'franchise',
        status: 'published',
        total_episodes: 15,
        total_views: 1000000,
        total_favorites: 5000,
        is_featured: true,
        created_at: '2024-01-01',
        display_order: 1,
        updated_at: '2024-01-10',
        videos: [
          {
            video_id: 1,
            episode_number: 1,
            title: 'Movie 1',
            poster_url: 'poster1.jpg',
            duration: 7200,
            view_count: 50000,
            added_at: '2024-01-01',
          },
        ],
      }

      mockApi.get.mockResolvedValue({ data: mockSeries })

      const result = await seriesService.getDetail(1)

      expect(mockApi.get).toHaveBeenCalledWith('/series/1')
      expect(result.title).toBe('MCU Phase 4')
      expect(result.videos).toHaveLength(1)
    })

    it('should handle series not found', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 404, data: { detail: 'Series not found' } },
      })

      await expect(seriesService.getDetail(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })
  })

  describe('getFeatured', () => {
    it('should fetch featured series with default limit', async () => {
      const mockFeatured = [
        {
          id: 1,
          title: 'Featured 1',
          type: 'series',
          status: 'published',
          total_episodes: 12,
          total_views: 10000,
          total_favorites: 500,
          is_featured: true,
          created_at: '2024-01-01',
        },
        {
          id: 2,
          title: 'Featured 2',
          type: 'collection',
          status: 'published',
          total_episodes: 8,
          total_views: 8000,
          total_favorites: 300,
          is_featured: true,
          created_at: '2024-01-02',
        },
      ]

      mockApi.get.mockResolvedValue({ data: mockFeatured })

      const result = await seriesService.getFeatured()

      expect(mockApi.get).toHaveBeenCalledWith('/series/featured/list', {
        params: { limit: 10 },
      })
      expect(result).toHaveLength(2)
      expect(result.every((s) => s.is_featured)).toBe(true)
    })

    it('should fetch featured series with custom limit', async () => {
      mockApi.get.mockResolvedValue({ data: [] })

      await seriesService.getFeatured(5)

      expect(mockApi.get).toHaveBeenCalledWith('/series/featured/list', {
        params: { limit: 5 },
      })
    })

    it('should handle no featured series', async () => {
      mockApi.get.mockResolvedValue({ data: [] })

      const result = await seriesService.getFeatured()

      expect(result).toHaveLength(0)
    })
  })
})

