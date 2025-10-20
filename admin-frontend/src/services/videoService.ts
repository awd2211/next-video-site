/**
 * 视频服务（管理后台）
 */
import api from '../utils/axios'

export interface Video {
  id: number
  title: string
  description?: string
  video_url: string
  poster_url?: string
  backdrop_url?: string
  duration?: number
  view_count: number
  rating?: number
  status: string
  created_at: string
  // 🆕 Operation fields
  is_featured?: boolean
  is_trending?: boolean
  is_pinned?: boolean
  quality_score?: number
  scheduled_publish_at?: string | null
}

export interface PaginatedVideoResponse {
  total: number
  page: number
  page_size: number
  items: Video[]
}

// 🆕 Dashboard stats response
export interface DashboardStatsResponse {
  total_videos: number
  standalone_videos: number
  series_videos: number
  today_new: number
  pending_review: number
  scheduled_count: number
  trending_count: number
  pinned_count: number
  featured_count: number
  this_week_views: number
}

// 🆕 Batch operation requests
export interface BatchMarkRequest {
  ids: number[]
  value: boolean
}

export interface BatchQualityScoreRequest {
  ids: number[]
  quality_score: number
}

export interface SchedulePublishRequest {
  scheduled_publish_at: string
}

const videoService = {
  // 获取视频列表（管理员）
  getList: async (params?: {
    page?: number
    page_size?: number
    status?: string
    search?: string
    // 🆕 Operation filters
    is_standalone?: boolean
    is_trending?: boolean
    is_pinned?: boolean
    is_featured?: boolean
    quality_score_min?: number
    scheduled_status?: 'pending' | 'published'
  }): Promise<PaginatedVideoResponse> => {
    const response = await api.get<PaginatedVideoResponse>('/api/v1/admin/videos', { params })
    return response.data
  },

  // 获取视频详情
  getDetail: async (id: number): Promise<Video> => {
    const response = await api.get<Video>(`/api/v1/admin/videos/${id}`)
    return response.data
  },

  // 搜索视频（用于选择器）
  search: async (query: string, params?: {
    page?: number
    page_size?: number
  }): Promise<PaginatedVideoResponse> => {
    const response = await api.get<PaginatedVideoResponse>('/api/v1/admin/videos', {
      params: { search: query, ...params }
    })
    return response.data
  },

  // ==================== 🆕 Operation APIs ====================

  // 获取运营看板统计数据
  getDashboardStats: async (): Promise<DashboardStatsResponse> => {
    const response = await api.get<DashboardStatsResponse>('/api/v1/admin/videos/dashboard-stats')
    return response.data
  },

  // 批量标记/取消热门
  batchMarkTrending: async (data: BatchMarkRequest): Promise<{ success: boolean; affected: number; message: string }> => {
    const response = await api.put('/api/v1/admin/videos/batch/mark-trending', data)
    return response.data
  },

  // 批量置顶/取消置顶
  batchMarkPinned: async (data: BatchMarkRequest): Promise<{ success: boolean; affected: number; message: string }> => {
    const response = await api.put('/api/v1/admin/videos/batch/mark-pinned', data)
    return response.data
  },

  // 批量设置质量评分
  batchSetQualityScore: async (data: BatchQualityScoreRequest): Promise<{ success: boolean; affected: number; quality_score: number; message: string }> => {
    const response = await api.put('/api/v1/admin/videos/batch/set-quality', data)
    return response.data
  },

  // 设置视频定时发布
  schedulePublish: async (videoId: number, data: SchedulePublishRequest): Promise<{ success: boolean; video_id: number; scheduled_publish_at: string; message: string }> => {
    const response = await api.post(`/api/v1/admin/videos/${videoId}/schedule`, data)
    return response.data
  },

  // 取消视频定时发布
  cancelSchedule: async (videoId: number): Promise<{ success: boolean; video_id: number; message: string }> => {
    const response = await api.delete(`/api/v1/admin/videos/${videoId}/schedule`)
    return response.data
  },

  // 快速切换热门状态
  toggleTrending: async (videoId: number): Promise<{ success: boolean; video_id: number; is_trending: boolean }> => {
    const response = await api.put(`/api/v1/admin/videos/${videoId}/toggle-trending`)
    return response.data
  },

  // 快速切换置顶状态
  togglePinned: async (videoId: number): Promise<{ success: boolean; video_id: number; is_pinned: boolean }> => {
    const response = await api.put(`/api/v1/admin/videos/${videoId}/toggle-pinned`)
    return response.data
  },
}

export default videoService
