/**
 * 收藏夹服务测试
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  getFavoriteFolders,
  getFavoriteFolderById,
  createFavoriteFolder,
  updateFavoriteFolder,
  deleteFavoriteFolder,
  moveFavoriteToFolder,
  batchMoveFavoritesToFolder,
} from '../favoriteFolderService'
import axios from 'axios'

vi.mock('axios')

describe('Favorite Folder Service', () => {
  const mockAxios = vi.mocked(axios)

  beforeEach(() => {
    vi.clearAllMocks()
    
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: vi.fn().mockReturnValue('test-access-token'),
      },
      writable: true,
    })

    // Mock environment variable
    vi.stubEnv('VITE_API_BASE_URL', 'https://api.example.com')
  })

  afterEach(() => {
    vi.unstubAllEnvs()
  })

  describe('getFavoriteFolders', () => {
    it('should fetch all favorite folders', async () => {
      const mockFolders = [
        {
          id: 1,
          user_id: 1,
          name: 'Default',
          is_public: false,
          is_default: true,
          video_count: 10,
          created_at: '2024-01-01T00:00:00Z',
        },
        {
          id: 2,
          user_id: 1,
          name: 'Action Movies',
          description: 'My favorite action movies',
          is_public: true,
          is_default: false,
          video_count: 5,
          created_at: '2024-01-02T00:00:00Z',
        },
      ]

      mockAxios.get.mockResolvedValue({ data: mockFolders })

      const result = await getFavoriteFolders()

      expect(mockAxios.get).toHaveBeenCalledWith(
        'https://api.example.com/api/v1/favorites/folders',
        {
          headers: { Authorization: 'Bearer test-access-token' },
        }
      )
      expect(result).toHaveLength(2)
      expect(result[0].is_default).toBe(true)
      expect(result[1].name).toBe('Action Movies')
    })

    it('should handle empty folders list', async () => {
      mockAxios.get.mockResolvedValue({ data: [] })

      const result = await getFavoriteFolders()

      expect(result).toHaveLength(0)
    })

    it('should handle unauthorized access', async () => {
      mockAxios.get.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      })

      await expect(getFavoriteFolders()).rejects.toMatchObject({
        response: { status: 401 },
      })
    })
  })

  describe('getFavoriteFolderById', () => {
    it('should fetch folder with videos', async () => {
      const mockFolderWithVideos = {
        id: 1,
        user_id: 1,
        name: 'Comedy Collection',
        description: 'Funny movies',
        is_public: false,
        is_default: false,
        video_count: 3,
        created_at: '2024-01-01T00:00:00Z',
        videos: [
          { id: 1, title: 'Comedy 1', poster_url: 'poster1.jpg' },
          { id: 2, title: 'Comedy 2', poster_url: 'poster2.jpg' },
        ],
      }

      mockAxios.get.mockResolvedValue({ data: mockFolderWithVideos })

      const result = await getFavoriteFolderById(1)

      expect(mockAxios.get).toHaveBeenCalledWith(
        'https://api.example.com/api/v1/favorites/folders/1',
        {
          params: { page: 1, page_size: 20 },
          headers: { Authorization: 'Bearer test-access-token' },
        }
      )
      expect(result.videos).toHaveLength(2)
      expect(result.name).toBe('Comedy Collection')
    })

    it('should fetch with custom pagination', async () => {
      mockAxios.get.mockResolvedValue({
        data: { id: 1, name: 'Test', videos: [] },
      })

      await getFavoriteFolderById(1, 2, 10)

      expect(mockAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/folders/1'),
        expect.objectContaining({
          params: { page: 2, page_size: 10 },
        })
      )
    })

    it('should handle folder not found', async () => {
      mockAxios.get.mockRejectedValue({
        response: { status: 404, data: { detail: 'Folder not found' } },
      })

      await expect(getFavoriteFolderById(999)).rejects.toMatchObject({
        response: { status: 404 },
      })
    })
  })

  describe('createFavoriteFolder', () => {
    it('should create a new folder', async () => {
      const folderData = {
        name: 'New Folder',
        description: 'My new collection',
        is_public: false,
      }

      const mockCreatedFolder = {
        id: 3,
        user_id: 1,
        name: 'New Folder',
        description: 'My new collection',
        is_public: false,
        is_default: false,
        video_count: 0,
        created_at: '2024-01-03T00:00:00Z',
      }

      mockAxios.post.mockResolvedValue({ data: mockCreatedFolder })

      const result = await createFavoriteFolder(folderData)

      expect(mockAxios.post).toHaveBeenCalledWith(
        'https://api.example.com/api/v1/favorites/folders',
        folderData,
        { headers: { Authorization: 'Bearer test-access-token' } }
      )
      expect(result.name).toBe('New Folder')
      expect(result.video_count).toBe(0)
    })

    it('should handle validation errors', async () => {
      mockAxios.post.mockRejectedValue({
        response: { status: 422, data: { detail: 'Name is required' } },
      })

      await expect(createFavoriteFolder({ name: '' })).rejects.toMatchObject({
        response: { status: 422 },
      })
    })
  })

  describe('updateFavoriteFolder', () => {
    it('should update folder', async () => {
      const updateData = { name: 'Updated Name', is_public: true }
      const mockUpdatedFolder = {
        id: 1,
        user_id: 1,
        name: 'Updated Name',
        is_public: true,
        is_default: false,
        video_count: 5,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-03T00:00:00Z',
      }

      mockAxios.put.mockResolvedValue({ data: mockUpdatedFolder })

      const result = await updateFavoriteFolder(1, updateData)

      expect(mockAxios.put).toHaveBeenCalledWith(
        'https://api.example.com/api/v1/favorites/folders/1',
        updateData,
        { headers: { Authorization: 'Bearer test-access-token' } }
      )
      expect(result.name).toBe('Updated Name')
      expect(result.is_public).toBe(true)
    })

    it('should handle folder not found', async () => {
      mockAxios.put.mockRejectedValue({
        response: { status: 404, data: { detail: 'Folder not found' } },
      })

      await expect(updateFavoriteFolder(999, { name: 'Test' })).rejects.toMatchObject({
        response: { status: 404 },
      })
    })
  })

  describe('deleteFavoriteFolder', () => {
    it('should delete folder with default move behavior', async () => {
      mockAxios.delete.mockResolvedValue({ data: null })

      await deleteFavoriteFolder(1)

      expect(mockAxios.delete).toHaveBeenCalledWith(
        'https://api.example.com/api/v1/favorites/folders/1',
        {
          params: { move_to_default: true },
          headers: { Authorization: 'Bearer test-access-token' },
        }
      )
    })

    it('should delete folder without moving to default', async () => {
      mockAxios.delete.mockResolvedValue({ data: null })

      await deleteFavoriteFolder(1, false)

      expect(mockAxios.delete).toHaveBeenCalledWith(
        expect.stringContaining('/folders/1'),
        expect.objectContaining({
          params: { move_to_default: false },
        })
      )
    })

    it('should handle deletion of default folder', async () => {
      mockAxios.delete.mockRejectedValue({
        response: { status: 400, data: { detail: 'Cannot delete default folder' } },
      })

      await expect(deleteFavoriteFolder(1)).rejects.toMatchObject({
        response: { status: 400 },
      })
    })
  })

  describe('moveFavoriteToFolder', () => {
    it('should move favorite to another folder', async () => {
      mockAxios.post.mockResolvedValue({ data: null })

      await moveFavoriteToFolder({ favorite_id: 5, target_folder_id: 2 })

      expect(mockAxios.post).toHaveBeenCalledWith(
        'https://api.example.com/api/v1/favorites/move',
        { favorite_id: 5, target_folder_id: 2 },
        { headers: { Authorization: 'Bearer test-access-token' } }
      )
    })

    it('should move favorite to default folder', async () => {
      mockAxios.post.mockResolvedValue({ data: null })

      await moveFavoriteToFolder({ favorite_id: 5 })

      expect(mockAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/favorites/move'),
        { favorite_id: 5 },
        expect.any(Object)
      )
    })

    it('should handle favorite not found', async () => {
      mockAxios.post.mockRejectedValue({
        response: { status: 404, data: { detail: 'Favorite not found' } },
      })

      await expect(
        moveFavoriteToFolder({ favorite_id: 999, target_folder_id: 1 })
      ).rejects.toMatchObject({
        response: { status: 404 },
      })
    })
  })

  describe('batchMoveFavoritesToFolder', () => {
    it('should batch move favorites to folder', async () => {
      mockAxios.post.mockResolvedValue({ data: null })

      await batchMoveFavoritesToFolder({
        favorite_ids: [1, 2, 3],
        target_folder_id: 5,
      })

      expect(mockAxios.post).toHaveBeenCalledWith(
        'https://api.example.com/api/v1/favorites/batch-move',
        { favorite_ids: [1, 2, 3], target_folder_id: 5 },
        { headers: { Authorization: 'Bearer test-access-token' } }
      )
    })

    it('should batch move favorites to default folder', async () => {
      mockAxios.post.mockResolvedValue({ data: null })

      await batchMoveFavoritesToFolder({ favorite_ids: [1, 2] })

      expect(mockAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/favorites/batch-move'),
        { favorite_ids: [1, 2] },
        expect.any(Object)
      )
    })

    it('should handle empty favorite IDs array', async () => {
      mockAxios.post.mockRejectedValue({
        response: { status: 400, data: { detail: 'No favorites selected' } },
      })

      await expect(
        batchMoveFavoritesToFolder({ favorite_ids: [] })
      ).rejects.toMatchObject({
        response: { status: 400 },
      })
    })
  })
})
