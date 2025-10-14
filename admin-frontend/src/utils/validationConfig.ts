/**
 * 统一的表单验证限制常量（管理后台）
 * 用于确保整个应用中的验证规则一致
 */

export const VALIDATION_LIMITS = {
  // 视频相关
  VIDEO_TITLE: { min: 2, max: 500 },
  VIDEO_ORIGINAL_TITLE: { max: 500 },
  VIDEO_DESCRIPTION: { max: 2000 },
  VIDEO_LANGUAGE: { max: 100 },
  
  // 演员/导演
  PERSON_NAME: { min: 1, max: 200 },
  BIOGRAPHY: { max: 1000 },
  
  // 横幅
  BANNER_TITLE: { max: 200 },
  BANNER_DESCRIPTION: { max: 500 },
  
  // 公告
  ANNOUNCEMENT_TITLE: { max: 200 },
  ANNOUNCEMENT_CONTENT: { max: 2000 },
  
  // 剧集
  SERIES_NAME: { max: 500 },
  SERIES_DESCRIPTION: { max: 2000 },
  EPISODE_TITLE: { max: 500 },
  
  // 邮件模板
  EMAIL_SUBJECT: { max: 200 },
  EMAIL_TEMPLATE: { max: 10000 },
  
  // 系统设置
  SETTING_KEY: { max: 100 },
  SETTING_VALUE: { max: 1000 },
  
  // IP黑名单
  IP_REASON: { max: 500 },
  
  // 通用
  URL: { max: 2048 },
  FILENAME: { max: 255 },
} as const

/**
 * 文件大小限制（MB）
 */
export const FILE_SIZE_LIMITS = {
  VIDEO: 2048, // 2GB
  POSTER: 10,
  THUMBNAIL: 5,
  BACKDROP: 15,
  BANNER_IMAGE: 10,
  SUBTITLE: 1,
  DOCUMENT: 50,
} as const

/**
 * 数值范围限制
 */
export const NUMBER_LIMITS = {
  YEAR: { min: 1900, max: 2100 },
  DURATION: { min: 1, max: 10000 }, // 分钟
  SORT_ORDER: { min: -99999, max: 99999 },
  VIDEO_ID: { min: 1, max: 2147483647 },
  RATING: { min: 0, max: 10 },
} as const

