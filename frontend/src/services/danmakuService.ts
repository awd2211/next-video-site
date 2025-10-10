import api from './api'

export type DanmakuType = 'scroll' | 'top' | 'bottom'

export interface Danmaku {
  id: number
  video_id: number
  user_id: number
  content: string
  time: number  // 出现时间(秒)
  type: DanmakuType
  color: string
  font_size: number
  status: string
  is_blocked: boolean
  report_count: number
  created_at: string
}

export interface DanmakuCreate {
  video_id: number
  content: string
  time: number
  type?: DanmakuType
  color?: string
  font_size?: number
}

export interface DanmakuListResponse {
  total: number
  items: Danmaku[]
}

export const danmakuService = {
  /**
   * 发送弹幕
   */
  send: async (data: DanmakuCreate): Promise<Danmaku> => {
    const response = await api.post('/danmaku/', data)
    return response.data
  },

  /**
   * 获取视频弹幕
   */
  getVideoDanmaku: async (
    videoId: number,
    startTime?: number,
    endTime?: number
  ): Promise<DanmakuListResponse> => {
    const params: any = {}
    if (startTime !== undefined) params.start_time = startTime
    if (endTime !== undefined) params.end_time = endTime

    const response = await api.get(`/danmaku/video/${videoId}`, { params })
    return response.data
  },

  /**
   * 删除自己的弹幕
   */
  deleteMyDanmaku: async (danmakuId: number): Promise<void> => {
    await api.delete(`/danmaku/${danmakuId}`)
  },

  /**
   * 举报弹幕
   */
  report: async (danmakuId: number): Promise<{ message: string; report_count: number }> => {
    const response = await api.post(`/danmaku/${danmakuId}/report`)
    return response.data
  },

  /**
   * 获取我发送的弹幕
   */
  getMyDanmaku: async (
    videoId?: number,
    page: number = 1,
    pageSize: number = 20
  ): Promise<Danmaku[]> => {
    const params: any = { page, page_size: pageSize }
    if (videoId) params.video_id = videoId

    const response = await api.get('/danmaku/my-danmaku', { params })
    return response.data
  },
}
