/**
 * WebSocket Hook for Real-time Notifications
 * 用于管理后台实时接收转码进度、系统消息等通知
 */
import { useEffect, useRef, useState, useCallback } from 'react'
import { message as antdMessage } from 'antd'

export interface WebSocketMessage {
  type: string
  [key: string]: any
}

export interface TranscodeProgressMessage {
  type: 'transcode_progress'
  video_id: number
  status: string
  progress: number
  message?: string
  timestamp: string
}

export interface TranscodeCompleteMessage {
  type: 'transcode_complete'
  video_id: number
  title: string
  format_type: string
  file_size: number
  timestamp: string
}

export interface TranscodeFailedMessage {
  type: 'transcode_failed'
  video_id: number
  title: string
  error: string
  timestamp: string
}

export interface SystemMessage {
  type: 'system_message'
  message: string
  level: 'info' | 'warning' | 'error' | 'success'
  timestamp: string
}

export interface UseWebSocketOptions {
  /**
   * 是否自动连接 (默认true)
   */
  autoConnect?: boolean

  /**
   * 是否自动重连 (默认true)
   */
  autoReconnect?: boolean

  /**
   * 重连间隔 (毫秒, 默认3000)
   */
  reconnectInterval?: number

  /**
   * 最大重连次数 (默认5, 0为无限)
   */
  maxReconnectAttempts?: number

  /**
   * 心跳间隔 (毫秒, 默认30000)
   */
  heartbeatInterval?: number

  /**
   * 消息回调
   */
  onMessage?: (message: WebSocketMessage) => void

  /**
   * 转码进度回调
   */
  onTranscodeProgress?: (message: TranscodeProgressMessage) => void

  /**
   * 转码完成回调
   */
  onTranscodeComplete?: (message: TranscodeCompleteMessage) => void

  /**
   * 转码失败回调
   */
  onTranscodeFailed?: (message: TranscodeFailedMessage) => void

  /**
   * 系统消息回调
   */
  onSystemMessage?: (message: SystemMessage) => void

  /**
   * 连接成功回调
   */
  onConnect?: () => void

  /**
   * 连接断开回调
   */
  onDisconnect?: () => void

  /**
   * 错误回调
   */
  onError?: (error: Event) => void
}

