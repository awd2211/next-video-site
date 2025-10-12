/**
 * 搜索历史管理工具
 * 使用 localStorage 存储用户的搜索历史记录
 */

const STORAGE_KEY = 'media-manager-search-history'
const MAX_HISTORY_SIZE = 10

export interface SearchHistoryItem {
  text: string
  timestamp: number
}

/**
 * 获取搜索历史
 */
export function getSearchHistory(): SearchHistoryItem[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) return []
    const history = JSON.parse(stored) as SearchHistoryItem[]
    // 按时间倒序排列
    return history.sort((a, b) => b.timestamp - a.timestamp)
  } catch (error) {
    console.error('Failed to load search history:', error)
    return []
  }
}

/**
 * 添加搜索记录
 */
export function addSearchHistory(text: string): void {
  if (!text || !text.trim()) return

  const trimmedText = text.trim()
  const history = getSearchHistory()

  // 检查是否已存在
  const existingIndex = history.findIndex((item) => item.text === trimmedText)
  if (existingIndex !== -1) {
    // 更新时间戳并移到最前面
    const existingItem = history[existingIndex]
    if (existingItem) {
      existingItem.timestamp = Date.now()
    }
  } else {
    // 添加新记录
    history.unshift({
      text: trimmedText,
      timestamp: Date.now(),
    })
  }

  // 限制历史记录数量
  const limitedHistory = history.slice(0, MAX_HISTORY_SIZE)

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(limitedHistory))
  } catch (error) {
    console.error('Failed to save search history:', error)
  }
}

/**
 * 清空搜索历史
 */
export function clearSearchHistory(): void {
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch (error) {
    console.error('Failed to clear search history:', error)
  }
}

/**
 * 删除单条搜索记录
 */
export function removeSearchHistoryItem(text: string): void {
  const history = getSearchHistory()
  const filtered = history.filter((item) => item.text !== text)

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered))
  } catch (error) {
    console.error('Failed to remove search history item:', error)
  }
}

/**
 * 获取搜索建议（基于历史记录匹配）
 */
export function getSearchSuggestions(query: string, limit: number = 5): string[] {
  if (!query || !query.trim()) return []

  const history = getSearchHistory()
  const lowerQuery = query.toLowerCase()

  return history
    .filter((item) => item.text.toLowerCase().includes(lowerQuery))
    .slice(0, limit)
    .map((item) => item.text)
}
