/**
 * Auto Play Hook
 * Handles automatic video playback when current video ends
 */
import { useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { PlaylistVideo } from '../components/PlaylistSidebar'

interface UseAutoPlayOptions {
  /**
   * Current video ID
   */
  currentVideoId: number

  /**
   * List of videos in the playlist
   */
  playlist: PlaylistVideo[]

  /**
   * Whether autoplay is enabled
   */
  enabled?: boolean

  /**
   * Callback when video ends (before auto-navigation)
   */
  onVideoEnd?: () => void

  /**
   * Callback when navigating to next video
   */
  onNext?: (nextVideoId: number) => void
}

export const useAutoPlay = ({
  currentVideoId,
  playlist,
  enabled = true,
  onVideoEnd,
  onNext,
}: UseAutoPlayOptions) => {
  const navigate = useNavigate()

  /**
   * Get the next video in the playlist
   */
  const getNextVideo = useCallback((): PlaylistVideo | null => {
    const currentIndex = playlist.findIndex((v) => v.id === currentVideoId)

    if (currentIndex === -1 || currentIndex === playlist.length - 1) {
      return null // No next video
    }

    return playlist[currentIndex + 1]
  }, [currentVideoId, playlist])

  /**
   * Get the previous video in the playlist
   */
  const getPreviousVideo = useCallback((): PlaylistVideo | null => {
    const currentIndex = playlist.findIndex((v) => v.id === currentVideoId)

    if (currentIndex === -1 || currentIndex === 0) {
      return null // No previous video
    }

    return playlist[currentIndex - 1]
  }, [currentVideoId, playlist])

  /**
   * Play next video
   */
  const playNext = useCallback(() => {
    const nextVideo = getNextVideo()

    if (nextVideo) {
      if (onNext) {
        onNext(nextVideo.id)
      } else {
        navigate(`/videos/${nextVideo.id}`)
      }
    } else {
      console.log('No next video in playlist')
    }
  }, [getNextVideo, navigate, onNext])

  /**
   * Play previous video
   */
  const playPrevious = useCallback(() => {
    const previousVideo = getPreviousVideo()

    if (previousVideo) {
      if (onNext) {
        onNext(previousVideo.id)
      } else {
        navigate(`/videos/${previousVideo.id}`)
      }
    } else {
      console.log('No previous video in playlist')
    }
  }, [getPreviousVideo, navigate, onNext])

  /**
   * Handle video end event
   */
  const handleVideoEnd = useCallback(() => {
    if (onVideoEnd) {
      onVideoEnd()
    }

    if (enabled) {
      // Wait 3 seconds before auto-playing next video
      const timer = setTimeout(() => {
        playNext()
      }, 3000)

      return () => clearTimeout(timer)
    }
  }, [enabled, onVideoEnd, playNext])

  return {
    playNext,
    playPrevious,
    getNextVideo,
    getPreviousVideo,
    handleVideoEnd,
    hasNext: getNextVideo() !== null,
    hasPrevious: getPreviousVideo() !== null,
  }
}

export default useAutoPlay
