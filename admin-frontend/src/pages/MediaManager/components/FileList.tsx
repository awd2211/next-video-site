import React, { useState } from 'react'
import {
  Checkbox,
  Empty,
  Spin,
  Pagination,
  Image,
  Dropdown,
  Modal,
  message,
} from 'antd'
import {
  FileImageOutlined,
  VideoCameraOutlined,
  FolderOutlined,
  MoreOutlined,
  DeleteOutlined,
  DownloadOutlined,
  EyeOutlined,
} from '@ant-design/icons'
import type { MenuProps } from 'antd'
import type { MediaItem } from '../types'

interface FileListProps {
  data: MediaItem[]
  loading: boolean
  total: number
  page: number
  pageSize: number
  onPageChange: (page: number) => void
  onPageSizeChange: (size: number) => void
  selectedFiles: number[]
  onSelectChange: (ids: number[]) => void
  onMove: (mediaIds: number[], targetParentId?: number) => void
  onDelete: (mediaIds: number[], permanent: boolean) => void
  onRefresh: () => void
}

const FileList: React.FC<FileListProps> = ({
  data,
  loading,
  total,
  page,
  pageSize,
  onPageChange,
  onPageSizeChange,
  selectedFiles,
  onSelectChange,
  onMove,
  onDelete,
  onRefresh,
}) => {
  const [previewImage, setPreviewImage] = useState<string | null>(null)

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
  }

  // 切换选中状态
  const toggleSelect = (id: number) => {
    if (selectedFiles.includes(id)) {
      onSelectChange(selectedFiles.filter((fid) => fid !== id))
    } else {
      onSelectChange([...selectedFiles, id])
    }
  }

  // 全选/取消全选
  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      onSelectChange(data.map((item) => item.id))
    } else {
      onSelectChange([])
    }
  }

  // 右键菜单
  const getContextMenu = (item: MediaItem): MenuProps['items'] => [
    {
      key: 'preview',
      label: '预览',
      icon: <EyeOutlined />,
      onClick: () => {
        if (item.media_type === 'image') {
          setPreviewImage(item.url)
        } else {
          window.open(item.url, '_blank')
        }
      },
    },
    {
      key: 'download',
      label: '下载',
      icon: <DownloadOutlined />,
      onClick: () => {
        window.open(item.url, '_blank')
      },
    },
    {
      type: 'divider',
    },
    {
      key: 'delete',
      label: '删除',
      icon: <DeleteOutlined />,
      danger: true,
      onClick: () => {
        Modal.confirm({
          title: '确认删除',
          content: `确定要删除 "${item.title}" 吗？`,
          okText: '确认',
          cancelText: '取消',
          onOk: () => onDelete([item.id], false),
        })
      },
    },
  ]

  // 渲染文件图标
  const renderFileIcon = (item: MediaItem) => {
    if (item.is_folder) {
      return <FolderOutlined className="file-card-preview-icon" />
    }

    if (item.media_type === 'image' && item.thumbnail_url) {
      return (
        <img
          src={item.thumbnail_url || item.url}
          alt={item.title}
          style={{ cursor: 'pointer' }}
          onClick={() => setPreviewImage(item.url)}
        />
      )
    }

    if (item.media_type === 'video') {
      return item.thumbnail_url ? (
        <img src={item.thumbnail_url} alt={item.title} />
      ) : (
        <VideoCameraOutlined className="file-card-preview-icon" />
      )
    }

    return <FileImageOutlined className="file-card-preview-icon" />
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <Empty
        description="暂无文件"
        style={{ margin: '100px 0' }}
      />
    )
  }

  return (
    <div className="file-list">
      <div style={{ marginBottom: 16 }}>
        <Checkbox
          checked={selectedFiles.length === data.length && data.length > 0}
          indeterminate={selectedFiles.length > 0 && selectedFiles.length < data.length}
          onChange={(e) => handleSelectAll(e.target.checked)}
        >
          全选 ({selectedFiles.length}/{data.length})
        </Checkbox>
      </div>

      <div className="file-grid">
        {data.map((item) => (
          <Dropdown
            key={item.id}
            menu={{ items: getContextMenu(item) }}
            trigger={['contextMenu']}
          >
            <div
              className={`file-card ${selectedFiles.includes(item.id) ? 'selected' : ''}`}
              onClick={(e) => {
                if (e.ctrlKey || e.metaKey) {
                  toggleSelect(item.id)
                } else {
                  onSelectChange([item.id])
                }
              }}
            >
              <Checkbox
                checked={selectedFiles.includes(item.id)}
                onChange={() => toggleSelect(item.id)}
                onClick={(e) => e.stopPropagation()}
                style={{ position: 'absolute', top: 8, left: 8, zIndex: 1 }}
              />

              <div className="file-card-preview">
                {renderFileIcon(item)}
              </div>

              <div className="file-card-title" title={item.title}>
                {item.title}
              </div>

              <div className="file-card-info">
                <div>{formatFileSize(item.file_size)}</div>
                <div>
                  {item.media_type === 'video' && item.duration
                    ? `${Math.floor(item.duration / 60)}:${(item.duration % 60).toString().padStart(2, '0')}`
                    : item.media_type === 'image' && item.width
                    ? `${item.width}×${item.height}`
                    : ''}
                </div>
              </div>
            </div>
          </Dropdown>
        ))}
      </div>

      <div style={{ marginTop: 24, textAlign: 'center' }}>
        <Pagination
          current={page}
          pageSize={pageSize}
          total={total}
          onChange={onPageChange}
          onShowSizeChange={(_, size) => onPageSizeChange(size)}
          showSizeChanger
          showQuickJumper
          showTotal={(total) => `共 ${total} 项`}
        />
      </div>

      {/* 图片预览 */}
      <Image
        style={{ display: 'none' }}
        preview={{
          visible: !!previewImage,
          src: previewImage || '',
          onVisibleChange: (visible) => {
            if (!visible) setPreviewImage(null)
          },
        }}
      />
    </div>
  )
}

export default FileList
