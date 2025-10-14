/**
 * 数据服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { dataService } from '../dataService'
import api from '../api'

vi.mock('../api')

describe('Data Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getCategories', () => {
    it('should fetch categories', async () => {
      const mockCategories = [
        { id: 1, name: 'Action', slug: 'action', description: 'Action movies' },
        { id: 2, name: 'Comedy', slug: 'comedy', description: 'Comedy movies' },
        { id: 3, name: 'Drama', slug: 'drama', description: 'Drama movies' },
      ]

      mockApi.get.mockResolvedValue({ data: mockCategories })

      const result = await dataService.getCategories()

      expect(mockApi.get).toHaveBeenCalledWith('/categories')
      expect(result).toHaveLength(3)
      expect(result[0].name).toBe('Action')
      expect(result[1].slug).toBe('comedy')
      expect(result[2].description).toBe('Drama movies')
    })

    it('should handle empty categories', async () => {
      mockApi.get.mockResolvedValue({ data: [] })

      const result = await dataService.getCategories()

      expect(result).toHaveLength(0)
    })

    it('should handle API errors', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 500, data: { detail: 'Server error' } },
      })

      await expect(dataService.getCategories()).rejects.toMatchObject({
        response: { status: 500 },
      })
    })

    it('should handle network errors', async () => {
      mockApi.get.mockRejectedValue(new Error('Network error'))

      await expect(dataService.getCategories()).rejects.toThrow('Network error')
    })

    it('should handle categories with all fields', async () => {
      const mockCategories = [
        {
          id: 1,
          name: 'Sci-Fi',
          slug: 'sci-fi',
          description: 'Science fiction movies and series',
          is_active: true,
          sort_order: 1,
          video_count: 150,
          created_at: '2024-01-01T00:00:00Z',
        },
      ]

      mockApi.get.mockResolvedValue({ data: mockCategories })

      const result = await dataService.getCategories()

      expect(result[0].video_count).toBe(150)
      expect(result[0].is_active).toBe(true)
    })
  })

  describe('getCountries', () => {
    it('should fetch countries', async () => {
      const mockCountries = [
        { id: 1, name: 'United States', code: 'US' },
        { id: 2, name: 'China', code: 'CN' },
        { id: 3, name: 'Japan', code: 'JP' },
      ]

      mockApi.get.mockResolvedValue({ data: mockCountries })

      const result = await dataService.getCountries()

      expect(mockApi.get).toHaveBeenCalledWith('/countries')
      expect(result).toHaveLength(3)
      expect(result[0].name).toBe('United States')
      expect(result[1].code).toBe('CN')
      expect(result[2].name).toBe('Japan')
    })

    it('should handle empty countries', async () => {
      mockApi.get.mockResolvedValue({ data: [] })

      const result = await dataService.getCountries()

      expect(result).toHaveLength(0)
    })

    it('should handle API errors', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 503, data: { detail: 'Service unavailable' } },
      })

      await expect(dataService.getCountries()).rejects.toMatchObject({
        response: { status: 503 },
      })
    })

    it('should handle network errors', async () => {
      mockApi.get.mockRejectedValue(new Error('Connection timeout'))

      await expect(dataService.getCountries()).rejects.toThrow('Connection timeout')
    })

    it('should handle countries with extended fields', async () => {
      const mockCountries = [
        {
          id: 1,
          name: 'South Korea',
          code: 'KR',
          flag_url: 'https://example.com/kr.png',
          is_active: true,
          video_count: 80,
          created_at: '2024-01-01T00:00:00Z',
        },
      ]

      mockApi.get.mockResolvedValue({ data: mockCountries })

      const result = await dataService.getCountries()

      expect(result[0].flag_url).toBe('https://example.com/kr.png')
      expect(result[0].video_count).toBe(80)
    })

    it('should handle malformed response gracefully', async () => {
      mockApi.get.mockResolvedValue({ data: null })

      await expect(dataService.getCountries()).rejects.toThrow()
    })
  })
})
