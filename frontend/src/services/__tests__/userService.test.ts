/**
 * 用户服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { userService } from '../userService'
import api from '../api'

vi.mock('../api')

describe('User Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getCurrentUser', () => {
    it('should fetch current user profile', async () => {
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        full_name: 'Test User',
        avatar: 'https://example.com/avatar.jpg',
        is_active: true,
        is_verified: true,
        is_vip: false,
        created_at: '2024-01-01T00:00:00Z',
      }

      mockApi.get.mockResolvedValue({ data: mockUser })

      const result = await userService.getCurrentUser()

      expect(mockApi.get).toHaveBeenCalledWith('/users/me')
      expect(result).toEqual(mockUser)
      expect(result.email).toBe('test@example.com')
      expect(result.username).toBe('testuser')
    })

    it('should handle unauthorized error', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(userService.getCurrentUser()).rejects.toMatchObject({
        response: { status: 401 },
      })
    })

    it('should handle VIP user data', async () => {
      const mockVipUser = {
        id: 2,
        email: 'vip@example.com',
        username: 'vipuser',
        is_active: true,
        is_verified: true,
        is_vip: true,
        vip_expires_at: '2025-12-31T23:59:59Z',
        created_at: '2024-01-01T00:00:00Z',
      }

      mockApi.get.mockResolvedValue({ data: mockVipUser })

      const result = await userService.getCurrentUser()

      expect(result.is_vip).toBe(true)
      expect(result.vip_expires_at).toBe('2025-12-31T23:59:59Z')
    })
  })

  describe('updateProfile', () => {
    it('should update user profile with full_name', async () => {
      const updateData = { full_name: 'Updated Name' }
      const mockUpdatedUser = {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        full_name: 'Updated Name',
        is_active: true,
        is_verified: true,
        is_vip: false,
        created_at: '2024-01-01T00:00:00Z',
      }

      mockApi.put.mockResolvedValue({ data: mockUpdatedUser })

      const result = await userService.updateProfile(updateData)

      expect(mockApi.put).toHaveBeenCalledWith('/users/me', updateData)
      expect(result.full_name).toBe('Updated Name')
    })

    it('should update user avatar', async () => {
      const updateData = { avatar: 'https://example.com/new-avatar.jpg' }
      const mockUpdatedUser = {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        avatar: 'https://example.com/new-avatar.jpg',
        is_active: true,
        is_verified: true,
        is_vip: false,
        created_at: '2024-01-01T00:00:00Z',
      }

      mockApi.put.mockResolvedValue({ data: mockUpdatedUser })

      const result = await userService.updateProfile(updateData)

      expect(mockApi.put).toHaveBeenCalledWith('/users/me', updateData)
      expect(result.avatar).toBe('https://example.com/new-avatar.jpg')
    })

    it('should update both full_name and avatar', async () => {
      const updateData = {
        full_name: 'New Name',
        avatar: 'https://example.com/avatar2.jpg',
      }

      mockApi.put.mockResolvedValue({
        data: {
          id: 1,
          email: 'test@example.com',
          username: 'testuser',
          full_name: 'New Name',
          avatar: 'https://example.com/avatar2.jpg',
          is_active: true,
          is_verified: true,
          is_vip: false,
          created_at: '2024-01-01T00:00:00Z',
        },
      })

      const result = await userService.updateProfile(updateData)

      expect(result.full_name).toBe('New Name')
      expect(result.avatar).toBe('https://example.com/avatar2.jpg')
    })

    it('should handle validation errors', async () => {
      mockApi.put.mockRejectedValue({
        response: {
          status: 422,
          data: { detail: 'Validation error' },
        },
      })

      await expect(userService.updateProfile({ full_name: '' })).rejects.toMatchObject({
        response: { status: 422 },
      })
    })
  })

  describe('changePassword', () => {
    it('should change password successfully', async () => {
      const passwordData = {
        old_password: 'oldpass123',
        new_password: 'newpass123',
      }
      const mockResponse = { message: 'Password changed successfully' }

      mockApi.post.mockResolvedValue({ data: mockResponse })

      const result = await userService.changePassword(passwordData)

      expect(mockApi.post).toHaveBeenCalledWith('/users/me/change-password', passwordData)
      expect(result.message).toBe('Password changed successfully')
    })

    it('should handle incorrect old password', async () => {
      const passwordData = {
        old_password: 'wrongpass',
        new_password: 'newpass123',
      }

      mockApi.post.mockRejectedValue({
        response: {
          status: 400,
          data: { detail: 'Incorrect password' },
        },
      })

      await expect(userService.changePassword(passwordData)).rejects.toMatchObject({
        response: { status: 400 },
      })
    })

    it('should handle weak new password', async () => {
      const passwordData = {
        old_password: 'oldpass123',
        new_password: '123',
      }

      mockApi.post.mockRejectedValue({
        response: {
          status: 422,
          data: { detail: 'Password too weak' },
        },
      })

      await expect(userService.changePassword(passwordData)).rejects.toMatchObject({
        response: { status: 422 },
      })
    })

    it('should handle unauthorized request', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(
        userService.changePassword({
          old_password: 'old',
          new_password: 'new',
        })
      ).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockApi.get.mockRejectedValue(new Error('Network Error'))

      await expect(userService.getCurrentUser()).rejects.toThrow('Network Error')
    })

    it('should handle server errors', async () => {
      mockApi.get.mockRejectedValue({
        response: {
          status: 500,
          data: { detail: 'Internal Server Error' },
        },
      })

      await expect(userService.getCurrentUser()).rejects.toMatchObject({
        response: { status: 500 },
      })
    })
  })
})

