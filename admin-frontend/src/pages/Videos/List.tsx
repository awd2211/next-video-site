import { useQuery } from '@tanstack/react-query'
import { Table, Button, Space, Tag, Input, Select, message } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import axios from '@/utils/axios'

const VideoList = () => {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<string>()

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['admin-videos', page, search, status],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/videos', {
        params: { page, page_size: 20, search, status },
      })
      return response.data
    },
  })

  const handleDelete = async (id: number) => {
    try {
      await axios.delete(`/api/v1/admin/videos/${id}`)
      message.success('Video deleted successfully')
      refetch()
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Delete failed')
    }
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: 'Type',
      dataIndex: 'video_type',
      key: 'video_type',
      render: (type: string) => <Tag>{type}</Tag>,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'published' ? 'green' : 'orange'}>{status}</Tag>
      ),
    },
    {
      title: 'Views',
      dataIndex: 'view_count',
      key: 'view_count',
    },
    {
      title: 'Rating',
      dataIndex: 'average_rating',
      key: 'average_rating',
      render: (rating: number) => rating.toFixed(1),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: any) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => navigate(`/videos/${record.id}/edit`)}
          >
            Edit
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            Delete
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Space>
          <Input.Search
            placeholder="Search videos..."
            onSearch={setSearch}
            style={{ width: 300 }}
          />
          <Select
            placeholder="Status"
            style={{ width: 150 }}
            allowClear
            onChange={setStatus}
            options={[
              { label: 'Draft', value: 'draft' },
              { label: 'Published', value: 'published' },
              { label: 'Archived', value: 'archived' },
            ]}
          />
        </Space>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate('/videos/new')}
        >
          Add Video
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={data?.items}
        loading={isLoading}
        rowKey="id"
        pagination={{
          current: page,
          pageSize: 20,
          total: data?.total,
          onChange: setPage,
        }}
      />
    </div>
  )
}

export default VideoList
