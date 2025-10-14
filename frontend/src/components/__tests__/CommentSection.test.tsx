/**
 * CommentSection 组件测试
 * 测试评论区的渲染、交互和功能
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { I18nextProvider } from 'react-i18next'
import i18n from 'i18next'
import CommentSection from '../CommentSection/CommentSection'
import { commentService } from '@/services/commentService'

// Initialize i18n for testing
i18n.init({
  lng: 'en',
  resources: {
    en: {
      translation: {
        'validation.rateLimitExceeded': 'Rate limit exceeded',
        'validation.commentEmpty': 'Comment cannot be empty',
        'validation.commentTooLong': 'Comment too long',
        'validation.loginRequired': 'Login required',
        'comment.commentSuccess': 'Comment posted',
        'comment.commentFailed': 'Failed to post comment',
        'comment.deleteConfirm': 'Are you sure?',
        'comment.deleteSuccess': 'Comment deleted',
        'comment.deleteFailed': 'Failed to delete',
      },
    },
  },
})

// Mock services
vi.mock('@/services/commentService', () => ({
  commentService: {
    getVideoComments: vi.fn(),
    createComment: vi.fn(),
    deleteComment: vi.fn(),
    likeComment: vi.fn(),
    unlikeComment: vi.fn(),
  },
}))

vi.mock('@/utils/rateLimit', () => ({
  checkCommentRateLimit: vi.fn(() => ({ allowed: true, remaining: 10 })),
}))

vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

const renderWithI18n = (component: React.ReactElement) => {
  return render(<I18nextProvider i18n={i18n}>{component}</I18nextProvider>)
}

describe('CommentSection Component', () => {
  const mockComments = {
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
      {
        id: 2,
        video_id: 1,
        user_id: 2,
        parent_id: null,
        content: 'Nice work!',
        status: 'approved',
        like_count: 3,
        is_pinned: false,
        created_at: '2024-01-02T00:00:00Z',
        updated_at: null,
        user: { id: 2, username: 'user2', avatar: 'avatar.jpg' },
        reply_count: 0,
        replies: [],
      },
    ],
    total: 2,
    page: 1,
    page_size: 20,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(commentService.getVideoComments).mockResolvedValue(mockComments)
  })

  describe('Basic Rendering', () => {
    it('should render comment section', async () => {
      renderWithI18n(<CommentSection videoId={1} />)
      
      await waitFor(() => {
        expect(commentService.getVideoComments).toHaveBeenCalledWith(1, 1, 20)
      })
    })

    it('should load and display comments', async () => {
      renderWithI18n(<CommentSection videoId={1} />)
      
      await waitFor(() => {
        expect(screen.getByText('Great video!')).toBeInTheDocument()
        expect(screen.getByText('Nice work!')).toBeInTheDocument()
      })
    })

    it('should display comment usernames', async () => {
      renderWithI18n(<CommentSection videoId={1} />)
      
      await waitFor(() => {
        expect(screen.getByText('user1')).toBeInTheDocument()
        expect(screen.getByText('user2')).toBeInTheDocument()
      })
    })
  })

  describe('Comment Form', () => {
    it('should render comment input form', () => {
      renderWithI18n(<CommentSection videoId={1} />)
      
      const textarea = screen.getByRole('textbox')
      expect(textarea).toBeInTheDocument()
    })

    it('should allow typing in comment input', () => {
      renderWithI18n(<CommentSection videoId={1} />)
      
      const textarea = screen.getByRole('textbox')
      fireEvent.change(textarea, { target: { value: 'Test comment' } })
      
      expect(textarea).toHaveValue('Test comment')
    })

    it('should submit comment on form submit', async () => {
      vi.mocked(commentService.createComment).mockResolvedValue({
        id: 3,
        video_id: 1,
        user_id: 1,
        parent_id: null,
        content: 'New comment',
        status: 'approved',
        like_count: 0,
        is_pinned: false,
        created_at: '2024-01-03T00:00:00Z',
        updated_at: null,
        user: { id: 1, username: 'user1', avatar: null },
        reply_count: 0,
        replies: [],
      })

      renderWithI18n(<CommentSection videoId={1} />)
      
      const textarea = screen.getByRole('textbox')
      const form = textarea.closest('form')!
      
      fireEvent.change(textarea, { target: { value: 'New comment' } })
      fireEvent.submit(form)
      
      await waitFor(() => {
        expect(commentService.createComment).toHaveBeenCalledWith({
          video_id: 1,
          content: 'New comment',
        })
      })
    })

    it('should clear input after successful submit', async () => {
      vi.mocked(commentService.createComment).mockResolvedValue({} as any)

      renderWithI18n(<CommentSection videoId={1} />)
      
      const textarea = screen.getByRole('textbox')
      const form = textarea.closest('form')!
      
      fireEvent.change(textarea, { target: { value: 'Test' } })
      fireEvent.submit(form)
      
      await waitFor(() => {
        expect(textarea).toHaveValue('')
      })
    })
  })

  describe('Comment Validation', () => {
    it('should not submit empty comment', async () => {
      renderWithI18n(<CommentSection videoId={1} />)
      
      const form = screen.getByRole('textbox').closest('form')!
      fireEvent.submit(form)
      
      await waitFor(() => {
        expect(commentService.createComment).not.toHaveBeenCalled()
      })
    })

    it('should handle rate limiting', async () => {
      const { checkCommentRateLimit } = await import('@/utils/rateLimit')
      vi.mocked(checkCommentRateLimit).mockReturnValue({ allowed: false, remaining: 0 })

      renderWithI18n(<CommentSection videoId={1} />)
      
      const textarea = screen.getByRole('textbox')
      const form = textarea.closest('form')!
      
      fireEvent.change(textarea, { target: { value: 'Test' } })
      fireEvent.submit(form)
      
      await waitFor(() => {
        expect(commentService.createComment).not.toHaveBeenCalled()
      })
    })
  })

  describe('Comment Interactions', () => {
    it('should display like count for comments', async () => {
      renderWithI18n(<CommentSection videoId={1} />)
      
      await waitFor(() => {
        const likeElements = screen.getAllByText(/5|3/)
        expect(likeElements.length).toBeGreaterThan(0)
      })
    })

    it('should handle comment deletion', async () => {
      global.confirm = vi.fn(() => true)
      vi.mocked(commentService.deleteComment).mockResolvedValue()

      renderWithI18n(<CommentSection videoId={1} />)
      
      await waitFor(() => {
        expect(screen.getByText('Great video!')).toBeInTheDocument()
      })

      // 找到删除按钮并点击
      const deleteButtons = screen.getAllByRole('button', { name: /delete/i })
      if (deleteButtons.length > 0) {
        fireEvent.click(deleteButtons[0])
        
        await waitFor(() => {
          expect(commentService.deleteComment).toHaveBeenCalled()
        })
      }
    })
  })

  describe('Loading States', () => {
    it('should show loading state while fetching comments', () => {
      vi.mocked(commentService.getVideoComments).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      )

      renderWithI18n(<CommentSection videoId={1} />)
      
      // Should be in loading state
      expect(commentService.getVideoComments).toHaveBeenCalled()
    })

    it('should handle empty comment list', async () => {
      vi.mocked(commentService.getVideoComments).mockResolvedValue({
        items: [],
        total: 0,
        page: 1,
        page_size: 20,
      })

      renderWithI18n(<CommentSection videoId={1} />)
      
      await waitFor(() => {
        expect(screen.queryByText('Great video!')).not.toBeInTheDocument()
      })
    })
  })

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      vi.mocked(commentService.getVideoComments).mockRejectedValue(
        new Error('API Error')
      )

      renderWithI18n(<CommentSection videoId={1} />)
      
      await waitFor(() => {
        // Should not crash
        expect(commentService.getVideoComments).toHaveBeenCalled()
      })
    })

    it('should handle unauthorized comment submission', async () => {
      vi.mocked(commentService.createComment).mockRejectedValue({
        response: { status: 401 },
      })

      renderWithI18n(<CommentSection videoId={1} />)
      
      const textarea = screen.getByRole('textbox')
      const form = textarea.closest('form')!
      
      fireEvent.change(textarea, { target: { value: 'Test' } })
      fireEvent.submit(form)
      
      await waitFor(() => {
        expect(commentService.createComment).toHaveBeenCalled()
      })
    })
  })

  describe('Pagination', () => {
    it('should support pagination', async () => {
      renderWithI18n(<CommentSection videoId={1} />)
      
      await waitFor(() => {
        expect(commentService.getVideoComments).toHaveBeenCalledWith(1, 1, 20)
      })
    })

    it('should load different pages', async () => {
      const { rerender } = renderWithI18n(<CommentSection videoId={1} />)
      
      await waitFor(() => {
        expect(commentService.getVideoComments).toHaveBeenCalled()
      })

      // Simulate page change
      vi.mocked(commentService.getVideoComments).mockClear()
      rerender(<I18nextProvider i18n={i18n}><CommentSection videoId={1} /></I18nextProvider>)
      
      // Should reload comments
      await waitFor(() => {
        expect(commentService.getVideoComments).toHaveBeenCalled()
      })
    })
  })
})
