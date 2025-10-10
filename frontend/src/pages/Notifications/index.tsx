import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import notificationService, { Notification } from '@/services/notificationService'
import './style.css'

const NotificationsPage: React.FC = () => {
  const [page, setPage] = useState(1)
  const [filter, setFilter] = useState<{ type?: string; is_read?: boolean }>({})
  const queryClient = useQueryClient()

  // 获取通知列表
  const { data, isLoading } = useQuery({
    queryKey: ['notifications', page, filter],
    queryFn: () =>
      notificationService.getNotifications({
        page,
        page_size: 20,
        ...filter,
      }),
  })

  // 标记为已读
  const markAsReadMutation = useMutation({
    mutationFn: notificationService.markAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      queryClient.invalidateQueries({ queryKey: ['notification-stats'] })
    },
  })

  // 标记所有为已读
  const markAllAsReadMutation = useMutation({
    mutationFn: notificationService.markAllAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      queryClient.invalidateQueries({ queryKey: ['notification-stats'] })
    },
  })

  // 删除通知
  const deleteNotificationMutation = useMutation({
    mutationFn: notificationService.deleteNotification,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      queryClient.invalidateQueries({ queryKey: ['notification-stats'] })
    },
  })

  // 清空所有通知
  const clearAllMutation = useMutation({
    mutationFn: notificationService.clearAll,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      queryClient.invalidateQueries({ queryKey: ['notification-stats'] })
    },
  })

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.is_read) {
      markAsReadMutation.mutate(notification.id)
    }
  }

  const handleDelete = (e: React.MouseEvent, notificationId: number) => {
    e.preventDefault()
    e.stopPropagation()
    if (confirm('确定要删除这条通知吗?')) {
      deleteNotificationMutation.mutate(notificationId)
    }
  }

  const handleClearAll = () => {
    if (confirm('确定要清空所有通知吗?')) {
      clearAllMutation.mutate()
    }
  }

  const totalPages = data ? Math.ceil(data.total / 20) : 0

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="notifications-page">
        <div className="notifications-container">
          {/* 头部 */}
          <div className="notifications-header">
            <h1>通知中心</h1>
            <div className="notifications-actions">
              {data && data.unread_count > 0 && (
                <button
                  className="btn-secondary"
                  onClick={() => markAllAsReadMutation.mutate()}
                  disabled={markAllAsReadMutation.isPending}
                >
                  全部已读
                </button>
              )}
              {data && data.total > 0 && (
                <button
                  className="btn-danger"
                  onClick={handleClearAll}
                  disabled={clearAllMutation.isPending}
                >
                  清空通知
                </button>
              )}
            </div>
          </div>

          {/* 筛选器 */}
          <div className="notifications-filters">
            <button
              className={`filter-btn ${!filter.is_read && filter.is_read !== false ? 'active' : ''}`}
              onClick={() => setFilter({})}
            >
              全部 ({data?.total || 0})
            </button>
            <button
              className={`filter-btn ${filter.is_read === false ? 'active' : ''}`}
              onClick={() => setFilter({ is_read: false })}
            >
              未读 ({data?.unread_count || 0})
            </button>
            <button
              className={`filter-btn ${filter.is_read === true ? 'active' : ''}`}
              onClick={() => setFilter({ is_read: true })}
            >
              已读
            </button>
          </div>

          {/* 通知列表 */}
          <div className="notifications-list">
            {isLoading ? (
              <div className="notifications-loading">加载中...</div>
            ) : data?.notifications.length === 0 ? (
              <div className="notifications-empty">
                <svg
                  className="empty-icon"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                  />
                </svg>
                <p>暂无通知</p>
              </div>
            ) : (
              data?.notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`notification-item ${
                    !notification.is_read ? 'notification-item--unread' : ''
                  }`}
                >
                  {notification.link ? (
                    <Link
                      to={notification.link}
                      className="notification-content"
                      onClick={() => handleNotificationClick(notification)}
                    >
                      <NotificationContent notification={notification} />
                    </Link>
                  ) : (
                    <div
                      className="notification-content"
                      onClick={() => handleNotificationClick(notification)}
                    >
                      <NotificationContent notification={notification} />
                    </div>
                  )}

                  <button
                    className="notification-delete"
                    onClick={(e) => handleDelete(e, notification.id)}
                    aria-label="删除"
                  >
                    <svg
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      width="16"
                      height="16"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </div>
              ))
            )}
          </div>

          {/* 分页 */}
          {totalPages > 1 && (
            <div className="notifications-pagination">
              <button
                className="pagination-btn"
                disabled={page === 1}
                onClick={() => setPage(page - 1)}
              >
                上一页
              </button>
              <span className="pagination-info">
                第 {page} / {totalPages} 页
              </span>
              <button
                className="pagination-btn"
                disabled={page === totalPages}
                onClick={() => setPage(page + 1)}
              >
                下一页
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// 通知内容组件
const NotificationContent: React.FC<{ notification: Notification }> = ({
  notification,
}) => {
  return (
    <>
      <div className="notification-icon">
        <NotificationIcon type={notification.type} />
      </div>
      <div className="notification-body">
        <div className="notification-title">{notification.title}</div>
        <div className="notification-text">{notification.content}</div>
        <div className="notification-time">{formatTime(notification.created_at)}</div>
      </div>
      {!notification.is_read && <div className="notification-unread-dot"></div>}
    </>
  )
}

// 通知图标
const NotificationIcon: React.FC<{ type: string }> = ({ type }) => {
  switch (type) {
    case 'comment_reply':
      return (
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
      )
    case 'video_published':
      return (
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
          />
        </svg>
      )
    case 'system_announcement':
      return (
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z"
          />
        </svg>
      )
    default:
      return (
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      )
  }
}

// 时间格式化
function formatTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 7) {
    return date.toLocaleString('zh-CN')
  } else if (days > 0) {
    return `${days}天前`
  } else if (hours > 0) {
    return `${hours}小时前`
  } else if (minutes > 0) {
    return `${minutes}分钟前`
  } else {
    return '刚刚'
  }
}

export default NotificationsPage
