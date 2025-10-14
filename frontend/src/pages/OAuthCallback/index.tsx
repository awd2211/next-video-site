/**
 * OAuth Callback Page
 * Handles the redirect from OAuth provider after user authorization
 */

import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import { handleOAuthCallback } from '@/services/oauthService'
import { useAuthStore } from '@/store/authStore'

const OAuthCallback = () => {
  const { t } = useTranslation()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const [error, setError] = useState<string>('')
  const [processing, setProcessing] = useState(true)

  useEffect(() => {
    const processCallback = async () => {
      const code = searchParams.get('code')
      const state = searchParams.get('state')
      const errorParam = searchParams.get('error')

      // Extract provider from URL path (e.g., /oauth/google/callback)
      const pathParts = window.location.pathname.split('/')
      const providerIndex = pathParts.indexOf('oauth') + 1
      const provider = pathParts[providerIndex]

      // Check for OAuth errors
      if (errorParam) {
        const errorDescription = searchParams.get('error_description') || 'OAuth authorization was denied'
        setError(errorDescription)
        setProcessing(false)
        toast.error(errorDescription)
        setTimeout(() => navigate('/login'), 3000)
        return
      }

      if (!code || !state) {
        setError(t('auth.invalidOAuthCallback', 'Invalid OAuth callback parameters'))
        setProcessing(false)
        setTimeout(() => navigate('/login'), 3000)
        return
      }

      if (!provider || !['google', 'facebook'].includes(provider)) {
        setError(t('auth.unsupportedProvider', 'Unsupported OAuth provider'))
        setProcessing(false)
        setTimeout(() => navigate('/login'), 3000)
        return
      }

      try {
        // Exchange code for tokens
        const response = await handleOAuthCallback(provider, code, state)

        // Store tokens
        localStorage.setItem('access_token', response.access_token)
        localStorage.setItem('refresh_token', response.refresh_token)

        // Update auth state
        setAuth(response.user, response.access_token)

        // Success message
        const welcomeMsg = t('auth.welcomeBack', { name: response.user.username || response.user.email })
        toast.success(welcomeMsg)

        // Redirect to home
        setTimeout(() => navigate('/'), 500)
      } catch (err: any) {
        console.error('OAuth callback error:', err)
        const errorMsg = err.response?.data?.detail || t('auth.oauthCallbackError', 'OAuth login failed')
        setError(errorMsg)
        setProcessing(false)
        toast.error(errorMsg)

        // Redirect to login after 3 seconds
        setTimeout(() => navigate('/login'), 3000)
      }
    }

    processCallback()
  }, [searchParams, navigate, setAuth, t])

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        {processing ? (
          <>
            {/* Loading State */}
            <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-red-600 mb-6"></div>
            <h2 className="text-2xl font-bold text-white mb-2">
              {t('auth.completing Login', 'Completing login...')}
            </h2>
            <p className="text-gray-400">
              {t('auth.pleaseWait', 'Please wait while we sign you in')}
            </p>
          </>
        ) : error ? (
          <>
            {/* Error State */}
            <div className="bg-red-500 bg-opacity-10 border border-red-500 rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-6">
              <svg
                className="w-8 h-8 text-red-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-red-500 mb-4">
              {t('auth.loginFailed', 'Login Failed')}
            </h2>
            <p className="text-gray-400 mb-4">{error}</p>
            <p className="text-gray-500 text-sm">
              {t('auth.redirectingToLogin', 'Redirecting to login page...')}
            </p>
          </>
        ) : null}
      </div>
    </div>
  )
}

export default OAuthCallback
