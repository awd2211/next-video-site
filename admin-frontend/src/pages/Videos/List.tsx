import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Table,
  Button,
  Space,
  Tag,
  Input,
  Select,
  message,
  Modal,
  Grid,
  Card,
  Row,
  Col,
  Statistic,
  Slider,
  Checkbox,
  Collapse,
  Tooltip,
  Badge,
  InputNumber,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  DownloadOutlined,
  UploadOutlined,
  LineChartOutlined,
  FireOutlined,
  PushpinOutlined,
  StarOutlined,
  ClockCircleOutlined,
  FilterOutlined,
  ThunderboltOutlined,
  TrophyOutlined,
  EyeOutlined,
  CalendarOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useHotkeys } from 'react-hotkeys-hook'
import { useDebounce } from '@/hooks/useDebounce'
import { useTableSort } from '@/hooks/useTableSort'
import { exportToCSV } from '@/utils/exportUtils'
import EmptyState from '@/components/EmptyState'
import VideoPreviewPopover from '@/components/VideoPreviewPopover'
import BatchUploader from '@/components/BatchUploader'
import SchedulePublishModal from '@/components/SchedulePublishModal'
import QualityScoreSlider from '@/components/QualityScoreSlider'
import { useTheme } from '@/contexts/ThemeContext'
import { getTagStyle, getTextColor } from '@/utils/awsColorHelpers'
import videoService from '@/services/videoService'
import '@/styles/page-layout.css'
import dayjs from 'dayjs'

const { Panel } = Collapse

