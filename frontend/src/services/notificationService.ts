import api from '@/utils/axios'

export interface Notification {
  id: number
  user_id: number
  type: string
  title: string
  content: string
  related_type?: string
  related_id?: number
  link?: string
  is_read: boolean
  created_at: string
  read_at?: string
}

export interface NotificationStats {
  total: number
  unread: number
  read: number
}

export interface NotificationListResponse {
  notifications: Notification[]
  total: number
  page: number
  page_size: number
  unread_count: number
}

const notificationService = {
  // 获取通知列表
  getNotifications: async (params?: {
    page?: number
    page_size?: number
    type?: string
    is_read?: boolean
  }): Promise<NotificationListResponse> => {
    const response = await api.get('/notifications/', { params })
    return response.data
  },

  // 获取通知统计
  getStats: async (): Promise<NotificationStats> => {
    const response = await api.get('/notifications/stats')
    return response.data
  },

  // 标记通知为已读
  markAsRead: async (notificationId: number): Promise<Notification> => {
    const response = await api.patch(`/notifications/${notificationId}`)
    return response.data
  },

  // 标记所有通知为已读
  markAllAsRead: async (): Promise<{ message: string; count: number }> => {
    const response = await api.post('/notifications/mark-all-read')
    return response.data
  },

  // 删除通知
  deleteNotification: async (notificationId: number): Promise<{ message: string }> => {
    const response = await api.delete(`/notifications/${notificationId}`)
    return response.data
  },

  // 清空所有通知
  clearAll: async (): Promise<{ message: string; count: number }> => {
    const response = await api.post('/notifications/clear-all')
    return response.data
  },
}

export default notificationService
