/**
 * NotificationDrawer - 管理员通知抽屉
 * 显示实时通知列表，支持筛选、标记已读、删除等操作
 */
import { useState, useEffect } from 'react'
import {
  Drawer,
  List,
  Badge,
  Button,
  Empty,
  Tag,
  Space,
  Spin,
  Segmented,
  Popconfirm,
  message,
  Typography,
  Divider,
} from 'antd'
import {
  BellOutlined,
  CheckOutlined,
  DeleteOutlined,
  ReloadOutlined,
  ClearOutlined,
  InfoCircleOutlined,
  WarningOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getAdminNotifications,
  markNotificationAsRead,
  markAllNotificationsAsRead,
  deleteNotification,
  clearAllNotifications,
  AdminNotification,
} from '@/services/adminNotificationService'
import { useNavigate } from 'react-router-dom'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const { Text, Paragraph } = Typography

interface NotificationDrawerProps {
  open: boolean
  onClose: () => void
  unreadCount?: number
}

export default function NotificationDrawer({
  open,
  onClose,
  unreadCount = 0,
}: NotificationDrawerProps) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [filter, setFilter] = useState<'all' | 'unread'>('unread')
  const [page, setPage] = useState(1)
  const pageSize = 20

  // 获取通知列表
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['adminNotifications', page, filter],
    queryFn: () =>
      getAdminNotifications({
        page,
        page_size: pageSize,
        is_read: filter === 'unread' ? false : undefined,
      }),
    enabled: open,
  })

  // 标记已读
  const markReadMutation = useMutation({
    mutationFn: markNotificationAsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminNotifications'] })
      queryClient.invalidateQueries({ queryKey: ['adminNotificationStats'] })
    },
  })

  // 标记全部已读
  const markAllReadMutation = useMutation({
    mutationFn: markAllNotificationsAsRead,
    onSuccess: (data) => {
      message.success(data.message)
      queryClient.invalidateQueries({ queryKey: ['adminNotifications'] })
      queryClient.invalidateQueries({ queryKey: ['adminNotificationStats'] })
    },
  })

  // 删除通知
  const deleteMutation = useMutation({
    mutationFn: deleteNotification,
    onSuccess: () => {
      message.success('通知已删除')
      queryClient.invalidateQueries({ queryKey: ['adminNotifications'] })
      queryClient.invalidateQueries({ queryKey: ['adminNotificationStats'] })
    },
  })

  // 清空所有通知
  const clearAllMutation = useMutation({
    mutationFn: clearAllNotifications,
    onSuccess: (data) => {
      message.success(data.message)
      queryClient.invalidateQueries({ queryKey: ['adminNotifications'] })
      queryClient.invalidateQueries({ queryKey: ['adminNotificationStats'] })
    },
  })

  // 处理通知点击
  const handleNotificationClick = async (notification: AdminNotification) => {
    if (!notification.is_read) {
      await markReadMutation.mutateAsync(notification.id)
    }

    if (notification.link) {
      navigate(notification.link)
      onClose()
    }
  }

  // 获取严重程度图标和颜色
  const getSeverityInfo = (severity: string) => {
    switch (severity) {
      case 'critical':
        return { icon: <ExclamationCircleOutlined />, color: 'red', text: '严重' }
      case 'error':
        return { icon: <CloseCircleOutlined />, color: 'red', text: '错误' }
      case 'warning':
        return { icon: <WarningOutlined />, color: 'orange', text: '警告' }
      default:
        return { icon: <InfoCircleOutlined />, color: 'blue', text: '信息' }
    }
  }

  // 格式化时间
  const formatTime = (time: string) => {
    const date = dayjs(time)
    const now = dayjs()
    const diffHours = now.diff(date, 'hour')

    if (diffHours < 24) {
      return date.fromNow()
    } else if (diffHours < 48) {
      return '昨天 ' + date.format('HH:mm')
    } else {
      return date.format('MM-DD HH:mm')
    }
  }

  useEffect(() => {
    setPage(1)
  }, [filter])

  return (
    <Drawer
      title={
        <Space>
          <BellOutlined />
          <span>通知中心</span>
          {unreadCount > 0 && <Badge count={unreadCount} />}
        </Space>
      }
      placement="right"
      onClose={onClose}
      open={open}
      width={480}
      extra={
        <Space>
          <Button type="text" icon={<ReloadOutlined />} onClick={() => refetch()} loading={isLoading} />
          <Popconfirm title="确定标记所有通知为已读吗？" onConfirm={() => markAllReadMutation.mutate()}>
            <Button type="text" icon={<CheckOutlined />} disabled={unreadCount === 0}>全部已读</Button>
          </Popconfirm>
          <Popconfirm title="确定清空所有通知吗？此操作不可恢复" onConfirm={() => clearAllMutation.mutate()}>
            <Button type="text" danger icon={<ClearOutlined />}>清空</Button>
          </Popconfirm>
        </Space>
      }
    >
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <Segmented
          block
          value={filter}
          onChange={(value) => setFilter(value as 'all' | 'unread')}
          options={[{ label: '未读', value: 'unread' }, { label: '全部', value: 'all' }]}
        />

        <Divider style={{ margin: 0 }} />

        <Spin spinning={isLoading}>
          {data?.notifications && data.notifications.length > 0 ? (
            <List
              dataSource={data.notifications}
              renderItem={(notification) => {
                const severityInfo = getSeverityInfo(notification.severity)
                return (
                  <List.Item
                    key={notification.id}
                    style={{
                      padding: '12px',
                      background: notification.is_read ? 'transparent' : '#f0f5ff',
                      borderRadius: '4px',
                      marginBottom: '8px',
                      cursor: notification.link ? 'pointer' : 'default',
                      opacity: notification.is_read ? 0.7 : 1,
                    }}
                    onClick={() => handleNotificationClick(notification)}
                    actions={[
                      !notification.is_read && (
                        <Button
                          type="text"
                          size="small"
                          icon={<CheckOutlined />}
                          onClick={(e) => { e.stopPropagation(); markReadMutation.mutate(notification.id) }}
                        />
                      ),
                      <Popconfirm
                        title="确定删除此通知吗？"
                        onConfirm={(e) => { e?.stopPropagation(); deleteMutation.mutate(notification.id) }}
                        onCancel={(e) => e?.stopPropagation()}
                      >
                        <Button
                          type="text"
                          size="small"
                          danger
                          icon={<DeleteOutlined />}
                          onClick={(e) => e.stopPropagation()}
                        />
                      </Popconfirm>,
                    ]}
                  >
                    <List.Item.Meta
                      avatar={<div style={{ fontSize: 24, color: severityInfo.color }}>{severityInfo.icon}</div>}
                      title={
                        <Space>
                          <Text strong={!notification.is_read}>{notification.title}</Text>
                          <Tag color={severityInfo.color}>{severityInfo.text}</Tag>
                        </Space>
                      }
                      description={
                        <Space direction="vertical" size="small" style={{ width: '100%' }}>
                          <Paragraph ellipsis={{ rows: 2 }} style={{ margin: 0, fontSize: 13, color: '#666' }}>
                            {notification.content}
                          </Paragraph>
                          <Text type="secondary" style={{ fontSize: 12 }}>{formatTime(notification.created_at)}</Text>
                        </Space>
                      }
                    />
                  </List.Item>
                )
              }}
            />
          ) : (
            <Empty description={filter === 'unread' ? '暂无未读通知' : '暂无通知'} />
          )}
        </Spin>

        {data && data.pages > 1 && page < data.pages && (
          <Button block onClick={() => setPage((p) => p + 1)} loading={isLoading} style={{ marginTop: 16 }}>
            加载更多
          </Button>
        )}
      </Space>
    </Drawer>
  )
}
