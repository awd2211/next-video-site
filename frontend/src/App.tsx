import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import VideoDetail from './pages/VideoDetail'
import Search from './pages/Search'
import Category from './pages/Category'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'
import Favorites from './pages/Favorites'
import FolderVideos from './pages/FolderVideos'
import History from './pages/History'
import ActorDetail from './pages/ActorDetail'
import DirectorDetail from './pages/DirectorDetail'
import SeriesList from './pages/Series/SeriesList'
import SeriesDetail from './pages/Series/SeriesDetail'
import HelpCenter from './pages/HelpCenter'
import ContactUs from './pages/ContactUs'
import FAQ from './pages/FAQ'
import PrivacyPolicy from './pages/PrivacyPolicy'
import TermsOfService from './pages/TermsOfService'

function App() {
  return (
    <BrowserRouter>
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
    </BrowserRouter>
  )
}

export default App
