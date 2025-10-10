import api from '@/utils/axios'

export interface Subtitle {
  id: number
  video_id: number
  language: string
  language_name: string
  file_url: string
  format: string
  is_default: boolean
  is_auto_generated: boolean
  sort_order: number
  created_at: string
  updated_at?: string
}

export interface SubtitleListResponse {
  subtitles: Subtitle[]
  total: number
}

const subtitleService = {
  // 获取视频字幕列表 (公开API)
  getVideoSubtitles: async (videoId: number): Promise<SubtitleListResponse> => {
    const response = await api.get(`/videos/${videoId}/subtitles`)
    return response.data
  },
}

export default subtitleService
