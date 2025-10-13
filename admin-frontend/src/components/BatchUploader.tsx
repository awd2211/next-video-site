import { useState, useRef } from 'react'
import {
  Upload,
  Progress,
  message,
  Button,
  List,
  Space,
  Tag,
  Modal,
  Tooltip,
} from 'antd'
import {
  InboxOutlined,
  PauseCircleOutlined,
  PlayCircleOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  CloudUploadOutlined,
} from '@ant-design/icons'
import axios from '@/utils/axios'
import type { UploadFile } from 'antd/es/upload/interface'

const { Dragger } = Upload

interface BatchUploaderProps {
  onAllComplete?: (urls: string[]) => void
  accept?: string
  maxSize?: number // MB per file
  maxCount?: number // Maximum number of files
  autoUpload?: boolean // Auto upload after selecting files
}

interface UploadItem {
  file: File
  uploadId?: string
  progress: number
  status: 'pending' | 'uploading' | 'paused' | 'completed' | 'error'
  url?: string
  error?: string
  totalChunks: number
  uploadedChunks: number
}

const BatchUploader = ({
  onAllComplete,
  accept = 'video/*',
  maxSize = 2048, // 2GB default
  maxCount = 10,
  autoUpload = false,
}: BatchUploaderProps) => {
  const [uploadItems, setUploadItems] = useState<UploadItem[]>([])
  const [batchId, setBatchId] = useState<string>()
  const [uploading, setUploading] = useState(false)
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const abortControllersRef = useRef<Map<string, AbortController>>(new Map())

  const CHUNK_SIZE = 5 * 1024 * 1024 // 5MB

  /**
   * Initialize batch upload
   */
  const initBatchUpload = async (files: File[]) => {
    const filesInfo = files.map((file) => ({
      filename: file.name,
      file_size: file.size,
      mime_type: file.type,
      title: file.name.split('.')[0],
    }))

    const response = await axios.post('/api/v1/admin/upload/batch/init', filesInfo)
    return response.data
  }

  /**
   * Upload single chunk
   */
  const uploadChunk = async (
    uploadId: string,
    chunk: Blob,
    chunkIndex: number,
    abortController: AbortController
  ) => {
    const formData = new FormData()
    formData.append('upload_id', uploadId)
    formData.append('chunk_index', chunkIndex.toString())
    formData.append('file', chunk)

    const response = await axios.post('/api/v1/admin/upload/batch/chunk', formData, {
      signal: abortController.signal,
    })
    return response.data
  }

  /**
   * Complete upload for single file
   */
  const completeUpload = async (uploadId: string) => {
    const response = await axios.post(`/api/v1/admin/upload/batch/complete/${uploadId}`)
    return response.data
  }

  /**
   * Cancel upload for single file
   */
  const cancelUpload = async (uploadId: string) => {
    await axios.delete(`/api/v1/admin/upload/batch/cancel/${uploadId}`)
  }

  /**
   * Handle file selection
   */
  const handleFileSelect = async (files: File[]) => {
    // Check file count
    if (files.length > maxCount) {
      message.error(`最多只能上传 ${maxCount} 个文件`)
      return
    }

    // Check file sizes
    const maxSizeBytes = maxSize * 1024 * 1024
    for (const file of files) {
      if (file.size > maxSizeBytes) {
        message.error(`文件 ${file.name} 超过最大大小 ${maxSize}MB`)
        return
      }
    }

    try {
      // Initialize batch upload
      const batchData = await initBatchUpload(files)
      setBatchId(batchData.batch_id)

      // Create upload items
      const items: UploadItem[] = files.map((file, index) => ({
        file,
        uploadId: batchData.sessions[index].upload_id,
        progress: 0,
        status: 'pending',
        totalChunks: batchData.sessions[index].total_chunks,
        uploadedChunks: 0,
      }))

      setUploadItems(items)
      message.success(`已添加 ${files.length} 个文件`)

      // Auto upload if enabled
      if (autoUpload) {
        handleStartAll(items)
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '初始化上传失败')
    }
  }

  /**
   * Upload single file
   */
  const uploadFile = async (item: UploadItem, index: number) => {
    if (!item.uploadId) return

    const abortController = new AbortController()
    abortControllersRef.current.set(item.uploadId, abortController)

    try {
      // Update status to uploading
      updateItemStatus(index, { status: 'uploading' })

      // Upload chunks
      for (let i = 0; i < item.totalChunks; i++) {
        // Check if paused
        if (uploadItems[index]?.status === 'paused') {
          break
        }

        const start = i * CHUNK_SIZE
        const end = Math.min(start + CHUNK_SIZE, item.file.size)
        const chunk = item.file.slice(start, end)

        const chunkData = await uploadChunk(item.uploadId, chunk, i, abortController)

        // Update progress
        updateItemStatus(index, {
          progress: chunkData.progress,
          uploadedChunks: chunkData.uploaded_chunks,
        })
      }

      // Complete upload
      const result = await completeUpload(item.uploadId)

      // Update status to completed
      updateItemStatus(index, {
        status: 'completed',
        progress: 100,
        url: result.url,
      })

      abortControllersRef.current.delete(item.uploadId)
    } catch (error: any) {
      if (error.name === 'CanceledError') {
        // Paused by user
        return
      }

      updateItemStatus(index, {
        status: 'error',
        error: error.response?.data?.detail || '上传失败',
      })
      abortControllersRef.current.delete(item.uploadId!)
    }
  }

  /**
   * Update item status
   */
  const updateItemStatus = (index: number, updates: Partial<UploadItem>) => {
    setUploadItems((prev) =>
      prev.map((item, i) => (i === index ? { ...item, ...updates } : item))
    )
  }

  /**
   * Start uploading all pending files
   */
  const handleStartAll = async (items?: UploadItem[]) => {
    setUploading(true)
    const itemsToUpload = items || uploadItems

    // Upload files concurrently (max 3 at a time)
    const concurrency = 3
    const queue = itemsToUpload
      .map((item, index) => ({ item, index }))
      .filter(({ item }) => item.status === 'pending' || item.status === 'paused')

    for (let i = 0; i < queue.length; i += concurrency) {
      const batch = queue.slice(i, i + concurrency)
      await Promise.all(batch.map(({ item, index }) => uploadFile(item, index)))
    }

    setUploading(false)

    // Check if all completed
    const completedUrls = uploadItems
      .filter((item) => item.status === 'completed' && item.url)
      .map((item) => item.url!)

    if (completedUrls.length === uploadItems.length) {
      message.success('所有文件上传完成')
      onAllComplete?.(completedUrls)
    }
  }

  /**
   * Pause single upload
   */
  const handlePause = (index: number) => {
    const item = uploadItems[index]
    if (item.uploadId) {
      abortControllersRef.current.get(item.uploadId)?.abort()
      updateItemStatus(index, { status: 'paused' })
    }
  }

  /**
   * Resume single upload
   */
  const handleResume = (index: number) => {
    const item = uploadItems[index]
    updateItemStatus(index, { status: 'pending' })
    uploadFile(item, index)
  }

  /**
   * Remove single item
   */
  const handleRemove = async (index: number) => {
    const item = uploadItems[index]

    if (item.uploadId && item.status !== 'completed') {
      try {
        await cancelUpload(item.uploadId)
      } catch (error) {
        // Ignore error
      }
    }

    setUploadItems((prev) => prev.filter((_, i) => i !== index))
  }

  /**
   * Clear all completed items
   */
  const handleClearCompleted = () => {
    setUploadItems((prev) => prev.filter((item) => item.status !== 'completed'))
  }

  /**
   * Get status color
   */
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success'
      case 'uploading':
        return 'processing'
      case 'paused':
        return 'warning'
      case 'error':
        return 'error'
      default:
        return 'default'
    }
  }

  /**
   * Get status text
   */
  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return '已完成'
      case 'uploading':
        return '上传中'
      case 'paused':
        return '已暂停'
      case 'error':
        return '失败'
      default:
        return '等待中'
    }
  }

  return (
    <div>
      {/* Upload Area */}
      {uploadItems.length === 0 && (
        <Dragger
          beforeUpload={() => false}
          onChange={({ fileList }) => {
            const files = fileList.map((f) => f.originFileObj as File).filter(Boolean)
            if (files.length > 0) {
              handleFileSelect(files)
            }
            setFileList([])
          }}
          fileList={fileList}
          accept={accept}
          multiple
          maxCount={maxCount}
          disabled={uploading}
          showUploadList={false}
        >
          <p className="ant-upload-drag-icon">
            <InboxOutlined style={{ fontSize: 48, color: '#0073bb' }} />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域批量上传</p>
          <p className="ant-upload-hint">
            支持批量上传，单个文件最大 {maxSize}MB，最多 {maxCount} 个文件
          </p>
        </Dragger>
      )}

      {/* Upload List */}
      {uploadItems.length > 0 && (
        <div>
          <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
            <Space>
              <Button
                type="primary"
                icon={<CloudUploadOutlined />}
                onClick={() => handleStartAll()}
                disabled={
                  uploading ||
                  uploadItems.every(
                    (item) => item.status === 'completed' || item.status === 'uploading'
                  )
                }
              >
                开始全部上传
              </Button>
              <Button onClick={handleClearCompleted}>清除已完成</Button>
            </Space>

            <Space>
              <Tag color="blue">
                总计: {uploadItems.length} | 完成:{' '}
                {uploadItems.filter((item) => item.status === 'completed').length}
              </Tag>
            </Space>
          </div>

          <List
            dataSource={uploadItems}
            renderItem={(item, index) => (
              <List.Item
                key={index}
                actions={[
                  item.status === 'uploading' ? (
                    <Tooltip title="暂停">
                      <Button
                        type="text"
                        size="small"
                        icon={<PauseCircleOutlined />}
                        onClick={() => handlePause(index)}
                      />
                    </Tooltip>
                  ) : item.status === 'paused' ? (
                    <Tooltip title="继续">
                      <Button
                        type="text"
                        size="small"
                        icon={<PlayCircleOutlined />}
                        onClick={() => handleResume(index)}
                      />
                    </Tooltip>
                  ) : null,
                  item.status !== 'completed' && (
                    <Tooltip title="删除">
                      <Button
                        type="text"
                        size="small"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={() => handleRemove(index)}
                      />
                    </Tooltip>
                  ),
                ]}
              >
                <List.Item.Meta
                  avatar={
                    item.status === 'completed' ? (
                      <CheckCircleOutlined style={{ fontSize: 24, color: '#52c41a' }} />
                    ) : item.status === 'error' ? (
                      <CloseCircleOutlined style={{ fontSize: 24, color: '#ff4d4f' }} />
                    ) : (
                      <CloudUploadOutlined style={{ fontSize: 24, color: '#1890ff' }} />
                    )
                  }
                  title={
                    <Space>
                      <span>{item.file.name}</span>
                      <Tag color={getStatusColor(item.status)}>{getStatusText(item.status)}</Tag>
                    </Space>
                  }
                  description={
                    <div>
                      <div style={{ marginBottom: 8 }}>
                        大小: {(item.file.size / 1024 / 1024).toFixed(2)} MB
                        {item.error && (
                          <span style={{ color: '#ff4d4f', marginLeft: 16 }}>
                            错误: {item.error}
                          </span>
                        )}
                      </div>
                      {item.status !== 'pending' && item.status !== 'error' && (
                        <Progress
                          percent={Math.round(item.progress)}
                          status={
                            item.status === 'completed'
                              ? 'success'
                              : item.status === 'paused'
                              ? 'exception'
                              : 'active'
                          }
                          size="small"
                        />
                      )}
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        </div>
      )}
    </div>
  )
}

export default BatchUploader
