/**
 * Video Detail Page Skeleton
 * Loading placeholder for video detail page
 */

const VideoDetailSkeleton = () => {
  return (
    <div className="max-w-7xl mx-auto animate-pulse">
      {/* Video Player Skeleton */}
      <div className="mb-6">
        <div className="aspect-video bg-gray-700 rounded-lg" />
      </div>

      {/* Video Info Skeleton */}
      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        {/* Title */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="h-8 bg-gray-700 rounded w-3/4 mb-2" />
            <div className="h-6 bg-gray-700 rounded w-1/2" />
          </div>
          <div className="flex gap-3 ml-4">
            <div className="w-10 h-10 bg-gray-700 rounded-full" />
            <div className="w-10 h-10 bg-gray-700 rounded-full" />
          </div>
        </div>

        {/* Meta info */}
        <div className="flex gap-4 mb-4">
          <div className="h-4 bg-gray-700 rounded w-16" />
          <div className="h-4 bg-gray-700 rounded w-20" />
          <div className="h-4 bg-gray-700 rounded w-24" />
        </div>

        {/* Rating */}
        <div className="mb-4">
          <div className="h-6 bg-gray-700 rounded w-32" />
        </div>

        {/* Categories */}
        <div className="flex gap-2 mb-4">
          <div className="h-6 bg-gray-700 rounded-full w-20" />
          <div className="h-6 bg-gray-700 rounded-full w-24" />
          <div className="h-6 bg-gray-700 rounded-full w-28" />
        </div>

        {/* Description */}
        <div className="space-y-2">
          <div className="h-4 bg-gray-700 rounded w-full" />
          <div className="h-4 bg-gray-700 rounded w-5/6" />
          <div className="h-4 bg-gray-700 rounded w-4/6" />
        </div>
      </div>

      {/* Comments Skeleton */}
      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        <div className="h-7 bg-gray-700 rounded w-32 mb-6" />
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex gap-4">
              <div className="w-10 h-10 bg-gray-700 rounded-full flex-shrink-0" />
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-700 rounded w-1/4" />
                <div className="h-4 bg-gray-700 rounded w-full" />
                <div className="h-4 bg-gray-700 rounded w-3/4" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Similar Videos Skeleton */}
      <div className="mb-6">
        <div className="h-7 bg-gray-700 rounded w-32 mb-4" />
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-gray-800 rounded-lg overflow-hidden">
              <div className="aspect-video bg-gray-700" />
              <div className="p-3 space-y-2">
                <div className="h-4 bg-gray-700 rounded w-full" />
                <div className="h-3 bg-gray-700 rounded w-2/3" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default VideoDetailSkeleton

