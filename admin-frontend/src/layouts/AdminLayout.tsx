import { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, theme, Space, Button, Tooltip } from 'antd'
import { QuestionCircleOutlined } from '@ant-design/icons'
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
import { useTranslation } from 'react-i18next'
import Breadcrumb from '../components/Breadcrumb'
import LanguageSwitcher from '../components/LanguageSwitcher'
import ThemeSwitcher from '../components/ThemeSwitcher'
import HotkeysHelp from '../components/HotkeysHelp'
import PageTransition from '../components/PageTransition'
import { useGlobalHotkeys } from '../hooks/useGlobalHotkeys'

const { Header, Content, Sider } = Layout

const AdminLayout = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)
  const [hotkeysHelpVisible, setHotkeysHelpVisible] = useState(false)
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken()
  
  // Enable global hotkeys
  useGlobalHotkeys()

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
      label: t('menu.dashboard'),
    },
    {
      key: '/videos',
      icon: <VideoCameraOutlined />,
      label: t('menu.videos'),
    },
    {
      key: '/users',
      icon: <UserOutlined />,
      label: t('menu.users'),
    },
    {
      key: '/comments',
      icon: <CommentOutlined />,
      label: t('menu.comments'),
    },
    {
      key: '/banners',
      icon: <PictureOutlined />,
      label: t('menu.banners'),
    },
    {
      key: '/announcements',
      icon: <SoundOutlined />,
      label: t('menu.announcements'),
    },
    {
      key: '/actors',
      icon: <TeamOutlined />,
      label: t('menu.actors'),
    },
    {
      key: '/directors',
      icon: <TeamOutlined />,
      label: t('menu.directors'),
    },
    {
      key: '/statistics',
      icon: <BarChartOutlined />,
      label: t('menu.statistics'),
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: t('menu.settings'),
    },
    {
      key: '/logs',
      icon: <FileTextOutlined />,
      label: t('menu.logs'),
    },
    {
      key: '/ip-blacklist',
      icon: <StopOutlined />,
      label: t('menu.ipBlacklist'),
    },
    {
      key: '/series',
      icon: <AppstoreOutlined />,
      label: t('menu.series'),
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
            {t('common.adminPanel')}
          </div>
          <Space size="large">
            <Tooltip title="快捷键帮助 (Shift+?)">
              <Button
                type="text"
                icon={<QuestionCircleOutlined />}
                onClick={() => setHotkeysHelpVisible(true)}
              />
            </Tooltip>
            <ThemeSwitcher />
            <LanguageSwitcher />
            <a onClick={handleLogout} style={{ color: 'inherit', cursor: 'pointer' }}>
              <LogoutOutlined /> {t('common.logout')}
            </a>
          </Space>
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
            <PageTransition>
              <Outlet />
            </PageTransition>
          </div>
        </Content>
      </Layout>
      
      {/* Hotkeys Help Modal */}
      <HotkeysHelp visible={hotkeysHelpVisible} onClose={() => setHotkeysHelpVisible(false)} />
    </Layout>
  )
}

export default AdminLayout
