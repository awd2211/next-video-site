/**
 * 字幕服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import subtitleService from '../subtitleService'
import api from '../api'

vi.mock('../api')

describe('Subtitle Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getVideoSubtitles', () => {
    it('should get video subtitles', async () => {
      const mockResponse = {
        subtitles: [
          {
            id: 1,
            video_id: 10,
            language: 'en',
            language_name: 'English',
            file_url: 'https://cdn.example.com/subtitles/video10_en.vtt',
            format: 'vtt',
            is_default: true,
            is_auto_generated: false,
            sort_order: 0,
            created_at: '2024-01-01T00:00:00Z',
          },
          {
            id: 2,
            video_id: 10,
            language: 'zh-CN',
            language_name: '中文（简体）',
            file_url: 'https://cdn.example.com/subtitles/video10_zh.vtt',
            format: 'vtt',
            is_default: false,
            is_auto_generated: true,
            sort_order: 1,
            created_at: '2024-01-01T00:00:00Z',
          },
        ],
        total: 2,
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await subtitleService.getVideoSubtitles(10)

      expect(mockApi.get).toHaveBeenCalledWith('/videos/10/subtitles')
      expect(result.subtitles).toHaveLength(2)
      expect(result.total).toBe(2)
      expect(result.subtitles[0].language).toBe('en')
      expect(result.subtitles[0].is_default).toBe(true)
      expect(result.subtitles[1].is_auto_generated).toBe(true)
    })

    it('should handle video with no subtitles', async () => {
      const mockResponse = {
        subtitles: [],
        total: 0,
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await subtitleService.getVideoSubtitles(999)

      expect(result.subtitles).toHaveLength(0)
      expect(result.total).toBe(0)
    })

    it('should handle video not found', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 404, data: { detail: 'Video not found' } },
      })

      await expect(subtitleService.getVideoSubtitles(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })

    it('should handle server errors', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 500, data: { detail: 'Internal server error' } },
      })

      await expect(subtitleService.getVideoSubtitles(10)).rejects.toMatchObject({
        response: { status: 500 },
      })
    })

    it('should handle network errors', async () => {
      mockApi.get.mockRejectedValue(new Error('Network error'))

      await expect(subtitleService.getVideoSubtitles(10)).rejects.toThrow('Network error')
    })

    it('should handle subtitles with different formats', async () => {
      const mockResponse = {
        subtitles: [
          {
            id: 1,
            video_id: 10,
            language: 'en',
            language_name: 'English',
            file_url: 'https://cdn.example.com/subtitles/video10_en.srt',
            format: 'srt',
            is_default: true,
            is_auto_generated: false,
            sort_order: 0,
            created_at: '2024-01-01T00:00:00Z',
          },
          {
            id: 2,
            video_id: 10,
            language: 'fr',
            language_name: 'Français',
            file_url: 'https://cdn.example.com/subtitles/video10_fr.ass',
            format: 'ass',
            is_default: false,
            is_auto_generated: false,
            sort_order: 1,
            created_at: '2024-01-01T00:00:00Z',
          },
        ],
        total: 2,
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await subtitleService.getVideoSubtitles(10)

      expect(result.subtitles[0].format).toBe('srt')
      expect(result.subtitles[1].format).toBe('ass')
      expect(result.subtitles[1].language_name).toBe('Français')
    })

    it('should handle subtitles with updated timestamps', async () => {
      const mockResponse = {
        subtitles: [
          {
            id: 1,
            video_id: 10,
            language: 'en',
            language_name: 'English',
            file_url: 'https://cdn.example.com/subtitles/video10_en.vtt',
            format: 'vtt',
            is_default: true,
            is_auto_generated: false,
            sort_order: 0,
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-02T12:00:00Z',
          },
        ],
        total: 1,
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await subtitleService.getVideoSubtitles(10)

      expect(result.subtitles[0].updated_at).toBe('2024-01-02T12:00:00Z')
    })
  })
})
