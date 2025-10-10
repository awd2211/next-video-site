/**
 * Folder Selector Component
 * Select a favorite folder when adding to favorites
 */
import React, { useState, useEffect } from 'react'
import { getFavoriteFolders, FavoriteFolder } from '../../services/favoriteFolderService'
import './styles.css'

interface FolderSelectorProps {
  onSelect: (folderId?: number) => void
  onCancel: () => void
}

const FolderSelector: React.FC<FolderSelectorProps> = ({ onSelect, onCancel }) => {
  const [folders, setFolders] = useState<FavoriteFolder[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedFolderId, setSelectedFolderId] = useState<number | undefined>()

  useEffect(() => {
    loadFolders()
  }, [])

  const loadFolders = async () => {
    try {
      const data = await getFavoriteFolders()
      setFolders(data)
      // Pre-select default folder
      const defaultFolder = data.find((f) => f.is_default)
      if (defaultFolder) {
        setSelectedFolderId(defaultFolder.id)
      }
    } catch (error) {
      console.error('Failed to load folders:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleConfirm = () => {
    onSelect(selectedFolderId)
  }

  if (loading) {
    return (
      <div className="folder-selector-overlay">
        <div className="folder-selector-modal">
          <p>加载中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="folder-selector-overlay" onClick={onCancel}>
      <div className="folder-selector-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>选择收藏夹</h3>
          <button className="btn-close" onClick={onCancel}>
            ✕
          </button>
        </div>

        <div className="folder-selector-list">
          {folders.map((folder) => (
            <div
              key={folder.id}
              className={`folder-selector-item ${
                selectedFolderId === folder.id ? 'selected' : ''
              }`}
              onClick={() => setSelectedFolderId(folder.id)}
            >
              <div className="folder-radio">
                <input
                  type="radio"
                  name="folder"
                  checked={selectedFolderId === folder.id}
                  onChange={() => setSelectedFolderId(folder.id)}
                />
              </div>
              <div className="folder-icon">
                {folder.is_default ? '📁' : folder.is_public ? '🌐' : '📂'}
              </div>
              <div className="folder-info">
                <h4>
                  {folder.name}
                  {folder.is_default && <span className="badge">默认</span>}
                </h4>
                {folder.description && <p>{folder.description}</p>}
                <span className="video-count">{folder.video_count} 个视频</span>
              </div>
            </div>
          ))}

          {folders.length === 0 && (
            <div className="no-folders">
              <p>还没有收藏夹</p>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn-cancel" onClick={onCancel}>
            取消
          </button>
          <button className="btn-confirm" onClick={handleConfirm}>
            确定
          </button>
        </div>
      </div>
    </div>
  )
}

export default FolderSelector
