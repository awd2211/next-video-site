/**
 * Season (季度) 管理组件
 * 用于管理电视剧的季度信息
 */
import React, { useState, useEffect } from 'react'
import {
  Table,
  Button,
  Space,
  message,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  Popconfirm,
  Image,
  Tag,
  InputNumber,
  DatePicker,
  Tooltip,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  ReloadOutlined,
  CheckOutlined,
  InboxOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import seasonService, {
  SeasonListItem,
  SeasonCreateRequest,
  SeasonUpdateRequest,
  SeasonStatus,
} from '@/services/seasonService'
import { formatAWSDate, formatAWSNumber, AWSTag } from '@/utils/awsStyleHelpers'
import dayjs from 'dayjs'

interface SeasonManagerProps {
  seriesId: number
  onSeasonClick?: (seasonId: number) => void
}

const SeasonManager: React.FC<SeasonManagerProps> = ({ seriesId, onSeasonClick }) => {
  const [loading, setLoading] = useState(false)
  const [dataSource, setDataSource] = useState<SeasonListItem[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])

  // 创建/编辑 Modal
  const [modalVisible, setModalVisible] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form] = Form.useForm()

  // 加载季度列表
  const loadData = async () => {
    setLoading(true)
    try {
      const response = await seasonService.getListBySeries(seriesId, {
        page,
        page_size: pageSize,
        sort_by: 'season_number',
        sort_order: 'asc',
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
  }, [seriesId, page, pageSize])

  // 打开创建/编辑 Modal
  const handleOpenModal = async (seasonId?: number) => {
    if (seasonId) {
      setEditingId(seasonId)
      setLoading(true)
      try {
        const data = await seasonService.getDetail(seasonId)
        form.setFieldsValue({
          season_number: data.season_number,
          title: data.title,
          description: data.description,
          status: data.status,
          vip_required: data.vip_required,
          poster_url: data.poster_url,
          backdrop_url: data.backdrop_url,
          trailer_url: data.trailer_url,
          release_date: data.release_date ? dayjs(data.release_date) : null,
          is_featured: data.is_featured,
          sort_order: data.sort_order,
        })
      } catch (error: any) {
        message.error(error.response?.data?.detail || '加载失败')
        return
      } finally {
        setLoading(false)
      }
    } else {
      setEditingId(null)
      // 自动填充下一个季号
      const maxSeasonNumber = dataSource.length > 0
        ? Math.max(...dataSource.map(s => s.season_number))
        : 0
      form.setFieldsValue({
        season_number: maxSeasonNumber + 1,
        status: 'draft',
        vip_required: false,
        is_featured: false,
        sort_order: 0,
      })
    }
    setModalVisible(true)
  }

  // 保存季度
  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      const data = {
        ...values,
        release_date: values.release_date ? values.release_date.toISOString() : undefined,
      }

      if (editingId) {
        await seasonService.update(editingId, data as SeasonUpdateRequest)
        message.success('更新成功')
      } else {
        await seasonService.create(seriesId, data as SeasonCreateRequest)
        message.success('创建成功')
      }

      setModalVisible(false)
      form.resetFields()
      loadData()
    } catch (error: any) {
      if (error.errorFields) {
        // 表单验证错误
        return
      }
      message.error(error.response?.data?.detail || '保存失败')
    }
  }

  // 删除季度
  const handleDelete = async (id: number) => {
    try {
      await seasonService.delete(id)
      message.success('删除成功')
      loadData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败')
    }
  }

  // 批量发布
  const handleBatchPublish = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请选择要发布的季度')
      return
    }

    try {
      await seasonService.batchPublish(selectedRowKeys as number[])
      message.success(`成功发布 ${selectedRowKeys.length} 个季度`)
      setSelectedRowKeys([])
      loadData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '批量发布失败')
    }
  }

  // 批量归档
  const handleBatchArchive = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请选择要归档的季度')
      return
    }

    try {
      await seasonService.batchArchive(selectedRowKeys as number[])
      message.success(`成功归档 ${selectedRowKeys.length} 个季度`)
      setSelectedRowKeys([])
      loadData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '批量归档失败')
    }
  }

  // 批量删除
  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请选择要删除的季度')
      return
    }

    try {
      await seasonService.batchDelete(selectedRowKeys as number[])
      message.success(`成功删除 ${selectedRowKeys.length} 个季度`)
      setSelectedRowKeys([])
      loadData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '批量删除失败')
    }
  }

  // 状态标签
  const getStatusTag = (status: SeasonStatus) => {
    const statusMap: Record<SeasonStatus, { type: 'default' | 'success' | 'warning'; text: string }> = {
      draft: { type: 'default', text: '草稿' },
      published: { type: 'success', text: '已发布' },
      archived: { type: 'warning', text: '已归档' },
    }
    const config = statusMap[status]
    return <AWSTag type={config.type}>{config.text}</AWSTag>
  }

  const columns: ColumnsType<SeasonListItem> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '季号',
      dataIndex: 'season_number',
      key: 'season_number',
      width: 80,
      render: (num: number) => <Tag color="blue">第 {num} 季</Tag>,
    },
    {
      title: '封面',
      dataIndex: 'poster_url',
      key: 'poster_url',
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
              fontSize: 12,
              color: '#999',
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
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: SeasonStatus) => getStatusTag(status),
    },
    {
      title: 'VIP',
      dataIndex: 'vip_required',
      key: 'vip_required',
      width: 80,
      render: (vip: boolean) => (vip ? <Tag color="gold">VIP</Tag> : <Tag>免费</Tag>),
    },
    {
      title: '集数',
      dataIndex: 'total_episodes',
      key: 'total_episodes',
      width: 80,
      render: (num: number) => formatAWSNumber(num),
    },
    {
      title: '播放量',
      dataIndex: 'view_count',
      key: 'view_count',
      width: 100,
      render: (views: number) => formatAWSNumber(views.toLocaleString()),
    },
    {
      title: '评分',
      dataIndex: 'average_rating',
      key: 'average_rating',
      width: 80,
      render: (rating: number) => rating ? rating.toFixed(1) : '-',
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
      width: 160,
      render: (time: string) => formatAWSDate(time, 'YYYY-MM-DD HH:mm'),
    },
    {
      title: '操作',
      key: 'action',
      width: 220,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看剧集">
            <Button
              type="link"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => onSeasonClick?.(record.id)}
            >
              剧集
            </Button>
          </Tooltip>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleOpenModal(record.id)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除此季度吗？"
            description="删除后将级联删除该季下的所有剧集"
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

  const rowSelection = {
    selectedRowKeys,
    onChange: (selectedKeys: React.Key[]) => {
      setSelectedRowKeys(selectedKeys)
    },
  }

  return (
    <div>
      {/* 工具栏 */}
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Space>
          {selectedRowKeys.length > 0 && (
            <>
              <Button
                type="primary"
                icon={<CheckOutlined />}
                onClick={handleBatchPublish}
              >
                批量发布 ({selectedRowKeys.length})
              </Button>
              <Button
                icon={<InboxOutlined />}
                onClick={handleBatchArchive}
              >
                批量归档
              </Button>
              <Popconfirm
                title="确定要删除选中的季度吗？"
                description="此操作将级联删除所有关联的剧集"
                onConfirm={handleBatchDelete}
                okText="确定"
                cancelText="取消"
              >
                <Button danger icon={<DeleteOutlined />}>
                  批量删除
                </Button>
              </Popconfirm>
            </>
          )}
        </Space>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={loadData}>
            刷新
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => handleOpenModal()}
          >
            创建季度
          </Button>
        </Space>
      </div>

      {/* 季度列表 */}
      <Table
        columns={columns}
        dataSource={dataSource}
        rowKey="id"
        loading={loading}
        rowSelection={rowSelection}
        scroll={{ x: 1400 }}
        pagination={{
          current: page,
          pageSize: pageSize,
          total: total,
          onChange: (newPage, newPageSize) => {
            setPage(newPage)
            setPageSize(newPageSize || pageSize)
          },
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条`,
        }}
      />

      {/* 创建/编辑 Modal */}
      <Modal
        title={editingId ? '编辑季度' : '创建季度'}
        open={modalVisible}
        onOk={handleSave}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
        }}
        width={720}
        okText="保存"
        cancelText="取消"
      >
        <Form
          form={form}
          layout="vertical"
          autoComplete="off"
        >
          <Form.Item
            label="季号"
            name="season_number"
            rules={[
              { required: true, message: '请输入季号' },
              { type: 'number', min: 1, message: '季号必须大于0' },
            ]}
          >
            <InputNumber
              min={1}
              style={{ width: '100%' }}
              placeholder="如：1 表示第一季"
              disabled={!!editingId}
            />
          </Form.Item>

          <Form.Item
            label="标题"
            name="title"
            rules={[{ required: true, message: '请输入标题' }]}
          >
            <Input placeholder="如：第一季：凛冬将至" />
          </Form.Item>

          <Form.Item label="简介" name="description">
            <Input.TextArea rows={4} placeholder="季度简介" />
          </Form.Item>

          <Form.Item label="状态" name="status" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="draft">草稿</Select.Option>
              <Select.Option value="published">已发布</Select.Option>
              <Select.Option value="archived">已归档</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item label="封面图URL" name="poster_url">
            <Input placeholder="https://..." />
          </Form.Item>

          <Form.Item label="背景图URL" name="backdrop_url">
            <Input placeholder="https://..." />
          </Form.Item>

          <Form.Item label="预告片URL" name="trailer_url">
            <Input placeholder="https://..." />
          </Form.Item>

          <Form.Item label="上线时间" name="release_date">
            <DatePicker showTime style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item label="VIP专享" name="vip_required" valuePropName="checked">
            <Switch />
          </Form.Item>

          <Form.Item label="推荐" name="is_featured" valuePropName="checked">
            <Switch />
          </Form.Item>

          <Form.Item label="排序权重" name="sort_order">
            <InputNumber style={{ width: '100%' }} placeholder="数字越大越靠前" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default SeasonManager
