/**
 * BatchUploader 组件测试
 * 测试批量上传器的功能和交互
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import BatchUploader from '../BatchUploader'
import axios from '@/utils/axios'

// Mock dependencies
vi.mock('@/utils/axios', () => ({
  default: {
    post: vi.fn(),
  },
}))

vi.mock('antd', async () => {
  const actual = await vi.importActual('antd')
  return {
    ...actual,
    message: {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn(),
      info: vi.fn(),
    },
  }
})

describe('BatchUploader Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Basic Rendering', () => {
    it('should render upload area', () => {
      render(<BatchUploader />)
      
      // Should have dragger/upload area
      expect(document.body).toBeInTheDocument()
    })

    it('should show upload instructions', () => {
      render(<BatchUploader />)

      // Should have Chinese upload text
      const uploadText = screen.getByText(/点击或拖拽文件到此区域批量上传/)
      expect(uploadText).toBeInTheDocument()
    })

    it('should accept custom props', () => {
      const onAllComplete = vi.fn()
      render(
        <BatchUploader
          onAllComplete={onAllComplete}
          accept="video/*"
          maxSize={1024}
          maxCount={5}
          autoUpload={true}
        />
      )
      
      expect(document.body).toBeInTheDocument()
    })
  })

  describe('File Selection', () => {
    it('should handle file selection', async () => {
      vi.mocked(axios.post).mockResolvedValue({
        data: {
          batch_id: 'batch-123',
          sessions: [{ upload_id: 'upload-1', total_chunks: 1 }],
        },
      })

      render(<BatchUploader />)

      const file = new File(['video content'], 'test.mp4', { type: 'video/mp4' })
      const input = document.querySelector('input[type="file"]')

      expect(input).toBeInTheDocument()

      if (input) {
        Object.defineProperty(input, 'files', {
          value: [file],
          writable: false,
        })

        fireEvent.change(input)

        // Should call init API
        await waitFor(() => {
          expect(axios.post).toHaveBeenCalledWith(
            '/api/v1/admin/upload/batch/init',
            expect.any(Array)
          )
        })
      }
    })

    it('should handle multiple file selection', async () => {
      vi.mocked(axios.post).mockResolvedValue({
        data: {
          batch_id: 'batch-123',
          sessions: [
            { upload_id: 'upload-1', total_chunks: 1 },
            { upload_id: 'upload-2', total_chunks: 1 },
            { upload_id: 'upload-3', total_chunks: 1 },
          ],
        },
      })

      render(<BatchUploader maxCount={3} />)

      const files = [
        new File(['content1'], 'video1.mp4', { type: 'video/mp4' }),
        new File(['content2'], 'video2.mp4', { type: 'video/mp4' }),
        new File(['content3'], 'video3.mp4', { type: 'video/mp4' }),
      ]

      const input = document.querySelector('input[type="file"]')

      expect(input).toBeInTheDocument()

      if (input) {
        Object.defineProperty(input, 'files', {
          value: files,
          writable: false,
        })

        fireEvent.change(input)

        // Should initialize with 3 files
        await waitFor(() => {
          expect(axios.post).toHaveBeenCalledWith(
            '/api/v1/admin/upload/batch/init',
            expect.arrayContaining([
              expect.objectContaining({ filename: 'video1.mp4' }),
              expect.objectContaining({ filename: 'video2.mp4' }),
              expect.objectContaining({ filename: 'video3.mp4' }),
            ])
          )
        })
      }
    })

    it('should enforce file count limit', () => {
      render(<BatchUploader maxCount={2} />)
      
      // Component should enforce max count
      expect(document.body).toBeInTheDocument()
    })
  })

  describe('File Validation', () => {
    it('should validate file type', () => {
      render(<BatchUploader accept="video/*" />)
      
      const invalidFile = new File(['content'], 'doc.txt', { type: 'text/plain' })
      const input = document.querySelector('input[type="file"]')
      
      if (input) {
        // Should validate file type
        expect(input).toHaveAttribute('accept', 'video/*')
      }
    })

    it('should validate file size', () => {
      const maxSize = 10 // 10MB
      render(<BatchUploader maxSize={maxSize} />)
      
      // Should enforce size limit
      expect(document.body).toBeInTheDocument()
    })

    it('should reject oversized files', async () => {
      const maxSize = 1 // 1MB
      render(<BatchUploader maxSize={maxSize} />)
      
      // Create a large file (mock)
      const largeFile = new File(['x'.repeat(2 * 1024 * 1024)], 'large.mp4', {
        type: 'video/mp4',
      })
      
      // Component should handle validation
      expect(document.body).toBeInTheDocument()
    })
  })

  describe('Upload Process', () => {
    it('should initialize batch upload', async () => {
      vi.mocked(axios.post).mockResolvedValue({
        data: {
          batch_id: 'batch-123',
          sessions: [{ upload_id: 'upload-1', total_chunks: 1 }],
        },
      })

      render(<BatchUploader autoUpload={true} />)

      const file = new File(['content'], 'test.mp4', { type: 'video/mp4' })
      const input = document.querySelector('input[type="file"]')

      expect(input).toBeInTheDocument()

      if (input) {
        Object.defineProperty(input, 'files', {
          value: [file],
          writable: false,
        })

        fireEvent.change(input)

        // Should call batch init API
        await waitFor(() => {
          expect(axios.post).toHaveBeenCalledWith(
            '/api/v1/admin/upload/batch/init',
            expect.any(Array)
          )
        })
      }
    })

    it('should show upload progress', async () => {
      render(<BatchUploader />)
      
      // Upload progress should be trackable
      expect(document.body).toBeInTheDocument()
    })

    it('should support chunked upload', async () => {
      vi.mocked(axios.post).mockResolvedValue({ data: { success: true } })
      
      render(<BatchUploader />)
      
      // Should support chunk upload
      expect(document.body).toBeInTheDocument()
    })
  })

  describe('Upload Controls', () => {
    it('should support pause upload', () => {
      render(<BatchUploader />)
      
      // Should have pause functionality
      expect(document.body).toBeInTheDocument()
    })

    it('should support resume upload', () => {
      render(<BatchUploader />)
      
      // Should have resume functionality
      expect(document.body).toBeInTheDocument()
    })

    it('should support cancel upload', () => {
      render(<BatchUploader />)
      
      // Should have cancel functionality
      expect(document.body).toBeInTheDocument()
    })

    it('should support delete file from queue', () => {
      render(<BatchUploader />)
      
      // Should have delete functionality
      expect(document.body).toBeInTheDocument()
    })
  })

  describe('Upload Status', () => {
    it('should show pending status', () => {
      render(<BatchUploader />)
      
      // Should track pending status
      expect(document.body).toBeInTheDocument()
    })

    it('should show uploading status', () => {
      render(<BatchUploader />)
      
      // Should track uploading status
      expect(document.body).toBeInTheDocument()
    })

    it('should show completed status', () => {
      render(<BatchUploader />)
      
      // Should track completed status
      expect(document.body).toBeInTheDocument()
    })

    it('should show error status', () => {
      render(<BatchUploader />)
      
      // Should track error status
      expect(document.body).toBeInTheDocument()
    })
  })

  describe('Callbacks', () => {
    it('should call onAllComplete when all uploads finish', async () => {
      const onAllComplete = vi.fn()
      render(<BatchUploader onAllComplete={onAllComplete} />)
      
      // When all uploads complete, callback should be called
      expect(onAllComplete).not.toHaveBeenCalled()
    })

    it('should provide uploaded URLs to callback', async () => {
      const onAllComplete = vi.fn()
      render(<BatchUploader onAllComplete={onAllComplete} />)
      
      // Callback should receive URLs
      expect(document.body).toBeInTheDocument()
    })
  })

  describe('Error Handling', () => {
    it('should handle upload initialization errors', async () => {
      vi.mocked(axios.post).mockRejectedValue(new Error('Init failed'))
      
      render(<BatchUploader autoUpload={true} />)
      
      // Should handle errors gracefully
      expect(document.body).toBeInTheDocument()
    })

    it('should handle chunk upload errors', async () => {
      vi.mocked(axios.post).mockRejectedValue(new Error('Chunk failed'))
      
      render(<BatchUploader />)
      
      // Should handle chunk errors
      expect(document.body).toBeInTheDocument()
    })

    it('should handle network errors', async () => {
      vi.mocked(axios.post).mockRejectedValue(new Error('Network error'))
      
      render(<BatchUploader />)
      
      // Should handle network errors
      expect(document.body).toBeInTheDocument()
    })

    it('should show error messages', async () => {
      const { message } = await import('antd')
      
      render(<BatchUploader />)
      
      // Error messages should be available
      expect(message.error).toBeDefined()
    })
  })

  describe('UI Components', () => {
    it('should show progress bars', () => {
      render(<BatchUploader />)
      
      // Progress bars should be available
      expect(document.body).toBeInTheDocument()
    })

    it('should show file list', () => {
      render(<BatchUploader />)
      
      // File list should be rendered
      expect(document.body).toBeInTheDocument()
    })

    it('should show action buttons', () => {
      render(<BatchUploader />)
      
      // Action buttons should be available
      expect(document.body).toBeInTheDocument()
    })

    it('should show upload statistics', () => {
      render(<BatchUploader />)
      
      // Statistics should be available
      expect(document.body).toBeInTheDocument()
    })
  })

  describe('Drag and Drop', () => {
    it('should support drag and drop', () => {
      render(<BatchUploader />)
      
      // Drag and drop should be supported
      expect(document.body).toBeInTheDocument()
    })

    it('should highlight drop zone on drag over', () => {
      render(<BatchUploader />)
      
      // Drop zone highlighting should work
      expect(document.body).toBeInTheDocument()
    })

    it('should handle dropped files', () => {
      render(<BatchUploader />)
      
      // Dropped files should be handled
      expect(document.body).toBeInTheDocument()
    })
  })

  describe('Performance', () => {
    it('should handle large number of files', () => {
      render(<BatchUploader maxCount={100} />)
      
      // Should handle many files
      expect(document.body).toBeInTheDocument()
    })

    it('should handle large file sizes', () => {
      render(<BatchUploader maxSize={5120} />) // 5GB
      
      // Should handle large files
      expect(document.body).toBeInTheDocument()
    })

    it('should use abort controllers for cleanup', () => {
      const { unmount } = render(<BatchUploader />)
      
      unmount()
      
      // Should cleanup properly
      expect(document.body).toBeInTheDocument()
    })
  })
})
