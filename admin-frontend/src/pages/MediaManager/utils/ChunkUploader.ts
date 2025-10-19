/**
 * 分块上传工具类
 * 支持大文件分块上传、断点续传、进度追踪
 */

import axios from '@/utils/axios'

export interface UploadOptions {
  file: File
  parentId?: number
  title?: string
  description?: string
  tags?: string
  chunkSize?: number // 默认 5MB
  onProgress?: (progress: number) => void
  onChunkComplete?: (chunkIndex: number, total: number) => void
  onComplete?: (mediaId: number, url: string) => void
  onError?: (error: Error) => void
}

export interface UploadSession {
  upload_id: string  // 后端返回的是 snake_case
  chunk_size: number
  total_chunks: number
  expires_at: string
}

export class ChunkUploader {
  private uploadId: string | null = null
  private file: File
  private options: UploadOptions
  private totalChunks: number = 0
  private uploadedChunks: Set<number> = new Set()
  private isUploading: boolean = false
  private isPaused: boolean = false

  constructor(options: UploadOptions) {
    this.file = options.file
    this.options = {
      chunkSize: 5 * 1024 * 1024, // 默认 5MB
      ...options,
    }
  }

  /**
   * 开始上传
   */
  async start(): Promise<void> {
    if (this.isUploading) {
      throw new Error('上传已在进行中')
    }

    this.isUploading = true
    this.isPaused = false

    try {
      // 1. 初始化上传会话
      await this.initSession()

      // 2. 上传所有分块
      await this.uploadChunks()

      // 3. 完成上传
      await this.complete()
    } catch (error) {
      this.isUploading = false
      this.options.onError?.(error as Error)
      throw error
    }
  }

  /**
   * 暂停上传
   */
  pause(): void {
    this.isPaused = true
  }

  /**
   * 恢复上传
   */
  async resume(): Promise<void> {
    if (!this.uploadId) {
      throw new Error('没有可恢复的上传会话')
    }

    this.isPaused = false
    await this.uploadChunks()
    await this.complete()
  }

  /**
   * 取消上传
   */
  cancel(): void {
    this.isPaused = true
    this.isUploading = false
    this.uploadId = null
  }

  /**
   * 初始化上传会话
   */
  private async initSession(): Promise<void> {
    const response = await axios.post('/api/v1/admin/media/upload/init', null, {
      params: {
        filename: this.file.name,
        file_size: this.file.size,
        mime_type: this.file.type,
        title: this.options.title || this.file.name,
        parent_id: this.options.parentId,
        description: this.options.description,
        tags: this.options.tags,
        chunk_size: this.options.chunkSize,
      },
    })

    const session: UploadSession = response.data
    this.uploadId = session.upload_id
    this.totalChunks = session.total_chunks

    // 尝试从 localStorage 恢复进度
    const savedProgress = this.loadProgress()
    if (savedProgress) {
      this.uploadedChunks = new Set(savedProgress)
    }
  }

  /**
   * 上传所有分块
   */
  private async uploadChunks(): Promise<void> {
    const chunkSize = this.options.chunkSize!

    for (let i = 0; i < this.totalChunks; i++) {
      if (this.isPaused) {
        this.saveProgress()
        throw new Error('上传已暂停')
      }

      // 跳过已上传的分块
      if (this.uploadedChunks.has(i)) {
        continue
      }

      const start = i * chunkSize
      const end = Math.min(start + chunkSize, this.file.size)
      const chunk = this.file.slice(start, end)

      await this.uploadChunk(i, chunk)

      this.uploadedChunks.add(i)
      this.saveProgress()

      // 触发进度回调
      const progress = (this.uploadedChunks.size / this.totalChunks) * 100
      this.options.onProgress?.(progress)
      this.options.onChunkComplete?.(i, this.totalChunks)
    }
  }

  /**
   * 上传单个分块
   */
  private async uploadChunk(index: number, chunk: Blob): Promise<void> {
    const formData = new FormData()
    formData.append('chunk', chunk)

    await axios.post('/api/v1/admin/media/upload/chunk', formData, {
      params: {
        upload_id: this.uploadId,
        chunk_index: index,
      },
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  }

  /**
   * 完成上传
   */
  private async complete(): Promise<void> {
    const response = await axios.post('/api/v1/admin/media/upload/complete', null, {
      params: {
        upload_id: this.uploadId,
      },
    })

    this.isUploading = false
    this.clearProgress()

    const { media_id, url } = response.data
    this.options.onComplete?.(media_id, url)
  }

  /**
   * 保存上传进度到 localStorage
   */
  private saveProgress(): void {
    if (!this.uploadId) return

    const progress = Array.from(this.uploadedChunks)
    localStorage.setItem(`upload_progress_${this.uploadId}`, JSON.stringify(progress))
  }

  /**
   * 从 localStorage 加载进度
   */
  private loadProgress(): number[] | null {
    if (!this.uploadId) return null

    const saved = localStorage.getItem(`upload_progress_${this.uploadId}`)
    return saved ? JSON.parse(saved) : null
  }

  /**
   * 清除保存的进度
   */
  private clearProgress(): void {
    if (!this.uploadId) return
    localStorage.removeItem(`upload_progress_${this.uploadId}`)
  }

  /**
   * 获取当前进度
   */
  getProgress(): number {
    if (this.totalChunks === 0) return 0
    return (this.uploadedChunks.size / this.totalChunks) * 100
  }
}

/**
 * 简化的上传函数（单个文件）
 */
export async function uploadFile(options: UploadOptions): Promise<void> {
  const uploader = new ChunkUploader(options)
  await uploader.start()
}

/**
 * 批量上传文件
 */
export async function uploadFiles(
  files: File[],
  options: Omit<UploadOptions, 'file'>,
  onFileProgress?: (file: File, progress: number) => void
): Promise<void> {
  for (const file of files) {
    const uploader = new ChunkUploader({
      ...options,
      file,
      onProgress: (progress) => onFileProgress?.(file, progress),
    })
    await uploader.start()
  }
}
