import { useState, useMemo, useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Layout,
  Menu,
  theme,
  Space,
  Button,
  Tooltip,
  Input,
  Badge,
  Avatar,
} from 'antd';
import { useResizableSidebar } from '../hooks/useResizableSidebar';
import {
  QuestionCircleOutlined,
  PlayCircleOutlined,
  SearchOutlined,
} from '@ant-design/icons';
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
  UserAddOutlined,
  FolderOutlined,
  RobotOutlined,
  ApiOutlined,
  MailOutlined,
  ClockCircleOutlined,
  SafetyOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import Breadcrumb from '../components/Breadcrumb';
import LanguageSwitcher from '../components/LanguageSwitcher';
import ThemeSwitcher from '../components/ThemeSwitcher';
import HotkeysHelp from '../components/HotkeysHelp';
import PageTransition from '../components/PageTransition';
import NotificationBadge from '../components/NotificationBadge';
import { useGlobalHotkeys } from '../hooks/useGlobalHotkeys';
import { useMenuBadges } from '../contexts/MenuBadgeContext';
import { useTheme } from '../contexts/ThemeContext';
import './AdminLayout.css';

const { Header, Content, Sider } = Layout;
const { Search } = Input;

interface MenuItem {
  key: string;
  icon: React.ReactNode;
  label: string;
  badge?: number;
}

interface MenuGroup {
  key: string;
  label: string;
  items: MenuItem[];
}

