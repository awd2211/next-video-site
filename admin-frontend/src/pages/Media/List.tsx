import { useState, useEffect } from 'react'
import {
  Table,
  Card,
  Button,
  Space,
  Input,
  Select,
  Modal,
  Form,
  Upload,
  message,
  Image,
  Tag,
  Statistic,
  Row,
  Col,
  Popconfirm,
  Tooltip,
} from 'antd'
import {
  PlusOutlined,
  SearchOutlined,
  UploadOutlined,
  DeleteOutlined,
  EditOutlined,
  EyeOutlined,
  DownloadOutlined,
  FolderOutlined,
  PictureOutlined,
  VideoCameraOutlined,
  ReloadOutlined,
  FolderAddOutlined,
  SettingOutlined,
} from '@ant-design/icons'
import axios from '@/utils/axios'
import type { UploadFile } from 'antd/es/upload/interface'

const { TextArea } = Input
const { Option } = Select

interface Media {
  id: number
  title: string
  description: string | null
  filename: string
  file_path: string
  file_size: number
  mime_type: string
  media_type: 'image' | 'video'
  status: string
  width: number | null
  height: number | null
  duration: number | null
  url: string
  thumbnail_url: string | null
  folder: string | null
  tags: string | null
  view_count: number
  download_count: number
  created_at: string
}

interface MediaStats {
  total_count: number
  image_count: number
  video_count: number
  total_size: number
  total_views: number
  total_downloads: number
}

