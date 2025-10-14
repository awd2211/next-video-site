import { useState, useEffect } from 'react'
import { commentService, Comment, CommentCreate } from '../../services/commentService'
import { sanitizeHTML, sanitizeInput } from '@/utils/security'
import { checkCommentRateLimit } from '@/utils/rateLimit'
import { VALIDATION_LIMITS } from '@/utils/validationConfig'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'

interface CommentSectionProps {
  videoId: number
}

const MAX_COMMENT_LENGTH = VALIDATION_LIMITS.COMMENT.max

const CommentSection = ({ videoId }: CommentSectionProps) => {
  const { t } = useTranslation()
  const [comments, setComments] = useState<Comment[]>([])
  const [loading, setLoading] = useState(false)
  const [newComment, setNewComment] = useState('')
  const [replyTo, setReplyTo] = useState<number | null>(null)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const pageSize = 20

  const loadComments = async () => {
    try {
      setLoading(true)
      const data = await commentService.getVideoComments(videoId, page, pageSize)
      setComments(data.items)
      setTotal(data.total)
    } catch (error) {
      console.error('Failed to load comments:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadComments()
  }, [videoId, page])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // 检查速率限制
    const rateLimit = checkCommentRateLimit()
    if (!rateLimit.allowed) {
      toast.error(t('validation.rateLimitExceeded'))
      return
    }

    // 清理输入
    const cleanedComment = sanitizeInput(newComment, MAX_COMMENT_LENGTH)

    if (!cleanedComment) {
      toast.error(t('validation.commentEmpty'))
      return
    }

    if (cleanedComment.length > MAX_COMMENT_LENGTH) {
      toast.error(t('validation.commentTooLong', { max: MAX_COMMENT_LENGTH }))
      return
    }

    try {
      const data: CommentCreate = {
        video_id: videoId,
        content: cleanedComment
      }
      if (replyTo) {
        data.parent_id = replyTo
      }

      await commentService.createComment(data)
      setNewComment('')
      setReplyTo(null)
      toast.success(t('comment.commentSuccess'))
      loadComments() // Reload comments
    } catch (error: any) {
      if (error.response?.status === 401) {
        toast.error(t('validation.loginRequired'))
      } else {
        toast.error(t('comment.commentFailed'))
      }
    }
  }

  const handleDelete = async (commentId: number) => {
    if (!confirm(t('comment.deleteConfirm'))) return

    try {
      await commentService.deleteComment(commentId)
      toast.success(t('comment.deleteSuccess'))
      loadComments()
    } catch (error) {
      toast.error(t('comment.deleteFailed'))
    }
  }

  const handleLike = async (commentId: number) => {
    try {
      const result = await commentService.likeComment(commentId)
      // Update the comment's like count in the local state
      setComments(prev =>
        prev.map(comment =>
          comment.id === commentId
            ? { ...comment, like_count: result.like_count }
            : comment
        )
      )
    } catch (error: any) {
      if (error.response?.status === 401) {
        toast.error(t('validation.loginRequired'))
      } else {
        toast.error(t('common.error'))
      }
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }

  return (
    <div className="comment-section mt-8">
      <h3 className="text-2xl font-bold mb-4">{t('comment.title')} ({total})</h3>

      {/* Comment Form */}
      <form onSubmit={handleSubmit} className="mb-6">
        {replyTo && (
          <div className="mb-2 text-sm text-gray-600">
            {t('comment.replyTo', { name: `#${replyTo}` })}
            <button
              type="button"
              onClick={() => setReplyTo(null)}
              className="ml-2 text-red-600"
            >
              {t('common.cancel')}
            </button>
          </div>
        )}
        <div className="relative">
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder={t('comment.addComment')}
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={3}
            maxLength={MAX_COMMENT_LENGTH}
          />
          <div className="absolute bottom-2 right-2 text-xs text-gray-500">
            {newComment.length}/{MAX_COMMENT_LENGTH}
          </div>
        </div>
        <button
          type="submit"
          disabled={!newComment.trim()}
          className="mt-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {t('comment.postComment')}
        </button>
      </form>

      {/* Comments List */}
      {loading ? (
        <div className="text-center py-4">{t('common.loading')}</div>
      ) : comments.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          {t('comment.noComments')}. {t('comment.beFirst')}
        </div>
      ) : (
        <div className="space-y-4">
          {comments.map((comment) => (
            <div key={comment.id} className="border rounded-lg p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-gray-300 flex items-center justify-center">
                    {comment.user.avatar ? (
                      <img
                        src={comment.user.avatar}
                        alt={comment.user.username}
                        className="w-10 h-10 rounded-full"
                      />
                    ) : (
                      <span className="text-gray-600 font-bold">
                        {comment.user.username[0].toUpperCase()}
                      </span>
                    )}
                  </div>
                  <div>
                    <div className="font-semibold">{comment.user.username}</div>
                    <div className="text-sm text-gray-500">
                      {formatDate(comment.created_at)}
                    </div>
                  </div>
                </div>
              </div>

              <div
                className="mt-3 text-gray-800"
                dangerouslySetInnerHTML={{ __html: sanitizeHTML(comment.content) }}
              />

              <div className="mt-3 flex items-center space-x-4 text-sm">
                <button
                  onClick={() => handleLike(comment.id)}
                  className="flex items-center space-x-1 text-gray-600 hover:text-blue-600"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                  </svg>
                  <span>{comment.like_count}</span>
                </button>
                <button
                  onClick={() => setReplyTo(comment.id)}
                  className="text-blue-600 hover:text-blue-800"
                >
                  {t('comment.reply')}
                </button>
                {comment.reply_count > 0 && (
                  <span className="text-gray-500">
                    {t('comment.replies', { count: comment.reply_count })}
                  </span>
                )}
                <button
                  onClick={() => handleDelete(comment.id)}
                  className="text-red-600 hover:text-red-800"
                >
                  {t('comment.deleteComment')}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {total > pageSize && (
        <div className="mt-6 flex justify-center space-x-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 border rounded hover:bg-gray-100 disabled:opacity-50"
          >
            {t('common.previous')}
          </button>
          <span className="px-4 py-2">
            {t('common.page', { current: page, total: Math.ceil(total / pageSize) })}
          </span>
          <button
            onClick={() => setPage(p => p + 1)}
            disabled={page >= Math.ceil(total / pageSize)}
            className="px-4 py-2 border rounded hover:bg-gray-100 disabled:opacity-50"
          >
            {t('common.next')}
          </button>
        </div>
      )}
    </div>
  )
}

export default CommentSection
