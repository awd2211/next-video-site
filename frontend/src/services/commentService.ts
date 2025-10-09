import api from './api'

export interface Comment {
  id: number
  video_id: number
  user_id: number
  parent_id: number | null
  content: string
  status: string
  like_count: number
  is_pinned: boolean
  created_at: string
  updated_at: string | null
  user: {
    id: number
    username: string
    avatar: string | null
  }
  reply_count: number
  replies: Comment[]
}

export interface CommentCreate {
  video_id: number
  parent_id?: number
  content: string
}

export interface PaginatedComments {
  total: number
  page: number
  page_size: number
  items: Comment[]
}

export const commentService = {
  // 获取视频评论
  getVideoComments: async (
    videoId: number,
    page: number = 1,
    pageSize: number = 20,
    parentId?: number
  ): Promise<PaginatedComments> => {
    const params: any = { page, page_size: pageSize }
    if (parentId !== undefined) {
      params.parent_id = parentId
    }
    const response = await api.get(`/comments/video/${videoId}`, { params })
    return response.data
  },

  // 发表评论
  createComment: async (data: CommentCreate): Promise<Comment> => {
    const response = await api.post('/comments/', data)
    return response.data
  },

  // 更新评论
  updateComment: async (commentId: number, content: string): Promise<Comment> => {
    const response = await api.put(`/comments/${commentId}`, { content })
    return response.data
  },

  // 删除评论
  deleteComment: async (commentId: number): Promise<void> => {
    await api.delete(`/comments/${commentId}`)
  },

  // 获取我的评论
  getMyComments: async (page: number = 1, pageSize: number = 20): Promise<PaginatedComments> => {
    const response = await api.get('/comments/user/me', {
      params: { page, page_size: pageSize }
    })
    return response.data
  },

  // 点赞评论
  likeComment: async (commentId: number): Promise<{ like_count: number }> => {
    const response = await api.post(`/comments/${commentId}/like`)
    return response.data
  },

  // 取消点赞
  unlikeComment: async (commentId: number): Promise<{ like_count: number }> => {
    const response = await api.delete(`/comments/${commentId}/like`)
    return response.data
  }
}
