import React from 'react'
import { Empty, Button } from 'antd'
import {
  InboxOutlined,
  UploadOutlined,
  FolderAddOutlined,
  CloudUploadOutlined,
} from '@ant-design/icons'

interface EmptyStateProps {
  type: 'root' | 'folder' | 'search'
  onUpload?: () => void
  onCreateFolder?: () => void
  searchText?: string
}

const EmptyState: React.FC<EmptyStateProps> = ({
  type,
  onUpload,
  onCreateFolder,
  searchText,
}) => {
  if (type === 'search') {
    return (
      <Empty
        image={<InboxOutlined style={{ fontSize: 64, color: '#bfbfbf' }} />}
        description={
          <div>
            <p style={{ fontSize: 16, marginBottom: 8 }}>
              没有找到 "{searchText}" 相关的文件
            </p>
            <p style={{ fontSize: 14, color: '#8c8c8c' }}>
              尝试使用不同的关键词搜索
            </p>
          </div>
        }
        style={{ padding: '80px 20px' }}
      />
    )
  }

  if (type === 'folder') {
    return (
      <Empty
        image={<InboxOutlined style={{ fontSize: 64, color: '#bfbfbf' }} />}
        description={
          <div>
            <p style={{ fontSize: 16, marginBottom: 8 }}>
              这个文件夹是空的
            </p>
            <p style={{ fontSize: 14, color: '#8c8c8c', marginBottom: 24 }}>
              上传文件或创建子文件夹来开始使用
            </p>
            <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
              <Button
                type="primary"
                icon={<UploadOutlined />}
                onClick={onUpload}
              >
                上传文件
              </Button>
              <Button
                icon={<FolderAddOutlined />}
                onClick={onCreateFolder}
              >
                新建文件夹
              </Button>
            </div>
          </div>
        }
        style={{ padding: '80px 20px' }}
      />
    )
  }

  // type === 'root' - 根目录为空
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: 400,
      padding: 40,
    }}>
      <div style={{ textAlign: 'center', maxWidth: 600 }}>
        <CloudUploadOutlined
          style={{
            fontSize: 120,
            color: '#1890ff',
            marginBottom: 32,
          }}
        />

        <h2 style={{ fontSize: 24, marginBottom: 16, color: '#262626' }}>
          欢迎使用媒体管理器
        </h2>

        <p style={{ fontSize: 16, color: '#595959', marginBottom: 32 }}>
          开始上传您的图片和视频文件，或创建文件夹来组织您的媒体资源
        </p>

        <div style={{
          display: 'flex',
          gap: 16,
          justifyContent: 'center',
          marginBottom: 48,
        }}>
          <Button
            type="primary"
            size="large"
            icon={<UploadOutlined />}
            onClick={onUpload}
          >
            上传文件
          </Button>
          <Button
            size="large"
            icon={<FolderAddOutlined />}
            onClick={onCreateFolder}
          >
            新建文件夹
          </Button>
        </div>

        <div style={{
          background: '#f6f8fa',
          borderRadius: 8,
          padding: 24,
          textAlign: 'left',
        }}>
          <h3 style={{ fontSize: 16, marginBottom: 16, color: '#262626' }}>
            💡 快速开始指南
          </h3>
          <ul style={{
            listStyle: 'none',
            padding: 0,
            margin: 0,
            color: '#595959',
            lineHeight: 2,
          }}>
            <li>🖱️ <strong>拖拽上传：</strong>直接拖拽文件到此页面即可上传</li>
            <li>📂 <strong>文件夹管理：</strong>创建文件夹来组织您的文件</li>
            <li>⌨️ <strong>快捷键：</strong>Ctrl+A 全选，Delete 删除，Esc 取消</li>
            <li>🔍 <strong>搜索：</strong>使用顶部搜索框快速查找文件</li>
            <li>👁️ <strong>双击：</strong>双击文件夹进入，双击文件预览</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default EmptyState
