import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { App as AntApp } from 'antd'
import { useEffect, useState } from 'react'
import AdminLayout from './layouts/AdminLayout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import VideoList from './pages/Videos/List'
import VideoEdit from './pages/Videos/Edit'
import UserList from './pages/Users/List'
import CommentList from './pages/Comments/List'
import Statistics from './pages/Statistics'
import Settings from './pages/Settings'
import OperationLogs from './pages/Logs'
import BannersList from './pages/Banners/List'
import AnnouncementsList from './pages/Announcements/List'
import ActorsList from './pages/Actors/List'
import DirectorsList from './pages/Directors/List'
import IPBlacklist from './pages/IPBlacklist'
import SeriesList from './pages/Series/List'
import SeriesEdit from './pages/Series/Edit'

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const location = useLocation()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isChecking, setIsChecking] = useState(true)

  useEffect(() => {
    // Check authentication whenever location changes
    const checkAuth = () => {
      const token = localStorage.getItem('admin_access_token')
      setIsAuthenticated(!!token)
      setIsChecking(false)
    }

    checkAuth()
  }, [location]) // Re-check when location changes

  if (isChecking) {
    return <div>Loading...</div>
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

function App() {
  return (
    <AntApp>
      <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AdminLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="videos" element={<VideoList />} />
          <Route path="videos/new" element={<VideoEdit />} />
          <Route path="videos/:id/edit" element={<VideoEdit />} />
          <Route path="users" element={<UserList />} />
          <Route path="comments" element={<CommentList />} />
          <Route path="banners" element={<BannersList />} />
          <Route path="announcements" element={<AnnouncementsList />} />
          <Route path="actors" element={<ActorsList />} />
          <Route path="directors" element={<DirectorsList />} />
          <Route path="statistics" element={<Statistics />} />
          <Route path="settings" element={<Settings />} />
          <Route path="logs" element={<OperationLogs />} />
          <Route path="ip-blacklist" element={<IPBlacklist />} />
          <Route path="series" element={<SeriesList />} />
          <Route path="series/new" element={<SeriesEdit />} />
          <Route path="series/:id" element={<SeriesEdit />} />
          <Route path="series/:id/edit" element={<SeriesEdit />} />
        </Route>
      </Routes>
    </BrowserRouter>
    </AntApp>
  )
}

export default App
