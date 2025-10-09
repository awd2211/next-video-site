import { useState } from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
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
} from '@ant-design/icons'

const { Header, Content, Sider } = Layout

const AdminLayout = () => {
  const navigate = useNavigate()
  const [collapsed, setCollapsed] = useState(false)
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken()

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
          defaultSelectedKeys={['/']}
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
