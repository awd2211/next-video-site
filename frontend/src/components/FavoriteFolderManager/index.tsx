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
import { sanitizeInput } from '@/utils/security'
import { VALIDATION_LIMITS } from '@/utils/validationConfig'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import './styles.css'

interface FavoriteFolderManagerProps {
  onSelectFolder?: (folderId: number) => void
  selectedFolderId?: number
}

const FavoriteFolderManager: React.FC<FavoriteFolderManagerProps> = ({
  onSelectFolder,
  selectedFolderId,
}) => {
  const { t } = useTranslation()
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
      toast.error(t('favorites.loadFailed'))
    } finally {
      setLoading(false)
    }
  }

  const handleCreateFolder = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // 验证和清理输入
    const cleanedName = sanitizeInput(formData.name, VALIDATION_LIMITS.TITLE.max)
    const cleanedDescription = sanitizeInput(formData.description, VALIDATION_LIMITS.DESCRIPTION.max)
    
    if (!cleanedName.trim()) {
      toast.error(t('favorites.nameRequired'))
      return
    }
    
    if (cleanedName.length > VALIDATION_LIMITS.TITLE.max) {
      toast.error(t('validation.maxLength', { max: VALIDATION_LIMITS.TITLE.max }))
      return
    }
    
    try {
      await createFavoriteFolder({
        name: cleanedName,
        description: cleanedDescription || undefined,
        is_public: formData.is_public,
      })
      setFormData({ name: '', description: '', is_public: false })
      setShowCreateForm(false)
      toast.success(t('favorites.createSuccess'))
      await loadFolders()
    } catch (error: any) {
      console.error('Failed to create folder:', error)
      toast.error(error.response?.data?.detail || t('favorites.createFailed'))
    }
  }

  const handleUpdateFolder = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingFolder) return

    // 验证和清理输入
    const cleanedName = sanitizeInput(formData.name, VALIDATION_LIMITS.TITLE.max)
    const cleanedDescription = sanitizeInput(formData.description, VALIDATION_LIMITS.DESCRIPTION.max)
    
    if (!cleanedName.trim()) {
      toast.error(t('favorites.nameRequired'))
      return
    }

    try {
      await updateFavoriteFolder(editingFolder.id, {
        name: cleanedName,
        description: cleanedDescription || undefined,
        is_public: formData.is_public,
      })
      setEditingFolder(null)
      setFormData({ name: '', description: '', is_public: false })
      toast.success(t('favorites.updateSuccess'))
      await loadFolders()
    } catch (error: any) {
      console.error('Failed to update folder:', error)
      toast.error(error.response?.data?.detail || t('favorites.updateFailed'))
    }
  }

  const handleDeleteFolder = async (folderId: number) => {
    if (!confirm(t('favorites.deleteConfirm'))) return

    try {
      await deleteFavoriteFolder(folderId, true)
      toast.success(t('favorites.deleteSuccess'))
      await loadFolders()
    } catch (error: any) {
      console.error('Failed to delete folder:', error)
      toast.error(error.response?.data?.detail || t('favorites.deleteFailed'))
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
          <h3>{editingFolder ? t('favorites.editFolder') : t('favorites.createFolder')}</h3>
          <div className="form-group">
            <label>{t('favorites.folderName')} *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              maxLength={VALIDATION_LIMITS.TITLE.max}
              placeholder={t('favorites.folderNamePlaceholder')}
            />
            <div className="char-count">
              {formData.name.length}/{VALIDATION_LIMITS.TITLE.max}
            </div>
          </div>
          <div className="form-group">
            <label>{t('favorites.folderDescription')}</label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              maxLength={VALIDATION_LIMITS.DESCRIPTION.max}
              placeholder={t('favorites.folderDescriptionPlaceholder')}
              rows={3}
            />
            <div className="char-count">
              {formData.description.length}/{VALIDATION_LIMITS.DESCRIPTION.max}
            </div>
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
              <span>{t('favorites.publicFolder')}</span>
            </label>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-submit">
              {editingFolder ? t('common.save') : t('common.create')}
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
