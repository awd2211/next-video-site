import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { ChevronLeft, ChevronRight, Play, Info } from 'lucide-react'
import { Video } from '@/types'

interface HeroCarouselProps {
  videos: Video[]
}

const HeroCarousel: React.FC<HeroCarouselProps> = ({ videos }) => {
  const [currentIndex, setCurrentIndex] = useState(0)

  // Auto-play carousel
  useEffect(() => {
    if (videos.length === 0) return

    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % videos.length)
    }, 5000) // 每5秒切换

    return () => clearInterval(timer)
  }, [videos.length])

  if (!videos || videos.length === 0) {
    return null
  }

  const currentVideo = videos[currentIndex]

  const goToPrevious = () => {
    setCurrentIndex((prev) => (prev - 1 + videos.length) % videos.length)
  }

  const goToNext = () => {
    setCurrentIndex((prev) => (prev + 1) % videos.length)
  }

  return (
    <div className="relative h-[500px] rounded-lg overflow-hidden group">
      {/* Background Image with Parallax Effect */}
      <div className="absolute inset-0 transition-transform duration-700">
        <img
          src={currentVideo.backdrop_url || currentVideo.poster_url || '/placeholder.jpg'}
          alt={currentVideo.title}
          className="w-full h-full object-cover"
        />
        {/* Overlay Gradient */}
        <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/60 to-transparent"></div>
        <div className="absolute inset-0 bg-gradient-to-r from-gray-900/80 via-transparent to-transparent"></div>
      </div>

      {/* Content */}
      <div className="relative h-full flex items-end">
        <div className="container mx-auto px-8 pb-12 max-w-2xl">
          {/* Title */}
          <h1 className="text-5xl font-bold mb-4 drop-shadow-lg">
            {currentVideo.title}
          </h1>

          {/* Meta Info */}
          <div className="flex items-center space-x-4 mb-4 text-sm">
            {currentVideo.release_year && (
              <span className="px-3 py-1 bg-gray-800/80 rounded-full">
                {currentVideo.release_year}
              </span>
            )}
            {currentVideo.average_rating > 0 && (
              <span className="flex items-center">
                <span className="text-yellow-500 mr-1">★</span>
                {currentVideo.average_rating.toFixed(1)}
              </span>
            )}
            {currentVideo.duration && (
              <span>
                {Math.floor(currentVideo.duration / 60)}分钟
              </span>
            )}
          </div>

          {/* Description */}
          <p className="text-gray-300 text-lg mb-6 line-clamp-2">
            {currentVideo.description || '精彩内容，即将为您呈现...'}
          </p>

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <Link
              to={`/video/${currentVideo.id}`}
              className="flex items-center space-x-2 bg-red-600 hover:bg-red-700 text-white font-semibold px-8 py-3 rounded-lg transition-colors"
            >
              <Play className="w-5 h-5" fill="currentColor" />
              <span>立即播放</span>
            </Link>
            <Link
              to={`/video/${currentVideo.id}`}
              className="flex items-center space-x-2 bg-gray-700/80 hover:bg-gray-600/80 text-white font-semibold px-8 py-3 rounded-lg transition-colors backdrop-blur-sm"
            >
              <Info className="w-5 h-5" />
              <span>更多信息</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Navigation Arrows */}
      {videos.length > 1 && (
        <>
          <button
            onClick={goToPrevious}
            className="absolute left-4 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white p-3 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
            aria-label="Previous"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>
          <button
            onClick={goToNext}
            className="absolute right-4 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white p-3 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
            aria-label="Next"
          >
            <ChevronRight className="w-6 h-6" />
          </button>
        </>
      )}

      {/* Indicators */}
      {videos.length > 1 && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex space-x-2">
          {videos.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentIndex(index)}
              className={`w-2 h-2 rounded-full transition-all ${
                index === currentIndex
                  ? 'bg-white w-8'
                  : 'bg-white/50 hover:bg-white/75'
              }`}
              aria-label={`Go to slide ${index + 1}`}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default HeroCarousel
