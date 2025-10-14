/**
 * 增强版 WebSocket Context
 * 集成桌面通知、声音提醒、通知偏好设置
 */
import { createContext, useContext, useState, ReactNode, useCallback } from 'react'
import { useWebSocket, TranscodeProgressMessage, TranscodeCompleteMessage, TranscodeFailedMessage } from '@/hooks/useWebSocket'
import { notification } from 'antd'
import { SyncOutlined, CheckCircleOutlined, CloseCircleOutlined, BellOutlined, WarningOutlined, ExclamationCircleOutlined } from '@ant-design/icons'
import { useQueryClient } from '@tanstack/react-query'
import { desktopNotification, NotificationSeverity } from '@/utils/desktopNotification'
import { useNotificationPreferences } from '@/hooks/useNotificationPreferences'

interface WebSocketContextValue {
  isConnected: boolean
  unreadCount: number
  transcodeProgress: Map<number, TranscodeProgressMessage>
  markAsRead: () => void
  adminUnreadCount: number
}

const WebSocketContext = createContext<WebSocketContextValue | undefined>(undefined)

export function useWebSocketContext() {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocketContext must be used within WebSocketProvider')
  }
  return context
}

interface WebSocketProviderProps {
  children: ReactNode
}

export function WebSocketProvider({ children }: WebSocketProviderProps) {
  const queryClient = useQueryClient()
  const { preferences, shouldShowNotificationType, shouldShowSeverity, isQuietHours } = useNotificationPreferences()
  const [unreadCount, setUnreadCount] = useState(0)
  const [adminUnreadCount, setAdminUnreadCount] = useState(0)
  const [transcodeProgress, setTranscodeProgress] = useState<Map<number, TranscodeProgressMessage>>(new Map())

  // 通知去重缓存
  const notificationCache = new Map<string, { count: number; lastTime: number }>()

  /**
   * 检查是否应该显示通知（去重）
   */
  const shouldShowNotification = useCallback((type: string, title: string): boolean => {
    const key = `${type}_${title}`
    const cached = notificationCache.get(key)
    const now = Date.now()

    // 如果 1 分钟内已显示过相同通知，不再显示
    if (cached && (now - cached.lastTime) < 60000) {
      cached.count++
      return false
    }

    notificationCache.set(key, { count: 1, lastTime: now })
    return true
  }, [])

  /**
   * 处理管理员通知
   */
  const handleAdminNotification = useCallback((message: any) => {
    console.log('📢 收到管理员通知:', message)

    // 检查通知偏好
    if (!shouldShowNotificationType(message.notification_type)) {
      console.log('⏭️ 通知类型被过滤:', message.notification_type)
      return
    }

    if (!shouldShowSeverity(message.severity)) {
      console.log('⏭️ 通知严重程度被过滤:', message.severity)
      return
    }

    // 检查是否应该显示（去重）
    if (!shouldShowNotification(message.notification_type, message.title)) {
      console.log('⏭️ 重复通知被过滤')
      return
    }

    // 增加未读计数
    setAdminUnreadCount((prev) => prev + 1)

    // 刷新通知列表
    queryClient.invalidateQueries({ queryKey: ['adminNotifications'] })
    queryClient.invalidateQueries({ queryKey: ['adminNotificationStats'] })

    const severity = message.severity as NotificationSeverity

    // 播放声音
    if (preferences.enableSound && !isQuietHours()) {
      desktopNotification.playSound(severity)
    }

    // 震动提醒 (移动端)
    if (preferences.enableVibration && (severity === 'error' || severity === 'critical')) {
      desktopNotification.vibrate(severity)
    }

    // 显示桌面通知
    if (preferences.enableDesktopNotification) {
      desktopNotification.show({
        title: message.title || '新通知',
        body: message.content,
        severity,
        link: message.link,
        tag: `notification-${message.notification_id}`,
      })
    }

    // 根据严重程度显示不同的应用内通知
    const notificationConfig: any = {
      message: message.title || '新通知',
      description: message.content,
      duration: severity === 'critical' || severity === 'error' ? 0 : 5,
      placement: preferences.notificationPosition,
      onClick: () => {
        if (message.link) {
          window.location.href = message.link
        }
      },
    }

    switch (severity) {
      case 'critical':
      case 'error':
        notification.error({
          ...notificationConfig,
          icon: <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
        })
        break
      case 'warning':
        notification.warning({
          ...notificationConfig,
          icon: <WarningOutlined style={{ color: '#faad14' }} />,
        })
        break
      case 'info':
      default:
        notification.info({
          ...notificationConfig,
          icon: <BellOutlined style={{ color: '#1890ff' }} />,
        })
        break
    }

    // Critical 级别通知：额外处理
    if (severity === 'critical') {
      // 可以在这里添加模态框或其他强提示
      console.warn('🚨 严重通知:', message.title)
    }
  }, [
    preferences,
    shouldShowNotificationType,
    shouldShowSeverity,
    shouldShowNotification,
    isQuietHours,
    queryClient,
  ])

  // 转码进度更新
  const handleTranscodeProgress = useCallback((message: TranscodeProgressMessage) => {
    setTranscodeProgress((prev) => {
      const newMap = new Map(prev)
      newMap.set(message.video_id, message)
      return newMap
    })

    // 如果是开始转码,显示通知
    if (message.progress === 0) {
      notification.info({
        message: '开始转码',
        description: message.message || `视频ID: ${message.video_id}`,
        icon: <SyncOutlined spin style={{ color: '#1890ff' }} />,
        duration: 3,
        placement: preferences.notificationPosition,
      })
      setUnreadCount((prev) => prev + 1)
    }
  }, [preferences.notificationPosition])

  // 转码完成
  const handleTranscodeComplete = useCallback((message: TranscodeCompleteMessage) => {
    // 从进度中移除
    setTranscodeProgress((prev) => {
      const newMap = new Map(prev)
      newMap.delete(message.video_id)
      return newMap
    })

    notification.success({
      message: '转码完成',
      description: (
        <div>
          <div><strong>{message.title}</strong></div>
          <div>格式: {message.format_type.toUpperCase()}</div>
          <div>大小: {formatFileSize(message.file_size)}</div>
        </div>
      ),
      icon: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
      duration: 5,
      placement: preferences.notificationPosition,
    })
    setUnreadCount((prev) => prev + 1)

    // 播放成功音效
    if (preferences.enableSound) {
      desktopNotification.playSound('info')
    }
  }, [preferences])

  // 转码失败
  const handleTranscodeFailed = useCallback((message: TranscodeFailedMessage) => {
    // 从进度中移除
    setTranscodeProgress((prev) => {
      const newMap = new Map(prev)
      newMap.delete(message.video_id)
      return newMap
    })

    notification.error({
      message: '转码失败',
      description: (
        <div>
          <div><strong>{message.title}</strong></div>
          <div style={{ color: '#ff4d4f', fontSize: '12px' }}>
            {message.error.substring(0, 100)}...
          </div>
        </div>
      ),
      icon: <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
      duration: 0,
      placement: preferences.notificationPosition,
    })
    setUnreadCount((prev) => prev + 1)

    // 播放错误音效
    if (preferences.enableSound) {
      desktopNotification.playSound('error')
    }
  }, [preferences])

  // 标记为已读
  const markAsRead = useCallback(() => {
    setUnreadCount(0)
  }, [])

  const { isConnected } = useWebSocket(true, {
    autoConnect: true,
    autoReconnect: true,
    onTranscodeProgress: handleTranscodeProgress,
    onTranscodeComplete: handleTranscodeComplete,
    onTranscodeFailed: handleTranscodeFailed,
    onMessage: (message) => {
      // 处理所有消息类型
      if (message.type === 'admin_notification') {
        handleAdminNotification(message)
      }
    },
    onConnect: () => {
      console.log('✅ WebSocket已连接')

      // 连接成功后，如果有启用桌面通知，确保权限已授予
      if (preferences.enableDesktopNotification && desktopNotification.getPermission() !== 'granted') {
        desktopNotification.requestPermission()
      }
    },
    onDisconnect: () => {
      console.log('❌ WebSocket已断开')
    },
  })

  return (
    <WebSocketContext.Provider
      value={{
        isConnected,
        unreadCount,
        transcodeProgress,
        markAsRead,
        adminUnreadCount,
      }}
    >
      {children}
    </WebSocketContext.Provider>
  )
}

/**
 * 格式化文件大小
 */
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}
