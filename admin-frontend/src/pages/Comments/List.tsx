import { useState } from 'react'
import {
  Table,
  Button,
  Space,
  Input,
  message,
  Modal,
  Tag,
  Card,
  Select,
  Tooltip,
  Grid,
} from 'antd'
import {
  CheckOutlined,
  CloseOutlined,
  DeleteOutlined,
  SearchOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import axios from '@/utils/axios'
import dayjs from 'dayjs'
import { useTheme } from '@/contexts/ThemeContext'
import { getTagStyle, getTextColor } from '@/utils/awsColorHelpers'

const { Search } = Input
const { Option } = Select

const CommentsList = () => {
  const { t } = useTranslation()
  const screens = Grid.useBreakpoint()
  const { theme } = useTheme()
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('all')
  const [selectedRowKeys, setSelectedRowKeys] = useState<number[]>([])
  const queryClient = useQueryClient()  // Fetch comments
  const { data, isLoading } = useQuery({
    queryKey: ['admin-comments', page, pageSize, search, status],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        search,
      })
      if (status !== 'all') {
        params.append('status', status)
      }
      const response = await axios.get(`/api/v1/admin/comments?${params}`)
      return response.data
    },
    placeholderData: (previousData) => previousData, // Keep previous data while loading
  })

  // Approve comment mutation
  const approveMutation = useMutation({
    mutationFn: async (commentId: number) => {
      await axios.put(
        `/api/v1/admin/comments/${commentId}/approve`,
        {}
      )
    },
    onSuccess: () => {
      message.success('评论已通过')
      queryClient.invalidateQueries({ queryKey: ['admin-comments'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '操作失败')
    },
  })

  // Reject comment mutation
  const rejectMutation = useMutation({
    mutationFn: async (commentId: number) => {
      await axios.put(
        `/api/v1/admin/comments/${commentId}/reject`,
        {}
      )
    },
    onSuccess: () => {
      message.success('评论已拒绝')
      queryClient.invalidateQueries({ queryKey: ['admin-comments'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '操作失败')
    },
  })

  // Delete comment mutation
  const deleteMutation = useMutation({
    mutationFn: async (commentId: number) => {
      await axios.delete(`/api/v1/admin/comments/${commentId}`)
    },
    onSuccess: () => {
      message.success('评论已删除')
      queryClient.invalidateQueries({ queryKey: ['admin-comments'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '删除失败')
    },
  })

  // Batch approve mutation
  const batchApproveMutation = useMutation({
    mutationFn: async (commentIds: number[]) => {
      await axios.put(
        '/api/v1/admin/comments/batch/approve',
        { comment_ids: commentIds }
      )
    },
    onSuccess: () => {
      message.success('批量通过成功')
      setSelectedRowKeys([])
      queryClient.invalidateQueries({ queryKey: ['admin-comments'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '操作失败')
    },
  })

  // Batch reject mutation
  const batchRejectMutation = useMutation({
    mutationFn: async (commentIds: number[]) => {
      await axios.put(
        '/api/v1/admin/comments/batch/reject',
        { comment_ids: commentIds }
      )
    },
    onSuccess: () => {
      message.success('批量拒绝成功')
      setSelectedRowKeys([])
      queryClient.invalidateQueries({ queryKey: ['admin-comments'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '操作失败')
    },
  })

  // Batch delete mutation
  const batchDeleteMutation = useMutation({
    mutationFn: async (commentIds: number[]) => {
      await axios.delete('/api/v1/admin/comments/batch', {
        data: { comment_ids: commentIds },
      })
    },
    onSuccess: () => {
      message.success('批量删除成功')
      setSelectedRowKeys([])
      queryClient.invalidateQueries({ queryKey: ['admin-comments'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '删除失败')
    },
  })

  const handleApprove = (commentId: number) => {
    Modal.confirm({
      title: '确认通过',
      icon: <ExclamationCircleOutlined />,
      content: '确定要通过这条评论吗？',
      onOk: () => approveMutation.mutate(commentId),
    })
  }

  const handleReject = (commentId: number) => {
    Modal.confirm({
      title: '确认拒绝',
      icon: <ExclamationCircleOutlined />,
      content: '确定要拒绝这条评论吗？',
      onOk: () => rejectMutation.mutate(commentId),
    })
  }

  const handleDelete = (commentId: number) => {
    Modal.confirm({
      title: '确认删除',
      icon: <ExclamationCircleOutlined />,
      content: '确定要删除这条评论吗？此操作不可恢复。',
      okText: '删除',
      okType: 'danger',
      onOk: () => deleteMutation.mutate(commentId),
    })
  }

  const handleBatchApprove = () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择评论')
      return
    }
    Modal.confirm({
      title: '批量通过',
      icon: <ExclamationCircleOutlined />,
      content: `确定要通过选中的 ${selectedRowKeys.length} 条评论吗？`,
      onOk: () => batchApproveMutation.mutate(selectedRowKeys),
    })
  }

  const handleBatchReject = () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择评论')
      return
    }
    Modal.confirm({
      title: '批量拒绝',
      icon: <ExclamationCircleOutlined />,
      content: `确定要拒绝选中的 ${selectedRowKeys.length} 条评论吗？`,
      onOk: () => batchRejectMutation.mutate(selectedRowKeys),
    })
  }

  const handleBatchDelete = () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择评论')
      return
    }
    Modal.confirm({
      title: '批量删除',
      icon: <ExclamationCircleOutlined />,
      content: `确定要删除选中的 ${selectedRowKeys.length} 条评论吗？此操作不可恢复。`,
      okText: '删除',
      okType: 'danger',
      onOk: () => batchDeleteMutation.mutate(selectedRowKeys),
    })
  }

  const columns = [
    {
      title: '用户',
      dataIndex: ['user', 'username'],
      key: 'user',
      width: 120,
      render: (username: string, record: any) => (
        <div>
          <div>{username || record.user?.email}</div>
          {record.user?.full_name && (
            <div style={{ fontSize: 12, color: '#999' }}>{record.user.full_name}</div>
          )}
        </div>
      ),
    },
    {
      title: '视频',
      dataIndex: ['video', 'title'],
      key: 'video',
      width: 200,
      ellipsis: true,
      render: (title: string) => (
        <Tooltip title={title}>
          <span>{title}</span>
        </Tooltip>
      ),
    },
    {
      title: '评论内容',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
      render: (content: string) => (
        <Tooltip title={content}>
          <span>{content}</span>
        </Tooltip>
      ),
    },
    {
      title: '评分',
      dataIndex: 'rating',
      key: 'rating',
      width: 80,
      render: (rating: number) => (
        <span style={{
          fontFamily: 'Monaco, Menlo, Consolas, monospace',
          color: getTextColor('primary', theme)
        }}>
          {rating ? `${rating.toFixed(1)} ★` : '-'}
        </span>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const statusVariantMap: { [key: string]: { variant: 'warning' | 'success' | 'error' | 'neutral'; text: string } } = {
          PENDING: {
            variant: 'warning',
            text: '待审核'
          },
          APPROVED: {
            variant: 'success',
            text: '已通过'
          },
          REJECTED: {
            variant: 'error',
            text: '已拒绝'
          },
        }
        const config = statusVariantMap[status] || {
          variant: 'neutral' as const,
          text: status
        }
        return (
          <Tag style={getTagStyle(config.variant, theme)}>
            {config.text}
          </Tag>
        )
      },
    },
    {
      title: '点赞数',
      dataIndex: 'like_count',
      key: 'like_count',
      width: 80,
      sorter: (a: any, b: any) => a.like_count - b.like_count,
      render: (count: number) => (
        <span style={{
          fontFamily: 'Monaco, Menlo, Consolas, monospace',
          color: getTextColor('primary', theme)
        }}>
          {count || 0}
        </span>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => (
        <span style={{
          fontFamily: 'Monaco, Menlo, Consolas, monospace',
          color: getTextColor('primary', theme),
          fontSize: '13px'
        }}>
          {dayjs(date).format('YYYY-MM-DD HH:mm:ss')}
        </span>
      ),
      sorter: (a: any, b: any) =>
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right' as const,
      render: (_: any, record: any) => (
        <Space size="small">
          {record.status === 'PENDING' && (
            <>
              <Button
                type="primary"
                size="small"
                icon={<CheckOutlined />}
                onClick={() => handleApprove(record.id)}
              >
                {t('comment.approve')}
              </Button>
              <Button
                size="small"
                icon={<CloseOutlined />}
                onClick={() => handleReject(record.id)}
              >
                {t('comment.reject')}
              </Button>
            </>
          )}
          {record.status === 'APPROVED' && (
            <Button
              size="small"
              icon={<CloseOutlined />}
              onClick={() => handleReject(record.id)}
            >
              {t('comment.reject')}
            </Button>
          )}
          {record.status === 'REJECTED' && (
            <Button
              type="primary"
              size="small"
              icon={<CheckOutlined />}
              onClick={() => handleApprove(record.id)}
            >
              {t('comment.approve')}
            </Button>
          )}
          <Button
            danger
            size="small"
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
    onChange: (keys: any) => setSelectedRowKeys(keys),
  }

  return (
    <div>
      <Card>
        <Space style={{ marginBottom: 16 }} wrap>
          <Search
            placeholder="搜索评论内容"
            allowClear
            onSearch={setSearch}
            style={{ width: 300 }}
            prefix={<SearchOutlined />}
          />
          <Select value={status} onChange={setStatus} style={{ width: 120 }}>
            <Option value="all">全部状态</Option>
            <Option value="pending">待审核</Option>
            <Option value="approved">已通过</Option>
            <Option value="rejected">已拒绝</Option>
          </Select>
          {selectedRowKeys.length > 0 && (
            <>
              <Button
                type="primary"
                icon={<CheckOutlined />}
                onClick={handleBatchApprove}
                loading={batchApproveMutation.isPending}
              >
                批量通过 ({selectedRowKeys.length})
              </Button>
              <Button
                icon={<CloseOutlined />}
                onClick={handleBatchReject}
                loading={batchRejectMutation.isPending}
              >
                批量拒绝 ({selectedRowKeys.length})
              </Button>
              <Button
                danger
                icon={<DeleteOutlined />}
                onClick={handleBatchDelete}
                loading={batchDeleteMutation.isPending}
              >
                批量删除 ({selectedRowKeys.length})
              </Button>
            </>
          )}
        </Space>

        <Table
          rowSelection={rowSelection}
          columns={columns}
          dataSource={data?.items || []}
          rowKey="id"
          loading={isLoading}
          scroll={{ x: screens.xs ? 800 : 1400 }}
          sticky
          pagination={{
            current: page,
            pageSize: screens.xs ? 10 : pageSize,
            total: data?.total || 0,
            simple: screens.xs,
            showSizeChanger: false,
            showQuickJumper: true,
            showTotal: (total) => t('common.total', { count: total }),
            onChange: (newPage) => setPage(newPage),
          }}
        />
      </Card>
    </div>
  )
}

export default CommentsList
