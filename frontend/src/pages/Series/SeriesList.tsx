/**
 * 视频专辑/系列列表页 - 用户端
 */
import React, { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import seriesService, { SeriesListItem, SeriesType } from '@/services/seriesService'

const SeriesList: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const [series, setSeries] = useState<SeriesListItem[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const pageSize = 20

  const typeFilter = searchParams.get('type') as SeriesType | null

  // 加载数据
  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      try {
        const response = await seriesService.getList({
          page,
          page_size: pageSize,
          type: typeFilter || undefined,
        })
        setSeries(response.items)
        setTotal(response.total)
      } catch (error) {
        console.error('加载专辑列表失败', error)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [page, typeFilter])

  // 类型标签
  const getTypeLabel = (type: SeriesType) => {
    const typeMap = {
      series: '系列剧',
      collection: '合集',
      franchise: '系列作品',
    }
    return typeMap[type]
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">视频专辑</h1>

      {/* 类型筛选 */}
      <div className="mb-6 flex gap-2">
        <button
          onClick={() => {
            setSearchParams({})
            setPage(1)
          }}
          className={`px-4 py-2 rounded ${
            !typeFilter ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          全部
        </button>
        <button
          onClick={() => {
            setSearchParams({ type: 'series' })
            setPage(1)
          }}
          className={`px-4 py-2 rounded ${
            typeFilter === 'series' ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          系列剧
        </button>
        <button
          onClick={() => {
            setSearchParams({ type: 'collection' })
            setPage(1)
          }}
          className={`px-4 py-2 rounded ${
            typeFilter === 'collection' ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          合集
        </button>
        <button
          onClick={() => {
            setSearchParams({ type: 'franchise' })
            setPage(1)
          }}
          className={`px-4 py-2 rounded ${
            typeFilter === 'franchise' ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          系列作品
        </button>
      </div>

      {/* 专辑网格 */}
      {loading ? (
        <div className="text-center py-12">加载中...</div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {series.map((item) => (
              <div
                key={item.id}
                className="cursor-pointer hover:shadow-lg transition-shadow rounded-lg overflow-hidden bg-white"
                onClick={() => navigate(`/series/${item.id}`)}
              >
                {/* 封面 */}
                <div className="relative aspect-[2/3]">
                  {item.cover_image ? (
                    <img
                      src={item.cover_image}
                      alt={item.title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                      <span className="text-gray-400">无封面</span>
                    </div>
                  )}
                  {/* 推荐标签 */}
                  {item.is_featured && (
                    <div className="absolute top-2 right-2 bg-red-500 text-white text-xs px-2 py-1 rounded">
                      推荐
                    </div>
                  )}
                  {/* 类型标签 */}
                  <div className="absolute bottom-2 left-2 bg-black bg-opacity-70 text-white text-xs px-2 py-1 rounded">
                    {getTypeLabel(item.type)}
                  </div>
                </div>

                {/* 信息 */}
                <div className="p-3">
                  <h3 className="font-semibold truncate mb-1">{item.title}</h3>
                  <div className="text-sm text-gray-600 space-y-1">
                    <div>共 {item.total_episodes} 集</div>
                    <div>播放 {item.total_views.toLocaleString()}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* 分页 */}
          {total > pageSize && (
            <div className="mt-8 flex justify-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
              >
                上一页
              </button>
              <span className="px-4 py-2">
                第 {page} 页 / 共 {Math.ceil(total / pageSize)} 页
              </span>
              <button
                onClick={() => setPage((p) => Math.min(Math.ceil(total / pageSize), p + 1))}
                disabled={page >= Math.ceil(total / pageSize)}
                className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
              >
                下一页
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default SeriesList
