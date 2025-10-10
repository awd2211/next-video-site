import { useQuery } from '@tanstack/react-query'
import { videoService } from '@/services/videoService'
import { recommendationService } from '@/services/recommendationService'
import seriesService from '@/services/seriesService'
import VideoCard from '@/components/VideoCard'
import HeroCarousel from '@/components/HeroCarousel'
import CategoryNav from '@/components/CategoryNav'
import ContinueWatching from '@/components/ContinueWatching'
import { VideoCardSkeleton, HeroSkeleton } from '@/components/Skeleton'
import EmptyState from '@/components/EmptyState'
import ErrorState from '@/components/ErrorState'
import BackToTop from '@/components/BackToTop'
import useInfiniteScroll from '@/hooks/useInfiniteScroll'
import { useState, useEffect } from 'react'
import type { Video } from '@/types'

const Home = () => {
  // State for infinite scroll - Trending
  const [trendingPage, setTrendingPage] = useState(1)
  const [allTrendingVideos, setAllTrendingVideos] = useState<Video[]>([])
  const [hasMoreTrending, setHasMoreTrending] = useState(true)

  // State for infinite scroll - Latest
  const [latestPage, setLatestPage] = useState(1)
  const [allLatestVideos, setAllLatestVideos] = useState<Video[]>([])
  const [hasMoreLatest, setHasMoreLatest] = useState(true)

  // Featured videos for hero carousel
  const {
    data: featuredVideos,
    isLoading: featuredLoading,
    error: featuredError,
    refetch: refetchFeatured
  } = useQuery({
    queryKey: ['featured-videos'],
    queryFn: () => videoService.getFeaturedVideos({ page: 1, page_size: 5 }),
    staleTime: 5 * 60 * 1000, // 5分钟缓存
  })

  // Trending videos with infinite scroll
  const {
    data: trendingData,
    isLoading: trendingLoading,
    error: trendingError,
    refetch: refetchTrending
  } = useQuery({
    queryKey: ['trending-videos', trendingPage],
    queryFn: () => videoService.getTrendingVideos({ page: trendingPage, page_size: 12 }),
  })

  // Handle trending data updates
  useEffect(() => {
    if (trendingData) {
      if (trendingPage === 1) {
        setAllTrendingVideos(trendingData.items)
      } else {
        setAllTrendingVideos(prev => [...prev, ...trendingData.items])
      }
      setHasMoreTrending(trendingData.items.length === 12 && trendingData.page < trendingData.pages)
    }
  }, [trendingData, trendingPage])

  // Personalized recommendations for logged-in users
  const { data: forYouVideos, isLoading: forYouLoading } = useQuery({
    queryKey: ['for-you-videos'],
    queryFn: () => recommendationService.getForYouRecommendations(12),
    retry: false, // 如果用户未登录，不重试
  })

  // Watch history for continue watching
  const { data: watchHistory } = useQuery({
    queryKey: ['watch-history-recent'],
    queryFn: async () => {
      try {
        const response = await fetch('/api/v1/history?page=1&page_size=6', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        })
        if (!response.ok) return []
        const data = await response.json()
        return data.items || []
      } catch {
        return []
      }
    },
    retry: false,
  })

  // Latest videos with infinite scroll
  const {
    data: latestData,
    isLoading: latestLoading,
    error: latestError,
    refetch: refetchLatest
  } = useQuery({
    queryKey: ['latest-videos', latestPage],
    queryFn: () => videoService.getVideos({ page: latestPage, page_size: 12, sort_by: 'created_at' }),
  })

  // Handle latest data updates
  useEffect(() => {
    if (latestData) {
      if (latestPage === 1) {
        setAllLatestVideos(latestData.items)
      } else {
        setAllLatestVideos(prev => [...prev, ...latestData.items])
      }
      setHasMoreLatest(latestData.items.length === 12 && latestData.page < latestData.pages)
    }
  }, [latestData, latestPage])

  // Series
  const { data: seriesList, isLoading: seriesLoading } = useQuery({
    queryKey: ['series-list-home'],
    queryFn: () => seriesService.getSeriesList({ page: 1, page_size: 6 }),
  })

  // Infinite scroll observers
  const { observerTarget: trendingObserver } = useInfiniteScroll({
    onLoadMore: () => setTrendingPage(prev => prev + 1),
    hasMore: hasMoreTrending,
    isLoading: trendingLoading,
    threshold: 300
  })

  const { observerTarget: latestObserver } = useInfiniteScroll({
    onLoadMore: () => setLatestPage(prev => prev + 1),
    hasMore: hasMoreLatest,
    isLoading: latestLoading,
    threshold: 300
  })

  return (
    <>
      <BackToTop />
      <div className="space-y-12">
      {/* Hero Carousel */}
      <section>
        {featuredLoading ? (
          <HeroSkeleton />
        ) : featuredError ? (
          <ErrorState
            message="无法加载精选内容"
            onRetry={() => refetchFeatured()}
          />
        ) : featuredVideos && featuredVideos.items.length > 0 ? (
          <HeroCarousel videos={featuredVideos.items} />
        ) : (
          <div className="relative h-96 rounded-lg overflow-hidden bg-gradient-to-r from-red-900 to-red-700 flex items-center justify-center">
            <div className="text-center px-8">
              <h1 className="text-5xl font-bold mb-4">欢迎来到 VideoSite</h1>
              <p className="text-xl text-gray-200">
                精彩内容，即将为您呈现
              </p>
            </div>
          </div>
        )}
      </section>

      {/* Category Navigation */}
      <section>
        <h2 className="text-2xl font-bold mb-6">浏览分类</h2>
        <CategoryNav />
      </section>

      {/* Continue Watching */}
      {watchHistory && watchHistory.length > 0 && (
        <section>
          <h2 className="text-3xl font-bold mb-6">继续观看</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <ContinueWatching history={watchHistory} />
          </div>
        </section>
      )}

      {/* Trending Videos with Infinite Scroll */}
      <section>
        <h2 className="text-3xl font-bold mb-6">热门推荐</h2>
        {trendingError ? (
          <ErrorState
            message="无法加载热门视频"
            onRetry={() => {
              setTrendingPage(1)
              setAllTrendingVideos([])
              refetchTrending()
            }}
          />
        ) : allTrendingVideos.length > 0 || trendingLoading ? (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {allTrendingVideos.map((video) => (
                <VideoCard key={video.id} video={video} />
              ))}
              {/* Show loading skeletons while fetching more */}
              {trendingLoading && [...Array(4)].map((_, i) => (
                <VideoCardSkeleton key={`skeleton-${i}`} />
              ))}
            </div>
            {/* Infinite scroll trigger element */}
            {hasMoreTrending && (
              <div ref={trendingObserver} className="h-20 flex items-center justify-center mt-8">
                {trendingLoading && (
                  <div className="flex items-center gap-2 text-gray-400">
                    <div className="w-5 h-5 border-2 border-red-600 border-t-transparent rounded-full animate-spin"></div>
                    <span>加载更多...</span>
                  </div>
                )}
              </div>
            )}
          </>
        ) : (
          <EmptyState message="暂无热门视频" description="敬请期待精彩内容" />
        )}
      </section>

      {/* Series */}
      {seriesList && seriesList.items && seriesList.items.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-3xl font-bold">热门系列</h2>
            <a href="/series" className="text-red-600 hover:text-red-500 font-semibold">
              查看全部 →
            </a>
          </div>
          {seriesLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <VideoCardSkeleton key={i} />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
              {seriesList.items.map((series) => (
                <a
                  key={series.id}
                  href={`/series/${series.id}`}
                  className="group card hover:ring-2 hover:ring-red-600 transition-all"
                >
                  <div className="relative aspect-video overflow-hidden rounded-t-lg">
                    <img
                      src={series.cover_image || '/placeholder.jpg'}
                      alt={series.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute top-2 right-2 bg-red-600 px-3 py-1 rounded-full text-xs font-semibold">
                      {series.video_count || 0} 集
                    </div>
                  </div>
                  <div className="p-4">
                    <h3 className="font-semibold text-lg line-clamp-1 group-hover:text-red-600 transition-colors">
                      {series.title}
                    </h3>
                    <p className="text-sm text-gray-400 mt-1 line-clamp-2">
                      {series.description || '精彩系列剧集'}
                    </p>
                  </div>
                </a>
              ))}
            </div>
          )}
        </section>
      )}

      {/* For You - Personalized Recommendations */}
      {forYouVideos && forYouVideos.length > 0 && (
        <section>
          <h2 className="text-3xl font-bold mb-6">为你推荐</h2>
          {forYouLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {[...Array(8)].map((_, i) => (
                <VideoCardSkeleton key={i} />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {forYouVideos.map((video) => (
                <VideoCard key={video.id} video={video} />
              ))}
            </div>
          )}
        </section>
      )}

      {/* Latest Videos with Infinite Scroll */}
      <section>
        <h2 className="text-3xl font-bold mb-6">最新发布</h2>
        {latestError ? (
          <ErrorState
            message="无法加载最新视频"
            onRetry={() => {
              setLatestPage(1)
              setAllLatestVideos([])
              refetchLatest()
            }}
          />
        ) : allLatestVideos.length > 0 || latestLoading ? (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {allLatestVideos.map((video) => (
                <VideoCard key={video.id} video={video} />
              ))}
              {/* Show loading skeletons while fetching more */}
              {latestLoading && [...Array(4)].map((_, i) => (
                <VideoCardSkeleton key={`skeleton-latest-${i}`} />
              ))}
            </div>
            {/* Infinite scroll trigger element */}
            {hasMoreLatest && (
              <div ref={latestObserver} className="h-20 flex items-center justify-center mt-8">
                {latestLoading && (
                  <div className="flex items-center gap-2 text-gray-400">
                    <div className="w-5 h-5 border-2 border-red-600 border-t-transparent rounded-full animate-spin"></div>
                    <span>加载更多...</span>
                  </div>
                )}
              </div>
            )}
          </>
        ) : (
          <EmptyState message="暂无最新视频" description="敬请期待精彩内容" />
        )}
      </section>
      </div>
    </>
  )
}

export default Home
