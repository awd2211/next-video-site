import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { lazy, Suspense, useEffect } from 'react'
import { ThemeProvider } from './contexts/ThemeContext'
import ErrorBoundary from './components/ErrorBoundary'
import Layout from './components/Layout'
import Home from './pages/Home'
import PWAInstallPrompt from './components/PWAInstallPrompt'

// Lazy load components for code splitting with prefetch hints
const VideoDetail = lazy(() => import(/* webpackPrefetch: true */ './pages/VideoDetail'))
const Search = lazy(() => import(/* webpackPrefetch: true */ './pages/Search'))
const Trending = lazy(() => import(/* webpackPrefetch: true */ './pages/Trending'))
const Category = lazy(() => import('./pages/Category'))
const Login = lazy(() => import('./pages/Login'))
const Register = lazy(() => import('./pages/Register'))
const Profile = lazy(() => import('./pages/Profile'))
const Favorites = lazy(() => import('./pages/Favorites'))
const FolderVideos = lazy(() => import('./pages/FolderVideos'))
const History = lazy(() => import('./pages/History'))
const ActorDetail = lazy(() => import('./pages/ActorDetail'))
const DirectorDetail = lazy(() => import('./pages/DirectorDetail'))
const SeriesList = lazy(() => import('./pages/Series/SeriesList'))
const SeriesDetail = lazy(() => import('./pages/Series/SeriesDetail'))
const HelpCenter = lazy(() => import('./pages/HelpCenter'))
const ContactUs = lazy(() => import('./pages/ContactUs'))
const FAQ = lazy(() => import('./pages/FAQ'))
const PrivacyPolicy = lazy(() => import('./pages/PrivacyPolicy'))
const TermsOfService = lazy(() => import('./pages/TermsOfService'))
const Announcements = lazy(() => import('./pages/Announcements'))
const MyList = lazy(() => import('./pages/MyList'))
const SharedList = lazy(() => import('./pages/SharedList'))
const OAuthCallback = lazy(() => import('./pages/OAuthCallback'))

// Preload critical routes
const preloadCriticalRoutes = () => {
  // Preload most visited pages after 2 seconds
  const timer = setTimeout(() => {
    import('./pages/VideoDetail')
    import('./pages/Search')
  }, 2000)

  return () => clearTimeout(timer)
}

// Loading fallback component
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-screen">
    <div className="flex flex-col items-center gap-4">
      <div className="w-12 h-12 border-4 border-red-600 border-t-transparent rounded-full animate-spin"></div>
      <p className="text-gray-400">加载中...</p>
    </div>
  </div>
)

function App() {
  // Preload critical routes on mount
  useEffect(() => {
    const cleanup = preloadCriticalRoutes()
    return cleanup
  }, [])

  return (
    <ErrorBoundary>
      <ThemeProvider>
        <BrowserRouter>
          <Suspense fallback={<PageLoader />}>
            <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Home />} />
              <Route path="video/:id" element={<VideoDetail />} />
              <Route path="search" element={<Search />} />
              <Route path="trending" element={<Trending />} />
              <Route path="category/:slug" element={<Category />} />
              <Route path="profile" element={<Profile />} />
              <Route path="favorites" element={<Favorites />} />
              <Route path="favorites/folders/:folderId" element={<FolderVideos />} />
              <Route path="history" element={<History />} />
              <Route path="actor/:id" element={<ActorDetail />} />
              <Route path="director/:id" element={<DirectorDetail />} />
              <Route path="series" element={<SeriesList />} />
              <Route path="series/:id" element={<SeriesDetail />} />
              <Route path="help" element={<HelpCenter />} />
              <Route path="contact" element={<ContactUs />} />
              <Route path="faq" element={<FAQ />} />
              <Route path="privacy" element={<PrivacyPolicy />} />
              <Route path="terms" element={<TermsOfService />} />
              <Route path="announcements" element={<Announcements />} />
              <Route path="my-list" element={<MyList />} />
              <Route path="shared/:token" element={<SharedList />} />
            </Route>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/oauth/:provider/callback" element={<OAuthCallback />} />
            </Routes>
          </Suspense>
          
          {/* PWA Install Prompt */}
          <PWAInstallPrompt />
        </BrowserRouter>
      </ThemeProvider>
    </ErrorBoundary>
  )
}

export default App
