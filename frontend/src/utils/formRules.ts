/**
 * 通用表单验证规则
 * 支持国际化和可复用的验证逻辑
 */

import { isValidURL, isValidEmail, isValidUsername } from './security'
import { VALIDATION_LIMITS } from './validationConfig'

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
   * 用户名验证
   */
  username: {
    validator: (_: any, value: string) => {
      if (!value) return Promise.resolve()
      return isValidUsername(value)
        ? Promise.resolve()
        : Promise.reject(new Error(t('validation.invalidUsername')))
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
   * 密码强度验证
   */
  passwordStrength: {
    validator: (_: any, value: string) => {
      if (!value) return Promise.resolve()
      
      const hasLength = value.length >= VALIDATION_LIMITS.PASSWORD.min
      const hasUpperCase = /[A-Z]/.test(value)
      const hasLowerCase = /[a-z]/.test(value)
      const hasNumber = /\d/.test(value)
      const hasSpecial = /[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/;'`~]/.test(value)
      
      if (hasLength && hasUpperCase && hasLowerCase && hasNumber && hasSpecial) {
        return Promise.resolve()
      }
      
      return Promise.reject(new Error(t('validation.passwordWeak')))
    },
  },

  /**
   * 密码确认匹配验证
   */
  passwordMatch: (getFieldValue: (field: string) => any) => ({
    validator: (_: any, value: string) => {
      if (!value || getFieldValue('password') === value) {
        return Promise.resolve()
      }
      return Promise.reject(new Error(t('validation.passwordMismatch')))
    },
  }),

  /**
   * 验证码验证
   */
  captcha: {
    validator: (_: any, value: string) => {
      if (!value || value.length !== 4) {
        return Promise.reject(new Error(t('validation.captchaInvalid')))
      }
      return Promise.resolve()
    },
  },
})

/**
 * 常用验证限制的快捷方式
 */
export const getValidationLimit = (field: keyof typeof VALIDATION_LIMITS) => {
  return VALIDATION_LIMITS[field]
}

