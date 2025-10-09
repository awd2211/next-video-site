import api from './api'
import { Video, PaginatedResponse } from '@/types'

export const videoService = {
  getVideos: async (params?: {
    page?: number
    page_size?: number
    video_type?: string
    country_id?: number
    category_id?: number
    year?: number
    sort_by?: string
  }): Promise<PaginatedResponse<Video>> => {
    const response = await api.get('/videos', { params })
    return response.data
  },

  getVideo: async (id: number): Promise<Video> => {
    const response = await api.get(`/videos/${id}`)
    return response.data
  },

  getTrendingVideos: async (params?: {
    page?: number
    page_size?: number
  }): Promise<PaginatedResponse<Video>> => {
    const response = await api.get('/videos/trending', { params })
    return response.data
  },

  searchVideos: async (query: string, page?: number): Promise<PaginatedResponse<Video>> => {
    const response = await api.get('/search', {
      params: { q: query, page },
    })
    return response.data
  },
}
