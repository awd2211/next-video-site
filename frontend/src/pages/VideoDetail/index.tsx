import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { videoService } from '@/services/videoService'
import { recommendationService } from '@/services/recommendationService'
import VideoCard from '@/components/VideoCard'
import RatingStars from '@/components/RatingStars'
import FavoriteButton from '@/components/FavoriteButton'
import ShareButton from '@/components/ShareButton'
import { useMobilePlayer } from '@/hooks/useDeviceDetect'
import { useEffect, useState, lazy, Suspense } from 'react'
import { historyService } from '@/services/historyService'
import { VideoDetailSkeleton } from '@/components/Skeleton'

// Lazy load heavy components
const VideoPlayer = lazy(() => import('@/components/VideoPlayer'))
const MobileVideoPlayer = lazy(() => import('@/components/MobileVideoPlayer'))
const CommentSection = lazy(() => import('@/components/CommentSection'))

const VideoDetail = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const useMobile = useMobilePlayer()
  const [initialTime, setInitialTime] = useState(0)

  const { data: video, isLoading } = useQuery({
    queryKey: ['video', id],
    queryFn: () => videoService.getVideo(Number(id)),
    enabled: !!id,
  })

  // Fetch similar videos (intelligent recommendations based on this video)
  const { data: similarVideos } = useQuery({
    queryKey: ['similar-videos', id],
    queryFn: () => recommendationService.getSimilarVideos(Number(id), 6),
    enabled: !!id,
  })

  // Load last watch position
  useEffect(() => {
    const loadPosition = async () => {
      if (video && id) {
        try {
          const history = await historyService.getVideoHistory(Number(id))
          if (history && history.last_position > 0 && !history.is_completed) {
            setInitialTime(history.last_position)
          }
        } catch (error) {
          console.error('Failed to load watch position:', error)
        }
      }
    }
    loadPosition()
  }, [video, id])

  if (isLoading) {
    return <VideoDetailSkeleton />
  }

  if (!video) {
    return (
      <div className="max-w-7xl mx-auto text-center py-20">
        <div className="bg-gray-800 rounded-lg p-12">
          <svg className="w-24 h-24 mx-auto mb-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <h2 className="text-3xl font-bold mb-4">视频不存在</h2>
          <p className="text-gray-400 mb-8">抱歉，该视频可能已被删除或暂时不可用</p>
          <button
            onClick={() => navigate('/')}
            className="bg-red-600 hover:bg-red-700 px-6 py-3 rounded-lg transition-colors"
          >
            返回首页
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Video Player - 自动切换桌面/移动端播放器 */}
      <div className="mb-6">
        <Suspense fallback={
          <div className="aspect-video bg-gray-800 rounded-lg flex items-center justify-center">
            <div className="flex flex-col items-center gap-4">
              <div className="w-12 h-12 border-4 border-red-600 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-gray-400">加载播放器...</p>
            </div>
          </div>
        }>
          {useMobile ? (
            <MobileVideoPlayer
              src={video.video_url || ''}
              poster={video.backdrop_url || video.poster_url}
              initialTime={initialTime}
            />
          ) : (
            <VideoPlayer
              src={video.video_url || ''}
              poster={video.backdrop_url || video.poster_url}
              videoId={video.id}
              initialTime={initialTime}
              autoSaveProgress={true}
              enableSubtitles={true}
            />
          )}
        </Suspense>
      </div>

      {/* Video Info */}
      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        {/* Title and Actions Row */}
        <div className="flex items-start justify-between mb-4">
          <h1 className="text-3xl font-bold flex-1">{video.title}</h1>
          <div className="flex items-center gap-3 ml-4">
            <FavoriteButton videoId={Number(id)} />
            <ShareButton videoId={Number(id)} videoTitle={video.title} />
          </div>
        </div>

        {/* Meta info */}
        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-400 mb-4">
          {video.release_year && <span>{video.release_year}</span>}
          {video.duration && (
            <span>
              {Math.floor(video.duration / 60)}h {video.duration % 60}m
            </span>
          )}
          {video.country && <span>{video.country.name}</span>}
          <span>{video.view_count.toLocaleString()} views</span>
        </div>

        {/* Rating Section */}
        <div className="mb-4">
          <RatingStars videoId={Number(id)} />
        </div>

        {/* Categories */}
        {video.categories && video.categories.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {video.categories.map((category) => (
              <span
                key={category.id}
                className="bg-gray-700 px-3 py-1 rounded-full text-sm"
              >
                {category.name}
              </span>
            ))}
          </div>
        )}

        {/* Description */}
        {video.description && (
          <div className="mb-4">
            <h3 className="font-semibold mb-2">Description</h3>
            <p className="text-gray-300">{video.description}</p>
          </div>
        )}

        {/* Cast */}
        {video.actors && video.actors.length > 0 && (
          <div className="mb-4">
            <h3 className="font-semibold mb-2">Cast</h3>
            <div className="flex flex-wrap gap-2">
              {video.actors.map((actor) => (
                <div key={actor.id} className="flex items-center bg-gray-700 rounded-full px-3 py-1">
                  {actor.avatar && (
                    <img
                      src={actor.avatar}
                      alt={actor.name}
                      className="w-6 h-6 rounded-full mr-2"
                    />
                  )}
                  <span className="text-sm">{actor.name}</span>
                  {actor.role_name && (
                    <span className="text-xs text-gray-400 ml-1">as {actor.role_name}</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Directors */}
        {video.directors && video.directors.length > 0 && (
          <div>
            <h3 className="font-semibold mb-2">Directors</h3>
            <div className="flex gap-2">
              {video.directors.map((director) => (
                <span key={director.id} className="text-gray-300">
                  {director.name}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Comments Section */}
      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        <h2 className="text-2xl font-bold mb-6">Comments</h2>
        <Suspense fallback={
          <div className="flex items-center justify-center py-12">
            <div className="flex flex-col items-center gap-4">
              <div className="w-8 h-8 border-4 border-red-600 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-gray-400">加载评论...</p>
            </div>
          </div>
        }>
          <CommentSection videoId={Number(id)} />
        </Suspense>
      </div>

      {/* Similar Videos - Intelligent Recommendations */}
      {similarVideos && similarVideos.length > 0 && (
        <div className="mb-6">
          <h2 className="text-2xl font-bold mb-4">相似推荐</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {similarVideos.map((similarVideo) => (
              <VideoCard key={similarVideo.id} video={similarVideo} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default VideoDetail
