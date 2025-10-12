/**
 * MediaManager - Mega 风格文件管理器
 * 双面板布局：左侧文件夹树，右侧文件列表
 */

import React, { useState, useEffect } from 'react'
import { Layout, message } from 'antd'
import FolderTree from './components/FolderTree'
import FileList from './components/FileList'
import Toolbar from './components/Toolbar'
import UploadManager from './components/UploadManager'
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

  // 搜索
  const [searchText, setSearchText] = useState('')

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
        },
      })

      const data = response.data
      setFileList(data.items || [])
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

  // 添加上传任务
  const handleAddUploadTask = (files: File[]) => {
    const newTasks: UploadTask[] = files.map((file) => ({
      id: `${Date.now()}_${file.name}`,
      file,
      status: 'pending',
      progress: 0,
    }))

    setUploadTasks((prev) => [...prev, ...newTasks])
    setUploadDrawerVisible(true)
  }

  // 初始化加载
  useEffect(() => {
    loadFolderTree()
  }, [])

  useEffect(() => {
    loadFileList()
  }, [selectedFolderId, page, pageSize, searchText])

  return (
    <div className="media-manager">
      <Toolbar
        onSearch={setSearchText}
        onUpload={handleAddUploadTask}
        onCreateFolder={() => handleCreateFolder('新建文件夹', selectedFolderId)}
        onRefresh={() => {
          loadFolderTree()
          loadFileList()
        }}
        selectedCount={selectedFiles.length}
        onBatchDelete={() => handleDelete(selectedFiles, false)}
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
            onRefresh={loadFolderTree}
          />
        </Sider>

        <Content className="media-manager-content">
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
    </div>
  )
}

export default MediaManager
