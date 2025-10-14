/**
 * Common type definitions used across the application
 */

export interface PaginatedResponse<T> {
  total: number
  page: number
  page_size: number
  items: T[]
}

export interface ApiError {
  detail: string | Record<string, string>[]
  status?: number
}

// 使用大写匹配后端 VideoStatus 枚举
export type VideoStatus = 'DRAFT' | 'PUBLISHED' | 'ARCHIVED'
export type VideoType = 'movie' | 'tv_series' | 'anime' | 'documentary'
export type CommentStatus = 'PENDING' | 'APPROVED' | 'REJECTED'
export type UserRole = 'user' | 'admin' | 'superadmin'

export interface SelectOption {
  label: string
  value: string | number
}

export interface DateRange {
  start: string
  end: string
}

