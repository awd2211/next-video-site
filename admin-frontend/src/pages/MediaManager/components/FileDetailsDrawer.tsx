/**
 * FileDetailsDrawer - 文件详情侧边抽屉
 * 显示完整的文件信息、预览、操作按钮
 */

import React, { useState } from 'react'
import { Drawer, Descriptions, Image, Tag, Button, Space, Typography, Divider, message, Card } from 'antd'
import {
  FileOutlined,
  FolderOutlined,
  DownloadOutlined,
  DeleteOutlined,
  EditOutlined,
  CopyOutlined,
  EyeOutlined,
  ClockCircleOutlined,
  TagsOutlined,
  FileImageOutlined,
  VideoCameraOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons'
import type { MediaItem } from '../types'

const { Text, Title, Paragraph } = Typography

interface FileDetailsDrawerProps {
  visible: boolean
  item: MediaItem | null
  onClose: () => void
  onDownload?: (item: MediaItem) => void
  onDelete?: (item: MediaItem) => void
  onRename?: (item: MediaItem) => void
  onOpenTags?: (item: MediaItem) => void
  onNext?: () => void
  onPrev?: () => void
  hasNext?: boolean
  hasPrev?: boolean
}

const FileDetailsDrawer: React.FC<FileDetailsDrawerProps> = ({
  visible,
  item,
  onClose,
  onDownload,
  onDelete,
  onRename,
  onOpenTags,
  onNext,
  onPrev,
  hasNext,
  hasPrev,
}) => {
  const [copying, setCopying] = useState(false)

  if (!item) return null

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
  }

  // 格式化日期
  const formatDate = (date: string): string => {
    return new Date(date).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  // 格式化时长
  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)

    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  // 复制 URL
  const handleCopyUrl = async () => {
    setCopying(true)
    try {
      await navigator.clipboard.writeText(item.url)
      message.success('链接已复制到剪贴板')
    } catch (error) {
      message.error('复制失败')
    } finally {
      setCopying(false)
    }
  }

  // 获取文件图标
  const getFileIcon = () => {
    if (item.is_folder) {
      return <FolderOutlined style={{ fontSize: 48, color: '#faad14' }} />
    }
    if (item.media_type === 'image') {
      return <FileImageOutlined style={{ fontSize: 48, color: '#52c41a' }} />
    }
    if (item.media_type === 'video') {
      return <VideoCameraOutlined style={{ fontSize: 48, color: '#1890ff' }} />
    }
    return <FileOutlined style={{ fontSize: 48, color: '#8c8c8c' }} />
  }

  // 解析标签
  const tags = item.tags
    ? item.tags
        .split(',')
        .map((tag) => tag.trim())
        .filter(Boolean)
    : []

  return (
    <Drawer
      title={
        <Space>
          <InfoCircleOutlined />
          文件详情
        </Space>
      }
      placement="right"
      width={480}
      onClose={onClose}
      open={visible}
      styles={{
        body: { padding: 0 },
      }}
    >
      {/* 预览区域 */}
      <div style={{ padding: '24px 24px 16px', background: '#fafafa', borderBottom: '1px solid #f0f0f0' }}>
        {item.is_folder ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            {getFileIcon()}
            <Title level={4} style={{ marginTop: 16, marginBottom: 0 }}>
              {item.title}
            </Title>
          </div>
        ) : item.media_type === 'image' ? (
          <div style={{ textAlign: 'center' }}>
            <Image
              src={item.url}
              alt={item.title}
              style={{ maxWidth: '100%', maxHeight: 300, objectFit: 'contain' }}
              preview={{
                mask: (
                  <div>
                    <EyeOutlined style={{ marginRight: 8 }} />
                    点击预览
                  </div>
                ),
              }}
            />
          </div>
        ) : item.media_type === 'video' ? (
          <div style={{ textAlign: 'center' }}>
            <video
              src={item.url}
              controls
              style={{ maxWidth: '100%', maxHeight: 300, background: '#000' }}
              preload="metadata"
            />
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            {getFileIcon()}
          </div>
        )}

        {/* 导航按钮 */}
        {(hasNext || hasPrev) && (
          <div style={{ marginTop: 16, display: 'flex', justifyContent: 'space-between' }}>
            <Button
              disabled={!hasPrev}
              onClick={onPrev}
              icon={<span>←</span>}
            >
              上一个
            </Button>
            <Button
              disabled={!hasNext}
              onClick={onNext}
              icon={<span>→</span>}
            >
              下一个
            </Button>
          </div>
        )}
      </div>

      {/* 操作按钮区域 */}
      <div style={{ padding: '16px 24px', borderBottom: '1px solid #f0f0f0' }}>
        <Space wrap style={{ width: '100%', justifyContent: 'center' }}>
          {!item.is_folder && onDownload && (
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={() => onDownload(item)}
            >
              下载
            </Button>
          )}
          {onRename && (
            <Button
              icon={<EditOutlined />}
              onClick={() => onRename(item)}
            >
              重命名
            </Button>
          )}
          {!item.is_folder && (
            <Button
              icon={<CopyOutlined />}
              onClick={handleCopyUrl}
              loading={copying}
            >
              复制链接
            </Button>
          )}
          {onOpenTags && !item.is_folder && (
            <Button
              icon={<TagsOutlined />}
              onClick={() => onOpenTags(item)}
            >
              标签
            </Button>
          )}
          {onDelete && (
            <Button
              danger
              icon={<DeleteOutlined />}
              onClick={() => onDelete(item)}
            >
              删除
            </Button>
          )}
        </Space>
      </div>

      {/* 详细信息 */}
      <div style={{ padding: '24px' }}>
        <Descriptions column={1} size="small" labelStyle={{ fontWeight: 600, width: 100 }}>
          <Descriptions.Item label="文件名">
            <Paragraph
              copyable
              style={{ margin: 0, wordBreak: 'break-all' }}
            >
              {item.title}
            </Paragraph>
          </Descriptions.Item>

          <Descriptions.Item label="类型">
            {item.is_folder ? (
              <Tag color="gold">文件夹</Tag>
            ) : item.media_type === 'image' ? (
              <Tag color="green">图片</Tag>
            ) : item.media_type === 'video' ? (
              <Tag color="blue">视频</Tag>
            ) : (
              <Tag>文件</Tag>
            )}
          </Descriptions.Item>

          {!item.is_folder && (
            <Descriptions.Item label="大小">
              <Text>{formatFileSize(item.file_size)}</Text>
            </Descriptions.Item>
          )}

          {item.media_type === 'image' && item.width && item.height && (
            <Descriptions.Item label="尺寸">
              <Text>
                {item.width} × {item.height} 像素
              </Text>
            </Descriptions.Item>
          )}

          {item.media_type === 'video' && item.duration && (
            <Descriptions.Item label="时长">
              <Text>{formatDuration(item.duration)}</Text>
            </Descriptions.Item>
          )}

          {item.media_type === 'video' && item.width && item.height && (
            <Descriptions.Item label="分辨率">
              <Text>
                {item.width} × {item.height}
              </Text>
            </Descriptions.Item>
          )}

          <Descriptions.Item label="创建时间">
            <Space>
              <ClockCircleOutlined />
              <Text>{formatDate(item.created_at)}</Text>
            </Space>
          </Descriptions.Item>

          {item.updated_at && item.updated_at !== item.created_at && (
            <Descriptions.Item label="修改时间">
              <Space>
                <ClockCircleOutlined />
                <Text>{formatDate(item.updated_at)}</Text>
              </Space>
            </Descriptions.Item>
          )}

          <Descriptions.Item label="ID">
            <Text code copyable>
              {item.id}
            </Text>
          </Descriptions.Item>

          {!item.is_folder && (
            <Descriptions.Item label="URL">
              <Paragraph
                copyable
                ellipsis={{ rows: 2, expandable: true }}
                style={{ margin: 0, wordBreak: 'break-all' }}
              >
                {item.url}
              </Paragraph>
            </Descriptions.Item>
          )}
        </Descriptions>

        {/* 标签区域 */}
        {tags.length > 0 && (
          <>
            <Divider style={{ margin: '16px 0' }} />
            <Card size="small" title={<Space><TagsOutlined />标签</Space>}>
              <Space wrap>
                {tags.map((tag) => (
                  <Tag key={tag} color="blue">
                    {tag}
                  </Tag>
                ))}
              </Space>
            </Card>
          </>
        )}
      </div>
    </Drawer>
  )
}

export default FileDetailsDrawer
