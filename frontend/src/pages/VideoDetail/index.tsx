import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { videoService } from '@/services/videoService'
import { recommendationService } from '@/services/recommendationService'
import VideoCard from '@/components/VideoCard'
import RatingStars from '@/components/RatingStars'
import FavoriteButton from '@/components/FavoriteButton'
import ShareButton from '@/components/ShareButton'
import { useWatchHistory } from '@/hooks/useWatchHistory'
import { useMobilePlayer } from '@/hooks/useDeviceDetect'
import { useEffect, useRef, lazy, Suspense } from 'react'

// Lazy load heavy components
const VideoPlayer = lazy(() => import('@/components/VideoPlayer'))
const MobileVideoPlayer = lazy(() => import('@/components/MobileVideoPlayer'))
const CommentSection = lazy(() => import('@/components/CommentSection'))

const VideoDetail = () => {
  const { id } = useParams<{ id: string }>()
  const playerRef = useRef<any>(null)
  const useMobile = useMobilePlayer()

  const { data: video, isLoading } = useQuery({
    queryKey: ['video', id],
    queryFn: () => videoService.getVideo(Number(id)),
    enabled: !!id,
  })

  // Watch history hook
  const { setPlayerRef, resumeFromLastPosition } = useWatchHistory({
    videoId: Number(id),
    duration: video?.duration || 0,
    enabled: !!video,
  })

  // Fetch similar videos (intelligent recommendations based on this video)
  const { data: similarVideos } = useQuery({
    queryKey: ['similar-videos', id],
    queryFn: () => recommendationService.getSimilarVideos(Number(id), 6),
    enabled: !!id,
  })

  // Resume from last position when video loads
  useEffect(() => {
    if (video && playerRef.current) {
      setPlayerRef(playerRef.current)
      resumeFromLastPosition().then((position) => {
        if (position > 0 && playerRef.current?.currentTime) {
          playerRef.current.currentTime(position)
        }
      })
    }
  }, [video, setPlayerRef, resumeFromLastPosition])

  if (isLoading) {
    return <div className="text-center py-12">Loading...</div>
  }

  if (!video) {
    return <div className="text-center py-12">Video not found</div>
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
              initialTime={0}
            />
          ) : (
            <VideoPlayer
              src={video.video_url || ''}
              poster={video.backdrop_url || video.poster_url}
              initialTime={0}
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
