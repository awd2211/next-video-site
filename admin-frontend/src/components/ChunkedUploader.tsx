import { useState } from 'react'
import { Upload, Progress, message, Button } from 'antd'
import { InboxOutlined, PauseCircleOutlined, PlayCircleOutlined } from '@ant-design/icons'
import axios from '@/utils/axios'
import type { UploadFile } from 'antd/es/upload/interface'
import { validateFile, FileValidationPresets, formatFileSize } from '@/utils/fileValidation'

const { Dragger } = Upload

interface ChunkedUploaderProps {
  videoId?: number
  uploadType: 'video' | 'poster' | 'backdrop'
  onUploadComplete?: (url: string) => void
  accept?: string
  maxSize?: number // MB
}

const ChunkedUploader = ({
  videoId,
  uploadType,
  onUploadComplete,
  accept,
  maxSize = 2048, // Default 2GB
}: ChunkedUploaderProps) => {
  const [uploading, setUploading] = useState(false)
  const [paused, setPaused] = useState(false)
  const [progress, setProgress] = useState(0)
  const [uploadId, setUploadId] = useState<string>()
  const [fileList, setFileList] = useState<UploadFile[]>([])
  // currentFile is used in handleUpload and handleCancel
  const [, setCurrentFile] = useState<File | null>(null)

  const CHUNK_SIZE = 5 * 1024 * 1024 // 5MB

  const initUpload = async (file: File) => {
    const response = await axios.post(
      '/api/v1/admin/upload/init-multipart',
      {
        filename: file.name,
        file_size: file.size,
        file_type: file.type,
      }
    )
    return response.data
  }

  const uploadChunk = async (
    uploadId: string,
    chunk: Blob,
    chunkIndex: number,
    totalChunks: number
  ) => {
    const formData = new FormData()
    formData.append('upload_id', uploadId)
    formData.append('chunk_index', chunkIndex.toString())
    formData.append('total_chunks', totalChunks.toString())
    formData.append('file', chunk)

    const response = await axios.post('/api/v1/admin/upload/upload-chunk', formData)
    return response.data
  }

  const completeUpload = async (uploadId: string) => {
    const response = await axios.post(
      '/api/v1/admin/upload/complete-multipart',
      {
        upload_id: uploadId,
        video_id: videoId,
        upload_type: uploadType,
      }
    )
    return response.data
  }

  const cancelUpload = async (uploadId: string) => {
    await axios.delete(`/api/v1/admin/upload/cancel-upload/${uploadId}`)
  }

  const handleUpload = async (file: File) => {
    try {
      setUploading(true)
      setPaused(false)
      setProgress(0)
      setCurrentFile(file)

      // Validate file based on upload type
      let validationConfig = FileValidationPresets.video
      if (uploadType === 'poster' || uploadType === 'backdrop') {
        validationConfig = FileValidationPresets.poster
      }

      // Override with custom maxSize if provided
      if (maxSize) {
        validationConfig = { ...validationConfig, maxSize }
      }

      const validation = validateFile(file, validationConfig)
      if (!validation.valid) {
        message.error(validation.error || '文件验证失败')
        setUploading(false)
        return
      }

      message.info(`开始上传: ${file.name} (${formatFileSize(file.size)})`)

      // Initialize upload
      const initData = await initUpload(file)
      const newUploadId = initData.upload_id
      setUploadId(newUploadId)

      // Calculate chunks
      const totalChunks = Math.ceil(file.size / CHUNK_SIZE)

      // Upload chunks
      for (let i = 0; i < totalChunks; i++) {
        // Check if paused
        while (paused) {
          await new Promise((resolve) => setTimeout(resolve, 100))
        }

        const start = i * CHUNK_SIZE
        const end = Math.min(start + CHUNK_SIZE, file.size)
        const chunk = file.slice(start, end)

        const chunkData = await uploadChunk(newUploadId, chunk, i, totalChunks)
        setProgress(chunkData.progress)
      }

      // Complete upload
      const result = await completeUpload(newUploadId)
      message.success('上传完成')
      setProgress(100)
      onUploadComplete?.(result.url)
      setFileList([])
    } catch (error: any) {
      message.error(error.response?.data?.detail || '上传失败')
      if (uploadId) {
        await cancelUpload(uploadId)
      }
    } finally {
      setUploading(false)
      setPaused(false)
      setUploadId(undefined)
      setCurrentFile(null)
    }
  }

  const handlePauseResume = () => {
    setPaused(!paused)
  }

  const handleCancel = async () => {
    if (uploadId) {
      await cancelUpload(uploadId)
      message.info('上传已取消')
    }
    setUploading(false)
    setPaused(false)
    setProgress(0)
    setUploadId(undefined)
    setCurrentFile(null)
    setFileList([])
  }

  return (
    <div>
      <Dragger
        beforeUpload={(file) => {
          handleUpload(file)
          return false
        }}
        fileList={fileList}
        onChange={({ fileList }) => setFileList(fileList)}
        accept={accept}
        maxCount={1}
        disabled={uploading}
        showUploadList={false}
      >
        <p className="ant-upload-drag-icon">
          <InboxOutlined style={{ fontSize: 48, color: '#0073bb' }} />
        </p>
        <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
        <p className="ant-upload-hint">
          {uploadType === 'video' 
            ? '支持 MP4, AVI, MOV 等格式，单文件最大 2GB'
            : '支持 JPG, PNG 等图片格式'}
        </p>
      </Dragger>

      {uploading && (
        <div style={{ marginTop: 16 }}>
          <Progress percent={Math.round(progress)} status={paused ? 'exception' : 'active'} />
          <div style={{ marginTop: 8 }}>
            <Button
              size="small"
              icon={paused ? <PlayCircleOutlined /> : <PauseCircleOutlined />}
              onClick={handlePauseResume}
              style={{ marginRight: 8 }}
            >
              {paused ? '继续' : '暂停'}
            </Button>
            <Button size="small" danger onClick={handleCancel}>
              取消
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

export default ChunkedUploader
