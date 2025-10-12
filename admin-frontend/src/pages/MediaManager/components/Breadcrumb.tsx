import React from 'react'
import { Breadcrumb as AntBreadcrumb } from 'antd'
import { HomeOutlined, FolderOutlined } from '@ant-design/icons'

interface BreadcrumbItem {
  id?: number
  title: string
}

interface BreadcrumbProps {
  path: BreadcrumbItem[]
  onNavigate: (folderId?: number) => void
}

const Breadcrumb: React.FC<BreadcrumbProps> = ({ path, onNavigate }) => {
  const items = [
    {
      title: (
        <span
          style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4 }}
          onClick={() => onNavigate(undefined)}
        >
          <HomeOutlined />
          <span>全部文件</span>
        </span>
      ),
    },
    ...path.map((item, index) => ({
      title: (
        <span
          style={{
            cursor: index === path.length - 1 ? 'default' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 4,
            color: index === path.length - 1 ? '#1890ff' : undefined,
            fontWeight: index === path.length - 1 ? 500 : undefined,
          }}
          onClick={() => {
            if (index < path.length - 1) {
              onNavigate(item.id)
            }
          }}
        >
          <FolderOutlined />
          <span>{item.title}</span>
        </span>
      ),
    })),
  ]

  return (
    <div className="breadcrumb-nav">
      <AntBreadcrumb items={items} />
    </div>
  )
}

export default Breadcrumb
