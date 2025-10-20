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
  LineChartOutlined,
  LockOutlined,
  CalendarOutlined,
  DollarOutlined,
  CreditCardOutlined,
  GiftOutlined,
  WalletOutlined,
  HeartOutlined,
  BellOutlined,
  LineChartOutlined as ChartOutlined,
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
import profileService from '../services/profileService';
import { useTranslation as useI18n } from 'react-i18next';
import './AdminLayout.css';

const { Header, Content, Sider } = Layout;
const { Search } = Input;

interface MenuItem {
  key: string;
  icon: React.ReactNode;
  label: string;
  badge?: number;
  children?: MenuItem[];
}

interface MenuGroup {
  key: string;
  label: string;
  items: MenuItem[];
}

const AdminLayout = () => {
  const { t } = useTranslation();
  const { i18n } = useI18n();
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const [hotkeysHelpVisible, setHotkeysHelpVisible] = useState(false);
  const [searchValue, setSearchValue] = useState('');
  const { badges } = useMenuBadges();
  const { theme: currentTheme, setTheme } = useTheme();
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

  // Load user preferences on mount
  useEffect(() => {
    const loadUserPreferences = async () => {
      try {
        const profile = await profileService.getProfile();

        // Apply theme preference
        if (profile.preferred_theme && profile.preferred_theme !== currentTheme) {
          setTheme(profile.preferred_theme as 'light' | 'dark');
        }

        // Apply language preference
        if (profile.preferred_language && profile.preferred_language !== i18n.language) {
          i18n.changeLanguage(profile.preferred_language);
        }
      } catch (error) {
        console.error('Failed to load user preferences:', error);
        // Don't show error to user, just use defaults
      }
    };

    loadUserPreferences();
  }, []); // Only run once on mount

  // 更新 CSS 变量（用于设置页面底部栏）
  useEffect(() => {
    document.documentElement.style.setProperty('--sidebar-width', `${sidebarWidth}px`);
  }, [sidebarWidth]);

  // 菜单分组配置（优化后的结构 - 方案A）
  const menuGroups: MenuGroup[] = [
    // 📊 概览
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
    // 📹 内容管理
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
          icon: <CalendarOutlined />,
          label: t('menu.scheduling') || '内容调度',
        },
        {
          key: '/comments',
          icon: <CommentOutlined />,
          label: t('menu.comments'),
          badge: badges.pendingComments > 0 ? badges.pendingComments : undefined,
        },
      ],
    },
    // 👥 用户与权限
    {
      key: 'usersAndPermissions',
      label: t('menu.groupUsersAndPermissions') || '用户与权限',
      items: [
        {
          key: '/users',
          icon: <UserOutlined />,
          label: t('menu.users'),
        },
        {
          key: '/roles',
          icon: <TeamOutlined />,
          label: t('menu.roles') || '角色管理',
        },
        {
          key: '/ip-blacklist',
          icon: <StopOutlined />,
          label: t('menu.ipBlacklist'),
        },
        {
          key: '/oauth-settings',
          icon: <LockOutlined />,
          label: t('menu.oauthSettings') || 'OAuth设置',
        },
      ],
    },
    // 📁 资源库
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
    // 🤖 AI与智能
    {
      key: 'aiAndIntelligence',
      label: t('menu.groupAIAndIntelligence') || 'AI与智能',
      items: [
        {
          key: '/ai-management',
          icon: <RobotOutlined />,
          label: t('menu.aiManagement'),
        },
        {
          key: '/ai-logs',
          icon: <FileTextOutlined />,
          label: t('menu.aiLogs') || 'AI日志',
        },
      ],
    },
    // 📈 数据分析
    {
      key: 'dataAnalytics',
      label: t('menu.groupDataAnalytics') || '数据分析',
      items: [
        {
          key: '/statistics',
          icon: <LineChartOutlined />,
          label: t('menu.statistics'),
        },
        {
          key: '/reports',
          icon: <BarChartOutlined />,
          label: t('menu.reports') || '系统报告',
        },
        {
          key: '/logs',
          icon: <FileTextOutlined />,
          label: t('menu.logs'),
        },
      ],
    },
    // 💳 支付管理
    {
      key: 'payment',
      label: t('menu.groupPayment') || '支付管理',
      items: [
        {
          key: '/payment/plans',
          icon: <DollarOutlined />,
          label: t('menu.subscriptionPlans') || '订阅计划',
        },
        {
          key: '/payment/subscriptions',
          icon: <WalletOutlined />,
          label: t('menu.subscriptions') || '订阅管理',
        },
        {
          key: '/payment/payments',
          icon: <CreditCardOutlined />,
          label: t('menu.payments') || '支付记录',
        },
        {
          key: '/payment/coupons',
          icon: <GiftOutlined />,
          label: t('menu.coupons') || '优惠券',
        },
      ],
    },
    // ⚙️ 系统管理
    {
      key: 'system',
      label: t('menu.groupSystem'),
      items: [
        {
          key: 'system-health-submenu',
          icon: <HeartOutlined />,
          label: t('menu.systemHealth'),
          children: [
            {
              key: '/system-health',
              icon: <ApiOutlined />,
              label: t('menu.systemHealthOverview') || 'Overview',
            },
            {
              key: '/system-health/alerts',
              icon: <BellOutlined />,
              label: t('menu.systemHealthAlerts') || 'Alerts',
              badge: badges.activeAlerts,
            },
            {
              key: '/system-health/sla',
              icon: <ChartOutlined />,
              label: t('menu.systemHealthSLA') || 'SLA Reports',
            },
          ],
        },
        {
          key: '/email-management',
          icon: <MailOutlined />,
          label: t('menu.emailManagement') || '邮件管理',
        },
        {
          key: '/sentry-config',
          icon: <ApiOutlined />,
          label: t('menu.sentryConfig') || 'Sentry 配置',
        },
        {
          key: '/settings',
          icon: <SettingOutlined />,
          label: t('menu.settings'),
        },
      ],
    },
  ];

  // 扁平化所有菜单项（用于搜索）- 包括子菜单项
  const allMenuItems = useMemo(() => {
    return menuGroups.flatMap((group) =>
      group.items.flatMap((item) =>
        item.children ? item.children : item
      )
    );
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

    // 检查是否匹配完整路径（用于子菜单路由如 /system-health/alerts）
    const fullPath = path.endsWith('/') ? path.slice(0, -1) : path;

    // 查找是否有完全匹配的菜单项
    const hasExactMatch = allMenuItems.some(item => item.key === fullPath);
    if (hasExactMatch) {
      return fullPath;
    }

    // 否则返回第一段路径
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
  const renderMenuItem = (item: MenuItem): any => {
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

    // 有子菜单的情况
    if (item.children && item.children.length > 0) {
      // 收起状态：只显示父菜单图标
      if (collapsed) {
        return {
          key: item.key,
          icon: null,
          label: (
            <Tooltip title={item.label} placement="right">
              <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {item.icon}
              </span>
            </Tooltip>
          ),
          children: item.children.map((child) => renderMenuItem(child)),
        };
      }

      // 展开状态：显示子菜单
      return {
        key: item.key,
        icon: item.icon,
        label,
        children: item.children.map((child) => renderMenuItem(child)),
      };
    }

    // 没有子菜单的普通菜单项
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
            padding: 0,
            minHeight: 'calc(100vh - 56px)',
            background: currentTheme === 'dark' ? '#0f1b2a' : '#f7f6f3',
          }}
        >
          <PageTransition>
            <Outlet />
          </PageTransition>
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
