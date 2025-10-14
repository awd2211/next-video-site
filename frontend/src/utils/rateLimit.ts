/**
 * 前端速率限制工具
 * 用于防止用户过于频繁地执行操作（登录、注册、评论等）
 */

interface RateLimitConfig {
  maxAttempts: number  // 最大尝试次数
  windowMs: number     // 时间窗口（毫秒）
  message?: string     // 自定义错误消息
}

interface RateLimitRecord {
  count: number
  firstAttempt: number
  lastAttempt: number
}

class RateLimiter {
  private storage: Map<string, RateLimitRecord> = new Map()
  private storageKey = 'rate_limit_'

  /**
   * 检查是否超过速率限制
   * @param key 唯一标识符（如 'login', 'comment', 'register'）
   * @param config 速率限制配置
   * @returns 是否允许操作和剩余等待时间
   */
  check(key: string, config: RateLimitConfig): { allowed: boolean; waitTime: number; message: string } {
    const now = Date.now()
    const storageKey = `${this.storageKey}${key}`

    // 尝试从 localStorage 恢复数据（跨标签页共享）
    try {
      const stored = localStorage.getItem(storageKey)
      if (stored) {
        const record: RateLimitRecord = JSON.parse(stored)
        this.storage.set(key, record)
      }
    } catch (e) {
      // localStorage 不可用或数据损坏，忽略
    }

    let record = this.storage.get(key)

    // 如果没有记录或时间窗口已过，创建新记录
    if (!record || now - record.firstAttempt > config.windowMs) {
      record = {
        count: 1,
        firstAttempt: now,
        lastAttempt: now,
      }
      this.storage.set(key, record)
      this.saveToStorage(storageKey, record)
      return {
        allowed: true,
        waitTime: 0,
        message: '',
      }
    }

    // 检查是否超过限制
    if (record.count >= config.maxAttempts) {
      const waitTime = Math.ceil((record.firstAttempt + config.windowMs - now) / 1000)
      return {
        allowed: false,
        waitTime,
        message: config.message || `操作过于频繁，请 ${waitTime} 秒后再试`,
      }
    }

    // 更新记录
    record.count++
    record.lastAttempt = now
    this.storage.set(key, record)
    this.saveToStorage(storageKey, record)

    return {
      allowed: true,
      waitTime: 0,
      message: '',
    }
  }

  /**
   * 重置特定 key 的限制
   * @param key 唯一标识符
   */
  reset(key: string): void {
    this.storage.delete(key)
    try {
      localStorage.removeItem(`${this.storageKey}${key}`)
    } catch (e) {
      // 忽略错误
    }
  }

  /**
   * 清除所有限制记录
   */
  clearAll(): void {
    this.storage.clear()
    try {
      const keys = Object.keys(localStorage)
      keys.forEach((key) => {
        if (key.startsWith(this.storageKey)) {
          localStorage.removeItem(key)
        }
      })
    } catch (e) {
      // 忽略错误
    }
  }

  /**
   * 获取剩余尝试次数
   * @param key 唯一标识符
   * @param maxAttempts 最大尝试次数
   * @returns 剩余次数
   */
  getRemainingAttempts(key: string, maxAttempts: number): number {
    const record = this.storage.get(key)
    if (!record) return maxAttempts
    return Math.max(0, maxAttempts - record.count)
  }

  /**
   * 保存到 localStorage
   */
  private saveToStorage(key: string, record: RateLimitRecord): void {
    try {
      localStorage.setItem(key, JSON.stringify(record))
    } catch (e) {
      // localStorage 不可用，忽略
    }
  }
}

// 导出单例实例
export const rateLimiter = new RateLimiter()

// 预定义的速率限制配置
export const RateLimitConfigs = {
  // 登录：5次/5分钟
  login: {
    maxAttempts: 5,
    windowMs: 5 * 60 * 1000,
    message: '登录尝试过多，请稍后再试',
  },

  // 注册：3次/10分钟
  register: {
    maxAttempts: 3,
    windowMs: 10 * 60 * 1000,
    message: '注册尝试过多，请稍后再试',
  },

  // 评论：10次/1分钟
  comment: {
    maxAttempts: 10,
    windowMs: 60 * 1000,
    message: '评论过于频繁，请稍后再试',
  },

  // 弹幕：20次/1分钟
  danmaku: {
    maxAttempts: 20,
    windowMs: 60 * 1000,
    message: '弹幕发送过于频繁，请稍后再试',
  },

  // 搜索：30次/1分钟
  search: {
    maxAttempts: 30,
    windowMs: 60 * 1000,
    message: '搜索过于频繁，请稍后再试',
  },

  // 密码重置：3次/1小时
  passwordReset: {
    maxAttempts: 3,
    windowMs: 60 * 60 * 1000,
    message: '密码重置请求过多，请1小时后再试',
  },

  // 验证码：10次/5分钟
  captcha: {
    maxAttempts: 10,
    windowMs: 5 * 60 * 1000,
    message: '验证码请求过多，请稍后再试',
  },
}

/**
 * 便捷函数：检查登录速率限制
 */
export const checkLoginRateLimit = () => {
  return rateLimiter.check('login', RateLimitConfigs.login)
}

/**
 * 便捷函数：检查注册速率限制
 */
export const checkRegisterRateLimit = () => {
  return rateLimiter.check('register', RateLimitConfigs.register)
}

/**
 * 便捷函数：检查评论速率限制
 */
export const checkCommentRateLimit = () => {
  return rateLimiter.check('comment', RateLimitConfigs.comment)
}

/**
 * 便捷函数：检查弹幕速率限制
 */
export const checkDanmakuRateLimit = () => {
  return rateLimiter.check('danmaku', RateLimitConfigs.danmaku)
}

/**
 * React Hook：使用速率限制
 */
export const useRateLimit = (key: string, config: RateLimitConfig) => {
  const check = () => rateLimiter.check(key, config)
  const reset = () => rateLimiter.reset(key)
  const getRemainingAttempts = () => rateLimiter.getRemainingAttempts(key, config.maxAttempts)

  return {
    check,
    reset,
    getRemainingAttempts,
  }
}
