import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { actorService, ActorDetail } from '../../services/actorService'

const ActorDetailPage = () => {
  const { id } = useParams<{ id: string }>()
  const [actor, setActor] = useState<ActorDetail | null>(null)
  const [videos, setVideos] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [videosPage, setVideosPage] = useState(1)
  const pageSize = 12

  useEffect(() => {
    const loadActorData = async () => {
      if (!id) return

      try {
        setLoading(true)
        const actorData = await actorService.getActor(Number(id))
        setActor(actorData)

        const videosData = await actorService.getActorVideos(Number(id), videosPage, pageSize)
        setVideos(videosData)
      } catch (error) {
        console.error('Failed to load actor:', error)
      } finally {
        setLoading(false)
      }
    }

    loadActorData()
  }, [id, videosPage])

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Unknown'
    return new Date(dateString).toLocaleDateString()
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">Loading...</div>
      </div>
    )
  }

  if (!actor) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">Actor not found</div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Actor Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="flex flex-col md:flex-row">
          <div className="flex-shrink-0 mb-4 md:mb-0">
            {actor.avatar ? (
              <img
                src={actor.avatar}
                alt={actor.name}
                className="w-48 h-48 rounded-lg object-cover"
              />
            ) : (
              <div className="w-48 h-48 rounded-lg bg-gray-300 flex items-center justify-center">
                <span className="text-6xl text-gray-600">{actor.name[0]}</span>
              </div>
            )}
          </div>

          <div className="md:ml-6 flex-grow">
            <h1 className="text-3xl font-bold mb-2">{actor.name}</h1>

            <div className="space-y-2 text-gray-700">
              {actor.birth_date && (
                <div>
                  <span className="font-semibold">Born:</span> {formatDate(actor.birth_date)}
                </div>
              )}
            </div>

            {actor.biography && (
              <div className="mt-4">
                <h2 className="text-xl font-semibold mb-2">Biography</h2>
                <p className="text-gray-700 whitespace-pre-line">{actor.biography}</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Filmography */}
      <div>
        <h2 className="text-2xl font-bold mb-4">
          Filmography ({videos?.total || 0} {videos?.total === 1 ? 'title' : 'titles'})
        </h2>

        {videos && videos.items && videos.items.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {videos.items.map((video: any) => (
                <Link
                  key={video.id}
                  to={`/video/${video.id}`}
                  className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow"
                >
                  <img
                    src={video.poster_url || '/placeholder.jpg'}
                    alt={video.title}
                    className="w-full h-64 object-cover"
                  />
                  <div className="p-4">
                    <h3 className="font-semibold text-lg mb-2 line-clamp-2">
                      {video.title}
                    </h3>
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <span>{video.release_year}</span>
                      <span>⭐ {video.average_rating.toFixed(1)}</span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>

            {/* Pagination */}
            {videos.total > pageSize && (
              <div className="mt-8 flex justify-center space-x-2">
                <button
                  onClick={() => setVideosPage(p => Math.max(1, p - 1))}
                  disabled={videosPage === 1}
                  className="px-4 py-2 border rounded hover:bg-gray-100 disabled:opacity-50"
                >
                  Previous
                </button>
                <span className="px-4 py-2">
                  Page {videosPage} of {Math.ceil(videos.total / pageSize)}
                </span>
                <button
                  onClick={() => setVideosPage(p => p + 1)}
                  disabled={videosPage >= Math.ceil(videos.total / pageSize)}
                  className="px-4 py-2 border rounded hover:bg-gray-100 disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No videos found for this actor.
          </div>
        )}
      </div>
    </div>
  )
}

export default ActorDetailPage
