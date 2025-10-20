import { useQuery, useInfiniteQuery } from '@tanstack/react-query'
import { Helmet } from 'react-helmet-async'
import { videoService } from '@/services/videoService'
import { recommendationService } from '@/services/recommendationService'
import seriesService from '@/services/seriesService'
import VideoCard from '@/components/VideoCard'
import HeroCarousel from '@/components/HeroCarousel'
import CategoryNav from '@/components/CategoryNav'
import ContinueWatching from '@/components/ContinueWatching'
import AnnouncementBanner from '@/components/AnnouncementBanner'
import { VideoCardSkeleton, HeroSkeleton } from '@/components/Skeleton'
import EmptyState from '@/components/EmptyState'
import ErrorState from '@/components/ErrorState'
import BackToTop from '@/components/BackToTop'
import { useEffect, useRef } from 'react'

const Home = () => {
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

  // Trending videos with useInfiniteQuery
  const {
    data: trendingData,
    isLoading: trendingLoading,
    isFetchingNextPage: trendingFetchingNext,
    error: trendingError,
    hasNextPage: hasMoreTrending,
    fetchNextPage: fetchNextTrending,
    refetch: refetchTrending
  } = useInfiniteQuery({
    queryKey: ['trending-videos-infinite'],
    queryFn: ({ pageParam = 1 }) => videoService.getTrendingVideos({ page: pageParam, page_size: 12 }),
    getNextPageParam: (lastPage) => {
      // Return next page number if there are more pages
      return lastPage.page < lastPage.pages ? lastPage.page + 1 : undefined
    },
    initialPageParam: 1,
  })

  // Flatten all trending videos from pages
  const allTrendingVideos = trendingData?.pages.flatMap(page => page.items) ?? []

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

  // Latest videos with useInfiniteQuery
  const {
    data: latestData,
    isLoading: latestLoading,
    isFetchingNextPage: latestFetchingNext,
    error: latestError,
    hasNextPage: hasMoreLatest,
    fetchNextPage: fetchNextLatest,
    refetch: refetchLatest
  } = useInfiniteQuery({
    queryKey: ['latest-videos-infinite'],
    queryFn: ({ pageParam = 1 }) => videoService.getVideos({ page: pageParam, page_size: 12, sort_by: 'created_at' }),
    getNextPageParam: (lastPage) => {
      return lastPage.page < lastPage.pages ? lastPage.page + 1 : undefined
    },
    initialPageParam: 1,
  })

  // Flatten all latest videos from pages
  const allLatestVideos = latestData?.pages.flatMap(page => page.items) ?? []

  // Series
  const { data: seriesList, isLoading: seriesLoading } = useQuery({
    queryKey: ['series-list-home'],
    queryFn: () => seriesService.getList({ page: 1, page_size: 6 }),
  })

  // Intersection observer for infinite scroll - Trending
  const trendingObserverRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMoreTrending && !trendingFetchingNext) {
          fetchNextTrending()
        }
      },
      { rootMargin: '100px' }
    )

    const currentRef = trendingObserverRef.current
    if (currentRef) observer.observe(currentRef)

    return () => {
      if (currentRef) observer.unobserve(currentRef)
    }
  }, [hasMoreTrending, trendingFetchingNext, fetchNextTrending])

  // Intersection observer for infinite scroll - Latest
  const latestObserverRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMoreLatest && !latestFetchingNext) {
          fetchNextLatest()
        }
      },
      { rootMargin: '100px' }
    )

    const currentRef = latestObserverRef.current
    if (currentRef) observer.observe(currentRef)

    return () => {
      if (currentRef) observer.unobserve(currentRef)
    }
  }, [hasMoreLatest, latestFetchingNext, fetchNextLatest])

  return (
    <>
      {/* SEO Meta Tags for Home Page */}
      <Helmet>
        <title>VideoSite - 在线视频平台 | 观看最新最热门视频</title>
        <meta name="description" content="VideoSite 提供海量高清视频内容，包括电影、电视剧、综艺、纪录片等。立即观看最新最热门的视频！" />
        <link rel="canonical" href={window.location.origin} />
        
        {/* Open Graph */}
        <meta property="og:type" content="website" />
        <meta property="og:title" content="VideoSite - 在线视频平台" />
        <meta property="og:description" content="观看最新最热门的视频内容" />
        <meta property="og:url" content={window.location.origin} />
        <meta property="og:site_name" content="VideoSite" />
        <meta property="og:image" content={`${window.location.origin}/og-image.jpg`} />
        
        {/* Twitter Card */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="VideoSite - 在线视频平台" />
        <meta name="twitter:description" content="观看最新最热门的视频内容" />
        <meta name="twitter:image" content={`${window.location.origin}/og-image.jpg`} />
        
        {/* Keywords */}
        <meta name="keywords" content="视频,在线视频,电影,电视剧,综艺,纪录片,高清视频,免费视频" />
      </Helmet>

      <BackToTop />
      <div className="space-y-12">
      {/* Announcement Banner */}
      <AnnouncementBanner />

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
            onRetry={() => refetchTrending()}
          />
        ) : allTrendingVideos.length > 0 || trendingLoading ? (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {allTrendingVideos.map((video) => (
                <VideoCard key={video.id} video={video} />
              ))}
              {/* Show loading skeletons while fetching initial data or next page */}
              {(trendingLoading || trendingFetchingNext) && [...Array(4)].map((_, i) => (
                <VideoCardSkeleton key={`skeleton-${i}`} />
              ))}
            </div>
            {/* Infinite scroll trigger element */}
            {hasMoreTrending && (
              <div ref={trendingObserverRef} className="h-20 flex items-center justify-center mt-8">
                {trendingFetchingNext && (
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
            onRetry={() => refetchLatest()}
          />
        ) : allLatestVideos.length > 0 || latestLoading ? (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {allLatestVideos.map((video) => (
                <VideoCard key={video.id} video={video} />
              ))}
              {/* Show loading skeletons while fetching initial data or next page */}
              {(latestLoading || latestFetchingNext) && [...Array(4)].map((_, i) => (
                <VideoCardSkeleton key={`skeleton-latest-${i}`} />
              ))}
            </div>
            {/* Infinite scroll trigger element */}
            {hasMoreLatest && (
              <div ref={latestObserverRef} className="h-20 flex items-center justify-center mt-8">
                {latestFetchingNext && (
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
