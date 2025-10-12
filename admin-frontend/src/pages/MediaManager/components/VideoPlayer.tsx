import React from 'react'
import { Modal } from 'antd'
import type { MediaItem } from '../types'

interface VideoPlayerProps {
  visible: boolean
  video: MediaItem | null
  onClose: () => void
}

/**
 * 视频播放器组件
 */
const VideoPlayer: React.FC<VideoPlayerProps> = ({ visible, video, onClose }) => {
  if (!video) return null

  return (
    <Modal
      title={video.title}
      open={visible}
      onCancel={onClose}
      footer={null}
      width={1000}
      centered
      destroyOnClose
    >
      <div style={{
        width: '100%',
        minHeight: 400,
        background: '#000',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <video
          src={video.url}
          controls
          autoPlay
          style={{
            width: '100%',
            maxHeight: '70vh',
          }}
        >
          您的浏览器不支持视频播放
        </video>
      </div>

      <div style={{ marginTop: 16, color: '#8c8c8c', fontSize: 12 }}>
        <div>文件大小: {formatFileSize(video.file_size)}</div>
        <div>上传时间: {new Date(video.created_at).toLocaleString()}</div>
      </div>
    </Modal>
  )
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
}

export default VideoPlayer