export function useWebSocket(isAdmin: boolean = true, options: UseWebSocketOptions = {}) {
  const {
    autoConnect = true,
    autoReconnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    heartbeatInterval = 30000,
    onMessage,
    onTranscodeProgress,
    onTranscodeComplete,
    onTranscodeFailed,
    onSystemMessage,
    onConnect,
    onDisconnect,
    onError,
  } = options

  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null)
  const heartbeatTimerRef = useRef<NodeJS.Timeout | null>(null)

  /**
   * 获取WebSocket URL
   */
  const getWebSocketUrl = useCallback(() => {
    const token = localStorage.getItem('admin_access_token')
    if (!token) {
      throw new Error('未找到访问令牌')
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = import.meta.env.VITE_WS_URL || window.location.host.replace(':3001', ':8000')
    const endpoint = isAdmin ? '/ws/admin' : '/ws'

    return `${protocol}//${host}/api/v1${endpoint}?token=${token}`
  }, [isAdmin])

  /**
   * 处理收到的消息
   */
  const handleMessage = useCallback(
    (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data) as WebSocketMessage
        console.log('📡 收到WebSocket消息:', data)

        setLastMessage(data)

        // 通用消息回调
        if (onMessage) {
          onMessage(data)
        }

        // 根据消息类型分发
        switch (data.type) {
          case 'transcode_progress':
            if (onTranscodeProgress) {
              onTranscodeProgress(data as TranscodeProgressMessage)
            }
            break

          case 'transcode_complete':
            if (onTranscodeComplete) {
              onTranscodeComplete(data as TranscodeCompleteMessage)
            }
            // 默认显示成功提示
            const completeMsg = data as TranscodeCompleteMessage
            antdMessage.success(`视频 "${completeMsg.title}" 转码完成 (${completeMsg.format_type.toUpperCase()})`)
            break

          case 'transcode_failed':
            if (onTranscodeFailed) {
              onTranscodeFailed(data as TranscodeFailedMessage)
            }
            // 默认显示错误提示
            const failedMsg = data as TranscodeFailedMessage
            antdMessage.error(`视频 "${failedMsg.title}" 转码失败: ${failedMsg.error.substring(0, 50)}`)
            break

          case 'system_message':
            if (onSystemMessage) {
              onSystemMessage(data as SystemMessage)
            }
            // 默认显示系统消息
            const sysMsg = data as SystemMessage
            switch (sysMsg.level) {
              case 'success':
                antdMessage.success(sysMsg.message)
                break
              case 'error':
                antdMessage.error(sysMsg.message)
                break
              case 'warning':
                antdMessage.warning(sysMsg.message)
                break
              default:
                antdMessage.info(sysMsg.message)
            }
            break

          case 'connected':
            console.log('✅ WebSocket连接已建立:', data)
            break

          default:
            console.log('收到未知类型的消息:', data.type)
        }
      } catch (error) {
        console.error('解析WebSocket消息失败:', error)
      }
    },
    [onMessage, onTranscodeProgress, onTranscodeComplete, onTranscodeFailed, onSystemMessage]
  )

  /**
   * 启动心跳
   */
  const startHeartbeat = useCallback(() => {
    if (heartbeatTimerRef.current) {
      clearInterval(heartbeatTimerRef.current)
    }

    heartbeatTimerRef.current = setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send('ping')
      }
    }, heartbeatInterval)
  }, [heartbeatInterval])

  /**
   * 停止心跳
   */
  const stopHeartbeat = useCallback(() => {
    if (heartbeatTimerRef.current) {
      clearInterval(heartbeatTimerRef.current)
      heartbeatTimerRef.current = null
    }
  }, [])

  /**
   * 连接WebSocket
   */
  const connect = useCallback(() => {
    try {
      const url = getWebSocketUrl()
      console.log('🔌 正在连接WebSocket:', url)

      const ws = new WebSocket(url)

      ws.onopen = () => {
        console.log('✅ WebSocket连接成功')
        setIsConnected(true)
        reconnectAttemptsRef.current = 0
        startHeartbeat()

        if (onConnect) {
          onConnect()
        }
      }

      ws.onmessage = handleMessage

      ws.onerror = (error) => {
        console.error('❌ WebSocket错误:', error)
        if (onError) {
          onError(error)
        }
      }

      ws.onclose = () => {
        console.log('❌ WebSocket连接已断开')
        setIsConnected(false)
        stopHeartbeat()

        if (onDisconnect) {
          onDisconnect()
        }

        // 自动重连
        if (autoReconnect) {
          const shouldReconnect =
            maxReconnectAttempts === 0 || reconnectAttemptsRef.current < maxReconnectAttempts

          if (shouldReconnect) {
            reconnectAttemptsRef.current += 1
            console.log(
              `🔄 尝试重连... (${reconnectAttemptsRef.current}/${maxReconnectAttempts || '∞'})`
            )

            reconnectTimerRef.current = setTimeout(() => {
              connect()
            }, reconnectInterval)
          } else {
            console.log('⚠️ 达到最大重连次数,停止重连')
            antdMessage.warning('WebSocket连接已断开,请刷新页面重新连接')
          }
        }
      }

      wsRef.current = ws
    } catch (error) {
      console.error('创建WebSocket连接失败:', error)
      if (error instanceof Error) {
        antdMessage.error(error.message)
      }
    }
  }, [
    getWebSocketUrl,
    handleMessage,
    autoReconnect,
    maxReconnectAttempts,
    reconnectInterval,
    onConnect,
    onDisconnect,
    onError,
    startHeartbeat,
    stopHeartbeat,
  ])

  /**
   * 断开WebSocket
   */
  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current)
      reconnectTimerRef.current = null
    }

    stopHeartbeat()

    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    setIsConnected(false)
  }, [stopHeartbeat])

  /**
   * 发送消息
   */
  const sendMessage = useCallback((message: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(message)
      return true
    }
    console.warn('WebSocket未连接,无法发送消息')
    return false
  }, [])

  // 自动连接
  useEffect(() => {
    if (autoConnect) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [autoConnect, connect, disconnect])

  return {
    isConnected,
    lastMessage,
    connect,
    disconnect,
    sendMessage,
  }
}
