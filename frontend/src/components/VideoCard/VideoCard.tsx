import { Link } from 'react-router-dom'

interface VideoCardProps {
  video: {
    id: number
    title: string
    poster_url?: string
    duration?: number
    view_count?: number
    average_rating?: number
    release_year?: number
  }
}

const VideoCard: React.FC<VideoCardProps> = ({ video }) => {
  return (
    <Link
      to={`/video/${video.id}`}
      className="group block bg-gray-800 rounded-lg overflow-hidden hover:ring-2 hover:ring-blue-500 transition-all"
    >
      {/* Poster */}
      <div className="relative aspect-video bg-gray-700">
        {video.poster_url ? (
          <img
            src={video.poster_url}
            alt={video.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-500">
            <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
              />
            </svg>
          </div>
        )}

        {/* Duration Badge */}
        {video.duration && (
          <div className="absolute bottom-2 right-2 bg-black bg-opacity-75 px-2 py-1 rounded text-xs">
            {Math.floor(video.duration / 60)}:{(video.duration % 60).toString().padStart(2, '0')}
          </div>
        )}
      </div>

      {/* Info */}
      <div className="p-3">
        <h3 className="font-semibold text-sm line-clamp-2 mb-2 group-hover:text-blue-400 transition-colors">
          {video.title}
        </h3>

        <div className="flex items-center justify-between text-xs text-gray-400">
          {/* Rating */}
          {video.average_rating !== undefined && (
            <div className="flex items-center">
              <svg className="w-4 h-4 fill-yellow-500 mr-1" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              <span>{video.average_rating.toFixed(1)}</span>
            </div>
          )}

          {/* Year */}
          {video.release_year && <span>{video.release_year}</span>}
        </div>

        {/* Views */}
        {video.view_count !== undefined && (
          <div className="text-xs text-gray-500 mt-1">
            {video.view_count.toLocaleString()} views
          </div>
        )}
      </div>
    </Link>
  )
}

export default VideoCard
