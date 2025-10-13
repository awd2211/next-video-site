import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  Card,
  Row,
  Col,
  Statistic,
  Spin,
  Alert,
  Select,
  Space,
  Typography,
  Button,
  Divider,
  Tag,
} from 'antd'
import {
  LineChartOutlined,
  EyeOutlined,
  LikeOutlined,
  StarOutlined,
  CommentOutlined,
  ArrowLeftOutlined,
  TrophyOutlined,
} from '@ant-design/icons'
import { Line, Column, Pie } from '@ant-design/charts'
import { useState } from 'react'
import axios from '@/utils/axios'
import { useTranslation } from 'react-i18next'

const { Title, Text } = Typography

const VideoAnalytics = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { t } = useTranslation()
  const [days, setDays] = useState(30)

  // 获取视频分析数据
  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['video-analytics', id, days],
    queryFn: async () => {
      const response = await axios.get(`/api/v1/admin/analytics/videos/${id}/analytics`, {
        params: { days },
      })
      return response.data
    },
    enabled: !!id,
  })

  // 获取质量评分
  const { data: qualityScore, isLoading: scoreLoading } = useQuery({
    queryKey: ['video-quality-score', id],
    queryFn: async () => {
      const response = await axios.get(`/api/v1/admin/analytics/videos/${id}/quality-score`)
      return response.data
    },
    enabled: !!id,
  })

  if (analyticsLoading || scoreLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="加载分析数据..." />
      </div>
    )
  }

  if (!analytics) {
    return (
      <Alert
        message="无法加载数据"
        description="视频分析数据加载失败，请稍后重试"
        type="error"
        showIcon
      />
    )
  }

  // 准备图表数据
  const watchTrendData = analytics.watch_trend || []
  const hourlyData = analytics.time_distribution?.hourly || []
  const weekdayData = analytics.time_distribution?.weekday || []

  // 完播率分布数据
  const completionData = analytics.completion_analysis?.completion_rate_distribution
  const completionChartData = completionData
    ? [
        { range: '0-25%', count: completionData['0-25%'], percent: (completionData['0-25%'] / completionData.total_views) * 100 },
        { range: '25-50%', count: completionData['25-50%'], percent: (completionData['25-50%'] / completionData.total_views) * 100 },
        { range: '50-75%', count: completionData['50-75%'], percent: (completionData['50-75%'] / completionData.total_views) * 100 },
        { range: '75-90%', count: completionData['75-90%'], percent: (completionData['75-90%'] / completionData.total_views) * 100 },
        { range: '90-100%', count: completionData['90-100%'], percent: (completionData['90-100%'] / completionData.total_views) * 100 },
      ]
    : []

  // 质量评分等级颜色
  const getGradeColor = (grade: string) => {
    const colors: Record<string, string> = {
      S: '#722ed1',
      A: '#52c41a',
      B: '#1890ff',
      C: '#faad14',
      D: '#f5222d',
    }
    return colors[grade] || '#d9d9d9'
  }

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/videos')}>
            返回列表
          </Button>
          <Title level={2} style={{ margin: 0 }}>
            视频分析：{analytics.video_title}
          </Title>
        </Space>
        <Select
          value={days}
          onChange={setDays}
          style={{ width: 150 }}
          options={[
            { label: '最近7天', value: 7 },
            { label: '最近30天', value: 30 },
            { label: '最近90天', value: 90 },
            { label: '最近180天', value: 180 },
            { label: '最近1年', value: 365 },
          ]}
        />
      </div>

      {/* 质量评分卡片 */}
      {qualityScore && (
        <Card
          style={{ marginBottom: 24 }}
          bodyStyle={{ padding: '24px' }}
        >
          <Row gutter={24}>
            <Col span={6}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 48, fontWeight: 'bold', color: getGradeColor(qualityScore.quality_score.grade) }}>
                  {qualityScore.quality_score.grade}
                </div>
                <div style={{ fontSize: 24, marginTop: 8 }}>
                  {qualityScore.quality_score.total.toFixed(1)} 分
                </div>
                <Tag color={getGradeColor(qualityScore.quality_score.grade)} style={{ marginTop: 8 }}>
                  {qualityScore.quality_score.grade_text}
                </Tag>
              </div>
            </Col>
            <Col span={18}>
              <Title level={4}>质量评分详情</Title>
              <Row gutter={16} style={{ marginTop: 16 }}>
                <Col span={8}>
                  <Statistic
                    title="技术质量"
                    value={qualityScore.quality_score.breakdown.technical}
                    suffix="/ 40"
                    valueStyle={{ color: '#0073bb' }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="元数据完整度"
                    value={qualityScore.quality_score.breakdown.metadata}
                    suffix="/ 30"
                    valueStyle={{ color: '#1d8102' }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="用户互动"
                    value={qualityScore.quality_score.breakdown.engagement}
                    suffix="/ 30"
                    valueStyle={{ color: '#ff9900' }}
                  />
                </Col>
              </Row>
              {qualityScore.suggestions && qualityScore.suggestions.length > 0 && (
                <div style={{ marginTop: 16 }}>
                  <Text strong>改进建议：</Text>
                  <ul style={{ marginTop: 8 }}>
                    {qualityScore.suggestions.map((suggestion: any, idx: number) => (
                      <li key={idx}>
                        {suggestion.message}
                        <Tag color="green" style={{ marginLeft: 8 }}>
                          {suggestion.potential_gain}
                        </Tag>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </Col>
          </Row>
        </Card>
      )}

      {/* 基础统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总观看数"
              value={analytics.basic_stats.total_views}
              prefix={<EyeOutlined style={{ color: '#0073bb' }} />}
              valueStyle={{ color: '#0073bb' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="点赞数"
              value={analytics.basic_stats.like_count}
              prefix={<LikeOutlined style={{ color: '#ff4d4f' }} />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="收藏数"
              value={analytics.basic_stats.favorite_count}
              prefix={<StarOutlined style={{ color: '#faad14' }} />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="评论数"
              value={analytics.basic_stats.comment_count}
              prefix={<CommentOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 观看趋势 */}
      <Card title="观看趋势" style={{ marginBottom: 24 }} extra={<LineChartOutlined />}>
        <Line
          data={watchTrendData}
          xField="date"
          yField="views"
          smooth
          animation={{
            appear: {
              animation: 'path-in',
              duration: 1000,
            },
          }}
          color="#0073bb"
          height={300}
          yAxis={{
            label: {
              formatter: (v) => `${Number(v).toLocaleString()}`,
            },
          }}
          tooltip={{
            formatter: (datum) => ({
              name: '观看数',
              value: datum.views.toLocaleString(),
            }),
          }}
        />
      </Card>

      {/* 完播率分析 */}
      {completionChartData.length > 0 && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col xs={24} lg={16}>
            <Card title="完播率分布">
              <Column
                data={completionChartData}
                xField="range"
                yField="count"
                label={{
                  position: 'top',
                  style: {
                    fill: '#000',
                    opacity: 0.6,
                  },
                  formatter: (datum) => datum.count.toLocaleString(),
                }}
                color={(datum) => {
                  const colors = ['#f5222d', '#faad14', '#1890ff', '#52c41a', '#722ed1']
                  return colors[completionChartData.findIndex(d => d.range === datum.range)] || '#d9d9d9'
                }}
                height={300}
              />
            </Card>
          </Col>
          <Col xs={24} lg={8}>
            <Card title="完播率概览">
              <Statistic
                title="平均完播率"
                value={analytics.completion_analysis.average_completion_percentage}
                suffix="%"
                precision={1}
                valueStyle={{ color: '#0073bb', fontSize: 32 }}
                prefix={<TrophyOutlined />}
              />
              <Divider />
              <div>
                <Text type="secondary">完整观看（90-100%）</Text>
                <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                  {completionData['90-100%'].toLocaleString()}
                </div>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  占总观看的 {((completionData['90-100%'] / completionData.total_views) * 100).toFixed(1)}%
                </Text>
              </div>
            </Card>
          </Col>
        </Row>
      )}

      {/* 时段分布 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="24小时观看分布">
            <Column
              data={hourlyData}
              xField="hour"
              yField="views"
              color="#1890ff"
              height={250}
              xAxis={{
                label: {
                  formatter: (v) => `${v}:00`,
                },
              }}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="星期观看分布">
            <Column
              data={weekdayData}
              xField="weekday"
              yField="views"
              color="#52c41a"
              height={250}
              label={{
                position: 'top',
              }}
            />
          </Card>
        </Col>
      </Row>

      {/* 互动指标 */}
      {analytics.engagement_metrics && (
        <Card title="互动指标">
          <Row gutter={16}>
            <Col span={6}>
              <Statistic
                title="独立观众"
                value={analytics.engagement_metrics.total_unique_viewers}
                suffix="人"
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="评论用户"
                value={analytics.engagement_metrics.comment_users}
                suffix="人"
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="评论转化率"
                value={analytics.engagement_metrics.comment_rate}
                suffix="%"
                precision={2}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="收藏转化率"
                value={analytics.engagement_metrics.favorite_rate}
                suffix="%"
                precision={2}
              />
            </Col>
          </Row>
        </Card>
      )}
    </div>
  )
}

export default VideoAnalytics
