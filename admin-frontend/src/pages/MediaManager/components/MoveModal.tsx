import React, { useState } from 'react'
import { Modal, Tree, Empty } from 'antd'
import { FolderOutlined, HomeOutlined } from '@ant-design/icons'
import type { DataNode } from 'antd/es/tree'
import type { FolderNode } from '../types'

interface MoveModalProps {
  visible: boolean
  onCancel: () => void
  onConfirm: (targetFolderId?: number) => void
  folderTree: FolderNode[]
  selectedCount: number
  currentFolderId?: number
}

const MoveModal: React.FC<MoveModalProps> = ({
  visible,
  onCancel,
  onConfirm,
  folderTree,
  selectedCount,
  currentFolderId,
}) => {
  const [selectedFolderId, setSelectedFolderId] = useState<number | undefined>(undefined)

  // 转换文件夹树数据
  const convertToTreeData = (nodes: FolderNode[]): DataNode[] => {
    return nodes.map((node) => ({
      key: node.id.toString(),
      title: node.title,
      icon: <FolderOutlined />,
      children: node.children && node.children.length > 0 ? convertToTreeData(node.children) : [],
    }))
  }

  const fullTreeData: DataNode[] = [
    {
      key: 'root',
      title: '全部文件（根目录）',
      icon: <HomeOutlined />,
      children: convertToTreeData(folderTree),
    },
  ]

  const handleSelect = (selectedKeys: React.Key[]) => {
    if (selectedKeys.length === 0) {
      setSelectedFolderId(undefined)
    } else {
      const key = selectedKeys[0] as string
      if (key === 'root') {
        setSelectedFolderId(undefined)
      } else {
        setSelectedFolderId(Number(key))
      }
    }
  }

  const handleOk = () => {
    onConfirm(selectedFolderId)
    setSelectedFolderId(undefined)
  }

  const handleCancel = () => {
    onCancel()
    setSelectedFolderId(undefined)
  }

  return (
    <Modal
      title={`移动 ${selectedCount} 个项目`}
      open={visible}
      onOk={handleOk}
      onCancel={handleCancel}
      okText="移动到此"
      cancelText="取消"
      width={500}
    >
      <div style={{ marginBottom: 16, color: '#8c8c8c', fontSize: 14 }}>
        {currentFolderId
          ? '请选择目标文件夹（留空表示移动到根目录）'
          : '当前在根目录，请选择目标文件夹'}
      </div>

      {folderTree.length === 0 ? (
        <Empty description="暂无文件夹，将移动到根目录" />
      ) : (
        <Tree
          showIcon
          defaultExpandAll
          selectedKeys={selectedFolderId ? [selectedFolderId.toString()] : []}
          treeData={fullTreeData}
          onSelect={handleSelect}
          style={{
            border: '1px solid #d9d9d9',
            borderRadius: 4,
            padding: 12,
            maxHeight: 400,
            overflow: 'auto',
          }}
        />
      )}

      {selectedFolderId && (
        <div style={{ marginTop: 12, padding: 8, background: '#e6f7ff', borderRadius: 4 }}>
          目标文件夹：{selectedFolderId ? `文件夹 #${selectedFolderId}` : '根目录'}
        </div>
      )}
    </Modal>
  )
}

export default MoveModal
