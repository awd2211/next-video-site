import React, { useState } from 'react'
import {
  Checkbox,
  Spin,
  Pagination,
  Dropdown,
  Modal,
  Table,
  Input,
  message,
} from 'antd'
import EmptyState from './EmptyState'
import ImagePreview from './ImagePreview'
import VideoPlayer from './VideoPlayer'
import type { ColumnsType } from 'antd/es/table'
import {
  FileImageOutlined,
  VideoCameraOutlined,
  FolderOutlined,
  MoreOutlined,
  DeleteOutlined,
  DownloadOutlined,
  EyeOutlined,
  EditOutlined,
  DragOutlined,
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
  viewMode: 'grid' | 'list'
  sortBy: 'name' | 'size' | 'date'
  sortOrder: 'asc' | 'desc'
  onFolderOpen: (folderId: number) => void
  onRename: (mediaId: number, newTitle: string) => void
  onOpenMoveModal: () => void
  onUpload: () => void
  onCreateFolder: () => void
  searchText?: string
  currentFolderId?: number
  mediaTypeFilter?: 'image' | 'video'
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
  onDelete,
  viewMode,
  onFolderOpen,
  onRename,
  onOpenMoveModal,
  onUpload,
  onCreateFolder,
  searchText,
  currentFolderId,
  mediaTypeFilter,
}) => {
  const [renameModalVisible, setRenameModalVisible] = useState(false)
  const [renamingItem, setRenamingItem] = useState<MediaItem | null>(null)
  const [newTitle, setNewTitle] = useState('')

  // 图片预览状态
  const [imagePreviewVisible, setImagePreviewVisible] = useState(false)
  const [currentImageIndex, setCurrentImageIndex] = useState(0)
  const imageFiles = data.filter((item) => !item.is_folder && item.media_type === 'image')

  // 视频播放状态
  const [videoPlayerVisible, setVideoPlayerVisible] = useState(false)
  const [currentVideo, setCurrentVideo] = useState<MediaItem | null>(null)

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

  // 打开图片预览
  const openImagePreview = (item: MediaItem) => {
    const index = imageFiles.findIndex((img) => img.id === item.id)
    if (index !== -1) {
      setCurrentImageIndex(index)
      setImagePreviewVisible(true)
    }
  }

  // 打开视频播放器
  const openVideoPlayer = (item: MediaItem) => {
    setCurrentVideo(item)
    setVideoPlayerVisible(true)
  }

  // 处理双击 - 文件夹打开，文件预览
  const handleDoubleClick = (item: MediaItem) => {
    if (item.is_folder) {
      onFolderOpen(item.id)
    } else {
      // 文件预览
      if (item.media_type === 'image') {
        openImagePreview(item)
      } else if (item.media_type === 'video') {
        openVideoPlayer(item)
      } else {
        window.open(item.url, '_blank')
      }
    }
  }

  // 打开重命名对话框
  const handleRename = (item: MediaItem) => {
    setRenamingItem(item)
    setNewTitle(item.title)
    setRenameModalVisible(true)
  }

  // 确认重命名
  const confirmRename = () => {
    if (!renamingItem) return
    if (!newTitle.trim()) {
      message.error('名称不能为空')
      return
    }
    onRename(renamingItem.id, newTitle.trim())
    setRenameModalVisible(false)
    setRenamingItem(null)
    setNewTitle('')
  }

  // 右键菜单
  const getContextMenu = (item: MediaItem): MenuProps['items'] => {
    const menu: MenuProps['items'] = []

    // 文件夹：打开
    if (item.is_folder) {
      menu.push({
        key: 'open',
        label: '打开',
        icon: <FolderOutlined />,
        onClick: () => onFolderOpen(item.id),
      })
    } else {
      // 文件：预览和下载
      menu.push({
        key: 'preview',
        label: '预览',
        icon: <EyeOutlined />,
        onClick: () => {
          if (item.media_type === 'image') {
            openImagePreview(item)
          } else if (item.media_type === 'video') {
            openVideoPlayer(item)
          } else {
            window.open(item.url, '_blank')
          }
        },
      })
      menu.push({
        key: 'download',
        label: '下载',
        icon: <DownloadOutlined />,
        onClick: () => {
          window.open(item.url, '_blank')
        },
      })
    }

    // 通用操作
    menu.push(
      { type: 'divider' },
      {
        key: 'rename',
        label: '重命名',
        icon: <EditOutlined />,
        onClick: () => handleRename(item),
      },
      {
        key: 'move',
        label: '移动到',
        icon: <DragOutlined />,
        onClick: () => {
          // 选中当前项并打开移动Modal
          onSelectChange([item.id])
          onOpenMoveModal()
        },
      },
      { type: 'divider' },
      {
        key: 'delete',
        label: '删除',
        icon: <DeleteOutlined />,
        danger: true,
        onClick: () => {
          Modal.confirm({
            title: '确认删除',
            content: `确定要删除 "${item.title}" 吗？${item.is_folder ? ' 文件夹中的所有内容也会被删除。' : ''}`,
            okText: '确认',
            cancelText: '取消',
            onOk: () => onDelete([item.id], false),
          })
        },
      }
    )

    return menu
  }

  // 渲染文件图标
  const renderFileIcon = (item: MediaItem, isListView = false) => {
    const iconStyle = isListView ? { fontSize: 24 } : {}

    if (item.is_folder) {
      return <FolderOutlined className="file-card-preview-icon" style={iconStyle} />
    }

    if (item.media_type === 'image' && item.thumbnail_url) {
      if (isListView) {
        return <img src={item.thumbnail_url || item.url} alt={item.title} style={{ width: 32, height: 32, objectFit: 'cover', borderRadius: 4 }} />
      }
      return (
        <img
          src={item.thumbnail_url || item.url}
          alt={item.title}
          style={{ cursor: 'pointer' }}
          onClick={() => openImagePreview(item)}
        />
      )
    }

    if (item.media_type === 'video') {
      if (isListView && item.thumbnail_url) {
        return <img src={item.thumbnail_url} alt={item.title} style={{ width: 32, height: 32, objectFit: 'cover', borderRadius: 4 }} />
      }
      return item.thumbnail_url ? (
        <img src={item.thumbnail_url} alt={item.title} />
      ) : (
        <VideoCameraOutlined className="file-card-preview-icon" style={iconStyle} />
      )
    }

    return <FileImageOutlined className="file-card-preview-icon" style={iconStyle} />
  }

  // 格式化日期
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Table列定义（列表视图）
  const columns: ColumnsType<MediaItem> = [
    {
      title: '名称',
      dataIndex: 'title',
      key: 'title',
      render: (title, record) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {renderFileIcon(record, true)}
          <span>{title}</span>
        </div>
      ),
    },
    {
      title: '大小',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 120,
      render: (size) => formatFileSize(size),
    },
    {
      title: '类型',
      dataIndex: 'media_type',
      key: 'media_type',
      width: 100,
      render: (type, record) => {
        if (record.is_folder) return '文件夹'
        return type === 'image' ? '图片' : type === 'video' ? '视频' : '文件'
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date) => formatDate(date),
    },
    {
      title: '操作',
      key: 'actions',
      width: 80,
      render: (_, record) => (
        <Dropdown menu={{ items: getContextMenu(record) }} trigger={['click']}>
          <MoreOutlined style={{ cursor: 'pointer', fontSize: 18 }} />
        </Dropdown>
      ),
    },
  ]

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    )
  }

  if (data.length === 0) {
    // 确定空状态类型
    let emptyType: 'root' | 'folder' | 'search' = 'root'
    if (searchText && searchText.trim()) {
      emptyType = 'search'
    } else if (currentFolderId) {
      emptyType = 'folder'
    }

    return (
      <EmptyState
        type={emptyType}
        onUpload={onUpload}
        onCreateFolder={onCreateFolder}
        searchText={searchText}
      />
    )
  }

  // 列表视图
  if (viewMode === 'list') {
    return (
      <div className="file-list">
        <Table
          rowSelection={{
            selectedRowKeys: selectedFiles,
            onChange: (selectedRowKeys) => onSelectChange(selectedRowKeys as number[]),
          }}
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          onRow={(record) => ({
            onDoubleClick: () => handleDoubleClick(record),
            style: { cursor: 'pointer' },
          })}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            onChange: onPageChange,
            onShowSizeChange: (_, size) => onPageSizeChange(size),
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 项`,
          }}
        />

        {/* 图片预览 */}
        <ImagePreview
          visible={imagePreviewVisible}
          current={currentImageIndex}
          images={imageFiles}
          onClose={() => setImagePreviewVisible(false)}
          onChange={setCurrentImageIndex}
        />

        {/* 视频播放器 */}
        <VideoPlayer
          visible={videoPlayerVisible}
          video={currentVideo}
          onClose={() => {
            setVideoPlayerVisible(false)
            setCurrentVideo(null)
          }}
        />
      </div>
    )
  }

  // 网格视图
  return (
    <div className="file-list">
      <div style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 12 }}>
        <Checkbox
          checked={selectedFiles.length === data.length && data.length > 0}
          indeterminate={selectedFiles.length > 0 && selectedFiles.length < data.length}
          onChange={(e) => handleSelectAll(e.target.checked)}
        >
          全选 ({selectedFiles.length}/{data.length})
        </Checkbox>

        {/* 筛选器提示 */}
        {mediaTypeFilter && (
          <span style={{
            padding: '2px 8px',
            borderRadius: 4,
            background: '#e6f7ff',
            color: '#1890ff',
            fontSize: 12,
            display: 'inline-flex',
            alignItems: 'center',
            gap: 4,
          }}>
            {mediaTypeFilter === 'image' ? '仅显示图片' : '仅显示视频'}
          </span>
        )}
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
              onDoubleClick={() => handleDoubleClick(item)}
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
      <ImagePreview
        visible={imagePreviewVisible}
        current={currentImageIndex}
        images={imageFiles}
        onClose={() => setImagePreviewVisible(false)}
        onChange={setCurrentImageIndex}
      />

      {/* 视频播放器 */}
      <VideoPlayer
        visible={videoPlayerVisible}
        video={currentVideo}
        onClose={() => {
          setVideoPlayerVisible(false)
          setCurrentVideo(null)
        }}
      />

      {/* 重命名对话框 */}
      <Modal
        title="重命名"
        open={renameModalVisible}
        onOk={confirmRename}
        onCancel={() => {
          setRenameModalVisible(false)
          setRenamingItem(null)
          setNewTitle('')
        }}
        okText="确认"
        cancelText="取消"
      >
        <Input
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          placeholder="请输入新名称"
          onPressEnter={confirmRename}
          autoFocus
        />
      </Modal>
    </div>
  )
}

export default FileList
