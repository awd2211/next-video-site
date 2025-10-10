/**
 * 带弹幕的视频播放器
 */
import React, { useState, useEffect, useCallback, useRef } from 'react'
import VideoPlayer from '../VideoPlayer'
import DanmakuRenderer from '../DanmakuRenderer'
import DanmakuInput from '../DanmakuInput'
import DanmakuSettings, { DanmakuConfig } from '../DanmakuSettings'
import { danmakuService, Danmaku } from '../../services/danmakuService'
import './styles.css'

interface VideoPlayerWithDanmakuProps {
  src: string
  poster?: string
  videoId: number
  onTimeUpdate?: (currentTime: number) => void
  onEnded?: () => void
  initialTime?: number
  autoSaveProgress?: boolean
  enableSubtitles?: boolean
}

const DEFAULT_CONFIG: DanmakuConfig = {
  enabled: true,
  opacity: 0.8,
  speed: 1,
  fontSize: 1,
  density: 0.6,
}

const VideoPlayerWithDanmakuPlayer: React.FC<VideoPlayerWithDanmakuProps> = ({
  src,
  poster,
  videoId,
  onTimeUpdate,
  onEnded,
  initialTime,
  autoSaveProgress,
  enableSubtitles,
}) => {
  const [danmakuList, setDanmakuList] = useState<Danmaku[]>([])
  const [currentTime, setCurrentTime] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [containerSize, setContainerSize] = useState({ width: 0, height: 0 })
  const containerRef = useRef<HTMLDivElement>(null)

  // 从localStorage加载配置
  const [config, setConfig] = useState<DanmakuConfig>(() => {
    try {
      const saved = localStorage.getItem('danmaku_config')
      return saved ? JSON.parse(saved) : DEFAULT_CONFIG
    } catch {
      return DEFAULT_CONFIG
    }
  })

  // 保存配置到localStorage
  useEffect(() => {
    localStorage.setItem('danmaku_config', JSON.stringify(config))
  }, [config])

  // 加载弹幕
  useEffect(() => {
    if (!videoId) return

    const loadDanmaku = async () => {
      try {
        const response = await danmakuService.getVideoDanmaku(videoId)
        setDanmakuList(response.items)
      } catch (error) {
        console.error('加载弹幕失败:', error)
      }
    }

    loadDanmaku()
  }, [videoId])

  // 监听容器尺寸变化
  useEffect(() => {
    if (!containerRef.current) return

    const updateSize = () => {
      if (containerRef.current) {
        const { width, height } = containerRef.current.getBoundingClientRect()
        setContainerSize({ width, height })
      }
    }

    updateSize()

    const resizeObserver = new ResizeObserver(updateSize)
    resizeObserver.observe(containerRef.current)

    return () => {
      resizeObserver.disconnect()
    }
  }, [])

  // 监听播放状态
  useEffect(() => {
    const videoElement = containerRef.current?.querySelector('video')
    if (!videoElement) return

    const handlePlay = () => setIsPlaying(true)
    const handlePause = () => setIsPlaying(false)

    videoElement.addEventListener('play', handlePlay)
    videoElement.addEventListener('pause', handlePause)

    return () => {
      videoElement.removeEventListener('play', handlePlay)
      videoElement.removeEventListener('pause', handlePause)
    }
  }, [])

  const handleTimeUpdate = (time: number) => {
    setCurrentTime(time)
    if (onTimeUpdate) {
      onTimeUpdate(time)
    }
  }

  const handleDanmakuSent = async () => {
    // 重新加载弹幕列表
    try {
      const response = await danmakuService.getVideoDanmaku(videoId)
      setDanmakuList(response.items)
    } catch (error) {
      console.error('刷新弹幕失败:', error)
    }
  }

  return (
    <div className="video-player-with-danmaku" ref={containerRef}>
      <VideoPlayer
        src={src}
        poster={poster}
        videoId={videoId}
        onTimeUpdate={handleTimeUpdate}
        onEnded={onEnded}
        initialTime={initialTime}
        autoSaveProgress={autoSaveProgress}
        enableSubtitles={enableSubtitles}
      />

      {/* 弹幕渲染层 */}
      {containerSize.width > 0 && (
        <DanmakuRenderer
          danmakuList={danmakuList}
          currentTime={currentTime}
          isPlaying={isPlaying}
          enabled={config.enabled}
          opacity={config.opacity}
          speed={config.speed}
          fontSize={config.fontSize}
          density={config.density}
          containerWidth={containerSize.width}
          containerHeight={containerSize.height}
        />
      )}

      {/* 弹幕控制栏 */}
      <div className="danmaku-controls">
        <DanmakuInput
          videoId={videoId}
          currentTime={currentTime}
          onSent={handleDanmakuSent}
        />

        <button
          className="btn-danmaku-settings"
          onClick={() => setShowSettings(true)}
          title="弹幕设置"
        >
          ⚙️ 设置
        </button>
      </div>

      {/* 弹幕设置面板 */}
      {showSettings && (
        <DanmakuSettings
          config={config}
          onChange={setConfig}
          onClose={() => setShowSettings(false)}
        />
      )}
    </div>
  )
}

export default VideoPlayerWithDanmakuPlayer
