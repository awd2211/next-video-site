/**
 * WebSocket Context for Global Notification Management
 * 全局WebSocket上下文,提供实时通知功能
 */
import React, { createContext, useContext, useState, ReactNode } from 'react'
import { useWebSocket, TranscodeProgressMessage, TranscodeCompleteMessage, TranscodeFailedMessage } from '@/hooks/useWebSocket'
import { notification, Badge } from 'antd'
import { BellOutlined, SyncOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons'

interface WebSocketContextValue {
  isConnected: boolean
  unreadCount: number
  transcodeProgress: Map<number, TranscodeProgressMessage>
  markAsRead: () => void
}

const WebSocketContext = createContext<WebSocketContextValue | undefined>(undefined)

export function useWebSocketContext() {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocketContext must be used within WebSocketProvider')
  }
  return context
}

interface WebSocketProviderProps {
  children: ReactNode
}

export function WebSocketProvider({ children }: WebSocketProviderProps) {
  const [unreadCount, setUnreadCount] = useState(0)
  const [transcodeProgress, setTranscodeProgress] = useState<Map<number, TranscodeProgressMessage>>(new Map())

  // 转码进度更新
  const handleTranscodeProgress = (message: TranscodeProgressMessage) => {
    setTranscodeProgress((prev) => {
      const newMap = new Map(prev)
      newMap.set(message.video_id, message)
      return newMap
    })

    // 如果是开始转码,显示通知
    if (message.progress === 0) {
      notification.info({
        message: '开始转码',
        description: message.message || `视频ID: ${message.video_id}`,
        icon: <SyncOutlined spin style={{ color: '#1890ff' }} />,
        duration: 3,
      })
      setUnreadCount((prev) => prev + 1)
    }
  }

  // 转码完成
  const handleTranscodeComplete = (message: TranscodeCompleteMessage) => {
    // 从进度中移除
    setTranscodeProgress((prev) => {
      const newMap = new Map(prev)
      newMap.delete(message.video_id)
      return newMap
    })

    notification.success({
      message: '转码完成',
      description: (
        <div>
          <div><strong>{message.title}</strong></div>
          <div>格式: {message.format_type.toUpperCase()}</div>
          <div>大小: {formatFileSize(message.file_size)}</div>
        </div>
      ),
      icon: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
      duration: 5,
    })
    setUnreadCount((prev) => prev + 1)
  }

  // 转码失败
  const handleTranscodeFailed = (message: TranscodeFailedMessage) => {
    // 从进度中移除
    setTranscodeProgress((prev) => {
      const newMap = new Map(prev)
      newMap.delete(message.video_id)
      return newMap
    })

    notification.error({
      message: '转码失败',
      description: (
        <div>
          <div><strong>{message.title}</strong></div>
          <div style={{ color: '#ff4d4f', fontSize: '12px' }}>
            {message.error.substring(0, 100)}...
          </div>
        </div>
      ),
      icon: <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
      duration: 0, // 失败消息不自动关闭
    })
    setUnreadCount((prev) => prev + 1)
  }

  // 标记为已读
  const markAsRead = () => {
    setUnreadCount(0)
  }

  const { isConnected } = useWebSocket(true, {
    autoConnect: true,
    autoReconnect: true,
    onTranscodeProgress: handleTranscodeProgress,
    onTranscodeComplete: handleTranscodeComplete,
    onTranscodeFailed: handleTranscodeFailed,
    onConnect: () => {
      console.log('✅ WebSocket已连接')
    },
    onDisconnect: () => {
      console.log('❌ WebSocket已断开')
    },
  })

  return (
    <WebSocketContext.Provider
      value={{
        isConnected,
        unreadCount,
        transcodeProgress,
        markAsRead,
      }}
    >
      {children}
    </WebSocketContext.Provider>
  )
}

/**
 * 格式化文件大小
 */
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}