const AdminLayout = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const [hotkeysHelpVisible, setHotkeysHelpVisible] = useState(false);
  const [searchValue, setSearchValue] = useState('');
  const { badges } = useMenuBadges();
  const { theme: currentTheme } = useTheme();
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  // Resizable sidebar
  const { sidebarWidth, isResizing, handleMouseDown } = useResizableSidebar({
    defaultWidth: 260,
    minWidth: 200,
    maxWidth: 400,
  });

  // Enable global hotkeys
  useGlobalHotkeys();

  // 更新 CSS 变量（用于设置页面底部栏）
  useEffect(() => {
    document.documentElement.style.setProperty('--sidebar-width', `${sidebarWidth}px`);
  }, [sidebarWidth]);

  // 菜单分组配置（AWS 风格）
  const menuGroups: MenuGroup[] = [
    {
      key: 'overview',
      label: t('menu.groupOverview'),
      items: [
        {
          key: '/',
          icon: <DashboardOutlined />,
          label: t('menu.dashboard'),
        },
      ],
    },
    {
      key: 'content',
      label: t('menu.groupContent'),
      items: [
        {
          key: '/videos',
          icon: <VideoCameraOutlined />,
          label: t('menu.videos'),
          badge: badges.pendingVideos,
        },
        {
          key: '/series',
          icon: <AppstoreOutlined />,
          label: t('menu.series'),
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
          key: '/scheduling',
          icon: <ClockCircleOutlined />,
          label: t('menu.scheduling') || '内容调度',
        },
      ],
    },
    {
      key: 'community',
      label: t('menu.groupCommunity'),
      items: [
        {
          key: '/users',
          icon: <UserOutlined />,
          label: t('menu.users'),
        },
        {
          key: '/comments',
          icon: <CommentOutlined />,
          label: t('menu.comments'),
          badge: badges.pendingComments,
        },
      ],
    },
    {
      key: 'resources',
      label: t('menu.groupResources'),
      items: [
        {
          key: '/media',
          icon: <FolderOutlined />,
          label: t('menu.media'),
        },
        {
          key: '/actors',
          icon: <TeamOutlined />,
          label: t('menu.actors'),
        },
        {
          key: '/directors',
          icon: <UserAddOutlined />,
          label: t('menu.directors'),
        },
      ],
    },
    {
      key: 'system',
      label: t('menu.groupSystem'),
      items: [
        {
          key: '/system-health',
          icon: <ApiOutlined />,
          label: t('menu.systemHealth'),
        },
        {
          key: '/ai-management',
          icon: <RobotOutlined />,
          label: t('menu.aiManagement'),
        },
        {
          key: '/roles',
          icon: <TeamOutlined />,
          label: t('menu.roles') || '角色权限',
        },
        {
          key: '/reports',
          icon: <FileTextOutlined />,
          label: t('menu.reports') || '数据报表',
        },
        {
          key: '/email-management',
          icon: <MailOutlined />,
          label: t('menu.emailManagement') || '邮件管理',
        },
        {
          key: '/statistics',
          icon: <BarChartOutlined />,
          label: t('menu.statistics'),
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
          key: '/oauth-settings',
          icon: <SafetyOutlined />,
          label: t('menu.oauthSettings') || 'OAuth 设置',
        },
        {
          key: '/settings',
          icon: <SettingOutlined />,
          label: t('menu.settings'),
        },
      ],
    },
  ];

  // 扁平化所有菜单项（用于搜索）
  const allMenuItems = useMemo(() => {
    return menuGroups.flatMap((group) => group.items);
  }, [menuGroups]);

  // 搜索过滤后的菜单组
  const filteredMenuGroups = useMemo(() => {
    if (!searchValue.trim()) return menuGroups;

    const lowerSearch = searchValue.toLowerCase();
    return menuGroups
      .map((group) => ({
        ...group,
        items: group.items.filter((item) =>
          item.label.toLowerCase().includes(lowerSearch)
        ),
      }))
      .filter((group) => group.items.length > 0);
  }, [searchValue, menuGroups]);

  // 获取当前选中的菜单项
  const getSelectedKey = () => {
    const path = location.pathname;
    if (path === '/') return '/';
    const segments = path.split('/').filter(Boolean);
    return `/${segments[0]}`;
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_access_token');
    localStorage.removeItem('admin_refresh_token');
    navigate('/login');
  };

  // 搜索处理
  const handleSearch = (value: string) => {
    if (!value.trim()) return;

    const found = allMenuItems.find((item) =>
      item.label.toLowerCase().includes(value.toLowerCase())
    );
    if (found) {
      navigate(found.key);
      setSearchValue('');
    }
  };

  // 渲染菜单项（带徽章）
  const renderMenuItem = (item: MenuItem) => {
    // 收起状态：只显示图标（通过 Tooltip 包裹）
    if (collapsed) {
      return {
        key: item.key,
        icon: null, // 不使用 icon 属性
        label: (
          <Tooltip title={item.label} placement="right">
            <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {item.icon}
            </span>
          </Tooltip>
        ),
      };
    }

    // 展开状态：显示图标 + 文字 + 徽章
    const label = (
      <div className="menu-item-content">
        <span>{item.label}</span>
        {item.badge && item.badge > 0 && (
          <Badge
            count={item.badge}
            size="small"
            style={{
              marginLeft: 8,
              backgroundColor: '#ff4d4f',
            }}
          />
        )}
      </div>
    );

    return {
      key: item.key,
      icon: item.icon,
      label,
    };
  };

  // 构建 Ant Design Menu items
  const menuItems = filteredMenuGroups.flatMap((group, groupIndex) => {
    const items = [
      // 分组标题（非收起状态）
      ...(!collapsed
        ? [
            {
              type: 'group' as const,
              label: (
                <div className="menu-group-label">{group.label}</div>
              ),
              key: `group-${group.key}`,
            },
          ]
        : []),
      // 菜单项
      ...group.items.map((item) => renderMenuItem(item)),
    ];

    // 在分组之间添加分割线（除了最后一组）
    if (groupIndex < filteredMenuGroups.length - 1 && !collapsed) {
      items.push({
        type: 'divider',
        key: `divider-${group.key}`,
      } as any);
    }

    return items;
  });

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        width={sidebarWidth}
        className="admin-sidebar"
        style={{
          '--sidebar-width': `${sidebarWidth}px`,
        } as React.CSSProperties}
      >
        {/* Logo 区域 */}
        <div className="sidebar-logo">
          {collapsed ? (
            <Avatar style={{ background: '#0073bb' }} size={40}>
              VS
            </Avatar>
          ) : (
            <Space size={12} align="center">
              <Avatar
                style={{ background: '#0073bb' }}
                size={40}
                icon={<PlayCircleOutlined />}
              />
              <div>
                <div className="logo-title">VideoSite</div>
                <div className="logo-subtitle">Admin Console</div>
              </div>
            </Space>
          )}
        </div>

        {/* 搜索栏（非收起状态）*/}
        {!collapsed && (
          <div className="sidebar-search">
            <Search
              placeholder={t('menu.searchPlaceholder')}
              size="small"
              prefix={<SearchOutlined />}
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              onSearch={handleSearch}
              allowClear
            />
          </div>
        )}

        {/* 菜单 */}
        <Menu
          theme={currentTheme === 'dark' ? 'dark' : 'light'}
          mode="inline"
          selectedKeys={[getSelectedKey()]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          className="sidebar-menu"
        />

        {/* 拖拽手柄 */}
        {!collapsed && (
          <div
            className="sidebar-resize-handle"
            onMouseDown={handleMouseDown}
            style={{
              position: 'absolute',
              right: 0,
              top: 0,
              bottom: 0,
              width: '4px',
              cursor: 'col-resize',
              background: isResizing ? '#0073bb' : 'transparent',
              transition: 'background 0.2s',
            }}
          >
            <div
              style={{
                position: 'absolute',
                right: '-1px',
                top: '50%',
                transform: 'translateY(-50%)',
                width: '6px',
                height: '40px',
                background: 'rgba(255, 255, 255, 0.2)',
                borderRadius: '3px',
                opacity: 0.6,
              }}
            />
          </div>
        )}
      </Sider>

      <Layout
        style={{
          marginLeft: collapsed ? '80px' : `${sidebarWidth}px`,
          transition: isResizing ? 'none' : 'margin-left 0.2s',
        }}
      >
        <Header
          className="admin-header"
          style={{
            padding: '0 24px',
            background: colorBgContainer,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            borderBottom: currentTheme === 'dark' ? '1px solid rgba(255, 255, 255, 0.08)' : '1px solid #e9e9e7',
            boxShadow: '0 1px 2px 0 rgba(0, 7, 22, 0.05)',
            height: '56px',
            lineHeight: '56px',
          }}
        >
          <div style={{
            fontSize: '14px',
            fontWeight: 700,
            color: currentTheme === 'dark' ? '#d1d5db' : '#16191f',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            {t('common.adminPanel')}
          </div>
          <Space size="middle">
            <Tooltip title={t('common.help') || '快捷键帮助 (Shift+?)'}>
              <Button
                type="text"
                icon={<QuestionCircleOutlined style={{ fontSize: 18 }} />}
                onClick={() => setHotkeysHelpVisible(true)}
                style={{
                  color: currentTheme === 'dark' ? 'rgba(255, 255, 255, 0.85)' : 'rgba(55, 53, 47, 0.85)',
                }}
              />
            </Tooltip>
            <NotificationBadge />
            <ThemeSwitcher />
            <LanguageSwitcher />
            <Button
              type="text"
              icon={<UserOutlined />}
              onClick={() => navigate('/profile')}
              style={{
                color: currentTheme === 'dark' ? 'rgba(255, 255, 255, 0.85)' : 'rgba(55, 53, 47, 0.85)',
              }}
            >
              {t('common.profile') || '个人资料'}
            </Button>
            <Button
              type="text"
              icon={<LogoutOutlined />}
              onClick={handleLogout}
              style={{
                color: currentTheme === 'dark' ? 'rgba(255, 255, 255, 0.85)' : 'rgba(55, 53, 47, 0.85)',
              }}
            >
              {t('common.logout')}
            </Button>
          </Space>
        </Header>
        <Content
          style={{
            margin: '0',
            padding: '20px 24px',
            minHeight: 'calc(100vh - 56px)',
            background: currentTheme === 'dark' ? '#0f1b2a' : '#f7f6f3',
          }}
        >
          <div style={{ marginBottom: 16 }}>
            <Breadcrumb />
          </div>
          <div
            style={{
              padding: 24,
              minHeight: 360,
              background: colorBgContainer,
              borderRadius: 8,
              border: currentTheme === 'dark' ? '1px solid rgba(255, 255, 255, 0.08)' : '1px solid #e9e9e7',
              boxShadow: '0 0 0 1px rgba(0, 7, 22, 0.05), 0 1px 1px 0 rgba(0, 7, 22, 0.05)',
            }}
          >
            <PageTransition>
              <Outlet />
            </PageTransition>
          </div>
        </Content>
      </Layout>

      {/* Hotkeys Help Modal */}
      <HotkeysHelp
        visible={hotkeysHelpVisible}
        onClose={() => setHotkeysHelpVisible(false)}
      />
    </Layout>
  );
};

export default AdminLayout;
