/**
 * 表单验证规则测试
 */

import { describe, it, expect } from 'vitest'
import { createFormRules } from '../formRules'
import { VALIDATION_LIMITS } from '../validationConfig'

// Mock translation function
const mockT = (key: string, params?: any) => {
  const translations: Record<string, string> = {
    'validation.required': `${params?.field || 'This field'} is required`,
    'validation.field': 'This field',
    'validation.invalidEmail': 'Please enter a valid email address',
    'validation.invalidUrl': 'Please enter a valid URL',
    'validation.invalidUsername': 'Invalid username format',
    'validation.length': `Length should be between ${params?.min} and ${params?.max} characters`,
    'validation.maxLength': `Cannot exceed ${params?.max} characters`,
    'validation.minLength': `At least ${params?.min} characters required`,
    'validation.passwordWeak': 'Password is too weak',
    'validation.passwordMismatch': 'Passwords do not match',
    'validation.captchaInvalid': 'Invalid captcha code',
  }
  return translations[key] || key
}

describe('Form Rules', () => {
  const formRules = createFormRules(mockT)

  describe('required', () => {
    it('should create required rule', () => {
      const rule = formRules.required()
      expect(rule.required).toBe(true)
      expect(rule.message).toContain('required')
    })

    it('should include field name in message', () => {
      const rule = formRules.required('Email')
      expect(rule.message).toContain('Email')
    })
  })

  describe('email', () => {
    it('should validate correct email addresses', async () => {
      const validator = formRules.email.validator
      await expect(validator(null, 'test@example.com')).resolves.toBeUndefined()
      await expect(validator(null, 'user+tag@example.co.uk')).resolves.toBeUndefined()
    })

    it('should reject invalid email addresses', async () => {
      const validator = formRules.email.validator
      await expect(validator(null, 'invalid')).rejects.toThrow()
      await expect(validator(null, '@example.com')).rejects.toThrow()
      await expect(validator(null, 'test@')).rejects.toThrow()
    })

    it('should allow empty values', async () => {
      const validator = formRules.email.validator
      await expect(validator(null, '')).resolves.toBeUndefined()
    })
  })

  describe('url', () => {
    it('should validate correct URLs', async () => {
      const validator = formRules.url.validator
      await expect(validator(null, 'https://example.com')).resolves.toBeUndefined()
      await expect(validator(null, 'http://example.com/path')).resolves.toBeUndefined()
    })

    it('should reject invalid URLs', async () => {
      const validator = formRules.url.validator
      await expect(validator(null, 'not a url')).rejects.toThrow()
      await expect(validator(null, 'javascript:alert(1)')).rejects.toThrow()
      await expect(validator(null, 'ftp://example.com')).rejects.toThrow()
    })

    it('should allow empty values', async () => {
      const validator = formRules.url.validator
      await expect(validator(null, '')).resolves.toBeUndefined()
    })
  })

  describe('username', () => {
    it('should validate correct usernames', async () => {
      const validator = formRules.username.validator
      await expect(validator(null, 'john_doe')).resolves.toBeUndefined()
      await expect(validator(null, 'user123')).resolves.toBeUndefined()
    })

    it('should reject invalid usernames', async () => {
      const validator = formRules.username.validator
      await expect(validator(null, 'ab')).rejects.toThrow() // too short
      await expect(validator(null, 'user@name')).rejects.toThrow() // invalid char
    })

    it('should allow empty values', async () => {
      const validator = formRules.username.validator
      await expect(validator(null, '')).resolves.toBeUndefined()
    })
  })

  describe('length', () => {
    it('should create length range rule', () => {
      const rule = formRules.length(3, 20)
      expect(rule.min).toBe(3)
      expect(rule.max).toBe(20)
      expect(rule.message).toContain('3')
      expect(rule.message).toContain('20')
    })

    it('should handle only max length', () => {
      const rule = formRules.length(undefined, 100)
      expect(rule.max).toBe(100)
      expect(rule.message).toContain('100')
    })

    it('should handle only min length', () => {
      const rule = formRules.length(5, undefined)
      expect(rule.min).toBe(5)
      expect(rule.message).toContain('5')
    })
  })

  describe('passwordStrength', () => {
    it('should accept strong passwords', async () => {
      const validator = formRules.passwordStrength.validator
      await expect(validator(null, 'Strong@Pass123')).resolves.toBeUndefined()
      await expect(validator(null, 'MyP@ssw0rd!')).resolves.toBeUndefined()
    })

    it('should reject weak passwords', async () => {
      const validator = formRules.passwordStrength.validator
      await expect(validator(null, 'weak')).rejects.toThrow() // too short, no variety
      await expect(validator(null, 'password')).rejects.toThrow() // no uppercase, no numbers, no special
      await expect(validator(null, 'PASSWORD123')).rejects.toThrow() // no lowercase, no special
    })

    it('should allow empty values', async () => {
      const validator = formRules.passwordStrength.validator
      await expect(validator(null, '')).resolves.toBeUndefined()
    })
  })

  describe('passwordMatch', () => {
    it('should validate matching passwords', async () => {
      const mockGetFieldValue = (field: string) => 'MyPassword123!'
      const rule = formRules.passwordMatch(mockGetFieldValue)
      await expect(rule.validator(null, 'MyPassword123!')).resolves.toBeUndefined()
    })

    it('should reject non-matching passwords', async () => {
      const mockGetFieldValue = (field: string) => 'Password1'
      const rule = formRules.passwordMatch(mockGetFieldValue)
      await expect(rule.validator(null, 'Password2')).rejects.toThrow()
    })

    it('should allow empty values', async () => {
      const mockGetFieldValue = (field: string) => 'Password'
      const rule = formRules.passwordMatch(mockGetFieldValue)
      await expect(rule.validator(null, '')).resolves.toBeUndefined()
    })
  })

  describe('captcha', () => {
    it('should validate 4-digit captcha', async () => {
      const validator = formRules.captcha.validator
      await expect(validator(null, '1234')).resolves.toBeUndefined()
      await expect(validator(null, 'ABCD')).resolves.toBeUndefined()
    })

    it('should reject invalid captcha', async () => {
      const validator = formRules.captcha.validator
      await expect(validator(null, '123')).rejects.toThrow() // too short
      await expect(validator(null, '12345')).rejects.toThrow() // too long
      await expect(validator(null, '')).rejects.toThrow() // empty
    })
  })

  describe('VALIDATION_LIMITS', () => {
    it('should have correct limits defined', () => {
      expect(VALIDATION_LIMITS.USERNAME.min).toBe(3)
      expect(VALIDATION_LIMITS.USERNAME.max).toBe(30)
      expect(VALIDATION_LIMITS.COMMENT.max).toBe(500)
      expect(VALIDATION_LIMITS.DANMAKU.max).toBe(100)
      expect(VALIDATION_LIMITS.PASSWORD.min).toBe(8)
    })
  })
})

