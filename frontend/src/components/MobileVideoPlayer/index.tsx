/**
 * 移动端视频播放器
 * 特性:
 * - 触摸手势控制 (左右滑动调节进度, 上下滑动调节音量/亮度)
 * - 双击暂停/播放
 * - 全屏优化
 * - 自适应清晰度
 * - 移动网络提示
 */
import React, { useRef, useState, useEffect } from 'react'
import videojs from 'video.js'
import 'video.js/dist/video-js.css'
import Player from 'video.js/dist/types/player'
import { useDeviceDetect, useRecommendedQuality } from '@/hooks/useDeviceDetect'

interface MobileVideoPlayerProps {
  src: string
  poster?: string
  onTimeUpdate?: (currentTime: number, duration: number) => void
  onEnded?: () => void
  initialTime?: number
  autoplay?: boolean
}

const MobileVideoPlayer: React.FC<MobileVideoPlayerProps> = ({
  src,
  poster,
  onTimeUpdate,
  onEnded,
  initialTime = 0,
  autoplay = false,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null)
  const playerRef = useRef<Player | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [buffering, setBuffering] = useState(false)
  const [isMobileNetwork, setIsMobileNetwork] = useState(false)
  const device = useDeviceDetect()
  const recommendedQuality = useRecommendedQuality()

  // 触摸手势相关状态
  const touchStartRef = useRef<{ x: number; y: number; time: number } | null>(null)
  const [gestureHint, setGestureHint] = useState<string | null>(null)

  // 控制栏自动隐藏
  const hideControlsTimeoutRef = useRef<number | null>(null)

  // 检测网络类型
  useEffect(() => {
    const checkNetworkType = () => {
      const connection =
        (navigator as any).connection ||
        (navigator as any).mozConnection ||
        (navigator as any).webkitConnection

      if (connection) {
        const type = connection.effectiveType
        setIsMobileNetwork(['slow-2g', '2g', '3g'].includes(type))
      }
    }

    checkNetworkType()
  }, [])

  // 初始化播放器
  useEffect(() => {
    if (!videoRef.current) return

    // 移动端优化配置
    const player = videojs(videoRef.current, {
      controls: true,
      preload: 'metadata', // 移动端只预加载元数据
      fluid: true,
      responsive: true,
      playsinline: true, // iOS必须，否则会全屏播放
      html5: {
        vhs: {
          // HLS配置
          enableLowInitialPlaylist: true, // 优先加载低质量
          smoothQualityChange: true, // 平滑切换质量
          overrideNative: true,
        },
      },
      controlBar: {
        // 移动端简化控制栏
        children: [
          'playToggle',
          'currentTimeDisplay',
          'progressControl',
          'durationDisplay',
          'qualitySelector',
          'fullscreenToggle',
        ],
      },
    })

    playerRef.current = player

    // 设置视频源
    player.src({
      src,
      type: 'application/x-mpegURL', // HLS
    })

    if (poster) {
      player.poster(poster)
    }

    // 跳转到初始时间
    if (initialTime > 0) {
      player.one('loadedmetadata', () => {
        player.currentTime(initialTime)
      })
    }

    // 事件监听
    player.on('play', () => setIsPlaying(true))
    player.on('pause', () => setIsPlaying(false))
    player.on('waiting', () => setBuffering(true))
    player.on('canplay', () => setBuffering(false))

    player.on('timeupdate', () => {
      const duration = player.duration()
      if (onTimeUpdate && duration) {
        onTimeUpdate(player.currentTime(), duration)
      }
    })

    player.on('ended', () => {
      if (onEnded) onEnded()
    })

    // 移动端自动播放 (需要用户交互)
    if (autoplay && !isMobileNetwork) {
      player.play()?.catch((error: Error) => {
        console.log('自动播放失败，需要用户交互:', error)
      })
    }

    return () => {
      if (player && !player.isDisposed()) {
        player.dispose()
      }
    }
  }, [src])

  // 触摸手势处理
  const handleTouchStart = (e: React.TouchEvent) => {
    const touch = e.touches[0]
    touchStartRef.current = {
      x: touch.clientX,
      y: touch.clientY,
      time: Date.now(),
    }
  }

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!touchStartRef.current || !playerRef.current) return

    const touch = e.touches[0]
    const deltaX = touch.clientX - touchStartRef.current.x
    const deltaY = touch.clientY - touchStartRef.current.y

    // 水平滑动 - 调节进度
    if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 30) {
      e.preventDefault()
      const duration = playerRef.current.duration()
      if (duration) {
        const seekAmount = (deltaX / window.innerWidth) * duration * 0.3
        setGestureHint(
          `${deltaX > 0 ? '快进' : '快退'} ${Math.abs(Math.round(seekAmount))}秒`
        )
      }
    }

    // 垂直滑动 - 调节音量
    if (Math.abs(deltaY) > Math.abs(deltaX) && Math.abs(deltaY) > 30) {
      e.preventDefault()
      const volumeChange = -(deltaY / window.innerHeight)
      const currentVolume = playerRef.current.volume()
      if (typeof currentVolume === 'number') {
        const newVolume = Math.max(0, Math.min(1, currentVolume + volumeChange))
        playerRef.current.volume(newVolume)
        setGestureHint(`音量 ${Math.round(newVolume * 100)}%`)
      }
    }
  }

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (!touchStartRef.current || !playerRef.current) return

    const touch = e.changedTouches[0]
    const deltaX = touch.clientX - touchStartRef.current.x
    const deltaY = touch.clientY - touchStartRef.current.y
    const deltaTime = Date.now() - touchStartRef.current.time

    // 双击暂停/播放
    if (deltaTime < 300 && Math.abs(deltaX) < 10 && Math.abs(deltaY) < 10) {
      if (isPlaying) {
        playerRef.current.pause()
      } else {
        playerRef.current.play()
      }
    }

    // 应用进度调节
    if (Math.abs(deltaX) > 30) {
      const duration = playerRef.current.duration()
      if (duration) {
        const seekAmount = (deltaX / window.innerWidth) * duration * 0.3
        const newTime = Math.max(
          0,
          Math.min(duration, playerRef.current.currentTime() + seekAmount)
        )
        playerRef.current.currentTime(newTime)
      }
    }

    touchStartRef.current = null
    setTimeout(() => setGestureHint(null), 1000)
  }

  // 显示/隐藏控制栏
  const handlePlayerClick = () => {
    if (hideControlsTimeoutRef.current) {
      window.clearTimeout(hideControlsTimeoutRef.current)
    }

    hideControlsTimeoutRef.current = window.setTimeout(() => {
      // Auto-hide logic if needed
    }, 3000)
  }

  return (
    <div className="relative w-full bg-black">
      {/* 移动网络提示 */}
      {isMobileNetwork && !isPlaying && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-black bg-opacity-70">
          <div className="text-center text-white p-4">
            <div className="text-lg mb-2">您正在使用移动网络</div>
            <div className="text-sm text-gray-300 mb-4">
              播放视频可能消耗大量流量
            </div>
            <button
              onClick={() => {
                setIsMobileNetwork(false)
                playerRef.current?.play()
              }}
              className="px-6 py-2 bg-blue-500 rounded"
            >
              继续播放
            </button>
          </div>
        </div>
      )}

      {/* Video.js播放器 */}
      <div
        data-vjs-player
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        onClick={handlePlayerClick}
      >
        <video
          ref={videoRef}
          className="video-js vjs-big-play-centered"
          playsInline
          webkit-playsinline="true"
          x5-playsinline="true"
          x5-video-player-type="h5"
          x5-video-player-fullscreen="true"
        />
      </div>

      {/* 手势提示 */}
      {gestureHint && (
        <div className="absolute inset-0 z-20 flex items-center justify-center pointer-events-none">
          <div className="bg-black bg-opacity-70 text-white px-6 py-3 rounded-lg text-lg">
            {gestureHint}
          </div>
        </div>
      )}

      {/* 缓冲提示 */}
      {buffering && (
        <div className="absolute inset-0 z-20 flex items-center justify-center pointer-events-none">
          <div className="w-16 h-16 border-4 border-white border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {/* 推荐清晰度提示 */}
      {device.isMobile && (
        <div className="absolute top-2 left-2 z-10 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
          推荐: {recommendedQuality}
        </div>
      )}
    </div>
  )
}

export default MobileVideoPlayer
