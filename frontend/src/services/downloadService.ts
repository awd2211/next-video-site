/**
 * Video Download Service
 * Handles video download functionality
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export interface DownloadUrlResponse {
  download_url: string
  expires_in: number
  quality: string
  file_size: number | null
  video_title: string
}

/**
 * Get video download URL
 *
 * @param videoId - Video ID
 * @param quality - Video quality (1080p/720p/480p/360p/original)
 * @returns Download URL and metadata
 */
export const getVideoDownloadUrl = async (
  videoId: number,
  quality: string = '720p'
): Promise<DownloadUrlResponse> => {
  const response = await axios.get<DownloadUrlResponse>(
    `${API_BASE_URL}/videos/${videoId}/download`,
    {
      params: { quality },
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    }
  )
  return response.data
}

/**
 * Download video file
 * Opens download in a new window/tab
 *
 * @param videoId - Video ID
 * @param quality - Video quality
 */
export const downloadVideo = async (videoId: number, quality: string = '720p') => {
  try {
    const data = await getVideoDownloadUrl(videoId, quality)

    // Open download URL in new window
    // Most browsers will start downloading automatically
    window.open(data.download_url, '_blank')

    return data
  } catch (error) {
    console.error('Download video failed:', error)
    throw error
  }
}

/**
 * Format file size to human-readable string
 *
 * @param bytes - File size in bytes
 * @returns Formatted string (e.g., "1.5 GB")
 */
export const formatFileSize = (bytes: number | null): string => {
  if (!bytes || bytes === 0) return 'Unknown'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

export default {
  getVideoDownloadUrl,
  downloadVideo,
  formatFileSize,
}
