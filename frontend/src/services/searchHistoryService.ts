import api from './api'

export interface SearchHistoryItem {
  id: number
  query: string
  results_count: number
  created_at: string
}

export interface PopularSearch {
  query: string
  search_count: number
}

export const searchHistoryService = {
  /**
   * 记录搜索历史 (静默 - 不阻塞用户体验)
   * Record search (silent - don't block UX)
   */
  recordSearch: async (query: string, resultsCount: number): Promise<void> => {
    try {
      await api.post('/search/history', {
        query,
        results_count: resultsCount,
      })
    } catch (error) {
      // 静默失败 - 搜索历史不是关键功能
      console.warn('Failed to record search history:', error)
    }
  },

  /**
   * 获取用户的搜索历史 (需要登录)
   * Get user's search history (requires authentication)
   */
  getHistory: async (limit: number = 20): Promise<SearchHistoryItem[]> => {
    try {
      const response = await api.get('/search/history', { params: { limit } })
      return response.data
    } catch (error) {
      console.error('Failed to get search history:', error)
      return []
    }
  },

  /**
   * 删除单个搜索历史项
   * Delete single search history item
   */
  deleteItem: async (id: number): Promise<void> => {
    await api.delete(`/search/history/${id}`)
  },

  /**
   * 清空所有搜索历史
   * Clear all search history
   */
  clearAll: async (): Promise<void> => {
    await api.delete('/search/history')
  },

  /**
   * 获取热门搜索词
   * Get popular searches
   */
  getPopular: async (limit: number = 10, hours: number = 24): Promise<PopularSearch[]> => {
    try {
      const response = await api.get('/search/popular', {
        params: { limit, hours },
      })
      return response.data
    } catch (error) {
      console.error('Failed to get popular searches:', error)
      return []
    }
  },
}
