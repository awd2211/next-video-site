import React, { useState, useEffect, useCallback, useMemo } from 'react'
import {
  Card,
  Table,
  Button,
  Space,
  Modal,
  Form,
  DatePicker,
  Select,
  message,
  Popconfirm,
  Tag,
  Typography,
  Row,
  Col,
  Statistic,
  Alert,
  Input,
  Checkbox,
  InputNumber,
  Tooltip,
  Divider,
  Badge,
  Switch,
  Skeleton,
} from 'antd'
import {
  ClockCircleOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  CalendarOutlined,
  SearchOutlined,
  ReloadOutlined,
  BulbOutlined,
  HistoryOutlined,
  TagsOutlined,
  ThunderboltOutlined,
  CrownOutlined,
  FilterOutlined,
  SyncOutlined,
  CaretUpOutlined,
  CaretDownOutlined,
  UnorderedListOutlined,
} from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  schedulingService,
  ScheduledVideo,
  ScheduleCreate,
  ScheduleUpdate,
} from '@/services/scheduling'
import { useTranslation } from 'react-i18next'
import dayjs from 'dayjs'
import type { Dayjs } from 'dayjs'
import { debounce } from 'lodash'
import { useNavigate } from 'react-router-dom'

const { Title, Text, Paragraph } = Typography
const { Option } = Select
const { RangePicker } = DatePicker

