import api from './api'
import { Video } from '@/types'

export const recommendationService = {
  /**
   * 获取个性化推荐视频
   * @param limit 推荐数量
   * @param excludeIds 排除的视频ID列表
   */
  getPersonalizedRecommendations: async (
    limit: number = 20,
    excludeIds?: number[]
  ): Promise<Video[]> => {
    const params: any = { limit }
    if (excludeIds && excludeIds.length > 0) {
      params.exclude_ids = excludeIds.join(',')
    }
    const response = await api.get('/recommendations/personalized', { params })
    return response.data
  },

  /**
   * 获取相似视频推荐
   * @param videoId 视频ID
   * @param limit 推荐数量
   */
  getSimilarVideos: async (
    videoId: number,
    limit: number = 10
  ): Promise<Video[]> => {
    const response = await api.get(`/recommendations/similar/${videoId}`, {
      params: { limit },
    })
    return response.data
  },

  /**
   * 获取"为你推荐"视频（首页使用）
   * @param limit 推荐数量
   */
  getForYouRecommendations: async (limit: number = 20): Promise<Video[]> => {
    const response = await api.get('/recommendations/for-you', {
      params: { limit },
    })
    return response.data
  },
}
