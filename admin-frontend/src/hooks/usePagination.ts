import { useState, useCallback } from 'react'

export interface PaginationOptions {
  initialPage?: number
  initialPageSize?: number
}

export interface PaginationResult {
  page: number
  pageSize: number
  setPage: (page: number) => void
  setPageSize: (pageSize: number) => void
  resetPagination: () => void
  paginationConfig: {
    current: number
    pageSize: number
    onChange: (page: number, pageSize: number) => void
    showSizeChanger: boolean
    showQuickJumper: boolean
    showTotal: (total: number) => string
  }
}

/**
 * Hook for managing table pagination state
 */
export function usePagination(options: PaginationOptions = {}): PaginationResult {
  const { initialPage = 1, initialPageSize = 20 } = options

  const [page, setPage] = useState(initialPage)
  const [pageSize, setPageSize] = useState(initialPageSize)

  const handlePageChange = useCallback((newPage: number, newPageSize: number) => {
    setPage(newPage)
    if (newPageSize !== pageSize) {
      setPageSize(newPageSize)
      setPage(1) // Reset to first page when page size changes
    }
  }, [pageSize])

  const resetPagination = useCallback(() => {
    setPage(initialPage)
    setPageSize(initialPageSize)
  }, [initialPage, initialPageSize])

  return {
    page,
    pageSize,
    setPage,
    setPageSize,
    resetPagination,
    paginationConfig: {
      current: page,
      pageSize,
      onChange: handlePageChange,
      showSizeChanger: true,
      showQuickJumper: true,
      showTotal: (total: number) => `共 ${total} 条`,
    },
  }
}

export default usePagination

