import api from './api'

export interface Rating {
  id: number
  video_id: number
  user_id: number
  score: number
  created_at: string
  updated_at: string | null
}

export interface RatingStats {
  video_id: number
  average_rating: number
  rating_count: number
  user_rating: number | null
}

export const ratingService = {
  // 给视频评分
  rateVideo: async (videoId: number, score: number): Promise<Rating> => {
    const response = await api.post('/ratings/', {
      video_id: videoId,
      score
    })
    return response.data
  },

  // 获取视频评分统计
  getVideoRatingStats: async (videoId: number): Promise<RatingStats> => {
    const response = await api.get(`/ratings/video/${videoId}/stats`)
    return response.data
  },

  // 获取我的评分
  getMyRating: async (videoId: number): Promise<Rating | null> => {
    const response = await api.get(`/ratings/video/${videoId}/my-rating`)
    return response.data
  },

  // 删除评分
  deleteRating: async (videoId: number): Promise<void> => {
    await api.delete(`/ratings/video/${videoId}`)
  }
}
