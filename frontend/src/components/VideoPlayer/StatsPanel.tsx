import React, { useEffect, useState } from 'react'
import './StatsPanel.css'

export interface StatsPanelProps {
  visible: boolean
  onClose: () => void
  player: any | null
  videoId?: number
}

const StatsPanel: React.FC<StatsPanelProps> = ({
  visible,
  onClose,
  player,
  videoId,
}) => {
  const [stats, setStats] = useState({
    videoId: videoId || 0,
    resolution: '0x0',
    fps: 0,
    videoBitrate: 0,
    audioBitrate: 0,
    bufferHealth: 100,
    droppedFrames: 0,
    currentTime: 0,
    duration: 0,
    volume: 100,
    playbackRate: 1,
    videoCodec: 'N/A',
    audioCodec: 'N/A',
  })

  useEffect(() => {
    if (!visible || !player) return

    const updateStats = () => {
      const videoElement = player.tech({ IWillNotUseThisInPlugins: true }).el()
      const videoWidth = videoElement.videoWidth || 0
      const videoHeight = videoElement.videoHeight || 0

      // Get quality levels if available
      const qualityLevels = player.qualityLevels?.() || []
      const currentLevel = qualityLevels[qualityLevels.selectedIndex] || {}

      setStats({
        videoId: videoId || 0,
        resolution: `${videoWidth}x${videoHeight}`,
        fps: 30, // Video.js doesn't expose FPS directly, placeholder
        videoBitrate: Math.round((currentLevel.bitrate || 0) / 1000),
        audioBitrate: 128, // Placeholder
        bufferHealth: Math.round((player.bufferedPercent() || 0) * 100),
        droppedFrames: 0, // Placeholder
        currentTime: player.currentTime() || 0,
        duration: player.duration() || 0,
        volume: Math.round((player.volume() || 0) * 100),
        playbackRate: player.playbackRate() || 1,
        videoCodec: currentLevel.codecs || 'H.264',
        audioCodec: 'AAC',
      })
    }

    updateStats()
    const interval = setInterval(updateStats, 1000)

    return () => {
      clearInterval(interval)
    }
  }, [visible, player, videoId])

  if (!visible) return null

  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    const s = Math.floor(seconds % 60)
    if (h > 0) {
      return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
    }
    return `${m}:${s.toString().padStart(2, '0')}`
  }

  return (
    <div className="video-stats-overlay" onClick={(e) => e.stopPropagation()}>
      <div className="stats-panel">
        <div className="stats-header">
          <h4>统计信息</h4>
          <button className="stats-close" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="stats-content">
          <div className="stats-row">
            <span className="stats-label">视频 ID:</span>
            <span className="stats-value">{stats.videoId}</span>
          </div>

          <div className="stats-row">
            <span className="stats-label">分辨率:</span>
            <span className="stats-value">{stats.resolution}</span>
          </div>

          <div className="stats-row">
            <span className="stats-label">帧率:</span>
            <span className="stats-value">{stats.fps} fps</span>
          </div>

          <div className="stats-row">
            <span className="stats-label">视频编码:</span>
            <span className="stats-value">{stats.videoCodec}</span>
          </div>

          <div className="stats-row">
            <span className="stats-label">音频编码:</span>
            <span className="stats-value">{stats.audioCodec}</span>
          </div>

          <div className="stats-row">
            <span className="stats-label">视频码率:</span>
            <span className="stats-value">{stats.videoBitrate} kbps</span>
          </div>

          <div className="stats-row">
            <span className="stats-label">音频码率:</span>
            <span className="stats-value">{stats.audioBitrate} kbps</span>
          </div>

          <div className="stats-row">
            <span className="stats-label">缓冲健康度:</span>
            <span className="stats-value">{stats.bufferHealth}%</span>
          </div>

          <div className="stats-row">
            <span className="stats-label">已播放:</span>
            <span className="stats-value">{formatTime(stats.currentTime)}</span>
          </div>

          <div className="stats-row">
            <span className="stats-label">总时长:</span>
            <span className="stats-value">{formatTime(stats.duration)}</span>
          </div>

          <div className="stats-row">
            <span className="stats-label">音量:</span>
            <span className="stats-value">{stats.volume}%</span>
          </div>

          <div className="stats-row">
            <span className="stats-label">播放速度:</span>
            <span className="stats-value">{stats.playbackRate}x</span>
          </div>

          <div className="stats-row">
            <span className="stats-label">丢帧:</span>
            <span className="stats-value">{stats.droppedFrames}</span>
          </div>
        </div>

        <div className="stats-footer">
          <small>* 类似 YouTube 的 "Stats for nerds"</small>
        </div>
      </div>
    </div>
  )
}

export default StatsPanel
