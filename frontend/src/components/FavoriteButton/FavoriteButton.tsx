import { useState, useEffect } from 'react'
import { favoriteService } from '../../services/favoriteService'
import FolderSelector from '../FolderSelector'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'

interface FavoriteButtonProps {
  videoId: number
  className?: string
  enableFolderSelection?: boolean // New prop to enable folder selection
}

const FavoriteButton = ({
  videoId,
  className = '',
  enableFolderSelection = true
}: FavoriteButtonProps) => {
  const { t } = useTranslation()
  const [isFavorited, setIsFavorited] = useState(false)
  const [loading, setLoading] = useState(false)
  const [showFolderSelector, setShowFolderSelector] = useState(false)

  const checkFavorite = async () => {
    try {
      const favorited = await favoriteService.checkFavorite(videoId)
      setIsFavorited(favorited)
    } catch (error) {
      console.error('Failed to check favorite status:', error)
    }
  }

  useEffect(() => {
    checkFavorite()
  }, [videoId])

  const handleToggleFavorite = async () => {
    try {
      if (isFavorited) {
        // Remove favorite
        setLoading(true)
        await favoriteService.removeFavorite(videoId)
        setIsFavorited(false)
      } else {
        // Add favorite - show folder selector if enabled
        if (enableFolderSelection) {
          setShowFolderSelector(true)
        } else {
          setLoading(true)
          await favoriteService.addFavorite(videoId)
          setIsFavorited(true)
        }
      }
    } catch (error: any) {
      if (error.response?.status === 401) {
        toast.error(t('validation.loginRequired'))
      } else {
        toast.error(t('favorites.updateFailed'))
      }
    } finally {
      setLoading(false)
    }
  }

  const handleFolderSelect = async (folderId?: number) => {
    try {
      setLoading(true)
      setShowFolderSelector(false)
      await favoriteService.addFavorite(videoId, folderId)
      setIsFavorited(true)
      toast.success(t('favorites.addedToFavorites'))
    } catch (error: any) {
      if (error.response?.status === 401) {
        toast.error(t('validation.loginRequired'))
      } else {
        toast.error(t('favorites.addFailed'))
      }
    } finally {
      setLoading(false)
    }
  }

  const handleCancelFolderSelect = () => {
    setShowFolderSelector(false)
  }

  return (
    <>
      <button
        onClick={handleToggleFavorite}
        disabled={loading}
        className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
          isFavorited
            ? 'bg-red-600 text-white hover:bg-red-700'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        } disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      >
        <svg
          className="w-5 h-5"
          fill={isFavorited ? 'currentColor' : 'none'}
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
          />
        </svg>
        <span>{isFavorited ? 'Favorited' : 'Add to Favorites'}</span>
      </button>

      {/* Folder Selector Modal */}
      {showFolderSelector && (
        <FolderSelector
          onSelect={handleFolderSelect}
          onCancel={handleCancelFolderSelect}
        />
      )}
    </>
  )
}

export default FavoriteButton
