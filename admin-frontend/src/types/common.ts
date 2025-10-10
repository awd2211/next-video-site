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

export type VideoStatus = 'draft' | 'published' | 'archived'
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

