import { useState, useEffect } from 'react'
import { Play, Star, Clock, Eye } from 'lucide-react'
import type { Video } from '@/types'

interface VideoPreviewProps {
  video: Video
  position: { x: number; y: number }
  onClose: () => void
}

/**
 * VideoPreview - Enhanced preview card shown on hover
 * Displays additional video information in a larger card
 */
const VideoPreview = ({ video, position, onClose }: VideoPreviewProps) => {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    // Delay showing preview to avoid flickering
    const timer = setTimeout(() => setIsVisible(true), 500)
    return () => clearTimeout(timer)
  }, [])

  if (!isVisible) return null

  // Calculate position to keep preview in viewport
  const cardWidth = 320
  const cardHeight = 400
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight

  let left = position.x
  let top = position.y

  // Adjust horizontal position
  if (left + cardWidth > viewportWidth) {
    left = viewportWidth - cardWidth - 20
  }

  // Adjust vertical position
  if (top + cardHeight > viewportHeight) {
    top = viewportHeight - cardHeight - 20
  }

  return (
    <>
      {/* Backdrop to detect mouse leave */}
      <div
        className="fixed inset-0 z-40"
        onMouseEnter={onClose}
      />

      {/* Preview card */}
      <div
        className="fixed z-50 bg-gray-900 rounded-lg shadow-2xl border border-gray-700 overflow-hidden animate-scaleIn"
        style={{
          left: `${left}px`,
          top: `${top}px`,
          width: `${cardWidth}px`,
        }}
        onMouseLeave={onClose}
      >
        {/* Thumbnail */}
        <div className="relative aspect-video overflow-hidden group">
          <img
            src={video.poster_url || '/placeholder.jpg'}
            alt={video.title}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent" />

          {/* Play button */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="bg-red-600 rounded-full p-4 transform group-hover:scale-110 transition-transform">
              <Play className="w-6 h-6" fill="currentColor" />
            </div>
          </div>

          {/* Duration badge */}
          {video.duration && (
            <div className="absolute bottom-2 right-2 bg-black/80 px-2 py-1 rounded text-xs flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {Math.floor(video.duration / 60)}:{(video.duration % 60).toString().padStart(2, '0')}
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-4 space-y-3">
          {/* Title */}
          <h3 className="font-bold text-lg line-clamp-2 leading-tight">
            {video.title}
          </h3>

          {/* Stats */}
          <div className="flex items-center gap-4 text-sm text-gray-400">
            {video.average_rating > 0 && (
              <div className="flex items-center gap-1">
                <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                <span>{video.average_rating.toFixed(1)}</span>
              </div>
            )}
            <div className="flex items-center gap-1">
              <Eye className="w-4 h-4" />
              <span>
                {video.view_count > 10000
                  ? `${(video.view_count / 10000).toFixed(1)}万`
                  : video.view_count}
              </span>
            </div>
          </div>

          {/* Description */}
          {video.description && (
            <p className="text-sm text-gray-400 line-clamp-3 leading-relaxed">
              {video.description}
            </p>
          )}

          {/* Categories */}
          {video.categories && video.categories.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {video.categories.slice(0, 3).map((category) => (
                <span
                  key={category.id}
                  className="px-2 py-1 bg-gray-800 rounded text-xs text-gray-300"
                >
                  {category.name}
                </span>
              ))}
            </div>
          )}

          {/* Actors */}
          {video.actors && video.actors.length > 0 && (
            <div className="text-sm">
              <span className="text-gray-500">主演：</span>
              <span className="text-gray-300">
                {video.actors.slice(0, 3).map(a => a.name).join('、')}
              </span>
            </div>
          )}

          {/* Year and Type */}
          <div className="flex items-center gap-3 text-xs text-gray-500">
            {video.release_year && <span>{video.release_year}</span>}
            {video.video_type && <span>{video.video_type}</span>}
            {video.language && (
              <span className="px-2 py-0.5 bg-red-600 text-white rounded">
                {video.language}
              </span>
            )}
          </div>
        </div>
      </div>
    </>
  )
}

export default VideoPreview
