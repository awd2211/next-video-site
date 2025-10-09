import { useQuery } from '@tanstack/react-query'
import { Card, Row, Col, Statistic } from 'antd'
import { UserOutlined, VideoCameraOutlined, CommentOutlined, EyeOutlined } from '@ant-design/icons'
import axios from 'axios'

const Dashboard = () => {
  const { data: stats } = useQuery({
    queryKey: ['overview-stats'],
    queryFn: async () => {
      const token = localStorage.getItem('admin_access_token')
      const response = await axios.get('/api/v1/admin/stats/overview', {
        headers: { Authorization: `Bearer ${token}` },
      })
      return response.data
    },
  })

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>Dashboard</h1>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Users"
              value={stats?.total_users || 0}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Videos"
              value={stats?.total_videos || 0}
              prefix={<VideoCameraOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Comments"
              value={stats?.total_comments || 0}
              prefix={<CommentOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Views"
              value={stats?.total_views || 0}
              prefix={<EyeOutlined />}
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard
