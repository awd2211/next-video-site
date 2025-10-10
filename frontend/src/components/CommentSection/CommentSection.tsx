import { useState, useEffect } from 'react'
import { commentService, Comment, CommentCreate } from '../../services/commentService'

interface CommentSectionProps {
  videoId: number
}

const CommentSection = ({ videoId }: CommentSectionProps) => {
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
    if (!newComment.trim()) return

    try {
      const data: CommentCreate = {
        video_id: videoId,
        content: newComment.trim()
      }
      if (replyTo) {
        data.parent_id = replyTo
      }

      await commentService.createComment(data)
      setNewComment('')
      setReplyTo(null)
      loadComments() // Reload comments
    } catch (error: any) {
      if (error.response?.status === 401) {
        alert('Please login to comment')
      } else {
        alert('Failed to post comment')
      }
    }
  }

  const handleDelete = async (commentId: number) => {
    if (!confirm('Are you sure you want to delete this comment?')) return

    try {
      await commentService.deleteComment(commentId)
      loadComments()
    } catch (error) {
      alert('Failed to delete comment')
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
        alert('Please login to like comments')
      } else {
        alert('Failed to like comment')
      }
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }

  return (
    <div className="comment-section mt-8">
      <h3 className="text-2xl font-bold mb-4">Comments ({total})</h3>

      {/* Comment Form */}
      <form onSubmit={handleSubmit} className="mb-6">
        {replyTo && (
          <div className="mb-2 text-sm text-gray-600">
            Replying to comment #{replyTo}
            <button
              type="button"
              onClick={() => setReplyTo(null)}
              className="ml-2 text-red-600"
            >
              Cancel
            </button>
          </div>
        )}
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Write a comment..."
          className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={3}
        />
        <button
          type="submit"
          disabled={!newComment.trim()}
          className="mt-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          Post Comment
        </button>
      </form>

      {/* Comments List */}
      {loading ? (
        <div className="text-center py-4">Loading comments...</div>
      ) : comments.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No comments yet. Be the first to comment!
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

              <div className="mt-3 text-gray-800">{comment.content}</div>

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
                  Reply
                </button>
                {comment.reply_count > 0 && (
                  <span className="text-gray-500">
                    {comment.reply_count} {comment.reply_count === 1 ? 'reply' : 'replies'}
                  </span>
                )}
                <button
                  onClick={() => handleDelete(comment.id)}
                  className="text-red-600 hover:text-red-800"
                >
                  Delete
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
            Previous
          </button>
          <span className="px-4 py-2">
            Page {page} of {Math.ceil(total / pageSize)}
          </span>
          <button
            onClick={() => setPage(p => p + 1)}
            disabled={page >= Math.ceil(total / pageSize)}
            className="px-4 py-2 border rounded hover:bg-gray-100 disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}

export default CommentSection
