import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
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

function App() {
  const isAuthenticated = !!localStorage.getItem('admin_access_token')

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            isAuthenticated ? <AdminLayout /> : <Navigate to="/login" replace />
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
          <Route path="statistics" element={<Statistics />} />
          <Route path="settings" element={<Settings />} />
          <Route path="logs" element={<OperationLogs />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
