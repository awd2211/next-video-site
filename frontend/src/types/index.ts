export interface Video {
  id: number
  title: string
  slug: string
  description?: string
  video_type: string
  status: string
  poster_url?: string
  backdrop_url?: string
  video_url?: string
  trailer_url?: string
  release_year?: number
  release_date?: string
  duration?: number
  language?: string
  average_rating: number
  view_count: number
  like_count: number
  favorite_count: number
  comment_count: number
  rating_count: number
  is_featured: boolean
  is_recommended: boolean
  is_av1_available?: boolean  // Whether AV1 codec version is available
  created_at: string
  published_at?: string
  country?: Country
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
}

export interface Country {
  id: number
  name: string
  code: string
}

export interface Tag {
  id: number
  name: string
  slug: string
}

export interface Actor {
  id: number
  name: string
  avatar?: string
  role_name?: string
}

export interface Director {
  id: number
  name: string
  avatar?: string
}

export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  avatar?: string
  is_active: boolean
  is_verified: boolean
  is_vip: boolean
  vip_expires_at?: string
  created_at: string
  last_login_at?: string
}

export interface PaginatedResponse<T> {
  total: number
  page: number
  page_size: number
  pages: number
  items: T[]
}
