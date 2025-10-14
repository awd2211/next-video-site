/**
 * 安全工具函数测试
 */

import { describe, it, expect } from 'vitest'
import {
  sanitizeHTML,
  sanitizeText,
  sanitizeInput,
  isValidURL,
  isValidEmail,
  isValidUsername,
  sanitizeFilename,
  sanitizeSearchQuery,
} from '../security'

describe('Security Utils', () => {
  describe('sanitizeHTML', () => {
    it('should allow safe HTML tags', () => {
      const input = '<p>Hello <strong>World</strong></p>'
      const result = sanitizeHTML(input)
      expect(result).toContain('<p>')
      expect(result).toContain('<strong>')
    })

    it('should remove dangerous script tags', () => {
      const input = '<p>Hello</p><script>alert("XSS")</script>'
      const result = sanitizeHTML(input)
      expect(result).not.toContain('<script>')
      expect(result).toContain('<p>Hello</p>')
    })

    it('should remove event handlers', () => {
      const input = '<p onclick="alert(1)">Click me</p>'
      const result = sanitizeHTML(input)
      expect(result).not.toContain('onclick')
    })

    it('should sanitize href attributes', () => {
      const input = '<a href="javascript:alert(1)">Link</a>'
      const result = sanitizeHTML(input)
      expect(result).not.toContain('javascript:')
    })
  })

  describe('sanitizeText', () => {
    it('should remove all HTML tags', () => {
      const input = '<p>Hello <strong>World</strong></p>'
      const result = sanitizeText(input)
      expect(result).toBe('Hello World')
    })

    it('should handle empty strings', () => {
      expect(sanitizeText('')).toBe('')
    })
  })

  describe('sanitizeInput', () => {
    it('should trim whitespace', () => {
      const input = '  Hello World  '
      const result = sanitizeInput(input)
      expect(result).toBe('Hello World')
    })

    it('should remove control characters', () => {
      const input = 'Hello\x00\x1FWorld'
      const result = sanitizeInput(input)
      expect(result).toBe('HelloWorld')
    })

    it('should remove zero-width characters', () => {
      const input = 'Hello\u200B\u200CWorld'
      const result = sanitizeInput(input)
      expect(result).toBe('HelloWorld')
    })

    it('should truncate to max length', () => {
      const input = 'A'.repeat(100)
      const result = sanitizeInput(input, 50)
      expect(result).toHaveLength(50)
    })
  })

  describe('isValidURL', () => {
    it('should accept valid HTTP URLs', () => {
      expect(isValidURL('http://example.com')).toBe(true)
      expect(isValidURL('http://example.com/path')).toBe(true)
    })

    it('should accept valid HTTPS URLs', () => {
      expect(isValidURL('https://example.com')).toBe(true)
      expect(isValidURL('https://example.com/path?query=1')).toBe(true)
    })

    it('should accept mailto URLs', () => {
      expect(isValidURL('mailto:test@example.com')).toBe(true)
    })

    it('should reject invalid protocols', () => {
      expect(isValidURL('javascript:alert(1)')).toBe(false)
      expect(isValidURL('data:text/html,<script>alert(1)</script>')).toBe(false)
      expect(isValidURL('ftp://example.com')).toBe(false)
    })

    it('should reject malformed URLs', () => {
      expect(isValidURL('not a url')).toBe(false)
      expect(isValidURL('')).toBe(false)
      expect(isValidURL('//example.com')).toBe(false)
    })
  })

  describe('isValidEmail', () => {
    it('should accept valid email addresses', () => {
      expect(isValidEmail('test@example.com')).toBe(true)
      expect(isValidEmail('user.name+tag@example.co.uk')).toBe(true)
    })

    it('should reject invalid email addresses', () => {
      expect(isValidEmail('invalid')).toBe(false)
      expect(isValidEmail('@example.com')).toBe(false)
      expect(isValidEmail('test@')).toBe(false)
      expect(isValidEmail('test @example.com')).toBe(false)
      expect(isValidEmail('')).toBe(false)
    })
  })

  describe('isValidUsername', () => {
    it('should accept valid usernames', () => {
      expect(isValidUsername('john_doe')).toBe(true)
      expect(isValidUsername('user123')).toBe(true)
      expect(isValidUsername('张三李')).toBe(true) // 3个中文字符
      expect(isValidUsername('user用户')).toBe(true) // 混合
    })

    it('should reject usernames that are too short', () => {
      expect(isValidUsername('ab')).toBe(false)
    })

    it('should reject usernames that are too long', () => {
      expect(isValidUsername('a'.repeat(31))).toBe(false)
    })

    it('should reject usernames with invalid characters', () => {
      expect(isValidUsername('user@name')).toBe(false)
      expect(isValidUsername('user name')).toBe(false)
      expect(isValidUsername('user-name')).toBe(false)
    })
  })

  describe('sanitizeFilename', () => {
    it('should remove dangerous characters', () => {
      const input = 'test<file>.txt'
      const result = sanitizeFilename(input)
      expect(result).toBe('test_file_.txt')
    })

    it('should remove path traversal attempts', () => {
      const input = '../../../etc/passwd'
      const result = sanitizeFilename(input)
      expect(result).not.toContain('..')
    })

    it('should truncate long filenames', () => {
      const longName = 'a'.repeat(300) + '.txt'
      const result = sanitizeFilename(longName)
      expect(result.length).toBeLessThanOrEqual(255)
    })

    it('should preserve file extension when truncating', () => {
      const longName = 'a'.repeat(300) + '.txt'
      const result = sanitizeFilename(longName)
      expect(result).toMatch(/\.txt$/)
    })
  })

  describe('sanitizeSearchQuery', () => {
    it('should remove special SQL characters', () => {
      const input = "test'; DROP TABLE users--"
      const result = sanitizeSearchQuery(input)
      expect(result).not.toContain("'")
      expect(result).not.toContain(';')
    })

    it('should trim whitespace', () => {
      const input = '  search term  '
      const result = sanitizeSearchQuery(input)
      expect(result).toBe('search term')
    })

    it('should truncate to max length', () => {
      const input = 'a'.repeat(150)
      const result = sanitizeSearchQuery(input)
      expect(result).toHaveLength(100)
    })
  })
})

