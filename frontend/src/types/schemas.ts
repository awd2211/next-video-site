/**
 * Zod Schemas for Runtime Type Validation
 * Provides type-safe validation for API responses
 */
import { z } from 'zod'

// Category Schema
export const CategorySchema = z.object({
  id: z.number(),
  name: z.string(),
  slug: z.string(),
  description: z.string().optional(),
})

// Country Schema
export const CountrySchema = z.object({
  id: z.number(),
  name: z.string(),
  code: z.string(),
})

// Tag Schema
export const TagSchema = z.object({
  id: z.number(),
  name: z.string(),
  slug: z.string(),
})

// Actor Schema
export const ActorSchema = z.object({
  id: z.number(),
  name: z.string(),
  avatar: z.string().optional(),
  role_name: z.string().optional(),
})

// Director Schema
export const DirectorSchema = z.object({
  id: z.number(),
  name: z.string(),
  avatar: z.string().optional(),
})

// Video Schema - matches existing Video interface
export const VideoSchema = z.object({
  id: z.number(),
  title: z.string(),
  slug: z.string(),
  description: z.string().optional(),
  video_type: z.string(),
  status: z.string(),
  poster_url: z.string().optional(),
  backdrop_url: z.string().optional(),
  video_url: z.string().optional(),
  trailer_url: z.string().optional(),
  release_year: z.number().optional(),
  release_date: z.string().optional(),
  duration: z.number().optional(),
  language: z.string().optional(),
  average_rating: z.number(),
  view_count: z.number(),
  like_count: z.number(),
  favorite_count: z.number(),
  comment_count: z.number(),
  rating_count: z.number(),
  is_featured: z.boolean(),
  is_recommended: z.boolean(),
  is_av1_available: z.boolean().optional(),
  created_at: z.string(),
  published_at: z.string().optional(),
  country: CountrySchema.optional(),
  categories: z.array(CategorySchema).optional(),
  tags: z.array(TagSchema).optional(),
  actors: z.array(ActorSchema).optional(),
  directors: z.array(DirectorSchema).optional(),
})

// User Schema - matches existing User interface
export const UserSchema = z.object({
  id: z.number(),
  email: z.string().email(),
  username: z.string(),
  full_name: z.string().optional(),
  avatar: z.string().optional(),
  is_active: z.boolean(),
  is_verified: z.boolean(),
  is_vip: z.boolean(),
  vip_expires_at: z.string().optional(),
  created_at: z.string(),
  last_login_at: z.string().optional(),
})

// Paginated Response Schema
export const PaginatedResponseSchema = <T extends z.ZodTypeAny>(itemSchema: T) =>
  z.object({
    items: z.array(itemSchema),
    total: z.number(),
    page: z.number(),
    pages: z.number(),
    page_size: z.number(),
  })

// Comment Schema
export const CommentSchema = z.object({
  id: z.number(),
  content: z.string(),
  user_id: z.number(),
  video_id: z.number(),
  created_at: z.string(),
  user: UserSchema.optional(),
})

// Rating Schema
export const RatingSchema = z.object({
  id: z.number(),
  score: z.number().min(1).max(5),
  user_id: z.number(),
  video_id: z.number(),
  created_at: z.string().optional(),
})

// Watch History Schema
export const WatchHistorySchema = z.object({
  id: z.number(),
  video_id: z.number(),
  user_id: z.number(),
  last_position: z.number(),
  watch_duration: z.number(),
  is_completed: z.boolean(),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
  video: VideoSchema.optional(),
})

// Favorite Folder Schema
export const FavoriteFolderSchema = z.object({
  id: z.number(),
  name: z.string(),
  description: z.string().optional(),
  is_default: z.boolean(),
  video_count: z.number().optional(),
  created_at: z.string().optional(),
})

// Auth Response Schema
export const AuthResponseSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.string().default('bearer'),
  user: UserSchema.optional(),
})

// Export type inference (for reference, but use existing types from @/types/index.ts)
// Note: These are mainly for runtime validation, not replacing existing types

