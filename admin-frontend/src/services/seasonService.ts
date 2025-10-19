/**
 * Season (季度) 管理服务
 */
import api from '../utils/axios'

export type SeasonStatus = 'draft' | 'published' | 'archived'

export interface SeasonListItem {
  id: number
  series_id: number
  season_number: number
  title: string
  description?: string
  status: SeasonStatus
  vip_required: boolean
  poster_url?: string
  total_episodes: number
  total_duration: number
  view_count: number
  favorite_count: number
  average_rating: number
  is_featured: boolean
  sort_order?: number
  created_at: string
  updated_at?: string
}

export interface EpisodeInSeason {
  id: number
  video_id: number
  episode_number: number
  title: string
  description?: string
  is_free: boolean
  vip_required: boolean
  status: string
  view_count: number
  published_at?: string
  intro_start?: number
  intro_end?: number
  credits_start?: number
}

export interface SeasonDetail extends SeasonListItem {
  backdrop_url?: string
  trailer_url?: string
  release_date?: string
  published_at?: string
  episodes: EpisodeInSeason[]
}

export interface PaginatedSeasonResponse {
  total: number
  page: number
  page_size: number
  pages: number
  items: SeasonListItem[]
}

export interface SeasonCreateRequest {
  season_number: number
  title: string
  description?: string
  status?: SeasonStatus
  vip_required?: boolean
  poster_url?: string
  backdrop_url?: string
  trailer_url?: string
  release_date?: string
  is_featured?: boolean
  sort_order?: number
}

export interface SeasonUpdateRequest {
  title?: string
  description?: string
  status?: SeasonStatus
  vip_required?: boolean
  poster_url?: string
  backdrop_url?: string
  trailer_url?: string
  release_date?: string
  is_featured?: boolean
  sort_order?: number
}

export interface BatchOperationRequest {
  season_ids: number[]
}

export interface BatchDeleteRequest extends BatchOperationRequest {
  confirm: boolean
}

export interface SeasonStats {
  season_id: number
  season_number: number
  total_episodes: number
  total_views: number
  total_favorites: number
  average_rating: number
  episode_views: Array<{
    episode_number: number
    view_count: number
  }>
}

const seasonService = {
  // 获取剧集的所有季度列表
  getListBySeries: async (
    seriesId: number,
    params?: {
      page?: number
      page_size?: number
      status?: SeasonStatus
      search?: string
      sort_by?: string
      sort_order?: 'asc' | 'desc'
    }
  ) => {
    const response = await api.get<PaginatedSeasonResponse>(
      `/api/v1/admin/series/${seriesId}/seasons`,
      { params }
    )
    return response.data
  },

  // 创建新季度
  create: async (seriesId: number, data: SeasonCreateRequest) => {
    const response = await api.post<SeasonDetail>(
      `/api/v1/admin/series/${seriesId}/seasons`,
      data
    )
    return response.data
  },

  // 获取季度详情（包含剧集列表）
  getDetail: async (seasonId: number) => {
    const response = await api.get<SeasonDetail>(`/api/v1/admin/seasons/${seasonId}`)
    return response.data
  },

  // 更新季度信息
  update: async (seasonId: number, data: SeasonUpdateRequest) => {
    const response = await api.put<SeasonDetail>(`/api/v1/admin/seasons/${seasonId}`, data)
    return response.data
  },

  // 删除季度
  delete: async (seasonId: number) => {
    await api.delete(`/api/v1/admin/seasons/${seasonId}`)
  },

  // 批量发布季度
  batchPublish: async (seasonIds: number[]) => {
    const response = await api.post('/api/v1/admin/seasons/batch/publish', {
      season_ids: seasonIds,
    })
    return response.data
  },

  // 批量归档季度
  batchArchive: async (seasonIds: number[]) => {
    const response = await api.post('/api/v1/admin/seasons/batch/archive', {
      season_ids: seasonIds,
    })
    return response.data
  },

  // 批量删除季度
  batchDelete: async (seasonIds: number[]) => {
    const response = await api.post('/api/v1/admin/seasons/batch/delete', {
      season_ids: seasonIds,
      confirm: true,
    })
    return response.data
  },

  // 获取季度统计数据
  getStats: async (seasonId: number) => {
    const response = await api.get<SeasonStats>(`/api/v1/admin/seasons/${seasonId}/stats`)
    return response.data
  },
}

export default seasonService
