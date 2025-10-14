import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { historyService, PaginatedHistory } from '../../services/historyService'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'

const History = () => {
  const { t } = useTranslation()
  const [history, setHistory] = useState<PaginatedHistory | null>(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const pageSize = 20

  const loadHistory = async () => {
    try {
      setLoading(true)
      const data = await historyService.getHistory(page, pageSize)
      setHistory(data)
    } catch (error) {
      console.error('Failed to load history:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadHistory()
  }, [page])

  const handleRemove = async (videoId: number) => {
    if (!confirm(t('history.removeConfirm'))) return

    try {
      await historyService.deleteHistory(videoId)
      toast.success(t('history.removeSuccess'))
      loadHistory()
    } catch (error) {
      toast.error(t('history.removeFailed'))
    }
  }

  const handleClearAll = async () => {
    if (!confirm(t('history.clearConfirm'))) return

    try {
      await historyService.clearHistory()
      toast.success(t('history.clearSuccess'))
      loadHistory()
    } catch (error) {
      toast.error(t('history.clearFailed'))
    }
  }

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    if (hours > 0) {
      return `${hours}h ${minutes}m`
    }
    return `${minutes}m`
  }

  const getProgressPercentage = (history: any) => {
    if (!history.video.duration) return 0
    return Math.min(100, (history.last_position / (history.video.duration * 60)) * 100)
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">Loading history...</div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Watch History</h1>
        {history && history.items.length > 0 && (
          <button
            onClick={handleClearAll}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Clear All
          </button>
        )}
      </div>

      {!history || history.items.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">No watch history yet.</p>
          <Link to="/" className="text-blue-600 hover:text-blue-800">
            Start watching
          </Link>
        </div>
      ) : (
        <>
          <div className="space-y-4">
            {history.items.map((item) => (
              <div key={item.id} className="bg-white rounded-lg shadow-md p-4 flex">
                <Link to={`/video/${item.video.id}`} className="flex-shrink-0">
                  <img
                    src={item.video.poster_url || '/placeholder.jpg'}
                    alt={item.video.title}
                    className="w-40 h-24 object-cover rounded"
                  />
                </Link>
                <div className="ml-4 flex-grow">
                  <Link to={`/video/${item.video.id}`}>
                    <h3 className="font-semibold text-lg mb-2 hover:text-blue-600">
                      {item.video.title}
                    </h3>
                  </Link>
                  <div className="text-sm text-gray-600 space-y-1">
                    <div>
                      Watched: {formatDuration(item.watch_duration)} · Last position:{' '}
                      {formatDuration(item.last_position)}
                    </div>
                    <div>
                      Last watched: {new Date(item.updated_at || item.created_at).toLocaleDateString()}
                    </div>
                    {item.is_completed ? (
                      <div className="text-green-600">✓ Completed</div>
                    ) : (
                      <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${getProgressPercentage(item)}%` }}
                        />
                      </div>
                    )}
                  </div>
                </div>
                <div className="ml-4 flex-shrink-0">
                  <button
                    onClick={() => handleRemove(item.video_id)}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 text-sm"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {history.total > pageSize && (
            <div className="mt-8 flex justify-center space-x-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 border rounded hover:bg-gray-100 disabled:opacity-50"
              >
                Previous
              </button>
              <span className="px-4 py-2">
                Page {page} of {Math.ceil(history.total / pageSize)}
              </span>
              <button
                onClick={() => setPage(p => p + 1)}
                disabled={page >= Math.ceil(history.total / pageSize)}
                className="px-4 py-2 border rounded hover:bg-gray-100 disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default History
