/**
 * 通知偏好设置 Hook
 * 管理用户的通知偏好（声音、桌面通知、免打扰等）
 */
import { useState, useEffect } from 'react'

export interface NotificationPreferences {
  enableSound: boolean
  enableDesktopNotification: boolean
  enableVibration: boolean
  enabledTypes: string[]
  mutedTypes: string[]
  quietHours: {
    enabled: boolean
    startTime: string // "22:00"
    endTime: string // "08:00"
  }
  severityFilter: {
    info: boolean
    warning: boolean
    error: boolean
    critical: boolean
  }
  notificationPosition: 'topRight' | 'topLeft' | 'bottomRight' | 'bottomLeft'
  maxVisibleNotifications: number
}

const DEFAULT_PREFERENCES: NotificationPreferences = {
  enableSound: true,
  enableDesktopNotification: true,
  enableVibration: false,
  enabledTypes: ['*'], // '*' 表示所有类型
  mutedTypes: [],
  quietHours: {
    enabled: false,
    startTime: '22:00',
    endTime: '08:00',
  },
  severityFilter: {
    info: true,
    warning: true,
    error: true,
    critical: true,
  },
  notificationPosition: 'topRight',
  maxVisibleNotifications: 3,
}

const STORAGE_KEY = 'admin_notification_preferences'

export function useNotificationPreferences() {
  const [preferences, setPreferences] = useState<NotificationPreferences>(() => {
    // 从 localStorage 读取
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      try {
        return { ...DEFAULT_PREFERENCES, ...JSON.parse(stored) }
      } catch (error) {
        console.error('解析通知偏好设置失败:', error)
      }
    }
    return DEFAULT_PREFERENCES
  })

  // 保存到 localStorage
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences))
  }, [preferences])

  /**
   * 更新偏好设置
   */
  const updatePreferences = (updates: Partial<NotificationPreferences>) => {
    setPreferences((prev) => ({ ...prev, ...updates }))
  }

  /**
   * 重置为默认设置
   */
  const resetPreferences = () => {
    setPreferences(DEFAULT_PREFERENCES)
  }

  /**
   * 检查是否在免打扰时段
   */
  const isQuietHours = (): boolean => {
    if (!preferences.quietHours.enabled) return false

    const now = new Date()
    const currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`

    const { startTime, endTime } = preferences.quietHours

    // 处理跨天情况 (如 22:00 - 08:00)
    if (startTime > endTime) {
      return currentTime >= startTime || currentTime <= endTime
    } else {
      return currentTime >= startTime && currentTime <= endTime
    }
  }

  /**
   * 检查通知类型是否应该显示
   */
  const shouldShowNotificationType = (type: string): boolean => {
    // 如果在免打扰时段，只显示 critical
    if (isQuietHours() && type !== 'critical') {
      return false
    }

    // 检查是否被静音
    if (preferences.mutedTypes.includes(type)) {
      return false
    }

    // 检查是否在启用列表中
    if (preferences.enabledTypes.includes('*')) {
      return true
    }

    return preferences.enabledTypes.includes(type)
  }

  /**
   * 检查严重程度是否应该显示
   */
  const shouldShowSeverity = (severity: keyof NotificationPreferences['severityFilter']): boolean => {
    return preferences.severityFilter[severity]
  }

  /**
   * 启用/禁用特定通知类型
   */
  const toggleNotificationType = (type: string, enabled: boolean) => {
    setPreferences((prev) => {
      const newEnabledTypes = enabled
        ? [...prev.enabledTypes.filter((t) => t !== '*'), type]
        : prev.enabledTypes.filter((t) => t !== type)

      return {
        ...prev,
        enabledTypes: newEnabledTypes.length === 0 ? ['*'] : newEnabledTypes,
      }
    })
  }

  /**
   * 静音/取消静音特定通知类型
   */
  const toggleMuteType = (type: string, muted: boolean) => {
    setPreferences((prev) => ({
      ...prev,
      mutedTypes: muted
        ? [...prev.mutedTypes, type]
        : prev.mutedTypes.filter((t) => t !== type),
    }))
  }

  return {
    preferences,
    updatePreferences,
    resetPreferences,
    isQuietHours,
    shouldShowNotificationType,
    shouldShowSeverity,
    toggleNotificationType,
    toggleMuteType,
  }
}
