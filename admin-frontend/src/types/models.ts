/**
 * Data model type definitions
 */

import { VideoStatus, VideoType, CommentStatus } from './common'

export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  is_active: boolean
  is_vip: boolean
  vip_expires_at?: string
  created_at: string
  last_login_at?: string
}

export interface AdminUser {
  id: number
  email: string
  username: string
  full_name?: string
  is_active: boolean
  is_superadmin: boolean
  created_at: string
}

export interface Video {
  id: number
  title: string
  original_title?: string
  description?: string
  video_url: string
  poster_url?: string
  backdrop_url?: string
  trailer_url?: string
  duration?: number
  view_count: number
  average_rating?: number
  rating_count?: number
  status: VideoStatus
  video_type: VideoType
  release_year?: number
  release_date?: string
  language?: string
  country_id?: number
  total_seasons?: number
  total_episodes?: number
  created_at: string
  updated_at: string
  categories?: Category[]
  tags?: Tag[]
  actors?: Actor[]
  directors?: Director[]
}

export interface Category {
  id: number
  name: string
  slug: string
  description?: string
  icon?: string
  sort_order?: number
}

export interface Tag {
  id: number
  name: string
  slug: string
}

export interface Country {
  id: number
  name: string
  code: string
}

export interface Actor {
  id: number
  name: string
  avatar_url?: string
  bio?: string
  birth_date?: string
  nationality?: string
}

export interface Director {
  id: number
  name: string
  avatar_url?: string
  bio?: string
  birth_date?: string
  nationality?: string
}

export interface Comment {
  id: number
  user_id: number
  video_id: number
  content: string
  rating?: number
  status: CommentStatus
  like_count: number
  created_at: string
  updated_at: string
  user?: User
  video?: Video
}

export interface Banner {
  id: number
  title: string
  image_url: string
  link_url?: string
  position: string
  is_active: boolean
  sort_order: number
  start_time?: string
  end_time?: string
  created_at: string
}

export interface Announcement {
  id: number
  title: string
  content: string
  type: string
  is_active: boolean
  start_time?: string
  end_time?: string
  created_at: string
}

export interface Series {
  id: number
  name: string
  description?: string
  poster_url?: string
  backdrop_url?: string
  total_videos: number
  created_at: string
}

export interface IPBlacklist {
  id: number
  ip_address: string
  reason?: string
  expires_at?: string
  created_at: string
  created_by?: number
}

export interface OperationLog {
  id: number
  admin_user_id: number
  admin_user?: AdminUser
  module: string
  action: string
  description: string
  ip_address: string
  user_agent: string
  request_method: string
  request_url: string
  request_data?: string
  created_at: string
}

export interface Statistics {
  total_users: number
  total_videos: number
  total_comments: number
  total_views: number
}

