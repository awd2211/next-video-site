import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface FavoriteFolder {
  id: number
  user_id: number
  name: string
  description?: string
  is_public: boolean
  is_default: boolean
  video_count: number
  created_at: string
  updated_at?: string
}

export interface FavoriteFolderWithVideos extends FavoriteFolder {
  videos: any[]
}

export interface CreateFolderData {
  name: string
  description?: string
  is_public?: boolean
}

export interface UpdateFolderData {
  name?: string
  description?: string
  is_public?: boolean
}

export interface MoveFavoriteData {
  favorite_id: number
  target_folder_id?: number
}

export interface BatchMoveFavoritesData {
  favorite_ids: number[]
  target_folder_id?: number
}

/**
 * Get all favorite folders for current user
 */
export const getFavoriteFolders = async (): Promise<FavoriteFolder[]> => {
  const token = localStorage.getItem('access_token')
  const response = await axios.get(`${API_BASE_URL}/api/v1/favorites/folders`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
  return response.data
}

/**
 * Get favorite folder details with videos
 */
export const getFavoriteFolderById = async (
  folderId: number,
  page: number = 1,
  pageSize: number = 20
): Promise<FavoriteFolderWithVideos> => {
  const token = localStorage.getItem('access_token')
  const response = await axios.get(
    `${API_BASE_URL}/api/v1/favorites/folders/${folderId}`,
    {
      params: { page, page_size: pageSize },
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  )
  return response.data
}

/**
 * Create a new favorite folder
 */
export const createFavoriteFolder = async (
  data: CreateFolderData
): Promise<FavoriteFolder> => {
  const token = localStorage.getItem('access_token')
  const response = await axios.post(
    `${API_BASE_URL}/api/v1/favorites/folders`,
    data,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  )
  return response.data
}

/**
 * Update favorite folder
 */
export const updateFavoriteFolder = async (
  folderId: number,
  data: UpdateFolderData
): Promise<FavoriteFolder> => {
  const token = localStorage.getItem('access_token')
  const response = await axios.put(
    `${API_BASE_URL}/api/v1/favorites/folders/${folderId}`,
    data,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  )
  return response.data
}

/**
 * Delete favorite folder
 */
export const deleteFavoriteFolder = async (
  folderId: number,
  moveToDefault: boolean = true
): Promise<void> => {
  const token = localStorage.getItem('access_token')
  await axios.delete(`${API_BASE_URL}/api/v1/favorites/folders/${folderId}`, {
    params: { move_to_default: moveToDefault },
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
}

/**
 * Move a favorite to another folder
 */
export const moveFavoriteToFolder = async (
  data: MoveFavoriteData
): Promise<void> => {
  const token = localStorage.getItem('access_token')
  await axios.post(`${API_BASE_URL}/api/v1/favorites/move`, data, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
}

/**
 * Batch move favorites to another folder
 */
export const batchMoveFavoritesToFolder = async (
  data: BatchMoveFavoritesData
): Promise<void> => {
  const token = localStorage.getItem('access_token')
  await axios.post(`${API_BASE_URL}/api/v1/favorites/batch-move`, data, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
}
