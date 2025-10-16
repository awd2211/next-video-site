/**
 * Two-Factor Authentication Service Tests
 * 双因素认证服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import api from '@/utils/axios'
import * as twoFactorService from '../twoFactorService'

vi.mock('@/utils/axios')

describe('Two-Factor Authentication Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('get2FAStatus', () => {
    it('should fetch 2FA status when enabled', async () => {
      const mockStatus: twoFactorService.TwoFactorStatus = {
        enabled: true,
        verified_at: '2024-01-01T00:00:00Z',
        backup_codes_remaining: 8,
      }

      mockApi.get.mockResolvedValue({ data: mockStatus })

      const result = await twoFactorService.get2FAStatus()

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/2fa/status')
      expect(result.enabled).toBe(true)
      expect(result.backup_codes_remaining).toBe(8)
    })

    it('should fetch 2FA status when disabled', async () => {
      mockApi.get.mockResolvedValue({
        data: { enabled: false, backup_codes_remaining: 0 },
      })

      const result = await twoFactorService.get2FAStatus()

      expect(result.enabled).toBe(false)
    })
  })

  describe('setup2FA', () => {
    it('should initiate 2FA setup', async () => {
      const mockSetup: twoFactorService.TwoFactorSetupResponse = {
        secret: 'JBSWY3DPEHPK3PXP',
        qr_code: 'data:image/png;base64,iVBORw0KGgoAAAANS...',
        backup_codes: ['12345678', '23456789', '34567890'],
      }

      mockApi.post.mockResolvedValue({ data: mockSetup })

      const result = await twoFactorService.setup2FA()

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/admin/2fa/setup', {})
      expect(result.secret).toBe('JBSWY3DPEHPK3PXP')
      expect(result.backup_codes).toHaveLength(3)
    })
  })

  describe('verify2FA', () => {
    it('should verify TOTP token and enable 2FA', async () => {
      const mockVerify: twoFactorService.TwoFactorVerifyResponse = {
        enabled: true,
        backup_codes: ['12345678', '23456789'],
        verified_at: '2024-01-01T00:00:00Z',
      }

      mockApi.post.mockResolvedValue({ data: mockVerify })

      const result = await twoFactorService.verify2FA('123456')

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/admin/2fa/verify', { token: '123456' })
      expect(result.enabled).toBe(true)
      expect(result.backup_codes).toHaveLength(2)
    })

    it('should handle invalid token', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 400, data: { detail: 'Invalid token' } },
      })

      await expect(twoFactorService.verify2FA('000000')).rejects.toMatchObject({
        response: { status: 400 },
      })
    })
  })

  describe('disable2FA', () => {
    it('should disable 2FA with password', async () => {
      mockApi.post.mockResolvedValue({ data: { disabled: true } })

      const result = await twoFactorService.disable2FA('password123')

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/admin/2fa/disable', {
        password: 'password123',
        token: undefined,
      })
      expect(result.disabled).toBe(true)
    })

    it('should disable 2FA with password and token', async () => {
      mockApi.post.mockResolvedValue({ data: { disabled: true } })

      const result = await twoFactorService.disable2FA('password123', '654321')

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/admin/2fa/disable', {
        password: 'password123',
        token: '654321',
      })
      expect(result.disabled).toBe(true)
    })

    it('should handle incorrect password', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 401, data: { detail: 'Incorrect password' } },
      })

      await expect(twoFactorService.disable2FA('wrongpass')).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('regenerateBackupCodes', () => {
    it('should regenerate backup codes', async () => {
      const mockCodes: twoFactorService.RegenerateBackupCodesResponse = {
        backup_codes: ['new1', 'new2', 'new3', 'new4', 'new5', 'new6', 'new7', 'new8'],
      }

      mockApi.post.mockResolvedValue({ data: mockCodes })

      const result = await twoFactorService.regenerateBackupCodes('password123')

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/admin/2fa/regenerate-backup-codes', {
        password: 'password123',
      })
      expect(result.backup_codes).toHaveLength(8)
    })

    it('should handle incorrect password', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 401, data: { detail: 'Incorrect password' } },
      })

      await expect(twoFactorService.regenerateBackupCodes('wrongpass')).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('verify2FALogin', () => {
    it('should verify 2FA during login', async () => {
      const loginData: twoFactorService.TwoFactorLoginRequest = {
        email: 'admin@example.com',
        password: 'password123',
        token: '123456',
        captcha_id: 'captcha-id',
        captcha_code: '1234',
      }

      mockApi.post.mockResolvedValue({
        data: {
          access_token: 'access-token-xxx',
          refresh_token: 'refresh-token-xxx',
          token_type: 'bearer',
        },
      })

      const result = await twoFactorService.verify2FALogin(loginData)

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/admin/2fa/login-verify', loginData)
      expect(result.access_token).toBe('access-token-xxx')
      expect(result.token_type).toBe('bearer')
    })

    it('should handle invalid 2FA token during login', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 400, data: { detail: 'Invalid 2FA token' } },
      })

      await expect(
        twoFactorService.verify2FALogin({
          email: 'test@test.com',
          password: 'pass',
          token: '000000',
          captcha_id: 'id',
          captcha_code: '1234',
        })
      ).rejects.toMatchObject({ response: { status: 400 } })
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockApi.get.mockRejectedValue(new Error('Network error'))

      await expect(twoFactorService.get2FAStatus()).rejects.toThrow('Network error')
    })

    it('should handle 500 server errors', async () => {
      mockApi.post.mockRejectedValue({ response: { status: 500 } })

      await expect(twoFactorService.setup2FA()).rejects.toMatchObject({ response: { status: 500 } })
    })
  })

  describe('Edge Cases', () => {
    it('should handle very long tokens', async () => {
      const longToken = '1'.repeat(100)
      mockApi.post.mockResolvedValue({
        data: { enabled: true, backup_codes: [], verified_at: '' },
      })

      await twoFactorService.verify2FA(longToken)

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/admin/2fa/verify', { token: longToken })
    })

    it('should handle empty backup codes', async () => {
      mockApi.post.mockResolvedValue({
        data: {
          secret: 'SECRET',
          qr_code: 'QR',
          backup_codes: [],
        },
      })

      const result = await twoFactorService.setup2FA()

      expect(result.backup_codes).toHaveLength(0)
    })

    it('should handle special characters in password', async () => {
      const specialPass = 'p@$$w0rd!@#$%^&*()'
      mockApi.post.mockResolvedValue({ data: { disabled: true } })

      await twoFactorService.disable2FA(specialPass)

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/admin/2fa/disable', {
        password: specialPass,
        token: undefined,
      })
    })
  })
})
