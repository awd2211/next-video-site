/**
 * 统一的表单验证限制常量
 * 用于确保整个应用中的验证规则一致
 */

export const VALIDATION_LIMITS = {
  // 用户相关
  USERNAME: { min: 3, max: 30 },
  EMAIL: { max: 255 },
  PASSWORD: { min: 8, max: 128 },
  
  // 内容相关
  COMMENT: { max: 500 },
  DANMAKU: { max: 100 },
  TITLE: { max: 500 },
  DESCRIPTION: { max: 2000 },
  MESSAGE: { max: 1000 },
  
  // 联系表单
  CONTACT_NAME: { max: 100 },
  CONTACT_SUBJECT: { max: 200 },
  CONTACT_MESSAGE: { max: 2000 },
  
  // 文件相关
  FILENAME: { max: 255 },
  
  // 搜索
  SEARCH_QUERY: { max: 100 },
} as const

/**
 * 文件大小限制（MB）
 */
export const FILE_SIZE_LIMITS = {
  AVATAR: 5,
  IMAGE: 10,
  VIDEO: 2048, // 2GB
  SUBTITLE: 1,
  DOCUMENT: 50,
} as const

/**
 * 验证码配置
 */
export const CAPTCHA_CONFIG = {
  LENGTH: 4,
  REFRESH_INTERVAL: 60000, // 60秒
} as const

