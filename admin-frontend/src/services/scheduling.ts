import axios from '@/utils/axios'

export interface ScheduledVideo {
  id: number
  content_id: number
  content_type: string
  title?: string
  description?: string
  status: string
  scheduled_time: string
  actual_publish_time?: string
  created_at: string
  updated_at: string
  auto_publish: boolean
  notify_subscribers: boolean
  priority: number
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

export const schedulingService = {
  // Get scheduled items
  getScheduledVideos: async (
    status?: 'pending' | 'published' | 'cancelled',
    skip: number = 0,
    limit: number = 20
  ) => {
    const response = await axios.get<ScheduledVideosResponse>(
      '/api/v1/admin/scheduling/',
      {
        params: {
          status: status === 'pending' ? 'PENDING' : status === 'published' ? 'PUBLISHED' : status === 'cancelled' ? 'CANCELLED' : undefined,
          content_type: 'video',
          skip,
          limit
        },
      }
    )
    return response.data
  },

  // Schedule a video for publishing
  scheduleVideo: async (data: VideoScheduleCreate) => {
    const scheduleData = {
      content_type: 'video',
      content_id: data.video_id,
      scheduled_time: data.scheduled_publish_at,
      auto_publish: data.auto_publish ?? true,
      notify_subscribers: data.notify_subscribers ?? false,
    }
    const response = await axios.post('/api/v1/admin/scheduling/', scheduleData)
    return response.data
  },

  // Update video schedule
  updateVideoSchedule: async (scheduleId: number, data: VideoScheduleUpdate) => {
    const updateData = {
      scheduled_time: data.scheduled_publish_at,
      auto_publish: data.auto_publish,
      notify_subscribers: data.notify_subscribers,
    }
    const response = await axios.put(
      `/api/v1/admin/scheduling/${scheduleId}`,
      updateData
    )
    return response.data
  },

  // Cancel schedule
  cancelVideoSchedule: async (scheduleId: number) => {
    await axios.delete(`/api/v1/admin/scheduling/${scheduleId}`)
  },

  // Publish due schedules (manual trigger)
  publishScheduledVideos: async () => {
    const response = await axios.post('/api/v1/admin/scheduling/execute-due')
    return response.data
  },

  // Get scheduling statistics
  getStats: async () => {
    const response = await axios.get<SchedulingStats>('/api/v1/admin/scheduling/stats')
    return response.data
  },
}
