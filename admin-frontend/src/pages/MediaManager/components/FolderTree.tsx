import React, { useState } from 'react'
import { Tree, Button, Input, Modal, message, Dropdown } from 'antd'
import type { MenuProps } from 'antd'
import {
  FolderOutlined,
  FolderOpenOutlined,
  HomeOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  FolderAddOutlined
} from '@ant-design/icons'
import type { DataNode } from 'antd/es/tree'
import type { FolderNode } from '../types'

interface FolderTreeProps {
  treeData: FolderNode[]
  selectedFolderId?: number
  onSelect: (folderId?: number) => void
  onCreateFolder: (title: string, parentId?: number) => void
  onRename: (folderId: number, newTitle: string) => void
  onDelete: (folderId: number) => void
  onRefresh: () => void
}

const FolderTree: React.FC<FolderTreeProps> = ({
  treeData,
  selectedFolderId,
  onSelect,
  onCreateFolder,
  onRename,
  onDelete,
}) => {
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [newFolderName, setNewFolderName] = useState('')
  const [targetParentId, setTargetParentId] = useState<number | undefined>(undefined)
  const [renameModalVisible, setRenameModalVisible] = useState(false)
  const [renamingFolderId, setRenamingFolderId] = useState<number | null>(null)
  const [renameValue, setRenameValue] = useState('')

  // 获取文件夹右键菜单
  const getFolderContextMenu = (folderId: number, folderTitle: string): MenuProps['items'] => [
    {
      key: 'create',
      label: '新建子文件夹',
      icon: <FolderAddOutlined />,
      onClick: () => showCreateModal(folderId),
    },
    {
      type: 'divider',
    },
    {
      key: 'rename',
      label: '重命名',
      icon: <EditOutlined />,
      onClick: () => {
        setRenamingFolderId(folderId)
        setRenameValue(folderTitle)
        setRenameModalVisible(true)
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
          content: `确定要删除文件夹 "${folderTitle}" 吗？此操作将删除文件夹中的所有内容且不可恢复。`,
          okText: '确认删除',
          cancelText: '取消',
          okButtonProps: { danger: true },
          onOk: () => onDelete(folderId),
        })
      },
    },
  ]

  // 转换数据格式为 Ant Design Tree 需要的格式
  const convertToTreeData = (nodes: FolderNode[]): DataNode[] => {
    return nodes.map((node) => ({
      key: node.id.toString(),
      title: (
        <Dropdown
          menu={{ items: getFolderContextMenu(node.id, node.title) }}
          trigger={['contextMenu']}
        >
          <div className="folder-tree-node-title">
            <span>{node.title}</span>
            {node.children_count > 0 && (
              <span className="folder-tree-node-count">({node.children_count})</span>
            )}
          </div>
        </Dropdown>
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

  const handleRename = () => {
    if (!renamingFolderId) return
    if (!renameValue.trim()) {
      message.error('文件夹名称不能为空')
      return
    }
    onRename(renamingFolderId, renameValue.trim())
    setRenameModalVisible(false)
    setRenamingFolderId(null)
    setRenameValue('')
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

      <Modal
        title="重命名文件夹"
        open={renameModalVisible}
        onOk={handleRename}
        onCancel={() => {
          setRenameModalVisible(false)
          setRenamingFolderId(null)
          setRenameValue('')
        }}
        okText="确认"
        cancelText="取消"
      >
        <Input
          placeholder="输入新名称"
          value={renameValue}
          onChange={(e) => setRenameValue(e.target.value)}
          onPressEnter={handleRename}
          autoFocus
        />
      </Modal>
    </div>
  )
}

export default FolderTree
