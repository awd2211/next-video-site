/**
 * Centralized API endpoints configuration
 */

const API_BASE = '/api/v1'

export const API_ENDPOINTS = {
  // Authentication
  auth: {
    login: `${API_BASE}/auth/admin/login`,
    refresh: `${API_BASE}/auth/refresh`,
    captcha: `${API_BASE}/captcha/`,
  },

  // Admin endpoints
  admin: {
    // Videos
    videos: {
      list: `${API_BASE}/admin/videos`,
      detail: (id: number) => `${API_BASE}/admin/videos/${id}`,
      create: `${API_BASE}/admin/videos`,
      update: (id: number) => `${API_BASE}/admin/videos/${id}`,
      delete: (id: number) => `${API_BASE}/admin/videos/${id}`,
    },

    // Users
    users: {
      list: `${API_BASE}/admin/users`,
      detail: (id: number) => `${API_BASE}/admin/users/${id}`,
      ban: (id: number) => `${API_BASE}/admin/users/${id}/ban`,
    },

    // Comments
    comments: {
      list: `${API_BASE}/admin/comments`,
      detail: (id: number) => `${API_BASE}/admin/comments/${id}`,
      approve: (id: number) => `${API_BASE}/admin/comments/${id}/approve`,
      reject: (id: number) => `${API_BASE}/admin/comments/${id}/reject`,
      delete: (id: number) => `${API_BASE}/admin/comments/${id}`,
      batchApprove: `${API_BASE}/admin/comments/batch/approve`,
      batchReject: `${API_BASE}/admin/comments/batch/reject`,
      batchDelete: `${API_BASE}/admin/comments/batch`,
    },

    // Statistics
    stats: {
      overview: `${API_BASE}/admin/stats/overview`,
      trends: `${API_BASE}/admin/stats/trends`,
      videoTypes: `${API_BASE}/admin/stats/video-types`,
      topVideos: `${API_BASE}/admin/stats/top-videos`,
    },

    // Logs
    logs: {
      operations: `${API_BASE}/admin/logs/operations`,
      operationDetail: (id: number) => `${API_BASE}/admin/logs/operations/${id}`,
      modules: `${API_BASE}/admin/logs/operations/modules/list`,
      actions: `${API_BASE}/admin/logs/operations/actions/list`,
      stats: `${API_BASE}/admin/logs/operations/stats/summary`,
      cleanup: `${API_BASE}/admin/logs/operations/cleanup`,
      export: `${API_BASE}/admin/logs/operations/export`,
    },

    // Upload
    upload: {
      initMultipart: `${API_BASE}/admin/upload/init-multipart`,
      uploadChunk: `${API_BASE}/admin/upload/upload-chunk`,
      completeMultipart: `${API_BASE}/admin/upload/complete-multipart`,
      cancelUpload: (uploadId: string) => `${API_BASE}/admin/upload/cancel-upload/${uploadId}`,
    },

    // Banners
    banners: {
      list: `${API_BASE}/admin/banners`,
      detail: (id: number) => `${API_BASE}/admin/banners/${id}`,
      create: `${API_BASE}/admin/banners`,
      update: (id: number) => `${API_BASE}/admin/banners/${id}`,
      delete: (id: number) => `${API_BASE}/admin/banners/${id}`,
    },

    // Announcements
    announcements: {
      list: `${API_BASE}/admin/announcements`,
      detail: (id: number) => `${API_BASE}/admin/announcements/${id}`,
      create: `${API_BASE}/admin/announcements`,
      update: (id: number) => `${API_BASE}/admin/announcements/${id}`,
      delete: (id: number) => `${API_BASE}/admin/announcements/${id}`,
    },

    // Actors
    actors: {
      list: `${API_BASE}/admin/actors`,
      detail: (id: number) => `${API_BASE}/admin/actors/${id}`,
      create: `${API_BASE}/admin/actors`,
      update: (id: number) => `${API_BASE}/admin/actors/${id}`,
      delete: (id: number) => `${API_BASE}/admin/actors/${id}`,
    },

    // Directors
    directors: {
      list: `${API_BASE}/admin/directors`,
      detail: (id: number) => `${API_BASE}/admin/directors/${id}`,
      create: `${API_BASE}/admin/directors`,
      update: (id: number) => `${API_BASE}/admin/directors/${id}`,
      delete: (id: number) => `${API_BASE}/admin/directors/${id}`,
    },

    // Series
    series: {
      list: `${API_BASE}/admin/series`,
      detail: (id: number) => `${API_BASE}/admin/series/${id}`,
      create: `${API_BASE}/admin/series`,
      update: (id: number) => `${API_BASE}/admin/series/${id}`,
      delete: (id: number) => `${API_BASE}/admin/series/${id}`,
    },

    // IP Blacklist
    ipBlacklist: {
      list: `${API_BASE}/admin/ip-blacklist`,
      detail: (id: number) => `${API_BASE}/admin/ip-blacklist/${id}`,
      create: `${API_BASE}/admin/ip-blacklist`,
      delete: (id: number) => `${API_BASE}/admin/ip-blacklist/${id}`,
    },
  },

  // Public endpoints
  categories: `${API_BASE}/categories`,
  countries: `${API_BASE}/countries`,
  tags: `${API_BASE}/tags`,
}

export default API_ENDPOINTS

