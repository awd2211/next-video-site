// @ts-nocheck
/**
 * My List Page
 * Netflix-style watchlist for videos to watch later
 * With drag-and-drop reordering support
 */
import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Helmet } from 'react-helmet-async'
import { Link } from 'react-router-dom'
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd'
import watchlistService, { WatchlistItem } from '@/services/watchlistService'
import sharedWatchlistService from '@/services/sharedWatchlistService'
import EmptyState from '@/components/EmptyState'
import { VideoCardSkeleton } from '@/components/Skeleton'
import { sanitizeInput } from '@/utils/security'
import { VALIDATION_LIMITS } from '@/utils/validationConfig'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'

// Video type labels
const VIDEO_TYPE_LABELS: Record<string, string> = {
  movie: '电影',
  tv_series: '电视剧',
  anime: '动漫',
  documentary: '纪录片',
}

const MyList = () => {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [removingId, setRemovingId] = useState<number | null>(null)
  const [localWatchlist, setLocalWatchlist] = useState<WatchlistItem[]>([])
  const [filteredWatchlist, setFilteredWatchlist] = useState<WatchlistItem[]>([])
  const [isDragging, setIsDragging] = useState(false)

  // Filter states
  const [selectedType, setSelectedType] = useState<string>('all')
  const [selectedYear, setSelectedYear] = useState<string>('all')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  // Sort state
  const [sortBy, setSortBy] = useState<string>('custom') // custom, added, year, rating, views

  // Batch selection state
  const [batchMode, setBatchMode] = useState(false)
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set())

  // Share dialog state
  const [showShareDialog, setShowShareDialog] = useState(false)
  const [shareTitle, setShareTitle] = useState('')
  const [shareDescription, setShareDescription] = useState('')
  const [shareExpireDays, setShareExpireDays] = useState<number | undefined>(undefined)
  const [shareUrl, setShareUrl] = useState('')

  // Fetch watchlist
  const { data: watchlist, isLoading, error } = useQuery({
    queryKey: ['watchlist'],
    queryFn: watchlistService.getMyList,
  })

  // Sync local state with fetched data
  useEffect(() => {
    if (watchlist) {
      setLocalWatchlist(watchlist)
    }
  }, [watchlist])

  // Apply filters and sorting
  useEffect(() => {
    if (!localWatchlist) return

    let filtered = [...localWatchlist]

    // Filter by type
    if (selectedType !== 'all') {
      filtered = filtered.filter(item => item.video.video_type === selectedType)
    }

    // Filter by year
    if (selectedYear !== 'all') {
      const year = parseInt(selectedYear)
      filtered = filtered.filter(item => item.video.release_year === year)
    }

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(item =>
        item.video.categories?.some(cat => cat.slug === selectedCategory)
      )
    }

    // Apply sorting
    const sorted = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'added':
          // Sort by added time (newest first)
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()

        case 'year':
          // Sort by release year (newest first)
          const yearA = a.video.release_year || 0
          const yearB = b.video.release_year || 0
          return yearB - yearA

        case 'rating':
          // Sort by rating (highest first)
          return b.video.average_rating - a.video.average_rating

        case 'views':
          // Sort by view count (highest first)
          return b.video.view_count - a.video.view_count

        case 'custom':
        default:
          // Custom order (by position)
          return a.position - b.position
      }
    })

    setFilteredWatchlist(sorted)
  }, [localWatchlist, selectedType, selectedYear, selectedCategory, sortBy])

  // Extract unique values for filters
  const availableTypes = Array.from(
    new Set(localWatchlist.map(item => item.video.video_type))
  )

  const availableYears = Array.from(
    new Set(
      localWatchlist
        .map(item => item.video.release_year)
        .filter((year): year is number => year !== undefined)
    )
  ).sort((a, b) => b - a) // Sort descending

  const availableCategories = Array.from(
    new Map(
      localWatchlist
        .flatMap(item => item.video.categories || [])
        .map(cat => [cat.slug, cat])
    ).values()
  )

  // Reset filters
  const handleResetFilters = () => {
    setSelectedType('all')
    setSelectedYear('all')
    setSelectedCategory('all')
  }

  const hasActiveFilters = selectedType !== 'all' || selectedYear !== 'all' || selectedCategory !== 'all'

  // Reorder mutation
  const reorderMutation = useMutation({
    mutationFn: (videoIds: number[]) => watchlistService.reorder(videoIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchlist'] })
    },
  })

  // Remove from list mutation
  const removeMutation = useMutation({
    mutationFn: (videoId: number) => watchlistService.removeFromList(videoId),
    onMutate: (videoId) => {
      setRemovingId(videoId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchlist'] })
      setRemovingId(null)
    },
    onError: () => {
      setRemovingId(null)
    },
  })

  // Clear all mutation
  const clearAllMutation = useMutation({
    mutationFn: watchlistService.clearAll,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchlist'] })
    },
  })

  const handleRemove = (videoId: number) => {
    removeMutation.mutate(videoId)
  }

  const handleClearAll = () => {
    if (watchlist && watchlist.length > 0) {
      if (confirm(`确定要清空所有 ${watchlist.length} 个视频吗？`)) {
        clearAllMutation.mutate()
      }
    }
  }

  // Batch operation handlers
  const toggleBatchMode = () => {
    setBatchMode(!batchMode)
    setSelectedIds(new Set()) // Clear selections when toggling
  }

  const toggleSelection = (videoId: number) => {
    const newSelected = new Set(selectedIds)
    if (newSelected.has(videoId)) {
      newSelected.delete(videoId)
    } else {
      newSelected.add(videoId)
    }
    setSelectedIds(newSelected)
  }

  const selectAll = () => {
    const allIds = new Set(filteredWatchlist.map(item => item.video_id))
    setSelectedIds(allIds)
  }

  const deselectAll = () => {
    setSelectedIds(new Set())
  }

  const handleBatchRemove = async () => {
    if (selectedIds.size === 0) return

    if (confirm(`确定要移除选中的 ${selectedIds.size} 个视频吗？`)) {
      try {
        // Remove all selected videos
        await Promise.all(
          Array.from(selectedIds).map(videoId =>
            watchlistService.removeFromList(videoId)
          )
        )
        // Refresh the list
        queryClient.invalidateQueries({ queryKey: ['watchlist'] })
        toast.success(t('myList.batchRemoveSuccess'))
        // Exit batch mode
        setBatchMode(false)
        setSelectedIds(new Set())
      } catch (error) {
        console.error('Batch remove failed:', error)
        toast.error(t('myList.batchRemoveFailed'))
      }
    }
  }

  // Handle drag end
  const handleDragEnd = (result: DropResult) => {
    setIsDragging(false)

    if (!result.destination) {
      return
    }

    if (result.destination.index === result.source.index) {
      return
    }

    // Reorder local state
    const items = Array.from(localWatchlist)
    const [reorderedItem] = items.splice(result.source.index, 1)
    items.splice(result.destination.index, 0, reorderedItem)

    setLocalWatchlist(items)

    // Send reorder request to backend
    const videoIds = items.map(item => item.video_id)
    reorderMutation.mutate(videoIds)
  }

  const handleDragStart = () => {
    setIsDragging(true)
  }

  // Share list mutation
  const shareMutation = useMutation({
    mutationFn: sharedWatchlistService.createSharedList,
    onSuccess: (data) => {
      setShareUrl(data.share_url)
    },
    onError: (error) => {
      console.error('Share failed:', error)
      toast.error(t('myList.shareFailed'))
    },
  })

  const handleShare = () => {
    if (!filteredWatchlist || filteredWatchlist.length === 0) {
      toast.error(t('myList.emptyList'))
      return
    }

    setShareTitle(`${t('myList.myWatchlist')} - ${filteredWatchlist.length}${t('myList.videos')}`)
    setShareDescription('')
    setShareExpireDays(undefined)
    setShareUrl('')
    setShowShareDialog(true)
  }

  const handleConfirmShare = () => {
    const cleanedTitle = sanitizeInput(shareTitle, VALIDATION_LIMITS.TITLE.max)
    const cleanedDescription = sanitizeInput(shareDescription, VALIDATION_LIMITS.DESCRIPTION.max)

    if (!cleanedTitle.trim()) {
      toast.error(t('myList.titleRequired'))
      return
    }

    if (cleanedTitle.length > VALIDATION_LIMITS.TITLE.max) {
      toast.error(t('validation.maxLength', { max: VALIDATION_LIMITS.TITLE.max }))
      return
    }

    const videoIds = filteredWatchlist.map(item => item.video_id)

    shareMutation.mutate({
      title: cleanedTitle,
      description: cleanedDescription || undefined,
      video_ids: videoIds,
      expires_in_days: shareExpireDays,
    })
  }

  const handleCopyShareUrl = () => {
    if (shareUrl) {
      navigator.clipboard.writeText(shareUrl)
      toast.success(t('myList.linkCopied'))
    }
  }

  const _formatDuration = (minutes?: number) => {
    if (!minutes) return 'N/A'
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`
  }

  return (
    <>
      <Helmet>
        <title>我的列表 - VideoSite</title>
        <meta name="description" content="管理您想稍后观看的视频" />
      </Helmet>

      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold mb-2">我的列表</h1>
            <p className="text-gray-400">
              {watchlist ? `${watchlist.length} 个视频` : '加载中...'}
            </p>
          </div>

          {watchlist && watchlist.length > 0 && (
            <div className="flex items-center gap-3">
              <button
                onClick={handleShare}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                </svg>
                分享列表
              </button>

              <button
                onClick={toggleBatchMode}
                className={`px-4 py-2 rounded-lg transition flex items-center gap-2 ${
                  batchMode
                    ? 'bg-blue-600 hover:bg-blue-700'
                    : 'bg-gray-700 hover:bg-gray-600'
                }`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
                {batchMode ? '取消批量' : '批量管理'}
              </button>

              {!batchMode && (
                <button
                  onClick={handleClearAll}
                  disabled={clearAllMutation.isPending}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition disabled:opacity-50"
                >
                  {clearAllMutation.isPending ? '清空中...' : '清空列表'}
                </button>
              )}
            </div>
          )}
        </div>

        {/* Batch Operations Bar */}
        {batchMode && filteredWatchlist.length > 0 && (
          <div className="mb-4 bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="text-sm text-blue-400">
                  已选择 <span className="font-bold text-white">{selectedIds.size}</span> / {filteredWatchlist.length} 个视频
                </span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={selectAll}
                    className="text-sm text-blue-400 hover:text-blue-300 transition"
                  >
                    全选
                  </button>
                  <span className="text-gray-600">|</span>
                  <button
                    onClick={deselectAll}
                    className="text-sm text-blue-400 hover:text-blue-300 transition"
                  >
                    取消全选
                  </button>
                </div>
              </div>

              <button
                onClick={handleBatchRemove}
                disabled={selectedIds.size === 0}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg transition flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                批量移除 ({selectedIds.size})
              </button>
            </div>
          </div>
        )}

        {/* Drag Hint */}
        {localWatchlist && localWatchlist.length > 1 && sortBy === 'custom' && (
          <div className="mb-4 flex items-center gap-2 text-sm text-gray-400 bg-gray-800/50 rounded-lg px-4 py-3">
            <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
            </svg>
            <span>提示：按住并拖动视频卡片可以调整顺序</span>
          </div>
        )}

        {/* Sort Info */}
        {localWatchlist && localWatchlist.length > 1 && sortBy !== 'custom' && (
          <div className="mb-4 flex items-center gap-2 text-sm text-blue-400 bg-blue-900/20 rounded-lg px-4 py-3 border border-blue-500/30">
            <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>当前使用自动排序，拖拽功能已禁用。切换到"自定义顺序"以启用拖拽。</span>
          </div>
        )}

        {/* Filters and Sort */}
        {localWatchlist && localWatchlist.length > 0 && (
          <div className="mb-6 bg-gray-800/50 rounded-lg p-4">
            {/* Sort Selector */}
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-300">筛选和排序</h3>
              <div className="flex items-center gap-2">
                <label className="text-sm text-gray-400">排序:</label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="bg-gray-700 text-white rounded-lg px-3 py-1.5 text-sm border border-gray-600 focus:border-red-500 focus:ring-1 focus:ring-red-500 outline-none transition"
                >
                  <option value="custom">自定义顺序</option>
                  <option value="added">最近添加</option>
                  <option value="year">年份 (新→旧)</option>
                  <option value="rating">评分 (高→低)</option>
                  <option value="views">观看次数 (多→少)</option>
                </select>
              </div>
            </div>

            <div className="flex flex-col md:flex-row gap-4">
              {/* Type Filter */}
              {availableTypes.length > 1 && (
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    <svg className="inline w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
                    </svg>
                    类型
                  </label>
                  <select
                    value={selectedType}
                    onChange={(e) => setSelectedType(e.target.value)}
                    className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 border border-gray-600 focus:border-red-500 focus:ring-1 focus:ring-red-500 outline-none transition"
                  >
                    <option value="all">全部类型</option>
                    {availableTypes.map(type => (
                      <option key={type} value={type}>
                        {VIDEO_TYPE_LABELS[type] || type}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Year Filter */}
              {availableYears.length > 1 && (
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    <svg className="inline w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    年份
                  </label>
                  <select
                    value={selectedYear}
                    onChange={(e) => setSelectedYear(e.target.value)}
                    className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 border border-gray-600 focus:border-red-500 focus:ring-1 focus:ring-red-500 outline-none transition"
                  >
                    <option value="all">全部年份</option>
                    {availableYears.map(year => (
                      <option key={year} value={year}>
                        {year}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Category Filter */}
              {availableCategories.length > 1 && (
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    <svg className="inline w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                    </svg>
                    分类
                  </label>
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 border border-gray-600 focus:border-red-500 focus:ring-1 focus:ring-red-500 outline-none transition"
                  >
                    <option value="all">全部分类</option>
                    {availableCategories.map(category => (
                      <option key={category.slug} value={category.slug}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Reset Button */}
              {hasActiveFilters && (
                <div className="flex items-end">
                  <button
                    onClick={handleResetFilters}
                    className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition flex items-center gap-2 whitespace-nowrap"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    重置
                  </button>
                </div>
              )}
            </div>

            {/* Filter Results */}
            <div className="mt-3 text-sm text-gray-400">
              {hasActiveFilters ? (
                <span>
                  找到 <span className="text-red-500 font-semibold">{filteredWatchlist.length}</span> 个视频
                  （共 {localWatchlist.length} 个）
                </span>
              ) : (
                <span>共 {localWatchlist.length} 个视频</span>
              )}
            </div>
          </div>
        )}

        {/* Loading */}
        {isLoading && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
            {[...Array(10)].map((_, i) => (
              <VideoCardSkeleton key={i} />
            ))}
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="text-center py-12">
            <p className="text-red-500 mb-4">加载失败</p>
            <button
              onClick={() => queryClient.invalidateQueries({ queryKey: ['watchlist'] })}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg"
            >
              重试
            </button>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && watchlist && watchlist.length === 0 && (
          <EmptyState
            title="列表为空"
            message="您还没有添加任何视频到列表中"
            action={
              <Link
                to="/"
                className="inline-block px-6 py-3 bg-red-600 hover:bg-red-700 rounded-lg transition"
              >
                浏览视频
              </Link>
            }
          />
        )}

        {/* Filtered Empty State */}
        {!isLoading && hasActiveFilters && filteredWatchlist.length === 0 && (
          <div className="text-center py-12">
            <svg className="w-16 h-16 mx-auto mb-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <h3 className="text-xl font-semibold mb-2">没有找到匹配的视频</h3>
            <p className="text-gray-400 mb-4">请尝试调整筛选条件</p>
            <button
              onClick={handleResetFilters}
              className="px-6 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition"
            >
              重置筛选
            </button>
          </div>
        )}

        {/* Watchlist Grid with Drag & Drop */}
        {filteredWatchlist && filteredWatchlist.length > 0 && (
          <>
            {sortBy === 'custom' ? (
              <DragDropContext onDragEnd={handleDragEnd} onDragStart={handleDragStart}>
                <Droppable droppableId="watchlist" direction="horizontal">
                  {(provided, snapshot) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      className={`grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6 ${
                        snapshot.isDraggingOver ? 'bg-gray-800/30 rounded-lg p-2' : ''
                      }`}
                    >
                      {filteredWatchlist.map((item, index) => (
                        <Draggable
                          key={item.id}
                          draggableId={String(item.id)}
                          index={index}
                        >
                          {(provided, snapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              style={provided.draggableProps.style}
                            >
                              <WatchlistCard
                                item={item}
                                onRemove={handleRemove}
                                isRemoving={removingId === item.video_id}
                                isDragging={snapshot.isDragging}
                                batchMode={batchMode}
                                isSelected={selectedIds.has(item.video_id)}
                                onToggleSelection={toggleSelection}
                              />
                            </div>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              </DragDropContext>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                {filteredWatchlist.map((item) => (
                  <WatchlistCard
                    key={item.id}
                    item={item}
                    onRemove={handleRemove}
                    isRemoving={removingId === item.video_id}
                    isDragging={false}
                    batchMode={batchMode}
                    isSelected={selectedIds.has(item.video_id)}
                    onToggleSelection={toggleSelection}
                  />
                ))}
              </div>
            )}
          </>
        )}

        {/* Share Dialog */}
        {showShareDialog && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={() => !shareMutation.isPending && setShowShareDialog(false)}>
            <div className="bg-gray-900 rounded-lg p-6 max-w-md w-full" onClick={(e) => e.stopPropagation()}>
              <h2 className="text-2xl font-bold mb-4">分享我的列表</h2>

              {!shareUrl ? (
                <>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        标题 *
                      </label>
                      <input
                        type="text"
                        value={shareTitle}
                        onChange={(e) => setShareTitle(e.target.value)}
                        className="w-full bg-gray-800 text-white rounded-lg px-4 py-2 border border-gray-700 focus:border-green-500 focus:ring-1 focus:ring-green-500 outline-none"
                        placeholder={t('myList.titlePlaceholder')}
                        maxLength={VALIDATION_LIMITS.TITLE.max}
                      />
                      <div className="text-xs text-gray-400 mt-1">
                        {shareTitle.length}/{VALIDATION_LIMITS.TITLE.max}
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        描述（可选）
                      </label>
                      <textarea
                        value={shareDescription}
                        onChange={(e) => setShareDescription(e.target.value)}
                        className="w-full bg-gray-800 text-white rounded-lg px-4 py-2 border border-gray-700 focus:border-green-500 focus:ring-1 focus:ring-green-500 outline-none resize-none"
                        placeholder={t('myList.descriptionPlaceholder')}
                        rows={3}
                        maxLength={VALIDATION_LIMITS.DESCRIPTION.max}
                      />
                      <div className="text-xs text-gray-400 mt-1 text-right">
                        {shareDescription.length}/{VALIDATION_LIMITS.DESCRIPTION.max}
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        有效期（可选）
                      </label>
                      <select
                        value={shareExpireDays || ''}
                        onChange={(e) => setShareExpireDays(e.target.value ? parseInt(e.target.value) : undefined)}
                        className="w-full bg-gray-800 text-white rounded-lg px-4 py-2 border border-gray-700 focus:border-green-500 focus:ring-1 focus:ring-green-500 outline-none"
                      >
                        <option value="">永久有效</option>
                        <option value="1">1天</option>
                        <option value="7">7天</option>
                        <option value="30">30天</option>
                        <option value="90">90天</option>
                      </select>
                    </div>

                    <div className="text-sm text-gray-400">
                      将分享 <span className="text-green-500 font-semibold">{filteredWatchlist.length}</span> 个视频
                    </div>
                  </div>

                  <div className="flex items-center gap-3 mt-6">
                    <button
                      onClick={handleConfirmShare}
                      disabled={shareMutation.isPending || !shareTitle.trim()}
                      className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg transition"
                    >
                      {shareMutation.isPending ? '生成中...' : '生成分享链接'}
                    </button>
                    <button
                      onClick={() => setShowShareDialog(false)}
                      disabled={shareMutation.isPending}
                      className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
                    >
                      取消
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <div className="space-y-4">
                    <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4">
                      <div className="flex items-start gap-3">
                        <svg className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div>
                          <h3 className="font-semibold text-green-400 mb-1">分享链接已生成</h3>
                          <p className="text-sm text-gray-300">你可以将这个链接分享给任何人</p>
                        </div>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        分享链接
                      </label>
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          value={shareUrl}
                          readOnly
                          className="flex-1 bg-gray-800 text-white rounded-lg px-4 py-2 border border-gray-700 text-sm"
                        />
                        <button
                          onClick={handleCopyShareUrl}
                          className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition flex items-center gap-2"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                          复制
                        </button>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => setShowShareDialog(false)}
                    className="w-full mt-6 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
                  >
                    关闭
                  </button>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </>
  )
}

// Watchlist Card Component
interface WatchlistCardProps {
  item: WatchlistItem
  onRemove: (videoId: number) => void
  isRemoving: boolean
  isDragging?: boolean
  batchMode?: boolean
  isSelected?: boolean
  onToggleSelection?: (videoId: number) => void
}

const WatchlistCard: React.FC<WatchlistCardProps> = ({
  item,
  onRemove,
  isRemoving,
  isDragging,
  batchMode = false,
  isSelected = false,
  onToggleSelection
}) => {
  const { video } = item

  return (
    <div
      className={`group relative transition-all duration-200 ${
        isDragging ? 'scale-105 shadow-2xl ring-2 ring-red-500 rotate-2' : ''
      } ${isSelected ? 'ring-2 ring-blue-500' : ''}`}
      onClick={() => batchMode && onToggleSelection && onToggleSelection(video.id)}
    >
      {/* Batch Mode Checkbox */}
      {batchMode && (
        <div className="absolute top-2 left-2 z-20">
          <div
            className={`w-6 h-6 rounded border-2 flex items-center justify-center cursor-pointer transition ${
              isSelected
                ? 'bg-blue-600 border-blue-600'
                : 'bg-black/50 border-white/50 hover:border-white'
            }`}
          >
            {isSelected && (
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            )}
          </div>
        </div>
      )}

      {/* Drag Handle */}
      {!batchMode && (
        <div className="absolute top-2 left-2 w-8 h-8 bg-black/70 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-grab active:cursor-grabbing z-10">
          <svg className="w-5 h-5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8h16M4 16h16" />
          </svg>
        </div>
      )}

      {/* Video Card */}
      <Link
        to={`/video/${video.id}`}
        className="block"
        onClick={(e) => {
          if (isDragging || batchMode) e.preventDefault()
        }}
      >
        <div className="relative aspect-[2/3] rounded-lg overflow-hidden bg-gray-800">
          <img
            src={video.poster_url}
            alt={video.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />

          {/* Hover Overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
            <div className="absolute bottom-0 left-0 right-0 p-4">
              <h3 className="font-semibold mb-1 line-clamp-2">{video.title}</h3>
              <div className="flex items-center gap-2 text-sm text-gray-300">
                {video.release_year && <span>{video.release_year}</span>}
                {video.duration && <span>• {Math.floor(video.duration / 60)}h {video.duration % 60}m</span>}
              </div>
              {video.average_rating > 0 && (
                <div className="flex items-center gap-1 mt-1">
                  <svg className="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                  <span className="text-sm">{video.average_rating.toFixed(1)}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </Link>

      {/* Remove Button */}
      <button
        onClick={(e) => {
          e.preventDefault()
          onRemove(video.id)
        }}
        disabled={isRemoving}
        className="absolute top-2 right-2 w-8 h-8 bg-black/70 hover:bg-red-600 rounded-full flex items-center justify-center transition-colors opacity-0 group-hover:opacity-100 disabled:opacity-50"
        title="从列表移除"
      >
        {isRemoving ? (
          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
        ) : (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        )}
      </button>

      {/* Added Date */}
      <p className="text-xs text-gray-500 mt-2">
        添加于 {new Date(item.created_at).toLocaleDateString('zh-CN')}
      </p>
    </div>
  )
}

export default MyList
