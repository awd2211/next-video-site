import React from 'react'
import { Card, List, Button, Space, Empty, Tag, Tooltip } from 'antd'
import {
  ClockCircleOutlined,
  FolderOutlined,
  FileOutlined,
  EyeOutlined,
  HistoryOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons'
import type { MediaItem } from '../types'

interface QuickActionsProps {
  recentUploads: MediaItem[]
  recentFolders: Array<{ id?: number; title: string; timestamp: number }>
  onFileClick: (item: MediaItem) => void
  onFolderClick: (folderId?: number) => void
  onClearHistory: () => void
}

/**
 * 快捷操作面板
 */
const QuickActions: React.FC<QuickActionsProps> = ({
  recentUploads,
  recentFolders,
  onFileClick,
  onFolderClick,
  onClearHistory,
}) => {
  // 格式化时间
  const formatTime = (timestamp: number): string => {
    const now = Date.now()
    const diff = now - timestamp
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 1) return '刚刚'
    if (minutes < 60) return `${minutes}分钟前`
    if (hours < 24) return `${hours}小时前`
    if (days < 7) return `${days}天前`
    return new Date(timestamp).toLocaleDateString()
  }

  // 格式化文件大小
  const formatSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`
  }

  // 获取文件类型标签
  const getFileTypeTag = (item: MediaItem) => {
    if (item.is_folder) {
      return <Tag color="gold">文件夹</Tag>
    }
    if (item.media_type === 'image') {
      return <Tag color="green">图片</Tag>
    }
    if (item.media_type === 'video') {
      return <Tag color="blue">视频</Tag>
    }
    return <Tag>文件</Tag>
  }

  return (
    <div style={{ padding: '16px 0' }}>
      <Card
        size="small"
        title={
          <Space>
            <ThunderboltOutlined style={{ color: '#1890ff' }} />
            <span>快捷操作</span>
          </Space>
        }
        bordered={false}
      >
        {/* 最近上传 */}
        <div style={{ marginBottom: 24 }}>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 12,
            }}
          >
            <div style={{ fontSize: 14, fontWeight: 500 }}>
              <ClockCircleOutlined style={{ marginRight: 6, color: '#52c41a' }} />
              最近上传
            </div>
            {recentUploads.length > 0 && (
              <Button
                type="link"
                size="small"
                onClick={onClearHistory}
                style={{ padding: 0 }}
              >
                清空
              </Button>
            )}
          </div>

          {recentUploads.length === 0 ? (
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description="暂无最近上传"
              style={{ marginTop: 8 }}
            />
          ) : (
            <List
              size="small"
              dataSource={recentUploads.slice(0, 5)}
              renderItem={(item) => (
                <List.Item
                  style={{
                    padding: '8px 0',
                    cursor: 'pointer',
                    transition: 'background 0.2s',
                  }}
                  onClick={() => onFileClick(item)}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#f5f5f5'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'transparent'
                  }}
                >
                  <List.Item.Meta
                    avatar={
                      <FileOutlined
                        style={{
                          fontSize: 20,
                          color: item.media_type === 'image' ? '#52c41a' : '#1890ff',
                        }}
                      />
                    }
                    title={
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 6,
                          fontSize: 13,
                        }}
                      >
                        <Tooltip title={item.title}>
                          <span
                            style={{
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                              maxWidth: 150,
                              display: 'inline-block',
                            }}
                          >
                            {item.title}
                          </span>
                        </Tooltip>
                        {getFileTypeTag(item)}
                      </div>
                    }
                    description={
                      <div style={{ fontSize: 12, color: '#8c8c8c' }}>
                        {formatSize(item.file_size)} • {formatTime(new Date(item.created_at).getTime())}
                      </div>
                    }
                  />
                  <Button
                    type="text"
                    size="small"
                    icon={<EyeOutlined />}
                    onClick={(e) => {
                      e.stopPropagation()
                      onFileClick(item)
                    }}
                  />
                </List.Item>
              )}
            />
          )}
        </div>

        {/* 最近访问的文件夹 */}
        <div>
          <div style={{ fontSize: 14, fontWeight: 500, marginBottom: 12 }}>
            <HistoryOutlined style={{ marginRight: 6, color: '#faad14' }} />
            最近访问
          </div>

          {recentFolders.length === 0 ? (
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description="暂无访问记录"
              style={{ marginTop: 8 }}
            />
          ) : (
            <List
              size="small"
              dataSource={recentFolders.slice(0, 5)}
              renderItem={(folder) => (
                <List.Item
                  style={{
                    padding: '8px 0',
                    cursor: 'pointer',
                    transition: 'background 0.2s',
                  }}
                  onClick={() => onFolderClick(folder.id)}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#f5f5f5'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'transparent'
                  }}
                >
                  <List.Item.Meta
                    avatar={<FolderOutlined style={{ fontSize: 20, color: '#faad14' }} />}
                    title={
                      <div style={{ fontSize: 13 }}>
                        {folder.title || '根目录'}
                      </div>
                    }
                    description={
                      <div style={{ fontSize: 12, color: '#8c8c8c' }}>
                        {formatTime(folder.timestamp)}
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </div>
      </Card>
    </div>
  )
}

export default QuickActions
