/**
 * Reports Service Tests
 * 报告服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from '@/utils/axios'
import { reportsService } from '../reports'

vi.mock('@/utils/axios')

// Mock window.URL and document methods for Excel export
global.URL.createObjectURL = vi.fn(() => 'blob:mock-url')
global.URL.revokeObjectURL = vi.fn()
document.createElement = vi.fn((tag) => {
  if (tag === 'a') {
    return {
      href: '',
      download: '',
      click: vi.fn(),
      remove: vi.fn(),
      setAttribute: vi.fn(),
    } as any
  }
  return {} as any
})
document.body.appendChild = vi.fn()

describe('Reports Service', () => {
  const mockAxios = vi.mocked(axios)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getReportTypes', () => {
    it('should fetch available report types', async () => {
      const mockTypes = [
        { type: 'user_activity', name: 'User Activity', description: 'User behavior', icon: 'user' },
        { type: 'content_performance', name: 'Content Performance', description: 'Video stats', icon: 'video' },
        { type: 'vip_subscription', name: 'VIP Subscription', description: 'VIP stats', icon: 'vip' },
      ]

      mockAxios.get.mockResolvedValue({ data: { report_types: mockTypes } })

      const result = await reportsService.getReportTypes()

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/reports/types')
      expect(result).toHaveLength(3)
      expect(result[0].type).toBe('user_activity')
    })
  })

  describe('getUserActivityReport', () => {
    it('should fetch user activity report with default days', async () => {
      const mockReport = {
        report_type: 'user_activity' as const,
        period: { start: '2024-01-01', end: '2024-01-31', days: 30 },
        summary: {
          total_users: 1000,
          new_users: 50,
          active_users: 300,
          vip_users: 100,
          active_rate: 0.3,
        },
        user_trend: [{ date: '2024-01-01', count: 10 }],
        behavior_stats: {
          total_watches: 5000,
          total_comments: 500,
          total_favorites: 200,
          avg_watches_per_user: 5,
        },
      }

      mockAxios.get.mockResolvedValue({ data: mockReport })

      const result = await reportsService.getUserActivityReport()

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/reports/user-activity', { params: { days: 30 } })
      expect(result.summary.total_users).toBe(1000)
      expect(result.user_trend).toHaveLength(1)
    })

    it('should fetch with custom days', async () => {
      mockAxios.get.mockResolvedValue({
        data: {
          report_type: 'user_activity',
          period: { start: '', end: '', days: 7 },
          summary: { total_users: 0, new_users: 0, active_users: 0, vip_users: 0, active_rate: 0 },
          user_trend: [],
          behavior_stats: { total_watches: 0, total_comments: 0, total_favorites: 0, avg_watches_per_user: 0 },
        },
      })

      await reportsService.getUserActivityReport(7)

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/reports/user-activity', { params: { days: 7 } })
    })
  })

  describe('getContentPerformanceReport', () => {
    it('should fetch content performance report', async () => {
      const mockReport = {
        report_type: 'content_performance' as const,
        period: { start: '2024-01-01', end: '2024-01-31', days: 30 },
        summary: {
          total_videos: 500,
          new_videos: 20,
          total_views: 100000,
          total_likes: 5000,
          avg_views_per_video: 200,
        },
        video_trend: [{ date: '2024-01-01', count: 5 }],
        top_videos: [
          {
            id: 1,
            title: 'Top Video',
            video_type: 'movie',
            views: 10000,
            likes: 500,
            favorites: 200,
            comments: 100,
            rating: 9.5,
            created_at: '2024-01-01T00:00:00Z',
          },
        ],
        type_distribution: [{ type: 'movie', count: 300 }],
      }

      mockAxios.get.mockResolvedValue({ data: mockReport })

      const result = await reportsService.getContentPerformanceReport(30, 20)

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/reports/content-performance', {
        params: { days: 30, limit: 20 },
      })
      expect(result.top_videos).toHaveLength(1)
      expect(result.type_distribution).toHaveLength(1)
    })

    it('should use default parameters', async () => {
      mockAxios.get.mockResolvedValue({
        data: {
          report_type: 'content_performance',
          period: { start: '', end: '', days: 30 },
          summary: { total_videos: 0, new_videos: 0, total_views: 0, total_likes: 0, avg_views_per_video: 0 },
          video_trend: [],
          top_videos: [],
          type_distribution: [],
        },
      })

      await reportsService.getContentPerformanceReport()

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/reports/content-performance', {
        params: { days: 30, limit: 20 },
      })
    })
  })

  describe('getVIPSubscriptionReport', () => {
    it('should fetch VIP subscription report', async () => {
      const mockReport = {
        report_type: 'vip_subscription' as const,
        period: { start: '2024-01-01', end: '2024-01-31', days: 30 },
        summary: {
          total_vip: 100,
          new_vip: 10,
          expiring_soon: 5,
          expired: 3,
        },
        alerts: ['5 VIPs expiring soon', null],
      }

      mockAxios.get.mockResolvedValue({ data: mockReport })

      const result = await reportsService.getVIPSubscriptionReport(30)

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/reports/vip-subscription', { params: { days: 30 } })
      expect(result.summary.total_vip).toBe(100)
      expect(result.alerts).toHaveLength(2)
    })
  })

  describe('exportExcel', () => {
    it('should export report to Excel', async () => {
      const mockBlob = new Blob(['test'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })

      mockAxios.get.mockResolvedValue({
        data: mockBlob,
        headers: { 'content-disposition': 'attachment; filename="report.xlsx"' },
      })

      await reportsService.exportExcel('user_activity', 30)

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/reports/export/excel', {
        params: { report_type: 'user_activity', days: 30 },
        responseType: 'blob',
      })

      // Verify download logic
      expect(global.URL.createObjectURL).toHaveBeenCalledWith(expect.any(Blob))
      expect(document.createElement).toHaveBeenCalledWith('a')
    })

    it('should handle missing content-disposition header', async () => {
      const mockBlob = new Blob(['test'])

      mockAxios.get.mockResolvedValue({
        data: mockBlob,
        headers: {},
      })

      await reportsService.exportExcel('content_performance', 7)

      expect(mockAxios.get).toHaveBeenCalled()
    })

    it('should export with default days', async () => {
      mockAxios.get.mockResolvedValue({
        data: new Blob(),
        headers: {},
      })

      await reportsService.exportExcel('vip_subscription')

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/reports/export/excel', {
        params: { report_type: 'vip_subscription', days: 30 },
        responseType: 'blob',
      })
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockAxios.get.mockRejectedValue(new Error('Network error'))

      await expect(reportsService.getUserActivityReport()).rejects.toThrow('Network error')
    })

    it('should handle 404 errors', async () => {
      mockAxios.get.mockRejectedValue({ response: { status: 404 } })

      await expect(reportsService.getContentPerformanceReport()).rejects.toMatchObject({ response: { status: 404 } })
    })

    it('should handle 500 server errors', async () => {
      mockAxios.get.mockRejectedValue({ response: { status: 500 } })

      await expect(reportsService.getVIPSubscriptionReport()).rejects.toMatchObject({ response: { status: 500 } })
    })
  })

  describe('Edge Cases', () => {
    it('should handle very long time periods', async () => {
      mockAxios.get.mockResolvedValue({
        data: {
          report_type: 'user_activity',
          period: { start: '', end: '', days: 365 },
          summary: { total_users: 0, new_users: 0, active_users: 0, vip_users: 0, active_rate: 0 },
          user_trend: [],
          behavior_stats: { total_watches: 0, total_comments: 0, total_favorites: 0, avg_watches_per_user: 0 },
        },
      })

      await reportsService.getUserActivityReport(365)

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/reports/user-activity', { params: { days: 365 } })
    })

    it('should handle empty top videos list', async () => {
      mockAxios.get.mockResolvedValue({
        data: {
          report_type: 'content_performance',
          period: { start: '', end: '', days: 30 },
          summary: { total_videos: 0, new_videos: 0, total_views: 0, total_likes: 0, avg_views_per_video: 0 },
          video_trend: [],
          top_videos: [],
          type_distribution: [],
        },
      })

      const result = await reportsService.getContentPerformanceReport()

      expect(result.top_videos).toHaveLength(0)
    })

    it('should handle null alerts in VIP report', async () => {
      mockAxios.get.mockResolvedValue({
        data: {
          report_type: 'vip_subscription',
          period: { start: '', end: '', days: 30 },
          summary: { total_vip: 0, new_vip: 0, expiring_soon: 0, expired: 0 },
          alerts: [null, null, null],
        },
      })

      const result = await reportsService.getVIPSubscriptionReport()

      expect(result.alerts).toHaveLength(3)
      expect(result.alerts.every((a) => a === null)).toBe(true)
    })
  })
})
