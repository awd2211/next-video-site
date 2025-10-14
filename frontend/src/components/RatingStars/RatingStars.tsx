import { useState, useEffect } from 'react'
import { ratingService } from '../../services/ratingService'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'

interface RatingStarsProps {
  videoId: number
}

const RatingStars = ({ videoId }: RatingStarsProps) => {
  const { t } = useTranslation()
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
      toast.success(t('video.ratingSuccess'))
    } catch (error: any) {
      if (error.response?.status === 401) {
        toast.error(t('validation.loginRequired'))
      } else {
        toast.error(t('video.ratingFailed'))
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
          <div className="text-sm text-gray-600 mb-1">{t('video.averageRating')}</div>
          <div className="flex items-center space-x-1">
            {renderStars(averageRating, false)}
            <span className="ml-2 text-sm text-gray-600">
              {averageRating.toFixed(1)}/10 ({t('video.ratingCount', { count: ratingCount })})
            </span>
          </div>
        </div>
      </div>

      <div className="mt-4">
        <div className="text-sm text-gray-600 mb-1">
          {userRating ? t('video.yourRating') : t('video.rateThisVideo')}
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
            {t('video.clickToRate')}: {hoveredRating.toFixed(1)}/10
          </div>
        )}
      </div>
    </div>
  )
}

export default RatingStars
