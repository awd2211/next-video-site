import React from 'react'
import { Image } from 'antd'
import type { MediaItem } from '../types'

interface ImagePreviewProps {
  visible: boolean
  current: number
  images: MediaItem[]
  onClose: () => void
  onChange: (current: number) => void
}

/**
 * 图片预览组件 - 支持画廊模式和键盘导航
 */
const ImagePreview: React.FC<ImagePreviewProps> = ({
  visible,
  current,
  images,
  onClose,
  onChange,
}) => {
  if (images.length === 0) return null

  return (
    <Image.PreviewGroup
      preview={{
        visible,
        current,
        onVisibleChange: (value) => {
          if (!value) {
            onClose()
          }
        },
        onChange: (current) => {
          onChange(current)
        },
      }}
    >
      {images.map((item) => (
        <Image
          key={item.id}
          src={item.url}
          alt={item.title}
          style={{ display: 'none' }}
        />
      ))}
    </Image.PreviewGroup>
  )
}

export default ImagePreview
