import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Table, Button, Space, Tag, Input, Select, message, Modal, Grid } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, DownloadOutlined, UploadOutlined, LineChartOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useHotkeys } from 'react-hotkeys-hook'
import axios from '@/utils/axios'
import { useDebounce } from '@/hooks/useDebounce'
import { useTableSort } from '@/hooks/useTableSort'
import { exportToCSV } from '@/utils/exportUtils'
import EmptyState from '@/components/EmptyState'
import VideoPreviewPopover from '@/components/VideoPreviewPopover'
import BatchUploader from '@/components/BatchUploader'
import { useTheme } from '@/contexts/ThemeContext'
import { getTagStyle, getTextColor } from '@/utils/awsColorHelpers'
import '@/styles/page-layout.css'

const VideoList = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const screens = Grid.useBreakpoint()
  const { theme } = useTheme()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<string>()
  const [selectedRowKeys, setSelectedRowKeys] = useState<number[]>([])
  const [batchUploadVisible, setBatchUploadVisible] = useState(false)

  // Debounce search to reduce API calls
  const debouncedSearch = useDebounce(search, 500)

  // Table sorting
  const { handleTableChange, getSortParams } = useTableSort({
    defaultSortBy: 'created_at',
    defaultSortOrder: 'desc'
  })

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
    queryKey: ['admin-videos', page, pageSize, debouncedSearch, status, ...Object.values(getSortParams())],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/videos', {
        params: {
          page,
          page_size: pageSize,
          search: debouncedSearch,
          status,
          ...getSortParams(),
        },
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
      message.warning(t('message.pleaseSelect'))
      return
    }
    Modal.confirm({
      title: t('video.batchPublish'),
      content: `${t('common.confirm')} ${selectedRowKeys.length} ${t('menu.videos')}?`,
      okText: t('common.confirm'),
      cancelText: t('common.cancel'),
      onOk: () => batchPublishMutation.mutate(selectedRowKeys),
    })
  }
  
  const handleBatchArchive = () => {
    if (selectedRowKeys.length === 0) {
      message.warning(t('message.pleaseSelect'))
      return
    }
    Modal.confirm({
      title: t('video.batchArchive'),
      content: `${t('common.confirm')} ${selectedRowKeys.length} ${t('menu.videos')}?`,
      okText: t('common.confirm'),
      cancelText: t('common.cancel'),
      onOk: () => batchArchiveMutation.mutate(selectedRowKeys),
    })
  }
  
  const handleBatchDelete = () => {
    if (selectedRowKeys.length === 0) {
      message.warning(t('message.pleaseSelect'))
      return
    }
    Modal.confirm({
      title: t('video.batchDelete'),
      content: `${t('common.confirm')} ${selectedRowKeys.length} ${t('menu.videos')}? ${t('message.cannotUndo')}`,
      okText: t('common.delete'),
      okType: 'danger',
      cancelText: t('common.cancel'),
      onOk: () => batchDeleteMutation.mutate(selectedRowKeys),
    })
  }
  
  // Export to CSV
  const handleExport = () => {
    if (!data?.items || data.items.length === 0) {
      message.warning(t('message.noDataToExport'))
      return
    }
    
    const exportData = data.items.map((item: any) => ({
      ID: item.id,
      [t('video.title')]: item.title,
      [t('video.type')]: item.video_type,
      [t('video.status')]: item.status,
      [t('video.views')]: item.view_count,
      [t('table.createdAt')]: item.created_at,
    }))
    
    exportToCSV(exportData, 'videos')
    message.success(t('message.exportSuccess'))
  }

  const columns = [
    {
      title: t('table.id'),
      dataIndex: 'id',
      key: 'id',
      width: 80,
      sorter: true,
    },
    {
      title: t('video.title'),
      dataIndex: 'title',
      key: 'title',
      sorter: true,
      render: (title: string, record: any) => (
        <VideoPreviewPopover video={record} hoverDelay={300}>
          <div className="video-preview-trigger" style={{ cursor: 'pointer', padding: '4px 0' }}>
            {title}
          </div>
        </VideoPreviewPopover>
      ),
    },
    {
      title: t('video.type'),
      dataIndex: 'video_type',
      key: 'video_type',
      render: (type: string) => (
        <Tag style={getTagStyle('primary', theme)}>
          {type}
        </Tag>
      ),
    },
    {
      title: t('video.status'),
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const getStatusVariant = (status: string) => {
          switch (status.toUpperCase()) {
            case 'PUBLISHED':
              return 'success'
            case 'DRAFT':
              return 'info'
            case 'ARCHIVED':
              return 'warning'
            default:
              return 'neutral'
          }
        }
        return (
          <Tag style={getTagStyle(getStatusVariant(status), theme)}>{status}</Tag>
        )
      },
    },
    {
      title: t('video.views'),
      dataIndex: 'view_count',
      key: 'view_count',
      sorter: true,
    },
    {
      title: 'Rating',
      dataIndex: 'average_rating',
      key: 'average_rating',
      sorter: true,
      render: (rating: number) => (
        <span style={{
          fontFamily: 'Monaco, Menlo, Consolas, monospace',
          color: getTextColor('primary', theme)
        }}>
          {rating?.toFixed(1) || '0.0'}
        </span>
      ),
    },
    {
      title: t('table.actions'),
      key: 'actions',
      render: (_: any, record: any) => (
        <Space>
          <Button
            type="link"
            icon={<LineChartOutlined />}
            onClick={() => navigate(`/videos/${record.id}/analytics`)}
          >
            分析
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => navigate(`/videos/${record.id}/edit`)}
          >
            {t('common.edit')}
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            {t('common.delete')}
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
    <div className="page-container">
      {/* Page Header */}
      <div className="page-header">
        <div className="page-header-content">
          <div className="page-header-left">
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
                { label: t('video.draft'), value: 'DRAFT' },
                { label: t('video.published'), value: 'PUBLISHED' },
                { label: t('video.archived'), value: 'ARCHIVED' },
              ]}
            />
          </div>
          <div className="page-header-right">
            <Button
              icon={<UploadOutlined />}
              onClick={() => setBatchUploadVisible(true)}
            >
              {t('video.batchUpload') || '批量上传'}
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => navigate('/videos/new')}
            >
              {t('common.add')} Video
            </Button>
          </div>
        </div>
      </div>

      {/* Batch operations */}
      {selectedRowKeys.length > 0 && (
        <div className="batch-operations">
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

      {/* Page Content */}
      <div className="page-content">
        <div className="table-container">
          <Table
        rowSelection={rowSelection}
        columns={columns}
        dataSource={data?.items}
        loading={isLoading}
        rowKey="id"
        onChange={(pagination, filters, sorter) => handleTableChange(sorter)}
        pagination={{
          current: page,
          pageSize: pageSize,
          total: data?.total,
          onChange: setPage,
          onShowSizeChange: (current, size) => {
            setPageSize(size)
            setPage(1) // Reset to first page when changing page size
          },
          showSizeChanger: true,
          pageSizeOptions: ['10', '20', '50', '100'],
          showTotal: (total) => t('common.total', { count: total }),
          simple: screens.xs,
        }}
        scroll={{ x: screens.xs ? 800 : 1200 }}
        sticky
        locale={{
          emptyText: search || status ? (
            <EmptyState
              type="no-search-results"
              title={t('common.noData')}
              description={t('message.adjustSearchFilter')}
              onRefresh={() => {
                setSearch('')
                setStatus(undefined)
              }}
            />
          ) : (
            <EmptyState
              title={t('message.noVideosYet')}
              description={t('message.createFirst', { type: t('menu.videos').toLowerCase() })}
              actionText={t('common.create') + ' ' + t('menu.videos')}
              onAction={() => navigate('/videos/new')}
            />
          ),
        }}
      />
        </div>
      </div>

      {/* Batch Upload Modal */}
      <Modal
        title={t('video.batchUpload') || '批量上传视频'}
        open={batchUploadVisible}
        onCancel={() => setBatchUploadVisible(false)}
        footer={null}
        width={900}
        destroyOnClose
      >
        <BatchUploader
          onAllComplete={(urls) => {
            message.success(`成功上传 ${urls.length} 个视频`)
            setBatchUploadVisible(false)
            refetch()
          }}
          maxSize={2048}
          maxCount={10}
        />
      </Modal>
    </div>
  )
}

export default VideoList
