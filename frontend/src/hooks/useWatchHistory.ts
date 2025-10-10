import { useEffect, useRef, useCallback } from 'react'
import { historyService } from '../services/historyService'

interface UseWatchHistoryProps {
  videoId: number
  duration: number // Video duration in minutes
  enabled?: boolean
}

export const useWatchHistory = ({ videoId, duration, enabled = true }: UseWatchHistoryProps) => {
  const playerRef = useRef<any>(null)
  const watchStartTime = useRef<number>(Date.now())
  const lastSaveTime = useRef<number>(0)
  const saveIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Load previous watch position
  const loadWatchPosition = useCallback(async () => {
    if (!enabled) return null

    try {
      const history = await historyService.getVideoHistory(videoId)
      return history
    } catch (error) {
      console.error('Failed to load watch history:', error)
      return null
    }
  }, [videoId, enabled])

  // Save watch progress
  const saveWatchProgress = useCallback(async (currentTime: number, isCompleted: boolean = false) => {
    if (!enabled) return

    const now = Date.now()
    const watchDuration = Math.floor((now - watchStartTime.current) / 1000)

    try {
      await historyService.recordHistory(
        videoId,
        watchDuration,
        Math.floor(currentTime),
        isCompleted
      )
      lastSaveTime.current = now
    } catch (error) {
      console.error('Failed to save watch history:', error)
    }
  }, [videoId, enabled])

  // Auto-save progress every 30 seconds
  useEffect(() => {
    if (!enabled || !playerRef.current) return

    saveIntervalRef.current = setInterval(() => {
      if (playerRef.current && typeof playerRef.current.getCurrentTime === 'function') {
        const currentTime = playerRef.current.getCurrentTime()
        const videoDurationSeconds = duration * 60
        const isCompleted = currentTime >= videoDurationSeconds * 0.95 // Consider 95% as completed

        saveWatchProgress(currentTime, isCompleted)
      }
    }, 30000) // Save every 30 seconds

    return () => {
      if (saveIntervalRef.current) {
        clearInterval(saveIntervalRef.current)
      }
    }
  }, [enabled, duration, saveWatchProgress])

  // Save on unmount
  useEffect(() => {
    return () => {
      if (enabled && playerRef.current && typeof playerRef.current.getCurrentTime === 'function') {
        const currentTime = playerRef.current.getCurrentTime()
        const videoDurationSeconds = duration * 60
        const isCompleted = currentTime >= videoDurationSeconds * 0.95

        // Save one last time when component unmounts
        saveWatchProgress(currentTime, isCompleted)
      }
    }
  }, [enabled, duration, saveWatchProgress])

  // Return methods for manual control
  return {
    setPlayerRef: (ref: any) => {
      playerRef.current = ref
    },
    loadWatchPosition,
    saveWatchProgress,
    resumeFromLastPosition: async () => {
      const history = await loadWatchPosition()
      if (history && history.last_position > 0 && !history.is_completed) {
        return history.last_position
      }
      return 0
    }
  }
}
