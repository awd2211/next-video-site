import React, { useEffect, useState } from 'react'
import { Progress, Tag, Button, Space, Tooltip, message } from 'antd'
import {
  SyncOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  ReloadOutlined
} from '@ant-design/icons'
import axios from 'axios'

interface TranscodeStatusProps {
  videoId: number
  initialStatus?: string
  initialProgress?: number
  onRetry?: () => void
  autoRefresh?: boolean // 是否自动刷新进度
  refreshInterval?: number // 刷新间隔(毫秒)
}

interface TranscodeStatusData {
  video_id: number
  status: string
  progress: number
  error: string | null
  h264_transcode_at: string | null
  av1_transcode_at: string | null
  is_av1_available: boolean
}

const TranscodeStatus: React.FC<TranscodeStatusProps> = ({
  videoId,
  initialStatus = 'pending',
  initialProgress = 0,
  onRetry,
  autoRefresh = true,
  refreshInterval = 5000, // 默认5秒刷新一次
}) => {
  const [status, setStatus] = useState(initialStatus)
  const [progress, setProgress] = useState(initialProgress)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [h264TranscodeAt, setH264TranscodeAt] = useState<string | null>(null)
  const [av1TranscodeAt, setAv1TranscodeAt] = useState<string | null>(null)

  // 获取转码状态
  const fetchTranscodeStatus = async () => {
    try {
      const response = await axios.get<TranscodeStatusData>(
        `/api/v1/admin/videos/${videoId}/transcode-status`
      )
      const data = response.data

      setStatus(data.status)
      setProgress(data.progress)
      setError(data.error)
      setH264TranscodeAt(data.h264_transcode_at)
      setAv1TranscodeAt(data.av1_transcode_at)
    } catch (err) {
      console.error('获取转码状态失败:', err)
    }
  }

  // 重试转码
  const handleRetry = async () => {
    try {
      setLoading(true)
      await axios.post(`/api/v1/admin/videos/${videoId}/retry-transcode`)
      message.success('转码任务已重新启动')

      // 重置状态
      setStatus('pending')
      setProgress(0)
      setError(null)

      // 立即刷新状态
      setTimeout(fetchTranscodeStatus, 1000)

      if (onRetry) {
        onRetry()
      }
    } catch (err: any) {
      message.error(err.response?.data?.detail || '重试失败')
    } finally {
      setLoading(false)
    }
  }

  // 自动刷新
  useEffect(() => {
    if (!autoRefresh) return

    // 只在转码进行中时自动刷新
    if (status === 'processing' || status === 'pending') {
      const timer = setInterval(fetchTranscodeStatus, refreshInterval)
      return () => clearInterval(timer)
    }
  }, [videoId, status, autoRefresh, refreshInterval])

  // 渲染状态标签
  const renderStatusTag = () => {
    switch (status) {
      case 'pending':
        return (
          <Tag icon={<ClockCircleOutlined />} color="default">
            等待转码
          </Tag>
        )
      case 'processing':
        return (
          <Tag icon={<SyncOutlined spin />} color="processing">
            转码中
          </Tag>
        )
      case 'completed':
        return (
          <Tag icon={<CheckCircleOutlined />} color="success">
            已完成
          </Tag>
        )
      case 'failed':
        return (
          <Tag icon={<CloseCircleOutlined />} color="error">
            转码失败
          </Tag>
        )
      default:
        return <Tag color="default">未知状态</Tag>
    }
  }

  // 渲染进度条
  const renderProgress = () => {
    if (status === 'pending') {
      return <Progress percent={0} size="small" status="normal" />
    }

    if (status === 'processing') {
      return (
        <Progress
          percent={progress}
          size="small"
          status="active"
          strokeColor={{
            '0%': '#108ee9',
            '100%': '#87d068',
          }}
        />
      )
    }

    if (status === 'completed') {
      return <Progress percent={100} size="small" status="success" />
    }

    if (status === 'failed') {
      return <Progress percent={progress} size="small" status="exception" />
    }

    return null
  }

  // 渲染转码格式标签
  const renderFormatTags = () => {
    return (
      <Space size="small">
        {h264TranscodeAt && (
          <Tooltip title={`H.264转码完成: ${new Date(h264TranscodeAt).toLocaleString()}`}>
            <Tag color="blue">H.264</Tag>
          </Tooltip>
        )}
        {av1TranscodeAt && (
          <Tooltip title={`AV1转码完成: ${new Date(av1TranscodeAt).toLocaleString()}`}>
            <Tag color="green">AV1</Tag>
          </Tooltip>
        )}
      </Space>
    )
  }

  return (
    <div className="transcode-status">
      <Space direction="vertical" size="small" style={{ width: '100%' }}>
        {/* 状态标签和格式 */}
        <Space>
          {renderStatusTag()}
          {renderFormatTags()}
        </Space>

        {/* 进度条 */}
        {renderProgress()}

        {/* 错误信息 */}
        {error && (
          <Tooltip title={error}>
            <div style={{ color: '#ff4d4f', fontSize: '12px', cursor: 'pointer' }}>
              错误: {error.substring(0, 50)}...
            </div>
          </Tooltip>
        )}

        {/* 失败时显示重试按钮 */}
        {status === 'failed' && (
          <Button
            size="small"
            icon={<ReloadOutlined />}
            onClick={handleRetry}
            loading={loading}
          >
            重试转码
          </Button>
        )}
      </Space>
    </div>
  )
}

export default TranscodeStatus
