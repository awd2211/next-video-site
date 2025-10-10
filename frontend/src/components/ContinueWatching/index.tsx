import { Link } from 'react-router-dom'
import { Play } from 'lucide-react'

interface WatchHistory {
  id: number
  video_id: number
  video: {
    id: number
    title: string
    poster_url: string
    duration: number
  }
  progress: number
  watched_at: string
}

interface ContinueWatchingProps {
  history: WatchHistory[]
}

const ContinueWatching: React.FC<ContinueWatchingProps> = ({ history }) => {
  if (!history || history.length === 0) {
    return null
  }

  return (
    <div>
      {history.map((item) => {
        const progressPercentage = (item.progress / item.video.duration) * 100

        return (
          <Link
            key={item.id}
            to={`/video/${item.video.id}`}
            className="group relative"
          >
            <div className="card hover:ring-2 hover:ring-red-600 transition-all">
              {/* Thumbnail */}
              <div className="relative aspect-video overflow-hidden">
                <img
                  src={item.video.poster_url || '/placeholder.jpg'}
                  alt={item.video.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />

                {/* Play Overlay */}
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <div className="bg-red-600 rounded-full p-4">
                    <Play className="w-8 h-8" fill="currentColor" />
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-700">
                  <div
                    className="h-full bg-red-600 transition-all"
                    style={{ width: `${progressPercentage}%` }}
                  />
                </div>

                {/* Time Remaining */}
                <div className="absolute bottom-2 right-2 bg-black bg-opacity-80 px-2 py-1 rounded text-xs">
                  {Math.floor((item.video.duration - item.progress) / 60)}分钟剩余
                </div>
              </div>

              {/* Info */}
              <div className="p-4">
                <h3 className="font-semibold text-lg line-clamp-2 group-hover:text-red-600 transition-colors">
                  {item.video.title}
                </h3>
                <p className="text-sm text-gray-400 mt-1">
                  已观看 {Math.round(progressPercentage)}%
                </p>
              </div>
            </div>
          </Link>
        )
      })}
    </div>
  )
}

export default ContinueWatching
