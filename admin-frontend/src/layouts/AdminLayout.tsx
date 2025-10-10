import { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, theme } from 'antd'
import {
  DashboardOutlined,
  VideoCameraOutlined,
  UserOutlined,
  CommentOutlined,
  BarChartOutlined,
  SettingOutlined,
  FileTextOutlined,
  LogoutOutlined,
  PictureOutlined,
  SoundOutlined,
  TeamOutlined,
  StopOutlined,
  AppstoreOutlined,
} from '@ant-design/icons'
import Breadcrumb from '../components/Breadcrumb'

const { Header, Content, Sider } = Layout

const AdminLayout = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken()

  // Get the current selected menu key based on path
  const getSelectedKey = () => {
    const path = location.pathname
    // Handle nested routes - get the first segment after /
    if (path === '/') return '/'
    const segments = path.split('/').filter(Boolean)
    return `/${segments[0]}`
  }

  const handleLogout = () => {
    localStorage.removeItem('admin_access_token')
    localStorage.removeItem('admin_refresh_token')
    navigate('/login')
  }

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/videos',
      icon: <VideoCameraOutlined />,
      label: 'Videos',
    },
    {
      key: '/users',
      icon: <UserOutlined />,
      label: 'Users',
    },
    {
      key: '/comments',
      icon: <CommentOutlined />,
      label: 'Comments',
    },
    {
      key: '/banners',
      icon: <PictureOutlined />,
      label: 'Banners',
    },
    {
      key: '/announcements',
      icon: <SoundOutlined />,
      label: 'Announcements',
    },
    {
      key: '/actors',
      icon: <TeamOutlined />,
      label: 'Actors',
    },
    {
      key: '/directors',
      icon: <TeamOutlined />,
      label: 'Directors',
    },
    {
      key: '/statistics',
      icon: <BarChartOutlined />,
      label: 'Statistics',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: 'Settings',
    },
    {
      key: '/logs',
      icon: <FileTextOutlined />,
      label: 'Logs',
    },
    {
      key: '/ip-blacklist',
      icon: <StopOutlined />,
      label: 'IP Blacklist',
    },
    {
      key: '/series',
      icon: <AppstoreOutlined />,
      label: 'Series',
    },
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}>
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: collapsed ? '16px' : '20px',
            fontWeight: 'bold',
          }}
        >
          {collapsed ? 'VS' : 'VideoSite Admin'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[getSelectedKey()]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: '0 24px', background: colorBgContainer, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
            Admin Panel
          </div>
          <div>
            <a onClick={handleLogout} style={{ color: 'inherit', cursor: 'pointer' }}>
              <LogoutOutlined /> Logout
            </a>
          </div>
        </Header>
        <Content style={{ margin: '24px 16px' }}>
          <Breadcrumb />
          <div
            style={{
              padding: 24,
              minHeight: 360,
              background: colorBgContainer,
              borderRadius: borderRadiusLG,
            }}
          >
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  )
}

export default AdminLayout
