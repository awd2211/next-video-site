/**
 * 演员服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { actorService } from '../actorService'
import api from '../api'

vi.mock('../api')

describe('Actor Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getActors', () => {
    it('should fetch actors with default parameters', async () => {
      const mockResponse = {
        total: 2,
        page: 1,
        page_size: 20,
        items: [
          { id: 1, name: 'Actor 1', avatar: null, biography: null, birth_date: null, country_id: null, created_at: '2024-01-01' },
          { id: 2, name: 'Actor 2', avatar: 'avatar.jpg', biography: 'Bio', birth_date: '1990-01-01', country_id: 1, created_at: '2024-01-02' },
        ],
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await actorService.getActors()

      expect(mockApi.get).toHaveBeenCalledWith('/actors/', {
        params: { page: 1, page_size: 20, search: '' },
      })
      expect(result.items).toHaveLength(2)
    })

    it('should fetch actors with custom pagination', async () => {
      mockApi.get.mockResolvedValue({
        data: { total: 0, page: 2, page_size: 10, items: [] },
      })

      await actorService.getActors(2, 10)

      expect(mockApi.get).toHaveBeenCalledWith('/actors/', {
        params: { page: 2, page_size: 10, search: '' },
      })
    })

    it('should search actors by name', async () => {
      mockApi.get.mockResolvedValue({
        data: { total: 1, page: 1, page_size: 20, items: [{ id: 1, name: 'John Doe' }] },
      })

      await actorService.getActors(1, 20, 'John')

      expect(mockApi.get).toHaveBeenCalledWith('/actors/', {
        params: { page: 1, page_size: 20, search: 'John' },
      })
    })
  })

  describe('getActor', () => {
    it('should fetch actor detail', async () => {
      const mockActor = {
        id: 1,
        name: 'John Doe',
        avatar: 'avatar.jpg',
        biography: 'Famous actor',
        birth_date: '1980-01-01',
        country_id: 1,
        created_at: '2024-01-01',
        videos: [{ id: 1, title: 'Movie 1' }],
      }

      mockApi.get.mockResolvedValue({ data: mockActor })

      const result = await actorService.getActor(1)

      expect(mockApi.get).toHaveBeenCalledWith('/actors/1')
      expect(result.name).toBe('John Doe')
      expect(result.videos).toHaveLength(1)
    })

    it('should handle actor not found', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 404, data: { detail: 'Actor not found' } },
      })

      await expect(actorService.getActor(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })
  })

  describe('getActorVideos', () => {
    it('should fetch actor videos', async () => {
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

      const result = await actorService.getActorVideos(1)

      expect(mockApi.get).toHaveBeenCalledWith('/actors/1/videos', {
        params: { page: 1, page_size: 20 },
      })
      expect(result.items).toHaveLength(2)
    })

    it('should fetch with custom pagination', async () => {
      mockApi.get.mockResolvedValue({
        data: { total: 0, page: 2, page_size: 10, items: [] },
      })

      await actorService.getActorVideos(1, 2, 10)

      expect(mockApi.get).toHaveBeenCalledWith('/actors/1/videos', {
        params: { page: 2, page_size: 10 },
      })
    })
  })
})

