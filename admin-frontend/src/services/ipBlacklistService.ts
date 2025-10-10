/**
 * IP黑名单服务
 */
import api from '../utils/axios'

export interface IPBlacklistItem {
  ip: string
  reason: string
  banned_at: string
  expires_at?: string
  is_permanent: boolean
}

export interface IPBlacklistListResponse {
  total: number
  items: IPBlacklistItem[]
}

export interface IPBlacklistStats {
  total_blacklisted: number
  permanent_count: number
  temporary_count: number
  auto_banned_count: number
}

export interface AddIPBlacklistRequest {
  ip: string
  reason: string
  duration?: number // 秒, 不传表示永久封禁
}

const ipBlacklistService = {
  // 获取黑名单列表
  getList: async (params: { page?: number; page_size?: number; search?: string }) => {
    const response = await api.get<IPBlacklistListResponse>('/admin/ip-blacklist/', { params })
    return response.data
  },

  // 获取统计信息
  getStats: async () => {
    const response = await api.get<IPBlacklistStats>('/admin/ip-blacklist/stats/summary')
    return response.data
  },

  // 添加IP到黑名单
  add: async (data: AddIPBlacklistRequest) => {
    const response = await api.post<IPBlacklistItem>('/admin/ip-blacklist/', data)
    return response.data
  },

  // 从黑名单移除IP
  remove: async (ip: string) => {
    await api.delete(`/admin/ip-blacklist/${ip}`)
  },

  // 批量移除IP
  batchRemove: async (ips: string[]) => {
    const response = await api.post('/admin/ip-blacklist/batch-remove', ips)
    return response.data
  },

  // 查询IP状态
  checkIP: async (ip: string) => {
    const response = await api.get<IPBlacklistItem>(`/admin/ip-blacklist/${ip}`)
    return response.data
  },
}

export default ipBlacklistService
