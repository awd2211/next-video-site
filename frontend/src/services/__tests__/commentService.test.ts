/**
 * 评论服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { commentService } from '../commentService'
import api from '../api'

vi.mock('../api')

describe('Comment Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getVideoComments', () => {
    it('should fetch video comments with default pagination', async () => {
      const mockResponse = {
        total: 2,
        page: 1,
        page_size: 20,
        items: [
          {
            id: 1,
            video_id: 1,
            user_id: 1,
            parent_id: null,
            content: 'Great video!',
            status: 'approved',
            like_count: 5,
            is_pinned: false,
            created_at: '2024-01-01T00:00:00Z',
            updated_at: null,
            user: { id: 1, username: 'user1', avatar: null },
            reply_count: 0,
            replies: [],
          },
        ],
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await commentService.getVideoComments(1)

      expect(mockApi.get).toHaveBeenCalledWith('/comments/video/1', {
        params: { page: 1, page_size: 20 },
      })
      expect(result.items).toHaveLength(1)
      expect(result.items[0].content).toBe('Great video!')
    })

    it('should fetch comments with custom pagination', async () => {
      mockApi.get.mockResolvedValue({
        data: { total: 0, page: 2, page_size: 10, items: [] },
      })

      await commentService.getVideoComments(1, 2, 10)

      expect(mockApi.get).toHaveBeenCalledWith('/comments/video/1', {
        params: { page: 2, page_size: 10 },
      })
    })

    it('should fetch reply comments with parent_id', async () => {
      mockApi.get.mockResolvedValue({
        data: { total: 0, page: 1, page_size: 20, items: [] },
      })

      await commentService.getVideoComments(1, 1, 20, 5)

      expect(mockApi.get).toHaveBeenCalledWith('/comments/video/1', {
        params: { page: 1, page_size: 20, parent_id: 5 },
      })
    })
  })

  describe('createComment', () => {
    it('should create top-level comment', async () => {
      const commentData = {
        video_id: 1,
        content: 'This is a test comment',
      }

      const mockResponse = {
        id: 1,
        video_id: 1,
        user_id: 1,
        parent_id: null,
        content: 'This is a test comment',
        status: 'approved',
        like_count: 0,
        is_pinned: false,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: null,
        user: { id: 1, username: 'user1', avatar: null },
        reply_count: 0,
        replies: [],
      }

      mockApi.post.mockResolvedValue({ data: mockResponse })

      const result = await commentService.createComment(commentData)

      expect(mockApi.post).toHaveBeenCalledWith('/comments/', commentData)
      expect(result.content).toBe('This is a test comment')
      expect(result.parent_id).toBeNull()
    })

    it('should create reply comment', async () => {
      const replyData = {
        video_id: 1,
        parent_id: 5,
        content: 'This is a reply',
      }

      const mockResponse = {
        id: 2,
        video_id: 1,
        user_id: 1,
        parent_id: 5,
        content: 'This is a reply',
        status: 'approved',
        like_count: 0,
        is_pinned: false,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: null,
        user: { id: 1, username: 'user1', avatar: null },
        reply_count: 0,
        replies: [],
      }

      mockApi.post.mockResolvedValue({ data: mockResponse })

      const result = await commentService.createComment(replyData)

      expect(result.parent_id).toBe(5)
      expect(result.content).toBe('This is a reply')
    })

    it('should handle validation errors', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 422, data: { detail: 'Content too short' } },
      })

      await expect(
        commentService.createComment({ video_id: 1, content: 'x' })
      ).rejects.toMatchObject({
        response: { status: 422 },
      })
    })

    it('should require authentication', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(
        commentService.createComment({ video_id: 1, content: 'Test' })
      ).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('updateComment', () => {
    it('should update comment content', async () => {
      const mockUpdated = {
        id: 1,
        video_id: 1,
        user_id: 1,
        parent_id: null,
        content: 'Updated content',
        status: 'approved',
        like_count: 5,
        is_pinned: false,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
        user: { id: 1, username: 'user1', avatar: null },
        reply_count: 0,
        replies: [],
      }

      mockApi.put.mockResolvedValue({ data: mockUpdated })

      const result = await commentService.updateComment(1, 'Updated content')

      expect(mockApi.put).toHaveBeenCalledWith('/comments/1', {
        content: 'Updated content',
      })
      expect(result.content).toBe('Updated content')
      expect(result.updated_at).not.toBeNull()
    })

    it('should handle permission denied', async () => {
      mockApi.put.mockRejectedValue({
        response: { status: 403, data: { detail: 'Permission denied' } },
      })

      await expect(commentService.updateComment(1, 'New content')).rejects.toMatchObject({
        response: { status: 403 },
      })
    })
  })

  describe('deleteComment', () => {
    it('should delete comment', async () => {
      mockApi.delete.mockResolvedValue({ data: null })

      await commentService.deleteComment(1)

      expect(mockApi.delete).toHaveBeenCalledWith('/comments/1')
    })

    it('should handle comment not found', async () => {
      mockApi.delete.mockRejectedValue({
        response: { status: 404, data: { detail: 'Comment not found' } },
      })

      await expect(commentService.deleteComment(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })

    it('should handle permission denied', async () => {
      mockApi.delete.mockRejectedValue({
        response: { status: 403, data: { detail: 'Permission denied' } },
      })

      await expect(commentService.deleteComment(1)).rejects.toMatchObject({
        response: { status: 403 },
      })
    })
  })

  describe('getMyComments', () => {
    it('should fetch user\'s own comments', async () => {
      const mockResponse = {
        total: 3,
        page: 1,
        page_size: 20,
        items: [
          {
            id: 1,
            video_id: 1,
            user_id: 1,
            parent_id: null,
            content: 'My comment 1',
            status: 'approved',
            like_count: 2,
            is_pinned: false,
            created_at: '2024-01-01T00:00:00Z',
            updated_at: null,
            user: { id: 1, username: 'user1', avatar: null },
            reply_count: 0,
            replies: [],
          },
        ],
      }

      mockApi.get.mockResolvedValue({ data: mockResponse })

      const result = await commentService.getMyComments()

      expect(mockApi.get).toHaveBeenCalledWith('/comments/user/me', {
        params: { page: 1, page_size: 20 },
      })
      expect(result.items).toHaveLength(1)
    })

    it('should fetch with custom pagination', async () => {
      mockApi.get.mockResolvedValue({
        data: { total: 0, page: 2, page_size: 10, items: [] },
      })

      await commentService.getMyComments(2, 10)

      expect(mockApi.get).toHaveBeenCalledWith('/comments/user/me', {
        params: { page: 2, page_size: 10 },
      })
    })
  })

  describe('likeComment', () => {
    it('should like comment', async () => {
      mockApi.post.mockResolvedValue({ data: { like_count: 6 } })

      const result = await commentService.likeComment(1)

      expect(mockApi.post).toHaveBeenCalledWith('/comments/1/like')
      expect(result.like_count).toBe(6)
    })

    it('should handle already liked', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 409, data: { detail: 'Already liked' } },
      })

      await expect(commentService.likeComment(1)).rejects.toMatchObject({
        response: { status: 409 },
      })
    })

    it('should require authentication', async () => {
      mockApi.post.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(commentService.likeComment(1)).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('unlikeComment', () => {
    it('should unlike comment', async () => {
      mockApi.delete.mockResolvedValue({ data: { like_count: 4 } })

      const result = await commentService.unlikeComment(1)

      expect(mockApi.delete).toHaveBeenCalledWith('/comments/1/like')
      expect(result.like_count).toBe(4)
    })

    it('should handle not liked yet', async () => {
      mockApi.delete.mockRejectedValue({
        response: { status: 404, data: { detail: 'Not liked' } },
      })

      await expect(commentService.unlikeComment(1)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })
  })
})

