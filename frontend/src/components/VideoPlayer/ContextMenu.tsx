import React, { useEffect, useRef } from 'react'
import './ContextMenu.css'

export interface ContextMenuProps {
  visible: boolean
  x: number
  y: number
  onClose: () => void
  loopEnabled: boolean
  onToggleLoop: () => void
  currentPlaybackRate: number
  onChangePlaybackRate: (rate: number) => void
  currentQuality: string
  onChangeQuality: (quality: string) => void
  onCopyVideoUrl: () => void
  onCopyVideoUrlWithTime: () => void
  onToggleStats: () => void
  onToggleMiniPlayer: () => void
  onToggleTheaterMode: () => void
  onToggleFullscreen: () => void
  isTheaterMode: boolean
  isFullscreen: boolean
}

const ContextMenu: React.FC<ContextMenuProps> = ({
  visible,
  x,
  y,
  onClose,
  loopEnabled,
  onToggleLoop,
  currentPlaybackRate,
  onChangePlaybackRate,
  currentQuality,
  onChangeQuality,
  onCopyVideoUrl,
  onCopyVideoUrlWithTime,
  onToggleStats,
  onToggleMiniPlayer,
  onToggleTheaterMode,
  onToggleFullscreen,
  isTheaterMode,
  isFullscreen,
}) => {
  const menuRef = useRef<HTMLDivElement>(null)
  const [showSpeedSubmenu, setShowSpeedSubmenu] = React.useState(false)
  const [showQualitySubmenu, setShowQualitySubmenu] = React.useState(false)

  const playbackRates = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]
  const qualities = ['auto', '1080p', '720p', '480p', '360p']

  useEffect(() => {
    if (!visible) return

    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose()
      }
    }

    const handleScroll = () => {
      onClose()
    }

    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('wheel', handleScroll)

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('wheel', handleScroll)
    }
  }, [visible, onClose])

  if (!visible) return null

  // Adjust position if menu would go off screen
  const menuStyle: React.CSSProperties = {
    left: Math.min(x, window.innerWidth - 250),
    top: Math.min(y, window.innerHeight - 400),
  }

  const handleMenuItemClick = (action: () => void) => {
    action()
    onClose()
  }

  return (
    <div
      ref={menuRef}
      className="youtube-context-menu"
      style={menuStyle}
      onClick={(e) => e.stopPropagation()}
    >
      {/* Loop */}
      <div
        className="context-menu-item"
        onClick={() => handleMenuItemClick(onToggleLoop)}
      >
        <span className="context-menu-icon">{loopEnabled ? '✓' : ''}</span>
        <span>循环播放</span>
      </div>

      <div className="context-menu-divider" />

      {/* Playback Speed */}
      <div
        className="context-menu-item context-menu-submenu"
        onMouseEnter={() => setShowSpeedSubmenu(true)}
        onMouseLeave={() => setShowSpeedSubmenu(false)}
      >
        <span className="context-menu-icon"></span>
        <span>播放速度</span>
        <span className="context-menu-arrow">▶</span>

        {showSpeedSubmenu && (
          <div className="submenu-panel">
            {playbackRates.map((rate) => (
              <div
                key={rate}
                className="context-menu-item"
                onClick={() => handleMenuItemClick(() => onChangePlaybackRate(rate))}
              >
                <span className="context-menu-icon">
                  {Math.abs(rate - currentPlaybackRate) < 0.01 ? '✓' : ''}
                </span>
                <span>{rate === 1 ? '正常' : `${rate}x`}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quality */}
      <div
        className="context-menu-item context-menu-submenu"
        onMouseEnter={() => setShowQualitySubmenu(true)}
        onMouseLeave={() => setShowQualitySubmenu(false)}
      >
        <span className="context-menu-icon"></span>
        <span>画质</span>
        <span className="context-menu-arrow">▶</span>

        {showQualitySubmenu && (
          <div className="submenu-panel">
            {qualities.map((quality) => (
              <div
                key={quality}
                className="context-menu-item"
                onClick={() => handleMenuItemClick(() => onChangeQuality(quality))}
              >
                <span className="context-menu-icon">
                  {quality === currentQuality ? '✓' : ''}
                </span>
                <span>{quality === 'auto' ? '自动' : quality}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="context-menu-divider" />

      {/* Copy Video URL */}
      <div
        className="context-menu-item"
        onClick={() => handleMenuItemClick(onCopyVideoUrl)}
      >
        <span className="context-menu-icon"></span>
        <span>复制视频网址</span>
      </div>

      {/* Copy Video URL with Time */}
      <div
        className="context-menu-item"
        onClick={() => handleMenuItemClick(onCopyVideoUrlWithTime)}
      >
        <span className="context-menu-icon"></span>
        <span>复制当前时间的视频网址</span>
      </div>

      <div className="context-menu-divider" />

      {/* Stats */}
      <div
        className="context-menu-item"
        onClick={() => handleMenuItemClick(onToggleStats)}
      >
        <span className="context-menu-icon"></span>
        <span>统计信息</span>
      </div>

      {/* Mini Player */}
      <div
        className="context-menu-item"
        onClick={() => handleMenuItemClick(onToggleMiniPlayer)}
      >
        <span className="context-menu-icon"></span>
        <span>迷你播放器</span>
      </div>

      {/* Theater Mode */}
      <div
        className="context-menu-item"
        onClick={() => handleMenuItemClick(onToggleTheaterMode)}
      >
        <span className="context-menu-icon">{isTheaterMode ? '✓' : ''}</span>
        <span>剧场模式</span>
      </div>

      {/* Fullscreen */}
      <div
        className="context-menu-item"
        onClick={() => handleMenuItemClick(onToggleFullscreen)}
      >
        <span className="context-menu-icon">{isFullscreen ? '✓' : ''}</span>
        <span>全屏</span>
      </div>
    </div>
  )
}

export default ContextMenu
