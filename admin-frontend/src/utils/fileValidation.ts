/**
 * 文件上传安全验证工具
 * 用于验证文件类型、大小、文件名等
 */

import { sanitizeFilename } from './security'

export interface FileValidationConfig {
  maxSize?: number          // 最大文件大小（MB）
  allowedTypes?: string[]   // 允许的 MIME 类型
  allowedExtensions?: string[] // 允许的文件扩展名
  checkMimeType?: boolean   // 是否检查 MIME 类型与扩展名匹配
}

export interface FileValidationResult {
  valid: boolean
  error?: string
  sanitizedName?: string
}

/**
 * 验证文件
 * @param file 要验证的文件
 * @param config 验证配置
 * @returns 验证结果
 */
export const validateFile = (
  file: File,
  config: FileValidationConfig = {}
): FileValidationResult => {
  const {
    maxSize = 100, // 默认 100MB
    allowedTypes = [],
    allowedExtensions = [],
    checkMimeType = true,
  } = config

  // 1. 验证文件名
  if (!file.name || file.name.length === 0) {
    return { valid: false, error: '文件名不能为空' }
  }

  if (file.name.length > 255) {
    return { valid: false, error: '文件名过长（最多255个字符）' }
  }

  // 清理文件名
  const sanitizedName = sanitizeFilename(file.name)
  if (sanitizedName !== file.name) {
    console.warn('文件名包含非法字符，已自动清理:', file.name, '->', sanitizedName)
  }

  // 2. 验证文件大小
  const fileSizeMB = file.size / (1024 * 1024)
  if (fileSizeMB > maxSize) {
    return {
      valid: false,
      error: `文件大小超过限制（最大 ${maxSize}MB，当前 ${fileSizeMB.toFixed(2)}MB）`,
    }
  }

  if (file.size === 0) {
    return { valid: false, error: '文件为空' }
  }

  // 3. 验证文件类型（MIME type）
  if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
    return {
      valid: false,
      error: `不支持的文件类型（${file.type || '未知'}）`,
    }
  }

  // 4. 验证文件扩展名
  const extension = getFileExtension(file.name).toLowerCase()
  if (allowedExtensions.length > 0 && !allowedExtensions.includes(extension)) {
    return {
      valid: false,
      error: `不支持的文件扩展名（.${extension}）`,
    }
  }

  // 5. 验证 MIME 类型与扩展名匹配
  if (checkMimeType && allowedExtensions.length > 0) {
    const expectedMimes = getMimeTypesForExtension(extension)
    if (expectedMimes.length > 0 && !expectedMimes.includes(file.type)) {
      return {
        valid: false,
        error: `文件类型与扩展名不匹配（扩展名: .${extension}, MIME: ${file.type}）`,
      }
    }
  }

  return {
    valid: true,
    sanitizedName,
  }
}

/**
 * 获取文件扩展名
 */
export const getFileExtension = (filename: string): string => {
  const lastDot = filename.lastIndexOf('.')
  if (lastDot === -1) return ''
  return filename.slice(lastDot + 1)
}

/**
 * 获取扩展名对应的 MIME 类型
 */
const getMimeTypesForExtension = (extension: string): string[] => {
  const mimeMap: Record<string, string[]> = {
    // 图片
    jpg: ['image/jpeg'],
    jpeg: ['image/jpeg'],
    png: ['image/png'],
    gif: ['image/gif'],
    webp: ['image/webp'],
    svg: ['image/svg+xml'],
    bmp: ['image/bmp'],

    // 视频
    mp4: ['video/mp4'],
    webm: ['video/webm'],
    ogg: ['video/ogg'],
    avi: ['video/x-msvideo'],
    mov: ['video/quicktime'],
    mkv: ['video/x-matroska'],
    flv: ['video/x-flv'],

    // 音频
    mp3: ['audio/mpeg'],
    wav: ['audio/wav'],
    m4a: ['audio/mp4'],

    // 文档
    pdf: ['application/pdf'],
    doc: ['application/msword'],
    docx: ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
    xls: ['application/vnd.ms-excel'],
    xlsx: ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
    ppt: ['application/vnd.ms-powerpoint'],
    pptx: ['application/vnd.openxmlformats-officedocument.presentationml.presentation'],
    txt: ['text/plain'],

    // 压缩文件
    zip: ['application/zip'],
    rar: ['application/x-rar-compressed'],
    '7z': ['application/x-7z-compressed'],
    tar: ['application/x-tar'],
    gz: ['application/gzip'],
  }

  return mimeMap[extension.toLowerCase()] || []
}

/**
 * 预定义的文件验证配置
 */
export const FileValidationPresets = {
  // 视频文件
  video: {
    maxSize: 2048, // 2GB
    allowedTypes: ['video/mp4', 'video/webm', 'video/ogg', 'video/x-msvideo', 'video/quicktime'],
    allowedExtensions: ['mp4', 'webm', 'ogg', 'avi', 'mov'],
    checkMimeType: true,
  },

  // 海报/背景图片
  poster: {
    maxSize: 10, // 10MB
    allowedTypes: ['image/jpeg', 'image/png', 'image/webp'],
    allowedExtensions: ['jpg', 'jpeg', 'png', 'webp'],
    checkMimeType: true,
  },

  // 缩略图
  thumbnail: {
    maxSize: 5, // 5MB
    allowedTypes: ['image/jpeg', 'image/png', 'image/webp'],
    allowedExtensions: ['jpg', 'jpeg', 'png', 'webp'],
    checkMimeType: true,
  },

  // 字幕文件
  subtitle: {
    maxSize: 1, // 1MB
    allowedTypes: ['text/plain', 'application/x-subrip'],
    allowedExtensions: ['srt', 'vtt', 'ass', 'ssa'],
    checkMimeType: false, // 字幕文件 MIME 类型不统一
  },

  // 文档
  document: {
    maxSize: 50, // 50MB
    allowedTypes: ['application/pdf', 'application/msword', 'text/plain'],
    allowedExtensions: ['pdf', 'doc', 'docx', 'txt'],
    checkMimeType: true,
  },
}

/**
 * 批量验证文件
 */
export const validateFiles = (
  files: File[],
  config: FileValidationConfig = {}
): { valid: boolean; errors: string[]; validFiles: File[] } => {
  const errors: string[] = []
  const validFiles: File[] = []

  for (const file of files) {
    const result = validateFile(file, config)
    if (result.valid) {
      validFiles.push(file)
    } else {
      errors.push(`${file.name}: ${result.error}`)
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    validFiles,
  }
}

/**
 * 检查文件是否为图片
 */
export const isImageFile = (file: File): boolean => {
  return file.type.startsWith('image/')
}

/**
 * 检查文件是否为视频
 */
export const isVideoFile = (file: File): boolean => {
  return file.type.startsWith('video/')
}

/**
 * 格式化文件大小
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}
