import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { videoService } from '@/services/videoService'
import VideoPlayer from '@/components/VideoPlayer'
import CommentSection from '@/components/CommentSection'
import RatingStars from '@/components/RatingStars'
import FavoriteButton from '@/components/FavoriteButton'
import VideoCard from '@/components/VideoCard'
import { useWatchHistory } from '@/hooks/useWatchHistory'
import { useEffect, useRef } from 'react'

const VideoDetail = () => {
  const { id } = useParams<{ id: string }>()
  const playerRef = useRef<any>(null)

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

  // Fetch recommended videos
  const { data: recommendedData } = useQuery({
    queryKey: ['recommended-videos'],
    queryFn: () => videoService.getRecommendedVideos(1, 6),
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
      {/* Video Player */}
      <div className="mb-6">
        <VideoPlayer
          src={video.video_url || ''}
          poster={video.backdrop_url || video.poster_url}
          initialTime={0}
        />
      </div>

      {/* Video Info */}
      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        {/* Title and Actions Row */}
        <div className="flex items-start justify-between mb-4">
          <h1 className="text-3xl font-bold flex-1">{video.title}</h1>
          <div className="ml-4">
            <FavoriteButton videoId={Number(id)} />
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
        <CommentSection videoId={Number(id)} />
      </div>

      {/* Recommended Videos */}
      {recommendedData && recommendedData.items && recommendedData.items.length > 0 && (
        <div className="mb-6">
          <h2 className="text-2xl font-bold mb-4">Recommended for You</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {recommendedData.items.map((recommendedVideo) => (
              <VideoCard key={recommendedVideo.id} video={recommendedVideo} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default VideoDetail
