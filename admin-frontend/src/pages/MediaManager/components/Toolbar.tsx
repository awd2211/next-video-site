import React, { useRef } from 'react'
import { Button, Input, Space, Popconfirm, Dropdown, Segmented } from 'antd'
import type { MenuProps } from 'antd'
import {
  SearchOutlined,
  UploadOutlined,
  FolderAddOutlined,
  ReloadOutlined,
  DeleteOutlined,
  AppstoreOutlined,
  BarsOutlined,
  SortAscendingOutlined,
  SortDescendingOutlined,
  FontSizeOutlined,
  FileOutlined,
  ClockCircleOutlined,
  DragOutlined,
} from '@ant-design/icons'

interface ToolbarProps {
  onSearch: (text: string) => void
  onUpload: (files: File[]) => void
  onCreateFolder: () => void
  onRefresh: () => void
  selectedCount: number
  onBatchDelete: () => void
  onBatchMove: () => void
  viewMode: 'grid' | 'list'
  onViewModeChange: (mode: 'grid' | 'list') => void
  sortBy: 'name' | 'size' | 'date'
  sortOrder: 'asc' | 'desc'
  onSortChange: (by: 'name' | 'size' | 'date', order: 'asc' | 'desc') => void
}

const Toolbar: React.FC<ToolbarProps> = ({
  onSearch,
  onUpload,
  onCreateFolder,
  onRefresh,
  selectedCount,
  onBatchDelete,
  onBatchMove,
  viewMode,
  onViewModeChange,
  sortBy,
  sortOrder,
  onSortChange,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    if (files.length > 0) {
      onUpload(files)
    }
    // 清空 input 以便可以重复选择相同文件
    e.target.value = ''
  }

  // 排序菜单
  const sortByItems: MenuProps['items'] = [
    {
      key: 'name',
      label: '按名称',
      icon: <FontSizeOutlined />,
    },
    {
      key: 'size',
      label: '按大小',
      icon: <FileOutlined />,
    },
    {
      key: 'date',
      label: '按日期',
      icon: <ClockCircleOutlined />,
    },
  ]

  const handleSortByClick: MenuProps['onClick'] = ({ key }) => {
    onSortChange(key as 'name' | 'size' | 'date', sortOrder)
  }

  const toggleSortOrder = () => {
    onSortChange(sortBy, sortOrder === 'asc' ? 'desc' : 'asc')
  }

  const getSortLabel = () => {
    const labels = {
      name: '名称',
      size: '大小',
      date: '日期',
    }
    return labels[sortBy]
  }

  return (
    <div className="media-toolbar">
      <div className="media-toolbar-left">
        <Input
          placeholder="搜索文件或文件夹..."
          prefix={<SearchOutlined />}
          allowClear
          style={{ width: 300 }}
          onChange={(e) => onSearch(e.target.value)}
        />
      </div>

      <div className="media-toolbar-right">
        <Space>
          {selectedCount > 0 && (
            <>
              <span style={{ color: '#8c8c8c' }}>已选 {selectedCount} 项</span>
              <Button
                icon={<DragOutlined />}
                onClick={onBatchMove}
              >
                移动到
              </Button>
              <Popconfirm
                title="确认删除"
                description={`确定要删除选中的 ${selectedCount} 个项目吗？`}
                onConfirm={onBatchDelete}
                okText="确认"
                cancelText="取消"
              >
                <Button icon={<DeleteOutlined />} danger>
                  批量删除
                </Button>
              </Popconfirm>
            </>
          )}

          {/* 视图模式切换 */}
          <Segmented
            value={viewMode}
            onChange={(value) => onViewModeChange(value as 'grid' | 'list')}
            options={[
              {
                value: 'grid',
                icon: <AppstoreOutlined />,
              },
              {
                value: 'list',
                icon: <BarsOutlined />,
              },
            ]}
          />

          {/* 排序控制 */}
          <Space.Compact>
            <Dropdown menu={{ items: sortByItems, onClick: handleSortByClick }}>
              <Button>
                排序: {getSortLabel()}
              </Button>
            </Dropdown>
            <Button
              icon={sortOrder === 'asc' ? <SortAscendingOutlined /> : <SortDescendingOutlined />}
              onClick={toggleSortOrder}
            />
          </Space.Compact>

          <Button
            type="primary"
            icon={<UploadOutlined />}
            onClick={() => fileInputRef.current?.click()}
          >
            上传文件
          </Button>

          <input
            ref={fileInputRef}
            type="file"
            multiple
            style={{ display: 'none' }}
            onChange={handleFileSelect}
          />

          <Button
            icon={<FolderAddOutlined />}
            onClick={onCreateFolder}
          >
            新建文件夹
          </Button>

          <Button
            icon={<ReloadOutlined />}
            onClick={onRefresh}
          >
            刷新
          </Button>
        </Space>
      </div>
    </div>
  )
}

export default Toolbar
