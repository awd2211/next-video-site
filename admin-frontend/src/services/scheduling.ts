import axios from '@/utils/axios'

// ========== 类型定义 ==========

export interface ScheduledVideo {
  id: number
  content_id: number
  content_type: string
  title?: string
  description?: string
  status: string
  scheduled_time: string
  actual_publish_time?: string
  end_time?: string
  created_at: string
  updated_at: string
  auto_publish: boolean
  auto_expire: boolean
  notify_subscribers: boolean
  priority: number
  recurrence: string
  publish_strategy: string
  tags: string[]
  is_overdue?: boolean
  is_due?: boolean
}

export interface ScheduledVideosResponse {
  items: ScheduledVideo[]
  total: number
  skip: number
  limit: number
}

export interface VideoScheduleCreate {
  video_id: number
  scheduled_publish_at: string
  auto_publish?: boolean
  notify_subscribers?: boolean
}

export interface VideoScheduleUpdate {
  scheduled_publish_at?: string
  auto_publish?: boolean
  notify_subscribers?: boolean
}

export interface ScheduleCreate {
  content_type: string
  content_id: number
  scheduled_time: string
  end_time?: string
  auto_publish?: boolean
  auto_expire?: boolean
  publish_strategy?: string
  strategy_config?: Record<string, any>
  recurrence?: string
  recurrence_config?: Record<string, any>
  notify_subscribers?: boolean
  notify_before_minutes?: number
  priority?: number
  title?: string
  description?: string
  tags?: string[]
}

export interface ScheduleUpdate {
  scheduled_time?: string
  end_time?: string
  auto_publish?: boolean
  auto_expire?: boolean
  publish_strategy?: string
  recurrence?: string
  notify_subscribers?: boolean
  priority?: number
  title?: string
  description?: string
  tags?: string[]
}

export interface SchedulingStats {
  pending_count: number
  published_today: number
  published_this_week: number
  failed_count: number
  overdue_count: number
  upcoming_24h: number
  by_content_type?: Record<string, number>
  by_status?: Record<string, number>
  by_strategy?: Record<string, number>
}

export interface TimeSlot {
  hour: number
  score: number
  reason: string
}

export interface SuggestedTime {
  recommended_times: TimeSlot[]
  content_type: string
  based_on: string
}

export interface CalendarEvent {
  id: number
  title: string
  content_type: string
  scheduled_time: string
  end_time?: string
  status: string
  priority: number
  color: string
}

export interface CalendarData {
  events: CalendarEvent[]
  month: number
  year: number
}

export interface ScheduleHistory {
  id: number
  schedule_id: number
  action: string
  status_before?: string
  status_after: string
  success: boolean
  message?: string
  details: Record<string, any>
  executed_at: string
  executed_by?: number
  is_automatic: boolean
  execution_time_ms?: number
}

export interface BatchCancelRequest {
  schedule_ids: number[]
  reason?: string
}

// ========== Cron Expression 相关 ==========

export interface CronValidation {
  valid: boolean
  error_message?: string
  description: string
  next_occurrences: string[]
}

export interface CronPattern {
  name: string
  expression: string
  description: string
  category: string
  next_run?: string
}

export interface CronPatternsResponse {
  patterns: CronPattern[]
  categories: string[]
}

// ========== 服务接口 ==========

