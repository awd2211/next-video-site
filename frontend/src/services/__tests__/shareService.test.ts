/**
 * 分享服务测试
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { shareService } from '../shareService'
import api from '../api'

vi.mock('../api')

// Mock window and document
Object.defineProperty(window, 'location', {
  value: { origin: 'https://example.com' },
  writable: true,
})

Object.defineProperty(document, 'title', {
  value: 'Test Video Title',
  writable: true,
})

describe('Share Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('recordShare', () => {
    it('should record share action', async () => {
      mockApi.post.mockResolvedValue({ data: null })

      await shareService.recordShare({ video_id: 1, platform: 'weibo' })

      expect(mockApi.post).toHaveBeenCalledWith('/shares/', {
        video_id: 1,
        platform: 'weibo',
      })
    })

    it('should handle different platforms', async () => {
      mockApi.post.mockResolvedValue({ data: null })

      const platforms = ['wechat', 'weibo', 'qq', 'twitter', 'facebook'] as const
      
      for (const platform of platforms) {
        await shareService.recordShare({ video_id: 1, platform })
        expect(mockApi.post).toHaveBeenCalledWith('/shares/', {
          video_id: 1,
          platform,
        })
      }
    })
  })

  describe('getVideoStats', () => {
    it('should get video share statistics', async () => {
      const mockStats = {
        total_shares: 100,
        platform_stats: {
          weibo: 30,
          wechat: 25,
          qq: 20,
          twitter: 15,
          facebook: 10,
        },
        recent_shares: 15,
      }

      mockApi.get.mockResolvedValue({ data: mockStats })

      const result = await shareService.getVideoStats(1)

      expect(mockApi.get).toHaveBeenCalledWith('/shares/video/1/stats')
      expect(result.total_shares).toBe(100)
      expect(result.platform_stats.weibo).toBe(30)
    })
  })

  describe('generateShareUrl', () => {
    it('should generate basic video URL', () => {
      const url = shareService.generateShareUrl(123)
      expect(url).toBe('https://example.com/videos/123')
    })

    it('should generate Weibo share URL', () => {
      const url = shareService.generateShareUrl(123, 'weibo')
      expect(url).toContain('service.weibo.com')
      expect(url).toContain(encodeURIComponent('https://example.com/videos/123'))
    })

    it('should generate QQ share URL', () => {
      const url = shareService.generateShareUrl(123, 'qq')
      expect(url).toContain('connect.qq.com')
      expect(url).toContain(encodeURIComponent('https://example.com/videos/123'))
    })

    it('should generate QZone share URL', () => {
      const url = shareService.generateShareUrl(123, 'qzone')
      expect(url).toContain('sns.qzone.qq.com')
      expect(url).toContain(encodeURIComponent('https://example.com/videos/123'))
    })

    it('should generate Twitter share URL', () => {
      const url = shareService.generateShareUrl(123, 'twitter')
      expect(url).toContain('twitter.com/intent/tweet')
      expect(url).toContain(encodeURIComponent('https://example.com/videos/123'))
    })

    it('should generate Facebook share URL', () => {
      const url = shareService.generateShareUrl(123, 'facebook')
      expect(url).toContain('facebook.com/sharer')
      expect(url).toContain(encodeURIComponent('https://example.com/videos/123'))
    })
  })

  describe('copyToClipboard', () => {
    it('should copy text using modern clipboard API', async () => {
      const mockWriteText = vi.fn().mockResolvedValue(undefined)
      Object.defineProperty(navigator, 'clipboard', {
        value: { writeText: mockWriteText },
        writable: true,
      })
      Object.defineProperty(window, 'isSecureContext', {
        value: true,
        writable: true,
      })

      const result = await shareService.copyToClipboard('test text')

      expect(mockWriteText).toHaveBeenCalledWith('test text')
      expect(result).toBe(true)
    })

    it('should fallback to execCommand for older browsers', async () => {
      // Mock old browser environment
      Object.defineProperty(navigator, 'clipboard', {
        value: undefined,
        writable: true,
      })

      const mockExecCommand = vi.fn().mockReturnValue(true)
      Object.defineProperty(document, 'execCommand', {
        value: mockExecCommand,
        writable: true,
      })

      // Mock DOM methods
      const mockTextArea = {
        value: '',
        style: { position: '', left: '' },
        focus: vi.fn(),
        select: vi.fn(),
      }
      const mockCreateElement = vi.fn().mockReturnValue(mockTextArea)
      const mockAppendChild = vi.fn()
      const mockRemoveChild = vi.fn()

      Object.defineProperty(document, 'createElement', {
        value: mockCreateElement,
        writable: true,
      })
      Object.defineProperty(document.body, 'appendChild', {
        value: mockAppendChild,
        writable: true,
      })
      Object.defineProperty(document.body, 'removeChild', {
        value: mockRemoveChild,
        writable: true,
      })

      const result = await shareService.copyToClipboard('fallback text')

      expect(mockCreateElement).toHaveBeenCalledWith('textarea')
      expect(mockTextArea.value).toBe('fallback text')
      expect(mockExecCommand).toHaveBeenCalledWith('copy')
      expect(result).toBe(true)
    })

    it('should handle clipboard API errors', async () => {
      const mockWriteText = vi.fn().mockRejectedValue(new Error('Permission denied'))
      Object.defineProperty(navigator, 'clipboard', {
        value: { writeText: mockWriteText },
        writable: true,
      })
      Object.defineProperty(window, 'isSecureContext', {
        value: true,
        writable: true,
      })

      const result = await shareService.copyToClipboard('test text')

      expect(result).toBe(false)
    })
  })

  describe('getQRCodeUrl', () => {
    it('should generate QR code URL', () => {
      const qrUrl = shareService.getQRCodeUrl(123)
      
      expect(qrUrl).toContain('api.qrserver.com')
      expect(qrUrl).toContain('200x200')
      expect(qrUrl).toContain(encodeURIComponent('https://example.com/videos/123'))
    })
  })
})
