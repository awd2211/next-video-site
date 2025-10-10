import { useState, useRef, memo, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Play, Heart, Plus, Eye, Star } from 'lucide-react'
import { Video } from '@/types'
import LazyImage from '@/components/LazyImage'
import VideoPreview from '@/components/VideoPreview'

interface VideoCardProps {
  video: Video
  showQuickActions?: boolean
  enablePreview?: boolean
}

const VideoCard: React.FC<VideoCardProps> = memo(({
  video,
  showQuickActions = true,
  enablePreview = true
}) => {
  const [isHovered, setIsHovered] = useState(false)
  const [isFavorited, setIsFavorited] = useState(false)
  const [isLiked, setIsLiked] = useState(false)
  const [showPreview, setShowPreview] = useState(false)
  const [previewPosition, setPreviewPosition] = useState({ x: 0, y: 0 })
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const cardRef = useRef<HTMLDivElement>(null)
  
  // Cleanup timeout on unmount to prevent memory leaks
  useEffect(() => {
    return () => {
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current)
        hoverTimeoutRef.current = null
      }
    }
  }, [])

  const handleFavorite = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsFavorited(!isFavorited)
    // TODO: 调用收藏API
  }

  const handleLike = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsLiked(!isLiked)
    // TODO: 调用点赞API
  }

  const handleMouseEnter = () => {
    setIsHovered(true)

    // Start timer for preview
    if (enablePreview) {
      hoverTimeoutRef.current = setTimeout(() => {
        if (cardRef.current) {
          const rect = cardRef.current.getBoundingClientRect()
          setPreviewPosition({
            x: rect.right + 10,
            y: rect.top
          })
          setShowPreview(true)
        }
      }, 800) // Show preview after 800ms hover
    }
  }

  const handleMouseLeave = () => {
    setIsHovered(false)

    // Clear preview timer
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current)
      hoverTimeoutRef.current = null
    }
    setShowPreview(false)
  }

  return (
    <>
      <Link
        to={`/video/${video.id}`}
        className="group"
        ref={cardRef}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
      <div className="card hover:ring-2 hover:ring-red-600 transition-all duration-300 overflow-hidden">
        {/* Thumbnail */}
        <div className="relative aspect-video overflow-hidden bg-gray-800">
          <LazyImage
            src={video.poster_url || '/placeholder.jpg'}
            alt={video.title}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
          />

          {/* Hover Overlay */}
          {isHovered && showQuickActions && (
            <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent animate-fadeIn">
              {/* Play Button */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="bg-red-600 rounded-full p-4 transform scale-0 group-hover:scale-100 transition-transform duration-300">
                  <Play className="w-8 h-8" fill="currentColor" />
                </div>
              </div>

              {/* Quick Actions */}
              <div className="absolute top-2 right-2 flex flex-col space-y-2">
                <button
                  onClick={handleFavorite}
                  className={`p-2 rounded-full backdrop-blur-sm transition-all ${
                    isFavorited
                      ? 'bg-red-600 text-white'
                      : 'bg-black/50 text-white hover:bg-red-600'
                  }`}
                  title="收藏"
                >
                  <Plus className="w-5 h-5" />
                </button>
                <button
                  onClick={handleLike}
                  className={`p-2 rounded-full backdrop-blur-sm transition-all ${
                    isLiked
                      ? 'bg-red-600 text-white'
                      : 'bg-black/50 text-white hover:bg-red-600'
                  }`}
                  title="点赞"
                >
                  <Heart className={`w-5 h-5 ${isLiked ? 'fill-current' : ''}`} />
                </button>
              </div>

              {/* Bottom Info */}
              <div className="absolute bottom-2 left-2 right-2 flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2 text-white">
                  {video.video_type && (
                    <span className="px-2 py-1 bg-red-600 rounded">
                      {video.video_type}
                    </span>
                  )}
                </div>
                {video.duration && (
                  <div className="bg-black/80 px-2 py-1 rounded">
                    {Math.floor(video.duration / 60)}:{(video.duration % 60).toString().padStart(2, '0')}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Duration (always visible on non-hover) */}
          {!isHovered && video.duration && (
            <div className="absolute bottom-2 right-2 bg-black/80 px-2 py-1 rounded text-xs">
              {Math.floor(video.duration / 60)}:{(video.duration % 60).toString().padStart(2, '0')}
            </div>
          )}

          {/* Quality Badge */}
          {video.is_av1_available && (
            <div className="absolute top-2 left-2 bg-gradient-to-r from-green-600 to-blue-600 px-2 py-1 rounded text-xs font-bold">
              AV1
            </div>
          )}
        </div>

        {/* Info */}
        <div className="p-4">
          <h3 className="font-semibold text-lg line-clamp-2 group-hover:text-red-600 transition-colors mb-2">
            {video.title}
          </h3>

          {/* Meta Info */}
          <div className="flex items-center justify-between text-sm text-gray-400">
            <span className="flex items-center space-x-1">
              {video.release_year && <span>{video.release_year}</span>}
            </span>
            <div className="flex items-center space-x-3">
              {video.average_rating > 0 && (
                <span className="flex items-center space-x-1">
                  <Star className="w-4 h-4 fill-yellow-500 text-yellow-500" />
                  <span>{video.average_rating.toFixed(1)}</span>
                </span>
              )}
              <span className="flex items-center space-x-1">
                <Eye className="w-4 h-4" />
                <span>{formatViewCount(video.view_count)}</span>
              </span>
            </div>
          </div>

          {/* Description (show on hover) */}
          {isHovered && video.description && (
            <p className="text-sm text-gray-400 mt-2 line-clamp-2 animate-fadeIn">
              {video.description}
            </p>
          )}
        </div>
      </div>
      </Link>

      {/* Enhanced Preview on Long Hover */}
      {showPreview && (
        <VideoPreview
          video={video}
          position={previewPosition}
          onClose={() => setShowPreview(false)}
        />
      )}
    </>
  )
}, (prevProps, nextProps) => {
  // Custom comparison function for memo
  // Only re-render if video id or critical props change
  return (
    prevProps.video.id === nextProps.video.id &&
    prevProps.video.view_count === nextProps.video.view_count &&
    prevProps.video.average_rating === nextProps.video.average_rating &&
    prevProps.showQuickActions === nextProps.showQuickActions &&
    prevProps.enablePreview === nextProps.enablePreview
  )
})

VideoCard.displayName = 'VideoCard'

// Helper function to format view count
const formatViewCount = (count: number): string => {
  if (count >= 1000000) {
    return `${(count / 1000000).toFixed(1)}M`
  } else if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}K`
  }
  return count.toString()
}

export default VideoCard
