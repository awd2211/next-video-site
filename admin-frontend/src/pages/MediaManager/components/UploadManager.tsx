import React, { useEffect } from 'react'
import { Drawer, Progress, Button, Space, Tag, message } from 'antd'
import {
  CheckCircleOutlined,
} from '@ant-design/icons'
import { ChunkUploader } from '../utils/ChunkUploader'
import type { UploadTask } from '../types'

interface UploadManagerProps {
  visible: boolean
  onClose: () => void
  tasks: UploadTask[]
  onTaskUpdate: (tasks: UploadTask[]) => void
  parentId?: number
  onComplete: () => void
}

const UploadManager: React.FC<UploadManagerProps> = ({
  visible,
  onClose,
  tasks,
  onTaskUpdate,
  parentId,
  onComplete,
}) => {
  // 更新任务状态
  const updateTask = (taskId: string, updates: Partial<UploadTask>) => {
    onTaskUpdate(
      tasks.map((task) =>
        task.id === taskId ? { ...task, ...updates } : task
      )
    )
  }

  // 开始上传单个任务
  const startUpload = async (task: UploadTask) => {
    if (task.status === 'uploading') return

    const startTime = Date.now()
    updateTask(task.id, {
      status: 'uploading',
      progress: 0,
      startTime,
      totalSize: task.file.size,
      uploadedSize: 0,
    })

    const uploader = new ChunkUploader({
      file: task.file,
      parentId,
      title: task.file.name,
      onProgress: (progress) => {
        const now = Date.now()
        const elapsedTime = (now - startTime) / 1000 // 秒
        const uploadedSize = (task.file.size * progress) / 100
        const speed = elapsedTime > 0 ? uploadedSize / elapsedTime : 0
        const remainingSize = task.file.size - uploadedSize
        const estimatedTime = speed > 0 ? remainingSize / speed : 0

        updateTask(task.id, {
          progress,
          uploadedSize,
          speed,
          estimatedTime,
        })
      },
      onComplete: (mediaId, url) => {
        updateTask(task.id, {
          status: 'completed',
          progress: 100,
          mediaId,
          url,
          uploadedSize: task.file.size,
          speed: 0,
          estimatedTime: 0,
        })
        message.success(`${task.file.name} 上传成功`)
        onComplete()
      },
      onError: (error) => {
        updateTask(task.id, {
          status: 'error',
          error: error.message,
        })
        message.error(`${task.file.name} 上传失败: ${error.message}`)
      },
    })

    try {
      await uploader.start()
    } catch (error) {
      // 错误已在 onError 回调中处理
    }
  }

  // 自动开始上传 pending 状态的任务
  useEffect(() => {
    const pendingTasks = tasks.filter((task) => task.status === 'pending')
    if (pendingTasks.length > 0 && visible) {
      // 限制并发数量，每次最多3个
      const concurrentLimit = 3
      const uploadingCount = tasks.filter((t) => t.status === 'uploading').length

      pendingTasks
        .slice(0, Math.max(0, concurrentLimit - uploadingCount))
        .forEach((task) => {
          startUpload(task)
        })
    }
  }, [tasks, visible])

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
  }

  // 格式化速度
  const formatSpeed = (bytesPerSecond: number): string => {
    return `${formatFileSize(bytesPerSecond)}/s`
  }

  // 格式化时间
  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${Math.round(seconds)}秒`
    if (seconds < 3600) return `${Math.round(seconds / 60)}分钟`
    return `${Math.round(seconds / 3600)}小时`
  }

  // 获取状态标签
  const getStatusTag = (status: UploadTask['status']) => {
    switch (status) {
      case 'pending':
        return <Tag color="default">等待中</Tag>
      case 'uploading':
        return <Tag color="processing">上传中</Tag>
      case 'completed':
        return <Tag color="success" icon={<CheckCircleOutlined />}>已完成</Tag>
      case 'error':
        return <Tag color="error">失败</Tag>
      case 'paused':
        return <Tag color="warning">已暂停</Tag>
      default:
        return null
    }
  }

  // 统计信息
  const stats = {
    total: tasks.length,
    completed: tasks.filter((t) => t.status === 'completed').length,
    uploading: tasks.filter((t) => t.status === 'uploading').length,
    error: tasks.filter((t) => t.status === 'error').length,
  }

  return (
    <Drawer
      title="上传管理"
      placement="right"
      width={500}
      open={visible}
      onClose={onClose}
      extra={
        <Space>
          <span style={{ fontSize: 12, color: '#8c8c8c' }}>
            {stats.completed}/{stats.total} 完成
            {stats.uploading > 0 && ` · ${stats.uploading} 上传中`}
            {stats.error > 0 && ` · ${stats.error} 失败`}
          </span>
        </Space>
      }
    >
      <div className="upload-manager">
        {tasks.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 0', color: '#8c8c8c' }}>
            暂无上传任务
          </div>
        ) : (
          tasks.map((task) => (
            <div key={task.id} className="upload-task">
              <div className="upload-task-header">
                <div className="upload-task-name" title={task.file.name}>
                  {task.file.name}
                </div>
                {getStatusTag(task.status)}
              </div>

              {task.status === 'uploading' && (
                <div className="upload-task-progress">
                  <Progress
                    percent={Math.round(task.progress)}
                    status="active"
                    strokeColor={{
                      '0%': '#108ee9',
                      '100%': '#87d068',
                    }}
                  />
                </div>
              )}

              {task.status === 'completed' && (
                <div className="upload-task-progress">
                  <Progress percent={100} status="success" />
                </div>
              )}

              {task.status === 'error' && (
                <div className="upload-task-progress">
                  <Progress percent={task.progress} status="exception" />
                  <div style={{ color: '#ff4d4f', fontSize: 12, marginTop: 4 }}>
                    {task.error}
                  </div>
                </div>
              )}

              <div className="upload-task-info">
                <span>{formatFileSize(task.file.size)}</span>
                {task.status === 'uploading' && task.speed && (
                  <>
                    <span>·</span>
                    <span style={{ color: '#52c41a' }}>{formatSpeed(task.speed)}</span>
                    {task.estimatedTime && task.estimatedTime > 0 && (
                      <>
                        <span>·</span>
                        <span style={{ color: '#1890ff' }}>剩余 {formatTime(task.estimatedTime)}</span>
                      </>
                    )}
                  </>
                )}
                {task.status !== 'uploading' && <span>{task.file.type}</span>}
              </div>

              {task.status === 'error' && (
                <div style={{ marginTop: 8 }}>
                  <Button
                    size="small"
                    type="primary"
                    onClick={() => startUpload(task)}
                  >
                    重试
                  </Button>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </Drawer>
  )
}

export default UploadManager
