/**
 * Menu Badge Context
 * 管理菜单徽章数据（待处理数量等）
 */

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from '@/utils/axios';

interface BadgeData {
  pendingComments: number;
  pendingVideos: number;
  pendingUsers: number;
  pendingBanners: number;
  activeAlerts: number;
}

interface MenuBadgeContextType {
  badges: BadgeData;
  refreshBadges: () => Promise<void>;
  loading: boolean;
}

const MenuBadgeContext = createContext<MenuBadgeContextType | undefined>(undefined);

export const useMenuBadges = () => {
  const context = useContext(MenuBadgeContext);
  if (!context) {
    throw new Error('useMenuBadges must be used within MenuBadgeProvider');
  }
  return context;
};

interface MenuBadgeProviderProps {
  children: ReactNode;
}

export const MenuBadgeProvider = ({ children }: MenuBadgeProviderProps) => {
  const [badges, setBadges] = useState<BadgeData>({
    pendingComments: 0,
    pendingVideos: 0,
    pendingUsers: 0,
    pendingBanners: 0,
    activeAlerts: 0,
  });
  const [loading, setLoading] = useState(false);

  const fetchBadges = async () => {
    try {
      setLoading(true);
      
      // 并行获取各类待处理数量
      const [commentsRes, videosRes, alertsRes] = await Promise.allSettled([
        // 待审核评论
        axios.get('/api/v1/admin/comments', {
          params: { page: 1, page_size: 1, status: 'pending' }
        }),
        // 草稿状态视频（待发布）
        axios.get('/api/v1/admin/videos', {
          params: { page: 1, page_size: 1, status: 'DRAFT' }
        }),
        // 活跃告警数量
        axios.get('/api/v1/admin/system-health/alerts/active/count'),
      ]);

      setBadges({
        pendingComments:
          commentsRes.status === 'fulfilled'
            ? commentsRes.value.data?.total || 0
            : 0,
        pendingVideos:
          videosRes.status === 'fulfilled'
            ? videosRes.value.data?.total || 0
            : 0,
        pendingUsers: 0, // 可以添加待审核用户逻辑
        pendingBanners: 0,
        activeAlerts:
          alertsRes.status === 'fulfilled'
            ? alertsRes.value.data?.count || 0
            : 0,
      });
    } catch (error) {
      console.error('Failed to fetch menu badges:', error);
    } finally {
      setLoading(false);
    }
  };

  const refreshBadges = async () => {
    await fetchBadges();
  };

  useEffect(() => {
    fetchBadges();

    // 每 5 分钟自动刷新一次
    const interval = setInterval(fetchBadges, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <MenuBadgeContext.Provider value={{ badges, refreshBadges, loading }}>
      {children}
    </MenuBadgeContext.Provider>
  );
};

