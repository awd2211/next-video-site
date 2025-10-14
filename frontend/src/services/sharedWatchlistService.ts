import api from './api'

export interface SharedWatchlistCreate {
  title: string
  description?: string
  video_ids: number[]
  expires_in_days?: number
}

export interface SharedWatchlistResponse {
  id: number
  user_id: number
  share_token: string
  title: string
  description?: string
  video_ids: number[]
  is_active: boolean
  view_count: number
  created_at: string
  updated_at: string
  expires_at?: string
}

export interface ShareLinkResponse {
  share_token: string
  share_url: string
  title: string
  expires_at?: string
}

export interface SharedWatchlistPublic {
  share_token: string
  title: string
  description?: string
  video_ids: number[]
  view_count: number
  created_at: string
  username: string
}

export interface SharedWatchlistPublicResponse {
  list_info: SharedWatchlistPublic
  videos: any[]
}

const sharedWatchlistService = {
  // Create a new shared list
  async createSharedList(data: SharedWatchlistCreate): Promise<ShareLinkResponse> {
    const response = await api.post('/shared-watchlist/create', data)
    return response.data
  },

  // Get all shared lists created by current user
  async getMySharedLists(): Promise<SharedWatchlistResponse[]> {
    const response = await api.get('/shared-watchlist/my-shares')
    return response.data
  },

  // Update a shared list
  async updateSharedList(shareToken: string, data: Partial<SharedWatchlistCreate> & { is_active?: boolean }): Promise<SharedWatchlistResponse> {
    const response = await api.patch(`/shared-watchlist/${shareToken}`, data)
    return response.data
  },

  // Delete a shared list
  async deleteSharedList(shareToken: string): Promise<void> {
    await api.delete(`/shared-watchlist/${shareToken}`)
  },

  // Get a shared list by token (public)
  async getSharedList(shareToken: string): Promise<SharedWatchlistPublicResponse> {
    const response = await api.get(`/shared-watchlist/${shareToken}`)
    return response.data
  },
}

export default sharedWatchlistService
