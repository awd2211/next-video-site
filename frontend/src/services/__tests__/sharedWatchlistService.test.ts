/**
 * 共享观看列表服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import sharedWatchlistService from '../sharedWatchlistService'
import api from '../api'

vi.mock('../api')

describe('Shared Watchlist Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('createSharedList', () => {
    it('should create a shared list with basic data', async () => {
      const createData = {
        title: 'My Awesome Movies',
        description: 'Collection of my favorite movies',
        video_ids: [1, 2, 3],
      }

      const mockResponse = {
        share_token: 'abc123def456',
        share_url: 'https://example.com/shared/abc123def456',
        title: 'My Awesome Movies',
      }

      mockApi.post.mockResolvedValue({ data: mockResponse })

      const result = await sharedWatchlistService.createSharedList(createData)

      expect(mockApi.post).toHaveBeenCalledWith('/shared-watchlist/create', createData)
      expect(result.share_token).toBe('abc123def456')
      expect(result.share_url).toContain('abc123def456')
      expect(result.title).toBe('My Awesome Movies')
    })

    it('should create a shared list with expiration', async () => {
      const createData = {
        title: 'Temporary List',
        video_ids: [1, 2],
        expires_in_days: 7,
      }

      const mockResponse = {
        share_token: 'xyz789abc',
        share_url: 'https://example.com/shared/xyz789abc',
        title: 'Temporary List',
        expires_at: '2024-01-08T00:00:00Z',
      }

      mockApi.post.mockResolvedValue({ data: mockResponse })

      const result = await sharedWatchlistService.createSharedList(createData)

      expect(result.expires_at).toBe('2024-01-08T00:00:00Z')
    })

    it('should handle validation errors', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 422, data: { detail: 'Title is required' } },
      })

      await expect(
        sharedWatchlistService.createSharedList({ title: '', video_ids: [] })
      ).rejects.toMatchObject({
        response: { status: 422 },
      })
    })

    it('should require authentication', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(
        sharedWatchlistService.createSharedList({ title: 'Test', video_ids: [1] })
      ).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('getMySharedLists', () => {
    it('should fetch user\'s shared lists', async () => {
      const mockSharedLists = [
        {
          id: 1,
          user_id: 1,
          share_token: 'token1',
          title: 'Action Movies',
          description: 'Best action movies',
          video_ids: [1, 2, 3],
          is_active: true,
          view_count: 25,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
        {
          id: 2,
          user_id: 1,
          share_token: 'token2',
          title: 'Comedy Collection',
          video_ids: [4, 5],
          is_active: false,
          view_count: 10,
          created_at: '2024-01-02T00:00:00Z',
          updated_at: '2024-01-02T00:00:00Z',
          expires_at: '2024-01-09T00:00:00Z',
        },
      ]

      mockApi.get.mockResolvedValue({ data: mockSharedLists })

      const result = await sharedWatchlistService.getMySharedLists()

      expect(mockApi.get).toHaveBeenCalledWith('/shared-watchlist/my-shares')
      expect(result).toHaveLength(2)
      expect(result[0].title).toBe('Action Movies')
      expect(result[1].is_active).toBe(false)
    })

    it('should handle empty shared lists', async () => {
      mockApi.get.mockResolvedValue({ data: [] })

      const result = await sharedWatchlistService.getMySharedLists()

      expect(result).toHaveLength(0)
    })

    it('should require authentication', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(sharedWatchlistService.getMySharedLists()).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('updateSharedList', () => {
    it('should update shared list title and description', async () => {
      const updateData = {
        title: 'Updated Title',
        description: 'Updated description',
      }

      const mockUpdatedList = {
        id: 1,
        user_id: 1,
        share_token: 'token1',
        title: 'Updated Title',
        description: 'Updated description',
        video_ids: [1, 2, 3],
        is_active: true,
        view_count: 25,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-03T00:00:00Z',
      }

      mockApi.patch.mockResolvedValue({ data: mockUpdatedList })

      const result = await sharedWatchlistService.updateSharedList('token1', updateData)

      expect(mockApi.patch).toHaveBeenCalledWith('/shared-watchlist/token1', updateData)
      expect(result.title).toBe('Updated Title')
      expect(result.description).toBe('Updated description')
    })

    it('should update shared list videos', async () => {
      const updateData = { video_ids: [1, 2, 3, 4, 5] }

      mockApi.patch.mockResolvedValue({
        data: { id: 1, share_token: 'token1', video_ids: [1, 2, 3, 4, 5] },
      })

      const result = await sharedWatchlistService.updateSharedList('token1', updateData)

      expect(result.video_ids).toHaveLength(5)
    })

    it('should deactivate shared list', async () => {
      const updateData = { is_active: false }

      mockApi.patch.mockResolvedValue({
        data: { id: 1, share_token: 'token1', is_active: false },
      })

      const result = await sharedWatchlistService.updateSharedList('token1', updateData)

      expect(result.is_active).toBe(false)
    })

    it('should handle shared list not found', async () => {
      mockApi.patch.mockRejectedValue({
        response: { status: 404, data: { detail: 'Shared list not found' } },
      })

      await expect(
        sharedWatchlistService.updateSharedList('invalid-token', { title: 'Test' })
      ).rejects.toMatchObject({
        response: { status: 404 },
      })
    })

    it('should handle permission denied', async () => {
      mockApi.patch.mockRejectedValue({
        response: { status: 403, data: { detail: 'Permission denied' } },
      })

      await expect(
        sharedWatchlistService.updateSharedList('token1', { title: 'Test' })
      ).rejects.toMatchObject({
        response: { status: 403 },
      })
    })
  })

  describe('deleteSharedList', () => {
    it('should delete shared list', async () => {
      mockApi.delete.mockResolvedValue({ data: null })

      await sharedWatchlistService.deleteSharedList('token1')

      expect(mockApi.delete).toHaveBeenCalledWith('/shared-watchlist/token1')
    })

    it('should handle shared list not found', async () => {
      mockApi.delete.mockRejectedValue({
        response: { status: 404, data: { detail: 'Shared list not found' } },
      })

      await expect(sharedWatchlistService.deleteSharedList('invalid-token')).rejects.toMatchObject({
        response: { status: 404 },
      })
    })

    it('should handle permission denied', async () => {
      mockApi.delete.mockRejectedValue({
        response: { status: 403, data: { detail: 'Permission denied' } },
      })

      await expect(sharedWatchlistService.deleteSharedList('token1')).rejects.toMatchObject({
        response: { status: 403 },
      })
    })
  })

  describe('getSharedList', () => {
    it('should get public shared list', async () => {
      const mockPublicResponse = {
        list_info: {
          share_token: 'public-token',
          title: 'Public Movie List',
          description: 'Great movies to watch',
          video_ids: [1, 2, 3],
          view_count: 50,
          created_at: '2024-01-01T00:00:00Z',
          username: 'moviefan123',
        },
        videos: [
          { id: 1, title: 'Movie 1', poster_url: 'poster1.jpg' },
          { id: 2, title: 'Movie 2', poster_url: 'poster2.jpg' },
          { id: 3, title: 'Movie 3', poster_url: 'poster3.jpg' },
        ],
      }

      mockApi.get.mockResolvedValue({ data: mockPublicResponse })

      const result = await sharedWatchlistService.getSharedList('public-token')

      expect(mockApi.get).toHaveBeenCalledWith('/shared-watchlist/public-token')
      expect(result.list_info.title).toBe('Public Movie List')
      expect(result.videos).toHaveLength(3)
      expect(result.list_info.username).toBe('moviefan123')
    })

    it('should handle expired shared list', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 410, data: { detail: 'Shared list has expired' } },
      })

      await expect(sharedWatchlistService.getSharedList('expired-token')).rejects.toMatchObject({
        response: { status: 410 },
      })
    })

    it('should handle inactive shared list', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 404, data: { detail: 'Shared list not found or inactive' } },
      })

      await expect(sharedWatchlistService.getSharedList('inactive-token')).rejects.toMatchObject({
        response: { status: 404 },
      })
    })

    it('should handle malformed token', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 400, data: { detail: 'Invalid token format' } },
      })

      await expect(sharedWatchlistService.getSharedList('invalid')).rejects.toMatchObject({
        response: { status: 400 },
      })
    })

    it('should increment view count on access', async () => {
      const mockResponse = {
        list_info: {
          share_token: 'token',
          title: 'Test List',
          video_ids: [1],
          view_count: 51, // Incremented from previous views
          created_at: '2024-01-01T00:00:00Z',
          username: 'user',
        },
        videos: [{ id: 1, title: 'Video 1' }],
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await sharedWatchlistService.getSharedList('token')

      expect(result.list_info.view_count).toBe(51)
    })
  })
})
