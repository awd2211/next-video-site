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
import History from './pages/History'
import ActorDetail from './pages/ActorDetail'
import DirectorDetail from './pages/DirectorDetail'

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
          <Route path="history" element={<History />} />
          <Route path="actor/:id" element={<ActorDetail />} />
          <Route path="director/:id" element={<DirectorDetail />} />
        </Route>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
