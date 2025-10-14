/**
 * Admin Notification Service
 * 管理员通知服务 - 对接后端管理员通知API
 */
import axios from '@/utils/axios'

export interface AdminNotification {
  id: number
  admin_user_id: number | null
  type: string
  title: string
  content: string
  severity: 'info' | 'warning' | 'error' | 'critical'
  related_type: string | null
  related_id: number | null
  link: string | null
  is_read: boolean
  created_at: string
  read_at: string | null
}

export interface AdminNotificationListResponse {
  notifications: AdminNotification[]
  total: number
  page: number
  page_size: number
  pages: number
  unread_count: number
}

export interface AdminNotificationStats {
  total: number
  unread: number
  read: number
  by_severity: Record<string, number>
}

export interface GetNotificationsParams {
  page?: number
  page_size?: number
  type?: string
  severity?: string
  is_read?: boolean
}

/**
 * 获取管理员通知列表
 */
export async function getAdminNotifications(
  params: GetNotificationsParams = {}
): Promise<AdminNotificationListResponse> {
  const response = await axios.get<AdminNotificationListResponse>(
    '/api/v1/admin/notifications',
    { params }
  )
  return response.data
}

/**
 * 获取管理员通知统计
 */
export async function getAdminNotificationStats(): Promise<AdminNotificationStats> {
  const response = await axios.get<AdminNotificationStats>('/api/v1/admin/notifications/stats')
  return response.data
}

/**
 * 标记单个通知为已读
 */
export async function markNotificationAsRead(notificationId: number): Promise<AdminNotification> {
  const response = await axios.patch<AdminNotification>(
    `/api/v1/admin/notifications/${notificationId}`
  )
  return response.data
}

/**
 * 标记所有通知为已读
 */
export async function markAllNotificationsAsRead(): Promise<{ message: string; count: number }> {
  const response = await axios.post<{ message: string; count: number }>(
    '/api/v1/admin/notifications/mark-all-read'
  )
  return response.data
}

/**
 * 删除单个通知
 */
export async function deleteNotification(notificationId: number): Promise<{ message: string }> {
  const response = await axios.delete<{ message: string }>(
    `/api/v1/admin/notifications/${notificationId}`
  )
  return response.data
}

/**
 * 清空所有通知
 */
export async function clearAllNotifications(): Promise<{ message: string; count: number }> {
  const response = await axios.post<{ message: string; count: number }>(
    '/api/v1/admin/notifications/clear-all'
  )
  return response.data
}

/**
 * 创建测试通知
 */
export async function createTestNotification(): Promise<{ message: string }> {
  const response = await axios.post<{ message: string }>(
    '/api/v1/admin/notifications/test-notification'
  )
  return response.data
}
