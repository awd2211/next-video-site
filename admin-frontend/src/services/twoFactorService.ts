/**
 * Two-Factor Authentication (2FA) Service
 * Handles all 2FA-related API calls
 */

import api from '../utils/axios'

export interface TwoFactorStatus {
  enabled: boolean
  verified_at?: string
  backup_codes_remaining: number
}

export interface TwoFactorSetupResponse {
  secret: string
  qr_code: string // Base64-encoded QR code image
  backup_codes: string[]
}

export interface TwoFactorVerifyResponse {
  enabled: boolean
  backup_codes: string[]
  verified_at: string
}

export interface RegenerateBackupCodesResponse {
  backup_codes: string[]
}

export interface TwoFactorLoginRequest {
  email: string
  password: string
  token: string
  captcha_id: string
  captcha_code: string
}

/**
 * Get current 2FA status
 */
export const get2FAStatus = async (): Promise<TwoFactorStatus> => {
  const response = await api.get('/api/v1/admin/2fa/status')
  return response.data
}

/**
 * Initiate 2FA setup - generates QR code and backup codes
 */
export const setup2FA = async (): Promise<TwoFactorSetupResponse> => {
  const response = await api.post('/api/v1/admin/2fa/setup', {})
  return response.data
}

/**
 * Verify TOTP token and enable 2FA
 */
export const verify2FA = async (token: string): Promise<TwoFactorVerifyResponse> => {
  const response = await api.post('/api/v1/admin/2fa/verify', { token })
  return response.data
}

/**
 * Disable 2FA
 */
export const disable2FA = async (password: string, token?: string): Promise<{ disabled: boolean }> => {
  const response = await api.post('/api/v1/admin/2fa/disable', { password, token })
  return response.data
}

/**
 * Regenerate backup codes
 */
export const regenerateBackupCodes = async (password: string): Promise<RegenerateBackupCodesResponse> => {
  const response = await api.post('/api/v1/admin/2fa/regenerate-backup-codes', { password })
  return response.data
}

/**
 * Complete 2FA login verification
 */
export const verify2FALogin = async (data: TwoFactorLoginRequest): Promise<{ access_token: string; refresh_token: string; token_type: string }> => {
  const response = await api.post('/api/v1/admin/2fa/login-verify', data)
  return response.data
}