const MediaList = () => {
  const [data, setData] = useState<Media[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [search, setSearch] = useState('')
  const [mediaType, setMediaType] = useState<string>('')
  const [folder, setFolder] = useState<string>('')
  const [folders, setFolders] = useState<{ name: string; count: number }[]>([])
  const [stats, setStats] = useState<MediaStats | null>(null)

  const [uploadModalVisible, setUploadModalVisible] = useState(false)
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [folderModalVisible, setFolderModalVisible] = useState(false)
  const [folderAction, setFolderAction] = useState<'create' | 'rename' | 'delete'>('create')
  const [selectedFolder, setSelectedFolder] = useState<string>('')
  const [currentMedia, setCurrentMedia] = useState<Media | null>(null)
  const [uploadForm] = Form.useForm()
  const [editForm] = Form.useForm()
  const [folderForm] = Form.useForm()
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    fetchData()
    fetchStats()
    fetchFolders()
  }, [page, pageSize, search, mediaType, folder])

  const fetchData = async () => {
    setLoading(true)
    try {
      const params: any = { page, page_size: pageSize }
      if (search) params.search = search
      if (mediaType) params.media_type = mediaType
      if (folder) params.folder = folder

      const response = await axios.get('/api/v1/admin/media', { params })
      setData(response.data.items)
      setTotal(response.data.total)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '加载失败')
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/v1/admin/media/stats')
      setStats(response.data)
    } catch (error) {
      console.error('获取统计失败', error)
    }
  }

  const fetchFolders = async () => {
    try {
      const response = await axios.get('/api/v1/admin/media/folders')
      setFolders(response.data)
    } catch (error) {
      console.error('获取文件夹失败', error)
    }
  }

  const handleUpload = async () => {
    try {
      const values = await uploadForm.validateFields()

      if (fileList.length === 0) {
        message.error('请选择文件')
        return
      }

      setUploading(true)
      const formData = new FormData()
      formData.append('file', fileList[0] as any)
      formData.append('title', values.title)
      if (values.description) formData.append('description', values.description)
      if (values.folder) formData.append('folder', values.folder)
      if (values.tags) formData.append('tags', values.tags)

      await axios.post('/api/v1/admin/media/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      message.success('上传成功')
      setUploadModalVisible(false)
      uploadForm.resetFields()
      setFileList([])
      fetchData()
      fetchStats()
      fetchFolders()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '上传失败')
    } finally {
      setUploading(false)
    }
  }

  const handleEdit = (record: Media) => {
    setCurrentMedia(record)
    editForm.setFieldsValue({
      title: record.title,
      description: record.description,
      folder: record.folder,
      tags: record.tags,
    })
    setEditModalVisible(true)
  }

  const handleUpdate = async () => {
    try {
      const values = await editForm.validateFields()
      await axios.put(`/api/v1/admin/media/${currentMedia?.id}`, values)
      message.success('更新成功')
      setEditModalVisible(false)
      fetchData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '更新失败')
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await axios.delete(`/api/v1/admin/media/${id}`)
      message.success('删除成功')
      fetchData()
      fetchStats()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败')
    }
  }

  const handleCreateFolder = () => {
    setFolderAction('create')
    folderForm.resetFields()
    setFolderModalVisible(true)
  }

  const handleRenameFolder = (folderName: string) => {
    setFolderAction('rename')
    setSelectedFolder(folderName)
    folderForm.setFieldsValue({ old_name: folderName, new_name: '' })
    setFolderModalVisible(true)
  }

  const handleDeleteFolder = (folderName: string) => {
    setFolderAction('delete')
    setSelectedFolder(folderName)
    folderForm.setFieldsValue({ folder_name: folderName, move_to: null })
    setFolderModalVisible(true)
  }

  const handleFolderSubmit = async () => {
    try {
      const values = await folderForm.validateFields()

      if (folderAction === 'create') {
        await axios.post('/api/v1/admin/media/folders', null, {
          params: { folder_name: values.folder_name }
        })
        message.success('文件夹创建成功')
      } else if (folderAction === 'rename') {
        await axios.put(`/api/v1/admin/media/folders/${selectedFolder}`, null, {
          params: { new_name: values.new_name }
        })
        message.success('文件夹重命名成功')
      } else if (folderAction === 'delete') {
        await axios.delete(`/api/v1/admin/media/folders/${selectedFolder}`, {
          params: { move_to: values.move_to || null }
        })
        message.success('文件夹删除成功')
      }

      setFolderModalVisible(false)
      fetchFolders()
      fetchData()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败')
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return '-'
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  const columns = [
    {
      title: '预览',
      dataIndex: 'url',
      key: 'preview',
      width: 100,
      render: (url: string, record: Media) => (
        record.media_type === 'image' ? (
          <Image src={url} width={60} height={60} style={{ objectFit: 'cover' }} />
        ) : (
          <div style={{
            width: 60,
            height: 60,
            background: '#f0f0f0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: 4,
          }}>
            <VideoCameraOutlined style={{ fontSize: 24, color: '#999' }} />
          </div>
        )
      ),
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: '类型',
      dataIndex: 'media_type',
      key: 'media_type',
      width: 80,
      render: (type: string) => (
        type === 'image' ? (
          <Tag icon={<PictureOutlined />} color="blue">图片</Tag>
        ) : (
          <Tag icon={<VideoCameraOutlined />} color="purple">视频</Tag>
        )
      ),
    },
    {
      title: '文件名',
      dataIndex: 'filename',
      key: 'filename',
      ellipsis: true,
    },
    {
      title: '大小',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 100,
      render: (size: number) => formatFileSize(size),
    },
    {
      title: '尺寸/时长',
      key: 'dimensions',
      width: 120,
      render: (_: any, record: Media) => {
        if (record.media_type === 'image') {
          return record.width && record.height ? `${record.width}×${record.height}` : '-'
        } else {
          return formatDuration(record.duration)
        }
      },
    },
    {
      title: '文件夹',
      dataIndex: 'folder',
      key: 'folder',
      width: 100,
      render: (folder: string | null) => folder || '-',
    },
    {
      title: '查看/下载',
      key: 'stats',
      width: 100,
      render: (_: any, record: Media) => (
        <Space direction="vertical" size={0}>
          <span><EyeOutlined /> {record.view_count}</span>
          <span><DownloadOutlined /> {record.download_count}</span>
        </Space>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 160,
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right' as const,
      render: (_: any, record: Media) => (
        <Space>
          <Tooltip title="编辑">
            <Button
              type="link"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          <Tooltip title="查看">
            <Button
              type="link"
              icon={<EyeOutlined />}
              onClick={() => window.open(record.url, '_blank')}
            />
          </Tooltip>
          <Popconfirm
            title="确定删除吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button type="link" danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      {/* 统计卡片 */}
      {stats && (
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={4}>
            <Card>
              <Statistic title="总数量" value={stats.total_count} />
            </Card>
          </Col>
          <Col span={4}>
            <Card>
              <Statistic
                title="图片"
                value={stats.image_count}
                prefix={<PictureOutlined />}
              />
            </Card>
          </Col>
          <Col span={4}>
            <Card>
              <Statistic
                title="视频"
                value={stats.video_count}
                prefix={<VideoCameraOutlined />}
              />
            </Card>
          </Col>
          <Col span={4}>
            <Card>
              <Statistic
                title="总大小"
                value={formatFileSize(stats.total_size)}
              />
            </Card>
          </Col>
          <Col span={4}>
            <Card>
              <Statistic title="总查看" value={stats.total_views} />
            </Card>
          </Col>
          <Col span={4}>
            <Card>
              <Statistic title="总下载" value={stats.total_downloads} />
            </Card>
          </Col>
        </Row>
      )}

      <Card>
        {/* 工具栏 */}
        <Space style={{ marginBottom: 16 }} wrap>
          <Input
            placeholder="搜索标题、描述、标签"
            prefix={<SearchOutlined />}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onPressEnter={fetchData}
            style={{ width: 250 }}
          />
          <Select
            placeholder="媒体类型"
            value={mediaType}
            onChange={setMediaType}
            style={{ width: 120 }}
            allowClear
          >
            <Option value="image">图片</Option>
            <Option value="video">视频</Option>
          </Select>
          <Select
            placeholder="文件夹"
            value={folder}
            onChange={setFolder}
            style={{ width: 150 }}
            allowClear
            dropdownRender={(menu) => (
              <>
                {menu}
                {folders.length > 0 && <div style={{ borderTop: '1px solid #f0f0f0', margin: '4px 0' }} />}
                <Space style={{ padding: '8px' }}>
                  <Button
                    type="text"
                    size="small"
                    icon={<FolderAddOutlined />}
                    onClick={handleCreateFolder}
                  >
                    新建文件夹
                  </Button>
                </Space>
              </>
            )}
          >
            {folders.map((f) => (
              <Option key={f.name} value={f.name}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span>
                    <FolderOutlined /> {f.name} ({f.count})
                  </span>
                  <Space size={4} onClick={(e) => e.stopPropagation()}>
                    <Button
                      type="text"
                      size="small"
                      icon={<EditOutlined />}
                      onClick={(e) => {
                        e.stopPropagation()
                        handleRenameFolder(f.name)
                      }}
                    />
                    <Button
                      type="text"
                      size="small"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDeleteFolder(f.name)
                      }}
                    />
                  </Space>
                </div>
              </Option>
            ))}
          </Select>
          <Button icon={<ReloadOutlined />} onClick={fetchData}>
            刷新
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setUploadModalVisible(true)}
          >
            上传媒体
          </Button>
        </Space>

        {/* 表格 */}
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1500 }}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => {
              setPage(page)
              setPageSize(pageSize)
            },
          }}
        />
      </Card>

      {/* 上传模态框 */}
      <Modal
        title="上传媒体"
        open={uploadModalVisible}
        onOk={handleUpload}
        onCancel={() => {
          setUploadModalVisible(false)
          uploadForm.resetFields()
          setFileList([])
        }}
        confirmLoading={uploading}
        width={600}
      >
        <Form form={uploadForm} layout="vertical">
          <Form.Item
            label="文件"
            required
          >
            <Upload
              fileList={fileList}
              beforeUpload={(file) => {
                setFileList([file])
                return false
              }}
              onRemove={() => setFileList([])}
              maxCount={1}
              accept="image/*,video/*"
            >
              <Button icon={<UploadOutlined />}>选择文件</Button>
            </Upload>
          </Form.Item>
          <Form.Item
            name="title"
            label="标题"
            rules={[{ required: true, message: '请输入标题' }]}
          >
            <Input placeholder="媒体标题" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="媒体描述" />
          </Form.Item>
          <Form.Item name="folder" label="文件夹">
            <Input placeholder="文件夹名称（可选）" />
          </Form.Item>
          <Form.Item name="tags" label="标签">
            <Input placeholder="标签，逗号分隔" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 编辑模态框 */}
      <Modal
        title="编辑媒体"
        open={editModalVisible}
        onOk={handleUpdate}
        onCancel={() => setEditModalVisible(false)}
        width={600}
      >
        <Form form={editForm} layout="vertical">
          <Form.Item
            name="title"
            label="标题"
            rules={[{ required: true, message: '请输入标题' }]}
          >
            <Input placeholder="媒体标题" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="媒体描述" />
          </Form.Item>
          <Form.Item name="folder" label="文件夹">
            <Input placeholder="文件夹名称" />
          </Form.Item>
          <Form.Item name="tags" label="标签">
            <Input placeholder="标签，逗号分隔" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 文件夹管理模态框 */}
      <Modal
        title={
          folderAction === 'create' ? '新建文件夹' :
          folderAction === 'rename' ? '重命名文件夹' :
          '删除文件夹'
        }
        open={folderModalVisible}
        onOk={handleFolderSubmit}
        onCancel={() => setFolderModalVisible(false)}
        width={500}
      >
        <Form form={folderForm} layout="vertical">
          {folderAction === 'create' && (
            <Form.Item
              name="folder_name"
              label="文件夹名称"
              rules={[
                { required: true, message: '请输入文件夹名称' },
                { max: 255, message: '文件夹名称最多255个字符' }
              ]}
            >
              <Input placeholder="输入文件夹名称" prefix={<FolderOutlined />} />
            </Form.Item>
          )}

          {folderAction === 'rename' && (
            <>
              <Form.Item label="原文件夹名称">
                <Input value={selectedFolder} disabled />
              </Form.Item>
              <Form.Item
                name="new_name"
                label="新文件夹名称"
                rules={[
                  { required: true, message: '请输入新文件夹名称' },
                  { max: 255, message: '文件夹名称最多255个字符' }
                ]}
              >
                <Input placeholder="输入新文件夹名称" prefix={<FolderOutlined />} />
              </Form.Item>
            </>
          )}

          {folderAction === 'delete' && (
            <>
              <Form.Item label="要删除的文件夹">
                <Input value={selectedFolder} disabled />
              </Form.Item>
              <Form.Item
                name="move_to"
                label="文件移动到"
                extra="删除文件夹后，其中的文件将移动到指定文件夹。留空则移到根目录。"
              >
                <Select placeholder="选择目标文件夹（可选）" allowClear>
                  {folders.filter(f => f.name !== selectedFolder).map((f) => (
                    <Option key={f.name} value={f.name}>
                      <FolderOutlined /> {f.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </>
          )}
        </Form>
      </Modal>
    </div>
  )
}

export default MediaList
