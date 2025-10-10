/**
 * Favorite Folder Manager Component
 * Manages user's favorite folders
 */
import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  getFavoriteFolders,
  createFavoriteFolder,
  updateFavoriteFolder,
  deleteFavoriteFolder,
  FavoriteFolder,
} from '../../services/favoriteFolderService'
import './styles.css'

interface FavoriteFolderManagerProps {
  onSelectFolder?: (folderId: number) => void
  selectedFolderId?: number
}

const FavoriteFolderManager: React.FC<FavoriteFolderManagerProps> = ({
  onSelectFolder,
  selectedFolderId,
}) => {
  const navigate = useNavigate()
  const [folders, setFolders] = useState<FavoriteFolder[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [editingFolder, setEditingFolder] = useState<FavoriteFolder | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    is_public: false,
  })

  useEffect(() => {
    loadFolders()
  }, [])

  const loadFolders = async () => {
    try {
      setLoading(true)
      const data = await getFavoriteFolders()
      setFolders(data)
    } catch (error) {
      console.error('Failed to load folders:', error)
      alert('加载收藏夹失败')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateFolder = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await createFavoriteFolder({
        name: formData.name,
        description: formData.description || undefined,
        is_public: formData.is_public,
      })
      setFormData({ name: '', description: '', is_public: false })
      setShowCreateForm(false)
      await loadFolders()
    } catch (error: any) {
      console.error('Failed to create folder:', error)
      alert(error.response?.data?.detail || '创建收藏夹失败')
    }
  }

  const handleUpdateFolder = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingFolder) return

    try {
      await updateFavoriteFolder(editingFolder.id, {
        name: formData.name,
        description: formData.description || undefined,
        is_public: formData.is_public,
      })
      setEditingFolder(null)
      setFormData({ name: '', description: '', is_public: false })
      await loadFolders()
    } catch (error: any) {
      console.error('Failed to update folder:', error)
      alert(error.response?.data?.detail || '更新收藏夹失败')
    }
  }

  const handleDeleteFolder = async (folderId: number) => {
    if (!confirm('确定要删除这个收藏夹吗？视频将移动到默认收藏夹。')) return

    try {
      await deleteFavoriteFolder(folderId, true)
      await loadFolders()
    } catch (error: any) {
      console.error('Failed to delete folder:', error)
      alert(error.response?.data?.detail || '删除收藏夹失败')
    }
  }

  const startEdit = (folder: FavoriteFolder) => {
    setEditingFolder(folder)
    setFormData({
      name: folder.name,
      description: folder.description || '',
      is_public: folder.is_public,
    })
  }

  const cancelEdit = () => {
    setEditingFolder(null)
    setFormData({ name: '', description: '', is_public: false })
  }

  const viewFolderVideos = (folderId: number) => {
    navigate(`/favorites/folders/${folderId}`)
  }

  if (loading) {
    return <div className="folder-manager-loading">加载中...</div>
  }

  return (
    <div className="favorite-folder-manager">
      <div className="folder-manager-header">
        <h2>我的收藏夹</h2>
        {!showCreateForm && !editingFolder && (
          <button
            className="btn-create-folder"
            onClick={() => setShowCreateForm(true)}
          >
            + 新建收藏夹
          </button>
        )}
      </div>

      {/* Create/Edit Form */}
      {(showCreateForm || editingFolder) && (
        <form
          className="folder-form"
          onSubmit={editingFolder ? handleUpdateFolder : handleCreateFolder}
        >
          <h3>{editingFolder ? '编辑收藏夹' : '新建收藏夹'}</h3>
          <div className="form-group">
            <label>名称 *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              maxLength={100}
              placeholder="收藏夹名称"
            />
          </div>
          <div className="form-group">
            <label>描述</label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              maxLength={500}
              placeholder="收藏夹描述（可选）"
              rows={3}
            />
          </div>
          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={formData.is_public}
                onChange={(e) =>
                  setFormData({ ...formData, is_public: e.target.checked })
                }
              />
              <span>公开（其他用户可见）</span>
            </label>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-submit">
              {editingFolder ? '保存' : '创建'}
            </button>
            <button
              type="button"
              className="btn-cancel"
              onClick={() => {
                if (editingFolder) {
                  cancelEdit()
                } else {
                  setShowCreateForm(false)
                  setFormData({ name: '', description: '', is_public: false })
                }
              }}
            >
              取消
            </button>
          </div>
        </form>
      )}

      {/* Folder List */}
      <div className="folder-list">
        {folders.map((folder) => (
          <div
            key={folder.id}
            className={`folder-item ${
              selectedFolderId === folder.id ? 'selected' : ''
            }`}
            onClick={() => onSelectFolder && onSelectFolder(folder.id)}
          >
            <div className="folder-icon">
              {folder.is_default ? '📁' : folder.is_public ? '🌐' : '📂'}
            </div>
            <div className="folder-info">
              <h4 className="folder-name">
                {folder.name}
                {folder.is_default && <span className="badge-default">默认</span>}
              </h4>
              {folder.description && (
                <p className="folder-description">{folder.description}</p>
              )}
              <p className="folder-meta">
                {folder.video_count} 个视频 · 创建于{' '}
                {new Date(folder.created_at).toLocaleDateString()}
              </p>
            </div>
            <div className="folder-actions">
              <button
                className="btn-action"
                onClick={(e) => {
                  e.stopPropagation()
                  viewFolderVideos(folder.id)
                }}
              >
                查看
              </button>
              {!folder.is_default && (
                <>
                  <button
                    className="btn-action"
                    onClick={(e) => {
                      e.stopPropagation()
                      startEdit(folder)
                    }}
                  >
                    编辑
                  </button>
                  <button
                    className="btn-action btn-danger"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDeleteFolder(folder.id)
                    }}
                  >
                    删除
                  </button>
                </>
              )}
            </div>
          </div>
        ))}

        {folders.length === 0 && (
          <div className="folder-empty">
            <p>还没有收藏夹，创建一个吧！</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default FavoriteFolderManager
