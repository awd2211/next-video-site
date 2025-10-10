import { useEffect, useRef, useCallback } from 'react'

interface UseInfiniteScrollOptions {
  onLoadMore: () => void
  hasMore: boolean
  isLoading: boolean
  threshold?: number // Distance from bottom in pixels to trigger load (not used with IntersectionObserver)
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
  threshold = 300,
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
      threshold: 0.1 // Trigger when 10% of element is visible
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
