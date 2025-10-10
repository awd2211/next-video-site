/**
 * 视频专辑/系列服务 - 用户端
 */
import api from './api'

export type SeriesType = 'series' | 'collection' | 'franchise'
export type SeriesStatus = 'draft' | 'published' | 'archived'

export interface SeriesVideoItem {
  video_id: number
  episode_number?: number
  title: string
  poster_url?: string
  duration?: number
  view_count: number
  added_at: string
}

export interface SeriesListItem {
  id: number
  title: string
  description?: string
  cover_image?: string
  type: SeriesType
  status: SeriesStatus
  total_episodes: number
  total_views: number
  total_favorites: number
  is_featured: boolean
  created_at: string
}

export interface SeriesDetail extends SeriesListItem {
  display_order: number
  updated_at?: string
  videos: SeriesVideoItem[]
}

export interface PaginatedSeriesResponse {
  total: number
  page: number
  page_size: number
  items: SeriesListItem[]
}

const seriesService = {
  // 获取专辑列表
  getList: async (params: {
    page?: number
    page_size?: number
    type?: SeriesType
    is_featured?: boolean
  }) => {
    const response = await api.get<PaginatedSeriesResponse>('/series', { params })
    return response.data
  },

  // 获取专辑详情
  getDetail: async (id: number) => {
    const response = await api.get<SeriesDetail>(`/series/${id}`)
    return response.data
  },

  // 获取推荐专辑
  getFeatured: async (limit: number = 10) => {
    const response = await api.get<SeriesListItem[]>('/series/featured/list', {
      params: { limit },
    })
    return response.data
  },
}

export default seriesService
