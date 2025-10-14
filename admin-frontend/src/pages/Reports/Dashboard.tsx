import React, { useState } from 'react'
import {
  Card,
  Row,
  Col,
  Select,
  Button,
  Statistic,
  Space,
  Alert,
  Spin,
  Typography,
  Table,
  message,
  Divider,
  Tag,
} from 'antd'
import {
  UserOutlined,
  VideoCameraOutlined,
  CrownOutlined,
  DownloadOutlined,
  EyeOutlined,
  LikeOutlined,
  StarOutlined,
  CommentOutlined,
  TrophyOutlined,
} from '@ant-design/icons'
import { useQuery } from '@tanstack/react-query'
import { Line, Column, Pie } from '@ant-design/charts'
import { reportsService } from '@/services/reports'
import { useTranslation } from 'react-i18next'
import dayjs from 'dayjs'
import '@/styles/page-layout.css'

const { Title, Text } = Typography
const { Option } = Select

const ReportsDashboard: React.FC = () => {
  const { t } = useTranslation()
  const [reportType, setReportType] = useState<string>('user-activity')
  const [days, setDays] = useState<number>(30)
  const [topLimit, setTopLimit] = useState<number>(20)
  const [topVideosPageSize, setTopVideosPageSize] = useState(20)
  const [exporting, setExporting] = useState(false)

  // Fetch available report types
  const { data: reportTypes } = useQuery({
    queryKey: ['report-types'],
    queryFn: reportsService.getReportTypes,
  })

  // Fetch user activity report
  const { data: userActivity, isLoading: loadingUserActivity } = useQuery({
    queryKey: ['user-activity-report', days],
    queryFn: () => reportsService.getUserActivityReport(days),
    enabled: reportType === 'user-activity',
  })

  // Fetch content performance report
  const { data: contentPerformance, isLoading: loadingContent } = useQuery({
    queryKey: ['content-performance-report', days, topLimit],
    queryFn: () => reportsService.getContentPerformanceReport(days, topLimit),
    enabled: reportType === 'content-performance',
  })

  // Fetch VIP subscription report
  const { data: vipSubscription, isLoading: loadingVIP } = useQuery({
    queryKey: ['vip-subscription-report', days],
    queryFn: () => reportsService.getVIPSubscriptionReport(days),
    enabled: reportType === 'vip-subscription',
  })

  const handleExport = async () => {
    setExporting(true)
    try {
      await reportsService.exportExcel(reportType, days)
      message.success(t('common.exportSuccess') || '导出成功')
    } catch (error) {
      message.error(t('common.exportFailed') || '导出失败')
    } finally {
      setExporting(false)
    }
  }

  const isLoading = loadingUserActivity || loadingContent || loadingVIP

  // Render User Activity Report
  const renderUserActivityReport = () => {
    if (!userActivity) return null

    const trendConfig = {
      data: userActivity.user_trend,
      xField: 'date',
      yField: 'count',
      smooth: true,
      animation: {
        appear: {
          animation: 'path-in',
          duration: 1000,
        },
      },
      point: {
        size: 3,
        shape: 'circle',
      },
      xAxis: {
        type: 'time',
        label: {
          formatter: (v: string) => dayjs(v).format('MM/DD'),
        },
      },
    }

    return (
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Summary Cards */}
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title={t('reports.totalUsers') || '总用户数'}
                value={userActivity.summary.total_users}
                prefix={<UserOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title={t('reports.newUsers') || '新增用户'}
                value={userActivity.summary.new_users}
                prefix={<UserOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title={t('reports.activeUsers') || '活跃用户'}
                value={userActivity.summary.active_users}
                prefix={<UserOutlined />}
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title={t('reports.activeRate') || '活跃率'}
                value={userActivity.summary.active_rate}
                suffix="%"
                precision={2}
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
        </Row>

        {/* User Trend Chart */}
        <Card title={t('reports.userTrend') || '用户增长趋势'}>
          <Line {...trendConfig} />
        </Card>

        {/* Behavior Stats */}
        <Card title={t('reports.behaviorStats') || '用户行为统计'}>
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} lg={6}>
              <Statistic
                title={t('reports.totalWatches') || '总观看次数'}
                value={userActivity.behavior_stats.total_watches}
                prefix={<EyeOutlined />}
              />
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Statistic
                title={t('reports.totalComments') || '总评论数'}
                value={userActivity.behavior_stats.total_comments}
                prefix={<CommentOutlined />}
              />
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Statistic
                title={t('reports.totalFavorites') || '总收藏数'}
                value={userActivity.behavior_stats.total_favorites}
                prefix={<StarOutlined />}
              />
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Statistic
                title={t('reports.avgWatchesPerUser') || '人均观看'}
                value={userActivity.behavior_stats.avg_watches_per_user}
                precision={2}
                prefix={<EyeOutlined />}
              />
            </Col>
          </Row>
        </Card>
      </Space>
    )
  }

  // Render Content Performance Report
  const renderContentPerformanceReport = () => {
    if (!contentPerformance) return null

    const trendConfig = {
      data: contentPerformance.video_trend,
      xField: 'date',
      yField: 'count',
      columnStyle: {
        radius: [4, 4, 0, 0],
      },
      xAxis: {
        label: {
          formatter: (v: string) => dayjs(v).format('MM/DD'),
        },
      },
    }

    const typeDistConfig = {
      data: contentPerformance.type_distribution,
      angleField: 'count',
      colorField: 'type',
      radius: 0.8,
      label: {
        type: 'outer',
      },
      interactions: [{ type: 'element-active' }],
    }

    const topVideosColumns = [
      {
        title: t('common.rank') || '排名',
        key: 'rank',
        width: 60,
        render: (_: any, __: any, index: number) => (
          <Space>
            {index < 3 && <TrophyOutlined style={{ color: ['#FFD700', '#C0C0C0', '#CD7F32'][index] }} />}
            <Text strong>{index + 1}</Text>
          </Space>
        ),
      },
      {
        title: t('video.title') || '标题',
        dataIndex: 'title',
        key: 'title',
        ellipsis: true,
      },
      {
        title: t('video.type') || '类型',
        dataIndex: 'video_type',
        key: 'video_type',
        width: 100,
        render: (type: string) => <Tag>{type || 'N/A'}</Tag>,
      },
      {
        title: t('video.views') || '观看数',
        dataIndex: 'views',
        key: 'views',
        width: 100,
        sorter: (a: any, b: any) => a.views - b.views,
      },
      {
        title: t('video.likes') || '点赞数',
        dataIndex: 'likes',
        key: 'likes',
        width: 100,
        sorter: (a: any, b: any) => a.likes - b.likes,
      },
      {
        title: t('video.favorites') || '收藏数',
        dataIndex: 'favorites',
        key: 'favorites',
        width: 100,
        sorter: (a: any, b: any) => a.favorites - b.favorites,
      },
      {
        title: t('video.rating') || '评分',
        dataIndex: 'rating',
        key: 'rating',
        width: 100,
        render: (rating: number) => rating.toFixed(1),
        sorter: (a: any, b: any) => a.rating - b.rating,
      },
    ]

    return (
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Summary Cards */}
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title={t('reports.totalVideos') || '总视频数'}
                value={contentPerformance.summary.total_videos}
                prefix={<VideoCameraOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title={t('reports.newVideos') || '新增视频'}
                value={contentPerformance.summary.new_videos}
                prefix={<VideoCameraOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title={t('reports.totalViews') || '总观看量'}
                value={contentPerformance.summary.total_views}
                prefix={<EyeOutlined />}
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title={t('reports.totalLikes') || '总点赞数'}
                value={contentPerformance.summary.total_likes}
                prefix={<LikeOutlined />}
                valueStyle={{ color: '#f5222d' }}
              />
            </Card>
          </Col>
        </Row>

        {/* Video Trend Chart */}
        <Card title={t('reports.videoTrend') || '视频发布趋势'}>
          <Column {...trendConfig} />
        </Card>

        {/* Top Videos Table */}
        <Card
          title={
            <Space>
              <Text>{t('reports.topVideos') || '热门视频排行'}</Text>
              <Select
                value={topLimit}
                onChange={setTopLimit}
                style={{ width: 120 }}
                size="small"
              >
                <Option value={10}>TOP 10</Option>
                <Option value={20}>TOP 20</Option>
                <Option value={50}>TOP 50</Option>
              </Select>
            </Space>
          }
        >
          <Table
            dataSource={contentPerformance.top_videos}
            columns={topVideosColumns}
            rowKey="id"
            pagination={{
              pageSize: topVideosPageSize,
              onShowSizeChange: (current, size) => setTopVideosPageSize(size),
              showSizeChanger: true,
              pageSizeOptions: ['10', '20', '50', '100'],
              showQuickJumper: true,
              showTotal: (total) => t('common.total', { count: total }),
            }}
          />
        </Card>

        {/* Type Distribution Chart */}
        <Card title={t('reports.typeDistribution') || '视频类型分布'}>
          <Pie {...typeDistConfig} />
        </Card>
      </Space>
    )
  }

  // Render VIP Subscription Report
  const renderVIPSubscriptionReport = () => {
    if (!vipSubscription) return null

    return (
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Alerts */}
        {vipSubscription.alerts.filter(Boolean).length > 0 && (
          <Alert
            message={t('reports.vipAlerts') || 'VIP订阅提醒'}
            description={
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                {vipSubscription.alerts.filter(Boolean).map((alert, index) => (
                  <li key={index}>{alert}</li>
                ))}
              </ul>
            }
            type="warning"
            showIcon
          />
        )}

        {/* Summary Cards */}
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title={t('reports.totalVIP') || '当前VIP用户'}
                value={vipSubscription.summary.total_vip}
                prefix={<CrownOutlined />}
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title={t('reports.newVIP') || '新增VIP'}
                value={vipSubscription.summary.new_vip}
                prefix={<CrownOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title={t('reports.expiringSoon') || '即将到期'}
                value={vipSubscription.summary.expiring_soon}
                prefix={<CrownOutlined />}
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title={t('reports.expired') || '已过期'}
                value={vipSubscription.summary.expired}
                prefix={<CrownOutlined />}
                valueStyle={{ color: '#8c8c8c' }}
              />
            </Card>
          </Col>
        </Row>

        {/* VIP Analysis */}
        <Card title={t('reports.vipAnalysis') || 'VIP订阅分析'}>
          <Row gutter={[16, 16]}>
            <Col span={24}>
              <Divider orientation="left">{t('reports.vipStatus') || 'VIP状态概览'}</Divider>
              <Space size="large">
                <Statistic
                  title={t('reports.vipConversionRate') || 'VIP转化率'}
                  value={
                    vipSubscription.summary.total_vip > 0
                      ? ((vipSubscription.summary.new_vip / vipSubscription.summary.total_vip) *
                          100).toFixed(2)
                      : 0
                  }
                  suffix="%"
                />
                <Statistic
                  title={t('reports.expiringRate') || '到期风险率'}
                  value={
                    vipSubscription.summary.total_vip > 0
                      ? ((vipSubscription.summary.expiring_soon /
                          vipSubscription.summary.total_vip) *
                          100).toFixed(2)
                      : 0
                  }
                  suffix="%"
                />
              </Space>
            </Col>
          </Row>
        </Card>
      </Space>
    )
  }

  return (
    <div className="page-container">
      {/* Page Header */}
      <div className="page-header">
        <div className="page-header-content">
          <div className="page-header-left">
            <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 600 }}>
              {t('menu.reports') || '数据报表'}
            </h2>
            <Text type="secondary" style={{ marginLeft: 16 }}>
              {t('reports.description') || '查看系统运营数据和分析报表'}
            </Text>
          </div>
          <div className="page-header-right">
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={handleExport}
              loading={exporting}
            >
              {t('common.export') || '导出Excel'}
            </Button>
          </div>
        </div>
      </div>

      {/* Page Content */}
      <div className="page-content">
        {/* Filters */}
        <Card style={{ marginBottom: 16 }}>
          <Row gutter={16} align="middle">
          <Col>
            <Space>
              <Text strong>{t('reports.reportType') || '报表类型'}:</Text>
              <Select
                value={reportType}
                onChange={setReportType}
                style={{ width: 200 }}
              >
                {reportTypes?.map((type) => (
                  <Option key={type.type} value={type.type}>
                    {type.name}
                  </Option>
                ))}
              </Select>
            </Space>
          </Col>
          <Col>
            <Space>
              <Text strong>{t('reports.timePeriod') || '时间范围'}:</Text>
              <Select value={days} onChange={setDays} style={{ width: 120 }}>
                <Option value={7}>7 {t('common.days') || '天'}</Option>
                <Option value={30}>30 {t('common.days') || '天'}</Option>
                <Option value={90}>90 {t('common.days') || '天'}</Option>
                <Option value={180}>180 {t('common.days') || '天'}</Option>
                <Option value={365}>365 {t('common.days') || '天'}</Option>
              </Select>
            </Space>
          </Col>
        </Row>
        </Card>

        {/* Report Content */}
        <Spin spinning={isLoading}>
          {reportType === 'user-activity' && renderUserActivityReport()}
          {reportType === 'content-performance' && renderContentPerformanceReport()}
          {reportType === 'vip-subscription' && renderVIPSubscriptionReport()}
        </Spin>
      </div>
    </div>
  )
}

export default ReportsDashboard
