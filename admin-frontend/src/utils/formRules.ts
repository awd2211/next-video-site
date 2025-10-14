/**
 * 通用表单验证规则（管理后台）
 * 支持国际化和可复用的验证逻辑
 */

import { isValidURL, isValidEmail } from './security'
import { VALIDATION_LIMITS, NUMBER_LIMITS } from './validationConfig'

/**
 * 创建带国际化支持的表单验证规则
 * @param t 国际化翻译函数
 * @returns 验证规则对象
 */
export const createFormRules = (t: (key: string, params?: any) => string) => ({
  /**
   * 必填验证
   */
  required: (fieldName?: string) => ({
    required: true,
    message: t('validation.required', { 
      field: fieldName || t('validation.field') 
    }),
  }),

  /**
   * 邮箱验证
   */
  email: {
    validator: (_: any, value: string) => {
      if (!value) return Promise.resolve()
      return isValidEmail(value) 
        ? Promise.resolve() 
        : Promise.reject(new Error(t('validation.invalidEmail')))
    },
  },

  /**
   * URL验证
   */
  url: {
    validator: (_: any, value: string) => {
      if (!value) return Promise.resolve()
      return isValidURL(value) 
        ? Promise.resolve() 
        : Promise.reject(new Error(t('validation.invalidUrl')))
    },
  },

  /**
   * 长度范围验证
   */
  length: (min?: number, max?: number) => ({
    min,
    max,
    message: min && max
      ? t('validation.length', { min, max })
      : max
      ? t('validation.maxLength', { max })
      : min
      ? t('validation.minLength', { min })
      : '',
  }),

  /**
   * 最小长度验证
   */
  minLength: (min: number) => ({
    min,
    message: t('validation.minLength', { min }),
  }),

  /**
   * 最大长度验证
   */
  maxLength: (max: number) => ({
    max,
    message: t('validation.maxLength', { max }),
  }),

  /**
   * IP地址验证
   */
  ipAddress: {
    validator: (_: any, value: string) => {
      if (!value) return Promise.resolve()
      const ipRegex = /^(?:\d{1,3}\.){3}\d{1,3}$/
      if (!ipRegex.test(value)) {
        return Promise.reject(new Error(t('validation.invalidIp')))
      }
      // 验证每个数字范围
      const parts = value.split('.')
      for (const part of parts) {
        const num = parseInt(part, 10)
        if (num < 0 || num > 255) {
          return Promise.reject(new Error(t('validation.invalidIp')))
        }
      }
      return Promise.resolve()
    },
  },

  /**
   * 数字范围验证
   */
  numberRange: (min?: number, max?: number) => ({
    type: 'number' as const,
    min,
    max,
    message: min !== undefined && max !== undefined
      ? t('validation.numberRange', { min, max })
      : max !== undefined
      ? t('validation.numberMax', { max })
      : min !== undefined
      ? t('validation.numberMin', { min })
      : '',
  }),
})

/**
 * 常用验证限制的快捷方式
 */
export const getValidationLimit = (field: keyof typeof VALIDATION_LIMITS) => {
  return VALIDATION_LIMITS[field]
}

/**
 * 数值范围限制的快捷方式
 */
export const getNumberLimit = (field: keyof typeof NUMBER_LIMITS) => {
  return NUMBER_LIMITS[field]
}

