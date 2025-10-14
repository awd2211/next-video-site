/**
 * 视频专辑/系列管理 - 列表页
 */
import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Card,
  Table,
  Button,
  Space,
  Popconfirm,
  message,
  Input,
  Select,
  Image,
  Statistic,
  Row,
  Col,
  Modal,
  Dropdown,
  Menu,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  ReloadOutlined,
  SearchOutlined,
  DownOutlined,
  CheckOutlined,
  StopOutlined,
  StarOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import seriesService, { SeriesListItem, SeriesType, SeriesStatus } from '@/services/seriesService'
import { formatAWSDate, formatAWSNumber, AWSTag } from '@/utils/awsStyleHelpers'
import { useTranslation } from 'react-i18next'
import { SeriesPreviewButton } from './SeriesPreview'
import { useTableSort } from '@/hooks/useTableSort'
import '@/styles/page-layout.css'

const SeriesList: React.FC = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [dataSource, setDataSource] = useState<SeriesListItem[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [searchText, setSearchText] = useState('')
  const [statusFilter, setStatusFilter] = useState<SeriesStatus | undefined>()
  const [typeFilter, setTypeFilter] = useState<SeriesType | undefined>()
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [stats, setStats] = useState<any>(null)

  // Table sorting
  const { handleTableChange, getSortParams } = useTableSort({
    defaultSortBy: 'created_at',
    defaultSortOrder: 'desc'
  })

  // 加载数据
  const loadData = async () => {
    setLoading(true)
    try {
      const response = await seriesService.getList({
        page,
        page_size: pageSize,
        status: statusFilter,
        type: typeFilter,
        search: searchText || undefined,
        ...getSortParams(),
      })
      setDataSource(response.items)
      setTotal(response.total)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '加载失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [page, pageSize, statusFilter, typeFilter])

  // 删除专辑
  const handleDelete = async (id: number) => {
    try {
      await seriesService.delete(id)
      message.success('删除成功')
      loadData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败')
    }
  }

  // 类型标签
  const getTypeTag = (type: SeriesType) => {
    const typeMap: Record<SeriesType, { type: 'info' | 'success' | 'default'; text: string }> = {
      series: { type: 'info', text: '系列剧' },
      collection: { type: 'success', text: '合集' },
      franchise: { type: 'default', text: '系列作品' },
    }
    const config = typeMap[type]
    return <AWSTag type={config.type}>{config.text}</AWSTag>
  }

  // 状态标签
  const getStatusTag = (status: SeriesStatus) => {
    const statusMap: Record<SeriesStatus, { type: 'default' | 'success' | 'warning'; text: string }> = {
      draft: { type: 'default', text: '草稿' },
      published: { type: 'success', text: '已发布' },
      archived: { type: 'warning', text: '已归档' },
    }
    const config = statusMap[status]
    return <AWSTag type={config.type}>{config.text}</AWSTag>
  }

  const columns: ColumnsType<SeriesListItem> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
      sorter: true,
    },
    {
      title: '封面',
      dataIndex: 'cover_image',
      key: 'cover_image',
      width: 100,
      render: (url: string) =>
        url ? (
          <Image src={url} width={60} height={80} style={{ objectFit: 'cover' }} />
        ) : (
          <div
            style={{
              width: 60,
              height: 80,
              background: '#f0f0f0',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            无封面
          </div>
        ),
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      sorter: true,
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 120,
      render: (type: SeriesType) => getTypeTag(type),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: SeriesStatus) => getStatusTag(status),
    },
    {
      title: '集数',
      dataIndex: 'total_episodes',
      key: 'total_episodes',
      width: 80,
      sorter: true,
      render: (num: number) => formatAWSNumber(num),
    },
    {
      title: '播放量',
      dataIndex: 'total_views',
      key: 'total_views',
      width: 100,
      sorter: true,
      render: (views: number) => formatAWSNumber(views.toLocaleString()),
    },
    {
      title: '收藏数',
      dataIndex: 'total_favorites',
      key: 'total_favorites',
      width: 100,
      sorter: true,
      render: (favs: number) => formatAWSNumber(favs.toLocaleString()),
    },
    {
      title: '推荐',
      dataIndex: 'is_featured',
      key: 'is_featured',
      width: 80,
      render: (featured: boolean) => (featured ? <AWSTag type="error">推荐</AWSTag> : '-'),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      sorter: true,
      render: (time: string) => formatAWSDate(time, 'YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/series/${record.id}`)}
          >
            查看
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => navigate(`/series/${record.id}/edit`)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除此专辑吗？"
            description="删除后将移除与视频的关联，但不会删除视频本身"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger size="small" icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div className="page-container">
      {/* Page Header */}
      <div className="page-header">
        <div className="page-header-content">
          <div className="page-header-left">
            <Input.Search
              placeholder="搜索专辑标题"
              allowClear
              enterButton={<SearchOutlined />}
              onSearch={(value) => {
                setSearchText(value)
                setPage(1)
                loadData()
              }}
              style={{ width: 250 }}
            />
            <Select
              placeholder="状态筛选"
              allowClear
              style={{ width: 120 }}
              value={statusFilter}
              onChange={(value) => {
                setStatusFilter(value)
                setPage(1)
              }}
            >
              <Select.Option value="draft">草稿</Select.Option>
              <Select.Option value="published">已发布</Select.Option>
              <Select.Option value="archived">已归档</Select.Option>
            </Select>
            <Select
              placeholder="类型筛选"
              allowClear
              style={{ width: 120 }}
              value={typeFilter}
              onChange={(value) => {
                setTypeFilter(value)
                setPage(1)
              }}
            >
              <Select.Option value="series">系列剧</Select.Option>
              <Select.Option value="collection">合集</Select.Option>
              <Select.Option value="franchise">系列作品</Select.Option>
            </Select>
          </div>
          <div className="page-header-right">
            <Button icon={<ReloadOutlined />} onClick={loadData}>
              刷新
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => navigate('/series/new')}
            >
              创建专辑
            </Button>
          </div>
        </div>
      </div>

      {/* Page Content */}
      <div className="page-content">
        <div className="table-container">
          <Table
            columns={columns}
            dataSource={dataSource}
            rowKey="id"
            loading={loading}
            onChange={(pagination, filters, sorter) => handleTableChange(sorter)}
            scroll={{ x: 1400 }}
            pagination={{
              current: page,
              pageSize: pageSize,
              total: total,
              onShowSizeChange: (current, size) => {
                setPageSize(size)
                setPage(1)
              },
              showSizeChanger: true,
              pageSizeOptions: ['10', '20', '50', '100'],
              showQuickJumper: true,
              showTotal: (total) => t('common.total', { count: total }),
              onChange: (newPage) => setPage(newPage),
            }}
          />
        </div>
      </div>
    </div>
  )
}

export default SeriesList
