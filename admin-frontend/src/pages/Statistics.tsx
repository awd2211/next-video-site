import { useQuery } from '@tanstack/react-query'
import { Card, Row, Col, Statistic, Spin, Empty, Typography, DatePicker, Space } from 'antd'
import {
  UserOutlined,
  VideoCameraOutlined,
  CommentOutlined,
  EyeOutlined,
  RiseOutlined,
} from '@ant-design/icons'
import { Line, Column, Pie } from '@ant-design/charts'
import axios from '@/utils/axios'
import { useState } from 'react'
import dayjs, { Dayjs } from 'dayjs'

const { Title } = Typography
const { RangePicker } = DatePicker

const Statistics = () => {
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs]>([
    dayjs().subtract(30, 'days'),
    dayjs(),
  ])

  // Fetch overview statistics
  const { data: overviewStats, isLoading: overviewLoading } = useQuery({
    queryKey: ['stats-overview'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/stats/overview')
      return response.data
    },
  })

  // Fetch trend data
  const { data: trendData, isLoading: trendLoading } = useQuery({
    queryKey: ['stats-trends', dateRange],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/stats/trends', {
        params: {
          start_date: dateRange[0].format('YYYY-MM-DD'),
          end_date: dateRange[1].format('YYYY-MM-DD'),
        },
      })
      return response.data
    },
  })

  // Fetch video types distribution
  const { data: videoTypes, isLoading: videoTypesLoading } = useQuery({
    queryKey: ['stats-video-types'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/stats/video-types')
      return response.data
    },
  })

  // Fetch top videos
  const { data: topVideos, isLoading: topVideosLoading } = useQuery({
    queryKey: ['stats-top-videos'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/stats/top-videos', {
        params: { limit: 10 },
      })
      return response.data
    },
  })

  const isLoading = overviewLoading || trendLoading || videoTypesLoading || topVideosLoading

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="Loading statistics..." />
      </div>
    )
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={2} style={{ margin: 0 }}>
          数据统计
        </Title>
        <Space>
          <span>时间范围：</span>
          <RangePicker
            value={dateRange}
            onChange={(dates) => {
              if (dates && dates[0] && dates[1]) {
                setDateRange([dates[0], dates[1]])
              }
            }}
            format="YYYY-MM-DD"
          />
        </Space>
      </div>

      {/* Overview Statistics Cards - AWS Style */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总用户数"
              value={overviewStats?.total_users || 0}
              prefix={<UserOutlined style={{ color: '#0073bb', fontSize: 24 }} />}
              valueStyle={{ color: '#0073bb' }}
              suffix={
                overviewStats?.user_growth_rate ? (
                  <span style={{ fontSize: 14, color: '#1d8102' }}>
                    <RiseOutlined /> {overviewStats.user_growth_rate}%
                  </span>
                ) : null
              }
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总视频数"
              value={overviewStats?.total_videos || 0}
              prefix={<VideoCameraOutlined style={{ color: '#1d8102', fontSize: 24 }} />}
              valueStyle={{ color: '#1d8102' }}
              suffix={
                overviewStats?.video_growth_rate ? (
                  <span style={{ fontSize: 14, color: '#1d8102' }}>
                    <RiseOutlined /> {overviewStats.video_growth_rate}%
                  </span>
                ) : null
              }
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总评论数"
              value={overviewStats?.total_comments || 0}
              prefix={<CommentOutlined style={{ color: '#ff9900', fontSize: 24 }} />}
              valueStyle={{ color: '#ff9900' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总播放量"
              value={overviewStats?.total_views || 0}
              prefix={<EyeOutlined style={{ color: '#d13212', fontSize: 24 }} />}
              valueStyle={{ color: '#d13212' }}
              formatter={(value) => `${Number(value).toLocaleString()}`}
            />
          </Card>
        </Col>
      </Row>

      {/* Trend Charts */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={16}>
          <Card title="数据增长趋势" extra={<span style={{ fontSize: 12, color: '#999' }}>近30天</span>}>
            {trendData?.combined && trendData.combined.length > 0 ? (
              <Line
                data={trendData.combined}
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
                color={['#0073bb', '#1d8102', '#ff9900']}
                height={300}
                legend={{
                  position: 'top-right',
                }}
                tooltip={{
                  shared: true,
                  showCrosshairs: true,
                }}
              />
            ) : (
              <Empty description="暂无趋势数据" style={{ padding: '60px 0' }} />
            )}
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="视频类型分布">
            {videoTypes && videoTypes.length > 0 ? (
              <Pie
                data={videoTypes}
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
                    content: videoTypes.reduce((sum: number, item: any) => sum + item.count, 0).toString(),
                  },
                }}
                height={300}
                legend={{
                  position: 'bottom',
                }}
              />
            ) : (
              <Empty description="暂无数据" style={{ padding: '60px 0' }} />
            )}
          </Card>
        </Col>
      </Row>

      {/* Top Videos */}
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card title="热门视频 TOP 10">
            {topVideos && topVideos.length > 0 ? (
              <Column
                data={topVideos}
                xField="title"
                yField="views"
                seriesField="title"
                legend={false}
                color="#0073bb"
                label={{
                  position: 'top',
                  style: {
                    fill: '#37352f',
                    opacity: 0.8,
                  },
                  formatter: (datum: any) => datum.views.toLocaleString(),
                }}
                xAxis={{
                  label: {
                    autoRotate: true,
                    autoHide: true,
                    style: {
                      fontSize: 11,
                    },
                  },
                }}
                yAxis={{
                  label: {
                    formatter: (v: string) => Number(v).toLocaleString(),
                  },
                }}
                height={350}
                tooltip={{
                  formatter: (datum: any) => {
                    return {
                      name: '播放量',
                      value: datum.views.toLocaleString(),
                    }
                  },
                }}
              />
            ) : (
              <Empty description="暂无数据" style={{ padding: '60px 0' }} />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Statistics
