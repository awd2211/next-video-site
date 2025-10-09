import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { videoService } from '@/services/videoService'
import VideoPlayer from '@/components/VideoPlayer'

const VideoDetail = () => {
  const { id } = useParams<{ id: string }>()

  const { data: video, isLoading } = useQuery({
    queryKey: ['video', id],
    queryFn: () => videoService.getVideo(Number(id)),
    enabled: !!id,
  })

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
          onTimeUpdate={(time) => console.log('Current time:', time)}
          onEnded={() => console.log('Video ended')}
        />
      </div>

      {/* Video Info */}
      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        <h1 className="text-3xl font-bold mb-4">{video.title}</h1>

        {/* Meta info */}
        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-400 mb-4">
          {video.release_year && <span>{video.release_year}</span>}
          {video.duration && (
            <span>
              {Math.floor(video.duration / 60)}h {video.duration % 60}m
            </span>
          )}
          {video.country && <span>{video.country.name}</span>}
          <span className="flex items-center">
            <svg className="w-5 h-5 mr-1 fill-yellow-500" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            {video.average_rating.toFixed(1)} ({video.rating_count})
          </span>
          <span>{video.view_count.toLocaleString()} views</span>
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
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-4">Comments ({video.comment_count})</h2>
        <p className="text-gray-400">Comments functionality coming soon...</p>
      </div>
    </div>
  )
}

export default VideoDetail
