/**
 * 安全工具函数库
 * 提供 XSS 防护、输入清理、敏感词过滤等功能
 */

import DOMPurify, { type Config as DOMPurifyConfig } from 'dompurify'

/**
 * 清理 HTML 内容，防止 XSS 攻击
 * @param dirty 待清理的 HTML 字符串
 * @param config DOMPurify 配置选项
 * @returns 清理后的安全 HTML 字符串
 */
export const sanitizeHTML = (
  dirty: string,
  config?: DOMPurifyConfig
): string => {
  // 默认配置：允许基本格式化标签，移除危险内容
  const defaultConfig: DOMPurifyConfig = {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
    ALLOWED_ATTR: ['href', 'target'],
    ALLOW_DATA_ATTR: false,
    ALLOWED_URI_REGEXP: /^(?:https?|mailto):/i,
  }

  return DOMPurify.sanitize(dirty, { ...defaultConfig, ...config }) as unknown as string
}

/**
 * 清理纯文本内容（完全移除 HTML 标签）
 * @param text 待清理的文本
 * @returns 纯文本字符串
 */
export const sanitizeText = (text: string): string => {
  return DOMPurify.sanitize(text, {
    ALLOWED_TAGS: [],
    ALLOWED_ATTR: [],
  })
}

/**
 * 清理用户输入，移除首尾空白和危险字符
 * @param input 用户输入
 * @param maxLength 最大长度（可选）
 * @returns 清理后的字符串
 */
export const sanitizeInput = (input: string, maxLength?: number): string => {
  let cleaned = input.trim()

  // 移除控制字符和零宽字符
  cleaned = cleaned.replace(/[\x00-\x1F\x7F-\x9F\u200B-\u200D\uFEFF]/g, '')

  // 如果指定了最大长度，进行截断
  if (maxLength && cleaned.length > maxLength) {
    cleaned = cleaned.substring(0, maxLength)
  }

  return cleaned
}

/**
 * 验证 URL 是否安全
 * @param url 待验证的 URL
 * @returns 是否是安全的 URL
 */
export const isValidURL = (url: string): boolean => {
  try {
    const urlObj = new URL(url)
    // 只允许 http, https, mailto 协议
    const allowedProtocols = ['http:', 'https:', 'mailto:']
    return allowedProtocols.includes(urlObj.protocol)
  } catch {
    return false
  }
}

/**
 * 验证邮箱格式
 * @param email 邮箱地址
 * @returns 是否是有效的邮箱
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * 验证用户名格式
 * @param username 用户名
 * @returns 是否是有效的用户名
 */
export const isValidUsername = (username: string): boolean => {
  // 3-30个字符，只允许字母、数字、下划线、中文
  const usernameRegex = /^[\w\u4e00-\u9fa5]{3,30}$/
  return usernameRegex.test(username)
}

/**
 * 敏感词列表（基础版本，实际项目应该从后端获取）
 */
const SENSITIVE_WORDS: string[] = [
  // 这里只是示例，实际应该从配置或API获取
  // '敏感词1', '敏感词2'
]

/**
 * 检查文本是否包含敏感词
 * @param text 待检查的文本
 * @returns 包含的敏感词列表
 */
export const detectSensitiveWords = (text: string): string[] => {
  const found: string[] = []
  const lowerText = text.toLowerCase()

  for (const word of SENSITIVE_WORDS) {
    if (lowerText.includes(word.toLowerCase())) {
      found.push(word)
    }
  }

  return found
}

/**
 * 过滤敏感词（用 * 替换）
 * @param text 待过滤的文本
 * @returns 过滤后的文本
 */
export const filterSensitiveWords = (text: string): string => {
  let filtered = text

  for (const word of SENSITIVE_WORDS) {
    const regex = new RegExp(word, 'gi')
    filtered = filtered.replace(regex, '*'.repeat(word.length))
  }

  return filtered
}

/**
 * 验证文件名是否安全
 * @param filename 文件名
 * @returns 是否是安全的文件名
 */
export const isValidFilename = (filename: string): boolean => {
  // 检查长度
  if (filename.length === 0 || filename.length > 255) {
    return false
  }

  // 不允许路径遍历字符
  if (filename.includes('..') || filename.includes('/') || filename.includes('\\')) {
    return false
  }

  // 不允许空字节
  if (filename.includes('\0')) {
    return false
  }

  // 不允许控制字符
  if (/[\x00-\x1F\x7F-\x9F]/.test(filename)) {
    return false
  }

  return true
}

/**
 * 清理文件名
 * @param filename 原始文件名
 * @returns 清理后的安全文件名
 */
export const sanitizeFilename = (filename: string): string => {
  let cleaned = filename.trim()

  // 移除危险字符
  cleaned = cleaned.replace(/[<>:"/\\|?*\x00-\x1F\x7F-\x9F]/g, '_')

  // 移除路径遍历
  cleaned = cleaned.replace(/\.\./g, '')

  // 限制长度
  if (cleaned.length > 255) {
    const ext = cleaned.split('.').pop() || ''
    const nameLength = 255 - ext.length - 1
    const name = cleaned.substring(0, nameLength)
    cleaned = `${name}.${ext}`
  }

  return cleaned
}

/**
 * 验证并清理搜索关键词
 * @param query 搜索关键词
 * @returns 清理后的关键词
 */
export const sanitizeSearchQuery = (query: string): string => {
  let cleaned = query.trim()

  // 移除特殊字符，防止 SQL 注入（虽然后端应该已经处理，但前端也应该过滤）
  cleaned = cleaned.replace(/['"<>%&;]/g, '')

  // 限制长度
  if (cleaned.length > 100) {
    cleaned = cleaned.substring(0, 100)
  }

  return cleaned
}

/**
 * 验证密码强度
 * @param password 密码
 * @returns 强度分数 0-100
 */
export const calculatePasswordStrength = (password: string): number => {
  let score = 0

  if (!password) return 0

  // 长度检查
  if (password.length >= 8) score += 25
  if (password.length >= 12) score += 15

  // 包含小写字母
  if (/[a-z]/.test(password)) score += 15

  // 包含大写字母
  if (/[A-Z]/.test(password)) score += 15

  // 包含数字
  if (/[0-9]/.test(password)) score += 15

  // 包含特殊字符
  if (/[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/;'`~]/.test(password)) score += 15

  return Math.min(100, score)
}

/**
 * 防抖函数
 * @param func 要执行的函数
 * @param wait 等待时间（毫秒）
 * @returns 防抖后的函数
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout | null = null

  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

/**
 * 节流函数
 * @param func 要执行的函数
 * @param limit 时间限制（毫秒）
 * @returns 节流后的函数
 */
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean = false

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}
