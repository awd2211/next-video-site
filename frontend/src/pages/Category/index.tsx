import { useState, useEffect } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { videoService } from '@/services/videoService'
import { dataService } from '@/services/dataService'
import VideoCard from '@/components/VideoCard'

const Category = () => {
  const { slug } = useParams<{ slug: string }>()
  const [searchParams, setSearchParams] = useSearchParams()
  
  const page = parseInt(searchParams.get('page') || '1')
  const sortBy = searchParams.get('sort_by') || 'created_at'
  
  // 获取所有分类
  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: dataService.getCategories,
  })
  
  // 找到当前分类
  const currentCategory = categories?.find((c) => c.slug === slug)
  
  // 获取该分类的视频
  const { data, isLoading, error } = useQuery({
    queryKey: ['videos', 'category', currentCategory?.id, page, sortBy],
    queryFn: () => videoService.getVideos({
      category_id: currentCategory?.id,
      page,
      page_size: 24,
      sort_by: sortBy,
    }),
    enabled: !!currentCategory?.id,
  })
  
  const handlePageChange = (newPage: number) => {
    setSearchParams({ page: String(newPage), sort_by: sortBy })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
  
  const handleSortChange = (newSort: string) => {
    setSearchParams({ page: '1', sort_by: newSort })
  }
  
  if (!categories) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12">加载中...</div>
      </div>
    )
  }
  
  if (!currentCategory) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12 text-gray-400">
          <p className="text-xl mb-2">分类不存在</p>
          <p className="text-sm">Slug: {slug}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">{currentCategory.name}</h1>
        {currentCategory.description && (
          <p className="text-gray-400">{currentCategory.description}</p>
        )}
      </div>

      {/* Sort and Filter */}
      <div className="mb-6 flex items-center justify-between">
        <div className="text-gray-400">
          {data && `共 ${data.total} 个视频`}
        </div>
        
        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-400">排序：</label>
          <select
            value={sortBy}
            onChange={(e) => handleSortChange(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="created_at">最新发布</option>
            <option value="view_count">最多播放</option>
            <option value="average_rating">最高评分</option>
            <option value="favorite_count">最多收藏</option>
          </select>
        </div>
      </div>

      {/* Video Grid */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="inline-block w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-gray-400">加载中...</p>
        </div>
      ) : error ? (
        <div className="text-center py-12 text-red-500">
          <p>加载失败</p>
          <p className="text-sm mt-2">{(error as Error).message}</p>
        </div>
      ) : data && data.items.length > 0 ? (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 md:gap-6">
            {data.items.map((video) => (
              <VideoCard key={video.id} video={video} />
            ))}
          </div>

          {/* Pagination */}
          {data.pages > 1 && (
            <div className="mt-12 flex items-center justify-center gap-2">
              <button
                onClick={() => handlePageChange(page - 1)}
                disabled={page === 1}
                className="px-4 py-2 bg-gray-800 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700 transition"
              >
                上一页
              </button>
              
              <div className="flex items-center gap-1">
                {Array.from({ length: Math.min(data.pages, 7) }, (_, i) => {
                  let pageNum
                  if (data.pages <= 7) {
                    pageNum = i + 1
                  } else if (page <= 4) {
                    pageNum = i + 1
                  } else if (page >= data.pages - 3) {
                    pageNum = data.pages - 6 + i
                  } else {
                    pageNum = page - 3 + i
                  }
                  
                  return (
                    <button
                      key={pageNum}
                      onClick={() => handlePageChange(pageNum)}
                      className={`w-10 h-10 rounded-lg transition ${
                        page === pageNum
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-800 hover:bg-gray-700'
                      }`}
                    >
                      {pageNum}
                    </button>
                  )
                })}
              </div>
              
              <button
                onClick={() => handlePageChange(page + 1)}
                disabled={page === data.pages}
                className="px-4 py-2 bg-gray-800 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700 transition"
              >
                下一页
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-12 text-gray-400">
          <p className="text-xl mb-2">暂无视频</p>
          <p className="text-sm">该分类下还没有视频</p>
        </div>
      )}
    </div>
  )
}

export default Category
