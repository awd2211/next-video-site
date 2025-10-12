/**
 * MediaManager - Mega 风格文件管理器
 * 双面板布局：左侧文件夹树，右侧文件列表
 * 支持拖拽上传、面包屑导航、视图切换、排序
 */

import React, { useState, useEffect, useRef } from 'react'
import { Layout, message } from 'antd'
import { CloudUploadOutlined } from '@ant-design/icons'
import JSZip from 'jszip'
import FolderTree from './components/FolderTree'
import FileList from './components/FileList'
import Toolbar from './components/Toolbar'
import UploadManager from './components/UploadManager'
import Breadcrumb from './components/Breadcrumb'
import MoveModal from './components/MoveModal'
import KeyboardHelp from './components/KeyboardHelp'
import { useDragUpload } from './hooks/useDragUpload'
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts'
import axios from '@/utils/axios'
import type { FolderNode, MediaItem, UploadTask } from './types'
import './styles.css'

const { Sider, Content } = Layout

const MediaManager: React.FC = () => {
  // 文件夹树数据
  const [folderTree, setFolderTree] = useState<FolderNode[]>([])
  const [selectedFolderId, setSelectedFolderId] = useState<number | undefined>(undefined)

  // 文件列表数据
  const [fileList, setFileList] = useState<MediaItem[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(50)

  // 上传队列
  const [uploadTasks, setUploadTasks] = useState<UploadTask[]>([])
  const [uploadDrawerVisible, setUploadDrawerVisible] = useState(false)

  // 选中的文件
  const [selectedFiles, setSelectedFiles] = useState<number[]>([])

  // 移动文件Modal
  const [moveModalVisible, setMoveModalVisible] = useState(false)

  // 计算选中文件的总大小
  const selectedFilesSize = fileList
    .filter(item => selectedFiles.includes(item.id))
    .reduce((total, item) => total + (item.file_size || 0), 0)

  // 搜索
  const [searchText, setSearchText] = useState('')

  // 媒体类型筛选
  const [mediaTypeFilter, setMediaTypeFilter] = useState<'image' | 'video' | undefined>(undefined)

  // 视图模式和排序
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [sortBy, setSortBy] = useState<'name' | 'size' | 'date'>('name')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')

  // 面包屑路径
  const [breadcrumbPath, setBreadcrumbPath] = useState<{ id?: number; title: string }[]>([])

  // 拖拽上传
  const dropZoneRef = useRef<HTMLDivElement>(null)
  const { isDragging } = useDragUpload(dropZoneRef, {
    onDrop: handleAddUploadTask,
    accept: ['image/*', 'video/*'],
    maxSize: 5 * 1024 * 1024 * 1024, // 5GB
  })

  // 构建面包屑路径
  const buildBreadcrumbPath = (folderId?: number, tree: FolderNode[] = folderTree): { id?: number; title: string }[] => {
    if (!folderId) return []

    // 递归查找路径
    const findPath = (nodes: FolderNode[], targetId: number, path: { id: number; title: string }[] = []): { id: number; title: string }[] | null => {
      for (const node of nodes) {
        if (node.id === targetId) {
          return [...path, { id: node.id, title: node.title }]
        }
        if (node.children && node.children.length > 0) {
          const result = findPath(node.children, targetId, [...path, { id: node.id, title: node.title }])
          if (result) return result
        }
      }
      return null
    }

    return findPath(tree, folderId) || []
  }

  // 加载文件夹树
  const loadFolderTree = async () => {
    try {
      const response = await axios.get('/api/v1/admin/media/tree')
      setFolderTree(response.data.tree || [])
    } catch (error) {
      message.error('加载文件夹树失败')
    }
  }

  // 加载文件列表
  const loadFileList = async () => {
    setLoading(true)
    try {
      const response = await axios.get('/api/v1/admin/media', {
        params: {
          page,
          page_size: pageSize,
          parent_id: selectedFolderId,
          search: searchText || undefined,
          media_type: mediaTypeFilter || undefined,
        },
      })

      const data = response.data
      let items = data.items || []

      // 前端排序（如果后端不支持排序）
      items = items.sort((a: MediaItem, b: MediaItem) => {
        let comparison = 0

        if (sortBy === 'name') {
          comparison = a.title.localeCompare(b.title)
        } else if (sortBy === 'size') {
          comparison = a.file_size - b.file_size
        } else if (sortBy === 'date') {
          comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        }

        return sortOrder === 'asc' ? comparison : -comparison
      })

      setFileList(items)
      setTotal(data.total || 0)
    } catch (error) {
      message.error('加载文件列表失败')
    } finally {
      setLoading(false)
    }
  }

  // 创建文件夹
  const handleCreateFolder = async (title: string, parentId?: number) => {
    try {
      await axios.post('/api/v1/admin/media/folders/create', null, {
        params: {
          title,
          parent_id: parentId,
        },
      })
      message.success('文件夹创建成功')
      loadFolderTree()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '创建失败')
    }
  }

  // 移动文件/文件夹
  const handleMove = async (mediaIds: number[], targetParentId?: number) => {
    try {
      await axios.post('/api/v1/admin/media/batch/move', null, {
        params: {
          media_ids: mediaIds,
          target_parent_id: targetParentId,
        },
      })
      message.success('移动成功')
      loadFileList()
      loadFolderTree()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '移动失败')
    }
  }

  // 删除文件/文件夹
  const handleDelete = async (mediaIds: number[], permanent: boolean = false) => {
    try {
      await axios.delete('/api/v1/admin/media/batch/delete', {
        params: {
          media_ids: mediaIds,
          permanent,
        },
      })
      message.success('删除成功')
      loadFileList()
      loadFolderTree()
      setSelectedFiles([])
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败')
    }
  }

  // 打开文件夹（双击进入）
  const handleFolderOpen = (folderId: number) => {
    setSelectedFolderId(folderId)
    setPage(1) // 重置到第一页
    setSelectedFiles([]) // 清空选中
  }

  // 重命名文件/文件夹
  const handleRename = async (mediaId: number, newTitle: string) => {
    try {
      await axios.put(`/api/v1/admin/media/${mediaId}`, { title: newTitle })
      message.success('重命名成功')
      loadFileList()
      loadFolderTree()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '重命名失败')
    }
  }

  // 删除文件夹（从树中删除）
  const handleDeleteFolder = async (folderId: number) => {
    try {
      // 使用批量删除API，传入文件夹的media_id
      await axios.delete('/api/v1/admin/media/batch/delete', {
        params: {
          media_ids: [folderId],
          permanent: false,
        },
      })
      message.success('文件夹删除成功')
      loadFolderTree()
      loadFileList()
      // 如果删除的是当前选中的文件夹，返回根目录
      if (selectedFolderId === folderId) {
        setSelectedFolderId(undefined)
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败')
    }
  }

  // 打开批量移动Modal
  const handleOpenMoveModal = () => {
    if (selectedFiles.length === 0) {
      message.warning('请先选择要移动的文件')
      return
    }
    setMoveModalVisible(true)
  }

  // 确认批量移动
  const handleConfirmMove = async (targetFolderId?: number) => {
    await handleMove(selectedFiles, targetFolderId)
    setMoveModalVisible(false)
    setSelectedFiles([]) // 清空选中
  }

  // 批量下载文件
  const handleBatchDownload = async () => {
    if (selectedFiles.length === 0) {
      message.warning('请先选择要下载的文件')
      return
    }

    // 过滤出文件（不包括文件夹）
    const selectedItems = fileList.filter((item) =>
      selectedFiles.includes(item.id) && !item.is_folder
    )

    if (selectedItems.length === 0) {
      message.warning('请选择文件进行下载，文件夹暂不支持下载')
      return
    }

    // 单个文件直接下载
    if (selectedItems.length === 1) {
      const item = selectedItems[0]
      if (item) {
        window.open(item.url, '_blank')
        message.success('开始下载')
      }
      return
    }

    // 多个文件打包成 zip 下载
    const hide = message.loading('正在打包文件...', 0)

    try {
      const zip = new JSZip()

      // 下载所有文件并添加到 zip
      for (const item of selectedItems) {
        try {
          const response = await fetch(item.url)
          const blob = await response.blob()
          // 使用文件标题和扩展名
          const extension = item.url.split('.').pop() || ''
          const filename = extension ? `${item.title}.${extension}` : item.title
          zip.file(filename, blob)
        } catch (error) {
          console.error(`下载文件失败: ${item.title}`, error)
        }
      }

      // 生成 zip 文件
      const zipBlob = await zip.generateAsync({ type: 'blob' })

      // 创建下载链接
      const url = window.URL.createObjectURL(zipBlob)
      const a = document.createElement('a')
      a.href = url
      a.download = `files_${Date.now()}.zip`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)

      hide()
      message.success(`成功下载 ${selectedItems.length} 个文件`)
      setSelectedFiles([])
    } catch (error) {
      hide()
      message.error('下载失败，请重试')
      console.error('批量下载失败:', error)
    }
  }

  // 添加上传任务
  function handleAddUploadTask(files: File[]) {
    const newTasks: UploadTask[] = files.map((file) => ({
      id: `${Date.now()}_${file.name}`,
      file,
      status: 'pending',
      progress: 0,
    }))

    setUploadTasks((prev) => [...prev, ...newTasks])
    setUploadDrawerVisible(true)
  }

  // 快捷键支持
  useKeyboardShortcuts({
    onSelectAll: () => {
      // Ctrl+A - 全选当前页所有文件
      const allIds = fileList.map(item => item.id)
      setSelectedFiles(allIds)
      if (allIds.length > 0) {
        message.info(`已选中 ${allIds.length} 项`)
      }
    },
    onDelete: () => {
      // Delete - 删除选中的文件
      if (selectedFiles.length > 0) {
        handleDelete(selectedFiles, false)
      }
    },
    onEscape: () => {
      // Esc - 取消选中
      if (selectedFiles.length > 0) {
        setSelectedFiles([])
        message.info('已取消选中')
      }
    },
    enabled: !uploadDrawerVisible && !moveModalVisible, // Modal打开时禁用快捷键
  })

  // 初始化加载
  useEffect(() => {
    loadFolderTree()
  }, [])

  useEffect(() => {
    loadFileList()
    // 更新面包屑
    if (selectedFolderId) {
      setBreadcrumbPath(buildBreadcrumbPath(selectedFolderId))
    } else {
      setBreadcrumbPath([])
    }
  }, [selectedFolderId, page, pageSize, searchText, mediaTypeFilter, sortBy, sortOrder, folderTree])

  return (
    <div className="media-manager" ref={dropZoneRef}>
      {/* 拖拽提示遮罩 */}
      {isDragging && (
        <div className="drag-overlay">
          <div className="drag-overlay-content">
            <CloudUploadOutlined style={{ fontSize: 64, color: '#1890ff' }} />
            <h2>松开鼠标上传文件</h2>
            <p>支持图片和视频文件</p>
          </div>
        </div>
      )}

      <Toolbar
        onSearch={setSearchText}
        onUpload={handleAddUploadTask}
        onCreateFolder={() => handleCreateFolder('新建文件夹', selectedFolderId)}
        onRefresh={() => {
          loadFolderTree()
          loadFileList()
        }}
        selectedCount={selectedFiles.length}
        selectedSize={selectedFilesSize}
        onBatchDelete={() => handleDelete(selectedFiles, false)}
        onBatchMove={handleOpenMoveModal}
        onBatchDownload={handleBatchDownload}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSortChange={(by, order) => {
          setSortBy(by)
          setSortOrder(order)
        }}
        mediaTypeFilter={mediaTypeFilter}
        onMediaTypeFilterChange={setMediaTypeFilter}
      />

      <Layout className="media-manager-layout">
        <Sider
          width={280}
          theme="light"
          className="media-manager-sider"
        >
          <FolderTree
            treeData={folderTree}
            selectedFolderId={selectedFolderId}
            onSelect={setSelectedFolderId}
            onCreateFolder={handleCreateFolder}
            onRename={handleRename}
            onDelete={handleDeleteFolder}
            onRefresh={loadFolderTree}
          />
        </Sider>

        <Content className="media-manager-content">
          {/* 面包屑导航 */}
          {breadcrumbPath.length > 0 && (
            <Breadcrumb
              path={breadcrumbPath}
              onNavigate={setSelectedFolderId}
            />
          )}

          <FileList
            data={fileList}
            loading={loading}
            total={total}
            page={page}
            pageSize={pageSize}
            onPageChange={setPage}
            onPageSizeChange={setPageSize}
            selectedFiles={selectedFiles}
            onSelectChange={setSelectedFiles}
            onMove={handleMove}
            onDelete={handleDelete}
            onRefresh={loadFileList}
            viewMode={viewMode}
            sortBy={sortBy}
            sortOrder={sortOrder}
            onFolderOpen={handleFolderOpen}
            onRename={handleRename}
            onOpenMoveModal={handleOpenMoveModal}
            onUpload={() => {
              // 触发文件选择器
              const input = document.createElement('input')
              input.type = 'file'
              input.multiple = true
              input.onchange = (e) => {
                const files = Array.from((e.target as HTMLInputElement).files || [])
                handleAddUploadTask(files)
              }
              input.click()
            }}
            onCreateFolder={() => handleCreateFolder('新建文件夹', selectedFolderId)}
            searchText={searchText}
            currentFolderId={selectedFolderId}
            mediaTypeFilter={mediaTypeFilter}
          />
        </Content>
      </Layout>

      <UploadManager
        visible={uploadDrawerVisible}
        onClose={() => setUploadDrawerVisible(false)}
        tasks={uploadTasks}
        onTaskUpdate={setUploadTasks}
        parentId={selectedFolderId}
        onComplete={() => {
          loadFileList()
          loadFolderTree()
        }}
      />

      <MoveModal
        visible={moveModalVisible}
        onCancel={() => setMoveModalVisible(false)}
        onConfirm={handleConfirmMove}
        folderTree={folderTree}
        selectedCount={selectedFiles.length}
        currentFolderId={selectedFolderId}
      />

      {/* 键盘快捷键帮助 */}
      <KeyboardHelp />
    </div>
  )
}

export default MediaManager
