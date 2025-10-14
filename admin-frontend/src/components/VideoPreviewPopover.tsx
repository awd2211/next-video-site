import { useState, useRef, useEffect } from 'react'
import { Card, Tag, Space, Popover, Statistic, Row, Col } from 'antd'
import {
  PlayCircleOutlined,
  EyeOutlined,
  LikeOutlined,
  StarOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons'
import './VideoPreviewPopover.css'

interface VideoPreviewPopoverProps {
  video: any
  children: React.ReactNode
  hoverDelay?: number // ms to wait before showing preview
}

const VideoPreviewPopover = ({
  video,
  children,
  hoverDelay = 500,
}: VideoPreviewPopoverProps) => {
  const [visible, setVisible] = useState(false)
  const [isVideoLoaded, setIsVideoLoaded] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  const hoverTimeoutRef = useRef<NodeJS.Timeout>()
  const playTimeoutRef = useRef<NodeJS.Timeout>()

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current)
      }
      if (playTimeoutRef.current) {
        clearTimeout(playTimeoutRef.current)
      }
    }
  }, [])

  // Handle popover visibility
  const handleVisibleChange = (newVisible: boolean) => {
    if (newVisible) {
      // Delay showing to avoid flickering when user quickly moves mouse
      hoverTimeoutRef.current = setTimeout(() => {
        setVisible(true)
      }, hoverDelay)
    } else {
      // Clear timeout if mouse leaves before delay
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current)
      }
      setVisible(false)
      setIsPlaying(false)
      setIsVideoLoaded(false)

      // Stop video if playing
      if (videoRef.current) {
        videoRef.current.pause()
        videoRef.current.currentTime = 0
      }
    }
  }

  // Auto-play video after preview is shown
  useEffect(() => {
    if (visible && videoRef.current && !isPlaying) {
      playTimeoutRef.current = setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.play()
          setIsPlaying(true)
        }
      }, 300) // Small delay before auto-play
    }

    return () => {
      if (playTimeoutRef.current) {
        clearTimeout(playTimeoutRef.current)
      }
    }
  }, [visible, isPlaying])

  // Format duration
  const formatDuration = (minutes: number | null | undefined) => {
    if (!minutes) return 'N/A'
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`
  }

  // Format number with K/M suffix
  const formatNumber = (num: number | null | undefined) => {
    if (!num) return '0'
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`
    }
    return num.toString()
  }

  // Get video URL (prefer AV1, fallback to H.264)
  const getVideoUrl = () => {
    if (video.is_av1_available && video.av1_master_url) {
      return video.av1_master_url
    }
    return video.video_url || video.trailer_url
  }

  const videoUrl = getVideoUrl()

  const previewContent = (
    <div className="video-preview-popover">
      {/* Video Player */}
      {videoUrl ? (
        <div className="video-preview-player">
          <video
            ref={videoRef}
            src={videoUrl}
            muted
            loop
            playsInline
            onLoadedData={() => setIsVideoLoaded(true)}
            className="preview-video"
            style={{ opacity: isVideoLoaded ? 1 : 0 }}
          />
          {!isVideoLoaded && (
            <div className="video-loading">
              <PlayCircleOutlined style={{ fontSize: 48, color: '#fff' }} />
            </div>
          )}

          {/* Overlay Info */}
          <div className="video-overlay">
            <Tag color={video.status === 'PUBLISHED' ? 'success' : 'default'}>
              {video.status}
            </Tag>
            {video.is_av1_available && (
              <Tag color="blue">AV1</Tag>
            )}
          </div>
        </div>
      ) : (
        <div className="video-no-preview">
          <PlayCircleOutlined style={{ fontSize: 48, color: '#999' }} />
          <p>无视频预览</p>
        </div>
      )}

      {/* Video Info */}
      <div className="video-preview-info">
        <h4 className="video-title">{video.title}</h4>
        {video.original_title && (
          <p className="video-original-title">{video.original_title}</p>
        )}

        {/* Stats */}
        <Row gutter={16} style={{ marginTop: 12 }}>
          <Col span={12}>
            <Statistic
              title="观看"
              value={formatNumber(video.view_count)}
              prefix={<EyeOutlined />}
              valueStyle={{ fontSize: 14 }}
            />
          </Col>
          <Col span={12}>
            <Statistic
              title="评分"
              value={video.average_rating?.toFixed(1) || '0.0'}
              prefix={<StarOutlined />}
              valueStyle={{ fontSize: 14 }}
            />
          </Col>
        </Row>

        <Row gutter={16} style={{ marginTop: 8 }}>
          <Col span={12}>
            <Statistic
              title="点赞"
              value={formatNumber(video.like_count)}
              prefix={<LikeOutlined />}
              valueStyle={{ fontSize: 14 }}
            />
          </Col>
          <Col span={12}>
            <Statistic
              title="时长"
              value={formatDuration(video.duration)}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ fontSize: 14 }}
            />
          </Col>
        </Row>

        {/* Categories */}
        {video.video_categories && video.video_categories.length > 0 && (
          <div style={{ marginTop: 12 }}>
            <Space size={[0, 4]} wrap>
              {video.video_categories.slice(0, 3).map((vc: any) => (
                <Tag key={vc.category?.id} color="blue" style={{ fontSize: 11 }}>
                  {vc.category?.name || vc.category?.name_en}
                </Tag>
              ))}
              {video.video_categories.length > 3 && (
                <Tag color="default" style={{ fontSize: 11 }}>
                  +{video.video_categories.length - 3}
                </Tag>
              )}
            </Space>
          </div>
        )}

        {/* Description (truncated) */}
        {video.description && (
          <p className="video-description">
            {video.description.length > 100
              ? `${video.description.substring(0, 100)}...`
              : video.description}
          </p>
        )}

        {/* Transcode Status */}
        {video.transcode_status && video.transcode_status !== 'completed' && (
          <div style={{ marginTop: 8 }}>
            <Tag color={video.transcode_status === 'processing' ? 'processing' : 'warning'}>
              转码: {video.transcode_status} ({video.transcode_progress || 0}%)
            </Tag>
          </div>
        )}
      </div>
    </div>
  )

  return (
    <Popover
      content={previewContent}
      title={null}
      trigger="hover"
      placement="rightTop"
      overlayClassName="video-preview-overlay"
      overlayStyle={{ width: 400 }}
      open={visible}
      onOpenChange={handleVisibleChange}
      mouseEnterDelay={hoverDelay / 1000} // Convert to seconds
      mouseLeaveDelay={0.1}
    >
      {children}
    </Popover>
  )
}

export default VideoPreviewPopover
