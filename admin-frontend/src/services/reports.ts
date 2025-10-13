import axios from '@/utils/axios'

export interface ReportPeriod {
  start: string
  end: string
  days: number
}

export interface UserActivityReport {
  report_type: 'user_activity'
  period: ReportPeriod
  summary: {
    total_users: number
    new_users: number
    active_users: number
    vip_users: number
    active_rate: number
  }
  user_trend: Array<{ date: string; count: number }>
  behavior_stats: {
    total_watches: number
    total_comments: number
    total_favorites: number
    avg_watches_per_user: number
  }
}

export interface ContentPerformanceReport {
  report_type: 'content_performance'
  period: ReportPeriod
  summary: {
    total_videos: number
    new_videos: number
    total_views: number
    total_likes: number
    avg_views_per_video: number
  }
  video_trend: Array<{ date: string; count: number }>
  top_videos: Array<{
    id: number
    title: string
    video_type: string | null
    views: number
    likes: number
    favorites: number
    comments: number
    rating: number
    created_at: string
  }>
  type_distribution: Array<{ type: string; count: number }>
}

export interface VIPSubscriptionReport {
  report_type: 'vip_subscription'
  period: ReportPeriod
  summary: {
    total_vip: number
    new_vip: number
    expiring_soon: number
    expired: number
  }
  alerts: Array<string | null>
}

export interface ReportType {
  type: string
  name: string
  description: string
  icon: string
}

export const reportsService = {
  // Get available report types
  getReportTypes: async () => {
    const response = await axios.get<{ report_types: ReportType[] }>(
      '/api/v1/admin/reports/types'
    )
    return response.data.report_types
  },

  // Get user activity report
  getUserActivityReport: async (days: number = 30) => {
    const response = await axios.get<UserActivityReport>(
      '/api/v1/admin/reports/user-activity',
      { params: { days } }
    )
    return response.data
  },

  // Get content performance report
  getContentPerformanceReport: async (days: number = 30, limit: number = 20) => {
    const response = await axios.get<ContentPerformanceReport>(
      '/api/v1/admin/reports/content-performance',
      { params: { days, limit } }
    )
    return response.data
  },

  // Get VIP subscription report
  getVIPSubscriptionReport: async (days: number = 30) => {
    const response = await axios.get<VIPSubscriptionReport>(
      '/api/v1/admin/reports/vip-subscription',
      { params: { days } }
    )
    return response.data
  },

  // Export report to Excel
  exportExcel: async (reportType: string, days: number = 30) => {
    const response = await axios.get('/api/v1/admin/reports/export/excel', {
      params: { report_type: reportType, days },
      responseType: 'blob',
    })

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url

    // Extract filename from response headers or use default
    const contentDisposition = response.headers['content-disposition']
    const filename = contentDisposition
      ? contentDisposition.split('filename=')[1]?.replace(/"/g, '')
      : `${reportType}_${new Date().getTime()}.xlsx`

    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  },
}
