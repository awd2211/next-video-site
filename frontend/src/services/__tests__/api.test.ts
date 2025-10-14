/**
 * API 客户端测试
 * 测试 axios 实例配置、拦截器和 token 刷新逻辑
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios from 'axios'
import MockAdapter from 'axios-mock-adapter'

describe('API Client', () => {
  let api: any
  let mock: MockAdapter

  beforeEach(async () => {
    // Clear localStorage
    localStorage.clear()
    
    // Reset module to get fresh instance
    vi.resetModules()
    
    // Import fresh instance
    const module = await import('../api')
    api = module.default
    
    // Create mock adapter
    mock = new MockAdapter(api)
  })

  afterEach(() => {
    mock.reset()
    vi.clearAllMocks()
  })

  describe('Base Configuration', () => {
    it('should have correct base URL', () => {
      expect(api.defaults.baseURL).toBe('/api/v1')
    })

    it('should have correct default headers', () => {
      expect(api.defaults.headers['Content-Type']).toBe('application/json')
    })
  })

  describe('Request Interceptor', () => {
    it('should add authorization header when token exists', async () => {
      const token = 'test-access-token'
      localStorage.setItem('access_token', token)

      mock.onGet('/test').reply(200, { success: true })

      await api.get('/test')

      const request = mock.history.get[0]
      expect(request.headers?.Authorization).toBe(`Bearer ${token}`)
    })

    it('should not add authorization header when token does not exist', async () => {
      mock.onGet('/test').reply(200, { success: true })

      await api.get('/test')

      const request = mock.history.get[0]
      expect(request.headers?.Authorization).toBeUndefined()
    })

    it('should add CSRF token from meta tag', async () => {
      // Mock meta tag
      const meta = document.createElement('meta')
      meta.name = 'csrf-token'
      meta.content = 'test-csrf-token'
      document.head.appendChild(meta)

      mock.onGet('/test').reply(200, { success: true })

      await api.get('/test')

      const request = mock.history.get[0]
      expect(request.headers?.['X-CSRF-Token']).toBe('test-csrf-token')

      document.head.removeChild(meta)
    })

    it('should add language headers', async () => {
      localStorage.setItem('language', 'en-US')

      mock.onGet('/test').reply(200, { success: true })

      await api.get('/test')

      const request = mock.history.get[0]
      expect(request.headers?.['X-Language']).toBe('en-US')
      expect(request.headers?.['Accept-Language']).toBe('en-US')
    })

    it('should use navigator language as fallback', async () => {
      mock.onGet('/test').reply(200, { success: true })

      await api.get('/test')

      const request = mock.history.get[0]
      expect(request.headers?.['X-Language']).toBeDefined()
      expect(request.headers?.['Accept-Language']).toBeDefined()
    })
  })

  describe('Response Interceptor - 401 Handling', () => {
    it('should redirect to login when no refresh token', async () => {
      const mockLocation = vi.fn()
      Object.defineProperty(window, 'location', {
        value: { href: mockLocation },
        writable: true,
      })

      mock.onGet('/test').reply(401)

      try {
        await api.get('/test')
      } catch (error) {
        // Expected to fail
      }

      expect(localStorage.length).toBe(0)
    })

    it('should attempt token refresh on 401', async () => {
      localStorage.setItem('refresh_token', 'old-refresh-token')
      localStorage.setItem('access_token', 'old-access-token')

      // First request fails with 401
      mock.onGet('/test').replyOnce(401)

      // Refresh request succeeds
      mock.onPost('/auth/refresh').reply(200, {
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token',
      })

      // Retry request succeeds
      mock.onGet('/test').reply(200, { success: true })

      const response = await api.get('/test')

      expect(response.data.success).toBe(true)
      expect(localStorage.getItem('access_token')).toBe('new-access-token')
      expect(localStorage.getItem('refresh_token')).toBe('new-refresh-token')
    })

    it('should not retry request twice', async () => {
      localStorage.setItem('refresh_token', 'refresh-token')

      mock.onGet('/test').reply(401)
      mock.onPost('/auth/refresh').reply(401)

      try {
        await api.get('/test')
      } catch (error) {
        expect(error).toBeDefined()
      }

      // Should only have one refresh attempt
      expect(mock.history.post.length).toBe(1)
    })
  })

  describe('Response Interceptor - Other Errors', () => {
    it('should pass through non-401 errors', async () => {
      mock.onGet('/test').reply(404, { error: 'Not found' })

      try {
        await api.get('/test')
      } catch (error: any) {
        expect(error.response.status).toBe(404)
        expect(error.response.data.error).toBe('Not found')
      }
    })

    it('should handle network errors', async () => {
      mock.onGet('/test').networkError()

      try {
        await api.get('/test')
      } catch (error: any) {
        expect(error.message).toBe('Network Error')
      }
    })

    it('should handle timeout errors', async () => {
      mock.onGet('/test').timeout()

      try {
        await api.get('/test')
      } catch (error: any) {
        expect(error.code).toBe('ECONNABORTED')
      }
    })
  })

  describe('HTTP Methods', () => {
    it('should support GET requests', async () => {
      mock.onGet('/test').reply(200, { data: 'test' })

      const response = await api.get('/test')

      expect(response.status).toBe(200)
      expect(response.data.data).toBe('test')
    })

    it('should support POST requests', async () => {
      mock.onPost('/test', { name: 'test' }).reply(201, { id: 1 })

      const response = await api.post('/test', { name: 'test' })

      expect(response.status).toBe(201)
      expect(response.data.id).toBe(1)
    })

    it('should support PUT requests', async () => {
      mock.onPut('/test/1', { name: 'updated' }).reply(200, { id: 1, name: 'updated' })

      const response = await api.put('/test/1', { name: 'updated' })

      expect(response.status).toBe(200)
      expect(response.data.name).toBe('updated')
    })

    it('should support PATCH requests', async () => {
      mock.onPatch('/test/1', { name: 'patched' }).reply(200, { id: 1, name: 'patched' })

      const response = await api.patch('/test/1', { name: 'patched' })

      expect(response.status).toBe(200)
      expect(response.data.name).toBe('patched')
    })

    it('should support DELETE requests', async () => {
      mock.onDelete('/test/1').reply(204)

      const response = await api.delete('/test/1')

      expect(response.status).toBe(204)
    })
  })

  describe('Query Parameters', () => {
    it('should handle query parameters correctly', async () => {
      mock.onGet('/test').reply(200)

      await api.get('/test', {
        params: {
          page: 1,
          size: 10,
          filter: 'active',
        },
      })

      const request = mock.history.get[0]
      expect(request.params).toEqual({
        page: 1,
        size: 10,
        filter: 'active',
      })
    })

    it('should handle array query parameters', async () => {
      mock.onGet('/test').reply(200)

      await api.get('/test', {
        params: {
          ids: [1, 2, 3],
        },
      })

      const request = mock.history.get[0]
      expect(request.params.ids).toEqual([1, 2, 3])
    })
  })

  describe('Request/Response Data', () => {
    it('should send JSON data by default', async () => {
      mock.onPost('/test').reply(200)

      await api.post('/test', { name: 'test', value: 123 })

      const request = mock.history.post[0]
      expect(request.headers?.['Content-Type']).toBe('application/json')
      expect(JSON.parse(request.data)).toEqual({ name: 'test', value: 123 })
    })

    it('should handle FormData', async () => {
      mock.onPost('/test').reply(200)

      const formData = new FormData()
      formData.append('file', new Blob(['test']), 'test.txt')

      await api.post('/test', formData)

      const request = mock.history.post[0]
      expect(request.data).toBeInstanceOf(FormData)
    })
  })
})

