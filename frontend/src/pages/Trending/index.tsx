import { useState, useEffect, useRef } from 'react'
import { useInfiniteQuery } from '@tanstack/react-query'
import { Helmet } from 'react-helmet-async'
import { videoService } from '@/services/videoService'
import VideoCard from '@/components/VideoCard'
import { VideoCardSkeleton } from '@/components/Skeleton'
import EmptyState from '@/components/EmptyState'
import ErrorState from '@/components/ErrorState'
import BackToTop from '@/components/BackToTop'
import { useTranslation } from 'react-i18next'

type TimeRange = 'today' | 'week' | 'all' | 'rising'

const Trending = () => {
  const { t } = useTranslation()
  const [activeTab, setActiveTab] = useState<TimeRange>('all')

  // Trending videos with useInfiniteQuery based on active tab
  const {
    data: trendingData,
    isLoading,
    isFetchingNextPage,
    error,
    hasNextPage,
    fetchNextPage,
    refetch
  } = useInfiniteQuery({
    queryKey: ['trending-videos', activeTab],
    queryFn: ({ pageParam = 1 }) =>
      videoService.getTrendingVideos({
        page: pageParam,
        page_size: 20,
        time_range: activeTab
      }),
    getNextPageParam: (lastPage) => {
      return lastPage.page < lastPage.pages ? lastPage.page + 1 : undefined
    },
    initialPageParam: 1,
  })

  // Flatten all videos from pages
  const allVideos = trendingData?.pages.flatMap(page => page.items) ?? []

  // Intersection observer for infinite scroll
  const observerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
          fetchNextPage()
        }
      },
      { rootMargin: '100px' }
    )

    const currentRef = observerRef.current
    if (currentRef) observer.observe(currentRef)

    return () => {
      if (currentRef) observer.unobserve(currentRef)
    }
  }, [hasNextPage, isFetchingNextPage, fetchNextPage])

  // Tab configuration
  const tabs: { key: TimeRange; label: string; description: string }[] = [
    {
      key: 'all',
      label: t('trending.allTime'),
      description: t('trending.allTimeDescription')
    },
    {
      key: 'week',
      label: t('trending.thisWeek'),
      description: t('trending.weekDescription')
    },
    {
      key: 'today',
      label: t('trending.today'),
      description: t('trending.todayDescription')
    },
    {
      key: 'rising',
      label: t('trending.rising'),
      description: t('trending.risingDescription')
    },
  ]

  const getEmptyMessage = () => {
    switch (activeTab) {
      case 'today':
        return t('trending.emptyToday')
      case 'week':
        return t('trending.emptyWeek')
      case 'rising':
        return t('trending.emptyRising')
      default:
        return t('trending.emptyAll')
    }
  }

  return (
    <>
      {/* SEO Meta Tags */}
      <Helmet>
        <title>{t('trending.pageTitle')}</title>
        <meta name="description" content={t('trending.pageDescription')} />
        <link rel="canonical" href={`${window.location.origin}/trending`} />

        {/* Open Graph */}
        <meta property="og:type" content="website" />
        <meta property="og:title" content={t('trending.title')} />
        <meta property="og:description" content={t('trending.pageDescription')} />
        <meta property="og:url" content={`${window.location.origin}/trending`} />

        {/* Twitter Card */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={t('trending.title')} />
        <meta name="twitter:description" content={t('trending.pageDescription')} />
      </Helmet>

      <BackToTop />

      <div className="space-y-8">
        {/* Page Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold">{t('trending.title')}</h1>
          <p className="text-gray-400 text-lg">
            {tabs.find(tab => tab.key === activeTab)?.description}
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center">
          <div className="inline-flex bg-gray-800 rounded-lg p-1 gap-1">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`px-6 py-2.5 rounded-md font-semibold transition-all ${
                  activeTab === tab.key
                    ? 'bg-red-600 text-white shadow-lg'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Content Section */}
        <section>
          {error ? (
            <ErrorState
              message={t('home.errorTrending')}
              onRetry={() => refetch()}
            />
          ) : allVideos.length > 0 || isLoading ? (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                {allVideos.map((video) => (
                  <VideoCard key={video.id} video={video} />
                ))}
                {/* Show loading skeletons while fetching initial data or next page */}
                {(isLoading || isFetchingNextPage) && [...Array(10)].map((_, i) => (
                  <VideoCardSkeleton key={`skeleton-${i}`} />
                ))}
              </div>

              {/* Infinite scroll trigger element */}
              {hasNextPage && (
                <div ref={observerRef} className="h-20 flex items-center justify-center mt-8">
                  {isFetchingNextPage && (
                    <div className="flex items-center gap-2 text-gray-400">
                      <div className="w-5 h-5 border-2 border-red-600 border-t-transparent rounded-full animate-spin"></div>
                      <span>{t('common.loadMore')}</span>
                    </div>
                  )}
                </div>
              )}
            </>
          ) : (
            <EmptyState
              message={getEmptyMessage()}
              description={t('home.emptyDescription')}
            />
          )}
        </section>
      </div>
    </>
  )
}

export default Trending
