/**
 * 实时通知徽章组件
 * 显示在管理后台Header,展示WebSocket连接状态和未读消息数
 */
import React from 'react'
import { Badge, Tooltip, Space } from 'antd'
import { BellOutlined, WifiOutlined } from '@ant-design/icons'
import { useWebSocketContext } from '@/contexts/WebSocketContext'
import './index.css'

const NotificationBadge: React.FC = () => {
  const { isConnected, unreadCount, markAsRead } = useWebSocketContext()

  return (
    <Space size="large">
      {/* WebSocket连接状态 */}
      <Tooltip title={isConnected ? 'WebSocket已连接' : 'WebSocket已断开'}>
        <WifiOutlined
          className={`websocket-status ${isConnected ? 'connected' : 'disconnected'}`}
          style={{
            fontSize: '18px',
            color: isConnected ? '#52c41a' : '#d9d9d9',
          }}
        />
      </Tooltip>

      {/* 通知铃铛 */}
      <Tooltip title={unreadCount > 0 ? `${unreadCount} 条未读通知` : '暂无通知'}>
        <Badge count={unreadCount} offset={[-3, 3]} onClick={markAsRead}>
          <BellOutlined
            style={{
              fontSize: '20px',
              color: '#1890ff',
              cursor: 'pointer',
            }}
          />
        </Badge>
      </Tooltip>
    </Space>
  )
}

export default NotificationBadge
