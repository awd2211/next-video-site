import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { favoriteService, PaginatedFavorites } from '../../services/favoriteService'
import FavoriteFolderManager from '../../components/FavoriteFolderManager'

const Favorites = () => {
  const [favorites, setFavorites] = useState<PaginatedFavorites | null>(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [showFolders, setShowFolders] = useState(false)
  const pageSize = 20

  const loadFavorites = async () => {
    try {
      setLoading(true)
      const data = await favoriteService.getFavorites(page, pageSize)
      setFavorites(data)
    } catch (error) {
      console.error('Failed to load favorites:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadFavorites()
  }, [page])

  const handleRemove = async (videoId: number) => {
    if (!confirm('Remove from favorites?')) return

    try {
      await favoriteService.removeFavorite(videoId)
      loadFavorites()
    } catch (error) {
      alert('Failed to remove from favorites')
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">Loading favorites...</div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">My Favorites</h1>
        <button
          onClick={() => setShowFolders(!showFolders)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          {showFolders ? '查看收藏列表' : '管理收藏夹'}
        </button>
      </div>

      {showFolders ? (
        <FavoriteFolderManager />
      ) : !favorites || favorites.items.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">You haven't favorited any videos yet.</p>
          <Link to="/" className="text-blue-600 hover:text-blue-800">
            Browse videos
          </Link>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {favorites.items.map((favorite) => (
              <div key={favorite.id} className="bg-white rounded-lg shadow-md overflow-hidden">
                <Link to={`/video/${favorite.video.id}`}>
                  <img
                    src={favorite.video.poster_url || '/placeholder.jpg'}
                    alt={favorite.video.title}
                    className="w-full h-48 object-cover"
                  />
                </Link>
                <div className="p-4">
                  <Link to={`/video/${favorite.video.id}`}>
                    <h3 className="font-semibold text-lg mb-2 hover:text-blue-600">
                      {favorite.video.title}
                    </h3>
                  </Link>
                  <div className="flex items-center justify-between text-sm text-gray-600">
                    <span>{favorite.video.release_year}</span>
                    <span>⭐ {favorite.video.average_rating.toFixed(1)}</span>
                  </div>
                  <button
                    onClick={() => handleRemove(favorite.video_id)}
                    className="mt-3 w-full px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {favorites.total > pageSize && (
            <div className="mt-8 flex justify-center space-x-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 border rounded hover:bg-gray-100 disabled:opacity-50"
              >
                Previous
              </button>
              <span className="px-4 py-2">
                Page {page} of {Math.ceil(favorites.total / pageSize)}
              </span>
              <button
                onClick={() => setPage(p => p + 1)}
                disabled={page >= Math.ceil(favorites.total / pageSize)}
                className="px-4 py-2 border rounded hover:bg-gray-100 disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </>
      )
      }
    </div>
  )
}

export default Favorites
