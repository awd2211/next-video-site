import React, { useEffect, useRef, useState } from 'react'
import videojs from 'video.js'
import 'video.js/dist/video-js.css'
import './VideoPlayer.css'
import { historyService } from '../../services/historyService'
import subtitleService, { Subtitle } from '../../services/subtitleService'

interface VideoPlayerProps {
  src: string
  poster?: string
  videoId?: number // 🆕 用于保存观看进度和加载字幕
  onTimeUpdate?: (currentTime: number) => void
  onEnded?: () => void
  initialTime?: number
  autoSaveProgress?: boolean // 🆕 是否自动保存进度 (默认true)
  enableSubtitles?: boolean // 🆕 是否启用字幕加载 (默认true)
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({
  src,
  poster,
  videoId,
  onTimeUpdate,
  onEnded,
  initialTime = 0,
  autoSaveProgress = true,
  enableSubtitles = true,
}) => {
  const videoRef = useRef<HTMLDivElement>(null)
  const playerRef = useRef<any>(null)
  const [lastSavedTime, setLastSavedTime] = useState(0)
  const [subtitles, setSubtitles] = useState<Subtitle[]>([])
  const progressSaveIntervalRef = useRef<NodeJS.Timeout | null>(null)

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
          case 'c':
            e.preventDefault()
            // 切换字幕显示
            const tracks = player.textTracks()
            let subtitleTrack = null
            for (let i = 0; i < tracks.length; i++) {
              if (tracks[i].kind === 'subtitles') {
                subtitleTrack = tracks[i]
                break
              }
            }
            if (subtitleTrack) {
              subtitleTrack.mode = subtitleTrack.mode === 'showing' ? 'hidden' : 'showing'
            }
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
        // 🆕 视频播放结束时保存进度(标记为已完成)
        if (videoId && autoSaveProgress) {
          const duration = player.duration() || 0
          historyService.updateProgress(videoId, duration, duration, true).catch(err => {
            console.error('保存完成状态失败:', err)
          })
        }

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

  // 🆕 自动保存播放进度 (每10秒)
  useEffect(() => {
    if (!videoId || !autoSaveProgress || !playerRef.current) {
      return
    }

    const player = playerRef.current

    const saveProgress = async () => {
      if (!player || player.paused()) {
        return // 暂停时不保存
      }

      const currentTime = Math.floor(player.currentTime() || 0)
      const duration = Math.floor(player.duration() || 0)

      // 至少播放了5秒才保存
      if (currentTime < 5) {
        return
      }

      // 避免频繁保存相同位置
      if (Math.abs(currentTime - lastSavedTime) < 5) {
        return
      }

      try {
        await historyService.updateProgress(videoId, currentTime, duration)
        setLastSavedTime(currentTime)
        console.log(`✅ 进度已保存: ${currentTime}s / ${duration}s`)
      } catch (error) {
        console.error('保存进度失败:', error)
      }
    }

    // 每10秒保存一次进度
    progressSaveIntervalRef.current = setInterval(saveProgress, 10000)

    // 播放开始时立即保存一次
    const handlePlay = () => {
      saveProgress()
    }

    player.on('play', handlePlay)

    return () => {
      if (progressSaveIntervalRef.current) {
        clearInterval(progressSaveIntervalRef.current)
      }
      if (player && !player.isDisposed()) {
        player.off('play', handlePlay)
      }
    }
  }, [videoId, autoSaveProgress, lastSavedTime])

  // 🆕 加载字幕
  useEffect(() => {
    if (!videoId || !enableSubtitles || !playerRef.current) {
      return
    }

    const loadSubtitles = async () => {
      try {
        const response = await subtitleService.getVideoSubtitles(videoId)
        const subtitleList = response.subtitles

        if (subtitleList.length === 0) {
          console.log('该视频没有字幕')
          return
        }

        setSubtitles(subtitleList)

        const player = playerRef.current
        if (!player) return

        // 添加字幕轨道
        subtitleList.forEach((subtitle, index) => {
          // 转换格式: SRT → VTT (Video.js只支持VTT)
          const subtitleUrl = subtitle.file_url.endsWith('.srt')
            ? convertSrtToVtt(subtitle.file_url)
            : subtitle.file_url

          player.addRemoteTextTrack(
            {
              kind: 'subtitles',
              src: subtitleUrl,
              srclang: subtitle.language,
              label: subtitle.language_name,
              default: subtitle.is_default,
            },
            false // 不自动添加到DOM
          )

          console.log(
            `✅ 字幕已加载: ${subtitle.language_name} (${subtitle.language})`
          )
        })

        // 如果有默认字幕,启用字幕显示
        const hasDefault = subtitleList.some(s => s.is_default)
        if (hasDefault) {
          // 自动显示字幕
          const tracks = player.textTracks()
          for (let i = 0; i < tracks.length; i++) {
            const track = tracks[i]
            if (track.kind === 'subtitles' && track.default) {
              track.mode = 'showing'
            }
          }
        }
      } catch (error) {
        console.error('加载字幕失败:', error)
      }
    }

    loadSubtitles()
  }, [videoId, enableSubtitles])

  // 辅助函数: SRT转VTT URL (如果需要)
  const convertSrtToVtt = (srtUrl: string): string => {
    // 如果后端支持自动转换,直接替换扩展名
    // 否则需要客户端转换或后端提供转换API
    return srtUrl.replace('.srt', '.vtt')
  }

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
        <p>Keyboard shortcuts: Space/K = Play/Pause | ← → = Seek | ↑ ↓ = Volume | F = Fullscreen | M = Mute | 0-9 = Jump to % | C = Toggle Subtitles</p>
      </div>

      {/* Subtitle info */}
      {subtitles.length > 0 && (
        <div className="subtitle-info text-xs text-gray-500 mt-1">
          <p>Available subtitles: {subtitles.map(s => s.language_name).join(', ')}</p>
        </div>
      )}
    </div>
  )
}

export default VideoPlayer
