/**
 * Playlist Sidebar Component
 * Displays related videos for continuous playback
 */
import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './styles.css'

export interface PlaylistVideo {
  id: number
  title: string
  poster_url: string
  duration: number
  view_count: number
}

interface PlaylistSidebarProps {
  currentVideoId: number
  videos: PlaylistVideo[]
  title?: string
  autoPlayEnabled?: boolean
  onVideoSelect?: (videoId: number) => void
}

const PlaylistSidebar: React.FC<PlaylistSidebarProps> = ({
  currentVideoId,
  videos,
  title = 'Up Next',
  autoPlayEnabled = true,
  onVideoSelect,
}) => {
  const navigate = useNavigate()
  const [currentIndex, setCurrentIndex] = useState(0)

  // Find current video index
  useEffect(() => {
    const index = videos.findIndex((v) => v.id === currentVideoId)
    if (index !== -1) {
      setCurrentIndex(index)
    }
  }, [currentVideoId, videos])

  const handleVideoClick = (video: PlaylistVideo) => {
    if (onVideoSelect) {
      onVideoSelect(video.id)
    } else {
      navigate(`/videos/${video.id}`)
    }
  }

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const formatViewCount = (count: number): string => {
    if (count >= 1000000) {
      return `${(count / 1000000).toFixed(1)}M views`
    } else if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}K views`
    }
    return `${count} views`
  }

  return (
    <div className="playlist-sidebar">
      <div className="playlist-header">
        <h3 className="playlist-title">{title}</h3>
        <div className="playlist-info">
          {videos.length > 0 && (
            <span className="playlist-count">
              {currentIndex + 1} / {videos.length}
            </span>
          )}
        </div>
      </div>

      {autoPlayEnabled && (
        <div className="playlist-autoplay">
          <label className="autoplay-toggle">
            <input type="checkbox" checked={autoPlayEnabled} readOnly />
            <span>Autoplay</span>
          </label>
        </div>
      )}

      <div className="playlist-videos">
        {videos.map((video, index) => (
          <div
            key={video.id}
            className={`playlist-video-item ${video.id === currentVideoId ? 'active' : ''} ${
              index < currentIndex ? 'watched' : ''
            }`}
            onClick={() => handleVideoClick(video)}
          >
            {/* Thumbnail */}
            <div className="playlist-video-thumbnail">
              <img src={video.poster_url} alt={video.title} loading="lazy" />
              <div className="playlist-video-duration">{formatDuration(video.duration)}</div>
              {index === currentIndex && (
                <div className="playlist-video-badge">Now Playing</div>
              )}
            </div>

            {/* Info */}
            <div className="playlist-video-info">
              <h4 className="playlist-video-title">{video.title}</h4>
              <p className="playlist-video-meta">{formatViewCount(video.view_count)}</p>
            </div>

            {/* Index */}
            <div className="playlist-video-index">{index + 1}</div>
          </div>
        ))}

        {videos.length === 0 && (
          <div className="playlist-empty">
            <p>No related videos</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default PlaylistSidebar
