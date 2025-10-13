import { Modal, Button, Image, Tag, Descriptions, List } from 'antd'
import { EyeOutlined, PlayCircleOutlined } from '@ant-design/icons'
import { useState } from 'react'
import { formatAWSDate, formatAWSNumber } from '@/utils/awsStyleHelpers'

interface SeriesVideo {
  video_id: number
  episode_number: number
  title: string
  poster_url: string | null
  duration: number
  view_count: number
}

interface SeriesPreviewProps {
  series: {
    id: number
    title: string
    description: string | null
    cover_image: string | null
    type: string
    status: string
    total_episodes: number
    total_views: number
    total_favorites: number
    is_featured: boolean
    created_at: string
    videos?: SeriesVideo[]
  }
}

export const SeriesPreviewButton: React.FC<SeriesPreviewProps> = ({ series }) => {
  const [visible, setVisible] = useState(false)

  const getTypeText = (type: string) => {
    const typeMap: Record<string, string> = {
      series: '系列剧',
      collection: '合集',
      franchise: '系列作品',
    }
    return typeMap[type] || type
  }

  const getStatusColor = (status: string) => {
    const colorMap: Record<string, string> = {
      draft: 'default',
      published: 'success',
      archived: 'warning',
    }
    return colorMap[status] || 'default'
  }

  const getStatusText = (status: string) => {
    const textMap: Record<string, string> = {
      draft: '草稿',
      published: '已发布',
      archived: '已归档',
    }
    return textMap[status] || status
  }

  return (
    <>
      <Button
        type="link"
        size="small"
        icon={<EyeOutlined />}
        onClick={() => setVisible(true)}
      >
        预览
      </Button>

      <Modal
        title={<span style={{ fontSize: 18, fontWeight: 600 }}>{series.title}</span>}
        open={visible}
        onCancel={() => setVisible(false)}
        footer={[
          <Button key="close" onClick={() => setVisible(false)}>
            关闭
          </Button>,
        ]}
        width="90%"
        style={{ maxWidth: 1200 }}
      >
        <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
          {/* 左侧：封面图 */}
          <div style={{ flex: '0 0 300px' }}>
            {series.cover_image ? (
              <Image
                src={series.cover_image}
                alt={series.title}
                style={{
                  width: '100%',
                  borderRadius: '8px',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                }}
              />
            ) : (
              <div
                style={{
                  width: '100%',
                  height: '400px',
                  background: '#f0f0f0',
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#999',
                  fontSize: 16,
                }}
              >
                无封面
              </div>
            )}

            {/* 统计信息卡片 */}
            <div
              style={{
                marginTop: '16px',
                padding: '16px',
                background: '#f5f7fa',
                borderRadius: '8px',
              }}
            >
              <div style={{ marginBottom: '12px' }}>
                <span style={{ color: '#787774', fontSize: 14 }}>总集数</span>
                <div style={{ fontSize: 24, fontWeight: 600, color: '#0073bb' }}>
                  {formatAWSNumber(series.total_episodes)}
                </div>
              </div>
              <div style={{ marginBottom: '12px' }}>
                <span style={{ color: '#787774', fontSize: 14 }}>播放量</span>
                <div style={{ fontSize: 20, fontWeight: 600, color: '#1d8102' }}>
                  {formatAWSNumber(series.total_views.toLocaleString())}
                </div>
              </div>
              <div>
                <span style={{ color: '#787774', fontSize: 14 }}>收藏数</span>
                <div style={{ fontSize: 20, fontWeight: 600, color: '#ff9900' }}>
                  {formatAWSNumber(series.total_favorites.toLocaleString())}
                </div>
              </div>
            </div>
          </div>

          {/* 右侧：详细信息 */}
          <div style={{ flex: '1 1 400px' }}>
            {/* 基本信息 */}
            <Descriptions column={2} bordered size="small" style={{ marginBottom: '16px' }}>
              <Descriptions.Item label="类型">
                <Tag color="blue">{getTypeText(series.type)}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                <Tag color={getStatusColor(series.status)}>
                  {getStatusText(series.status)}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="是否推荐">
                {series.is_featured ? (
                  <Tag color="red">推荐</Tag>
                ) : (
                  <span style={{ color: '#999' }}>否</span>
                )}
              </Descriptions.Item>
              <Descriptions.Item label="创建时间">
                {formatAWSDate(series.created_at, 'YYYY-MM-DD HH:mm')}
              </Descriptions.Item>
            </Descriptions>

            {/* 描述 */}
            {series.description && (
              <div style={{ marginBottom: '16px' }}>
                <h4 style={{ marginBottom: '8px', color: '#37352f' }}>简介</h4>
                <div
                  style={{
                    padding: '12px',
                    background: '#fff',
                    border: '1px solid #e9e9e7',
                    borderRadius: '4px',
                    color: '#787774',
                    lineHeight: 1.6,
                  }}
                >
                  {series.description}
                </div>
              </div>
            )}

            {/* 视频列表 */}
            {series.videos && series.videos.length > 0 && (
              <div>
                <h4 style={{ marginBottom: '12px', color: '#37352f' }}>
                  剧集列表 ({series.videos.length}集)
                </h4>
                <List
                  size="small"
                  bordered
                  dataSource={series.videos}
                  style={{ maxHeight: '400px', overflow: 'auto' }}
                  renderItem={(video) => (
                    <List.Item>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', width: '100%' }}>
                        {/* 封面缩略图 */}
                        {video.poster_url ? (
                          <Image
                            src={video.poster_url}
                            width={80}
                            height={45}
                            style={{ objectFit: 'cover', borderRadius: '4px' }}
                          />
                        ) : (
                          <div
                            style={{
                              width: 80,
                              height: 45,
                              background: '#f0f0f0',
                              borderRadius: '4px',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                            }}
                          >
                            <PlayCircleOutlined style={{ fontSize: 20, color: '#999' }} />
                          </div>
                        )}

                        {/* 标题和信息 */}
                        <div style={{ flex: 1 }}>
                          <div style={{ marginBottom: '4px' }}>
                            <Tag color="blue" style={{ marginRight: '8px' }}>
                              第{video.episode_number}集
                            </Tag>
                            <span style={{ fontWeight: 500 }}>{video.title}</span>
                          </div>
                          <div style={{ fontSize: 12, color: '#999' }}>
                            时长: {Math.floor(video.duration / 60)}分钟 | 播放: {formatAWSNumber(video.view_count.toLocaleString())}
                          </div>
                        </div>
                      </div>
                    </List.Item>
                  )}
                />
              </div>
            )}
          </div>
        </div>
      </Modal>
    </>
  )
}

export default SeriesPreviewButton