export const schedulingService = {
  // ===== 列表查询 =====

  // 获取调度列表（增强版）
  getScheduledVideos: async (params?: {
    status?: 'pending' | 'published' | 'cancelled' | 'failed' | 'expired'
    content_type?: string
    skip?: number
    limit?: number
    search?: string
    created_by?: number
    sort_by?: string
    sort_order?: 'asc' | 'desc'
    start_date?: string
    end_date?: string
  }) => {
    const response = await axios.get<ScheduledVideosResponse>('/api/v1/admin/scheduling/', {
      params: {
        status: params?.status,
        content_type: params?.content_type || 'video',
        skip: params?.skip || 0,
        limit: params?.limit || 20,
        search: params?.search,
        created_by: params?.created_by,
        sort_by: params?.sort_by || 'scheduled_time',
        sort_order: params?.sort_order || 'desc',
        start_date: params?.start_date,
        end_date: params?.end_date,
      },
    })
    return response.data
  },

  // ===== 创建和更新 =====

  // 创建调度（通用）
  createSchedule: async (data: ScheduleCreate) => {
    const response = await axios.post('/api/v1/admin/scheduling/', data)
    return response.data
  },

  // 创建视频调度（兼容旧接口）
  scheduleVideo: async (data: VideoScheduleCreate) => {
    const scheduleData: ScheduleCreate = {
      content_type: 'video',
      content_id: data.video_id,
      scheduled_time: data.scheduled_publish_at,
      auto_publish: data.auto_publish ?? true,
      notify_subscribers: data.notify_subscribers ?? false,
    }
    const response = await axios.post('/api/v1/admin/scheduling/', scheduleData)
    return response.data
  },

  // 更新调度
  updateSchedule: async (scheduleId: number, data: ScheduleUpdate) => {
    const response = await axios.put(`/api/v1/admin/scheduling/${scheduleId}`, data)
    return response.data
  },

  // 更新视频调度（兼容旧接口）
  updateVideoSchedule: async (scheduleId: number, data: VideoScheduleUpdate) => {
    const updateData: ScheduleUpdate = {
      scheduled_time: data.scheduled_publish_at,
      auto_publish: data.auto_publish,
      notify_subscribers: data.notify_subscribers,
    }
    const response = await axios.put(`/api/v1/admin/scheduling/${scheduleId}`, updateData)
    return response.data
  },

  // ===== 删除和取消 =====

  // 取消调度
  cancelSchedule: async (scheduleId: number, reason?: string) => {
    await axios.delete(`/api/v1/admin/scheduling/${scheduleId}`, {
      params: { reason },
    })
  },

  // 取消视频调度（兼容旧接口）
  cancelVideoSchedule: async (scheduleId: number) => {
    await axios.delete(`/api/v1/admin/scheduling/${scheduleId}`)
  },

  // 批量取消调度
  batchCancelSchedules: async (schedule_ids: number[], reason?: string) => {
    const response = await axios.delete('/api/v1/admin/scheduling/batch/cancel', {
      params: { schedule_ids, reason },
    })
    return response.data
  },

  // ===== 执行控制 =====

  // 手动执行单个调度
  executeSchedule: async (scheduleId: number, force: boolean = false) => {
    const response = await axios.post(`/api/v1/admin/scheduling/${scheduleId}/execute`, {
      force,
    })
    return response.data
  },

  // 执行所有到期调度
  publishScheduledVideos: async () => {
    const response = await axios.post('/api/v1/admin/scheduling/execute-due')
    return response.data
  },

  // ===== 统计和分析 =====

  // 获取统计信息
  getStats: async () => {
    const response = await axios.get<SchedulingStats>('/api/v1/admin/scheduling/stats')
    return response.data
  },

  // 获取日历数据
  getCalendarData: async (params: { year: number; month: number }) => {
    const response = await axios.get<CalendarData>('/api/v1/admin/scheduling/calendar', {
      params,
    })
    return response.data
  },

  // 获取智能推荐时间
  getSuggestedTimes: async (content_type: string) => {
    const response = await axios.get<SuggestedTime>('/api/v1/admin/scheduling/suggest-time', {
      params: { content_type },
    })
    return response.data
  },

  // ===== 历史记录 =====

  // 获取调度历史记录
  getScheduleHistory: async (scheduleId: number, skip: number = 0, limit: number = 50) => {
    const response = await axios.get<ScheduleHistory[]>(
      `/api/v1/admin/scheduling/${scheduleId}/history`,
      {
        params: { skip, limit },
      }
    )
    return response.data
  },

  // 获取所有历史记录
  getAllHistories: async (params?: {
    skip?: number
    limit?: number
    action?: string
    content_type?: string
    start_date?: string
    end_date?: string
  }) => {
    const response = await axios.get<ScheduleHistory[]>('/api/v1/admin/scheduling/history', {
      params,
    })
    return response.data
  },

  // ===== 模板管理 =====

  // 获取模板列表
  getTemplates: async (params?: { is_active?: boolean; content_type?: string }) => {
    const response = await axios.get('/api/v1/admin/scheduling/templates', { params })
    return response.data
  },

  // 应用模板创建调度
  applyTemplate: async (
    templateId: number,
    data: {
      content_type: string
      content_id: number
      scheduled_time: string
      override_title?: string
      override_priority?: number
    }
  ) => {
    const response = await axios.post(
      `/api/v1/admin/scheduling/templates/${templateId}/apply`,
      data
    )
    return response.data
  },

  // ===== Cron Expression 工具 =====

  // 验证Cron表达式
  validateCron: async (expression: string) => {
    const response = await axios.post<CronValidation>('/api/v1/admin/scheduling/cron/validate', {
      expression,
    })
    return response.data
  },

  // 获取预定义Cron模式
  getCronPatterns: async () => {
    const response = await axios.get<CronPatternsResponse>(
      '/api/v1/admin/scheduling/cron/patterns'
    )
    return response.data
  },

  // 计算Cron下次执行时间
  getCronNextRuns: async (expression: string, count: number = 5, from_time?: string) => {
    const response = await axios.post<{
      expression: string
      description: string
      next_runs: string[]
    }>('/api/v1/admin/scheduling/cron/next-runs', {
      expression,
      count,
      from_time,
    })
    return response.data
  },
}
