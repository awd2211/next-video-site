import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { videoService } from '@/services/videoService'
import { dataService } from '@/services/dataService'
import VideoCard from '@/components/VideoCard'

const Search = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const query = searchParams.get('q') || ''

  const [filters, setFilters] = useState({
    category_id: searchParams.get('category_id') || '',
    country_id: searchParams.get('country_id') || '',
    year: searchParams.get('year') || '',
    min_rating: searchParams.get('min_rating') || '',
    sort_by: searchParams.get('sort_by') || 'created_at',
  })

  // Fetch categories and countries for filters
  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: dataService.getCategories,
  })

  const { data: countries } = useQuery({
    queryKey: ['countries'],
    queryFn: dataService.getCountries,
  })

  const { data, isLoading } = useQuery({
    queryKey: ['search', query, filters],
    queryFn: () =>
      videoService.searchVideos(query, {
        category_id: filters.category_id ? Number(filters.category_id) : undefined,
        country_id: filters.country_id ? Number(filters.country_id) : undefined,
        year: filters.year ? Number(filters.year) : undefined,
        min_rating: filters.min_rating ? Number(filters.min_rating) : undefined,
        sort_by: filters.sort_by || 'created_at',
      }),
    enabled: !!query,
  })

  const handleFilterChange = (key: string, value: string) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)

    // Update URL params
    const newParams = new URLSearchParams({ q: query })
    Object.entries(newFilters).forEach(([k, v]) => {
      if (v) newParams.set(k, v)
    })
    setSearchParams(newParams)
  }

  const clearFilters = () => {
    setFilters({
      category_id: '',
      country_id: '',
      year: '',
      min_rating: '',
      sort_by: 'created_at',
    })
    setSearchParams({ q: query })
  }

  // Generate year options (last 50 years)
  const currentYear = new Date().getFullYear()
  const years = Array.from({ length: 50 }, (_, i) => currentYear - i)

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">搜索结果: "{query}"</h1>

      {/* Advanced Filters */}
      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* Sort By */}
          <div>
            <label className="block text-sm font-medium mb-2">排序方式</label>
            <select
              value={filters.sort_by}
              onChange={(e) => handleFilterChange('sort_by', e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="created_at">最新发布</option>
              <option value="view_count">最多观看</option>
              <option value="average_rating">最高评分</option>
            </select>
          </div>

          {/* Category Filter */}
          <div>
            <label className="block text-sm font-medium mb-2">分类</label>
            <select
              value={filters.category_id}
              onChange={(e) => handleFilterChange('category_id', e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">全部分类</option>
              {categories?.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>

          {/* Country Filter */}
          <div>
            <label className="block text-sm font-medium mb-2">地区</label>
            <select
              value={filters.country_id}
              onChange={(e) => handleFilterChange('country_id', e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">全部地区</option>
              {countries?.map((country) => (
                <option key={country.id} value={country.id}>
                  {country.name}
                </option>
              ))}
            </select>
          </div>

          {/* Year Filter */}
          <div>
            <label className="block text-sm font-medium mb-2">年份</label>
            <select
              value={filters.year}
              onChange={(e) => handleFilterChange('year', e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">全部年份</option>
              {years.map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>
          </div>

          {/* Rating Filter */}
          <div>
            <label className="block text-sm font-medium mb-2">最低评分</label>
            <select
              value={filters.min_rating}
              onChange={(e) => handleFilterChange('min_rating', e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">不限</option>
              <option value="9">9分以上</option>
              <option value="8">8分以上</option>
              <option value="7">7分以上</option>
              <option value="6">6分以上</option>
              <option value="5">5分以上</option>
            </select>
          </div>
        </div>

        {/* Clear Filters Button */}
        {(filters.category_id || filters.country_id || filters.year || filters.min_rating || filters.sort_by !== 'created_at') && (
          <div className="mt-4">
            <button
              onClick={clearFilters}
              className="text-blue-500 hover:text-blue-400 text-sm font-medium"
            >
              清除所有筛选
            </button>
          </div>
        )}
      </div>

      {/* Results */}
      {isLoading ? (
        <div className="text-center py-12">加载中...</div>
      ) : data?.items.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          没有找到匹配 "{query}" 的结果
        </div>
      ) : (
        <>
          <p className="text-gray-400 mb-6">共找到 {data?.total} 个结果</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {data?.items.map((video) => (
              <VideoCard key={video.id} video={video} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}

export default Search
