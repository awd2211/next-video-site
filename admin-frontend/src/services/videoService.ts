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
}

export interface PaginatedVideoResponse {
  total: number
  page: number
  page_size: number
  items: Video[]
}

const videoService = {
  // 获取视频列表（管理员）
  getList: async (params?: {
    page?: number
    page_size?: number
    status?: string
    search?: string
  }): Promise<PaginatedVideoResponse> => {
    const response = await api.get<PaginatedVideoResponse>('/admin/videos', { params })
    return response.data
  },

  // 获取视频详情
  getDetail: async (id: number): Promise<Video> => {
    const response = await api.get<Video>(`/admin/videos/${id}`)
    return response.data
  },

  // 搜索视频（用于选择器）
  search: async (query: string, params?: {
    page?: number
    page_size?: number
  }): Promise<PaginatedVideoResponse> => {
    const response = await api.get<PaginatedVideoResponse>('/admin/videos', {
      params: { search: query, ...params }
    })
    return response.data
  },
}

export default videoService
