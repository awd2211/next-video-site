/**
 * Enum definitions for standardized status values
 */

// Video status enum - 匹配后端大写值
export enum VideoStatus {
  DRAFT = 'DRAFT',
  PUBLISHED = 'PUBLISHED',
  ARCHIVED = 'ARCHIVED',
}

// Video type enum - 匹配后端小写值
export enum VideoType {
  MOVIE = 'movie',
  TV_SERIES = 'tv_series',
  ANIME = 'anime',
  DOCUMENTARY = 'documentary',
}

// Comment status enum - using uppercase to match backend
export enum CommentStatus {
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
}

// User role enum
export enum UserRole {
  USER = 'user',
  ADMIN = 'admin',
  SUPERADMIN = 'superadmin',
}

// Banner position enum
export enum BannerPosition {
  HOME_TOP = 'home_top',
  HOME_MIDDLE = 'home_middle',
  HOME_BOTTOM = 'home_bottom',
  SIDEBAR = 'sidebar',
}

// Announcement type enum
export enum AnnouncementType {
  INFO = 'info',
  WARNING = 'warning',
  SUCCESS = 'success',
  ERROR = 'error',
}

// Operation log action enum
export enum OperationAction {
  CREATE = 'create',
  UPDATE = 'update',
  DELETE = 'delete',
  LOGIN = 'login',
  LOGOUT = 'logout',
  VIEW = 'view',
  CLEANUP = 'cleanup',
}

// HTTP method enum
export enum HttpMethod {
  GET = 'GET',
  POST = 'POST',
  PUT = 'PUT',
  DELETE = 'DELETE',
  PATCH = 'PATCH',
}

// Status display configuration
export const VIDEO_STATUS_CONFIG = {
  [VideoStatus.DRAFT]: { color: 'default', text: '草稿' },
  [VideoStatus.PUBLISHED]: { color: 'green', text: '已发布' },
  [VideoStatus.ARCHIVED]: { color: 'orange', text: '已归档' },
} as const

export const VIDEO_TYPE_CONFIG = {
  [VideoType.MOVIE]: { text: '电影' },
  [VideoType.TV_SERIES]: { text: '电视剧' },
  [VideoType.ANIME]: { text: '动漫' },
  [VideoType.DOCUMENTARY]: { text: '纪录片' },
} as const

export const COMMENT_STATUS_CONFIG = {
  [CommentStatus.PENDING]: { color: 'gold', text: '待审核' },
  [CommentStatus.APPROVED]: { color: 'green', text: '已通过' },
  [CommentStatus.REJECTED]: { color: 'red', text: '已拒绝' },
} as const

export const OPERATION_ACTION_COLOR_MAP = {
  [OperationAction.CREATE]: 'green',
  [OperationAction.UPDATE]: 'orange',
  [OperationAction.DELETE]: 'red',
  [OperationAction.LOGIN]: 'cyan',
  [OperationAction.LOGOUT]: 'default',
  [OperationAction.VIEW]: 'geekblue',
  [OperationAction.CLEANUP]: 'purple',
} as const

export const HTTP_METHOD_COLOR_MAP = {
  [HttpMethod.GET]: 'default',
  [HttpMethod.POST]: 'green',
  [HttpMethod.PUT]: 'orange',
  [HttpMethod.DELETE]: 'red',
  [HttpMethod.PATCH]: 'purple',
} as const

