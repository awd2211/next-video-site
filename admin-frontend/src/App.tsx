import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { App as AntApp } from 'antd'
import { useEffect, useState, lazy, Suspense } from 'react'
import { Spin } from 'antd'
import ErrorBoundary from './components/ErrorBoundary'
import AdminLayout from './layouts/AdminLayout'
import { MenuBadgeProvider } from './contexts/MenuBadgeContext'

// Lazy load pages for better performance
const Login = lazy(() => import('./pages/Login'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const VideoList = lazy(() => import('./pages/Videos/List'))
const VideoEdit = lazy(() => import('./pages/Videos/Edit'))
const VideoAnalytics = lazy(() => import('./pages/Videos/Analytics'))
const UserList = lazy(() => import('./pages/Users/List'))
const CommentList = lazy(() => import('./pages/Comments/List'))
const Statistics = lazy(() => import('./pages/Statistics'))
const Settings = lazy(() => import('./pages/Settings'))
const OperationLogs = lazy(() => import('./pages/Logs'))
const BannersList = lazy(() => import('./pages/Banners/List'))
const AnnouncementsList = lazy(() => import('./pages/Announcements/List'))
const ActorsList = lazy(() => import('./pages/Actors/List'))
const DirectorsList = lazy(() => import('./pages/Directors/List'))
const IPBlacklist = lazy(() => import('./pages/IPBlacklist'))
const SeriesList = lazy(() => import('./pages/Series/List'))
const SeriesEdit = lazy(() => import('./pages/Series/Edit'))
const MediaManager = lazy(() => import('./pages/MediaManager'))
const Profile = lazy(() => import('./pages/Profile'))
const AIManagement = lazy(() => import('./pages/AIManagement'))
const SystemHealth = lazy(() => import('./pages/SystemHealth'))
const UserDetail = lazy(() => import('./pages/Users/Detail'))
const RolesList = lazy(() => import('./pages/Roles/List'))
const ReportsDashboard = lazy(() => import('./pages/Reports/Dashboard'))
const EmailManagement = lazy(() => import('./pages/Email/Management'))
const SchedulingList = lazy(() => import('./pages/Scheduling/List'))

// Loading component for Suspense
const PageLoading = () => (
  <div style={{ textAlign: 'center', padding: '100px 0' }}>
    <Spin size="large" tip="Loading..." />
  </div>
)

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
    <ErrorBoundary>
      <AntApp>
        <BrowserRouter>
          <Suspense fallback={<PageLoading />}>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <MenuBadgeProvider>
                      <AdminLayout />
                    </MenuBadgeProvider>
                  </ProtectedRoute>
                }
              >
                <Route index element={<Dashboard />} />
                <Route path="videos" element={<VideoList />} />
                <Route path="videos/new" element={<VideoEdit />} />
                <Route path="videos/:id/edit" element={<VideoEdit />} />
                <Route path="videos/:id/analytics" element={<VideoAnalytics />} />
                <Route path="users" element={<UserList />} />
                <Route path="users/:id" element={<UserDetail />} />
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
                <Route path="media" element={<MediaManager />} />
                <Route path="profile" element={<Profile />} />
                <Route path="ai-management" element={<AIManagement />} />
                <Route path="system-health" element={<SystemHealth />} />
                <Route path="roles" element={<RolesList />} />
                <Route path="reports" element={<ReportsDashboard />} />
                <Route path="email-management" element={<EmailManagement />} />
                <Route path="scheduling" element={<SchedulingList />} />
              </Route>
            </Routes>
          </Suspense>
        </BrowserRouter>
      </AntApp>
    </ErrorBoundary>
  )
}

export default App
