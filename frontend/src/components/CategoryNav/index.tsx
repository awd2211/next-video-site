import { Link } from 'react-router-dom'
import { Film, Tv, Music, FileText, Sparkles, TrendingUp } from 'lucide-react'

const categories = [
  { name: '电影', slug: 'movies', icon: Film, color: 'from-red-500 to-pink-500' },
  { name: '电视剧', slug: 'tv-series', icon: Tv, color: 'from-blue-500 to-cyan-500' },
  { name: '动漫', slug: 'anime', icon: Sparkles, color: 'from-purple-500 to-pink-500' },
  { name: '纪录片', slug: 'documentary', icon: FileText, color: 'from-green-500 to-teal-500' },
  { name: '音乐', slug: 'music', icon: Music, color: 'from-yellow-500 to-orange-500' },
  { name: '热门', slug: 'trending', icon: TrendingUp, color: 'from-red-500 to-orange-500' },
]

const CategoryNav = () => {
  return (
    <div className="grid grid-cols-3 sm:grid-cols-6 gap-4">
      {categories.map((category) => {
        const Icon = category.icon
        return (
          <Link
            key={category.slug}
            to={`/category/${category.slug}`}
            className="group"
          >
            <div className="card hover:scale-105 transition-transform duration-300">
              <div className={`aspect-square rounded-lg bg-gradient-to-br ${category.color} p-6 flex items-center justify-center`}>
                <Icon className="w-12 h-12 text-white group-hover:scale-110 transition-transform" />
              </div>
              <div className="p-3 text-center">
                <h3 className="font-semibold group-hover:text-red-600 transition-colors">
                  {category.name}
                </h3>
              </div>
            </div>
          </Link>
        )
      })}
    </div>
  )
}

export default CategoryNav
