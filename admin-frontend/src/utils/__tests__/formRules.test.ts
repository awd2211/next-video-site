/**
 * 表单验证规则测试（管理后台）
 */

import { describe, it, expect } from 'vitest'
import { createFormRules } from '../formRules'
import { VALIDATION_LIMITS, NUMBER_LIMITS } from '../validationConfig'

// Mock translation function
const mockT = (key: string, params?: any) => {
  const translations: Record<string, string> = {
    'validation.required': `${params?.field || 'This field'} is required`,
    'validation.field': 'This field',
    'validation.invalidEmail': 'Please enter a valid email address',
    'validation.invalidUrl': 'Please enter a valid URL',
    'validation.invalidIp': 'Please enter a valid IP address',
    'validation.length': `Length should be between ${params?.min} and ${params?.max} characters`,
    'validation.maxLength': `Cannot exceed ${params?.max} characters`,
    'validation.minLength': `At least ${params?.min} characters required`,
    'validation.numberRange': `Value should be between ${params?.min} and ${params?.max}`,
    'validation.numberMax': `Value cannot exceed ${params?.max}`,
    'validation.numberMin': `Value cannot be less than ${params?.min}`,
  }
  return translations[key] || key
}

describe('Admin Form Rules', () => {
  const formRules = createFormRules(mockT)

  describe('required', () => {
    it('should create required rule', () => {
      const rule = formRules.required()
      expect(rule.required).toBe(true)
      expect(rule.message).toContain('required')
    })
  })

  describe('email', () => {
    it('should validate correct email addresses', async () => {
      const validator = formRules.email.validator
      await expect(validator(null, 'admin@example.com')).resolves.toBeUndefined()
    })

    it('should reject invalid email addresses', async () => {
      const validator = formRules.email.validator
      await expect(validator(null, 'invalid')).rejects.toThrow()
    })
  })

  describe('url', () => {
    it('should validate correct URLs', async () => {
      const validator = formRules.url.validator
      await expect(validator(null, 'https://example.com')).resolves.toBeUndefined()
    })

    it('should reject invalid URLs', async () => {
      const validator = formRules.url.validator
      await expect(validator(null, 'javascript:alert(1)')).rejects.toThrow()
    })
  })

  describe('ipAddress', () => {
    it('should validate correct IP addresses', async () => {
      const validator = formRules.ipAddress.validator
      await expect(validator(null, '192.168.1.1')).resolves.toBeUndefined()
      await expect(validator(null, '10.0.0.1')).resolves.toBeUndefined()
      await expect(validator(null, '127.0.0.1')).resolves.toBeUndefined()
    })

    it('should reject invalid IP addresses', async () => {
      const validator = formRules.ipAddress.validator
      await expect(validator(null, '256.1.1.1')).rejects.toThrow() // out of range
      await expect(validator(null, 'not.an.ip')).rejects.toThrow()
      await expect(validator(null, '192.168.1')).rejects.toThrow() // incomplete
    })

    it('should allow empty values', async () => {
      const validator = formRules.ipAddress.validator
      await expect(validator(null, '')).resolves.toBeUndefined()
    })
  })

  describe('numberRange', () => {
    it('should create number range rule', () => {
      const rule = formRules.numberRange(1, 100)
      expect(rule.type).toBe('number')
      expect(rule.min).toBe(1)
      expect(rule.max).toBe(100)
      expect(rule.message).toContain('1')
      expect(rule.message).toContain('100')
    })

    it('should handle only max value', () => {
      const rule = formRules.numberRange(undefined, 100)
      expect(rule.max).toBe(100)
    })

    it('should handle only min value', () => {
      const rule = formRules.numberRange(10, undefined)
      expect(rule.min).toBe(10)
    })
  })

  describe('VALIDATION_LIMITS', () => {
    it('should have video limits defined', () => {
      expect(VALIDATION_LIMITS.VIDEO_TITLE.min).toBe(2)
      expect(VALIDATION_LIMITS.VIDEO_TITLE.max).toBe(500)
      expect(VALIDATION_LIMITS.VIDEO_DESCRIPTION.max).toBe(2000)
    })

    it('should have person limits defined', () => {
      expect(VALIDATION_LIMITS.PERSON_NAME.min).toBe(1)
      expect(VALIDATION_LIMITS.PERSON_NAME.max).toBe(200)
      expect(VALIDATION_LIMITS.BIOGRAPHY.max).toBe(1000)
    })

    it('should have banner limits defined', () => {
      expect(VALIDATION_LIMITS.BANNER_TITLE.max).toBe(200)
      expect(VALIDATION_LIMITS.BANNER_DESCRIPTION.max).toBe(500)
    })
  })

  describe('NUMBER_LIMITS', () => {
    it('should have year limits defined', () => {
      expect(NUMBER_LIMITS.YEAR.min).toBe(1900)
      expect(NUMBER_LIMITS.YEAR.max).toBe(2100)
    })

    it('should have rating limits defined', () => {
      expect(NUMBER_LIMITS.RATING.min).toBe(0)
      expect(NUMBER_LIMITS.RATING.max).toBe(10)
    })
  })
})

