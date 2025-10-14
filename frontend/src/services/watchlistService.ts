/**
 * Watchlist (My List) Service
 * Netflix-style "My List" feature
 */
import api from './api'

export interface Category {
  id: number
  name: string
  slug: string
}

export interface Country {
  id: number
  name: string
  code: string
}

export interface WatchlistItem {
  id: number
  user_id: number
  video_id: number
  position: number
  created_at: string
  video: {
    id: number
    title: string
    poster_url: string
    duration: number
    view_count: number
    average_rating: number
    release_year?: number
    video_type: string
    country?: Country
    categories?: Category[]
  }
}

export interface WatchlistStatusResponse {
  in_watchlist: boolean
  watchlist_id: number | null
}

class WatchlistService {
  /**
   * Get user's watchlist
   */
  async getMyList(): Promise<WatchlistItem[]> {
    const response = await api.get<WatchlistItem[]>('/watchlist')
    return response.data
  }

  /**
   * Add video to watchlist
   */
  async addToList(videoId: number): Promise<void> {
    await api.post('/watchlist', { video_id: videoId })
  }

  /**
   * Remove video from watchlist
   */
  async removeFromList(videoId: number): Promise<void> {
    await api.delete(`/watchlist/${videoId}`)
  }

  /**
   * Check if video is in watchlist
   */
  async checkStatus(videoId: number): Promise<WatchlistStatusResponse> {
    const response = await api.get<WatchlistStatusResponse>(`/watchlist/check/${videoId}`)
    return response.data
  }

  /**
   * Reorder watchlist
   */
  async reorder(videoIds: number[]): Promise<void> {
    await api.put('/watchlist/reorder', { video_ids: videoIds })
  }

  /**
   * Clear entire watchlist
   */
  async clearAll(): Promise<void> {
    await api.delete('/watchlist')
  }
}

export default new WatchlistService()
