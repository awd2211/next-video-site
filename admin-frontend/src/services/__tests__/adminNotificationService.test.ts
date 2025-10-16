/**
 * Admin Notification Service Tests
 * 管理员通知服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from '@/utils/axios'
import {
  getAdminNotifications,
  getAdminNotificationStats,
  markNotificationAsRead,
  markAllNotificationsAsRead,
  deleteNotification,
  clearAllNotifications,
  createTestNotification,
  type AdminNotification,
  type AdminNotificationListResponse,
  type AdminNotificationStats,
} from '../adminNotificationService'

// Mock axios module
vi.mock('@/utils/axios')

describe('Admin Notification Service', () => {
  const mockAxios = vi.mocked(axios)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  // Mock notification data
  const mockNotification: AdminNotification = {
    id: 1,
    admin_user_id: 1,
    type: 'system_alert',
    title: 'Test Notification',
    content: 'This is a test notification',
    severity: 'info',
    related_type: 'video',
    related_id: 100,
    link: '/videos/100',
    is_read: false,
    created_at: '2024-01-01T00:00:00Z',
    read_at: null,
  }

  describe('getAdminNotifications', () => {
    it('should fetch notifications with default parameters', async () => {
      const mockResponse: AdminNotificationListResponse = {
        notifications: [mockNotification],
        total: 1,
        page: 1,
        page_size: 20,
        pages: 1,
        unread_count: 1,
      }

      mockAxios.get.mockResolvedValue({ data: mockResponse })

      const result = await getAdminNotifications()

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/notifications', { params: {} })
      expect(result.notifications).toHaveLength(1)
      expect(result.total).toBe(1)
      expect(result.unread_count).toBe(1)
    })

    it('should fetch notifications with custom parameters', async () => {
      const mockResponse: AdminNotificationListResponse = {
        notifications: [],
        total: 0,
        page: 2,
        page_size: 10,
        pages: 0,
        unread_count: 0,
      }

      mockAxios.get.mockResolvedValue({ data: mockResponse })

      const params = {
        page: 2,
        page_size: 10,
        type: 'error',
        severity: 'critical',
        is_read: false,
      }

      await getAdminNotifications(params)

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/notifications', { params })
    })

    it('should filter by notification type', async () => {
      const mockResponse: AdminNotificationListResponse = {
        notifications: [mockNotification],
        total: 1,
        page: 1,
        page_size: 20,
        pages: 1,
        unread_count: 1,
      }

      mockAxios.get.mockResolvedValue({ data: mockResponse })

      await getAdminNotifications({ type: 'system_alert' })

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/notifications', {
        params: { type: 'system_alert' },
      })
    })

    it('should filter by severity', async () => {
      const mockResponse: AdminNotificationListResponse = {
        notifications: [],
        total: 0,
        page: 1,
        page_size: 20,
        pages: 0,
        unread_count: 0,
      }

      mockAxios.get.mockResolvedValue({ data: mockResponse })

      await getAdminNotifications({ severity: 'warning' })

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/notifications', {
        params: { severity: 'warning' },
      })
    })

    it('should filter by read status', async () => {
      const mockResponse: AdminNotificationListResponse = {
        notifications: [],
        total: 0,
        page: 1,
        page_size: 20,
        pages: 0,
        unread_count: 0,
      }

      mockAxios.get.mockResolvedValue({ data: mockResponse })

      await getAdminNotifications({ is_read: true })

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/notifications', {
        params: { is_read: true },
      })
    })

    it('should handle API errors', async () => {
      mockAxios.get.mockRejectedValue(new Error('Network error'))

      await expect(getAdminNotifications()).rejects.toThrow('Network error')
    })
  })

  describe('getAdminNotificationStats', () => {
    it('should fetch notification statistics', async () => {
      const mockStats: AdminNotificationStats = {
        total: 100,
        unread: 25,
        read: 75,
        by_severity: {
          info: 50,
          warning: 30,
          error: 15,
          critical: 5,
        },
      }

      mockAxios.get.mockResolvedValue({ data: mockStats })

      const result = await getAdminNotificationStats()

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/notifications/stats')
      expect(result.total).toBe(100)
      expect(result.unread).toBe(25)
      expect(result.read).toBe(75)
      expect(result.by_severity.info).toBe(50)
      expect(result.by_severity.critical).toBe(5)
    })

    it('should handle empty statistics', async () => {
      const mockStats: AdminNotificationStats = {
        total: 0,
        unread: 0,
        read: 0,
        by_severity: {},
      }

      mockAxios.get.mockResolvedValue({ data: mockStats })

      const result = await getAdminNotificationStats()

      expect(result.total).toBe(0)
      expect(result.by_severity).toEqual({})
    })

    it('should handle API errors', async () => {
      mockAxios.get.mockRejectedValue(new Error('Failed to fetch stats'))

      await expect(getAdminNotificationStats()).rejects.toThrow('Failed to fetch stats')
    })
  })

  describe('markNotificationAsRead', () => {
    it('should mark single notification as read', async () => {
      const readNotification: AdminNotification = {
        ...mockNotification,
        is_read: true,
        read_at: '2024-01-01T12:00:00Z',
      }

      mockAxios.patch.mockResolvedValue({ data: readNotification })

      const result = await markNotificationAsRead(1)

      expect(mockAxios.patch).toHaveBeenCalledWith('/api/v1/admin/notifications/1')
      expect(result.is_read).toBe(true)
      expect(result.read_at).toBe('2024-01-01T12:00:00Z')
    })

    it('should handle marking already read notification', async () => {
      const readNotification: AdminNotification = {
        ...mockNotification,
        is_read: true,
        read_at: '2024-01-01T10:00:00Z',
      }

      mockAxios.patch.mockResolvedValue({ data: readNotification })

      const result = await markNotificationAsRead(1)

      expect(result.is_read).toBe(true)
    })

    it('should handle non-existent notification', async () => {
      mockAxios.patch.mockRejectedValue({
        response: { status: 404, data: { detail: 'Notification not found' } },
      })

      await expect(markNotificationAsRead(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })

    it('should handle API errors', async () => {
      mockAxios.patch.mockRejectedValue(new Error('Network error'))

      await expect(markNotificationAsRead(1)).rejects.toThrow('Network error')
    })
  })

  describe('markAllNotificationsAsRead', () => {
    it('should mark all notifications as read', async () => {
      const mockResponse = {
        message: 'All notifications marked as read',
        count: 10,
      }

      mockAxios.post.mockResolvedValue({ data: mockResponse })

      const result = await markAllNotificationsAsRead()

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/notifications/mark-all-read')
      expect(result.count).toBe(10)
      expect(result.message).toBe('All notifications marked as read')
    })

    it('should handle no unread notifications', async () => {
      const mockResponse = {
        message: 'No unread notifications',
        count: 0,
      }

      mockAxios.post.mockResolvedValue({ data: mockResponse })

      const result = await markAllNotificationsAsRead()

      expect(result.count).toBe(0)
    })

    it('should handle API errors', async () => {
      mockAxios.post.mockRejectedValue(new Error('Failed to mark all as read'))

      await expect(markAllNotificationsAsRead()).rejects.toThrow('Failed to mark all as read')
    })
  })

  describe('deleteNotification', () => {
    it('should delete single notification', async () => {
      const mockResponse = {
        message: 'Notification deleted successfully',
      }

      mockAxios.delete.mockResolvedValue({ data: mockResponse })

      const result = await deleteNotification(1)

      expect(mockAxios.delete).toHaveBeenCalledWith('/api/v1/admin/notifications/1')
      expect(result.message).toBe('Notification deleted successfully')
    })

    it('should handle non-existent notification', async () => {
      mockAxios.delete.mockRejectedValue({
        response: { status: 404, data: { detail: 'Notification not found' } },
      })

      await expect(deleteNotification(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })

    it('should handle permission errors', async () => {
      mockAxios.delete.mockRejectedValue({
        response: { status: 403, data: { detail: 'Permission denied' } },
      })

      await expect(deleteNotification(1)).rejects.toMatchObject({
        response: { status: 403 },
      })
    })

    it('should handle API errors', async () => {
      mockAxios.delete.mockRejectedValue(new Error('Network error'))

      await expect(deleteNotification(1)).rejects.toThrow('Network error')
    })
  })

  describe('clearAllNotifications', () => {
    it('should clear all notifications', async () => {
      const mockResponse = {
        message: 'All notifications cleared',
        count: 50,
      }

      mockAxios.post.mockResolvedValue({ data: mockResponse })

      const result = await clearAllNotifications()

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/notifications/clear-all')
      expect(result.count).toBe(50)
      expect(result.message).toBe('All notifications cleared')
    })

    it('should handle no notifications to clear', async () => {
      const mockResponse = {
        message: 'No notifications to clear',
        count: 0,
      }

      mockAxios.post.mockResolvedValue({ data: mockResponse })

      const result = await clearAllNotifications()

      expect(result.count).toBe(0)
    })

    it('should handle API errors', async () => {
      mockAxios.post.mockRejectedValue(new Error('Failed to clear notifications'))

      await expect(clearAllNotifications()).rejects.toThrow('Failed to clear notifications')
    })
  })

  describe('createTestNotification', () => {
    it('should create test notification', async () => {
      const mockResponse = {
        message: 'Test notification created successfully',
      }

      mockAxios.post.mockResolvedValue({ data: mockResponse })

      const result = await createTestNotification()

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/notifications/test-notification')
      expect(result.message).toBe('Test notification created successfully')
    })

    it('should handle API errors', async () => {
      mockAxios.post.mockRejectedValue(new Error('Failed to create test notification'))

      await expect(createTestNotification()).rejects.toThrow('Failed to create test notification')
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors gracefully', async () => {
      mockAxios.get.mockRejectedValue(new Error('Network Error'))

      await expect(getAdminNotifications()).rejects.toThrow('Network Error')
    })

    it('should handle server errors', async () => {
      mockAxios.get.mockRejectedValue({
        response: {
          status: 500,
          data: { detail: 'Internal Server Error' },
        },
      })

      await expect(getAdminNotifications()).rejects.toMatchObject({
        response: { status: 500 },
      })
    })

    it('should handle unauthorized access', async () => {
      mockAxios.get.mockRejectedValue({
        response: {
          status: 401,
          data: { detail: 'Unauthorized' },
        },
      })

      await expect(getAdminNotifications()).rejects.toMatchObject({
        response: { status: 401 },
      })
    })

    it('should handle validation errors', async () => {
      mockAxios.patch.mockRejectedValue({
        response: {
          status: 422,
          data: { detail: 'Validation Error' },
        },
      })

      await expect(markNotificationAsRead(1)).rejects.toMatchObject({
        response: { status: 422 },
      })
    })
  })

  describe('Edge Cases', () => {
    it('should handle large notification IDs', async () => {
      const largeId = 999999999

      mockAxios.patch.mockResolvedValue({
        data: { ...mockNotification, id: largeId },
      })

      const result = await markNotificationAsRead(largeId)

      expect(mockAxios.patch).toHaveBeenCalledWith(`/api/v1/admin/notifications/${largeId}`)
      expect(result.id).toBe(largeId)
    })

    it('should handle all severity types', async () => {
      const severities: Array<'info' | 'warning' | 'error' | 'critical'> = [
        'info',
        'warning',
        'error',
        'critical',
      ]

      for (const severity of severities) {
        mockAxios.get.mockResolvedValue({
          data: {
            notifications: [{ ...mockNotification, severity }],
            total: 1,
            page: 1,
            page_size: 20,
            pages: 1,
            unread_count: 1,
          },
        })

        await getAdminNotifications({ severity })

        expect(mockAxios.get).toHaveBeenLastCalledWith('/api/v1/admin/notifications', {
          params: { severity },
        })
      }
    })

    it('should handle pagination edge cases', async () => {
      const mockResponse: AdminNotificationListResponse = {
        notifications: [],
        total: 0,
        page: 100,
        page_size: 50,
        pages: 0,
        unread_count: 0,
      }

      mockAxios.get.mockResolvedValue({ data: mockResponse })

      await getAdminNotifications({ page: 100, page_size: 50 })

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/notifications', {
        params: { page: 100, page_size: 50 },
      })
    })

    it('should handle notifications with null values', async () => {
      const nullNotification: AdminNotification = {
        id: 1,
        admin_user_id: null,
        type: 'system',
        title: 'Test',
        content: 'Test content',
        severity: 'info',
        related_type: null,
        related_id: null,
        link: null,
        is_read: false,
        created_at: '2024-01-01T00:00:00Z',
        read_at: null,
      }

      mockAxios.get.mockResolvedValue({
        data: {
          notifications: [nullNotification],
          total: 1,
          page: 1,
          page_size: 20,
          pages: 1,
          unread_count: 1,
        },
      })

      const result = await getAdminNotifications()

      expect(result.notifications[0].admin_user_id).toBeNull()
      expect(result.notifications[0].related_type).toBeNull()
      expect(result.notifications[0].link).toBeNull()
    })
  })
})
