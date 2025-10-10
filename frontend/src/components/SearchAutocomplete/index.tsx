import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Clock, TrendingUp, X } from 'lucide-react'
import { videoService } from '@/services/videoService'
import type { Video } from '@/types'

interface SearchAutocompleteProps {
  onSearch?: (query: string) => void
}

const SearchAutocomplete = ({ onSearch }: SearchAutocompleteProps) => {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const [suggestions, setSuggestions] = useState<Video[]>([])
  const [searchHistory, setSearchHistory] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const wrapperRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // 从 localStorage 加载搜索历史
  useEffect(() => {
    const history = localStorage.getItem('search_history')
    if (history) {
      setSearchHistory(JSON.parse(history))
    }
  }, [])

  // 点击外部关闭下拉框
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // 搜索建议 - 防抖
  useEffect(() => {
    if (query.trim().length < 2) {
      setSuggestions([])
      return
    }

    const timer = setTimeout(async () => {
      setIsLoading(true)
      try {
        const response = await videoService.searchVideos(query, {
          page: 1,
          page_size: 5,
        })
        setSuggestions(response.items)
      } catch (error) {
        console.error('Search suggestions failed:', error)
        setSuggestions([])
      } finally {
        setIsLoading(false)
      }
    }, 300) // 300ms 防抖

    return () => clearTimeout(timer)
  }, [query])

  const handleSearch = (searchQuery: string) => {
    if (!searchQuery.trim()) return

    // 保存到搜索历史
    const newHistory = [
      searchQuery,
      ...searchHistory.filter(item => item !== searchQuery),
    ].slice(0, 10) // 最多保存 10 条

    setSearchHistory(newHistory)
    localStorage.setItem('search_history', JSON.stringify(newHistory))

    // 执行搜索
    setIsOpen(false)
    setQuery(searchQuery)
    navigate(`/search?q=${encodeURIComponent(searchQuery)}`)

    if (onSearch) {
      onSearch(searchQuery)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    handleSearch(query)
  }

  const clearHistory = () => {
    setSearchHistory([])
    localStorage.removeItem('search_history')
  }

  const removeHistoryItem = (item: string) => {
    const newHistory = searchHistory.filter(h => h !== item)
    setSearchHistory(newHistory)
    localStorage.setItem('search_history', JSON.stringify(newHistory))
  }

  return (
    <div ref={wrapperRef} className="relative w-full">
      <form onSubmit={handleSubmit}>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            ref={inputRef}
            type="text"
            placeholder="搜索视频、演员、导演..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setIsOpen(true)}
            className="w-full bg-gray-700 dark:bg-gray-700 light:bg-gray-100 text-white dark:text-white light:text-gray-900 rounded-full px-4 py-2 pl-10 pr-10 focus:outline-none focus:ring-2 focus:ring-red-600 transition-colors"
          />
          {query && (
            <button
              type="button"
              onClick={() => {
                setQuery('')
                inputRef.current?.focus()
              }}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-300"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
      </form>

      {/* 下拉建议框 */}
      {isOpen && (
        <div className="absolute top-full mt-2 w-full bg-gray-800 dark:bg-gray-800 light:bg-white rounded-lg shadow-2xl border border-gray-700 dark:border-gray-700 light:border-gray-200 max-h-96 overflow-y-auto z-50">
          {/* 搜索历史 */}
          {query.trim().length === 0 && searchHistory.length > 0 && (
            <div className="p-2">
              <div className="flex items-center justify-between px-3 py-2">
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <Clock className="w-4 h-4" />
                  <span>搜索历史</span>
                </div>
                <button
                  onClick={clearHistory}
                  className="text-xs text-gray-400 hover:text-red-600 transition-colors"
                >
                  清空
                </button>
              </div>
              {searchHistory.map((item, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between px-3 py-2 hover:bg-gray-700 dark:hover:bg-gray-700 light:hover:bg-gray-50 rounded cursor-pointer group"
                >
                  <div
                    onClick={() => handleSearch(item)}
                    className="flex-1 flex items-center gap-2"
                  >
                    <Clock className="w-4 h-4 text-gray-500" />
                    <span className="text-sm dark:text-gray-300 light:text-gray-700">{item}</span>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      removeHistoryItem(item)
                    }}
                    className="opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="w-4 h-4 text-gray-500 hover:text-red-600" />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* 加载中 */}
          {isLoading && query.trim().length >= 2 && (
            <div className="p-4 text-center text-gray-400">
              <div className="inline-block w-5 h-5 border-2 border-red-600 border-t-transparent rounded-full animate-spin"></div>
              <span className="ml-2">搜索中...</span>
            </div>
          )}

          {/* 搜索建议 */}
          {!isLoading && query.trim().length >= 2 && suggestions.length > 0 && (
            <div className="p-2">
              <div className="flex items-center gap-2 px-3 py-2 text-sm text-gray-400">
                <TrendingUp className="w-4 h-4" />
                <span>相关视频</span>
              </div>
              {suggestions.map((video) => (
                <div
                  key={video.id}
                  onClick={() => navigate(`/video/${video.id}`)}
                  className="flex items-center gap-3 px-3 py-2 hover:bg-gray-700 dark:hover:bg-gray-700 light:hover:bg-gray-50 rounded cursor-pointer"
                >
                  <img
                    src={video.poster_url || '/placeholder.jpg'}
                    alt={video.title}
                    className="w-16 h-10 object-cover rounded"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium dark:text-white light:text-gray-900 truncate">
                      {video.title}
                    </p>
                    <p className="text-xs text-gray-400 truncate">
                      {video.view_count > 10000
                        ? `${(video.view_count / 10000).toFixed(1)}万次观看`
                        : `${video.view_count}次观看`}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* 无结果 */}
          {!isLoading && query.trim().length >= 2 && suggestions.length === 0 && (
            <div className="p-4 text-center text-gray-400">
              <p>未找到相关视频</p>
              <p className="text-xs mt-1">尝试使用其他关键词</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default SearchAutocomplete