const SchedulingList: React.FC = () => {
  const { t } = useTranslation()
  const [form] = Form.useForm()
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  // ========== 状态管理 ==========
  const [scheduleModalVisible, setScheduleModalVisible] = useState(false)
  const [editingSchedule, setEditingSchedule] = useState<ScheduledVideo | null>(null)
  const [selectedRowKeys, setSelectedRowKeys] = useState<number[]>([])

  // 过滤器状态
  const [statusFilter, setStatusFilter] = useState<string>('pending')
  const [contentTypeFilter, setContentTypeFilter] = useState<string>('video')
  const [searchText, setSearchText] = useState<string>('')
  const [debouncedSearchText, setDebouncedSearchText] = useState<string>('')
  const [dateRange, setDateRange] = useState<[Dayjs | null, Dayjs | null] | null>(null)

  // 排序状态
  const [sortBy, setSortBy] = useState<string>('scheduled_time')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  // 分页状态
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)

  // 自动刷新
  const [autoRefresh, setAutoRefresh] = useState(false)
  const [showFilters, setShowFilters] = useState(true)

  // 搜索防抖
  const debouncedSearch = useMemo(
    () =>
      debounce((value: string) => {
        setDebouncedSearchText(value)
        setPage(1) // 重置页码
      }, 500),
    []
  )

  useEffect(() => {
    debouncedSearch(searchText)
    return () => {
      debouncedSearch.cancel()
    }
  }, [searchText, debouncedSearch])

  // ========== 数据查询 ==========

  // 获取统计数据
  const { data: stats, isLoading: statsLoading, refetch: refetchStats } = useQuery({
    queryKey: ['scheduling-stats'],
    queryFn: schedulingService.getStats,
    refetchInterval: autoRefresh ? 30000 : false, // 自动刷新时30秒
  })

  // 获取调度列表
  const { data: scheduledData, isLoading, isFetching, refetch: refetchList } = useQuery({
    queryKey: [
      'scheduled-videos',
      statusFilter,
      contentTypeFilter,
      debouncedSearchText,
      sortBy,
      sortOrder,
      page,
      pageSize,
      dateRange,
    ],
    queryFn: () =>
      schedulingService.getScheduledVideos({
        status: statusFilter === 'all' ? undefined : statusFilter as any,
        content_type: contentTypeFilter === 'all' ? undefined : contentTypeFilter,
        search: debouncedSearchText || undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
        skip: (page - 1) * pageSize,
        limit: pageSize,
        start_date: dateRange?.[0]?.toISOString(),
        end_date: dateRange?.[1]?.toISOString(),
      }),
    refetchInterval: autoRefresh ? 30000 : false, // 自动刷新时30秒
  })

  // 获取智能推荐时间
  const { data: suggestedTimes, refetch: refetchSuggestions } = useQuery({
    queryKey: ['suggested-times', contentTypeFilter],
    queryFn: () => schedulingService.getSuggestedTimes(contentTypeFilter),
    enabled: false, // 手动触发
  })

  // ========== 数据变更操作 ==========

  // 创建/更新调度
  const saveScheduleMutation = useMutation({
    mutationFn: async (values: any) => {
      const scheduleData: ScheduleCreate | ScheduleUpdate = {
        content_type: values.content_type,
        content_id: values.content_id,
        scheduled_time: values.scheduled_time.toISOString(),
        end_time: values.end_time?.toISOString(),
        auto_publish: values.auto_publish ?? true,
        auto_expire: values.auto_expire ?? false,
        notify_subscribers: values.notify_subscribers ?? false,
        priority: values.priority ?? 0,
        recurrence: values.recurrence ?? 'once',
        publish_strategy: values.publish_strategy ?? 'immediate',
        title: values.title,
        description: values.description,
        tags: values.tags || [],
      }

      if (editingSchedule) {
        return schedulingService.updateSchedule(editingSchedule.id, scheduleData as ScheduleUpdate)
      }
      return schedulingService.createSchedule(scheduleData as ScheduleCreate)
    },
    onSuccess: () => {
      message.success(editingSchedule ? t('scheduling.updateSuccess') : t('scheduling.scheduleSuccess'))
      queryClient.invalidateQueries({ queryKey: ['scheduled-videos'] })
      queryClient.invalidateQueries({ queryKey: ['scheduling-stats'] })
      setScheduleModalVisible(false)
      setEditingSchedule(null)
      form.resetFields()
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('common.operationFailed'))
    },
  })

  // 取消调度
  const cancelScheduleMutation = useMutation({
    mutationFn: schedulingService.cancelSchedule,
    onSuccess: () => {
      message.success(t('scheduling.cancelSuccess'))
      queryClient.invalidateQueries({ queryKey: ['scheduled-videos'] })
      queryClient.invalidateQueries({ queryKey: ['scheduling-stats'] })
    },
  })

  // 批量取消
  const batchCancelMutation = useMutation({
    mutationFn: (data: { ids: number[]; reason?: string }) =>
      schedulingService.batchCancelSchedules(data.ids, data.reason),
    onSuccess: () => {
      message.success(t('common.success'))
      setSelectedRowKeys([])
      queryClient.invalidateQueries({ queryKey: ['scheduled-videos'] })
      queryClient.invalidateQueries({ queryKey: ['scheduling-stats'] })
    },
  })

  // 执行调度
  const executeScheduleMutation = useMutation({
    mutationFn: (scheduleId: number) => schedulingService.executeSchedule(scheduleId),
    onSuccess: () => {
      message.success(t('scheduling.executeSuccess'))
      queryClient.invalidateQueries({ queryKey: ['scheduled-videos'] })
      queryClient.invalidateQueries({ queryKey: ['scheduling-stats'] })
    },
  })

  // 发布过期调度
  const publishScheduledMutation = useMutation({
    mutationFn: schedulingService.publishScheduledVideos,
    onSuccess: (data) => {
      message.success(`${t('scheduling.publishSuccess')}: ${data.executed_count} ${t('common.items')}`)
      queryClient.invalidateQueries({ queryKey: ['scheduled-videos'] })
      queryClient.invalidateQueries({ queryKey: ['scheduling-stats'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('scheduling.publishFailed'))
    },
  })

  // ========== 事件处理 ==========

  const handleScheduleSave = async () => {
    try {
      const values = await form.validateFields()
      await saveScheduleMutation.mutateAsync(values)
    } catch (error) {
      console.error('Validation failed:', error)
    }
  }

  const handleBatchCancel = () => {
    if (selectedRowKeys.length === 0) {
      message.warning(t('message.pleaseSelect'))
      return
    }

    Modal.confirm({
      title: t('scheduling.batchCancel'),
      content: t('message.confirmOperation', {
        action: t('common.cancel'),
        count: selectedRowKeys.length,
        type: t('common.items'),
      }),
      onOk: () => batchCancelMutation.mutate({ ids: selectedRowKeys }),
    })
  }

  const handleUseSuggestedTime = async () => {
    await refetchSuggestions()
    if (suggestedTimes?.recommended_times?.[0]) {
      const suggestion = suggestedTimes.recommended_times[0]
      const now = dayjs()
      const suggestedTime = now.hour(suggestion.hour).minute(0).second(0)

      // 如果推荐时间已过，则使用明天的该时间
      const finalTime = suggestedTime.isBefore(now) ? suggestedTime.add(1, 'day') : suggestedTime

      form.setFieldsValue({
        scheduled_time: finalTime,
      })
      message.success(`${t('scheduling.useSuggestedTime')}: ${suggestion.hour}:00 (${suggestion.reason})`)
    }
  }

  // 快速过滤
  const handleQuickFilter = useCallback((status: string, type?: string) => {
    setStatusFilter(status)
    if (type) setContentTypeFilter(type)
    setPage(1)
  }, [])

  // 清空所有过滤
  const handleClearFilters = useCallback(() => {
    setStatusFilter('pending')
    setContentTypeFilter('video')
    setSearchText('')
    setDebouncedSearchText('')
    setDateRange(null)
    setPage(1)
    message.success(t('common.filtersCleared'))
  }, [t])

  // 手动刷新
  const handleManualRefresh = useCallback(() => {
    refetchList()
    refetchStats()
    message.success(t('common.refreshed'))
  }, [refetchList, refetchStats, t])

  // 键盘快捷键
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Ctrl/Cmd + K: 聚焦搜索框
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        document.querySelector<HTMLInputElement>('input[placeholder*="搜索"]')?.focus()
      }
      // Ctrl/Cmd + R: 刷新
      if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault()
        handleManualRefresh()
      }
      // Ctrl/Cmd + N: 新建调度
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault()
        setEditingSchedule(null)
        form.resetFields()
        setScheduleModalVisible(true)
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [handleManualRefresh, form])

  // ========== 表格配置 ==========

  const columns = [
    {
      title: t('common.id'),
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: t('scheduling.contentType'),
      dataIndex: 'content_type',
      key: 'content_type',
      width: 100,
      render: (type: string) => {
        const colorMap: Record<string, string> = {
          video: 'blue',
          banner: 'purple',
          announcement: 'green',
          recommendation: 'orange',
          series: 'cyan',
        }
        return <Tag color={colorMap[type] || 'default'}>{t(`scheduling.${type}`)}</Tag>
      },
    },
    {
      title: t('video.id'),
      dataIndex: 'content_id',
      key: 'content_id',
      width: 100,
    },
    {
      title: t('scheduling.title'),
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      render: (title: string, record: ScheduledVideo) => (
        <Space direction="vertical" size={0}>
          <Text strong>{title || `${record.content_type} #${record.content_id}`}</Text>
          {record.tags && record.tags.length > 0 && (
            <Space size={4}>
              {record.tags.slice(0, 2).map((tag: string) => (
                <Tag key={tag} icon={<TagsOutlined />} style={{ fontSize: 11 }}>
                  {tag}
                </Tag>
              ))}
              {record.tags.length > 2 && <Text type="secondary">+{record.tags.length - 2}</Text>}
            </Space>
          )}
        </Space>
      ),
    },
    {
      title: t('common.status'),
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string, record: ScheduledVideo) => {
        const statusConfig: Record<string, { color: string; icon: React.ReactNode; text: string }> = {
          pending: { color: 'warning', icon: <ClockCircleOutlined />, text: t('scheduling.pending') },
          published: { color: 'success', icon: <CheckCircleOutlined />, text: t('scheduling.published') },
          cancelled: { color: 'default', icon: <CloseCircleOutlined />, text: t('scheduling.cancelled') },
          failed: { color: 'error', icon: <CloseCircleOutlined />, text: t('scheduling.failed') },
          expired: { color: 'default', icon: <CloseCircleOutlined />, text: t('scheduling.expired') },
        }
        const config = statusConfig[status.toLowerCase()] || statusConfig.pending
        return (
          <Badge
            status={config.color as any}
            text={
              <Space>
                {config.icon}
                {config.text}
              </Space>
            }
          />
        )
      },
    },
    {
      title: t('scheduling.priority'),
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: (priority: number) => (
        <Tag color={priority >= 80 ? 'red' : priority >= 50 ? 'orange' : 'default'}>
          {priority >= 80 && <CrownOutlined />} {priority}
        </Tag>
      ),
    },
    {
      title: t('scheduling.scheduledTime'),
      dataIndex: 'scheduled_time',
      key: 'scheduled_time',
      width: 200,
      render: (date: string, record: ScheduledVideo) => {
        const scheduleTime = dayjs(date)
        const now = dayjs()
        const isOverdue = record.is_overdue || scheduleTime.isBefore(now)

        return (
          <Space direction="vertical" size={0}>
            <Text strong={isOverdue} type={isOverdue ? 'danger' : undefined}>
              {scheduleTime.format('YYYY-MM-DD HH:mm')}
            </Text>
            <Text type="secondary" style={{ fontSize: 12 }}>
              {isOverdue ? `${t('scheduling.overdue')} ${scheduleTime.fromNow()}` : scheduleTime.fromNow()}
            </Text>
            {record.recurrence !== 'once' && (
              <Tag icon={<ReloadOutlined />} style={{ fontSize: 11 }}>
                {t(`scheduling.${record.recurrence}`)}
              </Tag>
            )}
          </Space>
        )
      },
    },
    {
      title: t('scheduling.publishStrategy'),
      dataIndex: 'publish_strategy',
      key: 'publish_strategy',
      width: 120,
      render: (strategy: string) => {
        const iconMap: Record<string, React.ReactNode> = {
          immediate: <ThunderboltOutlined />,
          progressive: <ReloadOutlined />,
          regional: <CalendarOutlined />,
          ab_test: <BulbOutlined />,
        }
        return (
          <Tag icon={iconMap[strategy]}>
            {t(`scheduling.${strategy.replace('_', '')}`)}
          </Tag>
        )
      },
    },
    {
      title: t('common.actions'),
      key: 'actions',
      width: 220,
      fixed: 'right' as const,
      render: (_: any, record: ScheduledVideo) => (
        <Space size="small">
          <Tooltip title={t('scheduling.viewHistory')}>
            <Button
              size="small"
              icon={<HistoryOutlined />}
              onClick={() => {
                // TODO: Open history drawer
                message.info('历史记录功能待实现')
              }}
            />
          </Tooltip>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => {
              setEditingSchedule(record)
              form.setFieldsValue({
                content_type: record.content_type,
                content_id: record.content_id,
                scheduled_time: dayjs(record.scheduled_time),
                end_time: record.end_time ? dayjs(record.end_time) : null,
                auto_publish: record.auto_publish,
                auto_expire: record.auto_expire,
                notify_subscribers: record.notify_subscribers,
                priority: record.priority,
                recurrence: record.recurrence,
                publish_strategy: record.publish_strategy,
                title: record.title,
                description: record.description,
                tags: record.tags,
              })
              setScheduleModalVisible(true)
            }}
            disabled={record.status !== 'pending'}
          >
            {t('common.edit')}
          </Button>
          {record.status === 'pending' && (
            <Popconfirm
              title={t('scheduling.confirmExecute')}
              onConfirm={() => executeScheduleMutation.mutate(record.id)}
            >
              <Button size="small" type="primary" icon={<PlayCircleOutlined />}>
                {t('scheduling.execute')}
              </Button>
            </Popconfirm>
          )}
          <Popconfirm
            title={t('scheduling.confirmCancel')}
            onConfirm={() => cancelScheduleMutation.mutate(record.id)}
            disabled={record.status !== 'pending'}
          >
            <Button
              size="small"
              danger
              icon={<DeleteOutlined />}
              disabled={record.status !== 'pending'}
            >
              {t('common.cancel')}
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <Card>
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={2} style={{ margin: 0 }}>
              {t('menu.scheduling')}
            </Title>
            <Paragraph type="secondary">{t('scheduling.description')}</Paragraph>
          </Col>
          <Col>
            <Space>
              <Button
                icon={<CalendarOutlined />}
                onClick={() => navigate('/scheduling/calendar')}
                size="large"
              >
                {t('scheduling.calendarView') || '日历视图'}
              </Button>
              <Button
                icon={<UnorderedListOutlined />}
                type="primary"
                size="large"
              >
                {t('scheduling.listView') || '列表视图'}
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Statistics */}
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Skeleton loading={statsLoading} active paragraph={{ rows: 1 }}>
              <Statistic
                title={t('scheduling.pendingScheduled')}
                value={stats?.pending_count || 0}
                prefix={<ClockCircleOutlined />}
                valueStyle={{ color: '#faad14', cursor: 'pointer' }}
                onClick={() => handleQuickFilter('pending')}
              />
            </Skeleton>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Skeleton loading={statsLoading} active paragraph={{ rows: 1 }}>
              <Statistic
                title={t('scheduling.scheduledToday')}
                value={stats?.published_today || 0}
                prefix={<CalendarOutlined />}
                valueStyle={{ color: '#1890ff', cursor: 'pointer' }}
                onClick={() => handleQuickFilter('published')}
              />
            </Skeleton>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Skeleton loading={statsLoading} active paragraph={{ rows: 1 }}>
              <Statistic
                title={t('scheduling.overdue')}
                value={stats?.overdue_count || 0}
                prefix={<CloseCircleOutlined />}
                valueStyle={{ color: '#ff4d4f', cursor: 'pointer' }}
                onClick={() => handleQuickFilter('pending')}
              />
            </Skeleton>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Skeleton loading={statsLoading} active paragraph={{ rows: 1 }}>
              <Statistic
                title={t('scheduling.upcoming24h')}
                value={stats?.upcoming_24h || 0}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: '#52c41a', cursor: 'pointer' }}
                onClick={() => handleQuickFilter('pending')}
              />
            </Skeleton>
          </Card>
        </Col>
      </Row>

      {/* Quick Filter Chips */}
      <Card style={{ marginTop: 16 }}>
        <Space wrap>
          <Text strong>{t('common.quickFilters')}:</Text>
          <Tag.CheckableTag
            checked={statusFilter === 'pending'}
            onChange={() => handleQuickFilter('pending')}
          >
            <ClockCircleOutlined /> {t('scheduling.pending')}
          </Tag.CheckableTag>
          <Tag.CheckableTag
            checked={statusFilter === 'published'}
            onChange={() => handleQuickFilter('published')}
          >
            <CheckCircleOutlined /> {t('scheduling.published')}
          </Tag.CheckableTag>
          <Tag.CheckableTag
            checked={statusFilter === 'failed'}
            onChange={() => handleQuickFilter('failed')}
          >
            <CloseCircleOutlined /> {t('scheduling.failed')}
          </Tag.CheckableTag>
          <Divider type="vertical" />
          <Tag.CheckableTag
            checked={contentTypeFilter === 'video'}
            onChange={() => handleQuickFilter(statusFilter, 'video')}
          >
            {t('scheduling.video')}
          </Tag.CheckableTag>
          <Tag.CheckableTag
            checked={contentTypeFilter === 'banner'}
            onChange={() => handleQuickFilter(statusFilter, 'banner')}
          >
            {t('scheduling.banner')}
          </Tag.CheckableTag>
          <Tag.CheckableTag
            checked={contentTypeFilter === 'announcement'}
            onChange={() => handleQuickFilter(statusFilter, 'announcement')}
          >
            {t('scheduling.announcement')}
          </Tag.CheckableTag>
          <Divider type="vertical" />
          <Button size="small" onClick={handleClearFilters} icon={<FilterOutlined />}>
            {t('common.clearFilters')}
          </Button>
        </Space>
      </Card>

      {/* Overdue Alert */}
      {stats && stats.overdue_count > 0 && (
        <Alert
          message={t('scheduling.overdueAlert')}
          description={
            <Space direction="vertical">
              <Text>{t('scheduling.overdueDescription', { count: stats.overdue_count })}</Text>
              <Button
                type="primary"
                size="small"
                icon={<PlayCircleOutlined />}
                onClick={() => publishScheduledMutation.mutate()}
                loading={publishScheduledMutation.isPending}
              >
                {t('scheduling.publishNow')}
              </Button>
            </Space>
          }
          type="warning"
          showIcon
          closable
          style={{ marginTop: 16 }}
        />
      )}

      {/* Filters and Actions */}
      <Card
        style={{ marginTop: 16 }}
        title={
          <Space>
            <FilterOutlined />
            {t('common.filters')}
            <Badge dot={searchText || dateRange} />
          </Space>
        }
        extra={
          <Space>
            <Tooltip title={t('common.autoRefresh')}>
              <Space>
                <Switch
                  checked={autoRefresh}
                  onChange={setAutoRefresh}
                  checkedChildren={<SyncOutlined spin />}
                  unCheckedChildren={<SyncOutlined />}
                />
                <Text type="secondary">{autoRefresh ? t('common.autoRefreshOn') : t('common.autoRefreshOff')}</Text>
              </Space>
            </Tooltip>
            <Tooltip title="Ctrl+R">
              <Button
                icon={<ReloadOutlined spin={isFetching} />}
                onClick={handleManualRefresh}
                loading={isFetching}
              >
                {t('common.refresh')}
              </Button>
            </Tooltip>
            <Button
              icon={showFilters ? <CaretUpOutlined /> : <CaretDownOutlined />}
              onClick={() => setShowFilters(!showFilters)}
            >
              {showFilters ? t('common.collapse') : t('common.expand')}
            </Button>
          </Space>
        }
      >
        {showFilters && (
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            {/* Row 1: Search and Primary Filters */}
            <Row gutter={16} align="middle">
              <Col flex="auto">
                <Input
                  placeholder={`${t('scheduling.searchPlaceholder')} (Ctrl+K)`}
                  prefix={<SearchOutlined />}
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  allowClear
                  suffix={searchText && searchText !== debouncedSearchText && <SyncOutlined spin />}
                />
              </Col>
              <Col>
                <Select
                  value={contentTypeFilter}
                  onChange={(value) => {
                    setContentTypeFilter(value)
                    setPage(1)
                  }}
                  style={{ width: 150 }}
                >
                  <Option value="all">{t('scheduling.allTypes')}</Option>
                  <Option value="video">{t('scheduling.video')}</Option>
                  <Option value="banner">{t('scheduling.banner')}</Option>
                  <Option value="announcement">{t('scheduling.announcement')}</Option>
                  <Option value="recommendation">{t('scheduling.recommendation')}</Option>
                  <Option value="series">{t('scheduling.series')}</Option>
                </Select>
              </Col>
              <Col>
                <Select
                  value={statusFilter}
                  onChange={(value) => {
                    setStatusFilter(value)
                    setPage(1)
                  }}
                  style={{ width: 150 }}
                >
                  <Option value="all">{t('common.all')}</Option>
                  <Option value="pending">{t('scheduling.pending')}</Option>
                  <Option value="published">{t('scheduling.published')}</Option>
                  <Option value="cancelled">{t('scheduling.cancelled')}</Option>
                  <Option value="failed">{t('scheduling.failed')}</Option>
                  <Option value="expired">{t('scheduling.expired')}</Option>
                </Select>
              </Col>
            </Row>

            {/* Row 2: Secondary Filters and Actions */}
            <Row gutter={16} align="middle">
              <Col>
                <RangePicker
                  value={dateRange}
                  onChange={(dates) => {
                    setDateRange(dates)
                    setPage(1)
                  }}
                  placeholder={[t('common.startDate'), t('common.endDate')]}
                />
              </Col>
              <Col>
                <Select value={sortBy} onChange={setSortBy} style={{ width: 150 }}>
                  <Option value="scheduled_time">{t('scheduling.sortByTime')}</Option>
                  <Option value="priority">{t('scheduling.sortByPriority')}</Option>
                  <Option value="created_at">{t('scheduling.sortByCreated')}</Option>
                </Select>
              </Col>
              <Col>
                <Select value={sortOrder} onChange={setSortOrder} style={{ width: 100 }}>
                  <Option value="desc">{t('common.descending')}</Option>
                  <Option value="asc">{t('common.ascending')}</Option>
                </Select>
              </Col>
              <Col flex="auto" />
              <Col>
                <Space>
                  <Tooltip title="Ctrl+N">
                    <Button
                      type="primary"
                      icon={<PlusOutlined />}
                      onClick={() => {
                        setEditingSchedule(null)
                        form.resetFields()
                        setScheduleModalVisible(true)
                      }}
                    >
                      {t('scheduling.addSchedule')}
                    </Button>
                  </Tooltip>
                  <Button
                    icon={<PlayCircleOutlined />}
                    onClick={() => publishScheduledMutation.mutate()}
                    loading={publishScheduledMutation.isPending}
                  >
                    {t('scheduling.publishOverdue')}
                  </Button>
                </Space>
              </Col>
            </Row>
          </Space>
        )}
      </Card>

      {/* Batch Operations Bar */}
      {selectedRowKeys.length > 0 && (
        <Card style={{ marginTop: 16, background: '#f0f2f5' }}>
          <Row align="middle" gutter={16}>
            <Col>
              <Text strong>
                {t('common.selected')}: {selectedRowKeys.length} {t('common.items')}
              </Text>
            </Col>
            <Col>
              <Button danger icon={<DeleteOutlined />} onClick={handleBatchCancel}>
                {t('scheduling.batchCancel')}
              </Button>
            </Col>
            <Col flex="auto" />
            <Col>
              <Button onClick={() => setSelectedRowKeys([])}>{t('common.clear')}</Button>
            </Col>
          </Row>
        </Card>
      )}

      {/* Table */}
      <Card style={{ marginTop: 16 }}>
        <Table
          dataSource={scheduledData?.items || []}
          columns={columns}
          rowKey="id"
          loading={isLoading}
          rowSelection={{
            selectedRowKeys,
            onChange: setSelectedRowKeys,
            getCheckboxProps: (record: ScheduledVideo) => ({
              disabled: record.status !== 'pending',
            }),
          }}
          scroll={{ x: 1500 }}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: scheduledData?.total || 0,
            onChange: (newPage) => setPage(newPage),
            onShowSizeChange: (current, size) => {
              setPageSize(size)
              setPage(1)
            },
            showSizeChanger: true,
            pageSizeOptions: ['10', '20', '50', '100'],
            showQuickJumper: true,
            showTotal: (total) => t('common.total', { count: total }),
          }}
        />
      </Card>

      {/* Schedule Modal */}
      <Modal
        title={
          editingSchedule ? t('scheduling.editSchedule') : t('scheduling.addSchedule')
        }
        open={scheduleModalVisible}
        onOk={handleScheduleSave}
        onCancel={() => {
          setScheduleModalVisible(false)
          setEditingSchedule(null)
          form.resetFields()
        }}
        confirmLoading={saveScheduleMutation.isPending}
        width={700}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Divider orientation="left">{t('scheduling.basicInfo')}</Divider>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="content_type"
                label={t('scheduling.contentType')}
                rules={[{ required: true }]}
                initialValue="video"
              >
                <Select disabled={!!editingSchedule}>
                  <Option value="video">{t('scheduling.video')}</Option>
                  <Option value="banner">{t('scheduling.banner')}</Option>
                  <Option value="announcement">{t('scheduling.announcement')}</Option>
                  <Option value="recommendation">{t('scheduling.recommendation')}</Option>
                  <Option value="series">{t('scheduling.series')}</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="content_id"
                label={t('video.id')}
                rules={[{ required: true }]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder={t('scheduling.enterVideoId')}
                  disabled={!!editingSchedule}
                  min={1}
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="title" label={t('scheduling.title')}>
            <Input placeholder={t('form.pleaseInput')} />
          </Form.Item>

          <Form.Item name="description" label={t('common.description')}>
            <Input.TextArea rows={3} placeholder={t('form.pleaseInput')} />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="scheduled_time"
                label={t('scheduling.scheduledTime')}
                rules={[{ required: true }]}
              >
                <DatePicker
                  showTime
                  format="YYYY-MM-DD HH:mm:ss"
                  style={{ width: '100%' }}
                  disabledDate={(current) => current && current < dayjs().startOf('day')}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="end_time" label={t('scheduling.endTime')}>
                <DatePicker
                  showTime
                  format="YYYY-MM-DD HH:mm:ss"
                  style={{ width: '100%' }}
                  disabledDate={(current) => current && current < dayjs().startOf('day')}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16} align="middle">
            <Col span={12}>
              <Button
                icon={<BulbOutlined />}
                onClick={handleUseSuggestedTime}
                style={{ marginTop: -8 }}
              >
                {t('scheduling.useSuggestedTime')}
              </Button>
            </Col>
          </Row>

          <Divider orientation="left">{t('scheduling.advancedSettings')}</Divider>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="priority"
                label={t('scheduling.priority')}
                initialValue={0}
              >
                <InputNumber style={{ width: '100%' }} min={0} max={100} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="recurrence"
                label={t('scheduling.recurrence')}
                initialValue="once"
              >
                <Select>
                  <Option value="once">{t('scheduling.once')}</Option>
                  <Option value="daily">{t('scheduling.daily')}</Option>
                  <Option value="weekly">{t('scheduling.weekly')}</Option>
                  <Option value="monthly">{t('scheduling.monthly')}</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="publish_strategy"
                label={t('scheduling.publishStrategy')}
                initialValue="immediate"
              >
                <Select>
                  <Option value="immediate">{t('scheduling.immediate')}</Option>
                  <Option value="progressive">{t('scheduling.progressive')}</Option>
                  <Option value="regional">{t('scheduling.regional')}</Option>
                  <Option value="ab_test">{t('scheduling.abTest')}</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="tags" label={t('scheduling.tags')}>
            <Select mode="tags" placeholder={t('form.pleaseInput')} />
          </Form.Item>

          <Space>
            <Form.Item
              name="auto_publish"
              valuePropName="checked"
              initialValue={true}
              noStyle
            >
              <Checkbox>{t('scheduling.autoPublish')}</Checkbox>
            </Form.Item>
            <Form.Item name="auto_expire" valuePropName="checked" initialValue={false} noStyle>
              <Checkbox>{t('scheduling.autoExpire')}</Checkbox>
            </Form.Item>
            <Form.Item
              name="notify_subscribers"
              valuePropName="checked"
              initialValue={false}
              noStyle
            >
              <Checkbox>{t('scheduling.notifySubscribers')}</Checkbox>
            </Form.Item>
          </Space>

          <Alert
            message={t('scheduling.hint')}
            description={t('scheduling.hintDescription')}
            type="info"
            showIcon
            style={{ marginTop: 16 }}
          />
        </Form>
      </Modal>
    </div>
  )
}

export default SchedulingList
