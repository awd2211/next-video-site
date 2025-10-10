/**
 * 视频专辑/系列详情页 - 用户端
 */
import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import seriesService, { SeriesDetail } from '@/services/seriesService'

const SeriesDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [series, setSeries] = useState<SeriesDetail | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const loadData = async () => {
      if (!id) return

      setLoading(true)
      try {
        const data = await seriesService.getDetail(parseInt(id))
        setSeries(data)
      } catch (error) {
        console.error('加载专辑详情失败', error)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [id])

  if (loading) {
    return <div className="container mx-auto px-4 py-12 text-center">加载中...</div>
  }

  if (!series) {
    return <div className="container mx-auto px-4 py-12 text-center">专辑不存在</div>
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* 专辑头部信息 */}
      <div className="flex gap-6 mb-8">
        {/* 封面 */}
        <div className="w-48 flex-shrink-0">
          {series.cover_image ? (
            <img
              src={series.cover_image}
              alt={series.title}
              className="w-full rounded-lg shadow-lg"
            />
          ) : (
            <div className="w-full aspect-[2/3] bg-gray-200 rounded-lg flex items-center justify-center">
              <span className="text-gray-400">无封面</span>
            </div>
          )}
        </div>

        {/* 信息 */}
        <div className="flex-1">
          <h1 className="text-3xl font-bold mb-4">{series.title}</h1>

          <div className="space-y-2 text-gray-700 mb-4">
            <div>
              <span className="font-semibold">类型：</span>
              <span>
                {series.type === 'series' && '系列剧'}
                {series.type === 'collection' && '合集'}
                {series.type === 'franchise' && '系列作品'}
              </span>
            </div>
            <div>
              <span className="font-semibold">总集数：</span>
              <span>{series.total_episodes} 集</span>
            </div>
            <div>
              <span className="font-semibold">播放量：</span>
              <span>{series.total_views.toLocaleString()}</span>
            </div>
            <div>
              <span className="font-semibold">收藏数：</span>
              <span>{series.total_favorites.toLocaleString()}</span>
            </div>
          </div>

          {series.description && (
            <div>
              <h3 className="font-semibold mb-2">简介</h3>
              <p className="text-gray-700 whitespace-pre-wrap">{series.description}</p>
            </div>
          )}
        </div>
      </div>

      {/* 视频列表 */}
      <div>
        <h2 className="text-2xl font-bold mb-4">视频列表</h2>

        {series.videos.length === 0 ? (
          <div className="text-center py-12 text-gray-500">暂无视频</div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {series.videos.map((video) => (
              <div
                key={video.video_id}
                className="cursor-pointer hover:shadow-lg transition-shadow rounded-lg overflow-hidden bg-white"
                onClick={() => navigate(`/videos/${video.video_id}`)}
              >
                {/* 封面 */}
                <div className="relative aspect-video">
                  {video.poster_url ? (
                    <img
                      src={video.poster_url}
                      alt={video.title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                      <span className="text-gray-400 text-sm">无封面</span>
                    </div>
                  )}
                  {/* 集数标签 */}
                  {video.episode_number && (
                    <div className="absolute top-2 left-2 bg-black bg-opacity-70 text-white text-sm px-2 py-1 rounded">
                      第 {video.episode_number} 集
                    </div>
                  )}
                  {/* 时长 */}
                  {video.duration && (
                    <div className="absolute bottom-2 right-2 bg-black bg-opacity-70 text-white text-xs px-2 py-1 rounded">
                      {video.duration} 分钟
                    </div>
                  )}
                </div>

                {/* 信息 */}
                <div className="p-3">
                  <h3 className="font-semibold truncate mb-1 text-sm">{video.title}</h3>
                  <div className="text-xs text-gray-600">
                    播放 {video.view_count.toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 返回按钮 */}
      <div className="mt-8">
        <button
          onClick={() => navigate('/series')}
          className="px-6 py-2 bg-gray-200 rounded hover:bg-gray-300"
        >
          返回列表
        </button>
      </div>
    </div>
  )
}

export default SeriesDetailPage
