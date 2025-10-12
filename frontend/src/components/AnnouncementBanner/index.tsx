import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { X, AlertCircle, Info, AlertTriangle, CheckCircle, ChevronLeft, ChevronRight } from 'lucide-react';
import axios from 'axios';
import './styles.css';

interface Announcement {
  id: number;
  title: string;
  content: string;
  type: string;
  is_pinned: boolean;
  created_at: string;
}

const AnnouncementBanner = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [closedIds, setClosedIds] = useState<number[]>([]);

  // 从localStorage加载已关闭的公告ID
  useEffect(() => {
    const stored = localStorage.getItem('closedAnnouncements');
    if (stored) {
      try {
        setClosedIds(JSON.parse(stored));
      } catch (e) {
        console.error('Failed to parse closed announcements', e);
      }
    }
  }, []);

  // 获取公告列表
  const { data: announcements } = useQuery({
    queryKey: ['announcements'],
    queryFn: async () => {
      const response = await axios.get<Announcement[]>('/api/v1/announcements?limit=5');
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5分钟
  });

  // 过滤已关闭的公告
  const activeAnnouncements = announcements?.filter(
    (a) => !closedIds.includes(a.id)
  ) || [];

  // 如果没有活跃公告，不显示横幅
  if (activeAnnouncements.length === 0) {
    return null;
  }

  const currentAnnouncement = activeAnnouncements[currentIndex];

  // 关闭当前公告
  const handleClose = () => {
    const newClosedIds = [...closedIds, currentAnnouncement.id];
    setClosedIds(newClosedIds);
    localStorage.setItem('closedAnnouncements', JSON.stringify(newClosedIds));

    // 如果还有其他公告，切换到下一个
    if (activeAnnouncements.length > 1) {
      setCurrentIndex((prev) => (prev >= activeAnnouncements.length - 1 ? 0 : prev));
    }
  };

  // 上一个公告
  const handlePrev = () => {
    setCurrentIndex((prev) =>
      prev === 0 ? activeAnnouncements.length - 1 : prev - 1
    );
  };

  // 下一个公告
  const handleNext = () => {
    setCurrentIndex((prev) =>
      prev === activeAnnouncements.length - 1 ? 0 : prev + 1
    );
  };

  // 获取图标
  const getIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'error':
      case 'danger':
        return <AlertCircle className="w-5 h-5" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5" />;
      case 'success':
        return <CheckCircle className="w-5 h-5" />;
      case 'info':
      default:
        return <Info className="w-5 h-5" />;
    }
  };

  // 获取样式类名
  const getTypeClass = (type: string) => {
    switch (type.toLowerCase()) {
      case 'error':
      case 'danger':
        return 'announcement-error';
      case 'warning':
        return 'announcement-warning';
      case 'success':
        return 'announcement-success';
      case 'info':
      default:
        return 'announcement-info';
    }
  };

  return (
    <div className={`announcement-banner ${getTypeClass(currentAnnouncement.type)}`}>
      <div className="announcement-content">
        <div className="announcement-icon">
          {getIcon(currentAnnouncement.type)}
        </div>

        <div className="announcement-text">
          <div className="announcement-title">
            {currentAnnouncement.title}
            {currentAnnouncement.is_pinned && (
              <span className="announcement-pinned-badge">置顶</span>
            )}
          </div>
          <div className="announcement-body">{currentAnnouncement.content}</div>
        </div>

        <div className="announcement-actions">
          {/* 如果有多个公告，显示导航按钮 */}
          {activeAnnouncements.length > 1 && (
            <div className="announcement-nav">
              <button
                onClick={handlePrev}
                className="announcement-nav-btn"
                aria-label="Previous announcement"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="announcement-counter">
                {currentIndex + 1} / {activeAnnouncements.length}
              </span>
              <button
                onClick={handleNext}
                className="announcement-nav-btn"
                aria-label="Next announcement"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}

          <button
            onClick={handleClose}
            className="announcement-close-btn"
            aria-label="Close announcement"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default AnnouncementBanner;
