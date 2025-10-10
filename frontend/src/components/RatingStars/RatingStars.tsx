import { useState, useEffect } from 'react'
import { ratingService } from '../../services/ratingService'

interface RatingStarsProps {
  videoId: number
}

const RatingStars = ({ videoId }: RatingStarsProps) => {
  const [averageRating, setAverageRating] = useState(0)
  const [ratingCount, setRatingCount] = useState(0)
  const [userRating, setUserRating] = useState<number | null>(null)
  const [hoveredRating, setHoveredRating] = useState(0)
  const [loading, setLoading] = useState(false)

  const loadRatingStats = async () => {
    try {
      const stats = await ratingService.getVideoRatingStats(videoId)
      setAverageRating(stats.average_rating)
      setRatingCount(stats.rating_count)
      setUserRating(stats.user_rating)
    } catch (error) {
      console.error('Failed to load rating stats:', error)
    }
  }

  useEffect(() => {
    loadRatingStats()
  }, [videoId])

  const handleRate = async (score: number) => {
    try {
      setLoading(true)
      await ratingService.rateVideo(videoId, score)
      await loadRatingStats()
    } catch (error: any) {
      if (error.response?.status === 401) {
        alert('Please login to rate this video')
      } else {
        alert('Failed to rate video')
      }
    } finally {
      setLoading(false)
    }
  }

  const renderStars = (rating: number, interactive: boolean = false) => {
    const stars = []
    const fullStars = Math.floor(rating / 2) // Convert 0-10 to 0-5
    const hasHalfStar = (rating / 2) % 1 >= 0.5

    for (let i = 1; i <= 5; i++) {
      const filled = i <= fullStars || (i === fullStars + 1 && hasHalfStar)
      const displayRating = hoveredRating || (userRating ?? 0)
      const isHovered = interactive && i <= Math.ceil(displayRating / 2)

      stars.push(
        <button
          key={i}
          type="button"
          disabled={!interactive || loading}
          onClick={() => interactive && handleRate(i * 2)}
          onMouseEnter={() => interactive && setHoveredRating(i * 2)}
          onMouseLeave={() => interactive && setHoveredRating(0)}
          className={`text-2xl ${interactive ? 'cursor-pointer' : 'cursor-default'} ${
            filled || isHovered ? 'text-yellow-400' : 'text-gray-300'
          }`}
        >
          ★
        </button>
      )
    }
    return stars
  }

  return (
    <div className="rating-stars">
      <div className="flex items-center space-x-4">
        <div>
          <div className="text-sm text-gray-600 mb-1">Average Rating</div>
          <div className="flex items-center space-x-1">
            {renderStars(averageRating, false)}
            <span className="ml-2 text-sm text-gray-600">
              {averageRating.toFixed(1)}/10 ({ratingCount} {ratingCount === 1 ? 'rating' : 'ratings'})
            </span>
          </div>
        </div>
      </div>

      <div className="mt-4">
        <div className="text-sm text-gray-600 mb-1">
          {userRating ? 'Your Rating' : 'Rate this video'}
        </div>
        <div className="flex items-center space-x-1">
          {renderStars(userRating ?? hoveredRating, true)}
          {userRating && (
            <span className="ml-2 text-sm text-gray-600">
              {userRating.toFixed(1)}/10
            </span>
          )}
        </div>
        {hoveredRating > 0 && !userRating && (
          <div className="text-sm text-gray-500 mt-1">
            Click to rate: {hoveredRating.toFixed(1)}/10
          </div>
        )}
      </div>
    </div>
  )
}

export default RatingStars
