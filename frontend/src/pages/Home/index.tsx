import { useQuery } from '@tanstack/react-query'
import { videoService } from '@/services/videoService'
import VideoCard from '@/components/VideoCard'

const Home = () => {
  const { data: trendingVideos, isLoading: trendingLoading } = useQuery({
    queryKey: ['trending-videos'],
    queryFn: () => videoService.getTrendingVideos({ page: 1, page_size: 12 }),
  })

  const { data: latestVideos, isLoading: latestLoading } = useQuery({
    queryKey: ['latest-videos'],
    queryFn: () => videoService.getVideos({ page: 1, page_size: 12, sort_by: 'created_at' }),
  })

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="relative h-96 rounded-lg overflow-hidden">
        <img
          src="/hero-bg.jpg"
          alt="Hero"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/50 to-transparent">
          <div className="absolute bottom-8 left-8">
            <h1 className="text-5xl font-bold mb-4">Welcome to VideoSite</h1>
            <p className="text-xl text-gray-300 mb-6">
              Watch the best movies and TV shows from around the world
            </p>
            <button className="btn-primary text-lg px-8 py-3">
              Browse Now
            </button>
          </div>
        </div>
      </section>

      {/* Trending Videos */}
      <section>
        <h2 className="text-3xl font-bold mb-6">Trending Now</h2>
        {trendingLoading ? (
          <div className="text-center py-12">Loading...</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {trendingVideos?.items.map((video) => (
              <VideoCard key={video.id} video={video} />
            ))}
          </div>
        )}
      </section>

      {/* Latest Videos */}
      <section>
        <h2 className="text-3xl font-bold mb-6">Latest Releases</h2>
        {latestLoading ? (
          <div className="text-center py-12">Loading...</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {latestVideos?.items.map((video) => (
              <VideoCard key={video.id} video={video} />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}

export default Home
