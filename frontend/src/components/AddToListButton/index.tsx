/**
 * Add to List Button Component
 * Toggle button to add/remove videos from watchlist
 */
import { useState, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import watchlistService from '@/services/watchlistService'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'

interface AddToListButtonProps {
  videoId: number
  variant?: 'icon' | 'button' | 'compact'
  className?: string
  onSuccess?: () => void
}

const AddToListButton: React.FC<AddToListButtonProps> = ({
  videoId,
  variant = 'button',
  className = '',
  onSuccess,
}) => {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [isInList, setIsInList] = useState(false)

  // Check if video is in watchlist
  const { data: status } = useQuery({
    queryKey: ['watchlist-status', videoId],
    queryFn: () => watchlistService.checkStatus(videoId),
    retry: false,
  })

  useEffect(() => {
    if (status) {
      setIsInList(status.in_watchlist)
    }
  }, [status])

  // Add to list mutation
  const addMutation = useMutation({
    mutationFn: () => watchlistService.addToList(videoId),
    onSuccess: () => {
      setIsInList(true)
      queryClient.invalidateQueries({ queryKey: ['watchlist'] })
      queryClient.invalidateQueries({ queryKey: ['watchlist-status', videoId] })
      onSuccess?.()
    },
  })

  // Remove from list mutation
  const removeMutation = useMutation({
    mutationFn: () => watchlistService.removeFromList(videoId),
    onSuccess: () => {
      setIsInList(false)
      queryClient.invalidateQueries({ queryKey: ['watchlist'] })
      queryClient.invalidateQueries({ queryKey: ['watchlist-status', videoId] })
      onSuccess?.()
    },
  })

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()

    const token = localStorage.getItem('access_token')
    if (!token) {
      toast.error(t('validation.loginRequired'))
      return
    }

    if (isInList) {
      removeMutation.mutate()
    } else {
      addMutation.mutate()
    }
  }

  const isLoading = addMutation.isPending || removeMutation.isPending

  // Icon variant (for video cards)
  if (variant === 'icon') {
    return (
      <button
        onClick={handleClick}
        disabled={isLoading}
        className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
          isInList
            ? 'bg-red-600 hover:bg-red-700'
            : 'bg-gray-700/80 hover:bg-gray-600'
        } disabled:opacity-50 ${className}`}
        title={isInList ? '从列表移除' : '加入我的列表'}
      >
        {isLoading ? (
          <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
        ) : isInList ? (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clipRule="evenodd"
            />
          </svg>
        ) : (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
        )}
      </button>
    )
  }

  // Compact variant (for video detail page - inline)
  if (variant === 'compact') {
    return (
      <button
        onClick={handleClick}
        disabled={isLoading}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
          isInList
            ? 'bg-gray-700 hover:bg-gray-600 text-white'
            : 'bg-white hover:bg-gray-100 text-gray-900'
        } disabled:opacity-50 ${className}`}
      >
        {isLoading ? (
          <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
        ) : isInList ? (
          <>
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clipRule="evenodd"
              />
            </svg>
            <span>已在列表</span>
          </>
        ) : (
          <>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            <span>加入列表</span>
          </>
        )}
      </button>
    )
  }

  // Button variant (default - full button)
  return (
    <button
      onClick={handleClick}
      disabled={isLoading}
      className={`flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium transition ${
        isInList
          ? 'bg-gray-700 hover:bg-gray-600'
          : 'bg-red-600 hover:bg-red-700'
      } disabled:opacity-50 ${className}`}
    >
      {isLoading ? (
        <>
          <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          <span>处理中...</span>
        </>
      ) : isInList ? (
        <>
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clipRule="evenodd"
            />
          </svg>
          <span>已在我的列表</span>
        </>
      ) : (
        <>
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          <span>加入我的列表</span>
        </>
      )}
    </button>
  )
}

export default AddToListButton
