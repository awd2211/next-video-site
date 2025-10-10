import { Link, useNavigate } from 'react-router-dom'
import ThemeToggle from '@/components/ThemeToggle'
import SearchAutocomplete from '@/components/SearchAutocomplete'
import { useAuthStore } from '@/store/authStore'

const Header = () => {
  const navigate = useNavigate()
  const { isAuthenticated, logout: storeLogout } = useAuthStore()

  const handleLogout = () => {
    storeLogout()
    navigate('/login')
  }

  return (
    <header className="bg-gray-800 border-b border-gray-700 sticky top-0 z-50">
      {/* Skip to Main Content (Accessibility) */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:bg-red-600 focus:text-white focus:px-4 focus:py-2 focus:rounded"
      >
        跳转到主内容
      </a>
      
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="text-2xl font-bold text-red-600 hover:text-red-500">
            VideoSite
          </Link>

          {/* Search with Autocomplete */}
          <div className="flex-1 max-w-2xl mx-8">
            <SearchAutocomplete />
          </div>

          {/* User menu */}
          <div className="flex items-center space-x-4">
            {/* Theme Toggle */}
            <ThemeToggle />

            {isAuthenticated ? (
              <>
                <Link to="/profile" className="hover:text-red-600 transition-colors">
                  Profile
                </Link>
                <button
                  onClick={handleLogout}
                  className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded transition-colors"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="hover:text-red-600 transition-colors"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded transition-colors"
                >
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
