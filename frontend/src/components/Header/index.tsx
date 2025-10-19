import { Link, useNavigate, useLocation } from 'react-router-dom'
import ThemeToggle from '@/components/ThemeToggle'
import LanguageSwitcher from '@/components/LanguageSwitcher'
import SearchAutocomplete from '@/components/SearchAutocomplete'
import { useAuthStore } from '@/store/authStore'
import { useTranslation } from 'react-i18next'

const Header = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const { isAuthenticated, logout: storeLogout } = useAuthStore()

  const handleLogout = () => {
    storeLogout()
    navigate('/login')
  }

  const isActivePath = (path: string) => {
    return location.pathname === path
  }

  return (
    <header className="bg-gray-800 border-b border-gray-700 sticky top-0 z-50">
      {/* Skip to Main Content (Accessibility) */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:bg-red-600 focus:text-white focus:px-4 focus:py-2 focus:rounded"
      >
        {t('common.skipToMain', 'Skip to main content')}
      </a>

      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="text-2xl font-bold text-red-600 hover:text-red-500 flex-shrink-0">
            VideoSite
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-6 ml-8">
            <Link
              to="/"
              className={`font-medium transition-colors ${
                isActivePath('/') ? 'text-red-600' : 'text-gray-300 hover:text-red-600'
              }`}
            >
              {t('nav.home')}
            </Link>
            <Link
              to="/trending"
              className={`font-medium transition-colors ${
                isActivePath('/trending') ? 'text-red-600' : 'text-gray-300 hover:text-red-600'
              }`}
            >
              {t('nav.trending')}
            </Link>
            <Link
              to="/series"
              className={`font-medium transition-colors ${
                isActivePath('/series') ? 'text-red-600' : 'text-gray-300 hover:text-red-600'
              }`}
            >
              {t('nav.series')}
            </Link>
            <Link
              to="/subscription"
              className={`font-medium transition-colors ${
                isActivePath('/subscription') ? 'text-red-600' : 'text-gray-300 hover:text-red-600'
              }`}
            >
              <span className="inline-flex items-center">
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                {t('nav.vip', 'VIP')}
              </span>
            </Link>
            {isAuthenticated && (
              <Link
                to="/my-list"
                className={`font-medium transition-colors ${
                  isActivePath('/my-list') ? 'text-red-600' : 'text-gray-300 hover:text-red-600'
                }`}
              >
                {t('nav.myList', 'My List')}
              </Link>
            )}
          </nav>

          {/* Search with Autocomplete */}
          <div className="flex-1 max-w-xl mx-8">
            <SearchAutocomplete />
          </div>

          {/* User menu */}
          <div className="flex items-center space-x-4">
            {/* Language Switcher */}
            <LanguageSwitcher />

            {/* Theme Toggle */}
            <ThemeToggle />

            {isAuthenticated ? (
              <>
                <Link to="/profile" className="hover:text-red-600 transition-colors">
                  {t('nav.profile')}
                </Link>
                <button
                  onClick={handleLogout}
                  className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded transition-colors"
                >
                  {t('nav.logout')}
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="hover:text-red-600 transition-colors"
                >
                  {t('nav.login')}
                </Link>
                <Link
                  to="/register"
                  className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded transition-colors"
                >
                  {t('nav.register')}
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
