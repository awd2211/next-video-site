/**
 * 下载服务测试
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import downloadService, { getVideoDownloadUrl, downloadVideo, formatFileSize } from '../downloadService'
import axios from 'axios'

vi.mock('axios')

describe('Download Service', () => {
  const mockAxios = vi.mocked(axios)

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: vi.fn().mockReturnValue('test-token'),
      },
      writable: true,
    })

    // Mock window.open
    Object.defineProperty(window, 'open', {
      value: vi.fn(),
      writable: true,
    })

    // Mock console.error
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('getVideoDownloadUrl', () => {
    it('should get download URL with default quality', async () => {
      const mockResponse = {
        data: {
          download_url: 'https://cdn.example.com/video123_720p.mp4',
          expires_in: 3600,
          quality: '720p',
          file_size: 1073741824, // 1GB
          video_title: 'Test Video',
        },
      }

      mockAxios.get.mockResolvedValue(mockResponse)

      const result = await getVideoDownloadUrl(123)

      expect(mockAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/videos/123/download'),
        {
          params: { quality: '720p' },
          headers: { Authorization: 'Bearer test-token' },
        }
      )
      expect(result.quality).toBe('720p')
      expect(result.file_size).toBe(1073741824)
    })

    it('should get download URL with custom quality', async () => {
      const mockResponse = {
        data: {
          download_url: 'https://cdn.example.com/video123_1080p.mp4',
          expires_in: 3600,
          quality: '1080p',
          file_size: 2147483648, // 2GB
          video_title: 'Test Video',
        },
      }

      mockAxios.get.mockResolvedValue(mockResponse)

      const result = await getVideoDownloadUrl(123, '1080p')

      expect(mockAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/videos/123/download'),
        {
          params: { quality: '1080p' },
          headers: { Authorization: 'Bearer test-token' },
        }
      )
      expect(result.quality).toBe('1080p')
    })

    it('should handle unauthorized access', async () => {
      mockAxios.get.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(getVideoDownloadUrl(123)).rejects.toMatchObject({
        response: { status: 401 },
      })
    })

    it('should handle video not found', async () => {
      mockAxios.get.mockRejectedValue({
        response: { status: 404, data: { detail: 'Video not found' } },
      })

      await expect(getVideoDownloadUrl(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })

    it('should handle quality not available', async () => {
      mockAxios.get.mockRejectedValue({
        response: { status: 400, data: { detail: 'Quality not available' } },
      })

      await expect(getVideoDownloadUrl(123, '4K')).rejects.toMatchObject({
        response: { status: 400 },
      })
    })
  })

  describe('downloadVideo', () => {
    it('should download video and open URL', async () => {
      const mockResponse = {
        data: {
          download_url: 'https://cdn.example.com/video123_720p.mp4',
          expires_in: 3600,
          quality: '720p',
          file_size: 1073741824,
          video_title: 'Test Video',
        },
      }

      mockAxios.get.mockResolvedValue(mockResponse)
      const mockOpen = vi.fn()
      Object.defineProperty(window, 'open', { value: mockOpen })

      const result = await downloadVideo(123)

      expect(mockOpen).toHaveBeenCalledWith(
        'https://cdn.example.com/video123_720p.mp4',
        '_blank'
      )
      expect(result.quality).toBe('720p')
    })

    it('should download video with custom quality', async () => {
      const mockResponse = {
        data: {
          download_url: 'https://cdn.example.com/video123_480p.mp4',
          expires_in: 3600,
          quality: '480p',
          file_size: 536870912, // 512MB
          video_title: 'Test Video',
        },
      }

      mockAxios.get.mockResolvedValue(mockResponse)

      await downloadVideo(123, '480p')

      expect(mockAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/videos/123/download'),
        expect.objectContaining({
          params: { quality: '480p' },
        })
      )
    })

    it('should handle download errors', async () => {
      mockAxios.get.mockRejectedValue(new Error('Network error'))

      await expect(downloadVideo(123)).rejects.toThrow('Network error')
      expect(console.error).toHaveBeenCalledWith(
        'Download video failed:',
        expect.any(Error)
      )
    })
  })

  describe('formatFileSize', () => {
    it('should format bytes correctly', () => {
      expect(formatFileSize(0)).toBe('Unknown')
      expect(formatFileSize(null)).toBe('Unknown')
      expect(formatFileSize(1024)).toBe('1 KB')
      expect(formatFileSize(1048576)).toBe('1 MB') // 1024 * 1024
      expect(formatFileSize(1073741824)).toBe('1 GB') // 1024 * 1024 * 1024
      expect(formatFileSize(1099511627776)).toBe('1 TB') // 1024^4
    })

    it('should format with decimals', () => {
      expect(formatFileSize(1536)).toBe('1.5 KB') // 1.5 * 1024
      expect(formatFileSize(1610612736)).toBe('1.5 GB') // 1.5 * 1024^3
    })

    it('should handle very small sizes', () => {
      expect(formatFileSize(512)).toBe('512 B')
      expect(formatFileSize(1)).toBe('1 B')
    })

    it('should handle very large sizes', () => {
      expect(formatFileSize(5497558138880)).toBe('5 TB') // 5 * 1024^4
    })
  })

  describe('default export', () => {
    it('should export all functions', () => {
      expect(downloadService.getVideoDownloadUrl).toBeDefined()
      expect(downloadService.downloadVideo).toBeDefined()
      expect(downloadService.formatFileSize).toBeDefined()
    })
  })
})
