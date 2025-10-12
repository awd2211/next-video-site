import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Table, Button, Space, Tag, Input, Select, message, Modal, Grid } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, DownloadOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useHotkeys } from 'react-hotkeys-hook'
import axios from '@/utils/axios'
import { useDebounce } from '@/hooks/useDebounce'
import { exportToCSV } from '@/utils/exportUtils'
import EmptyState from '@/components/EmptyState'

const VideoList = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const screens = Grid.useBreakpoint()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<string>()
  const [selectedRowKeys, setSelectedRowKeys] = useState<number[]>([])
  
  // Debounce search to reduce API calls
  const debouncedSearch = useDebounce(search, 500)
  
  // Hotkeys
  useHotkeys('ctrl+n', (e) => {
    e.preventDefault();
    navigate('/videos/new');
  }, { enableOnFormTags: false })
  
  useHotkeys('ctrl+f', (e) => {
    e.preventDefault();
    const searchInput = document.querySelector('input[type="search"]') as HTMLInputElement;
    searchInput?.focus();
  }, { enableOnFormTags: false })

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['admin-videos', page, debouncedSearch, status],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/videos', {
        params: { page, page_size: 20, search: debouncedSearch, status },
      })
      return response.data
    },
    placeholderData: (previousData) => previousData, // Keep previous data while loading
  })

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: t('video.confirmDelete'),
      content: t('video.deleteWarning'),
      okText: t('common.delete'),
      okType: 'danger',
      cancelText: t('common.cancel'),
      onOk: async () => {
        try {
          await axios.delete(`/api/v1/admin/videos/${id}`)
          message.success(t('message.deleteSuccess'))
          refetch()
        } catch (error: any) {
          message.error(error.response?.data?.detail || t('message.failed'))
        }
      },
    })
  }
  
  // Batch publish mutation
  const batchPublishMutation = useMutation({
    mutationFn: async (ids: number[]) => {
      await axios.put('/api/v1/admin/videos/batch/publish', { ids })
    },
    onSuccess: () => {
      message.success(t('message.success'))
      setSelectedRowKeys([])
      queryClient.invalidateQueries({ queryKey: ['admin-videos'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('message.failed'))
    },
  })
  
  // Batch archive mutation
  const batchArchiveMutation = useMutation({
    mutationFn: async (ids: number[]) => {
      await axios.put('/api/v1/admin/videos/batch/archive', { ids })
    },
    onSuccess: () => {
      message.success(t('message.success'))
      setSelectedRowKeys([])
      queryClient.invalidateQueries({ queryKey: ['admin-videos'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('message.failed'))
    },
  })
  
  // Batch delete mutation
  const batchDeleteMutation = useMutation({
    mutationFn: async (ids: number[]) => {
      await axios.delete('/api/v1/admin/videos/batch', {
        data: { ids },
      })
    },
    onSuccess: () => {
      message.success(t('message.deleteSuccess'))
      setSelectedRowKeys([])
      queryClient.invalidateQueries({ queryKey: ['admin-videos'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('message.failed'))
    },
  })
  
  // Batch operations handlers
  const handleBatchPublish = () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择视频')
      return
    }
    Modal.confirm({
      title: t('video.batchPublish'),
      content: `确定要发布选中的 ${selectedRowKeys.length} 个视频吗？`,
      onOk: () => batchPublishMutation.mutate(selectedRowKeys),
    })
  }
  
  const handleBatchArchive = () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择视频')
      return
    }
    Modal.confirm({
      title: t('video.batchArchive'),
      content: `确定要下架选中的 ${selectedRowKeys.length} 个视频吗？`,
      onOk: () => batchArchiveMutation.mutate(selectedRowKeys),
    })
  }
  
  const handleBatchDelete = () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择视频')
      return
    }
    Modal.confirm({
      title: t('video.batchDelete'),
      content: `确定要删除选中的 ${selectedRowKeys.length} 个视频吗？此操作不可恢复。`,
      okText: t('common.delete'),
      okType: 'danger',
      onOk: () => batchDeleteMutation.mutate(selectedRowKeys),
    })
  }
  
  // Export to CSV
  const handleExport = () => {
    if (!data?.items || data.items.length === 0) {
      message.warning('没有数据可导出')
      return
    }
    
    const exportData = data.items.map((item: any) => ({
      ID: item.id,
      标题: item.title,
      类型: item.video_type,
      状态: item.status,
      播放量: item.view_count,
      评分: item.average_rating?.toFixed(1) || '0.0',
      创建时间: item.created_at,
    }))
    
    exportToCSV(exportData, 'videos')
    message.success(t('message.success'))
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

  const rowSelection = {
    selectedRowKeys,
    onChange: (keys: React.Key[]) => setSelectedRowKeys(keys as number[]),
  }

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Space>
          <Input.Search
            placeholder={t('common.search') + ' videos...'}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onSearch={setSearch}
            loading={isLoading && !!debouncedSearch}
            allowClear
            style={{ width: 300 }}
          />
          <Select
            placeholder={t('video.status')}
            style={{ width: 150 }}
            allowClear
            onChange={setStatus}
            options={[
              { label: t('video.draft'), value: 'draft' },
              { label: t('video.published'), value: 'published' },
              { label: t('video.archived'), value: 'archived' },
            ]}
          />
        </Space>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate('/videos/new')}
        >
          {t('common.add')} Video
        </Button>
      </div>

      {/* Batch operations */}
      {selectedRowKeys.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <Space>
            <Button
              type="primary"
              onClick={handleBatchPublish}
            >
              {t('video.batchPublish')} ({selectedRowKeys.length})
            </Button>
            <Button
              onClick={handleBatchArchive}
            >
              {t('video.batchArchive')} ({selectedRowKeys.length})
            </Button>
            <Button
              danger
              onClick={handleBatchDelete}
            >
              {t('video.batchDelete')} ({selectedRowKeys.length})
            </Button>
            <Button
              icon={<DownloadOutlined />}
              onClick={handleExport}
            >
              {t('video.exportExcel')}
            </Button>
          </Space>
        </div>
      )}

      <Table
        rowSelection={rowSelection}
        columns={columns}
        dataSource={data?.items}
        loading={isLoading}
        rowKey="id"
        pagination={{
          current: page,
          pageSize: screens.xs ? 10 : 20,
          total: data?.total,
          onChange: setPage,
          showTotal: (total) => `${t('common.total')} ${total} ${t('common.items')}`,
          simple: screens.xs,
        }}
        scroll={{ x: screens.xs ? 800 : 1200 }}
        sticky
        locale={{
          emptyText: search || status ? (
            <EmptyState
              type="no-search-results"
              title={t('common.noData')}
              description="尝试调整搜索条件或筛选条件"
              onRefresh={() => {
                setSearch('')
                setStatus(undefined)
              }}
            />
          ) : (
            <EmptyState
              title="还没有视频"
              description="创建第一个视频，开始您的内容之旅"
              actionText="创建视频"
              onAction={() => navigate('/videos/new')}
            />
          ),
        }}
      />
    </div>
  )
}

export default VideoList
