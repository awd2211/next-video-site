/**
 * 拖拽上传 Hook
 * 支持拖拽文件到页面区域进行上传
 */

import { useState, useCallback, useEffect, RefObject } from 'react'

interface UseDragUploadOptions {
  onDrop: (files: File[]) => void
  accept?: string[] // 接受的文件类型
  maxSize?: number // 最大文件大小（字节）
}

interface UseDragUploadReturn {
  isDragging: boolean
  dragHandlers: {
    onDragEnter: (e: DragEvent) => void
    onDragOver: (e: DragEvent) => void
    onDragLeave: (e: DragEvent) => void
    onDrop: (e: DragEvent) => void
  }
}

export function useDragUpload(
  targetRef: RefObject<HTMLElement>,
  options: UseDragUploadOptions
): UseDragUploadReturn {
  const [isDragging, setIsDragging] = useState(false)
  const { onDrop, accept, maxSize } = options

  // 检查文件是否符合要求
  const validateFile = useCallback(
    (file: File): boolean => {
      // 检查文件类型
      if (accept && accept.length > 0) {
        const fileType = file.type
        const fileExt = file.name.split('.').pop()?.toLowerCase() || ''

        const isAccepted = accept.some((type) => {
          if (type.includes('*')) {
            // 支持通配符，如 image/*
            const prefix = type.split('/')[0] || ''
            return fileType.startsWith(prefix)
          }
          if (type.startsWith('.')) {
            // 支持扩展名，如 .jpg
            return type.slice(1) === fileExt
          }
          return fileType === type
        })

        if (!isAccepted) {
          return false
        }
      }

      // 检查文件大小
      if (maxSize && file.size > maxSize) {
        return false
      }

      return true
    },
    [accept, maxSize]
  )

  const handleDragEnter = useCallback((e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }, [])

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()

    // 只有当离开目标元素时才设置为 false
    if (e.target === targetRef.current) {
      setIsDragging(false)
    }
  }, [targetRef])

  const handleDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault()
      e.stopPropagation()
      setIsDragging(false)

      const files = Array.from(e.dataTransfer?.files || [])

      if (files.length === 0) return

      // 过滤和验证文件
      const validFiles = files.filter(validateFile)

      if (validFiles.length > 0) {
        onDrop(validFiles)
      }

      if (validFiles.length < files.length) {
        console.warn('某些文件不符合要求，已被过滤')
      }
    },
    [onDrop, validateFile]
  )

  useEffect(() => {
    const target = targetRef.current
    if (!target) return

    // 添加事件监听
    target.addEventListener('dragenter', handleDragEnter)
    target.addEventListener('dragover', handleDragOver)
    target.addEventListener('dragleave', handleDragLeave)
    target.addEventListener('drop', handleDrop)

    return () => {
      // 清理事件监听
      target.removeEventListener('dragenter', handleDragEnter)
      target.removeEventListener('dragover', handleDragOver)
      target.removeEventListener('dragleave', handleDragLeave)
      target.removeEventListener('drop', handleDrop)
    }
  }, [targetRef, handleDragEnter, handleDragOver, handleDragLeave, handleDrop])

  return {
    isDragging,
    dragHandlers: {
      onDragEnter: handleDragEnter,
      onDragOver: handleDragOver,
      onDragLeave: handleDragLeave,
      onDrop: handleDrop,
    },
  }
}
