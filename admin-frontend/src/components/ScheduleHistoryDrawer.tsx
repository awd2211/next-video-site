import React from 'react';
import {
  Drawer,
  Timeline,
  Typography,
  Tag,
  Space,
  Empty,
  Spin,
  Alert,
  Descriptions,
  Divider,
} from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  UserOutlined,
  ThunderboltOutlined,
  RobotOutlined,
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { schedulingService, ScheduleHistory } from '@/services/scheduling';
import { useTranslation } from 'react-i18next';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

const { Text, Paragraph } = Typography;

interface ScheduleHistoryDrawerProps {
  scheduleId: number | null;
  open: boolean;
  onClose: () => void;
}

const ScheduleHistoryDrawer: React.FC<ScheduleHistoryDrawerProps> = ({
  scheduleId,
  open,
  onClose,
}) => {
  const { t } = useTranslation();

  // Fetch history data
  const { data: histories, isLoading } = useQuery({
    queryKey: ['schedule-history', scheduleId],
    queryFn: () => schedulingService.getScheduleHistory(scheduleId!, 0, 100),
    enabled: open && !!scheduleId,
  });

  // Render action tag with icon
  const renderActionTag = (action: string) => {
    const actionMap: Record<string, { color: string; icon: React.ReactNode }> = {
      created: { color: 'blue', icon: <ClockCircleOutlined /> },
      updated: { color: 'cyan', icon: <ClockCircleOutlined /> },
      executed: { color: 'green', icon: <ThunderboltOutlined /> },
      published: { color: 'success', icon: <CheckCircleOutlined /> },
      cancelled: { color: 'default', icon: <CloseCircleOutlined /> },
      failed: { color: 'error', icon: <CloseCircleOutlined /> },
      retried: { color: 'warning', icon: <ClockCircleOutlined /> },
      expired: { color: 'default', icon: <CloseCircleOutlined /> },
    };

    const config = actionMap[action.toLowerCase()] || {
      color: 'default',
      icon: <ClockCircleOutlined />,
    };

    return (
      <Tag color={config.color} icon={config.icon}>
        {t(`scheduling.action.${action.toLowerCase()}`) || action}
      </Tag>
    );
  };

  // Render status tag
  const renderStatusTag = (success: boolean) => {
    return success ? (
      <Tag color="success" icon={<CheckCircleOutlined />}>
        {t('common.success')}
      </Tag>
    ) : (
      <Tag color="error" icon={<CloseCircleOutlined />}>
        {t('common.failed')}
      </Tag>
    );
  };

  // Render timeline item
  const renderTimelineItem = (history: ScheduleHistory) => {
    const color = history.success ? 'green' : 'red';
    const dot = history.success ? (
      <CheckCircleOutlined style={{ fontSize: '16px' }} />
    ) : (
      <CloseCircleOutlined style={{ fontSize: '16px' }} />
    );

    return (
      <Timeline.Item key={history.id} dot={dot} color={color}>
        <Space direction="vertical" style={{ width: '100%' }} size="small">
          {/* Header */}
          <Space size="middle" wrap>
            {renderActionTag(history.action)}
            {renderStatusTag(history.success)}
            {history.is_automatic ? (
              <Tag icon={<RobotOutlined />} color="purple">
                {t('scheduling.automatic')}
              </Tag>
            ) : (
              <Tag icon={<UserOutlined />}>
                {t('scheduling.manual')}
              </Tag>
            )}
          </Space>

          {/* Time and executor */}
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {dayjs(history.executed_at).format('YYYY-MM-DD HH:mm:ss')} (
            {dayjs(history.executed_at).fromNow()})
            {history.execution_time_ms && ` • ${history.execution_time_ms}ms`}
            {history.executed_by && ` • ${t('common.executor')}: #${history.executed_by}`}
          </Text>

          {/* Status change */}
          {history.status_before && (
            <Text>
              <Text type="secondary">{t('common.status')}: </Text>
              <Tag color="default">{history.status_before}</Tag>
              <Text type="secondary"> → </Text>
              <Tag color="blue">{history.status_after}</Tag>
            </Text>
          )}

          {/* Message */}
          {history.message && (
            <Alert
              message={history.message}
              type={history.success ? 'success' : 'error'}
              showIcon
              style={{ marginTop: 8 }}
            />
          )}

          {/* Details */}
          {history.details && Object.keys(history.details).length > 0 && (
            <>
              <Divider style={{ margin: '8px 0' }} />
              <Descriptions
                size="small"
                column={1}
                bordered
                style={{ background: '#fafafa' }}
              >
                {Object.entries(history.details).map(([key, value]) => (
                  <Descriptions.Item
                    key={key}
                    label={<Text strong>{key}</Text>}
                  >
                    <Text code>{JSON.stringify(value)}</Text>
                  </Descriptions.Item>
                ))}
              </Descriptions>
            </>
          )}
        </Space>
      </Timeline.Item>
    );
  };

  return (
    <Drawer
      title={
        <Space>
          <ClockCircleOutlined />
          {t('scheduling.executionHistory')}
          {scheduleId && <Tag color="blue">#{scheduleId}</Tag>}
        </Space>
      }
      placement="right"
      width={600}
      onClose={onClose}
      open={open}
    >
      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '50px 0' }}>
          <Spin size="large" tip={t('common.loading')} />
        </div>
      ) : !histories || histories.length === 0 ? (
        <Empty
          description={t('scheduling.noHistory')}
          style={{ marginTop: 50 }}
        />
      ) : (
        <>
          <Alert
            message={t('scheduling.historyInfo')}
            description={t('scheduling.historyDescription', {
              count: histories.length,
            })}
            type="info"
            showIcon
            closable
            style={{ marginBottom: 24 }}
          />
          <Timeline mode="left">
            {histories.map((history) => renderTimelineItem(history))}
          </Timeline>
        </>
      )}
    </Drawer>
  );
};

export default ScheduleHistoryDrawer;
