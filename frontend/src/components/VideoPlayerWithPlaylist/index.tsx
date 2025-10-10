/**
 * Video Player with Playlist Component
 * Combines VideoPlayer with PlaylistSidebar for continuous playback
 */
import React, { useState } from 'react'
import VideoPlayer from '../VideoPlayer'
import PlaylistSidebar, { PlaylistVideo } from '../PlaylistSidebar'
import { useAutoPlay } from '../../hooks/useAutoPlay'
import './styles.css'

interface VideoPlayerWithPlaylistProps {
  /**
   * Current video source URL
   */
  src: string

  /**
   * Current video ID
   */
  videoId: number

  /**
   * Video poster/thumbnail
   */
  poster?: string

  /**
   * Playlist of related videos
   */
  playlist: PlaylistVideo[]

  /**
   * Playlist title
   */
  playlistTitle?: string

  /**
   * Whether autoplay is enabled
   */
  autoPlayEnabled?: boolean

  /**
   * Initial playback position (seconds)
   */
  initialTime?: number

  /**
   * Whether to auto-save watch progress
   */
  autoSaveProgress?: boolean

  /**
   * Whether to enable subtitles
   */
  enableSubtitles?: boolean

  /**
   * Callback when video selection changes
   */
  onVideoChange?: (videoId: number) => void
}

const VideoPlayerWithPlaylist: React.FC<VideoPlayerWithPlaylistProps> = ({
  src,
  videoId,
  poster,
  playlist,
  playlistTitle = 'Related Videos',
  autoPlayEnabled = true,
  initialTime,
  autoSaveProgress = true,
  enableSubtitles = true,
  onVideoChange,
}) => {
  const [isAutoPlayEnabled, setIsAutoPlayEnabled] = useState(autoPlayEnabled)

  const { handleVideoEnd, playNext, playPrevious, hasNext, hasPrevious } = useAutoPlay({
    currentVideoId: videoId,
    playlist,
    enabled: isAutoPlayEnabled,
    onNext: onVideoChange,
  })

  return (
    <div className="video-player-with-playlist">
      {/* Main Video Player */}
      <div className="video-player-container">
        <VideoPlayer
          src={src}
          poster={poster}
          videoId={videoId}
          initialTime={initialTime}
          autoSaveProgress={autoSaveProgress}
          enableSubtitles={enableSubtitles}
          onEnded={handleVideoEnd}
        />

        {/* Navigation Controls */}
        <div className="video-nav-controls">
          <button
            className="nav-button prev"
            onClick={playPrevious}
            disabled={!hasPrevious}
            title="Previous Video"
          >
            <svg
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Previous
          </button>

          <button
            className="nav-button next"
            onClick={playNext}
            disabled={!hasNext}
            title="Next Video"
          >
            Next
            <svg
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Playlist Sidebar */}
      <div className="playlist-container">
        <PlaylistSidebar
          currentVideoId={videoId}
          videos={playlist}
          title={playlistTitle}
          autoPlayEnabled={isAutoPlayEnabled}
          onVideoSelect={onVideoChange}
        />
      </div>
    </div>
  )
}

export default VideoPlayerWithPlaylist
