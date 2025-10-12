import { useQuery } from '@tanstack/react-query'
import { Card, Row, Col, Statistic, Table, Tag, Space, Typography, Skeleton, Grid } from 'antd'
import {
  UserOutlined,
  VideoCameraOutlined,
  CommentOutlined,
  EyeOutlined,
  RiseOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons'
import { Line, Column, Pie } from '@ant-design/charts'
import { useTranslation } from 'react-i18next'
import axios from '@/utils/axios'

const { Title } = Typography

const Dashboard = () => {
  const { t } = useTranslation()
  const screens = Grid.useBreakpoint()
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['overview-stats'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/stats/overview')
      return response.data
    },
  })

  const { data: recentVideos, isLoading: videosLoading } = useQuery({
    queryKey: ['recent-videos'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/videos?page=1&page_size=5')
      return response.data.items
    },
  })

  const { data: trendData } = useQuery({
    queryKey: ['trend-stats'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/stats/trends')
      return response.data
    },
  })

  const { data: videoTypes } = useQuery({
    queryKey: ['video-types'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/stats/video-types')
      return response.data
    },
  })

  const { data: topVideos } = useQuery({
    queryKey: ['top-videos'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/stats/top-videos')
      return response.data
    },
  })

  const videoColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: '类型',
      dataIndex: 'video_type',
      key: 'video_type',
      width: 100,
      render: (type: string) => {
        const typeMap: Record<string, string> = {
          movie: '电影',
          tv_series: '电视剧',
          anime: '动漫',
          documentary: '纪录片',
        }
        return <Tag color="blue">{typeMap[type] || type}</Tag>
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const statusConfig: Record<string, { color: string; text: string }> = {
          draft: { color: 'default', text: '草稿' },
          published: { color: 'green', text: '已发布' },
          archived: { color: 'orange', text: '已归档' },
        }
        const config = statusConfig[status] || { color: 'default', text: status }
        return <Tag color={config.color}>{config.text}</Tag>
      },
    },
    {
      title: '播放量',
      dataIndex: 'view_count',
      key: 'view_count',
      width: 100,
      render: (count: number) => count?.toLocaleString() || 0,
    },
  ]

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        {t('dashboard.title')}
      </Title>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          {statsLoading ? (
            <Card bordered={false}>
              <Skeleton active paragraph={{ rows: 2 }} />
            </Card>
          ) : (
            <Card bordered={false} style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
              <Statistic
                title={<span style={{ color: 'rgba(255,255,255,0.85)' }}>{t('dashboard.totalUsers')}</span>}
                value={stats?.total_users || 0}
                prefix={<UserOutlined />}
                valueStyle={{ color: '#fff' }}
              />
            </Card>
          )}
        </Col>
        <Col xs={24} sm={12} lg={6}>
          {statsLoading ? (
            <Card bordered={false}>
              <Skeleton active paragraph={{ rows: 2 }} />
            </Card>
          ) : (
            <Card bordered={false} style={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
              <Statistic
                title={<span style={{ color: 'rgba(255,255,255,0.85)' }}>{t('dashboard.totalVideos')}</span>}
                value={stats?.total_videos || 0}
                prefix={<VideoCameraOutlined />}
                valueStyle={{ color: '#fff' }}
              />
            </Card>
          )}
        </Col>
        <Col xs={24} sm={12} lg={6}>
          {statsLoading ? (
            <Card bordered={false}>
              <Skeleton active paragraph={{ rows: 2 }} />
            </Card>
          ) : (
            <Card bordered={false} style={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
              <Statistic
                title={<span style={{ color: 'rgba(255,255,255,0.85)' }}>{t('dashboard.totalComments')}</span>}
                value={stats?.total_comments || 0}
                prefix={<CommentOutlined />}
                valueStyle={{ color: '#fff' }}
              />
            </Card>
          )}
        </Col>
        <Col xs={24} sm={12} lg={6}>
          {statsLoading ? (
            <Card bordered={false}>
              <Skeleton active paragraph={{ rows: 2 }} />
            </Card>
          ) : (
            <Card bordered={false} style={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }}>
              <Statistic
                title={<span style={{ color: 'rgba(255,255,255,0.85)' }}>{t('dashboard.totalViews')}</span>}
                value={stats?.total_views || 0}
                prefix={<EyeOutlined />}
                valueStyle={{ color: '#fff' }}
              />
            </Card>
          )}
        </Col>
      </Row>

      {/* 最近添加的视频 */}
      <Card
        title={
          <Space>
            <FileTextOutlined />
            <span>{t('dashboard.recentVideos')}</span>
          </Space>
        }
        style={{ marginBottom: 24 }}
      >
        <Table
          columns={videoColumns}
          dataSource={recentVideos}
          loading={videosLoading}
          rowKey="id"
          pagination={false}
          size="middle"
          scroll={{ x: screens.xs ? 600 : undefined }}
        />
      </Card>

      {/* 数据趋势图表 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={16}>
          <Card title="数据增长趋势（近30天）">
            <Line
              data={trendData?.combined || []}
              xField="date"
              yField="count"
              seriesField="type"
              smooth
              animation={{
                appear: {
                  animation: 'path-in',
                  duration: 1000,
                },
              }}
              color={['#667eea', '#f093fb', '#4facfe']}
              height={300}
            />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="视频类型分布">
            <Pie
              data={videoTypes || []}
              angleField="count"
              colorField="type"
              radius={0.8}
              innerRadius={0.6}
              label={{
                type: 'outer',
                content: '{name} {percentage}',
              }}
              statistic={{
                title: {
                  content: '总数',
                },
                content: {
                  content: videoTypes?.reduce((sum: number, item: any) => sum + item.count, 0) || 0,
                },
              }}
              height={300}
            />
          </Card>
        </Col>
      </Row>

      {/* 热门视频排行 */}
      <Card title="热门视频 TOP 10" style={{ marginBottom: 24 }}>
        <Column
          data={topVideos || []}
          xField="title"
          yField="views"
          seriesField="title"
          legend={false}
          label={{
            position: 'top',
            style: {
              fill: '#000',
              opacity: 0.6,
            },
          }}
          xAxis={{
            label: {
              autoRotate: true,
              autoHide: false,
              style: {
                fontSize: 10,
              },
            },
          }}
          height={300}
        />
      </Card>

      {/* 快捷操作 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} md={12}>
          <Card
            title="快捷操作"
            extra={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
          >
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <div>
                <a href="/videos/new" style={{ fontSize: 16, fontWeight: 500 }}>
                  ➕ 添加新视频
                </a>
                <div style={{ color: '#8c8c8c', marginTop: 4 }}>快速创建新的视频内容</div>
              </div>
              <div>
                <a href="/users" style={{ fontSize: 16, fontWeight: 500 }}>
                  👥 管理用户
                </a>
                <div style={{ color: '#8c8c8c', marginTop: 4 }}>查看和管理系统用户</div>
              </div>
              <div>
                <a href="/comments" style={{ fontSize: 16, fontWeight: 500 }}>
                  💬 审核评论
                </a>
                <div style={{ color: '#8c8c8c', marginTop: 4 }}>审核用户提交的评论</div>
              </div>
            </Space>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card
            title="系统信息"
            extra={<RiseOutlined style={{ color: '#1890ff' }} />}
          >
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#8c8c8c' }}>数据库状态:</span>
                <Tag color="green">正常</Tag>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#8c8c8c' }}>缓存服务:</span>
                <Tag color="green">运行中</Tag>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#8c8c8c' }}>存储服务:</span>
                <Tag color="green">可用</Tag>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#8c8c8c' }}>API 版本:</span>
                <span>v1.0.0</span>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard
