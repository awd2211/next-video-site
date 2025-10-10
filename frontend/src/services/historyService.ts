import api from './api'

export interface WatchHistory {
  id: number
  user_id: number
  video_id: number
  watch_duration: number
  last_position: number
  is_completed: number
  created_at: string
  updated_at: string | null
  video: any // VideoListResponse
}

export interface PaginatedHistory {
  total: number
  page: number
  page_size: number
  items: WatchHistory[]
}

export const historyService = {
  // 记录观看历史
  recordHistory: async (
    videoId: number,
    watchDuration: number,
    lastPosition: number,
    isCompleted: boolean = false
  ): Promise<WatchHistory> => {
    const response = await api.post('/history/', {
      video_id: videoId,
      watch_duration: watchDuration,
      last_position: lastPosition,
      is_completed: isCompleted
    })
    return response.data
  },

  // 获取观看历史列表
  getHistory: async (page: number = 1, pageSize: number = 20): Promise<PaginatedHistory> => {
    const response = await api.get('/history/', {
      params: { page, page_size: pageSize }
    })
    return response.data
  },

  // 获取特定视频的观看历史
  getVideoHistory: async (videoId: number): Promise<WatchHistory | null> => {
    try {
      const response = await api.get(`/history/${videoId}`)
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null
      }
      throw error
    }
  },

  // 🆕 快速更新观看进度 (轻量级,用于播放器每10秒同步)
  updateProgress: async (
    videoId: number,
    lastPosition: number,
    watchDuration?: number,
    isCompleted?: boolean
  ): Promise<WatchHistory> => {
    const response = await api.patch(`/history/${videoId}/progress`, {
      last_position: lastPosition,
      watch_duration: watchDuration,
      is_completed: isCompleted
    })
    return response.data
  },

  // 删除观看历史
  deleteHistory: async (videoId: number): Promise<void> => {
    await api.delete(`/history/${videoId}`)
  },

  // 清空所有历史
  clearHistory: async (): Promise<void> => {
    await api.delete('/history/')
  }
}
