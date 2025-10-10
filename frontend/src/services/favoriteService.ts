import api from './api'

export interface Favorite {
  id: number
  user_id: number
  video_id: number
  folder_id?: number
  created_at: string
  video: any // VideoListResponse
}

export interface PaginatedFavorites {
  total: number
  page: number
  page_size: number
  items: Favorite[]
}

export const favoriteService = {
  // 添加收藏
  addFavorite: async (videoId: number, folderId?: number): Promise<Favorite> => {
    const response = await api.post('/favorites/', {
      video_id: videoId,
      folder_id: folderId
    })
    return response.data
  },

  // 取消收藏
  removeFavorite: async (videoId: number): Promise<void> => {
    await api.delete(`/favorites/${videoId}`)
  },

  // 获取收藏列表
  getFavorites: async (page: number = 1, pageSize: number = 20): Promise<PaginatedFavorites> => {
    const response = await api.get('/favorites/', {
      params: { page, page_size: pageSize }
    })
    return response.data
  },

  // 检查是否已收藏
  checkFavorite: async (videoId: number): Promise<boolean> => {
    const response = await api.get(`/favorites/check/${videoId}`)
    return response.data.is_favorited
  }
}
