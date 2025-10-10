/**
 * 视频专辑/系列 - 编辑页
 */
import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Card,
  Form,
  Input,
  Select,
  InputNumber,
  Switch,
  Button,
  Space,
  message,
  Tabs,
  Table,
  Modal,
  Image,
  Tag,
  Popconfirm,
} from 'antd'
import {
  SaveOutlined,
  RollbackOutlined,
  PlusOutlined,
  DeleteOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import seriesService, {
  SeriesDetail,
  SeriesVideoItem,
  SeriesCreateRequest,
  SeriesUpdateRequest,
} from '@/services/seriesService'
import videoService from '@/services/videoService'

const SeriesEdit: React.FC = () => {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const isEditMode = !!id
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [seriesData, setSeriesData] = useState<SeriesDetail | null>(null)
  const [videos, setVideos] = useState<SeriesVideoItem[]>([])
  const [addVideoModalVisible, setAddVideoModalVisible] = useState(false)
  const [availableVideos, setAvailableVideos] = useState<any[]>([])
  const [selectedVideoIds, setSelectedVideoIds] = useState<number[]>([])

  // 加载专辑数据
  const loadSeriesData = async () => {
    if (!id) return

    setLoading(true)
    try {
      const data = await seriesService.getDetail(parseInt(id))
      setSeriesData(data)
      setVideos(data.videos)
      form.setFieldsValue({
        title: data.title,
        description: data.description,
        cover_image: data.cover_image,
        type: data.type,
        status: data.status,
        display_order: data.display_order,
        is_featured: data.is_featured,
      })
    } catch (error: any) {
      message.error(error.response?.data?.detail || '加载失败')
    } finally {
      setLoading(false)
    }
  }

  // 加载可用视频列表
  const loadAvailableVideos = async () => {
    try {
      const response = await videoService.getList({ page: 1, page_size: 100, status: 'published' })
      setAvailableVideos(response.items)
    } catch (error) {
      console.error('加载视频列表失败', error)
    }
  }

  useEffect(() => {
    if (isEditMode) {
      loadSeriesData()
    }
    loadAvailableVideos()
  }, [id])

  // 保存专辑
  const handleSave = async (values: any) => {
    setLoading(true)
    try {
      if (isEditMode) {
        const updateData: SeriesUpdateRequest = {
          title: values.title,
          description: values.description,
          cover_image: values.cover_image,
          type: values.type,
          status: values.status,
          display_order: values.display_order,
          is_featured: values.is_featured,
        }
        await seriesService.update(parseInt(id!), updateData)
        message.success('更新成功')
      } else {
        const createData: SeriesCreateRequest = {
          title: values.title,
          description: values.description,
          cover_image: values.cover_image,
          type: values.type,
          status: values.status,
          display_order: values.display_order || 0,
          is_featured: values.is_featured || false,
        }
        const newSeries = await seriesService.create(createData)
        message.success('创建成功')
        navigate(`/series/${newSeries.id}/edit`)
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '保存失败')
    } finally {
      setLoading(false)
    }
  }

  // 添加视频到专辑
  const handleAddVideos = async () => {
    if (selectedVideoIds.length === 0) {
      message.warning('请选择视频')
      return
    }

    try {
      await seriesService.addVideos(parseInt(id!), {
        video_ids: selectedVideoIds,
      })
      message.success(`成功添加 ${selectedVideoIds.length} 个视频`)
      setAddVideoModalVisible(false)
      setSelectedVideoIds([])
      loadSeriesData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '添加失败')
    }
  }

  // 移除视频
  const handleRemoveVideo = async (videoId: number) => {
    try {
      await seriesService.removeVideos(parseInt(id!), {
        video_ids: [videoId],
      })
      message.success('移除成功')
      loadSeriesData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '移除失败')
    }
  }

  // 移动视频顺序
  const handleMoveVideo = async (videoId: number, direction: 'up' | 'down') => {
    const currentIndex = videos.findIndex((v) => v.video_id === videoId)
    if (currentIndex === -1) return

    const newIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1
    if (newIndex < 0 || newIndex >= videos.length) return

    const newVideos = [...videos]
    const [movedVideo] = newVideos.splice(currentIndex, 1)
    newVideos.splice(newIndex, 0, movedVideo)

    // 更新集数
    const videoOrder = newVideos.map((v, idx) => ({
      video_id: v.video_id,
      episode_number: idx + 1,
    }))

    try {
      await seriesService.updateVideoOrder(parseInt(id!), { video_order: videoOrder })
      message.success('顺序更新成功')
      loadSeriesData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '更新失败')
    }
  }

  const videoColumns: ColumnsType<SeriesVideoItem> = [
    {
      title: '集数',
      dataIndex: 'episode_number',
      key: 'episode_number',
      width: 80,
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
          '-'
        ),
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: '时长',
      dataIndex: 'duration',
      key: 'duration',
      width: 100,
      render: (duration?: number) => (duration ? `${duration}分钟` : '-'),
    },
    {
      title: '播放量',
      dataIndex: 'view_count',
      key: 'view_count',
      width: 100,
      render: (views: number) => views.toLocaleString(),
    },
    {
      title: '添加时间',
      dataIndex: 'added_at',
      key: 'added_at',
      width: 180,
      render: (time: string) => new Date(time).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_, record, index) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<ArrowUpOutlined />}
            disabled={index === 0}
            onClick={() => handleMoveVideo(record.video_id, 'up')}
          >
            上移
          </Button>
          <Button
            type="link"
            size="small"
            icon={<ArrowDownOutlined />}
            disabled={index === videos.length - 1}
            onClick={() => handleMoveVideo(record.video_id, 'down')}
          >
            下移
          </Button>
          <Popconfirm
            title="确定要移除此视频吗？"
            onConfirm={() => handleRemoveVideo(record.video_id)}
          >
            <Button type="link" danger size="small" icon={<DeleteOutlined />}>
              移除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div style={{ padding: '24px' }}>
      <h2>{isEditMode ? '编辑专辑' : '创建专辑'}</h2>

      <Tabs
        defaultActiveKey="basic"
        items={[
          {
            key: 'basic',
            label: '基本信息',
            children: (
              <Card>
                <Form
                  form={form}
                  layout="vertical"
                  onFinish={handleSave}
                  initialValues={{
                    type: 'series',
                    status: 'draft',
                    display_order: 0,
                    is_featured: false,
                  }}
                >
                  <Form.Item
                    name="title"
                    label="专辑标题"
                    rules={[{ required: true, message: '请输入标题' }]}
                  >
                    <Input placeholder="输入专辑标题" />
                  </Form.Item>

                  <Form.Item name="description" label="专辑描述">
                    <Input.TextArea rows={4} placeholder="输入专辑描述" />
                  </Form.Item>

                  <Form.Item name="cover_image" label="封面图URL">
                    <Input placeholder="输入封面图URL" />
                  </Form.Item>

                  <Form.Item name="type" label="专辑类型" rules={[{ required: true }]}>
                    <Select>
                      <Select.Option value="series">系列剧</Select.Option>
                      <Select.Option value="collection">合集</Select.Option>
                      <Select.Option value="franchise">系列作品</Select.Option>
                    </Select>
                  </Form.Item>

                  <Form.Item name="status" label="发布状态" rules={[{ required: true }]}>
                    <Select>
                      <Select.Option value="draft">草稿</Select.Option>
                      <Select.Option value="published">已发布</Select.Option>
                      <Select.Option value="archived">已归档</Select.Option>
                    </Select>
                  </Form.Item>

                  <Form.Item name="display_order" label="显示顺序">
                    <InputNumber min={0} style={{ width: '100%' }} />
                  </Form.Item>

                  <Form.Item name="is_featured" label="推荐到首页" valuePropName="checked">
                    <Switch />
                  </Form.Item>

                  <Form.Item>
                    <Space>
                      <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={loading}>
                        保存
                      </Button>
                      <Button icon={<RollbackOutlined />} onClick={() => navigate('/series')}>
                        返回
                      </Button>
                    </Space>
                  </Form.Item>
                </Form>
              </Card>
            ),
          },
          {
            key: 'videos',
            label: `视频管理 (${videos.length})`,
            disabled: !isEditMode,
            children: (
              <Card>
                <Space style={{ marginBottom: 16 }}>
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={() => setAddVideoModalVisible(true)}
                  >
                    添加视频
                  </Button>
                  <Tag color="blue">共 {videos.length} 个视频</Tag>
                </Space>

                <Table
                  columns={videoColumns}
                  dataSource={videos}
                  rowKey="video_id"
                  scroll={{ x: 1200 }}
                  pagination={false}
                />
              </Card>
            ),
          },
        ]}
      />

      {/* 添加视频Modal */}
      <Modal
        title="添加视频到专辑"
        open={addVideoModalVisible}
        onOk={handleAddVideos}
        onCancel={() => {
          setAddVideoModalVisible(false)
          setSelectedVideoIds([])
        }}
        width={800}
      >
        <Table
          dataSource={availableVideos}
          rowKey="id"
          rowSelection={{
            selectedRowKeys: selectedVideoIds,
            onChange: (keys) => setSelectedVideoIds(keys as number[]),
          }}
          columns={[
            {
              title: 'ID',
              dataIndex: 'id',
              width: 60,
            },
            {
              title: '标题',
              dataIndex: 'title',
              ellipsis: true,
            },
            {
              title: '播放量',
              dataIndex: 'view_count',
              width: 100,
              render: (v: number) => v.toLocaleString(),
            },
          ]}
          pagination={{ pageSize: 10 }}
        />
      </Modal>
    </div>
  )
}

export default SeriesEdit
