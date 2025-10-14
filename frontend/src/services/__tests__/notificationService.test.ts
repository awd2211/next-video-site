/**
 * 通知服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import notificationService from '../notificationService'
import api from '../api'

vi.mock('../api')

describe('Notification Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getNotifications', () => {
    it('should fetch notifications with default parameters', async () => {
      const mockResponse = {
        notifications: [
          {
            id: 1,
            user_id: 1,
            type: 'system',
            title: 'System Update',
            content: 'System maintenance completed',
            is_read: false,
            created_at: '2024-01-01T00:00:00Z',
          },
        ],
        total: 1,
        page: 1,
        page_size: 20,
        unread_count: 1,
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await notificationService.getNotifications()

      expect(mockApi.get).toHaveBeenCalledWith('/notifications/', { params: undefined })
      expect(result.notifications).toHaveLength(1)
      expect(result.unread_count).toBe(1)
    })

    it('should fetch notifications with filters', async () => {
      mockApi.get.mockResolvedValue({
        data: { notifications: [], total: 0, page: 1, page_size: 10, unread_count: 0 },
      })

      const params = { page: 2, page_size: 10, type: 'comment', is_read: true }
      await notificationService.getNotifications(params)

      expect(mockApi.get).toHaveBeenCalledWith('/notifications/', { params })
    })
  })

  describe('getStats', () => {
    it('should fetch notification statistics', async () => {
      const mockStats = { total: 50, unread: 10, read: 40 }
      mockApi.get.mockResolvedValue({ data: mockStats })

      const result = await notificationService.getStats()

      expect(mockApi.get).toHaveBeenCalledWith('/notifications/stats')
      expect(result.total).toBe(50)
      expect(result.unread).toBe(10)
    })
  })

  describe('markAsRead', () => {
    it('should mark notification as read', async () => {
      const mockNotification = {
        id: 1,
        user_id: 1,
        type: 'system',
        title: 'Test',
        content: 'Test content',
        is_read: true,
        created_at: '2024-01-01T00:00:00Z',
        read_at: '2024-01-01T01:00:00Z',
      }

      mockApi.patch.mockResolvedValue({ data: mockNotification })

      const result = await notificationService.markAsRead(1)

      expect(mockApi.patch).toHaveBeenCalledWith('/notifications/1')
      expect(result.is_read).toBe(true)
      expect(result.read_at).toBeDefined()
    })
  })

  describe('markAllAsRead', () => {
    it('should mark all notifications as read', async () => {
      mockApi.post.mockResolvedValue({ data: { message: 'All marked as read', count: 5 } })

      const result = await notificationService.markAllAsRead()

      expect(mockApi.post).toHaveBeenCalledWith('/notifications/mark-all-read')
      expect(result.count).toBe(5)
    })
  })

  describe('deleteNotification', () => {
    it('should delete notification', async () => {
      mockApi.delete.mockResolvedValue({ data: { message: 'Notification deleted' } })

      const result = await notificationService.deleteNotification(1)

      expect(mockApi.delete).toHaveBeenCalledWith('/notifications/1')
      expect(result.message).toBe('Notification deleted')
    })
  })

  describe('clearAll', () => {
    it('should clear all notifications', async () => {
      mockApi.post.mockResolvedValue({ data: { message: 'All cleared', count: 20 } })

      const result = await notificationService.clearAll()

      expect(mockApi.post).toHaveBeenCalledWith('/notifications/clear-all')
      expect(result.count).toBe(20)
    })
  })
})
