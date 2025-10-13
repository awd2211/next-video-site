/**
 * NotificationDrawer - 管理员通知抽屉
 * 显示管理员通知列表，支持筛选、标记为已读、删除等操作
 */
import React, { useState } from 'react';
import {
  Drawer,
  List,
  Tag,
  Button,
  Space,
  Empty,
  Spin,
  Typography,
  Tabs,
  Badge,
  Popconfirm,
  message,
} from 'antd';
import {
  BellOutlined,
  CheckOutlined,
  DeleteOutlined,
  UserAddOutlined,
  CommentOutlined,
  ExclamationCircleOutlined,
  DatabaseOutlined,
  CloudUploadOutlined,
  VideoCameraOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from '@/utils/axios';
import { formatDistanceToNow } from 'date-fns';
import { zhCN, enUS } from 'date-fns/locale';
import { useTranslation } from 'react-i18next';
import './index.css';

const { Text, Title } = Typography;

interface AdminNotification {
  id: number;
  type: string;
  title: string;
  content: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  link?: string;
  is_read: boolean;
  created_at: string;
  related_type?: string;
  related_id?: number;
}

interface NotificationDrawerProps {
  open: boolean;
  onClose: () => void;
}

const NotificationDrawer: React.FC<NotificationDrawerProps> = ({ open, onClose }) => {
  const { t, i18n } = useTranslation();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<string>('all');

  // Fetch notifications
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['admin-notifications', activeTab],
    queryFn: async () => {
      const params: any = { page: 1, page_size: 50 };
      if (activeTab === 'unread') params.is_read = false;
      else if (activeTab === 'read') params.is_read = true;

      const response = await axios.get('/api/v1/admin/notifications', { params });
      return response.data;
    },
    enabled: open,
  });

  // Mark as read mutation
  const markAsReadMutation = useMutation({
    mutationFn: async (notificationId: number) => {
      await axios.patch(`/api/v1/admin/notifications/${notificationId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-notifications'] });
      message.success(t('notifications.markedAsRead'));
    },
  });

  // Mark all as read mutation
  const markAllAsReadMutation = useMutation({
    mutationFn: async () => {
      await axios.post('/api/v1/admin/notifications/mark-all-read');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-notifications'] });
      message.success(t('notifications.allMarkedAsRead'));
    },
  });

  // Delete notification mutation
  const deleteMutation = useMutation({
    mutationFn: async (notificationId: number) => {
      await axios.delete(`/api/v1/admin/notifications/${notificationId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-notifications'] });
      message.success(t('notifications.deleted'));
    },
  });

  // Clear all notifications
  const clearAllMutation = useMutation({
    mutationFn: async () => {
      await axios.post('/api/v1/admin/notifications/clear-all');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-notifications'] });
      message.success(t('notifications.cleared'));
    },
  });

  // Get notification icon by type
  const getNotificationIcon = (type: string, severity: string) => {
    const iconStyle = { fontSize: 20 };

    switch (type) {
      case 'new_user_registration':
        return <UserAddOutlined style={{ ...iconStyle, color: '#52c41a' }} />;
      case 'pending_comment_review':
        return <CommentOutlined style={{ ...iconStyle, color: '#1890ff' }} />;
      case 'system_error_alert':
        return <ExclamationCircleOutlined style={{ ...iconStyle, color: '#ff4d4f' }} />;
      case 'storage_warning':
        return <DatabaseOutlined style={{ ...iconStyle, color: '#faad14' }} />;
      case 'upload_failed':
        return <CloudUploadOutlined style={{ ...iconStyle, color: '#ff4d4f' }} />;
      case 'video_processing_complete':
        return <VideoCameraOutlined style={{ ...iconStyle, color: '#52c41a' }} />;
      case 'suspicious_activity':
        return <WarningOutlined style={{ ...iconStyle, color: '#faad14' }} />;
      default:
        return <InfoCircleOutlined style={{ ...iconStyle, color: '#1890ff' }} />;
    }
  };

  // Get severity color
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return '#cf1322';
      case 'error':
        return '#ff4d4f';
      case 'warning':
        return '#faad14';
      default:
        return '#1890ff';
    }
  };

  // Handle notification click
  const handleNotificationClick = (notification: AdminNotification) => {
    if (!notification.is_read) {
      markAsReadMutation.mutate(notification.id);
    }
    if (notification.link) {
      window.location.href = notification.link;
    }
  };

  // Format time
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return formatDistanceToNow(date, {
      addSuffix: true,
      locale: i18n.language === 'zh-CN' ? zhCN : enUS,
    });
  };

  const notifications = data?.notifications || [];
  const unreadCount = data?.unread_count || 0;

  return (
    <Drawer
      title={
        <Space>
          <BellOutlined />
          <span>{t('notifications.title')}</span>
          {unreadCount > 0 && (
            <Badge count={unreadCount} style={{ backgroundColor: '#ff4d4f' }} />
          )}
        </Space>
      }
      placement="right"
      width={480}
      open={open}
      onClose={onClose}
      extra={
        <Space>
          <Button
            type="text"
            size="small"
            onClick={() => refetch()}
            loading={isLoading}
          >
            {t('common.refresh')}
          </Button>
          {unreadCount > 0 && (
            <Button
              type="text"
              size="small"
              icon={<CheckOutlined />}
              onClick={() => markAllAsReadMutation.mutate()}
              loading={markAllAsReadMutation.isPending}
            >
              {t('notifications.markAllAsRead')}
            </Button>
          )}
          <Popconfirm
            title={t('notifications.clearAllConfirm')}
            onConfirm={() => clearAllMutation.mutate()}
            okText={t('common.confirm')}
            cancelText={t('common.cancel')}
          >
            <Button
              type="text"
              size="small"
              danger
              icon={<DeleteOutlined />}
              loading={clearAllMutation.isPending}
            >
              {t('notifications.clearAll')}
            </Button>
          </Popconfirm>
        </Space>
      }
    >
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={[
          {
            key: 'all',
            label: `${t('notifications.all')} (${data?.total || 0})`,
          },
          {
            key: 'unread',
            label: `${t('notifications.unread')} (${unreadCount})`,
          },
          {
            key: 'read',
            label: t('notifications.read'),
          },
        ]}
      />

      <Spin spinning={isLoading}>
        {notifications.length === 0 ? (
          <Empty
            description={t('notifications.noNotifications')}
            style={{ marginTop: 60 }}
          />
        ) : (
          <List
            dataSource={notifications}
            renderItem={(notification: AdminNotification) => (
              <List.Item
                key={notification.id}
                className={`notification-item ${!notification.is_read ? 'unread' : ''}`}
                actions={[
                  !notification.is_read && (
                    <Button
                      type="text"
                      size="small"
                      icon={<CheckOutlined />}
                      onClick={(e) => {
                        e.stopPropagation();
                        markAsReadMutation.mutate(notification.id);
                      }}
                    />
                  ),
                  <Popconfirm
                    title={t('notifications.deleteConfirm')}
                    onConfirm={(e) => {
                      e?.stopPropagation();
                      deleteMutation.mutate(notification.id);
                    }}
                    okText={t('common.confirm')}
                    cancelText={t('common.cancel')}
                  >
                    <Button
                      type="text"
                      size="small"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={(e) => e.stopPropagation()}
                    />
                  </Popconfirm>,
                ].filter(Boolean)}
                onClick={() => handleNotificationClick(notification)}
                style={{ cursor: notification.link ? 'pointer' : 'default' }}
              >
                <List.Item.Meta
                  avatar={getNotificationIcon(notification.type, notification.severity)}
                  title={
                    <Space>
                      <Text strong={!notification.is_read}>{notification.title}</Text>
                      <Tag
                        color={getSeverityColor(notification.severity)}
                        style={{ fontSize: 10 }}
                      >
                        {notification.severity.toUpperCase()}
                      </Tag>
                    </Space>
                  }
                  description={
                    <div>
                      <Text type="secondary" style={{ fontSize: 13 }}>
                        {notification.content}
                      </Text>
                      <div style={{ marginTop: 4 }}>
                        <Text type="secondary" style={{ fontSize: 11 }}>
                          {formatTime(notification.created_at)}
                        </Text>
                      </div>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Spin>
    </Drawer>
  );
};

export default NotificationDrawer;
