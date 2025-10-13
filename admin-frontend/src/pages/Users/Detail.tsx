import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Card,
  Descriptions,
  Tag,
  Space,
  Button,
  Typography,
  Spin,
  Alert,
  Row,
  Col,
  Statistic,
  Table,
  Tabs,
  Avatar,
  Modal,
  message,
  Timeline,
} from 'antd';
import {
  UserOutlined,
  MailOutlined,
  CalendarOutlined,
  CrownOutlined,
  LockOutlined,
  UnlockOutlined,
  ArrowLeftOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  EyeOutlined,
  StarOutlined,
  CommentOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import axios from '@/utils/axios';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

interface UserDetail {
  user: {
    id: number;
    username: string;
    email: string;
    full_name?: string;
    avatar_url?: string;
    is_active: boolean;
    is_verified: boolean;
    is_vip: boolean;
    vip_expire_at?: string;
    created_at: string;
    last_login?: string;
  };
  statistics: {
    total_watch_count: number;
    total_favorites: number;
    total_comments: number;
    total_ratings: number;
    recent_watches_7d: number;
    recent_comments_7d: number;
  };
  recent_activity: {
    watch_history: Array<{
      id: number;
      video?: {
        id: number;
        title: string;
        cover_url?: string;
      };
      progress: number;
      duration: number;
      completed: boolean;
      updated_at: string;
    }>;
    comments: Array<{
      id: number;
      video?: {
        id: number;
        title: string;
      };
      content: string;
      status: string;
      created_at: string;
    }>;
    favorites: Array<{
      id: number;
      video?: {
        id: number;
        title: string;
        cover_url?: string;
      };
      created_at: string;
    }>;
  };
}

const UserDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery<UserDetail>({
    queryKey: ['user-detail', id],
    queryFn: async () => {
      const response = await axios.get(`/api/v1/admin/users/${id}/detail`);
      return response.data;
    },
    enabled: !!id,
  });

  const banMutation = useMutation({
    mutationFn: async () => {
      await axios.put(`/api/v1/admin/users/${id}/ban`, {});
    },
    onSuccess: () => {
      message.success(data?.user.is_active ? 'User banned successfully' : 'User unbanned successfully');
      queryClient.invalidateQueries({ queryKey: ['user-detail', id] });
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Operation failed');
    },
  });

  const handleBanToggle = () => {
    const action = data?.user.is_active ? 'ban' : 'unban';
    Modal.confirm({
      title: `Confirm ${action}`,
      content: `Are you sure you want to ${action} this user: ${data?.user.username}?`,
      okText: 'Confirm',
      cancelText: 'Cancel',
      okButtonProps: { danger: data?.user.is_active },
      onOk: () => banMutation.mutate(),
    });
  };

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="Loading user details..." />
      </div>
    );
  }

  if (error || !data) {
    return (
      <Alert
        message="Failed to load user details"
        description={error instanceof Error ? error.message : 'User not found'}
        type="error"
        showIcon
      />
    );
  }

  const user = data.user;
  const stats = data.statistics;
  const activity = data.recent_activity;

  const watchHistoryColumns = [
    {
      title: 'Video',
      dataIndex: ['video', 'title'],
      key: 'title',
      ellipsis: true,
      render: (title: string, record: any) => (
        <Space>
          {record.video?.cover_url && (
            <Avatar src={record.video.cover_url} shape="square" size="small" />
          )}
          <span>{title || 'Unknown Video'}</span>
        </Space>
      ),
    },
    {
      title: 'Progress',
      key: 'progress',
      width: 200,
      render: (_: any, record: any) => {
        const percent = record.duration > 0 ? (record.progress / record.duration) * 100 : 0;
        return (
          <Space direction="vertical" size={0}>
            <Text style={{ fontSize: 12 }}>
              {Math.floor(record.progress / 60)}:{(record.progress % 60).toString().padStart(2, '0')} /{' '}
              {Math.floor(record.duration / 60)}:{(record.duration % 60).toString().padStart(2, '0')}
            </Text>
            <div style={{ width: 150, height: 4, background: '#f0f0f0', borderRadius: 2 }}>
              <div
                style={{
                  width: `${percent}%`,
                  height: '100%',
                  background: record.completed ? '#52c41a' : '#1890ff',
                  borderRadius: 2,
                }}
              />
            </div>
          </Space>
        );
      },
    },
    {
      title: 'Status',
      dataIndex: 'completed',
      key: 'completed',
      width: 100,
      render: (completed: boolean) => (
        <Tag color={completed ? 'success' : 'processing'}>
          {completed ? 'Completed' : 'Watching'}
        </Tag>
      ),
    },
    {
      title: 'Last Watched',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 180,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
  ];

  const commentsColumns = [
    {
      title: 'Video',
      dataIndex: ['video', 'title'],
      key: 'video_title',
      ellipsis: true,
      render: (title: string) => title || 'Unknown Video',
    },
    {
      title: 'Content',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const statusConfig: Record<string, { color: string; text: string }> = {
          pending: { color: 'warning', text: 'Pending' },
          approved: { color: 'success', text: 'Approved' },
          rejected: { color: 'error', text: 'Rejected' },
        };
        const config = statusConfig[status] || { color: 'default', text: status };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
  ];

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/users')} style={{ marginBottom: 16 }}>
          Back to Users
        </Button>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <Avatar size={64} src={user.avatar_url} icon={<UserOutlined />} />
            <div>
              <Title level={2} style={{ margin: 0 }}>
                {user.username}
              </Title>
              <Space>
                <Tag color={user.is_active ? 'success' : 'error'}>
                  {user.is_active ? 'Active' : 'Banned'}
                </Tag>
                {user.is_verified && <Tag color="blue">Verified</Tag>}
                {user.is_vip && (
                  <Tag color="gold" icon={<CrownOutlined />}>
                    VIP
                  </Tag>
                )}
              </Space>
            </div>
          </Space>
          <Button
            type={user.is_active ? 'default' : 'primary'}
            danger={user.is_active}
            icon={user.is_active ? <LockOutlined /> : <UnlockOutlined />}
            onClick={handleBanToggle}
            loading={banMutation.isPending}
          >
            {user.is_active ? 'Ban User' : 'Unban User'}
          </Button>
        </div>
      </div>

      {/* Basic Info */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={16}>
          <Card title="Basic Information">
            <Descriptions column={2}>
              <Descriptions.Item label="User ID">{user.id}</Descriptions.Item>
              <Descriptions.Item label="Username">{user.username}</Descriptions.Item>
              <Descriptions.Item label="Email">
                <Space>
                  <MailOutlined />
                  {user.email}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="Full Name">{user.full_name || '-'}</Descriptions.Item>
              <Descriptions.Item label="Account Status">
                <Tag
                  icon={user.is_active ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
                  color={user.is_active ? 'success' : 'error'}
                >
                  {user.is_active ? 'Active' : 'Banned'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Email Verified">
                <Tag color={user.is_verified ? 'success' : 'default'}>
                  {user.is_verified ? 'Yes' : 'No'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="VIP Status">
                {user.is_vip ? (
                  <Space direction="vertical" size={0}>
                    <Tag color="gold" icon={<CrownOutlined />}>
                      VIP Member
                    </Tag>
                    {user.vip_expire_at && (
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        Expires: {dayjs(user.vip_expire_at).format('YYYY-MM-DD')}
                      </Text>
                    )}
                  </Space>
                ) : (
                  <Text type="secondary">Regular User</Text>
                )}
              </Descriptions.Item>
              <Descriptions.Item label="Member Since">
                <Space>
                  <CalendarOutlined />
                  {dayjs(user.created_at).format('YYYY-MM-DD HH:mm')}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="Last Login">
                {user.last_login ? (
                  <Space>
                    <ClockCircleOutlined />
                    {dayjs(user.last_login).format('YYYY-MM-DD HH:mm')}
                  </Space>
                ) : (
                  '-'
                )}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card title="Activity Statistics">
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Statistic
                  title="Total Watches"
                  value={stats.total_watch_count}
                  prefix={<EyeOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Favorites"
                  value={stats.total_favorites}
                  prefix={<StarOutlined />}
                  valueStyle={{ color: '#faad14' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Comments"
                  value={stats.total_comments}
                  prefix={<CommentOutlined />}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Ratings"
                  value={stats.total_ratings}
                  prefix={<StarOutlined />}
                  valueStyle={{ color: '#722ed1' }}
                />
              </Col>
            </Row>
            <Card
              type="inner"
              title={<Text strong>Last 7 Days</Text>}
              style={{ marginTop: 16 }}
              size="small"
            >
              <Space direction="vertical" style={{ width: '100%' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text>Watches:</Text>
                  <Text strong>{stats.recent_watches_7d}</Text>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text>Comments:</Text>
                  <Text strong>{stats.recent_comments_7d}</Text>
                </div>
              </Space>
            </Card>
          </Card>
        </Col>
      </Row>

      {/* Activity Tabs */}
      <Card>
        <Tabs defaultActiveKey="watch_history">
          <TabPane tab={`Watch History (${activity.watch_history.length})`} key="watch_history">
            <Table
              dataSource={activity.watch_history}
              columns={watchHistoryColumns}
              rowKey="id"
              pagination={{ pageSize: 10 }}
            />
          </TabPane>

          <TabPane tab={`Comments (${activity.comments.length})`} key="comments">
            <Table
              dataSource={activity.comments}
              columns={commentsColumns}
              rowKey="id"
              pagination={{ pageSize: 10 }}
            />
          </TabPane>

          <TabPane tab={`Favorites (${activity.favorites.length})`} key="favorites">
            <Row gutter={[16, 16]}>
              {activity.favorites.map((fav) => (
                <Col xs={24} sm={12} md={8} lg={6} key={fav.id}>
                  <Card
                    hoverable
                    cover={
                      fav.video?.cover_url ? (
                        <img
                          alt={fav.video.title}
                          src={fav.video.cover_url}
                          style={{ height: 160, objectFit: 'cover' }}
                        />
                      ) : (
                        <div style={{ height: 160, background: '#f0f0f0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <EyeOutlined style={{ fontSize: 32, color: '#999' }} />
                        </div>
                      )
                    }
                  >
                    <Card.Meta
                      title={<Text ellipsis>{fav.video?.title || 'Unknown'}</Text>}
                      description={
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          {dayjs(fav.created_at).format('YYYY-MM-DD')}
                        </Text>
                      }
                    />
                  </Card>
                </Col>
              ))}
              {activity.favorites.length === 0 && (
                <Col span={24}>
                  <Alert message="No favorite videos" type="info" showIcon />
                </Col>
              )}
            </Row>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default UserDetail;
