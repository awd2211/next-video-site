import { Empty, Button, Space } from 'antd';
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons';

export type EmptyStateType = 'no-data' | 'no-search-results' | 'error';

interface EmptyStateProps {
  type?: EmptyStateType;
  title?: string;
  description?: string;
  actionText?: string;
  onAction?: () => void;
  onRefresh?: () => void;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  type = 'no-data',
  title,
  description,
  actionText,
  onAction,
  onRefresh,
}) => {
  const getConfig = () => {
    switch (type) {
      case 'no-search-results':
        return {
          image: Empty.PRESENTED_IMAGE_SIMPLE,
          title: title || '未找到相关内容',
          description: description || '尝试调整搜索条件或清空筛选',
        };
      case 'error':
        return {
          image: Empty.PRESENTED_IMAGE_DEFAULT,
          title: title || '加载失败',
          description: description || '请刷新页面重试',
        };
      default:
        return {
          image: Empty.PRESENTED_IMAGE_SIMPLE,
          title: title || '暂无数据',
          description: description || '开始创建第一条记录',
        };
    }
  };

  const config = getConfig();

  return (
    <Empty
      image={config.image}
      description={
        <div style={{ padding: '16px 0' }}>
          <div style={{ fontSize: 16, fontWeight: 500, marginBottom: 8 }}>
            {config.title}
          </div>
          {config.description && (
            <div style={{ color: '#999', fontSize: 14 }}>
              {config.description}
            </div>
          )}
        </div>
      }
    >
      <Space>
        {onAction && actionText && (
          <Button type="primary" icon={<PlusOutlined />} onClick={onAction}>
            {actionText}
          </Button>
        )}
        {onRefresh && (
          <Button icon={<ReloadOutlined />} onClick={onRefresh}>
            刷新
          </Button>
        )}
      </Space>
    </Empty>
  );
};

export default EmptyState;

