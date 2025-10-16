/**
 * Profile Service Tests
 * 管理员个人资料服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import api from '@/utils/axios'
import profileService from '../profileService'

vi.mock('@/utils/axios')

describe('Profile Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  const mockProfile = {
    id: 1,
    email: 'admin@example.com',
    username: 'admin',
    full_name: 'Admin User',
    avatar: 'https://example.com/avatar.jpg',
    is_superadmin: true,
    role_id: 1,
    timezone: 'Asia/Shanghai',
    preferred_language: 'zh-CN',
    preferred_theme: 'dark',
    created_at: '2024-01-01T00:00:00Z',
    last_login_at: '2024-01-10T10:00:00Z',
  }

  describe('getProfile', () => {
    it('should fetch current admin profile', async () => {
      mockApi.get.mockResolvedValue({ data: mockProfile })

      const result = await profileService.getProfile()

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/profile/me')
      expect(result.id).toBe(1)
      expect(result.email).toBe('admin@example.com')
      expect(result.is_superadmin).toBe(true)
    })

    it('should handle profile with null fields', async () => {
      mockApi.get.mockResolvedValue({
        data: { ...mockProfile, full_name: null, avatar: null, timezone: null },
      })

      const result = await profileService.getProfile()

      expect(result.full_name).toBeNull()
      expect(result.avatar).toBeNull()
    })

    it('should handle 401 unauthorized', async () => {
      mockApi.get.mockRejectedValue({ response: { status: 401 } })

      await expect(profileService.getProfile()).rejects.toMatchObject({ response: { status: 401 } })
    })
  })

  describe('updateProfile', () => {
    it('should update full name', async () => {
      mockApi.put.mockResolvedValue({
        data: { ...mockProfile, full_name: 'Updated Name' },
      })

      const result = await profileService.updateProfile({ full_name: 'Updated Name' })

      expect(mockApi.put).toHaveBeenCalledWith('/api/v1/admin/profile/me', { full_name: 'Updated Name' })
      expect(result.full_name).toBe('Updated Name')
    })

    it('should update avatar', async () => {
      mockApi.put.mockResolvedValue({
        data: { ...mockProfile, avatar: 'https://example.com/new-avatar.jpg' },
      })

      const result = await profileService.updateProfile({ avatar: 'https://example.com/new-avatar.jpg' })

      expect(result.avatar).toBe('https://example.com/new-avatar.jpg')
    })

    it('should clear optional fields', async () => {
      mockApi.put.mockResolvedValue({
        data: { ...mockProfile, full_name: null, avatar: null },
      })

      const result = await profileService.updateProfile({ full_name: null, avatar: null })

      expect(result.full_name).toBeNull()
      expect(result.avatar).toBeNull()
    })
  })

  describe('changePassword', () => {
    it('should change password successfully', async () => {
      mockApi.put.mockResolvedValue({
        data: { message: 'Password changed successfully' },
      })

      const result = await profileService.changePassword({
        old_password: 'oldpass123',
        new_password: 'newpass456',
      })

      expect(mockApi.put).toHaveBeenCalledWith('/api/v1/admin/profile/me/password', {
        old_password: 'oldpass123',
        new_password: 'newpass456',
      })
      expect(result.message).toBe('Password changed successfully')
    })

    it('should handle incorrect old password', async () => {
      mockApi.put.mockRejectedValue({
        response: { status: 400, data: { detail: 'Incorrect old password' } },
      })

      await expect(
        profileService.changePassword({
          old_password: 'wrong',
          new_password: 'newpass',
        })
      ).rejects.toMatchObject({ response: { status: 400 } })
    })

    it('should handle weak new password', async () => {
      mockApi.put.mockRejectedValue({
        response: { status: 422, data: { detail: 'Password too weak' } },
      })

      await expect(
        profileService.changePassword({
          old_password: 'oldpass',
          new_password: '123',
        })
      ).rejects.toMatchObject({ response: { status: 422 } })
    })
  })

  describe('changeEmail', () => {
    it('should change email successfully', async () => {
      mockApi.put.mockResolvedValue({
        data: { ...mockProfile, email: 'newemail@example.com' },
      })

      const result = await profileService.changeEmail({
        new_email: 'newemail@example.com',
        password: 'password123',
      })

      expect(mockApi.put).toHaveBeenCalledWith('/api/v1/admin/profile/me/email', {
        new_email: 'newemail@example.com',
        password: 'password123',
      })
      expect(result.email).toBe('newemail@example.com')
    })

    it('should handle email already in use', async () => {
      mockApi.put.mockRejectedValue({
        response: { status: 409, data: { detail: 'Email already in use' } },
      })

      await expect(
        profileService.changeEmail({
          new_email: 'existing@example.com',
          password: 'password',
        })
      ).rejects.toMatchObject({ response: { status: 409 } })
    })

    it('should handle invalid email format', async () => {
      mockApi.put.mockRejectedValue({
        response: { status: 422, data: { detail: 'Invalid email format' } },
      })

      await expect(
        profileService.changeEmail({
          new_email: 'invalid-email',
          password: 'password',
        })
      ).rejects.toMatchObject({ response: { status: 422 } })
    })
  })

  describe('updatePreferences', () => {
    it('should update timezone', async () => {
      mockApi.put.mockResolvedValue({
        data: { ...mockProfile, timezone: 'America/New_York' },
      })

      const result = await profileService.updatePreferences({
        timezone: 'America/New_York',
      })

      expect(mockApi.put).toHaveBeenCalledWith('/api/v1/admin/profile/me/preferences', {
        timezone: 'America/New_York',
      })
      expect(result.timezone).toBe('America/New_York')
    })

    it('should update language', async () => {
      mockApi.put.mockResolvedValue({
        data: { ...mockProfile, preferred_language: 'en-US' },
      })

      const result = await profileService.updatePreferences({
        preferred_language: 'en-US',
      })

      expect(result.preferred_language).toBe('en-US')
    })

    it('should update theme', async () => {
      mockApi.put.mockResolvedValue({
        data: { ...mockProfile, preferred_theme: 'light' },
      })

      const result = await profileService.updatePreferences({
        preferred_theme: 'light',
      })

      expect(result.preferred_theme).toBe('light')
    })

    it('should update multiple preferences', async () => {
      mockApi.put.mockResolvedValue({
        data: {
          ...mockProfile,
          timezone: 'UTC',
          preferred_language: 'en-US',
          preferred_theme: 'auto',
        },
      })

      const result = await profileService.updatePreferences({
        timezone: 'UTC',
        preferred_language: 'en-US',
        preferred_theme: 'auto',
      })

      expect(result.timezone).toBe('UTC')
      expect(result.preferred_language).toBe('en-US')
      expect(result.preferred_theme).toBe('auto')
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockApi.get.mockRejectedValue(new Error('Network error'))

      await expect(profileService.getProfile()).rejects.toThrow('Network error')
    })

    it('should handle 500 server errors', async () => {
      mockApi.put.mockRejectedValue({ response: { status: 500 } })

      await expect(profileService.updateProfile({ full_name: 'Test' })).rejects.toMatchObject({
        response: { status: 500 },
      })
    })
  })

  describe('Edge Cases', () => {
    it('should handle very long full names', async () => {
      const longName = 'A'.repeat(500)
      mockApi.put.mockResolvedValue({
        data: { ...mockProfile, full_name: longName },
      })

      const result = await profileService.updateProfile({ full_name: longName })

      expect(result.full_name?.length).toBe(500)
    })

    it('should handle special characters in full name', async () => {
      const specialName = '张三 & John™ © 2024'
      mockApi.put.mockResolvedValue({
        data: { ...mockProfile, full_name: specialName },
      })

      const result = await profileService.updateProfile({ full_name: specialName })

      expect(result.full_name).toBe(specialName)
    })

    it('should handle null preference values', async () => {
      mockApi.put.mockResolvedValue({
        data: { ...mockProfile, timezone: null, preferred_language: null, preferred_theme: null },
      })

      const result = await profileService.updatePreferences({
        timezone: null,
        preferred_language: null,
        preferred_theme: null,
      })

      expect(result.timezone).toBeNull()
    })
  })
})
