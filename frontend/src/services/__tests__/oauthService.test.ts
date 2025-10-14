/**
 * OAuth 服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { initiateOAuthLogin, handleOAuthCallback, unlinkOAuthAccount } from '../oauthService'
import api from '../api'

vi.mock('../api')

describe('OAuth Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('initiateOAuthLogin', () => {
    it('should initiate Google OAuth login', async () => {
      const mockResponse = {
        authorization_url: 'https://accounts.google.com/oauth/authorize?client_id=123',
        state: 'random-state-123',
      }

      mockApi.post.mockResolvedValue({ data: mockResponse })

      const result = await initiateOAuthLogin('google')

      expect(mockApi.post).toHaveBeenCalledWith('/oauth/google/login')
      expect(result.authorization_url).toContain('google.com')
      expect(result.state).toBe('random-state-123')
    })

    it('should initiate Facebook OAuth login', async () => {
      const mockResponse = {
        authorization_url: 'https://www.facebook.com/v18.0/dialog/oauth?client_id=456',
        state: 'random-state-456',
      }

      mockApi.post.mockResolvedValue({ data: mockResponse })

      const result = await initiateOAuthLogin('facebook')

      expect(mockApi.post).toHaveBeenCalledWith('/oauth/facebook/login')
      expect(result.authorization_url).toContain('facebook.com')
    })

    it('should handle OAuth provider errors', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 400, data: { detail: 'Invalid provider' } },
      })

      await expect(initiateOAuthLogin('google')).rejects.toMatchObject({
        response: { status: 400 },
      })
    })
  })

  describe('handleOAuthCallback', () => {
    it('should handle successful OAuth callback', async () => {
      const mockResponse = {
        access_token: 'jwt-access-token',
        refresh_token: 'jwt-refresh-token',
        token_type: 'bearer',
        user: {
          id: 1,
          email: 'user@gmail.com',
          username: 'user123',
          full_name: 'John Doe',
          avatar: 'https://example.com/avatar.jpg',
          is_verified: true,
          oauth_provider: 'google',
        },
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await handleOAuthCallback('google', 'auth-code-123', 'state-123')

      expect(mockApi.get).toHaveBeenCalledWith('/oauth/google/callback', {
        params: { code: 'auth-code-123', state: 'state-123' },
      })
      expect(result.access_token).toBe('jwt-access-token')
      expect(result.user.oauth_provider).toBe('google')
    })

    it('should handle OAuth callback errors', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 400, data: { detail: 'Invalid authorization code' } },
      })

      await expect(
        handleOAuthCallback('google', 'invalid-code', 'state-123')
      ).rejects.toMatchObject({
        response: { status: 400 },
      })
    })

    it('should handle state mismatch errors', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 400, data: { detail: 'State mismatch' } },
      })

      await expect(
        handleOAuthCallback('google', 'code-123', 'wrong-state')
      ).rejects.toMatchObject({
        response: { status: 400 },
      })
    })
  })

  describe('unlinkOAuthAccount', () => {
    it('should unlink OAuth account', async () => {
      mockApi.post.mockResolvedValue({
        data: { success: true, message: 'Google account unlinked successfully' },
      })

      const result = await unlinkOAuthAccount('google')

      expect(mockApi.post).toHaveBeenCalledWith('/oauth/google/unlink')
      expect(result.success).toBe(true)
      expect(result.message).toContain('unlinked')
    })

    it('should handle already unlinked account', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 404, data: { detail: 'OAuth account not found' } },
      })

      await expect(unlinkOAuthAccount('google')).rejects.toMatchObject({
        response: { status: 404 },
      })
    })

    it('should require authentication', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(unlinkOAuthAccount('facebook')).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })
})
