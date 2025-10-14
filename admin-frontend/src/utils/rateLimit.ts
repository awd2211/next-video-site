/**
 * 管理后台前端速率限制工具
 */

interface RateLimitConfig {
  maxAttempts: number
  windowMs: number
  message?: string
}

interface RateLimitRecord {
  count: number
  firstAttempt: number
  lastAttempt: number
}

class RateLimiter {
  private storage: Map<string, RateLimitRecord> = new Map()
  private storageKey = 'admin_rate_limit_'

  check(key: string, config: RateLimitConfig): { allowed: boolean; waitTime: number; message: string } {
    const now = Date.now()
    const storageKey = `${this.storageKey}${key}`

    try {
      const stored = localStorage.getItem(storageKey)
      if (stored) {
        const record: RateLimitRecord = JSON.parse(stored)
        this.storage.set(key, record)
      }
    } catch (e) {
      // Ignore
    }

    let record = this.storage.get(key)

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

    if (record.count >= config.maxAttempts) {
      const waitTime = Math.ceil((record.firstAttempt + config.windowMs - now) / 1000)
      return {
        allowed: false,
        waitTime,
        message: config.message || `操作过于频繁，请 ${waitTime} 秒后再试`,
      }
    }

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

  reset(key: string): void {
    this.storage.delete(key)
    try {
      localStorage.removeItem(`${this.storageKey}${key}`)
    } catch (e) {
      // Ignore
    }
  }

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
      // Ignore
    }
  }

  private saveToStorage(key: string, record: RateLimitRecord): void {
    try {
      localStorage.setItem(key, JSON.stringify(record))
    } catch (e) {
      // Ignore
    }
  }
}

export const rateLimiter = new RateLimiter()

// 管理后台速率限制配置
export const RateLimitConfigs = {
  // 登录：5次/5分钟
  login: {
    maxAttempts: 5,
    windowMs: 5 * 60 * 1000,
    message: '登录尝试过多，请5分钟后再试',
  },

  // 密码重置：3次/1小时
  passwordReset: {
    maxAttempts: 3,
    windowMs: 60 * 60 * 1000,
    message: '密码重置请求过多，请1小时后再试',
  },

  // 批量操作：10次/1分钟
  batchOperation: {
    maxAttempts: 10,
    windowMs: 60 * 1000,
    message: '批量操作过于频繁，请稍后再试',
  },

  // API测试：20次/1分钟
  apiTest: {
    maxAttempts: 20,
    windowMs: 60 * 1000,
    message: 'API测试请求过多，请稍后再试',
  },
}

export const checkLoginRateLimit = () => {
  return rateLimiter.check('login', RateLimitConfigs.login)
}
