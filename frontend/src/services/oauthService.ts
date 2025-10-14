/**
 * OAuth Service for Google and Facebook authentication
 */

import api from './api'

export interface OAuthLoginResponse {
  authorization_url: string
  state: string
}

export interface OAuthCallbackResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: {
    id: number
    email: string
    username: string
    full_name?: string
    avatar?: string
    is_verified: boolean
    oauth_provider?: string
  }
}

export interface OAuthUnlinkResponse {
  success: boolean
  message: string
}

/**
 * Initiate OAuth login flow
 * @param provider - OAuth provider (google or facebook)
 * @returns Authorization URL and state
 */
export const initiateOAuthLogin = async (
  provider: 'google' | 'facebook'
): Promise<OAuthLoginResponse> => {
  const response = await api.post(`/oauth/${provider}/login`)
  return response.data
}

/**
 * Handle OAuth callback
 * @param provider - OAuth provider
 * @param code - Authorization code from OAuth provider
 * @param state - State parameter for CSRF protection
 * @returns User data and JWT tokens
 */
export const handleOAuthCallback = async (
  provider: string,
  code: string,
  state: string
): Promise<OAuthCallbackResponse> => {
  const response = await api.get(`/oauth/${provider}/callback`, {
    params: { code, state }
  })
  return response.data
}

/**
 * Unlink OAuth account from user
 * @param provider - OAuth provider to unlink
 * @returns Success status and message
 */
export const unlinkOAuthAccount = async (
  provider: string
): Promise<OAuthUnlinkResponse> => {
  const response = await api.post(`/oauth/${provider}/unlink`)
  return response.data
}