const VideoList = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const screens = Grid.useBreakpoint()
  const { theme } = useTheme()

  // Basic state
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<string>()
  const [selectedRowKeys, setSelectedRowKeys] = useState<number[]>([])
  const [batchUploadVisible, setBatchUploadVisible] = useState(false)

  // 🆕 Operation state
  const [isStandalone, setIsStandalone] = useState<boolean>()
  const [isTrending, setIsTrending] = useState<boolean>()
  const [isPinned, setIsPinned] = useState<boolean>()
  const [isFeatured, setIsFeatured] = useState<boolean>()
  const [qualityScoreMin, setQualityScoreMin] = useState<number>()
  const [scheduledStatus, setScheduledStatus] = useState<'pending' | 'published'>()
  const [filterVisible, setFilterVisible] = useState(false)

  // 🆕 Schedule modal state
  const [scheduleModalVisible, setScheduleModalVisible] = useState(false)
  const [scheduleTargetVideo, setScheduleTargetVideo] = useState<any>(null)

  // 🆕 Quality score modal state
  const [qualityModalVisible, setQualityModalVisible] = useState(false)
  const [qualityTargetVideo, setQualityTargetVideo] = useState<any>(null)
  const [qualityScore, setQualityScore] = useState(0)

  // 🆕 Batch quality score modal
  const [batchQualityModalVisible, setBatchQualityModalVisible] = useState(false)
  const [batchQualityScore, setBatchQualityScore] = useState(0)

  // Debounce search to reduce API calls
  const debouncedSearch = useDebounce(search, 500)

  // Table sorting
  const { handleTableChange, getSortParams } = useTableSort({
    defaultSortBy: 'created_at',
    defaultSortOrder: 'desc',
  })

  // Hotkeys
  useHotkeys(
    'ctrl+n',
    (e) => {
      e.preventDefault()
      navigate('/videos/new')
    },
    { enableOnFormTags: false }
  )

  useHotkeys(
    'ctrl+f',
    (e) => {
      e.preventDefault()
      const searchInput = document.querySelector('input[type="search"]') as HTMLInputElement
      searchInput?.focus()
    },
    { enableOnFormTags: false }
  )

  // 🆕 Fetch dashboard stats
  const { data: dashboardStats } = useQuery({
    queryKey: ['video-dashboard-stats'],
    queryFn: () => videoService.getDashboardStats(),
  })

  // Fetch videos list
  const { data, isLoading, refetch } = useQuery({
    queryKey: [
      'admin-videos',
      page,
      pageSize,
      debouncedSearch,
      status,
      isStandalone,
      isTrending,
      isPinned,
      isFeatured,
      qualityScoreMin,
      scheduledStatus,
      ...Object.values(getSortParams()),
    ],
    queryFn: async () => {
      const response = await videoService.getList({
        page,
        page_size: pageSize,
        search: debouncedSearch,
        status,
        is_standalone: isStandalone,
        is_trending: isTrending,
        is_pinned: isPinned,
        is_featured: isFeatured,
        quality_score_min: qualityScoreMin,
        scheduled_status: scheduledStatus,
        ...getSortParams(),
      })
      return response
    },
    placeholderData: (previousData) => previousData,
  })

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: t('video.confirmDelete'),
      content: t('video.deleteWarning'),
      okText: t('common.delete'),
      okType: 'danger',
      cancelText: t('common.cancel'),
      onOk: async () => {
        try {
          await videoService.getDetail(id) // TODO: Replace with actual delete API
          message.success(t('message.deleteSuccess'))
          refetch()
        } catch (error: any) {
          message.error(error.response?.data?.detail || t('message.failed'))
        }
      },
    })
  }

  // 🆕 Toggle Trending mutation
  const toggleTrendingMutation = useMutation({
    mutationFn: (videoId: number) => videoService.toggleTrending(videoId),
    onSuccess: (_, videoId) => {
      message.success(t('video.operation.operationSuccess'))
      queryClient.invalidateQueries({ queryKey: ['admin-videos'] })
      queryClient.invalidateQueries({ queryKey: ['video-dashboard-stats'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('message.failed'))
    },
  })

  // 🆕 Toggle Pinned mutation
  const togglePinnedMutation = useMutation({
    mutationFn: (videoId: number) => videoService.togglePinned(videoId),
    onSuccess: () => {
      message.success(t('video.operation.operationSuccess'))
      queryClient.invalidateQueries({ queryKey: ['admin-videos'] })
      queryClient.invalidateQueries({ queryKey: ['video-dashboard-stats'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('message.failed'))
    },
  })

  // 🆕 Batch mark trending mutation
  const batchMarkTrendingMutation = useMutation({
    mutationFn: (data: { ids: number[]; value: boolean }) => videoService.batchMarkTrending(data),
    onSuccess: () => {
      message.success(t('video.operation.operationSuccess'))
      setSelectedRowKeys([])
      queryClient.invalidateQueries({ queryKey: ['admin-videos'] })
      queryClient.invalidateQueries({ queryKey: ['video-dashboard-stats'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('message.failed'))
    },
  })

  // 🆕 Batch mark pinned mutation
  const batchMarkPinnedMutation = useMutation({
    mutationFn: (data: { ids: number[]; value: boolean }) => videoService.batchMarkPinned(data),
    onSuccess: () => {
      message.success(t('video.operation.operationSuccess'))
      setSelectedRowKeys([])
      queryClient.invalidateQueries({ queryKey: ['admin-videos'] })
      queryClient.invalidateQueries({ queryKey: ['video-dashboard-stats'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('message.failed'))
    },
  })

  // 🆕 Batch set quality score mutation
  const batchSetQualityMutation = useMutation({
    mutationFn: (data: { ids: number[]; quality_score: number }) =>
      videoService.batchSetQualityScore(data),
    onSuccess: () => {
      message.success(t('video.operation.operationSuccess'))
      setSelectedRowKeys([])
      setBatchQualityModalVisible(false)
      queryClient.invalidateQueries({ queryKey: ['admin-videos'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('message.failed'))
    },
  })

  // 🆕 Schedule publish mutation
  const schedulePublishMutation = useMutation({
    mutationFn: (data: { videoId: number; scheduled_publish_at: string }) =>
      videoService.schedulePublish(data.videoId, { scheduled_publish_at: data.scheduled_publish_at }),
    onSuccess: () => {
      message.success(t('video.operation.scheduleSuccess'))
      setScheduleModalVisible(false)
      setScheduleTargetVideo(null)
      queryClient.invalidateQueries({ queryKey: ['admin-videos'] })
      queryClient.invalidateQueries({ queryKey: ['video-dashboard-stats'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('message.failed'))
    },
  })

  // 🆕 Cancel schedule mutation
  const cancelScheduleMutation = useMutation({
    mutationFn: (videoId: number) => videoService.cancelSchedule(videoId),
    onSuccess: () => {
      message.success(t('video.operation.cancelScheduleSuccess'))
      queryClient.invalidateQueries({ queryKey: ['admin-videos'] })
      queryClient.invalidateQueries({ queryKey: ['video-dashboard-stats'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('message.failed'))
    },
  })

  // 🆕 Batch operation handlers
  const handleBatchMarkTrending = (value: boolean) => {
    if (selectedRowKeys.length === 0) {
      message.warning(t('message.pleaseSelect'))
      return
    }
    Modal.confirm({
      title: value ? t('video.operation.batchMarkTrending') : t('video.operation.batchUnmarkTrending'),
      content: `${t('common.confirm')} ${selectedRowKeys.length} ${t('menu.videos')}?`,
      okText: t('common.confirm'),
      cancelText: t('common.cancel'),
      onOk: () => batchMarkTrendingMutation.mutate({ ids: selectedRowKeys, value }),
    })
  }

  const handleBatchMarkPinned = (value: boolean) => {
    if (selectedRowKeys.length === 0) {
      message.warning(t('message.pleaseSelect'))
      return
    }
    Modal.confirm({
      title: value ? t('video.operation.batchMarkPinned') : t('video.operation.batchUnmarkPinned'),
      content: `${t('common.confirm')} ${selectedRowKeys.length} ${t('menu.videos')}?`,
      okText: t('common.confirm'),
      cancelText: t('common.cancel'),
      onOk: () => batchMarkPinnedMutation.mutate({ ids: selectedRowKeys, value }),
    })
  }

  const handleBatchSetQuality = () => {
    if (selectedRowKeys.length === 0) {
      message.warning(t('message.pleaseSelect'))
      return
    }
    setBatchQualityModalVisible(true)
  }

  // Export to CSV
  const handleExport = () => {
    if (!data?.items || data.items.length === 0) {
      message.warning(t('message.noDataToExport'))
      return
    }

    const exportData = data.items.map((item: any) => ({
      ID: item.id,
      [t('video.title')]: item.title,
      [t('video.type')]: item.video_type,
      [t('video.status')]: item.status,
      [t('video.views')]: item.view_count,
      [t('video.operation.qualityScore')]: item.quality_score,
      [t('video.operation.trending')]: item.is_trending ? 'Yes' : 'No',
      [t('video.operation.pinned')]: item.is_pinned ? 'Yes' : 'No',
      [t('table.createdAt')]: item.created_at,
    }))

    exportToCSV(exportData, 'videos')
    message.success(t('message.exportSuccess'))
  }

  const columns = [
    {
      title: t('table.id'),
      dataIndex: 'id',
      key: 'id',
      width: 80,
      sorter: true,
    },
    {
      title: t('video.title'),
      dataIndex: 'title',
      key: 'title',
      sorter: true,
      render: (title: string, record: any) => (
        <VideoPreviewPopover video={record} hoverDelay={300}>
          <div className="video-preview-trigger" style={{ cursor: 'pointer', padding: '4px 0' }}>
            {title}
          </div>
        </VideoPreviewPopover>
      ),
    },
    {
      title: t('video.type'),
      dataIndex: 'video_type',
      key: 'video_type',
      render: (type: string) => <Tag style={getTagStyle('primary', theme)}>{type}</Tag>,
    },
    {
      title: t('video.status'),
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const getStatusVariant = (status: string) => {
          switch (status.toUpperCase()) {
            case 'PUBLISHED':
              return 'success'
            case 'DRAFT':
              return 'info'
            case 'ARCHIVED':
              return 'warning'
            default:
              return 'neutral'
          }
        }
        return <Tag style={getTagStyle(getStatusVariant(status), theme)}>{status}</Tag>
      },
    },
    // 🆕 Operation Tags Column
    {
      title: t('video.operation.trending') + '/' + t('video.operation.pinned'),
      key: 'operation_tags',
      width: 150,
      render: (_: any, record: any) => (
        <Space size={4}>
          {record.is_trending && (
            <Tooltip title={t('video.operation.trending')}>
              <Tag icon={<FireOutlined />} color="red">
                {t('video.operation.trending')}
              </Tag>
            </Tooltip>
          )}
          {record.is_pinned && (
            <Tooltip title={t('video.operation.pinned')}>
              <Tag icon={<PushpinOutlined />} color="blue">
                {t('video.operation.pinned')}
              </Tag>
            </Tooltip>
          )}
          {record.is_featured && (
            <Tooltip title={t('video.operation.featured')}>
              <Tag icon={<StarOutlined />} color="gold">
                {t('video.operation.featured')}
              </Tag>
            </Tooltip>
          )}
          {record.scheduled_publish_at && new Date(record.scheduled_publish_at) > new Date() && (
            <Tooltip title={`${t('video.operation.scheduled')}: ${dayjs(record.scheduled_publish_at).format('YYYY-MM-DD HH:mm')}`}>
              <Tag icon={<ClockCircleOutlined />} color="orange">
                {t('video.operation.scheduled')}
              </Tag>
            </Tooltip>
          )}
        </Space>
      ),
    },
    // 🆕 Quality Score Column
    {
      title: t('video.operation.qualityScore'),
      dataIndex: 'quality_score',
      key: 'quality_score',
      width: 120,
      sorter: true,
      render: (score: number) => {
        const getScoreColor = (score: number) => {
          if (score === 0) return '#d9d9d9'
          if (score < 30) return '#ff4d4f'
          if (score < 60) return '#faad14'
          if (score < 80) return '#1890ff'
          return '#52c41a'
        }
        return (
          <Badge
            count={score}
            showZero
            style={{ backgroundColor: getScoreColor(score), fontWeight: 'bold' }}
          />
        )
      },
    },
    {
      title: t('video.views'),
      dataIndex: 'view_count',
      key: 'view_count',
      sorter: true,
      render: (count: number) => count?.toLocaleString() || 0,
    },
    {
      title: 'Rating',
      dataIndex: 'average_rating',
      key: 'average_rating',
      sorter: true,
      render: (rating: number) => (
        <span
          style={{
            fontFamily: 'Monaco, Menlo, Consolas, monospace',
            color: getTextColor('primary', theme),
          }}
        >
          {rating?.toFixed(1) || '0.0'}
        </span>
      ),
    },
    // 🆕 Enhanced Actions Column
    {
      title: t('table.actions'),
      key: 'actions',
      width: 280,
      render: (_: any, record: any) => (
        <Space size="small">
          {/* Quick Toggle Buttons */}
          <Tooltip title={record.is_trending ? t('video.operation.unmarkTrending') : t('video.operation.markTrending')}>
            <Button
              size="small"
              type={record.is_trending ? 'primary' : 'default'}
              danger={record.is_trending}
              icon={<FireOutlined />}
              onClick={() => toggleTrendingMutation.mutate(record.id)}
            />
          </Tooltip>
          <Tooltip title={record.is_pinned ? t('video.operation.unmarkPinned') : t('video.operation.markPinned')}>
            <Button
              size="small"
              type={record.is_pinned ? 'primary' : 'default'}
              icon={<PushpinOutlined />}
              onClick={() => togglePinnedMutation.mutate(record.id)}
            />
          </Tooltip>
          <Tooltip title={t('video.operation.schedulePublish')}>
            <Button
              size="small"
              icon={<ClockCircleOutlined />}
              onClick={() => {
                setScheduleTargetVideo(record)
                setScheduleModalVisible(true)
              }}
            />
          </Tooltip>
          <Button
            size="small"
            type="link"
            icon={<LineChartOutlined />}
            onClick={() => navigate(`/videos/${record.id}/analytics`)}
          >
            {t('video.analytics')}
          </Button>
          <Button
            size="small"
            type="link"
            icon={<EditOutlined />}
            onClick={() => navigate(`/videos/${record.id}/edit`)}
          >
            {t('common.edit')}
          </Button>
          <Button
            size="small"
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            {t('common.delete')}
          </Button>
        </Space>
      ),
    },
  ]

  const rowSelection = {
    selectedRowKeys,
    onChange: (keys: React.Key[]) => setSelectedRowKeys(keys as number[]),
  }

  return (
    <div className="page-container">
      {/* 🆕 Dashboard Statistics Cards */}
      {dashboardStats && (
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={12} md={8} lg={6} xl={4}>
            <Card>
              <Statistic
                title={t('video.operation.dashboard.totalVideos')}
                value={dashboardStats.total_videos}
                prefix={<EyeOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6} xl={4}>
            <Card>
              <Statistic
                title={t('video.operation.dashboard.todayNew')}
                value={dashboardStats.today_new}
                prefix={<PlusOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6} xl={4}>
            <Card>
              <Statistic
                title={t('video.operation.dashboard.pendingReview')}
                value={dashboardStats.pending_review}
                prefix={<ClockCircleOutlined />}
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6} xl={4}>
            <Card>
              <Statistic
                title={t('video.operation.dashboard.scheduledCount')}
                value={dashboardStats.scheduled_count}
                prefix={<CalendarOutlined />}
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6} xl={4}>
            <Card>
              <Statistic
                title={t('video.operation.dashboard.trendingCount')}
                value={dashboardStats.trending_count}
                prefix={<FireOutlined />}
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6} xl={4}>
            <Card>
              <Statistic
                title={t('video.operation.dashboard.thisWeekViews')}
                value={dashboardStats.this_week_views}
                prefix={<TrophyOutlined />}
                valueStyle={{ color: '#13c2c2' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* Page Header */}
      <div className="page-header">
        <div className="page-header-content">
          <div className="page-header-left">
            <Input.Search
              placeholder={t('common.search') + ' videos...'}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onSearch={setSearch}
              loading={isLoading && !!debouncedSearch}
              allowClear
              style={{ width: 300 }}
            />
            <Select
              placeholder={t('video.status')}
              style={{ width: 150 }}
              allowClear
              onChange={setStatus}
              options={[
                { label: t('video.draft'), value: 'DRAFT' },
                { label: t('video.published'), value: 'PUBLISHED' },
                { label: t('video.archived'), value: 'ARCHIVED' },
              ]}
            />
            {/* 🆕 Advanced Filter Toggle */}
            <Button
              icon={<FilterOutlined />}
              onClick={() => setFilterVisible(!filterVisible)}
              type={filterVisible ? 'primary' : 'default'}
            >
              {t('video.operation.filter.title')}
            </Button>
          </div>
          <div className="page-header-right">
            <Button icon={<UploadOutlined />} onClick={() => setBatchUploadVisible(true)}>
              {t('video.batchUpload') || '批量上传'}
            </Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/videos/new')}>
              {t('common.add')} Video
            </Button>
          </div>
        </div>
      </div>

      {/* 🆕 Advanced Filter Panel */}
      {filterVisible && (
        <Card style={{ marginBottom: 16 }}>
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} md={8} lg={6}>
              <Checkbox
                checked={isStandalone}
                onChange={(e) => setIsStandalone(e.target.checked ? true : undefined)}
              >
                {t('video.operation.filter.showStandaloneOnly')}
              </Checkbox>
            </Col>
            <Col xs={24} sm={12} md={8} lg={6}>
              <Checkbox
                checked={isTrending}
                onChange={(e) => setIsTrending(e.target.checked ? true : undefined)}
              >
                {t('video.operation.filter.showTrending')}
              </Checkbox>
            </Col>
            <Col xs={24} sm={12} md={8} lg={6}>
              <Checkbox
                checked={isPinned}
                onChange={(e) => setIsPinned(e.target.checked ? true : undefined)}
              >
                {t('video.operation.filter.showPinned')}
              </Checkbox>
            </Col>
            <Col xs={24} sm={12} md={8} lg={6}>
              <Checkbox
                checked={isFeatured}
                onChange={(e) => setIsFeatured(e.target.checked ? true : undefined)}
              >
                {t('video.operation.filter.showFeatured')}
              </Checkbox>
            </Col>
            <Col xs={24} sm={12} md={12}>
              <div>
                <div style={{ marginBottom: 8 }}>{t('video.operation.filter.minQualityScore')}</div>
                <Slider
                  min={0}
                  max={100}
                  value={qualityScoreMin || 0}
                  onChange={setQualityScoreMin}
                  marks={{ 0: '0', 30: '30', 60: '60', 80: '80', 100: '100' }}
                />
              </div>
            </Col>
            <Col xs={24} sm={12} md={8} lg={6}>
              <div>
                <div style={{ marginBottom: 8 }}>{t('video.operation.filter.scheduledStatus')}</div>
                <Select
                  style={{ width: '100%' }}
                  placeholder={t('video.operation.filter.all')}
                  allowClear
                  onChange={setScheduledStatus}
                  options={[
                    { label: t('video.operation.filter.scheduledPending'), value: 'pending' },
                    { label: t('video.operation.filter.scheduledPublished'), value: 'published' },
                  ]}
                />
              </div>
            </Col>
            <Col xs={24}>
              <Button
                onClick={() => {
                  setIsStandalone(undefined)
                  setIsTrending(undefined)
                  setIsPinned(undefined)
                  setIsFeatured(undefined)
                  setQualityScoreMin(undefined)
                  setScheduledStatus(undefined)
                }}
              >
                {t('common.reset')}
              </Button>
            </Col>
          </Row>
        </Card>
      )}

      {/* 🆕 Enhanced Batch operations */}
      {selectedRowKeys.length > 0 && (
        <div className="batch-operations">
          <Space wrap>
            <Button
              icon={<FireOutlined />}
              onClick={() => handleBatchMarkTrending(true)}
              style={{ background: '#fff1f0', borderColor: '#ffa39e', color: '#cf1322' }}
            >
              {t('video.operation.batchMarkTrending')} ({selectedRowKeys.length})
            </Button>
            <Button icon={<FireOutlined />} onClick={() => handleBatchMarkTrending(false)}>
              {t('video.operation.batchUnmarkTrending')} ({selectedRowKeys.length})
            </Button>
            <Button
              icon={<PushpinOutlined />}
              onClick={() => handleBatchMarkPinned(true)}
              type="primary"
            >
              {t('video.operation.batchMarkPinned')} ({selectedRowKeys.length})
            </Button>
            <Button icon={<PushpinOutlined />} onClick={() => handleBatchMarkPinned(false)}>
              {t('video.operation.batchUnmarkPinned')} ({selectedRowKeys.length})
            </Button>
            <Button icon={<ThunderboltOutlined />} onClick={handleBatchSetQuality}>
              {t('video.operation.batchSetQualityScore')} ({selectedRowKeys.length})
            </Button>
            <Button icon={<DownloadOutlined />} onClick={handleExport}>
              {t('video.exportExcel')}
            </Button>
          </Space>
        </div>
      )}

      {/* Page Content */}
      <div className="page-content">
        <div className="table-container">
          <Table
            rowSelection={rowSelection}
            columns={columns}
            dataSource={data?.items}
            loading={isLoading}
            rowKey="id"
            onChange={(pagination, filters, sorter) => handleTableChange(sorter)}
            pagination={{
              current: page,
              pageSize: pageSize,
              total: data?.total,
              onChange: setPage,
              onShowSizeChange: (current, size) => {
                setPageSize(size)
                setPage(1)
              },
              showSizeChanger: true,
              pageSizeOptions: ['10', '20', '50', '100'],
              showTotal: (total) => t('common.total', { count: total }),
              simple: screens.xs,
            }}
            scroll={{ x: screens.xs ? 800 : 1400 }}
            sticky
            locale={{
              emptyText:
                search || status ? (
                  <EmptyState
                    type="no-search-results"
                    title={t('common.noData')}
                    description={t('message.adjustSearchFilter')}
                    onRefresh={() => {
                      setSearch('')
                      setStatus(undefined)
                    }}
                  />
                ) : (
                  <EmptyState
                    title={t('message.noVideosYet')}
                    description={t('message.createFirst', { type: t('menu.videos').toLowerCase() })}
                    actionText={t('common.create') + ' ' + t('menu.videos')}
                    onAction={() => navigate('/videos/new')}
                  />
                ),
            }}
          />
        </div>
      </div>

      {/* 🆕 Schedule Publish Modal */}
      <SchedulePublishModal
        visible={scheduleModalVisible}
        videoId={scheduleTargetVideo?.id}
        videoTitle={scheduleTargetVideo?.title}
        currentScheduledTime={scheduleTargetVideo?.scheduled_publish_at}
        onOk={(data) =>
          schedulePublishMutation.mutate({
            videoId: scheduleTargetVideo.id,
            scheduled_publish_at: data.scheduled_publish_at,
          })
        }
        onCancel={() => {
          setScheduleModalVisible(false)
          setScheduleTargetVideo(null)
        }}
        loading={schedulePublishMutation.isPending}
      />

      {/* 🆕 Batch Quality Score Modal */}
      <Modal
        title={t('video.operation.batchSetQualityScore')}
        open={batchQualityModalVisible}
        onOk={() => batchSetQualityMutation.mutate({ ids: selectedRowKeys, quality_score: batchQualityScore })}
        onCancel={() => setBatchQualityModalVisible(false)}
        confirmLoading={batchSetQualityMutation.isPending}
      >
        <QualityScoreSlider value={batchQualityScore} onChange={setBatchQualityScore} />
      </Modal>

      {/* Batch Upload Modal */}
      <Modal
        title={t('video.batchUpload') || '批量上传视频'}
        open={batchUploadVisible}
        onCancel={() => setBatchUploadVisible(false)}
        footer={null}
        width={900}
        destroyOnClose
      >
        <BatchUploader
          onAllComplete={(urls) => {
            message.success(t('video.uploadSuccess', { count: urls.length }))
            setBatchUploadVisible(false)
            refetch()
          }}
          maxSize={2048}
          maxCount={10}
        />
      </Modal>
    </div>
  )
}

export default VideoList
