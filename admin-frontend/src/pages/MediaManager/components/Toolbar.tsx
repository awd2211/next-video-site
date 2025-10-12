import React, { useRef } from 'react'
import { Button, Input, Space, Upload, Popconfirm } from 'antd'
import {
  SearchOutlined,
  UploadOutlined,
  FolderAddOutlined,
  ReloadOutlined,
  DeleteOutlined,
} from '@ant-design/icons'

interface ToolbarProps {
  onSearch: (text: string) => void
  onUpload: (files: File[]) => void
  onCreateFolder: () => void
  onRefresh: () => void
  selectedCount: number
  onBatchDelete: () => void
}

const Toolbar: React.FC<ToolbarProps> = ({
  onSearch,
  onUpload,
  onCreateFolder,
  onRefresh,
  selectedCount,
  onBatchDelete,
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
