/**
 * 文件验证工具测试
 */

import { describe, it, expect } from 'vitest'
import {
  validateFile,
  validateFiles,
  isImageFile,
  isVideoFile,
  formatFileSize,
  getFileExtension,
  FileValidationPresets,
} from '../fileValidation'

describe('File Validation Utils', () => {
  // 创建模拟文件对象
  const createMockFile = (name: string, type: string, size: number): File => {
    const content = new Array(size).fill('a').join('')
    const file = new File([content], name, { type })
    Object.defineProperty(file, 'size', {
      value: size,
      writable: false,
    })
    return file
  }

  describe('validateFile', () => {
    it('should accept valid image file', () => {
      const file = createMockFile('test.jpg', 'image/jpeg', 1024 * 1024) // 1MB
      const result = validateFile(file, FileValidationPresets.image)
      expect(result.valid).toBe(true)
    })

    it('should reject file that is too large', () => {
      const file = createMockFile('large.jpg', 'image/jpeg', 20 * 1024 * 1024) // 20MB
      const result = validateFile(file, FileValidationPresets.image) // max 10MB
      expect(result.valid).toBe(false)
      expect(result.error).toContain('超过限制')
    })

    it('should reject empty file', () => {
      const file = createMockFile('empty.jpg', 'image/jpeg', 0)
      const result = validateFile(file)
      expect(result.valid).toBe(false)
      expect(result.error).toContain('为空')
    })

    it('should reject invalid file type', () => {
      const file = createMockFile('test.exe', 'application/x-msdownload', 1024)
      const result = validateFile(file, FileValidationPresets.image)
      expect(result.valid).toBe(false)
    })

    it('should sanitize dangerous filenames', () => {
      const file = createMockFile('../../../etc/passwd', 'text/plain', 1024)
      const result = validateFile(file)
      expect(result.sanitizedName).toBeDefined()
      expect(result.sanitizedName).not.toContain('..')
    })

    it('should reject filename that is too long', () => {
      const longName = 'a'.repeat(300) + '.jpg'
      const file = createMockFile(longName, 'image/jpeg', 1024)
      const result = validateFile(file)
      expect(result.valid).toBe(false)
      expect(result.error).toContain('过长')
    })
  })

  describe('validateFiles', () => {
    it('should validate multiple files', () => {
      const files = [
        createMockFile('test1.jpg', 'image/jpeg', 1024 * 1024),
        createMockFile('test2.png', 'image/png', 2 * 1024 * 1024),
      ]
      const result = validateFiles(files, FileValidationPresets.image)
      expect(result.valid).toBe(true)
      expect(result.validFiles).toHaveLength(2)
      expect(result.errors).toHaveLength(0)
    })

    it('should collect errors for invalid files', () => {
      const files = [
        createMockFile('valid.jpg', 'image/jpeg', 1024 * 1024),
        createMockFile('too-large.jpg', 'image/jpeg', 20 * 1024 * 1024),
        createMockFile('wrong-type.exe', 'application/x-msdownload', 1024),
      ]
      const result = validateFiles(files, FileValidationPresets.image)
      expect(result.valid).toBe(false)
      expect(result.validFiles).toHaveLength(1)
      expect(result.errors).toHaveLength(2)
    })
  })

  describe('isImageFile', () => {
    it('should identify image files', () => {
      const imageFile = createMockFile('test.jpg', 'image/jpeg', 1024)
      expect(isImageFile(imageFile)).toBe(true)
    })

    it('should reject non-image files', () => {
      const videoFile = createMockFile('test.mp4', 'video/mp4', 1024)
      expect(isImageFile(videoFile)).toBe(false)
    })
  })

  describe('isVideoFile', () => {
    it('should identify video files', () => {
      const videoFile = createMockFile('test.mp4', 'video/mp4', 1024)
      expect(isVideoFile(videoFile)).toBe(true)
    })

    it('should reject non-video files', () => {
      const imageFile = createMockFile('test.jpg', 'image/jpeg', 1024)
      expect(isVideoFile(imageFile)).toBe(false)
    })
  })

  describe('formatFileSize', () => {
    it('should format bytes correctly', () => {
      expect(formatFileSize(0)).toBe('0 B')
      expect(formatFileSize(1024)).toBe('1 KB')
      expect(formatFileSize(1024 * 1024)).toBe('1 MB')
      expect(formatFileSize(1024 * 1024 * 1024)).toBe('1 GB')
    })

    it('should format with decimals', () => {
      expect(formatFileSize(1536)).toBe('1.5 KB')
      expect(formatFileSize(1.5 * 1024 * 1024)).toBe('1.5 MB')
    })
  })

  describe('getFileExtension', () => {
    it('should extract file extension', () => {
      expect(getFileExtension('test.jpg')).toBe('jpg')
      expect(getFileExtension('document.pdf')).toBe('pdf')
      expect(getFileExtension('archive.tar.gz')).toBe('gz')
    })

    it('should handle files without extension', () => {
      expect(getFileExtension('noextension')).toBe('')
    })

    it('should handle hidden files', () => {
      expect(getFileExtension('.gitignore')).toBe('gitignore')
    })
  })

  describe('FileValidationPresets', () => {
    it('should have avatar preset', () => {
      expect(FileValidationPresets.avatar).toBeDefined()
      expect(FileValidationPresets.avatar.maxSize).toBe(5)
      expect(FileValidationPresets.avatar.allowedTypes).toContain('image/jpeg')
    })

    it('should have video preset', () => {
      expect(FileValidationPresets.video).toBeDefined()
      expect(FileValidationPresets.video.maxSize).toBe(2048)
      expect(FileValidationPresets.video.allowedTypes).toContain('video/mp4')
    })

    it('should have image preset', () => {
      expect(FileValidationPresets.image).toBeDefined()
      expect(FileValidationPresets.image.maxSize).toBe(10)
    })
  })
})

