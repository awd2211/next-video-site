import React, { useEffect, useRef, useState, useCallback } from 'react'
import videojs from 'video.js'
import toast from 'react-hot-toast'
import 'video.js/dist/video-js.css'
import './VideoPlayer.css'
import './VideoPlayer-YouTube.css'
import { historyService } from '../../services/historyService'
import subtitleService, { Subtitle } from '../../services/subtitleService'
import '../../utils/videojs-plugins' // Import plugins (they auto-register)
import ContextMenu from './ContextMenu'
import StatsPanel from './StatsPanel'
import SeekFeedback from './SeekFeedback'
import VolumeIndicator from './VolumeIndicator'
import KeyboardShortcuts from './KeyboardShortcuts'
import PlaybackRateIndicator from './PlaybackRateIndicator'

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

  // YouTube-style features state
  const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0 })
  const [showStats, setShowStats] = useState(false)
  const [loopEnabled, setLoopEnabled] = useState(false)
  const [theaterMode, setTheaterMode] = useState(false)
  const [miniPlayer, setMiniPlayer] = useState(false)
  const [showKeyboardHelp, setShowKeyboardHelp] = useState(false)
  const [seekFeedback, setSeekFeedback] = useState({
    show: false,
    direction: 'forward' as 'forward' | 'backward',
    seconds: 10,
    position: 'center' as 'left' | 'center' | 'right',
  })
  const [volumeIndicator, setVolumeIndicator] = useState({
    show: false,
    volume: 100,
    muted: false,
  })
  const [playbackRate, setPlaybackRate] = useState(1)
  const [showPlaybackRateIndicator, setShowPlaybackRateIndicator] = useState(false)
  const controlBarTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const lastClickTimeRef = useRef<number>(0)
  const clickCountRef = useRef<number>(0)

  useEffect(() => {
    // Initialize Video.js player
    if (!playerRef.current && videoRef.current) {
      const videoElement = document.createElement('video-js')
      videoElement.classList.add('vjs-big-play-centered')
      videoElement.classList.add('vjs-youtube-skin') // YouTube styling
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
            // YouTube 布局: 左侧控制
            'playToggle',
            'volumePanel',
            'currentTimeDisplay',
            'timeDivider',
            'durationDisplay',

            // 中间: 占位符 (进度条已经在上方绝对定位)
            'progressControl',

            // YouTube 布局: 右侧控制
            'subsCapsButton',          // 字幕按钮
            'qualitySelector',         // 画质选择器 (自定义)
            'playbackRateMenuButton',  // 播放速度
            'theaterButton',           // 影院模式 (自定义)
            'pictureInPictureToggle',  // 画中画
            'fullscreenToggle',        // 全屏
          ],
        },
      }))

      player.src(src)

      // 🆕 Initialize HLS Quality Selector Plugin
      // Use setTimeout to ensure plugin is fully registered before calling
      setTimeout(() => {
        const currentPlayer = playerRef.current
        if (currentPlayer && typeof currentPlayer.hlsQualitySelector === 'function') {
          try {
            currentPlayer.hlsQualitySelector({
              displayCurrentQuality: true, // Display current quality in the button
            })
          } catch (error) {
            console.warn('HLS Quality Selector initialization failed:', error)
          }
        }
      }, 0)

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
          case 'j':
            // 快退10秒
            e.preventDefault()
            player.currentTime((player.currentTime() || 0) - 10)
            setSeekFeedback({ show: true, direction: 'backward', seconds: 10, position: 'left' })
            break
          case 'l':
            // 快进10秒
            e.preventDefault()
            player.currentTime((player.currentTime() || 0) + 10)
            setSeekFeedback({ show: true, direction: 'forward', seconds: 10, position: 'right' })
            break
          case 'ArrowLeft':
            e.preventDefault()
            player.currentTime((player.currentTime() || 0) - 5)
            setSeekFeedback({ show: true, direction: 'backward', seconds: 5, position: 'left' })
            break
          case 'ArrowRight':
            e.preventDefault()
            player.currentTime((player.currentTime() || 0) + 5)
            setSeekFeedback({ show: true, direction: 'forward', seconds: 5, position: 'right' })
            break
          case 'ArrowUp':
            e.preventDefault()
            const newVolumeUp = Math.min(1, (player.volume() || 0) + 0.1)
            player.volume(newVolumeUp)
            setVolumeIndicator({ show: true, volume: newVolumeUp * 100, muted: player.muted() })
            break
          case 'ArrowDown':
            e.preventDefault()
            const newVolumeDown = Math.max(0, (player.volume() || 0) - 0.1)
            player.volume(newVolumeDown)
            setVolumeIndicator({ show: true, volume: newVolumeDown * 100, muted: player.muted() })
            break
          case 'f':
            e.preventDefault()
            if (player.isFullscreen()) {
              player.exitFullscreen()
            } else {
              player.requestFullscreen()
            }
            break
          case 't':
            // 剧场模式
            e.preventDefault()
            handleToggleTheaterMode()
            break
          case 'i':
            // 迷你播放器
            e.preventDefault()
            handleToggleMiniPlayer()
            break
          case 'm':
            e.preventDefault()
            const wasMuted = player.muted()
            player.muted(!wasMuted)
            setVolumeIndicator({ 
              show: true, 
              volume: (player.volume() || 0) * 100, 
              muted: !wasMuted 
            })
            break
          case ',':
            // 逐帧后退（暂停时）
            if (player.paused()) {
              e.preventDefault()
              const frameTime = 1 / 30 // 假设30fps
              player.currentTime((player.currentTime() || 0) - frameTime)
            }
            break
          case '.':
            // 逐帧前进（暂停时）
            if (player.paused()) {
              e.preventDefault()
              const frameTime = 1 / 30 // 假设30fps
              player.currentTime((player.currentTime() || 0) + frameTime)
            }
            break
          case '<':
            // 减慢播放速度
            e.preventDefault()
            {
              const rates = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]
              const currentRate = player.playbackRate()
              const currentIndex = rates.findIndex(r => Math.abs(r - currentRate) < 0.01)
              if (currentIndex > 0) {
                const newRate = rates[currentIndex - 1]
                player.playbackRate(newRate)
                setPlaybackRate(newRate)
                setShowPlaybackRateIndicator(true)
              }
            }
            break
          case '>':
            // 加快播放速度
            e.preventDefault()
            {
              const rates = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]
              const currentRate = player.playbackRate()
              const currentIndex = rates.findIndex(r => Math.abs(r - currentRate) < 0.01)
              if (currentIndex < rates.length - 1 && currentIndex !== -1) {
                const newRate = rates[currentIndex + 1]
                player.playbackRate(newRate)
                setPlaybackRate(newRate)
                setShowPlaybackRateIndicator(true)
              } else if (currentIndex === -1) {
                player.playbackRate(1)
                setPlaybackRate(1)
              }
            }
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
            for (let i = 0; i < (tracks as any).length; i++) {
              if ((tracks as any)[i].kind === 'subtitles') {
                subtitleTrack = (tracks as any)[i]
                break
              }
            }
            if (subtitleTrack) {
              subtitleTrack.mode = subtitleTrack.mode === 'showing' ? 'hidden' : 'showing'
            }
            break
          case '?':
            // 显示键盘快捷键帮助
            e.preventDefault()
            setShowKeyboardHelp(true)
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
        const isFullscreen = player.isFullscreen() || false
        console.log('Fullscreen:', isFullscreen)
        
        // Optimize subtitle position in fullscreen
        const textTrackDisplay = player.el().querySelector('.vjs-text-track-display')
        if (textTrackDisplay) {
          if (isFullscreen) {
            (textTrackDisplay as HTMLElement).style.fontSize = '1.5em'
            (textTrackDisplay as HTMLElement).style.bottom = '80px'
          } else {
            (textTrackDisplay as HTMLElement).style.fontSize = ''
            (textTrackDisplay as HTMLElement).style.bottom = ''
          }
        }
        
        // Ensure controls are visible when entering fullscreen
        if (isFullscreen) {
          const controlBar = player.controlBar?.el()
          if (controlBar) {
            controlBar.style.opacity = '1'
            controlBar.style.visibility = 'visible'
          }
        }
      })

      // Playback rate change tracking
      player.on('ratechange', () => {
        const rate = player.playbackRate() || 1
        setPlaybackRate(rate)
        if (rate !== 1) {
          setShowPlaybackRateIndicator(true)
        }
      })

      // Buffering state tracking
      player.on('waiting', () => {
        console.log('Buffering...')
        // The loading spinner is handled automatically by Video.js
      })

      player.on('canplay', () => {
        console.log('Can play - buffering complete')
      })

      player.on('progress', () => {
        // Track buffer progress
        const buffered = player.buffered()
        if (buffered.length > 0) {
          const bufferedEnd = buffered.end(buffered.length - 1)
          const duration = player.duration()
          const bufferedPercent = (bufferedEnd / duration) * 100
          console.log(`Buffered: ${bufferedPercent.toFixed(1)}%`)
        }
      })

      // Quality selector (if multiple sources)
      // player.qualityLevels() // Requires videojs-contrib-quality-levels

      // Add custom controls
      const Button = videojs.getComponent('Button')
      const MenuButton = videojs.getComponent('MenuButton')
      const MenuItem = videojs.getComponent('MenuItem')

      // Quality Selector Button (画质选择器)
      class QualitySelector extends MenuButton {
        constructor(player: any, options: any) {
          super(player, options)
          // @ts-ignore
          this.controlText('Quality')
          this.addClass('vjs-quality-selector')
        }

        createEl() {
          const el = super.createEl()
          // 添加设置图标 (齿轮图标)
          el.innerHTML = `
            <span class="vjs-icon-placeholder" aria-hidden="true">
              <svg height="100%" version="1.1" viewBox="0 0 36 36" width="100%">
                <path d="M 23.94,18.78 C 23.94,21.53 21.69,23.78 18.94,23.78 C 16.19,23.78 13.94,21.53 13.94,18.78 C 13.94,16.03 16.19,13.78 18.94,13.78 C 21.69,13.78 23.94,16.03 23.94,18.78 Z M 27.74,18.78 C 27.74,18.46 27.73,18.14 27.71,17.82 L 30.55,15.56 L 28.55,12.22 L 25.26,13.48 C 24.69,13.01 24.06,12.62 23.37,12.32 L 22.87,8.78 L 18.87,8.78 L 18.37,12.32 C 17.68,12.62 17.05,13.01 16.48,13.48 L 13.19,12.22 L 11.19,15.56 L 14.03,17.82 C 14.01,18.14 14,18.46 14,18.78 C 14,19.1 14.01,19.42 14.03,19.74 L 11.19,22 L 13.19,25.34 L 16.48,24.08 C 17.05,24.55 17.68,24.94 18.37,25.24 L 18.87,28.78 L 22.87,28.78 L 23.37,25.24 C 24.06,24.94 24.69,24.55 25.26,24.08 L 28.55,25.34 L 30.55,22 L 27.71,19.74 C 27.73,19.42 27.74,19.1 27.74,18.78 Z" fill="#fff"></path>
              </svg>
            </span>
          `
          return el
        }

        createItems() {
          const qualities = ['自动', '1080p', '720p', '480p', '360p']
          return qualities.map((quality) => {
            const item = new MenuItem(this.player(), {
              label: quality,
              selectable: true,
              selected: quality === '自动',
            })

            item.handleClick = () => {
              // 处理画质切换
              console.log('Selected quality:', quality)
              // TODO: 集成 HLS quality selector
            }

            return item
          })
        }
      }

      // Theater mode button (影院模式)
      class TheaterButton extends Button {
        constructor(player: any, options: any) {
          super(player, options)
          // @ts-ignore
          this.controlText('Theater mode')
          this.addClass('vjs-theater-button')
        }

        buildCSSClass() {
          return `vjs-theater-button ${super.buildCSSClass()}`
        }

        createEl() {
          const el = super.createEl()
          // 添加影院模式图标
          el.innerHTML = `
            <span class="vjs-icon-placeholder" aria-hidden="true">
              <svg height="100%" version="1.1" viewBox="0 0 36 36" width="100%">
                <path d="m 26,13 0,10 -16,0 0,-10 z m -14,2 12,0 0,6 -12,0 0,-6 z" fill="#fff"></path>
              </svg>
            </span>
          `
          return el
        }

        handleClick() {
          // Toggle theater mode
          const currentState = !theaterMode
          setTheaterMode(currentState)
          const playerEl = this.player().el()
          if (currentState) {
            playerEl.classList.add('vjs-theater-mode')
          } else {
            playerEl.classList.remove('vjs-theater-mode')
          }
        }
      }

      videojs.registerComponent('QualitySelector', QualitySelector)
      videojs.registerComponent('TheaterButton', TheaterButton)

      // 🆕 YouTube-style interactions
      const playerEl = player.el()

      // Double-click interactions: left 1/3 rewind, right 1/3 forward, center play/pause
      const handleDoubleClick = (e: MouseEvent) => {
        const rect = playerEl.getBoundingClientRect()
        const clickX = e.clientX - rect.left
        const width = rect.width
        const clickPercentage = clickX / width

        if (clickPercentage < 0.33) {
          // Left 1/3 - rewind 10 seconds
          player.currentTime((player.currentTime() || 0) - 10)
          setSeekFeedback({ show: true, direction: 'backward', seconds: 10, position: 'left' })
        } else if (clickPercentage > 0.67) {
          // Right 1/3 - forward 10 seconds
          player.currentTime((player.currentTime() || 0) + 10)
          setSeekFeedback({ show: true, direction: 'forward', seconds: 10, position: 'right' })
        } else {
          // Center - toggle play/pause
          if (player.paused()) {
            player.play()
          } else {
            player.pause()
          }
        }
      }

      // Detect double-click
      playerEl.addEventListener('click', (e: Event) => {
        const mouseEvent = e as MouseEvent
        const now = Date.now()
        const timeSinceLastClick = now - lastClickTimeRef.current

        if (timeSinceLastClick < 300) {
          // Double-click detected
          clickCountRef.current++
          if (clickCountRef.current === 2) {
            handleDoubleClick(mouseEvent)
            clickCountRef.current = 0
          }
        } else {
          clickCountRef.current = 1
        }

        lastClickTimeRef.current = now
      })

      // Wheel event for volume control
      const handleWheel = (e: WheelEvent) => {
        e.preventDefault()
        const delta = e.deltaY > 0 ? -0.05 : 0.05 // Scroll down = decrease, scroll up = increase
        const newVolume = Math.max(0, Math.min(1, (player.volume() || 0) + delta))
        player.volume(newVolume)
        setVolumeIndicator({ 
          show: true, 
          volume: newVolume * 100, 
          muted: player.muted() 
        })
      }

      playerEl.addEventListener('wheel', handleWheel, { passive: false })

      // Control bar auto-hide (YouTube-style)
      const handleMouseMove = () => {
        const controlBar = player.controlBar?.el()
        if (controlBar) {
          controlBar.style.opacity = '1'
          controlBar.style.visibility = 'visible'

          if (controlBarTimeoutRef.current) {
            clearTimeout(controlBarTimeoutRef.current)
          }

          controlBarTimeoutRef.current = setTimeout(() => {
            if (!player.paused()) {
              controlBar.style.opacity = '0'
              controlBar.style.visibility = 'hidden'
            }
          }, 3000)
        }
      }

      playerEl.addEventListener('mousemove', handleMouseMove)
      playerEl.addEventListener('mouseleave', () => {
        if (controlBarTimeoutRef.current) {
          clearTimeout(controlBarTimeoutRef.current)
        }
      })

      // Right-click context menu
      const handleContextMenu = (e: MouseEvent) => {
        e.preventDefault()
        setContextMenu({
          visible: true,
          x: e.clientX,
          y: e.clientY,
        })
      }

      playerEl.addEventListener('contextmenu', handleContextMenu)

      // Store player element for cleanup
      player.playerElement = playerEl
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

  // Handlers for feedback components
  const handleSeekFeedbackEnd = useCallback(() => {
    setSeekFeedback(prev => ({ ...prev, show: false }))
  }, [])

  const handleVolumeIndicatorEnd = useCallback(() => {
    setVolumeIndicator(prev => ({ ...prev, show: false }))
  }, [])

  // Context menu handlers (optimized with useCallback)
  const handleCloseContextMenu = useCallback(() => {
    setContextMenu({ visible: false, x: 0, y: 0 })
  }, [])

  const handleToggleLoop = useCallback(() => {
    const player = playerRef.current
    if (player) {
      setLoopEnabled(prev => {
        const newLoopState = !prev
        player.loop(newLoopState)
        return newLoopState
      })
    }
  }, [])

  const handleChangePlaybackRate = useCallback((rate: number) => {
    const player = playerRef.current
    if (player) {
      player.playbackRate(rate)
      setPlaybackRate(rate)
      if (rate !== 1) {
        setShowPlaybackRateIndicator(true)
      }
    }
  }, [])

  const handleChangeQuality = useCallback((quality: string) => {
    // Quality change handled by HLS quality selector plugin
    console.log('Change quality to:', quality)
  }, [])

  const handleCopyVideoUrl = useCallback(() => {
    const url = window.location.href.split('?')[0] // Remove query params
    navigator.clipboard.writeText(url).then(() => {
      toast.success('视频链接已复制', { duration: 2000 })
    }).catch(() => {
      toast.error('复制失败，请重试')
    })
  }, [])

  const handleCopyVideoUrlWithTime = useCallback(() => {
    const player = playerRef.current
    if (player) {
      const currentTime = Math.floor(player.currentTime() || 0)
      const url = `${window.location.href.split('?')[0]}?t=${currentTime}`
      navigator.clipboard.writeText(url).then(() => {
        toast.success(`链接已复制（含时间戳 ${currentTime}秒）`, { duration: 2000 })
      }).catch(() => {
        toast.error('复制失败，请重试')
      })
    }
  }, [])

  const handleToggleStats = useCallback(() => {
    setShowStats(prev => !prev)
  }, [])

  const handleToggleMiniPlayer = useCallback(() => {
    setMiniPlayer(prev => {
      const newState = !prev
      const player = playerRef.current
      if (player) {
        const playerEl = player.el()
        if (newState) {
          playerEl.classList.add('vjs-mini-player')
        } else {
          playerEl.classList.remove('vjs-mini-player')
        }
      }
      return newState
    })
  }, [])

  const handleToggleTheaterMode = useCallback(() => {
    setTheaterMode(prev => {
      const newState = !prev
      const player = playerRef.current
      if (player) {
        const playerEl = player.el()
        if (newState) {
          playerEl.classList.add('vjs-theater-mode')
        } else {
          playerEl.classList.remove('vjs-theater-mode')
        }
      }
      return newState
    })
  }, [])

  const handleToggleFullscreen = useCallback(() => {
    const player = playerRef.current
    if (player) {
      if (player.isFullscreen()) {
        player.exitFullscreen()
      } else {
        player.requestFullscreen()
      }
    }
  }, [])

  // Close context menu on scroll or outside click
  useEffect(() => {
    const handleClickOutside = () => {
      if (contextMenu.visible) {
        handleCloseContextMenu()
      }
    }

    const handleScroll = () => {
      if (contextMenu.visible) {
        handleCloseContextMenu()
      }
    }

    document.addEventListener('click', handleClickOutside)
    document.addEventListener('scroll', handleScroll)

    return () => {
      document.removeEventListener('click', handleClickOutside)
      document.removeEventListener('scroll', handleScroll)
    }
  }, [contextMenu.visible])

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
        // 静默保存，不显示 toast（避免干扰观看）
        if (process.env.NODE_ENV === 'development') {
          console.log(`✅ 进度已保存: ${currentTime}s / ${duration}s`)
        }
      } catch (error) {
        console.error('保存进度失败:', error)
        // 只在失败时显示提示
        if (process.env.NODE_ENV === 'development') {
          toast.error('保存进度失败', { duration: 2000 })
        }
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
        subtitleList.forEach((subtitle) => {
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
          for (let i = 0; i < (tracks as any).length; i++) {
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

      {/* Seek Feedback (Double-click or J/L keys) */}
      <SeekFeedback
        show={seekFeedback.show}
        direction={seekFeedback.direction}
        seconds={seekFeedback.seconds}
        position={seekFeedback.position}
        onAnimationEnd={handleSeekFeedbackEnd}
      />

      {/* Volume Indicator */}
      <VolumeIndicator
        show={volumeIndicator.show}
        volume={volumeIndicator.volume}
        muted={volumeIndicator.muted}
        onAnimationEnd={handleVolumeIndicatorEnd}
      />

      {/* Playback Rate Indicator */}
      <PlaybackRateIndicator
        rate={playbackRate}
        show={showPlaybackRateIndicator}
      />

      {/* YouTube-style Context Menu */}
      <ContextMenu
        visible={contextMenu.visible}
        x={contextMenu.x}
        y={contextMenu.y}
        onClose={handleCloseContextMenu}
        loopEnabled={loopEnabled}
        onToggleLoop={handleToggleLoop}
        currentPlaybackRate={playerRef.current?.playbackRate() || 1}
        onChangePlaybackRate={handleChangePlaybackRate}
        currentQuality="Auto" // TODO: Get from HLS quality selector
        onChangeQuality={handleChangeQuality}
        onCopyVideoUrl={handleCopyVideoUrl}
        onCopyVideoUrlWithTime={handleCopyVideoUrlWithTime}
        onToggleStats={handleToggleStats}
        onToggleMiniPlayer={handleToggleMiniPlayer}
        onToggleTheaterMode={handleToggleTheaterMode}
        onToggleFullscreen={handleToggleFullscreen}
        isTheaterMode={theaterMode}
        isFullscreen={playerRef.current?.isFullscreen() || false}
      />

      {/* Stats Panel (Stats for nerds) */}
      {showStats && videoId && (
        <StatsPanel
          visible={showStats}
          player={playerRef.current}
          videoId={videoId}
          onClose={() => setShowStats(false)}
        />
      )}

      {/* Keyboard Shortcuts Help (? key) */}
      <KeyboardShortcuts
        visible={showKeyboardHelp}
        onClose={() => setShowKeyboardHelp(false)}
      />

      {/* Keyboard shortcuts hint */}
      <div className="keyboard-shortcuts-hint text-xs text-gray-400 mt-2">
        <p>按 ? 查看完整快捷键列表 | Space/K = 播放/暂停 | J/L = 快退/快进 | ↑↓ = 音量 | F = 全屏</p>
      </div>

      {/* Subtitle info */}
      {subtitles.length > 0 && (
        <div className="subtitle-info text-xs text-gray-500 mt-1">
          <p>可用字幕: {subtitles.map(s => s.language_name).join(', ')}</p>
        </div>
      )}
    </div>
  )
}

export default VideoPlayer
