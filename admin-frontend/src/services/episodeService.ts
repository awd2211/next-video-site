/**
 * Episode (单集) 管理服务
 */
import api from '../utils/axios'

export type EpisodeStatus = 'draft' | 'published' | 'archived'

export interface VideoInEpisode {
  id: number
  title: string
  poster_url?: string
  video_url?: string
  duration?: number
  view_count: number
}

export interface EpisodeListItem {
  id: number
  season_id: number
  video_id: number
  episode_number: number
  title: string
  description?: string
  intro_start?: number
  intro_end?: number
  credits_start?: number
  is_free: boolean
  vip_required: boolean
  status: EpisodeStatus
  published_at?: string
  view_count: number
  like_count: number
  comment_count: number
  created_at: string
  updated_at?: string
}

export interface EpisodeDetail extends EpisodeListItem {
  next_episode_preview_url?: string
  preview_duration?: number
  release_date?: string
  is_featured: boolean
  sort_order: number
  video?: VideoInEpisode
}

export interface PaginatedEpisodeResponse {
  total: number
  page: number
  page_size: number
  pages: number
  items: EpisodeListItem[]
}

export interface EpisodeCreateRequest {
  video_id: number
  episode_number: number
  title: string
  description?: string
  intro_start?: number
  intro_end?: number
  credits_start?: number
  next_episode_preview_url?: string
  preview_duration?: number
  is_free?: boolean
  vip_required?: boolean
  status?: EpisodeStatus
  release_date?: string
  is_featured?: boolean
  sort_order?: number
}

export interface EpisodeUpdateRequest {
  title?: string
  description?: string
  episode_number?: number
  intro_start?: number
  intro_end?: number
  credits_start?: number
  next_episode_preview_url?: string
  preview_duration?: number
  is_free?: boolean
  vip_required?: boolean
  status?: EpisodeStatus
  release_date?: string
  is_featured?: boolean
  sort_order?: number
}

export interface BatchAddEpisodesRequest {
  video_ids: number[]
  start_episode_number?: number
  auto_title?: boolean
  title_prefix?: string
  title_suffix?: string
  is_free?: boolean
  vip_required?: boolean
  status?: EpisodeStatus
}

export interface EpisodeOrderItem {
  episode_id: number
  episode_number: number
}

export interface BatchUpdateOrderRequest {
  episode_orders: EpisodeOrderItem[]
}

export interface BatchSetIntroMarkersRequest {
  episode_ids: number[]
  intro_start?: number
  intro_end?: number
  credits_start?: number
}

export interface BatchOperationRequest {
  episode_ids: number[]
}

export interface BatchDeleteRequest extends BatchOperationRequest {
  confirm: boolean
}

const episodeService = {
  // 获取季度的所有剧集列表
  getListBySeason: async (
    seasonId: number,
    params?: {
      page?: number
      page_size?: number
      status?: EpisodeStatus
      search?: string
      sort_by?: string
      sort_order?: 'asc' | 'desc'
    }
  ) => {
    const response = await api.get<PaginatedEpisodeResponse>(
      `/api/v1/admin/seasons/${seasonId}/episodes`,
      { params }
    )
    return response.data
  },

  // 创建单个剧集
  create: async (seasonId: number, data: EpisodeCreateRequest) => {
    const response = await api.post<EpisodeDetail>(
      `/api/v1/admin/seasons/${seasonId}/episodes`,
      data
    )
    return response.data
  },

  // 获取剧集详情
  getDetail: async (episodeId: number) => {
    const response = await api.get<EpisodeDetail>(`/api/v1/admin/episodes/${episodeId}`)
    return response.data
  },

  // 更新剧集信息
  update: async (episodeId: number, data: EpisodeUpdateRequest) => {
    const response = await api.put<EpisodeDetail>(
      `/api/v1/admin/episodes/${episodeId}`,
      data
    )
    return response.data
  },

  // 删除剧集
  delete: async (episodeId: number) => {
    await api.delete(`/api/v1/admin/episodes/${episodeId}`)
  },

  // 批量添加剧集
  batchAdd: async (seasonId: number, data: BatchAddEpisodesRequest) => {
    const response = await api.post(
      `/api/v1/admin/seasons/${seasonId}/episodes/batch`,
      data
    )
    return response.data
  },

  // 更新剧集顺序（拖拽排序）
  updateOrder: async (seasonId: number, data: BatchUpdateOrderRequest) => {
    const response = await api.put(
      `/api/v1/admin/seasons/${seasonId}/episodes/order`,
      data
    )
    return response.data
  },

  // 批量设置片头片尾标记
  batchSetIntroMarkers: async (data: BatchSetIntroMarkersRequest) => {
    const response = await api.post('/api/v1/admin/episodes/batch/intro-markers', data)
    return response.data
  },

  // 批量发布剧集
  batchPublish: async (episodeIds: number[]) => {
    const response = await api.post('/api/v1/admin/episodes/batch/publish', {
      episode_ids: episodeIds,
    })
    return response.data
  },

  // 批量删除剧集
  batchDelete: async (episodeIds: number[]) => {
    const response = await api.post('/api/v1/admin/episodes/batch/delete', {
      episode_ids: episodeIds,
      confirm: true,
    })
    return response.data
  },
}

export default episodeService
