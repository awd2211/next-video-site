const HeroSkeleton = () => {
  return (
    <div className="animate-pulse">
      <div className="relative h-96 rounded-lg overflow-hidden bg-gray-800">
        <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/50 to-transparent">
          <div className="absolute bottom-8 left-8 space-y-4">
            <div className="h-12 bg-gray-700 rounded w-96"></div>
            <div className="h-6 bg-gray-700 rounded w-80"></div>
            <div className="h-12 bg-gray-700 rounded w-32"></div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HeroSkeleton
