/**
 * 视频专辑/系列服务
 */
import api from '../utils/axios'

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

export interface SeriesCreateRequest {
  title: string
  description?: string
  cover_image?: string
  type: SeriesType
  status: SeriesStatus
  display_order?: number
  is_featured?: boolean
}

export interface SeriesUpdateRequest {
  title?: string
  description?: string
  cover_image?: string
  type?: SeriesType
  status?: SeriesStatus
  display_order?: number
  is_featured?: boolean
}

export interface AddVideosRequest {
  video_ids: number[]
  start_episode_number?: number
}

export interface RemoveVideosRequest {
  video_ids: number[]
}

export interface UpdateVideoOrderRequest {
  video_order: Array<{ video_id: number; episode_number: number }>
}

const seriesService = {
  // 获取专辑列表（管理员）
  getList: async (params: {
    page?: number
    page_size?: number
    status?: SeriesStatus
    type?: SeriesType
    search?: string
  }) => {
    const response = await api.get<PaginatedSeriesResponse>('/admin/series', { params })
    return response.data
  },

  // 获取专辑详情
  getDetail: async (id: number) => {
    const response = await api.get<SeriesDetail>(`/admin/series/${id}`)
    return response.data
  },

  // 创建专辑
  create: async (data: SeriesCreateRequest) => {
    const response = await api.post<SeriesDetail>('/admin/series', data)
    return response.data
  },

  // 更新专辑
  update: async (id: number, data: SeriesUpdateRequest) => {
    const response = await api.put<SeriesDetail>(`/admin/series/${id}`, data)
    return response.data
  },

  // 删除专辑
  delete: async (id: number) => {
    await api.delete(`/admin/series/${id}`)
  },

  // 添加视频到专辑
  addVideos: async (id: number, data: AddVideosRequest) => {
    const response = await api.post(`/admin/series/${id}/videos`, data)
    return response.data
  },

  // 从专辑移除视频
  removeVideos: async (id: number, data: RemoveVideosRequest) => {
    const response = await api.delete(`/admin/series/${id}/videos`, { data })
    return response.data
  },

  // 更新视频顺序
  updateVideoOrder: async (id: number, data: UpdateVideoOrderRequest) => {
    const response = await api.put(`/admin/series/${id}/videos/order`, data)
    return response.data
  },
}

export default seriesService
