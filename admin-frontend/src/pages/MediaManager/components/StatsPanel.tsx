import React from 'react'
import { Card, Statistic, Row, Col, Progress, Tag } from 'antd'
import {
  FileOutlined,
  FolderOutlined,
  FileImageOutlined,
  VideoCameraOutlined,
  CloudOutlined,
} from '@ant-design/icons'
import type { MediaItem } from '../types'

interface StatsPanelProps {
  data: MediaItem[]
  visible: boolean
}

/**
 * 统计面板组件 - 显示文件统计信息
 */
const StatsPanel: React.FC<StatsPanelProps> = ({ data, visible }) => {
  if (!visible) return null

  // 计算统计数据
  const stats = React.useMemo(() => {
    const folderCount = data.filter((item) => item.is_folder).length
    const fileCount = data.filter((item) => !item.is_folder).length
    const imageCount = data.filter((item) => item.media_type === 'image').length
    const videoCount = data.filter((item) => item.media_type === 'video').length

    // 计算总大小（仅文件）
    const totalSize = data
      .filter((item) => !item.is_folder)
      .reduce((sum, item) => sum + (item.file_size || 0), 0)

    return {
      folderCount,
      fileCount,
      imageCount,
      videoCount,
      totalSize,
      totalCount: data.length,
    }
  }, [data])

  // 格式化文件大小
  const formatSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
  }

  // 计算文件类型占比
  const imagePercent = stats.fileCount > 0 ? (stats.imageCount / stats.fileCount) * 100 : 0
  const videoPercent = stats.fileCount > 0 ? (stats.videoCount / stats.fileCount) * 100 : 0

  return (
    <div style={{ padding: '16px 0' }}>
      <Card size="small" title="文件统计" bordered={false}>
        <Row gutter={16}>
          <Col span={8}>
            <Statistic
              title="总项目"
              value={stats.totalCount}
              prefix={<FileOutlined />}
              valueStyle={{ fontSize: 20 }}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="文件夹"
              value={stats.folderCount}
              prefix={<FolderOutlined />}
              valueStyle={{ fontSize: 20, color: '#faad14' }}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="文件"
              value={stats.fileCount}
              prefix={<FileOutlined />}
              valueStyle={{ fontSize: 20, color: '#1890ff' }}
            />
          </Col>
        </Row>

        <div style={{ marginTop: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <span style={{ fontSize: 14, color: '#8c8c8c' }}>
              <CloudOutlined /> 存储占用
            </span>
            <span style={{ fontSize: 16, fontWeight: 500 }}>
              {formatSize(stats.totalSize)}
            </span>
          </div>
        </div>

        {stats.fileCount > 0 && (
          <div style={{ marginTop: 24 }}>
            <div style={{ marginBottom: 8, fontSize: 14, color: '#8c8c8c' }}>
              文件类型分布
            </div>

            <div style={{ marginBottom: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <span>
                  <FileImageOutlined style={{ color: '#52c41a' }} /> 图片
                  <Tag color="green" style={{ marginLeft: 8 }}>{stats.imageCount}</Tag>
                </span>
                <span style={{ color: '#8c8c8c' }}>{imagePercent.toFixed(1)}%</span>
              </div>
              <Progress
                percent={imagePercent}
                showInfo={false}
                strokeColor="#52c41a"
                size="small"
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <span>
                  <VideoCameraOutlined style={{ color: '#1890ff' }} /> 视频
                  <Tag color="blue" style={{ marginLeft: 8 }}>{stats.videoCount}</Tag>
                </span>
                <span style={{ color: '#8c8c8c' }}>{videoPercent.toFixed(1)}%</span>
              </div>
              <Progress
                percent={videoPercent}
                showInfo={false}
                strokeColor="#1890ff"
                size="small"
              />
            </div>
          </div>
        )}
      </Card>
    </div>
  )
}

export default StatsPanel
