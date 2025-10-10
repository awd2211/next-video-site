import api from './api'
import { Video, PaginatedResponse } from '@/types'
import { VideoSchema, PaginatedResponseSchema } from '@/types/schemas'

// Create paginated video response schema
const PaginatedVideoSchema = PaginatedResponseSchema(VideoSchema)

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
    // Runtime validation with Zod
    return PaginatedVideoSchema.parse(response.data)
  },

  getVideo: async (id: number): Promise<Video> => {
    const response = await api.get(`/videos/${id}`)
    // Runtime validation with Zod
    return VideoSchema.parse(response.data)
  },

  getTrendingVideos: async (params?: {
    page?: number
    page_size?: number
  }): Promise<PaginatedResponse<Video>> => {
    const response = await api.get('/videos/trending', { params })
    return PaginatedVideoSchema.parse(response.data)
  },

  searchVideos: async (
    query: string,
    params?: {
      page?: number
      page_size?: number
      category_id?: number
      country_id?: number
      year?: number
      min_rating?: number
      sort_by?: string
    }
  ): Promise<PaginatedResponse<Video>> => {
    const response = await api.get('/search', {
      params: { q: query, ...params },
    })
    return PaginatedVideoSchema.parse(response.data)
  },

  getRecommendedVideos: async (page: number = 1, pageSize: number = 6): Promise<PaginatedResponse<Video>> => {
    const response = await api.get('/videos/recommended', {
      params: { page, page_size: pageSize },
    })
    return PaginatedVideoSchema.parse(response.data)
  },

  getFeaturedVideos: async (params?: {
    page?: number
    page_size?: number
  }): Promise<PaginatedResponse<Video>> => {
    const response = await api.get('/videos/featured', { params })
    return PaginatedVideoSchema.parse(response.data)
  },
}
