/**
 * 导演服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { directorService } from '../directorService'
import api from '../api'

vi.mock('../api')

describe('Director Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getDirectors', () => {
    it('should fetch directors with default parameters', async () => {
      const mockResponse = {
        total: 2,
        page: 1,
        page_size: 20,
        items: [
          { id: 1, name: 'Director 1', avatar: null, biography: null, birth_date: null, country_id: null, created_at: '2024-01-01' },
          { id: 2, name: 'Director 2', avatar: 'avatar.jpg', biography: 'Bio', birth_date: '1970-01-01', country_id: 1, created_at: '2024-01-02' },
        ],
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await directorService.getDirectors()

      expect(mockApi.get).toHaveBeenCalledWith('/directors/', {
        params: { page: 1, page_size: 20, search: '' },
      })
      expect(result.items).toHaveLength(2)
    })

    it('should fetch directors with custom pagination', async () => {
      mockApi.get.mockResolvedValue({
        data: { total: 0, page: 2, page_size: 10, items: [] },
      })

      await directorService.getDirectors(2, 10)

      expect(mockApi.get).toHaveBeenCalledWith('/directors/', {
        params: { page: 2, page_size: 10, search: '' },
      })
    })

    it('should search directors by name', async () => {
      mockApi.get.mockResolvedValue({
        data: { total: 1, page: 1, page_size: 20, items: [{ id: 1, name: 'Christopher Nolan' }] },
      })

      await directorService.getDirectors(1, 20, 'Nolan')

      expect(mockApi.get).toHaveBeenCalledWith('/directors/', {
        params: { page: 1, page_size: 20, search: 'Nolan' },
      })
    })
  })

  describe('getDirector', () => {
    it('should fetch director detail', async () => {
      const mockDirector = {
        id: 1,
        name: 'Christopher Nolan',
        avatar: 'avatar.jpg',
        biography: 'Famous director',
        birth_date: '1970-07-30',
        country_id: 1,
        created_at: '2024-01-01',
        videos: [{ id: 1, title: 'Inception' }],
      }

      mockApi.get.mockResolvedValue({ data: mockDirector })

      const result = await directorService.getDirector(1)

      expect(mockApi.get).toHaveBeenCalledWith('/directors/1')
      expect(result.name).toBe('Christopher Nolan')
      expect(result.videos).toHaveLength(1)
    })

    it('should handle director not found', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 404, data: { detail: 'Director not found' } },
      })

      await expect(directorService.getDirector(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })
  })

  describe('getDirectorVideos', () => {
    it('should fetch director videos', async () => {
      const mockResponse = {
        total: 10,
        page: 1,
        page_size: 20,
        items: [
          { id: 1, title: 'Movie 1' },
          { id: 2, title: 'Movie 2' },
        ],
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await directorService.getDirectorVideos(1)

      expect(mockApi.get).toHaveBeenCalledWith('/directors/1/videos', {
        params: { page: 1, page_size: 20 },
      })
      expect(result.items).toHaveLength(2)
    })

    it('should fetch with custom pagination', async () => {
      mockApi.get.mockResolvedValue({
        data: { total: 0, page: 2, page_size: 10, items: [] },
      })

      await directorService.getDirectorVideos(1, 2, 10)

      expect(mockApi.get).toHaveBeenCalledWith('/directors/1/videos', {
        params: { page: 2, page_size: 10 },
      })
    })
  })
})

