import React, { useState, useEffect, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import notificationService, { Notification } from '@/services/notificationService'
import './style.css'

const NotificationBell: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const queryClient = useQueryClient()

  // 获取通知统计
  const { data: stats } = useQuery({
    queryKey: ['notification-stats'],
    queryFn: notificationService.getStats,
    refetchInterval: 30000, // 每30秒刷新一次
  })

  // 获取最新5条未读通知
  const { data: notifications } = useQuery({
    queryKey: ['notifications-preview'],
    queryFn: () =>
      notificationService.getNotifications({
        page: 1,
        page_size: 5,
        is_read: false,
      }),
    enabled: isOpen, // 只在打开下拉框时请求
  })

  // 标记为已读
  const markAsReadMutation = useMutation({
    mutationFn: notificationService.markAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notification-stats'] })
      queryClient.invalidateQueries({ queryKey: ['notifications-preview'] })
    },
  })

  // 标记所有为已读
  const markAllAsReadMutation = useMutation({
    mutationFn: notificationService.markAllAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notification-stats'] })
      queryClient.invalidateQueries({ queryKey: ['notifications-preview'] })
    },
  })

  // 点击外部关闭下拉框
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const handleNotificationClick = (notification: Notification) => {
    // 标记为已读
    if (!notification.is_read) {
      markAsReadMutation.mutate(notification.id)
    }
    // 关闭下拉框
    setIsOpen(false)
  }

  const handleMarkAllRead = () => {
    markAllAsReadMutation.mutate()
  }

  const unreadCount = stats?.unread || 0

  return (
    <div className="notification-bell" ref={dropdownRef}>
      <button
        className="notification-bell__button"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="通知"
      >
        <svg
          className="notification-bell__icon"
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
        {unreadCount > 0 && (
          <span className="notification-bell__badge">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="notification-bell__dropdown">
          <div className="notification-bell__header">
            <h3>通知</h3>
            {unreadCount > 0 && (
              <button
                className="notification-bell__mark-all"
                onClick={handleMarkAllRead}
              >
                全部已读
              </button>
            )}
          </div>

          <div className="notification-bell__list">
            {notifications?.notifications.length === 0 ? (
              <div className="notification-bell__empty">暂无新通知</div>
            ) : (
              notifications?.notifications.map((notification) => (
                <Link
                  key={notification.id}
                  to={notification.link || '/notifications'}
                  className={`notification-bell__item ${
                    !notification.is_read ? 'notification-bell__item--unread' : ''
                  }`}
                  onClick={() => handleNotificationClick(notification)}
                >
                  <div className="notification-bell__item-title">
                    {notification.title}
                  </div>
                  <div className="notification-bell__item-content">
                    {notification.content}
                  </div>
                  <div className="notification-bell__item-time">
                    {formatTime(notification.created_at)}
                  </div>
                </Link>
              ))
            )}
          </div>

          <Link
            to="/notifications"
            className="notification-bell__view-all"
            onClick={() => setIsOpen(false)}
          >
            查看全部通知
          </Link>
        </div>
      )}
    </div>
  )
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
    return date.toLocaleDateString('zh-CN')
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

export default NotificationBell
