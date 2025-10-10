const VideoCardSkeleton = () => {
  return (
    <div className="animate-pulse">
      <div className="card">
        {/* Thumbnail skeleton */}
        <div className="relative aspect-video bg-gray-700 rounded-t-lg"></div>

        {/* Info skeleton */}
        <div className="p-4 space-y-3">
          {/* Title */}
          <div className="space-y-2">
            <div className="h-4 bg-gray-700 rounded w-3/4"></div>
            <div className="h-4 bg-gray-700 rounded w-1/2"></div>
          </div>

          {/* Meta info */}
          <div className="flex items-center justify-between">
            <div className="h-3 bg-gray-700 rounded w-16"></div>
            <div className="flex space-x-3">
              <div className="h-3 bg-gray-700 rounded w-12"></div>
              <div className="h-3 bg-gray-700 rounded w-12"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default VideoCardSkeleton
