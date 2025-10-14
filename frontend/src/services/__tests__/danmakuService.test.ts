/**
 * 弹幕服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { danmakuService } from '../danmakuService'
import api from '../api'

vi.mock('../api')

describe('Danmaku Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('send', () => {
    it('should send danmaku with default options', async () => {
      const danmakuData = {
        video_id: 1,
        content: 'Great video!',
        time: 60,
      }

      const mockResponse = {
        id: 1,
        video_id: 1,
        user_id: 1,
        content: 'Great video!',
        time: 60,
        type: 'scroll',
        color: '#FFFFFF',
        font_size: 14,
        status: 'approved',
        is_blocked: false,
        report_count: 0,
        created_at: '2024-01-01T00:00:00Z',
      }

      mockApi.post.mockResolvedValue({ data: mockResponse })

      const result = await danmakuService.send(danmakuData)

      expect(mockApi.post).toHaveBeenCalledWith('/danmaku/', danmakuData)
      expect(result.content).toBe('Great video!')
      expect(result.time).toBe(60)
    })

    it('should send danmaku with custom options', async () => {
      const danmakuData = {
        video_id: 1,
        content: 'Amazing!',
        time: 120,
        type: 'top' as const,
        color: '#FF0000',
        font_size: 16,
      }

      mockApi.post.mockResolvedValue({
        data: { ...danmakuData, id: 2, user_id: 1, status: 'approved', is_blocked: false, report_count: 0, created_at: '2024-01-01' },
      })

      const result = await danmakuService.send(danmakuData)

      expect(result.type).toBe('top')
      expect(result.color).toBe('#FF0000')
      expect(result.font_size).toBe(16)
    })

    it('should require authentication', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(danmakuService.send({ video_id: 1, content: 'Test', time: 0 })).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('getVideoDanmaku', () => {
    it('should fetch all danmaku for video', async () => {
      const mockResponse = {
        total: 2,
        items: [
          { id: 1, content: 'Danmaku 1', time: 10, type: 'scroll', color: '#FFFFFF', font_size: 14 },
          { id: 2, content: 'Danmaku 2', time: 20, type: 'top', color: '#FF0000', font_size: 16 },
        ],
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await danmakuService.getVideoDanmaku(1)

      expect(mockApi.get).toHaveBeenCalledWith('/danmaku/video/1', { params: {} })
      expect(result.items).toHaveLength(2)
    })

    it('should fetch danmaku with time range', async () => {
      mockApi.get.mockResolvedValue({ data: { total: 0, items: [] } })

      await danmakuService.getVideoDanmaku(1, 10, 60)

      expect(mockApi.get).toHaveBeenCalledWith('/danmaku/video/1', {
        params: { start_time: 10, end_time: 60 },
      })
    })

    it('should handle video with no danmaku', async () => {
      mockApi.get.mockResolvedValue({ data: { total: 0, items: [] } })

      const result = await danmakuService.getVideoDanmaku(999)

      expect(result.items).toHaveLength(0)
      expect(result.total).toBe(0)
    })
  })

  describe('deleteMyDanmaku', () => {
    it('should delete own danmaku', async () => {
      mockApi.delete.mockResolvedValue({ data: null })

      await danmakuService.deleteMyDanmaku(1)

      expect(mockApi.delete).toHaveBeenCalledWith('/danmaku/1')
    })

    it('should handle permission denied', async () => {
      mockApi.delete.mockRejectedValue({
        response: { status: 403, data: { detail: 'Permission denied' } },
      })

      await expect(danmakuService.deleteMyDanmaku(1)).rejects.toMatchObject({
        response: { status: 403 },
      })
    })

    it('should handle danmaku not found', async () => {
      mockApi.delete.mockRejectedValue({
        response: { status: 404, data: { detail: 'Danmaku not found' } },
      })

      await expect(danmakuService.deleteMyDanmaku(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })
  })

  describe('report', () => {
    it('should report inappropriate danmaku', async () => {
      mockApi.post.mockResolvedValue({
        data: { message: 'Report submitted', report_count: 1 },
      })

      const result = await danmakuService.report(1)

      expect(mockApi.post).toHaveBeenCalledWith('/danmaku/1/report')
      expect(result.report_count).toBe(1)
    })

    it('should handle already reported', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 409, data: { detail: 'Already reported' } },
      })

      await expect(danmakuService.report(1)).rejects.toMatchObject({
        response: { status: 409 },
      })
    })
  })

  describe('getMyDanmaku', () => {
    it('should fetch user\'s danmaku', async () => {
      const mockDanmaku = [
        { id: 1, video_id: 1, content: 'My danmaku 1', time: 10 },
        { id: 2, video_id: 2, content: 'My danmaku 2', time: 20 },
      ]

      mockApi.get.mockResolvedValue({ data: mockDanmaku })

      const result = await danmakuService.getMyDanmaku()

      expect(mockApi.get).toHaveBeenCalledWith('/danmaku/my-danmaku', {
        params: { page: 1, page_size: 20 },
      })
      expect(result).toHaveLength(2)
    })

    it('should fetch danmaku for specific video', async () => {
      mockApi.get.mockResolvedValue({ data: [] })

      await danmakuService.getMyDanmaku(10)

      expect(mockApi.get).toHaveBeenCalledWith('/danmaku/my-danmaku', {
        params: { page: 1, page_size: 20, video_id: 10 },
      })
    })

    it('should fetch with custom pagination', async () => {
      mockApi.get.mockResolvedValue({ data: [] })

      await danmakuService.getMyDanmaku(undefined, 2, 10)

      expect(mockApi.get).toHaveBeenCalledWith('/danmaku/my-danmaku', {
        params: { page: 2, page_size: 10 },
      })
    })
  })
})

