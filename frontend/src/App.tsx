import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import { ThemeProvider } from './contexts/ThemeContext'
import Layout from './components/Layout'
import Home from './pages/Home'

// Lazy load components for code splitting
const VideoDetail = lazy(() => import('./pages/VideoDetail'))
const Search = lazy(() => import('./pages/Search'))
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
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Suspense fallback={<PageLoader />}>
          <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="video/:id" element={<VideoDetail />} />
            <Route path="search" element={<Search />} />
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
          </Route>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App
