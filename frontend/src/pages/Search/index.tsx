import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { videoService } from '@/services/videoService'
import VideoCard from '@/components/VideoCard'

const Search = () => {
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q') || ''

  const { data, isLoading } = useQuery({
    queryKey: ['search', query],
    queryFn: () => videoService.searchVideos(query),
    enabled: !!query,
  })

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">
        Search Results for "{query}"
      </h1>

      {isLoading ? (
        <div className="text-center py-12">Loading...</div>
      ) : data?.items.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          No results found for "{query}"
        </div>
      ) : (
        <>
          <p className="text-gray-400 mb-6">{data?.total} results found</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {data?.items.map((video) => (
              <VideoCard key={video.id} video={video} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}

export default Search
