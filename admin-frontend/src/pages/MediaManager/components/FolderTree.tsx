import React, { useState } from 'react'
import { Tree, Button, Input, Modal, message } from 'antd'
import { FolderOutlined, FolderOpenOutlined, HomeOutlined, PlusOutlined } from '@ant-design/icons'
import type { DataNode } from 'antd/es/tree'
import type { FolderNode } from '../types'

interface FolderTreeProps {
  treeData: FolderNode[]
  selectedFolderId?: number
  onSelect: (folderId?: number) => void
  onCreateFolder: (title: string, parentId?: number) => void
  onRefresh: () => void
}

const FolderTree: React.FC<FolderTreeProps> = ({
  treeData,
  selectedFolderId,
  onSelect,
  onCreateFolder,
}) => {
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [newFolderName, setNewFolderName] = useState('')
  const [targetParentId, setTargetParentId] = useState<number | undefined>(undefined)

  // 转换数据格式为 Ant Design Tree 需要的格式
  const convertToTreeData = (nodes: FolderNode[]): DataNode[] => {
    return nodes.map((node) => ({
      key: node.id.toString(),
      title: (
        <div className="folder-tree-node-title">
          <span>{node.title}</span>
          {node.children_count > 0 && (
            <span className="folder-tree-node-count">({node.children_count})</span>
          )}
        </div>
      ),
      icon: selectedFolderId === node.id ? <FolderOpenOutlined /> : <FolderOutlined />,
      children: node.children && node.children.length > 0 ? convertToTreeData(node.children) : [],
    }))
  }

  const handleSelect = (selectedKeys: React.Key[]) => {
    if (selectedKeys.length === 0) {
      onSelect(undefined)
    } else {
      const key = selectedKeys[0] as string
      if (key === 'root') {
        onSelect(undefined)
      } else {
        onSelect(Number(key))
      }
    }
  }

  const handleCreateFolder = () => {
    if (!newFolderName.trim()) {
      message.warning('请输入文件夹名称')
      return
    }

    onCreateFolder(newFolderName, targetParentId)
    setCreateModalVisible(false)
    setNewFolderName('')
    setTargetParentId(undefined)
  }

  const showCreateModal = (parentId?: number) => {
    setTargetParentId(parentId)
    setCreateModalVisible(true)
  }

  // 构建完整的树数据（包含根目录）
  const fullTreeData: DataNode[] = [
    {
      key: 'root',
      title: (
        <div className="folder-tree-node-title">
          <HomeOutlined />
          <span>全部文件</span>
        </div>
      ),
      icon: <HomeOutlined />,
      children: convertToTreeData(treeData),
    },
  ]

  return (
    <div className="folder-tree">
      <div style={{ marginBottom: 12, display: 'flex', justifyContent: 'space-between' }}>
        <Button
          type="primary"
          size="small"
          icon={<PlusOutlined />}
          onClick={() => showCreateModal(selectedFolderId)}
        >
          新建文件夹
        </Button>
      </div>

      <Tree
        showIcon
        defaultExpandAll
        selectedKeys={selectedFolderId ? [selectedFolderId.toString()] : ['root']}
        treeData={fullTreeData}
        onSelect={handleSelect}
      />

      <Modal
        title="新建文件夹"
        open={createModalVisible}
        onOk={handleCreateFolder}
        onCancel={() => {
          setCreateModalVisible(false)
          setNewFolderName('')
        }}
        okText="创建"
        cancelText="取消"
      >
        <Input
          placeholder="输入文件夹名称"
          value={newFolderName}
          onChange={(e) => setNewFolderName(e.target.value)}
          onPressEnter={handleCreateFolder}
          autoFocus
        />
      </Modal>
    </div>
  )
}

export default FolderTree
