import React, { useEffect, useRef } from 'react'
import videojs from 'video.js'
import 'video.js/dist/video-js.css'
import './VideoPlayer.css'

interface VideoPlayerProps {
  src: string
  poster?: string
  onTimeUpdate?: (currentTime: number) => void
  onEnded?: () => void
  initialTime?: number
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({
  src,
  poster,
  onTimeUpdate,
  onEnded,
  initialTime = 0,
}) => {
  const videoRef = useRef<HTMLDivElement>(null)
  const playerRef = useRef<any>(null)

  useEffect(() => {
    // Initialize Video.js player
    if (!playerRef.current && videoRef.current) {
      const videoElement = document.createElement('video-js')
      videoElement.classList.add('vjs-big-play-centered')
      videoRef.current.appendChild(videoElement)

      const player = (playerRef.current = videojs(videoElement, {
        controls: true,
        autoplay: false,
        preload: 'auto',
        fluid: true,
        poster: poster,
        playbackRates: [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2],
        controlBar: {
          children: [
            'playToggle',
            'volumePanel',
            'currentTimeDisplay',
            'timeDivider',
            'durationDisplay',
            'progressControl',
            'remainingTimeDisplay',
            'playbackRateMenuButton',
            'chaptersButton',
            'descriptionsButton',
            'subsCapsButton',
            'audioTrackButton',
            'pictureInPictureToggle',
            'fullscreenToggle',
          ],
        },
      }))

      player.src(src)

      // Set initial time
      if (initialTime > 0) {
        player.currentTime(initialTime)
      }

      // Keyboard shortcuts (YouTube-like)
      player.on('keydown', (e: KeyboardEvent) => {
        switch (e.key) {
          case ' ':
          case 'k':
            e.preventDefault()
            if (player.paused()) {
              player.play()
            } else {
              player.pause()
            }
            break
          case 'ArrowLeft':
            e.preventDefault()
            player.currentTime((player.currentTime() || 0) - 5)
            break
          case 'ArrowRight':
            e.preventDefault()
            player.currentTime((player.currentTime() || 0) + 5)
            break
          case 'ArrowUp':
            e.preventDefault()
            player.volume(Math.min(1, (player.volume() || 0) + 0.1))
            break
          case 'ArrowDown':
            e.preventDefault()
            player.volume(Math.max(0, (player.volume() || 0) - 0.1))
            break
          case 'f':
            e.preventDefault()
            if (player.isFullscreen()) {
              player.exitFullscreen()
            } else {
              player.requestFullscreen()
            }
            break
          case 'm':
            e.preventDefault()
            player.muted(!player.muted())
            break
          case '0':
          case '1':
          case '2':
          case '3':
          case '4':
          case '5':
          case '6':
          case '7':
          case '8':
          case '9':
            e.preventDefault()
            const percent = parseInt(e.key) * 10
            player.currentTime(((player.duration() || 0) * percent) / 100)
            break
        }
      })

      // Time update
      player.on('timeupdate', () => {
        if (onTimeUpdate) {
          onTimeUpdate(player.currentTime() || 0)
        }
      })

      // Video ended
      player.on('ended', () => {
        if (onEnded) {
          onEnded()
        }
      })

      // Fullscreen change tracking
      player.on('fullscreenchange', () => {
        // Track fullscreen state changes if needed
        const isFullscreen = player.isFullscreen() || false
        console.log('Fullscreen:', isFullscreen)
      })

      // Quality selector (if multiple sources)
      // player.qualityLevels() // Requires videojs-contrib-quality-levels

      // Add custom controls
      const Button = videojs.getComponent('Button')

      // Theater mode button
      class TheaterButton extends Button {
        constructor(player: any, options: any) {
          super(player, options)
          // @ts-ignore - videojs Button type is incomplete
          this.controlText('Theater Mode')
        }

        handleClick() {
          // Toggle theater mode
          const playerEl = this.player().el()
          playerEl.classList.toggle('vjs-theater-mode')
        }
      }

      videojs.registerComponent('TheaterButton', TheaterButton)
    } else {
      // Update source if it changes
      const player = playerRef.current
      if (player) {
        player.src(src)
        if (poster) {
          player.poster(poster)
        }
      }
    }
  }, [src, poster])

  useEffect(() => {
    const player = playerRef.current

    return () => {
      if (player && !player.isDisposed()) {
        player.dispose()
        playerRef.current = null
      }
    }
  }, [])

  return (
    <div className="video-player-wrapper">
      <div ref={videoRef} className="video-player" />

      {/* Keyboard shortcuts hint */}
      <div className="keyboard-shortcuts-hint text-xs text-gray-400 mt-2">
        <p>Keyboard shortcuts: Space/K = Play/Pause | ← → = Seek | ↑ ↓ = Volume | F = Fullscreen | M = Mute | 0-9 = Jump to %</p>
      </div>
    </div>
  )
}

export default VideoPlayer
