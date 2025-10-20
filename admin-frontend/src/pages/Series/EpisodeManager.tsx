/**
 * Episode (单集) 管理组件
 * 用于管理季度下的剧集
 */
import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
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
  Tag,
  InputNumber,
  DatePicker,
  Tooltip,
  Tabs,
  Transfer,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  CheckOutlined,
  InboxOutlined,
  MenuOutlined,
  PlayCircleOutlined,
  ScissorOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { DndContext, DragEndEvent, PointerSensor, useSensor, useSensors } from '@dnd-kit/core'
import { restrictToVerticalAxis } from '@dnd-kit/modifiers'
import { SortableContext, useSortable, verticalListSortingStrategy, arrayMove } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import episodeService, {
  EpisodeListItem,
  EpisodeCreateRequest,
  EpisodeUpdateRequest,
  EpisodeStatus,
  BatchAddEpisodesRequest,
} from '@/services/episodeService'
import videoService from '@/services/videoService'
import { formatAWSDate, formatAWSNumber, AWSTag } from '@/utils/awsStyleHelpers'
import dayjs from 'dayjs'

interface EpisodeManagerProps {
  seasonId: number
  seriesId?: number
}

// 拖拽行组件
interface RowProps extends React.HTMLAttributes<HTMLTableRowElement> {
  'data-row-key': string
}

const Row = (props: RowProps) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: props['data-row-key'],
  })

  const style: React.CSSProperties = {
    ...props.style,
    transform: CSS.Transform.toString(transform),
    transition,
    cursor: 'move',
    ...(isDragging ? { position: 'relative', zIndex: 9999 } : {}),
  }

  return <tr {...props} ref={setNodeRef} style={style} {...attributes} {...listeners} />
}

