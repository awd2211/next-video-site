// @ts-nocheck
import { useQuery } from '@tanstack/react-query';
import { AlertCircle, Info, AlertTriangle, CheckCircle, Pin } from 'lucide-react';
import axios from 'axios';
import Layout from '../../components/Layout';
import './styles.css';

interface Announcement {
  id: number;
  title: string;
  content: string;
  type: string;
  is_pinned: boolean;
  created_at: string;
}

const Announcements = () => {
  // 获取公告列表
  const { data: announcements, isLoading } = useQuery({
    queryKey: ['announcements', 'all'],
    queryFn: async () => {
      const response = await axios.get<Announcement[]>('/api/v1/announcements?limit=50');
      return response.data;
    },
  });

  // 获取图标
  const getIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'error':
      case 'danger':
        return <AlertCircle className="w-6 h-6" />;
      case 'warning':
        return <AlertTriangle className="w-6 h-6" />;
      case 'success':
        return <CheckCircle className="w-6 h-6" />;
      case 'info':
      default:
        return <Info className="w-6 h-6" />;
    }
  };

  // 获取样式类名
  const getTypeClass = (type: string) => {
    switch (type.toLowerCase()) {
      case 'error':
      case 'danger':
        return 'announcement-card-error';
      case 'warning':
        return 'announcement-card-warning';
      case 'success':
        return 'announcement-card-success';
      case 'info':
      default:
        return 'announcement-card-info';
    }
  };

  // 格式化日期
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <Layout>
      <div className="announcements-page">
        <div className="announcements-header">
          <h1>网站公告</h1>
          <p>查看平台最新动态和重要通知</p>
        </div>

        {isLoading ? (
          <div className="announcements-loading">
            <div className="loading-spinner"></div>
            <p>加载中...</p>
          </div>
        ) : announcements && announcements.length > 0 ? (
          <div className="announcements-list">
            {announcements.map((announcement) => (
              <div
                key={announcement.id}
                className={`announcement-card ${getTypeClass(announcement.type)}`}
              >
                <div className="announcement-card-icon">
                  {getIcon(announcement.type)}
                </div>

                <div className="announcement-card-content">
                  <div className="announcement-card-header">
                    <h2 className="announcement-card-title">
                      {announcement.is_pinned && (
                        <Pin className="w-5 h-5 pinned-icon" />
                      )}
                      {announcement.title}
                    </h2>
                    <span className="announcement-card-date">
                      {formatDate(announcement.created_at)}
                    </span>
                  </div>

                  <div className="announcement-card-body">
                    {announcement.content}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="announcements-empty">
            <Info className="w-16 h-16 text-gray-400" />
            <p>暂无公告</p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Announcements;
