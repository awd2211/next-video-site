// @ts-nocheck
/**
 * Virtual Video Grid Component
 * Optimized for rendering thousands of videos efficiently
 */
import { FixedSizeGrid as Grid } from 'react-window'
// @ts-ignore
import InfiniteLoader from 'react-window-infinite-loader'
import AutoSizer from 'react-virtualized-auto-sizer'
import VideoCard from '@/components/VideoCard'
import { VideoCardSkeleton } from '@/components/Skeleton'
import type { Video } from '@/types'

interface VirtualVideoGridProps {
  videos: Video[]
  hasMore: boolean
  loadMore: () => Promise<void>
  isLoading: boolean
  columnCount?: number
  rowHeight?: number
}

export const VirtualVideoGrid: React.FC<VirtualVideoGridProps> = ({
  videos,
  hasMore,
  loadMore,
  isLoading,
  columnCount = 6,
  rowHeight = 320,
}) => {
  const rowCount = Math.ceil(videos.length / columnCount)
  
  // Check if item is loaded
  const isItemLoaded = (index: number) => {
    return !hasMore || index < Math.ceil(videos.length / columnCount)
  }

  // Cell renderer
  const Cell = ({ columnIndex, rowIndex, style }: any) => {
    const index = rowIndex * columnCount + columnIndex
    
    // Empty cell if beyond videos length
    if (index >= videos.length) {
      return <div style={style} />
    }
    
    const video = videos[index]
    
    return (
      <div style={{ ...style, padding: '8px' }}>
        <VideoCard 
          video={video} 
          showQuickActions={true}
          enablePreview={false} // Disable preview in virtual grid for performance
        />
      </div>
    )
  }

  return (
    <div style={{ height: '800px', width: '100%' }}>
      <AutoSizer>
        {({ height, width }) => {
          const columnWidth = width / columnCount
          
          return (
            <InfiniteLoader
              isItemLoaded={isItemLoaded}
              itemCount={hasMore ? rowCount + 1 : rowCount}
              loadMoreItems={loadMore}
              threshold={3} // Load more when 3 rows from bottom
            >
              {({ onItemsRendered, ref }) => (
                <Grid
                  ref={ref}
                  columnCount={columnCount}
                  columnWidth={columnWidth}
                  height={height}
                  rowCount={rowCount}
                  rowHeight={rowHeight}
                  width={width}
                  onItemsRendered={(gridData) => {
                    // Convert grid data to list data for InfiniteLoader
                    const {
                      visibleRowStartIndex,
                      visibleRowStopIndex,
                      overscanRowStartIndex,
                      overscanRowStopIndex,
                    } = gridData
                    
                    onItemsRendered({
                      visibleStartIndex: visibleRowStartIndex,
                      visibleStopIndex: visibleRowStopIndex,
                      overscanStartIndex: overscanRowStartIndex,
                      overscanStopIndex: overscanRowStopIndex,
                    })
                  }}
                  overscanRowCount={2} // Render 2 extra rows for smoother scrolling
                >
                  {Cell}
                </Grid>
              )}
            </InfiniteLoader>
          )
        }}
      </AutoSizer>
      
      {/* Loading indicator at bottom */}
      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <div className="flex items-center gap-2 text-gray-400">
            <div className="w-5 h-5 border-2 border-red-600 border-t-transparent rounded-full animate-spin"></div>
            <span>加载更多...</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default VirtualVideoGrid

