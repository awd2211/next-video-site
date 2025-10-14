import React, { useState } from 'react'
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
} from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  schedulingService,
  ScheduledVideo,
  VideoScheduleCreate,
} from '@/services/scheduling'
import { useTranslation } from 'react-i18next'
import dayjs from 'dayjs'
import type { Dayjs } from 'dayjs'

const { Title, Text, Paragraph } = Typography
const { Option } = Select
const { RangePicker } = DatePicker

const SchedulingList: React.FC = () => {
  const { t } = useTranslation()
  const [form] = Form.useForm()
  const queryClient = useQueryClient()

  const [scheduleModalVisible, setScheduleModalVisible] = useState(false)
  const [editingVideo, setEditingVideo] = useState<ScheduledVideo | null>(null)
  const [statusFilter, setStatusFilter] = useState<
    'pending' | 'published' | 'cancelled' | undefined
  >('pending')
  const [videoId, setVideoId] = useState<number | null>(null)

  // Fetch stats
  const { data: stats } = useQuery({
    queryKey: ['scheduling-stats'],
    queryFn: schedulingService.getStats,
    refetchInterval: 60000, // Refresh every minute
  })

  // Fetch scheduled videos
  const { data: scheduledData, isLoading } = useQuery({
    queryKey: ['scheduled-videos', statusFilter],
    queryFn: () => schedulingService.getScheduledVideos(statusFilter),
  })

  // Schedule video mutation
  const scheduleVideoMutation = useMutation({
    mutationFn: async (values: VideoScheduleCreate) => {
      if (editingVideo) {
        return schedulingService.updateVideoSchedule(editingVideo.id, {
          scheduled_publish_at: values.scheduled_publish_at,
          auto_publish: true,
          notify_subscribers: false,
        })
      }
      return schedulingService.scheduleVideo(values)
    },
    onSuccess: () => {
      message.success(
        editingVideo
          ? t('scheduling.updateSuccess') || '更新成功'
          : t('scheduling.scheduleSuccess') || '定时发布设置成功'
      )
      queryClient.invalidateQueries({ queryKey: ['scheduled-videos'] })
      queryClient.invalidateQueries({ queryKey: ['scheduling-stats'] })
      setScheduleModalVisible(false)
      setEditingVideo(null)
      form.resetFields()
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('common.operationFailed'))
    },
  })

  // Cancel schedule mutation
  const cancelScheduleMutation = useMutation({
    mutationFn: schedulingService.cancelVideoSchedule,
    onSuccess: () => {
      message.success(t('scheduling.cancelSuccess') || '取消定时发布成功')
      queryClient.invalidateQueries({ queryKey: ['scheduled-videos'] })
      queryClient.invalidateQueries({ queryKey: ['scheduling-stats'] })
    },
  })

  // Publish scheduled videos mutation
  const publishScheduledMutation = useMutation({
    mutationFn: schedulingService.publishScheduledVideos,
    onSuccess: (data) => {
      message.success(`${t('scheduling.publishSuccess') || '发布成功'}: ${data.count} ${t('common.videos')}`)
      queryClient.invalidateQueries({ queryKey: ['scheduled-videos'] })
      queryClient.invalidateQueries({ queryKey: ['scheduling-stats'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('scheduling.publishFailed'))
    },
  })

  // Table columns
  const columns = [
    {
      title: t('common.id') || 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: t('video.id') || '视频ID',
      dataIndex: 'content_id',
      key: 'content_id',
      width: 100,
    },
    {
      title: t('video.title') || '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      render: (title: string, record: ScheduledVideo) => title || `视频 #${record.content_id}`,
    },
    {
      title: t('common.status') || '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => {
        const statusConfig: Record<
          string,
          { color: string; icon: React.ReactNode; text: string }
        > = {
          PENDING: { color: 'warning', icon: <ClockCircleOutlined />, text: '待发布' },
          PUBLISHED: {
            color: 'success',
            icon: <CheckCircleOutlined />,
            text: '已发布',
          },
          CANCELLED: { color: 'default', icon: <CloseCircleOutlined />, text: '已取消' },
          FAILED: { color: 'error', icon: <CloseCircleOutlined />, text: '失败' },
          EXPIRED: { color: 'default', icon: <CloseCircleOutlined />, text: '已过期' },
        }
        const config = statusConfig[status] || statusConfig.PENDING
        return (
          <Tag icon={config.icon} color={config.color}>
            {config.text}
          </Tag>
        )
      },
    },
    {
      title: t('scheduling.scheduledTime') || '定时发布时间',
      dataIndex: 'scheduled_time',
      key: 'scheduled_time',
      width: 200,
      render: (date: string) => {
        const scheduleTime = dayjs(date)
        const now = dayjs()
        const isOverdue = scheduleTime.isBefore(now)

        return (
          <Space direction="vertical" size={0}>
            <Text strong={isOverdue} type={isOverdue ? 'danger' : undefined}>
              {scheduleTime.format('YYYY-MM-DD HH:mm')}
            </Text>
            <Text type="secondary" style={{ fontSize: 12 }}>
              {isOverdue
                ? `已过期 ${scheduleTime.fromNow()}`
                : `将于 ${scheduleTime.fromNow()} 发布`}
            </Text>
          </Space>
        )
      },
    },
    {
      title: t('common.createdAt') || '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: t('common.actions') || '操作',
      key: 'actions',
      width: 180,
      render: (_: any, record: ScheduledVideo) => (
        <Space>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => {
              setEditingVideo(record)
              form.setFieldsValue({
                video_id: record.content_id,
                scheduled_publish_at: dayjs(record.scheduled_time),
              })
              setScheduleModalVisible(true)
            }}
            disabled={record.status !== 'PENDING'}
          >
            {t('common.edit')}
          </Button>
          <Popconfirm
            title={t('scheduling.confirmCancel') || '确定取消定时发布？'}
            onConfirm={() => cancelScheduleMutation.mutate(record.id)}
            disabled={record.status !== 'PENDING'}
          >
            <Button
              size="small"
              danger
              icon={<DeleteOutlined />}
              disabled={record.status !== 'PENDING'}
            >
              {t('common.cancel')}
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  // Handle schedule save
  const handleScheduleSave = async () => {
    try {
      const values = await form.validateFields()
      const formattedValues: VideoScheduleCreate = {
        video_id: values.video_id,
        scheduled_publish_at: (values.scheduled_publish_at as Dayjs).toISOString(),
      }
      await scheduleVideoMutation.mutateAsync(formattedValues)
    } catch (error) {
      console.error('Validation failed:', error)
    }
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <Card>
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={2} style={{ margin: 0 }}>
              {t('menu.scheduling') || '内容调度'}
            </Title>
            <Paragraph type="secondary">
              {t('scheduling.description') || '管理视频定时发布和内容调度'}
            </Paragraph>
          </Col>
        </Row>
      </Card>

      {/* Statistics */}
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('scheduling.pendingScheduled') || '待发布'}
              value={stats?.pending_count || 0}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('scheduling.scheduledToday') || '今天发布'}
              value={stats?.published_today || 0}
              prefix={<CalendarOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('scheduling.overdue') || '已过期'}
              value={stats?.overdue_count || 0}
              prefix={<CloseCircleOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('scheduling.upcoming24h') || '未来24小时'}
              value={stats?.upcoming_24h || 0}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Alerts */}
      {stats && stats.overdue_count > 0 && (
        <Alert
          message={t('scheduling.overdueAlert') || '过期提醒'}
          description={
            <Space direction="vertical">
              <Text>
                {t('scheduling.overdueDescription') ||
                  `有 ${stats.overdue_count} 个视频的定时发布时间已过期，但仍未发布。`}
              </Text>
              <Button
                type="primary"
                size="small"
                icon={<PlayCircleOutlined />}
                onClick={() => publishScheduledMutation.mutate()}
                loading={publishScheduledMutation.isPending}
              >
                {t('scheduling.publishNow') || '立即发布'}
              </Button>
            </Space>
          }
          type="warning"
          showIcon
          closable
          style={{ marginTop: 16 }}
        />
      )}

      {/* Actions and Filters */}
      <Card style={{ marginTop: 16 }}>
        <Row gutter={16} align="middle">
          <Col flex="auto">
            <Space>
              <Text strong>{t('common.status')}:</Text>
              <Select
                value={statusFilter}
                onChange={setStatusFilter}
                style={{ width: 150 }}
              >
                <Option value={undefined}>{t('common.all') || '全部'}</Option>
                <Option value="pending">{t('scheduling.pending') || '待发布'}</Option>
                <Option value="published">{t('scheduling.published') || '已发布'}</Option>
                <Option value="cancelled">{t('scheduling.cancelled') || '已取消'}</Option>
              </Select>
            </Space>
          </Col>
          <Col>
            <Space>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => {
                  setEditingVideo(null)
                  form.resetFields()
                  setScheduleModalVisible(true)
                }}
              >
                {t('scheduling.addSchedule') || '添加定时发布'}
              </Button>
              <Button
                icon={<PlayCircleOutlined />}
                onClick={() => publishScheduledMutation.mutate()}
                loading={publishScheduledMutation.isPending}
              >
                {t('scheduling.publishOverdue') || '发布过期内容'}
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Table */}
      <Card style={{ marginTop: 16 }}>
        <Table
          dataSource={scheduledData?.items || []}
          columns={columns}
          rowKey="id"
          loading={isLoading}
          pagination={{
            total: scheduledData?.total || 0,
            pageSize: 20,
            showSizeChanger: true,
            showTotal: (total) => t('common.total', { count: total }),
          }}
        />
      </Card>

      {/* Schedule Modal */}
      <Modal
        title={
          editingVideo
            ? t('scheduling.editSchedule') || '编辑定时发布'
            : t('scheduling.addSchedule') || '添加定时发布'
        }
        open={scheduleModalVisible}
        onOk={handleScheduleSave}
        onCancel={() => {
          setScheduleModalVisible(false)
          setEditingVideo(null)
          form.resetFields()
        }}
        confirmLoading={scheduleVideoMutation.isPending}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item
            name="video_id"
            label={t('video.id') || '视频ID'}
            rules={[{ required: true, message: t('common.required') }]}
          >
            <Input
              type="number"
              placeholder={t('scheduling.enterVideoId') || '请输入视频ID'}
              disabled={!!editingVideo}
            />
          </Form.Item>

          <Form.Item
            name="scheduled_publish_at"
            label={t('scheduling.scheduledTime') || '定时发布时间'}
            rules={[{ required: true, message: t('common.required') }]}
          >
            <DatePicker
              showTime
              format="YYYY-MM-DD HH:mm:ss"
              style={{ width: '100%' }}
              disabledDate={(current) => {
                return current && current < dayjs().startOf('day')
              }}
            />
          </Form.Item>

          <Alert
            message={t('scheduling.hint') || '提示'}
            description={
              t('scheduling.hintDescription') ||
              '定时发布时间必须是未来时间。系统会在指定时间自动发布视频。'
            }
            type="info"
            showIcon
          />
        </Form>
      </Modal>
    </div>
  )
}

export default SchedulingList
