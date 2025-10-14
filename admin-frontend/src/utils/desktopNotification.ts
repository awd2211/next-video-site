/**
 * 桌面通知工具
 * 使用浏览器 Notification API 显示系统通知
 */

export type NotificationSeverity = 'info' | 'warning' | 'error' | 'critical'

interface DesktopNotificationOptions {
  title: string
  body: string
  severity?: NotificationSeverity
  icon?: string
  badge?: string
  tag?: string
  link?: string
  requireInteraction?: boolean
  onClick?: () => void
}

class DesktopNotificationManager {
  private static instance: DesktopNotificationManager
  private permission: NotificationPermission = 'default'
  private soundEnabled: boolean = true
  private audioCache: Map<string, HTMLAudioElement> = new Map()

  private constructor() {
    this.checkPermission()
    this.preloadSounds()
  }

  public static getInstance(): DesktopNotificationManager {
    if (!DesktopNotificationManager.instance) {
      DesktopNotificationManager.instance = new DesktopNotificationManager()
    }
    return DesktopNotificationManager.instance
  }

  /**
   * 检查通知权限
   */
  private checkPermission() {
    if ('Notification' in window) {
      this.permission = Notification.permission
    }
  }

  /**
   * 预加载声音文件
   */
  private preloadSounds() {
    const sounds = {
      info: '/sounds/notification.mp3',
      warning: '/sounds/warning.mp3',
      error: '/sounds/error.mp3',
      critical: '/sounds/critical.mp3',
    }

    Object.entries(sounds).forEach(([key, path]) => {
      const audio = new Audio(path)
      audio.preload = 'auto'
      // 设置不同严重程度的音量
      audio.volume = key === 'critical' ? 0.8 : key === 'error' ? 0.7 : 0.5
      this.audioCache.set(key, audio)
    })
  }

  /**
   * 请求通知权限
   */
  public async requestPermission(): Promise<NotificationPermission> {
    if (!('Notification' in window)) {
      console.warn('此浏览器不支持桌面通知')
      return 'denied'
    }

    if (this.permission === 'granted') {
      return 'granted'
    }

    try {
      this.permission = await Notification.requestPermission()
      return this.permission
    } catch (error) {
      console.error('请求通知权限失败:', error)
      return 'denied'
    }
  }

  /**
   * 播放通知声音
   */
  public playSound(severity: NotificationSeverity = 'info') {
    if (!this.soundEnabled) return

    const audio = this.audioCache.get(severity) || this.audioCache.get('info')
    if (audio) {
      // 重置播放位置
      audio.currentTime = 0
      audio.play().catch((err) => {
        console.log('声音播放失败 (可能需要用户交互):', err)
      })
    }
  }

  /**
   * 显示桌面通知
   */
  public async show(options: DesktopNotificationOptions): Promise<Notification | null> {
    // 检查权限
    if (this.permission !== 'granted') {
      const permission = await this.requestPermission()
      if (permission !== 'granted') {
        console.warn('桌面通知权限被拒绝')
        return null
      }
    }

    const {
      title,
      body,
      severity = 'info',
      icon = '/logo.png',
      badge = '/badge.png',
      tag,
      link,
      requireInteraction,
      onClick,
    } = options

    try {
      // 播放声音
      this.playSound(severity)

      // 创建通知
      const notification = new Notification(title, {
        body,
        icon,
        badge,
        tag: tag || `notification-${Date.now()}`,
        requireInteraction: requireInteraction ?? (severity === 'critical' || severity === 'error'),
        silent: false, // 使用系统默认声音
      })

      // 点击事件
      notification.onclick = () => {
        window.focus()
        if (onClick) {
          onClick()
        } else if (link) {
          window.location.href = link
        }
        notification.close()
      }

      // 自动关闭 (除了 critical 和 error)
      if (severity !== 'critical' && severity !== 'error') {
        setTimeout(() => {
          notification.close()
        }, 5000)
      }

      return notification
    } catch (error) {
      console.error('显示桌面通知失败:', error)
      return null
    }
  }

  /**
   * 启用/禁用声音
   */
  public setSoundEnabled(enabled: boolean) {
    this.soundEnabled = enabled
  }

  /**
   * 检查是否支持桌面通知
   */
  public isSupported(): boolean {
    return 'Notification' in window
  }

  /**
   * 获取当前权限状态
   */
  public getPermission(): NotificationPermission {
    return this.permission
  }

  /**
   * 震动提醒 (移动端)
   */
  public vibrate(severity: NotificationSeverity = 'info') {
    if (!('vibrate' in navigator)) return

    const patterns: Record<NotificationSeverity, number[]> = {
      info: [100],
      warning: [100, 50, 100],
      error: [200, 100, 200],
      critical: [200, 100, 200, 100, 200],
    }

    navigator.vibrate(patterns[severity])
  }
}

// 导出单例
export const desktopNotification = DesktopNotificationManager.getInstance()

// 便捷方法
export const showDesktopNotification = (options: DesktopNotificationOptions) => {
  return desktopNotification.show(options)
}

export const requestNotificationPermission = () => {
  return desktopNotification.requestPermission()
}

export const isDesktopNotificationSupported = () => {
  return desktopNotification.isSupported()
}

export const getNotificationPermission = () => {
  return desktopNotification.getPermission()
}
