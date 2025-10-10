/**
 * Folder Videos Page
 * Display videos in a favorite folder
 */
import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  getFavoriteFolderById,
  FavoriteFolderWithVideos,
} from '../../services/favoriteFolderService'
import VideoCard from '../../components/VideoCard'
import './styles.css'

const FolderVideos: React.FC = () => {
  const { folderId } = useParams<{ folderId: string }>()
  const navigate = useNavigate()
  const [folder, setFolder] = useState<FavoriteFolderWithVideos | null>(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const pageSize = 20

  useEffect(() => {
    if (folderId) {
      loadFolderVideos(parseInt(folderId))
    }
  }, [folderId, page])

  const loadFolderVideos = async (id: number) => {
    try {
      setLoading(true)
      const data = await getFavoriteFolderById(id, page, pageSize)
      setFolder(data)
    } catch (error: any) {
      console.error('Failed to load folder videos:', error)
      if (error.response?.status === 404) {
        alert('收藏夹不存在')
        navigate('/favorites')
      } else {
        alert('加载失败')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleNextPage = () => {
    setPage((prev) => prev + 1)
  }

  const handlePrevPage = () => {
    setPage((prev) => Math.max(1, prev - 1))
  }

  if (loading && !folder) {
    return (
      <div className="folder-videos-page">
        <div className="loading">加载中...</div>
      </div>
    )
  }

  if (!folder) {
    return (
      <div className="folder-videos-page">
        <div className="error">收藏夹不存在</div>
      </div>
    )
  }

  return (
    <div className="folder-videos-page">
      {/* Folder Header */}
      <div className="folder-header">
        <button className="btn-back" onClick={() => navigate('/favorites')}>
          ← 返回收藏夹列表
        </button>
        <div className="folder-title-section">
          <h1 className="folder-title">
            {folder.is_default ? '📁' : folder.is_public ? '🌐' : '📂'} {folder.name}
            {folder.is_default && <span className="badge-default">默认</span>}
          </h1>
          {folder.description && <p className="folder-desc">{folder.description}</p>}
          <div className="folder-stats">
            <span>{folder.video_count} 个视频</span>
            <span>·</span>
            <span>创建于 {new Date(folder.created_at).toLocaleDateString()}</span>
            {folder.is_public && (
              <>
                <span>·</span>
                <span className="public-badge">公开</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Video Grid */}
      {folder.videos.length > 0 ? (
        <>
          <div className="video-grid">
            {folder.videos.map((video: any) => (
              <VideoCard key={video.id} video={video} />
            ))}
          </div>

          {/* Pagination */}
          {folder.video_count > pageSize && (
            <div className="pagination">
              <button
                className="btn-page"
                onClick={handlePrevPage}
                disabled={page === 1}
              >
                上一页
              </button>
              <span className="page-info">
                第 {page} 页 / 共 {Math.ceil(folder.video_count / pageSize)} 页
              </span>
              <button
                className="btn-page"
                onClick={handleNextPage}
                disabled={page >= Math.ceil(folder.video_count / pageSize)}
              >
                下一页
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="empty-folder">
          <p>📭</p>
          <p>这个收藏夹还没有视频</p>
          <button className="btn-browse" onClick={() => navigate('/')}>
            去浏览视频
          </button>
        </div>
      )}
    </div>
  )
}

export default FolderVideos
