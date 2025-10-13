/**
 * 实时通知徽章组件
 * 显示在管理后台Header,展示WebSocket连接状态和未读消息数
 */
import React, { useState, useEffect } from 'react'
import { Badge, Tooltip, Button } from 'antd'
import { BellOutlined } from '@ant-design/icons'
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import axios from '@/utils/axios'
import NotificationDrawer from '../NotificationDrawer'
import './index.css'

const NotificationBadge: React.FC = () => {
  const { t } = useTranslation()
  const [drawerOpen, setDrawerOpen] = useState(false)

  // Fetch notification stats
  const { data: stats, refetch } = useQuery({
    queryKey: ['admin-notification-stats'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/notifications/stats')
      return response.data
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  const unreadCount = stats?.unread || 0

  // Refetch when drawer opens
  useEffect(() => {
    if (drawerOpen) {
      refetch()
    }
  }, [drawerOpen, refetch])

  return (
    <>
      <Tooltip title={unreadCount > 0 ? t('notifications.unreadCount', { count: unreadCount }) : t('notifications.noNew')}>
        <Badge count={unreadCount} offset={[-3, 3]}>
          <Button
            type="text"
            icon={<BellOutlined style={{ fontSize: 20 }} />}
            onClick={() => setDrawerOpen(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          />
        </Badge>
      </Tooltip>

      <NotificationDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />
    </>
  )
}

export default NotificationBadge
