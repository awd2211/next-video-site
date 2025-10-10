import { useEffect, useRef, useCallback } from 'react'

interface UseInfiniteScrollOptions {
  onLoadMore: () => void
  hasMore: boolean
  isLoading: boolean
  rootMargin?: string // Intersection observer root margin
}

/**
 * Hook for implementing infinite scroll functionality
 * Automatically loads more content when user scrolls near the bottom
 */
const useInfiniteScroll = ({
  onLoadMore,
  hasMore,
  isLoading,
  rootMargin = '0px'
}: UseInfiniteScrollOptions) => {
  const observerTarget = useRef<HTMLDivElement>(null)

  const handleObserver = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [entry] = entries

      // Load more when:
      // 1. Element is intersecting (visible in viewport)
      // 2. Not currently loading
      // 3. More content is available
      if (entry.isIntersecting && !isLoading && hasMore) {
        onLoadMore()
      }
    },
    [onLoadMore, isLoading, hasMore]
  )

  useEffect(() => {
    const element = observerTarget.current
    if (!element) return

    const observer = new IntersectionObserver(handleObserver, {
      root: null, // viewport
      rootMargin,
    })

    observer.observe(element)

    return () => {
      if (element) {
        observer.unobserve(element)
      }
    }
  }, [handleObserver, rootMargin])

  return { observerTarget }
}

export default useInfiniteScroll
