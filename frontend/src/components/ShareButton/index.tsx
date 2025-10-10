/**
 * 分享按钮组件
 */
import React, { useState } from 'react'
import { shareService, SharePlatform } from '../../services/shareService'
import './styles.css'

interface ShareButtonProps {
  videoId: number
  videoTitle?: string
  showLabel?: boolean
  className?: string
}

const ShareButton: React.FC<ShareButtonProps> = ({
  videoId,
  videoTitle,
  showLabel = true,
  className = '',
}) => {
  const [showModal, setShowModal] = useState(false)
  const [showQRCode, setShowQRCode] = useState(false)
  const [copySuccess, setCopySuccess] = useState(false)

  const platforms = [
    { id: 'wechat' as SharePlatform, name: '微信', icon: '💬', needsQR: true },
    { id: 'weibo' as SharePlatform, name: '微博', icon: '🔵', needsQR: false },
    { id: 'qq' as SharePlatform, name: 'QQ', icon: '🐧', needsQR: false },
    { id: 'qzone' as SharePlatform, name: 'QQ空间', icon: '⭐', needsQR: false },
    { id: 'twitter' as SharePlatform, name: 'Twitter', icon: '🐦', needsQR: false },
    { id: 'facebook' as SharePlatform, name: 'Facebook', icon: '👍', needsQR: false },
    { id: 'link' as SharePlatform, name: '复制链接', icon: '🔗', needsQR: false },
  ]

  const handleShare = async (platform: SharePlatform) => {
    try {
      // 记录分享行为
      await shareService.recordShare({
        video_id: videoId,
        platform: platform,
      })

      if (platform === 'wechat') {
        // 显示二维码
        setShowQRCode(true)
      } else if (platform === 'link') {
        // 复制链接
        const url = shareService.generateShareUrl(videoId)
        const success = await shareService.copyToClipboard(url)
        if (success) {
          setCopySuccess(true)
          setTimeout(() => setCopySuccess(false), 2000)
        }
      } else {
        // 打开分享窗口
        const shareUrl = shareService.generateShareUrl(videoId, platform)
        window.open(shareUrl, '_blank', 'width=600,height=400,menubar=no,toolbar=no')
      }
    } catch (error) {
      console.error('Share failed:', error)
    }
  }

  return (
    <div className={`share-button-wrapper ${className}`}>
      <button
        className="share-button"
        onClick={() => setShowModal(true)}
        aria-label="分享视频"
      >
        <span className="share-icon">📤</span>
        {showLabel && <span className="share-label">分享</span>}
      </button>

      {/* 分享模态框 */}
      {showModal && (
        <div className="share-modal-overlay" onClick={() => setShowModal(false)}>
          <div className="share-modal" onClick={(e) => e.stopPropagation()}>
            <div className="share-modal-header">
              <h3>分享到</h3>
              <button
                className="share-modal-close"
                onClick={() => setShowModal(false)}
                aria-label="关闭"
              >
                ×
              </button>
            </div>

            <div className="share-platforms">
              {platforms.map((platform) => (
                <button
                  key={platform.id}
                  className="share-platform-btn"
                  onClick={() => handleShare(platform.id)}
                >
                  <span className="platform-icon">{platform.icon}</span>
                  <span className="platform-name">{platform.name}</span>
                </button>
              ))}
            </div>

            {copySuccess && (
              <div className="copy-success-message">✓ 链接已复制到剪贴板</div>
            )}
          </div>
        </div>
      )}

      {/* 微信二维码模态框 */}
      {showQRCode && (
        <div className="share-modal-overlay" onClick={() => setShowQRCode(false)}>
          <div className="share-qr-modal" onClick={(e) => e.stopPropagation()}>
            <div className="share-modal-header">
              <h3>微信扫码分享</h3>
              <button
                className="share-modal-close"
                onClick={() => setShowQRCode(false)}
                aria-label="关闭"
              >
                ×
              </button>
            </div>

            <div className="qr-code-container">
              <img
                src={shareService.getQRCodeUrl(videoId)}
                alt="微信分享二维码"
                className="qr-code-image"
              />
              <p className="qr-code-hint">使用微信扫描二维码分享给好友</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ShareButton
