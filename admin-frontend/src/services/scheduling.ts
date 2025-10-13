import axios from '@/utils/axios'

export interface ScheduledVideo {
  id: number
  title: string
  status: string
  scheduled_publish_at: string
  created_at: string
  updated_at: string
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
  pending_scheduled: number
  scheduled_today: number
  overdue: number
  total_scheduled: number
}

export const schedulingService = {
  // Get scheduled videos
  getScheduledVideos: async (
    status?: 'pending' | 'published' | 'cancelled',
    skip: number = 0,
    limit: number = 20
  ) => {
    const response = await axios.get<ScheduledVideosResponse>(
      '/api/v1/admin/scheduling/videos/scheduled',
      {
        params: { status, skip, limit },
      }
    )
    return response.data
  },

  // Schedule a video for publishing
  scheduleVideo: async (data: VideoScheduleCreate) => {
    const response = await axios.post('/api/v1/admin/scheduling/videos/schedule', data)
    return response.data
  },

  // Update video schedule
  updateVideoSchedule: async (videoId: number, data: VideoScheduleUpdate) => {
    const response = await axios.put(
      `/api/v1/admin/scheduling/videos/${videoId}/schedule`,
      data
    )
    return response.data
  },

  // Cancel video schedule
  cancelVideoSchedule: async (videoId: number) => {
    await axios.delete(`/api/v1/admin/scheduling/videos/${videoId}/schedule`)
  },

  // Publish scheduled videos (manual trigger)
  publishScheduledVideos: async () => {
    const response = await axios.post('/api/v1/admin/scheduling/videos/publish-scheduled')
    return response.data
  },

  // Get scheduling statistics
  getStats: async () => {
    const response = await axios.get<SchedulingStats>('/api/v1/admin/scheduling/stats')
    return response.data
  },
}