const EpisodeManager: React.FC<EpisodeManagerProps> = ({
  const { t } = useTranslation()
 seasonId, seriesId }) => {
  const [loading, setLoading] = useState(false)
  const [dataSource, setDataSource] = useState<EpisodeListItem[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])

  // 创建/编辑 Modal
  const [modalVisible, setModalVisible] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form] = Form.useForm()

  // 批量添加 Modal
  const [batchAddModalVisible, setBatchAddModalVisible] = useState(false)
  const [batchAddForm] = Form.useForm()
  const [availableVideos, setAvailableVideos] = useState<any[]>([])
  const [selectedVideoIds, setSelectedVideoIds] = useState<number[]>([])

  // 片头片尾设置 Modal
  const [introModalVisible, setIntroModalVisible] = useState(false)
  const [introForm] = Form.useForm()

  // 拖拽排序
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 1,
      },
    })
  )

  // 加载剧集列表
  const loadData = async () => {
    setLoading(true)
    try {
      const response = await episodeService.getListBySeason(seasonId, {
        page,
        page_size: pageSize,
        sort_by: 'episode_number',
        sort_order: 'asc',
      })
      setDataSource(response.items)
      setTotal(response.total)
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('episode.message.loadFailed'))
    } finally {
      setLoading(false)
    }
  }

  // 加载可用视频
  const loadAvailableVideos = async () => {
    try {
      const response = await videoService.getList({
        page: 1,
        page_size: 200,
        status: 'PUBLISHED',
      })
      setAvailableVideos(response.items)
    } catch (error) {
      console.error(t('episode.message.loadVideosFailed'), error)
    }
  }

  useEffect(() => {
    loadData()
  }, [seasonId, page, pageSize])

  // 打开创建/编辑 Modal
  const handleOpenModal = async (episodeId?: number) => {
    if (episodeId) {
      setEditingId(episodeId)
      setLoading(true)
      try {
        const data = await episodeService.getDetail(episodeId)
        form.setFieldsValue({
          episode_number: data.episode_number,
          title: data.title,
          description: data.description,
          intro_start: data.intro_start,
          intro_end: data.intro_end,
          credits_start: data.credits_start,
          is_free: data.is_free,
          vip_required: data.vip_required,
          status: data.status,
          release_date: data.release_date ? dayjs(data.release_date) : null,
          is_featured: data.is_featured,
          sort_order: data.sort_order,
        })
      } catch (error: any) {
        message.error(error.response?.data?.detail || t('episode.message.loadFailed'))
        return
      } finally {
        setLoading(false)
      }
    } else {
      setEditingId(null)
      // 自动填充下一集号
      const maxEpisodeNumber = dataSource.length > 0
        ? Math.max(...dataSource.map(e => e.episode_number))
        : 0
      form.setFieldsValue({
        episode_number: maxEpisodeNumber + 1,
        status: 'draft',
        is_free: false,
        vip_required: false,
        is_featured: false,
        sort_order: 0,
      })
    }
    setModalVisible(true)
  }

  // 保存剧集
  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      const data = {
        ...values,
        release_date: values.release_date ? values.release_date.toISOString() : undefined,
      }

      if (editingId) {
        await episodeService.update(editingId, data as EpisodeUpdateRequest)
        message.success(t('episode.message.updateSuccess'))
      } else {
        await episodeService.create(seasonId, data as EpisodeCreateRequest)
        message.success(t('episode.message.createSuccess'))
      }

      setModalVisible(false)
      form.resetFields()
      loadData()
    } catch (error: any) {
      if (error.errorFields) {
        return
      }
      message.error(error.response?.data?.detail || t('episode.message.saveFailed'))
    }
  }

  // 删除剧集
  const handleDelete = async (id: number) => {
    try {
      await episodeService.delete(id)
      message.success(t('episode.message.deleteSuccess'))
      loadData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('episode.message.deleteFailed'))
    }
  }

  // 批量添加剧集
  const handleOpenBatchAdd = () => {
    loadAvailableVideos()
    batchAddForm.setFieldsValue({
      start_episode_number: (dataSource.length > 0 ? Math.max(...dataSource.map(e => e.episode_number)) : 0) + 1,
      auto_title: true,
      title_prefix: t('episode.prefix.episode'),
      title_suffix: t('episode.unit.episode'),
      is_free: false,
      vip_required: false,
      status: 'draft',
    })
    setBatchAddModalVisible(true)
  }

  const handleBatchAdd = async () => {
    try {
      const values = await batchAddForm.validateFields()
      const data: BatchAddEpisodesRequest = {
        video_ids: selectedVideoIds,
        start_episode_number: values.start_episode_number,
        auto_title: values.auto_title,
        title_prefix: values.title_prefix,
        title_suffix: values.title_suffix,
        is_free: values.is_free,
        vip_required: values.vip_required,
        status: values.status,
      }

      await episodeService.batchAdd(seasonId, data)
      message.success(t('episode.message.batchAddSuccess', { count: selectedVideoIds.length }))
      setBatchAddModalVisible(false)
      batchAddForm.resetFields()
      setSelectedVideoIds([])
      loadData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('episode.message.batchAddFailed'))
    }
  }

  // 拖拽结束
  const onDragEnd = async ({ active, over }: DragEndEvent) => {
    if (active.id !== over?.id) {
      const activeIndex = dataSource.findIndex((i) => i.id === active.id)
      const overIndex = dataSource.findIndex((i) => i.id === over?.id)
      const newData = arrayMove(dataSource, activeIndex, overIndex)

      // 更新本地状态
      setDataSource(newData)

      // 生成新的顺序
      const episode_orders = newData.map((item, index) => ({
        episode_id: item.id,
        episode_number: index + 1,
      }))

      // 保存到后端
      try {
        await episodeService.updateOrder(seasonId, { episode_orders })
        message.success(t('episode.message.orderUpdated'))
        loadData() // 重新加载以获取最新数据
      } catch (error: any) {
        message.error(error.response?.data?.detail || t('episode.message.updateOrderFailed'))
        loadData() // 发生错误时恢复数据
      }
    }
  }

  // 打开片头片尾设置
  const handleOpenIntroMarkers = () => {
    if (selectedRowKeys.length === 0) {
      message.warning(t('episode.message.selectForOpeningEnding'))
      return
    }
    setIntroModalVisible(true)
  }

  // 批量设置片头片尾
  const handleSetIntroMarkers = async () => {
    try {
      const values = await introForm.validateFields()
      await episodeService.batchSetIntroMarkers({
        episode_ids: selectedRowKeys as number[],
        intro_start: values.intro_start,
        intro_end: values.intro_end,
        credits_start: values.credits_start,
      })
      message.success(t('episode.message.setSuccess'))
      setIntroModalVisible(false)
      introForm.resetFields()
      setSelectedRowKeys([])
      loadData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('episode.message.setFailed'))
    }
  }

  // 批量发布
  const handleBatchPublish = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning(t('episode.message.selectToPublish'))
      return
    }

    try {
      await episodeService.batchPublish(selectedRowKeys as number[])
      message.success(`成功发布 ${selectedRowKeys.length} 集`)
      setSelectedRowKeys([])
      loadData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('episode.message.batchPublishFailed'))
    }
  }

  // 批量删除
  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning(t('episode.message.selectToDelete'))
      return
    }

    try {
      await episodeService.batchDelete(selectedRowKeys as number[])
      message.success(`成功删除 ${selectedRowKeys.length} 集`)
      setSelectedRowKeys([])
      loadData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || t('episode.message.batchDeleteFailed'))
    }
  }

  // 状态标签
  const getStatusTag = (status: EpisodeStatus) => {
    const statusMap: Record<EpisodeStatus, { type: 'default' | 'success' | 'warning'; text: string }> = {
      draft: { type: 'default', text: t('episode.status.draft') },
      published: { type: 'success', text: t('episode.status.published') },
      archived: { type: 'warning', text: t('episode.status.archived') },
    }
    const config = statusMap[status]
    return <AWSTag type={config.type}>{config.text}</AWSTag>
  }

  const columns: ColumnsType<EpisodeListItem> = [
    {
      key: 'sort',
      width: 40,
      render: () => <MenuOutlined style={{ cursor: 'move', color: '#999' }} />,
    },
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: t('episode.table.episodeNumber'),
      dataIndex: 'episode_number',
      key: 'episode_number',
      width: 80,
      render: (num: number) => <Tag color="blue">{t('episode.template.episodeNum', { num })}</Tag>,
    },
    {
      title: t('episode.table.title'),
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      width: 200,
    },
    {
      title: t('episode.table.status'),
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: EpisodeStatus) => getStatusTag(status),
    },
    {
      title: t('episode.table.permission'),
      key: 'permission',
      width: 120,
      render: (_, record) => (
        <Space size={4}>
          {record.is_free && <Tag color="green">{t('episode.permission.free')}</Tag>}
          {record.vip_required && <Tag color="gold">VIP</Tag>}
        </Space>
      ),
    },
    {
      title: '片头/片尾',
      key: 'markers',
      width: 150,
      render: (_, record) => {
        const markers = []
        if (record.intro_start !== null && record.intro_end !== null) {
          markers.push(`片头 ${record.intro_start}-${record.intro_end}s`)
        }
        if (record.credits_start !== null) {
          markers.push(`片尾 ${record.credits_start}s`)
        }
        return markers.length > 0 ? (
          <Tooltip title={markers.join(', ')}>
            <Tag icon={<ScissorOutlined />} color="purple">
              已设置
            </Tag>
          </Tooltip>
        ) : (
          <span style={{ color: '#ccc' }}>{t('episode.status.notSet')}</span>
        )
      },
    },
    {
      title: '播放量',
      dataIndex: 'view_count',
      key: 'view_count',
      width: 100,
      render: (views: number) => formatAWSNumber(views.toLocaleString()),
    },
    {
      title: t('episode.table.likes'),
      dataIndex: 'like_count',
      key: 'like_count',
      width: 80,
      render: (likes: number) => formatAWSNumber(likes),
    },
    {
      title: t('episode.table.comments'),
      dataIndex: 'comment_count',
      key: 'comment_count',
      width: 80,
      render: (comments: number) => formatAWSNumber(comments),
    },
    {
      title: t('episode.table.createTime'),
      dataIndex: 'created_at',
      key: 'created_at',
      width: 160,
      render: (time: string) => formatAWSDate(time, 'YYYY-MM-DD HH:mm'),
    },
    {
      title: t('common.actions'),
      key: 'action',
      width: 180,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleOpenModal(record.id)}
          >
            编辑
          </Button>
          <Popconfirm
            title={t('episode.confirm.deleteSingle')}
            onConfirm={() => handleDelete(record.id)}
            okText=t('common.confirm')
            cancelText=t('common.cancel')
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
                icon={<ScissorOutlined />}
                onClick={handleOpenIntroMarkers}
              >
                设置片头片尾
              </Button>
              <Popconfirm
                title={t('episode.confirm.deleteSelected')}
                onConfirm={handleBatchDelete}
                okText=t('common.confirm')
                cancelText=t('common.cancel')
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
            icon={<PlayCircleOutlined />}
            onClick={handleOpenBatchAdd}
          >
            批量添加视频
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => handleOpenModal()}
          >
            创建剧集
          </Button>
        </Space>
      </div>

      {/* 剧集列表（支持拖拽排序） */}
      <DndContext sensors={sensors} modifiers={[restrictToVerticalAxis]} onDragEnd={onDragEnd}>
        <SortableContext items={dataSource.map((i) => i.id)} strategy={verticalListSortingStrategy}>
          <Table
            components={{
              body: {
                row: Row,
              },
            }}
            columns={columns}
            dataSource={dataSource}
            rowKey="id"
            loading={loading}
            rowSelection={rowSelection}
            scroll={{ x: 1600 }}
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
              showTotal: (total) => t('common.totalItems', { total }),
            }}
          />
        </SortableContext>
      </DndContext>

      {/* 创建/编辑 Modal */}
      <Modal
        title={editingId ? '编辑剧集' : t('episode.actions.createEpisode')}
        open={modalVisible}
        onOk={handleSave}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
        }}
        width={720}
        okText=t('common.save')
        cancelText=t('common.cancel')
      >
        <Form form={form} layout="vertical" autoComplete="off">
          {!editingId && (
            <Form.Item
              label=t('episode.form.videoId')
              name="video_id"
              rules={[{ required: true, message: t('episode.placeholder.videoId') }]}
            >
              <InputNumber min={1} style={{ width: '100%' }} />
            </Form.Item>
          )}

          <Form.Item
            label=t('episode.table.episodeNumber')
            name="episode_number"
            rules={[
              { required: true, message: '请输入集号' },
              { type: 'number', min: 1, message: t('episode.validation.numberGreaterThanZero') },
            ]}
          >
            <InputNumber min={1} style={{ width: '100%' }} placeholder={t('episode.placeholder.firstEpisode')} />
          </Form.Item>

          <Form.Item
            label=t('episode.table.title')
            name="title"
            rules={[{ required: true, message: '请输入标题' }]}
          >
            <Input placeholder={t('episode.placeholder.episodeTitle')} />
          </Form.Item>

          <Form.Item label=t('episode.table.description') name="description">
            <Input.TextArea rows={3} placeholder=t('episode.form.description') />
          </Form.Item>

          <Tabs
            items={[
              {
                key: 'basic',
                label: t('episode.sections.basic'),
                children: (
                  <>
                    <Form.Item label=t('episode.table.status') name="status" rules={[{ required: true }]}>
                      <Select>
                        <Select.Option value="draft">{t('episode.status.draft')}</Select.Option>
                        <Select.Option value="published">{t('episode.status.published')}</Select.Option>
                        <Select.Option value="archived">{t('episode.status.archived')}</Select.Option>
                      </Select>
                    </Form.Item>

                    <Form.Item label={t('episode.form.releaseDate')} name="release_date">
                      <DatePicker showTime style={{ width: '100%' }} />
                    </Form.Item>

                    <Space size="large">
                      <Form.Item label=t('episode.permission.freeWatch') name="is_free" valuePropName="checked">
                        <Switch />
                      </Form.Item>

                      <Form.Item label=t('episode.permission.vipOnly') name="vip_required" valuePropName="checked">
                        <Switch />
                      </Form.Item>

                      <Form.Item label=t('episode.recommended') name="is_featured" valuePropName="checked">
                        <Switch />
                      </Form.Item>
                    </Space>
                  </>
                ),
              },
              {
                key: 'intro',
                label: t('episode.sections.openingEnding'),
                children: (
                  <>
                    <Form.Item label={t('episode.form.openingStartTime')} name="intro_start">
                      <InputNumber min={0} style={{ width: '100%' }} />
                    </Form.Item>

                    <Form.Item label=t('episode.form.openingEndTime') name="intro_end">
                      <InputNumber min={0} style={{ width: '100%' }} />
                    </Form.Item>

                    <Form.Item label=t('episode.form.endingStartTime') name="credits_start">
                      <InputNumber min={0} style={{ width: '100%' }} />
                    </Form.Item>
                  </>
                ),
              },
            ]}
          />
        </Form>
      </Modal>

      {/* 批量添加视频 Modal */}
      <Modal
        title={t('episode.modal.batchAddTitle')}
        open={batchAddModalVisible}
        onOk={handleBatchAdd}
        onCancel={() => {
          setBatchAddModalVisible(false)
          batchAddForm.resetFields()
          setSelectedVideoIds([])
        }}
        width={800}
        okText=t('common.add')
        cancelText=t('common.cancel')
        okButtonProps={{ disabled: selectedVideoIds.length === 0 }}
      >
        <Form form={batchAddForm} layout="vertical">
          <Form.Item label=t('episode.actions.selectVideo') required>
            <Transfer
              dataSource={availableVideos.map((v) => ({
                key: v.id,
                title: `[${v.id}] ${v.title}`,
                description: `时长: ${v.duration || 0}分钟`,
              }))}
              targetKeys={selectedVideoIds}
              onChange={(targetKeys) => setSelectedVideoIds(targetKeys as number[])}
              render={(item) => item.title}
              listStyle={{ width: 350, height: 400 }}
              showSearch
              filterOption={(inputValue, item) =>
                item.title.toLowerCase().includes(inputValue.toLowerCase())
              }
            />
          </Form.Item>

          <Form.Item
            label=t('episode.form.startNumber')
            name="start_episode_number"
            rules={[{ required: true }]}
          >
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item label=t('episode.actions.autoGenerateTitle') name="auto_title" valuePropName="checked">
            <Switch />
          </Form.Item>

          <Form.Item noStyle shouldUpdate={(prev, curr) => prev.auto_title !== curr.auto_title}>
            {({ getFieldValue }) =>
              getFieldValue('auto_title') ? (
                <Space>
                  <Form.Item label=t('episode.form.titlePrefix') name="title_prefix">
                    <Input style={{ width: 100 }} />
                  </Form.Item>
                  <Form.Item label=t('episode.form.titleSuffix') name="title_suffix">
                    <Input style={{ width: 100 }} />
                  </Form.Item>
                </Space>
              ) : null
            }
          </Form.Item>

          <Space>
            <Form.Item label=t('episode.permission.freeWatch') name="is_free" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item label=t('episode.permission.vipOnly') name="vip_required" valuePropName="checked">
              <Switch />
            </Form.Item>
          </Space>

          <Form.Item label=t('episode.table.status') name="status">
            <Select>
              <Select.Option value="draft">{t('episode.status.draft')}</Select.Option>
              <Select.Option value="published">{t('episode.status.published')}</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 批量设置片头片尾 Modal */}
      <Modal
        title={t('episode.modal.batchSetOpeningEnding')}
        open={introModalVisible}
        onOk={handleSetIntroMarkers}
        onCancel={() => {
          setIntroModalVisible(false)
          introForm.resetFields()
        }}
        okText=t('common.save')
        cancelText=t('common.cancel')
      >
        <Form form={introForm} layout="vertical">
          <p style={{ marginBottom: 16, color: '#666' }}>
            将对选中的 {selectedRowKeys.length} 集设置相同的片头片尾标记
          </p>

          <Form.Item label={t('episode.form.openingStartTime')} name="intro_start">
            <InputNumber min={0} style={{ width: '100%' }} placeholder=t('episode.placeholder.episodeNumber') />
          </Form.Item>

          <Form.Item label=t('episode.form.openingEndTime') name="intro_end">
            <InputNumber min={0} style={{ width: '100%' }} placeholder=t('episode.placeholder.openingTime') />
          </Form.Item>

          <Form.Item label=t('episode.form.endingStartTime') name="credits_start">
            <InputNumber min={0} style={{ width: '100%' }} placeholder=t('episode.placeholder.endingTime') />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default EpisodeManager
