/**
 * 文件处理工具函数
 */

/**
 * 生成智能重命名建议
 * @param fileName 原始文件名
 * @param existingNames 已存在的文件名列表
 * @returns 建议的新文件名
 */
export function generateSmartRename(fileName: string, existingNames: string[]): string {
  const nameParts = fileName.split('.')
  const extension = nameParts.length > 1 ? nameParts.pop() : ''
  const baseName = nameParts.join('.')

  // 策略1: 添加时间戳
  const timestamp = new Date().getTime()
  const withTimestamp = `${baseName}_${timestamp}`
  if (!existingNames.includes(`${withTimestamp}.${extension}`)) {
    return extension ? `${withTimestamp}.${extension}` : withTimestamp
  }

  // 策略2: 添加递增数字
  let counter = 1
  let newName = `${baseName}(${counter})`
  while (existingNames.includes(`${newName}.${extension}`)) {
    counter++
    newName = `${baseName}(${counter})`
  }

  return extension ? `${newName}.${extension}` : newName
}

/**
 * 检测文件名是否冲突
 * @param fileName 要检查的文件名
 * @param existingFiles 已存在的文件列表
 * @returns 是否存在冲突
 */
export function hasFileNameConflict(fileName: string, existingFiles: { title: string }[]): boolean {
  return existingFiles.some((file) => file.title === fileName)
}

/**
 * 计算文件MD5哈希（用于重复检测）
 * @param file 文件对象
 * @returns Promise<string> MD5哈希值
 */
export async function calculateFileMD5(file: File): Promise<string> {
  // 这里简化处理，实际项目中应该使用 crypto-js 或 spark-md5
  // 我们使用文件名+大小+修改时间作为简单的指纹
  const fingerprint = `${file.name}_${file.size}_${file.lastModified}`
  return btoa(fingerprint)
}

/**
 * 格式化文件大小
 * @param bytes 字节数
 * @returns 格式化后的文件大小字符串
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
}

/**
 * 获取文件扩展名
 * @param fileName 文件名
 * @returns 扩展名（不含点）
 */
export function getFileExtension(fileName: string): string {
  const parts = fileName.split('.')
  return parts.length > 1 ? (parts[parts.length - 1] || '').toLowerCase() : ''
}

/**
 * 获取文件名（不含扩展名）
 * @param fileName 完整文件名
 * @returns 文件名（不含扩展名）
 */
export function getFileNameWithoutExtension(fileName: string): string {
  const parts = fileName.split('.')
  if (parts.length <= 1) return fileName
  parts.pop()
  return parts.join('.')
}

/**
 * 验证文件名是否合法
 * @param fileName 文件名
 * @returns 是否合法
 */
export function isValidFileName(fileName: string): boolean {
  // 不允许的字符: / \ : * ? " < > |
  const invalidChars = /[/\\:*?"<>|]/
  return !invalidChars.test(fileName) && fileName.trim().length > 0
}
