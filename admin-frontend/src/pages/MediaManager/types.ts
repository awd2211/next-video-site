/**
 * MediaManager 相关类型定义
 */

export interface MediaItem {
  id: number
  title: string
  description?: string
  filename: string
  file_path: string
  file_size: number
  mime_type: string
  media_type: 'image' | 'video'
  status: string
  width?: number
  height?: number
  duration?: number
  url: string
  thumbnail_url?: string
  parent_id?: number
  path?: string
  is_folder: boolean
  tags?: string
  view_count: number
  download_count: number
  created_at: string
  updated_at?: string
}

export interface FolderNode {
  id: number
  title: string
  parent_id?: number
  path: string
  children_count: number
  children: FolderNode[]
  created_at: string
}

export interface UploadTask {
  id: string
  file: File
  status: 'pending' | 'uploading' | 'completed' | 'error' | 'paused'
  progress: number
  error?: string
  mediaId?: number
  url?: string
  uploadedSize?: number
  totalSize?: number
  speed?: number
  startTime?: number
  estimatedTime?: number
}

export interface MediaTreeResponse {
  tree: FolderNode[]
  parent_id?: number
}

export interface MediaListParams {
  page?: number
  page_size?: number
  parent_id?: number
  media_type?: 'image' | 'video'
  search?: string
}

export interface MediaListResponse {
  items: MediaItem[]
  total: number
  page: number
  page_size: number
  pages: number
}
