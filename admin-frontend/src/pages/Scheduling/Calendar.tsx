import React, { useState, useCallback } from 'react'
import { Card, Badge, Tag, Tooltip, Spin, Button, Space, Select, Modal, message } from 'antd'
import {
  CalendarOutlined,
  ReloadOutlined,
  FilterOutlined,
  LeftOutlined,
  RightOutlined,
} from '@ant-design/icons'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import { schedulingService } from '@/services/scheduling'
import dayjs from 'dayjs'

const { Option } = Select

// 状态颜色映射
const STATUS_COLORS = {
  pending: '#faad14',
  published: '#52c41a',
  failed: '#ff4d4f',
  cancelled: '#d9d9d9',
  expired: '#8c8c8c',
}

// 内容类型颜色映射
const CONTENT_TYPE_COLORS = {
  video: '#1890ff',
  banner: '#722ed1',
  announcement: '#13c2c2',
  recommendation: '#fa8c16',
  series: '#2f54eb',
}

const SchedulingCalendar: React.FC = () => {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const calendarRef = React.useRef<any>(null)

  const [currentDate, setCurrentDate] = useState(dayjs())
  const [viewType, setViewType] = useState<'dayGridMonth' | 'timeGridWeek' | 'timeGridDay'>(
    'dayGridMonth'
  )
  const [filterType, setFilterType] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [selectedEvent, setSelectedEvent] = useState<any>(null)
  const [modalVisible, setModalVisible] = useState(false)

  // 获取日历数据
  const { data: calendarData, isLoading, refetch } = useQuery({
    queryKey: ['scheduling-calendar', currentDate.year(), currentDate.month() + 1, filterType, filterStatus],
    queryFn: async () => {
      const response = await schedulingService.getCalendarData({
        month: currentDate.month() + 1,
        year: currentDate.year(),
      })
      return response
    },
  })

  // 将后端数据转换为 FullCalendar 事件格式
  const events = React.useMemo(() => {
    if (!calendarData?.events) return []

    let filteredEvents = calendarData.events

    // 过滤内容类型
    if (filterType !== 'all') {
      filteredEvents = filteredEvents.filter((e: any) => e.content_type === filterType)
    }

    // 过滤状态
    if (filterStatus !== 'all') {
      filteredEvents = filteredEvents.filter((e: any) => e.status === filterStatus)
    }

    return filteredEvents.map((event: any) => ({
      id: event.id.toString(),
      title: event.title,
      start: event.scheduled_time,
      end: event.end_time || undefined,
      backgroundColor: STATUS_COLORS[event.status as keyof typeof STATUS_COLORS] || '#1890ff',
      borderColor: CONTENT_TYPE_COLORS[event.content_type as keyof typeof CONTENT_TYPE_COLORS] || '#1890ff',
      extendedProps: {
        ...event,
      },
    }))
  }, [calendarData, filterType, filterStatus])

  // 处理事件点击
  const handleEventClick = useCallback((info: any) => {
    setSelectedEvent(info.event.extendedProps)
    setModalVisible(true)
  }, [])

  // 处理日期点击
  const handleDateClick = useCallback((info: any) => {
    message.info(`点击日期: ${info.dateStr}`)
    // TODO: 可以打开创建调度的模态框
  }, [])

  // 处理视图切换
  const handleViewChange = useCallback((view: string) => {
    setViewType(view as typeof viewType)
    if (calendarRef.current) {
      calendarRef.current.getApi().changeView(view)
    }
  }, [])

  // 导航到上一个月/周/天
  const handlePrev = useCallback(() => {
    if (calendarRef.current) {
      const calendarApi = calendarRef.current.getApi()
      calendarApi.prev()
      setCurrentDate(dayjs(calendarApi.getDate()))
    }
  }, [])

  // 导航到下一个月/周/天
  const handleNext = useCallback(() => {
    if (calendarRef.current) {
      const calendarApi = calendarRef.current.getApi()
      calendarApi.next()
      setCurrentDate(dayjs(calendarApi.getDate()))
    }
  }, [])

  // 导航到今天
  const handleToday = useCallback(() => {
    if (calendarRef.current) {
      const calendarApi = calendarRef.current.getApi()
      calendarApi.today()
      setCurrentDate(dayjs())
    }
  }, [])

  // 渲染事件内容
  const renderEventContent = useCallback((eventInfo: any) => {
    const { extendedProps } = eventInfo.event

    return (
      <Tooltip
        title={
          <div>
            <div><strong>{extendedProps.title}</strong></div>
            <div>类型: {t(`scheduling.${extendedProps.content_type}`)}</div>
            <div>状态: {t(`scheduling.${extendedProps.status}`)}</div>
            <div>优先级: {extendedProps.priority}</div>
            <div>时间: {dayjs(extendedProps.scheduled_time).format('YYYY-MM-DD HH:mm')}</div>
          </div>
        }
      >
        <div
          style={{
            padding: '2px 4px',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            fontSize: '12px',
          }}
        >
          <Badge
            status={
              extendedProps.status === 'pending'
                ? 'warning'
                : extendedProps.status === 'published'
                ? 'success'
                : 'default'
            }
            text={eventInfo.timeText ? `${eventInfo.timeText} ${eventInfo.event.title}` : eventInfo.event.title}
          />
        </div>
      </Tooltip>
    )
  }, [t])

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title={
          <Space>
            <CalendarOutlined />
            {t('menu.scheduling')} - {t('scheduling.calendarView')}
          </Space>
        }
        extra={
          <Space>
            {/* 视图切换 */}
            <Select value={viewType} onChange={handleViewChange} style={{ width: 120 }}>
              <Option value="dayGridMonth">{t('common.month')}</Option>
              <Option value="timeGridWeek">{t('common.week')}</Option>
              <Option value="timeGridDay">{t('common.day')}</Option>
            </Select>

            {/* 内容类型过滤 */}
            <Select value={filterType} onChange={setFilterType} style={{ width: 120 }}>
              <Option value="all">{t('scheduling.allTypes')}</Option>
              <Option value="video">{t('scheduling.video')}</Option>
              <Option value="banner">{t('scheduling.banner')}</Option>
              <Option value="announcement">{t('scheduling.announcement')}</Option>
              <Option value="recommendation">{t('scheduling.recommendation')}</Option>
              <Option value="series">{t('scheduling.series')}</Option>
            </Select>

            {/* 状态过滤 */}
            <Select value={filterStatus} onChange={setFilterStatus} style={{ width: 120 }}>
              <Option value="all">{t('common.all')}</Option>
              <Option value="pending">{t('scheduling.pending')}</Option>
              <Option value="published">{t('scheduling.published')}</Option>
              <Option value="failed">{t('scheduling.failed')}</Option>
              <Option value="cancelled">{t('scheduling.cancelled')}</Option>
            </Select>

            {/* 刷新按钮 */}
            <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
              {t('common.refresh')}
            </Button>
          </Space>
        }
      >
        {/* 导航栏 */}
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <Button icon={<LeftOutlined />} onClick={handlePrev} />
            <Button onClick={handleToday}>{t('common.today')}</Button>
            <Button icon={<RightOutlined />} onClick={handleNext} />
          </Space>

          <h3 style={{ margin: 0 }}>
            {viewType === 'dayGridMonth' && currentDate.format('YYYY年 MM月')}
            {viewType === 'timeGridWeek' && `${currentDate.startOf('week').format('YYYY-MM-DD')} ~ ${currentDate.endOf('week').format('YYYY-MM-DD')}`}
            {viewType === 'timeGridDay' && currentDate.format('YYYY年 MM月 DD日')}
          </h3>

          <Space>
            {/* 图例 */}
            <Tag color={STATUS_COLORS.pending}>{t('scheduling.pending')}</Tag>
            <Tag color={STATUS_COLORS.published}>{t('scheduling.published')}</Tag>
            <Tag color={STATUS_COLORS.failed}>{t('scheduling.failed')}</Tag>
          </Space>
        </div>

        {/* 日历组件 */}
        <Spin spinning={isLoading}>
          <div style={{ minHeight: '600px' }}>
            <FullCalendar
              ref={calendarRef}
              plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
              initialView={viewType}
              headerToolbar={false}  // 使用自定义头部
              events={events}
              eventClick={handleEventClick}
              dateClick={handleDateClick}
              eventContent={renderEventContent}
              height="auto"
              locale="zh-cn"
              firstDay={1}  // 周一开始
              nowIndicator={true}
              navLinks={true}
              editable={false}
              selectable={true}
              selectMirror={true}
              dayMaxEvents={true}
              weekends={true}
              slotMinTime="06:00:00"
              slotMaxTime="24:00:00"
              allDaySlot={false}
            />
          </div>
        </Spin>
      </Card>

      {/* 事件详情模态框 */}
      <Modal
        title="调度详情"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setModalVisible(false)}>
            关闭
          </Button>,
        ]}
        width={600}
      >
        {selectedEvent && (
          <div>
            <p><strong>标题:</strong> {selectedEvent.title}</p>
            <p><strong>内容类型:</strong> <Tag>{t(`scheduling.${selectedEvent.content_type}`)}</Tag></p>
            <p><strong>内容ID:</strong> {selectedEvent.content_id}</p>
            <p>
              <strong>状态:</strong>{' '}
              <Badge
                status={
                  selectedEvent.status === 'pending'
                    ? 'warning'
                    : selectedEvent.status === 'published'
                    ? 'success'
                    : 'default'
                }
                text={t(`scheduling.${selectedEvent.status}`)}
              />
            </p>
            <p><strong>优先级:</strong> {selectedEvent.priority}</p>
            <p><strong>计划时间:</strong> {dayjs(selectedEvent.scheduled_time).format('YYYY-MM-DD HH:mm:ss')}</p>
            {selectedEvent.end_time && (
              <p><strong>结束时间:</strong> {dayjs(selectedEvent.end_time).format('YYYY-MM-DD HH:mm:ss')}</p>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}

export default SchedulingCalendar
