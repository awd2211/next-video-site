/**
 * Video Download Button Component
 * Provides download functionality with quality selection
 */
import React, { useState } from 'react'
import { downloadVideo, formatFileSize } from '../../services/downloadService'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import './styles.css'

interface DownloadButtonProps {
  videoId: number
  className?: string
  buttonText?: string
}

const DownloadButton: React.FC<DownloadButtonProps> = ({
  videoId,
  className = '',
  buttonText = 'Download',
}) => {
  const { t } = useTranslation()
  const [showMenu, setShowMenu] = useState(false)
  const [loading, setLoading] = useState(false)
  const [selectedQuality, setSelectedQuality] = useState<string | null>(null)

  const qualities = [
    { value: '1080p', label: '1080p (Full HD)' },
    { value: '720p', label: '720p (HD)' },
    { value: '480p', label: '480p (SD)' },
    { value: '360p', label: '360p (Low)' },
    { value: 'original', label: 'Original' },
  ]

  const handleDownload = async (quality: string) => {
    setSelectedQuality(quality)
    setLoading(true)
    setShowMenu(false)

    try {
      const data = await downloadVideo(videoId, quality)
      console.log(`Downloading: ${data.video_title} (${quality})`)

      // Show success message (optional)
      if (data.file_size) {
        console.log(`File size: ${formatFileSize(data.file_size)}`)
      }
    } catch (error: any) {
      console.error('Download failed:', error)
      toast.error(error.response?.data?.detail || t('video.downloadFailed'))
    } finally {
      setLoading(false)
      setSelectedQuality(null)
    }
  }

  return (
    <div className={`download-button-container ${className}`}>
      <button
        className="download-button"
        onClick={() => setShowMenu(!showMenu)}
        disabled={loading}
      >
        {loading ? (
          <>
            <span className="loading-spinner"></span>
            Downloading...
          </>
        ) : (
          <>
            <svg
              className="download-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            {buttonText}
          </>
        )}
      </button>

      {showMenu && (
        <>
          {/* Backdrop */}
          <div className="download-menu-backdrop" onClick={() => setShowMenu(false)}></div>

          {/* Quality selection menu */}
          <div className="download-menu">
            <div className="download-menu-header">Select Quality</div>
            <ul className="download-menu-list">
              {qualities.map((quality) => (
                <li key={quality.value}>
                  <button
                    className="download-menu-item"
                    onClick={() => handleDownload(quality.value)}
                    disabled={loading && selectedQuality === quality.value}
                  >
                    <span>{quality.label}</span>
                    {loading && selectedQuality === quality.value && (
                      <span className="loading-spinner-small"></span>
                    )}
                  </button>
                </li>
              ))}
            </ul>
            <div className="download-menu-footer">
              <small>Download link expires in 24 hours</small>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default DownloadButton
