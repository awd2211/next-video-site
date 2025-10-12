/**
 * RecycleBin - 回收站抽屉
 * 显示已删除的文件，支持恢复和永久删除
 */

import React, { useState, useEffect } from 'react'
import {
  Drawer,
  List,
  Button,
  Space,
  Popconfirm,
  Empty,
  Typography,
  Tag,
  message,
  Input,
  Checkbox,
} from 'antd'
import {
  DeleteOutlined,
  RollbackOutlined,
  ClearOutlined,
  FileOutlined,
  FolderOutlined,
  FileImageOutlined,
  VideoCameraOutlined,
} from '@ant-design/icons'
import type { MediaItem } from '../types'

const { Text } = Typography
const { Search } = Input

interface RecycleBinProps {
  visible: boolean
  onClose: () => void
  onRestore: (ids: number[]) => void
  onPermanentDelete: (ids: number[]) => void
  onClearAll: () => void
  onRefresh: () => void
}

const RecycleBin: React.FC<RecycleBinProps> = ({
  visible,
  onClose,
  onRestore,
  onPermanentDelete,
  onClearAll,
  onRefresh,
}) => {
  const [deletedItems, setDeletedItems] = useState<MediaItem[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedIds, setSelectedIds] = useState<number[]>([])
  const [searchText, setSearchText] = useState('')

  // 加载回收站文件
  const loadDeletedItems = async () => {
    setLoading(true)
    try {
      // 模拟 API 调用 - 实际应该调用后端接口获取已删除的文件
      // const response = await axios.get('/api/v1/admin/media/deleted')
      // setDeletedItems(response.data.items || [])

      // 临时使用空数据
      setDeletedItems([])
    } catch (error) {
      message.error('加载回收站失败')
    } finally {
      setLoading(false)
    }
  }

  // 当抽屉打开时加载数据
  useEffect(() => {
    if (visible) {
      loadDeletedItems()
      setSelectedIds([])
      setSearchText('')
    }
  }, [visible])

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
  }

  // 格式化日期
  const formatDate = (date: string): string => {
    return new Date(date).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // 获取文件图标
  const getFileIcon = (item: MediaItem) => {
    if (item.is_folder) {
      return <FolderOutlined style={{ fontSize: 32, color: '#faad14' }} />
    }
    if (item.media_type === 'image') {
      return <FileImageOutlined style={{ fontSize: 32, color: '#52c41a' }} />
    }
    if (item.media_type === 'video') {
      return <VideoCameraOutlined style={{ fontSize: 32, color: '#1890ff' }} />
    }
    return <FileOutlined style={{ fontSize: 32, color: '#8c8c8c' }} />
  }

  // 切换选中
  const toggleSelect = (id: number) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    )
  }

  // 全选/取消全选
  const toggleSelectAll = () => {
    if (selectedIds.length === filteredItems.length) {
      setSelectedIds([])
    } else {
      setSelectedIds(filteredItems.map((item) => item.id))
    }
  }

  // 恢复选中的文件
  const handleRestore = () => {
    if (selectedIds.length === 0) {
      message.warning('请选择要恢复的文件')
      return
    }
    onRestore(selectedIds)
    setSelectedIds([])
    loadDeletedItems()
  }

  // 永久删除选中的文件
  const handlePermanentDelete = () => {
    if (selectedIds.length === 0) {
      message.warning('请选择要删除的文件')
      return
    }
    onPermanentDelete(selectedIds)
    setSelectedIds([])
    loadDeletedItems()
  }

  // 清空回收站
  const handleClearAll = () => {
    onClearAll()
    setSelectedIds([])
    loadDeletedItems()
  }

  // 筛选项
  const filteredItems = deletedItems.filter((item) =>
    item.title.toLowerCase().includes(searchText.toLowerCase())
  )

  return (
    <Drawer
      title={
        <Space>
          <DeleteOutlined />
          <span>回收站</span>
          {deletedItems.length > 0 && (
            <Tag color="red">{deletedItems.length} 项</Tag>
          )}
        </Space>
      }
      placement="right"
      width={600}
      onClose={onClose}
      open={visible}
      styles={{
        body: { padding: 0 },
      }}
      extra={
        <Space>
          <Button
            size="small"
            icon={<RollbackOutlined />}
            onClick={onRefresh}
          >
            刷新
          </Button>
        </Space>
      }
    >
      {/* 操作栏 */}
      {deletedItems.length > 0 && (
        <div style={{ padding: 16, borderBottom: '1px solid #f0f0f0', background: '#fafafa' }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            {/* 搜索框 */}
            <Search
              placeholder="搜索文件名..."
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              allowClear
            />

            {/* 批量操作 */}
            <Space style={{ width: '100%', justifyContent: 'space-between' }}>
              <Checkbox
                checked={selectedIds.length === filteredItems.length && filteredItems.length > 0}
                indeterminate={selectedIds.length > 0 && selectedIds.length < filteredItems.length}
                onChange={toggleSelectAll}
              >
                全选 {selectedIds.length > 0 && `(${selectedIds.length})`}
              </Checkbox>

              <Space>
                <Button
                  type="primary"
                  size="small"
                  icon={<RollbackOutlined />}
                  onClick={handleRestore}
                  disabled={selectedIds.length === 0}
                >
                  恢复
                </Button>
                <Popconfirm
                  title="永久删除"
                  description={`确定要永久删除选中的 ${selectedIds.length} 个项目吗？此操作无法撤销！`}
                  onConfirm={handlePermanentDelete}
                  okText="确认删除"
                  cancelText="取消"
                  okButtonProps={{ danger: true }}
                  disabled={selectedIds.length === 0}
                >
                  <Button
                    danger
                    size="small"
                    icon={<DeleteOutlined />}
                    disabled={selectedIds.length === 0}
                  >
                    永久删除
                  </Button>
                </Popconfirm>
                <Popconfirm
                  title="清空回收站"
                  description="确定要清空回收站吗？所有文件将被永久删除，此操作无法撤销！"
                  onConfirm={handleClearAll}
                  okText="确认清空"
                  cancelText="取消"
                  okButtonProps={{ danger: true }}
                >
                  <Button
                    danger
                    size="small"
                    icon={<ClearOutlined />}
                  >
                    清空回收站
                  </Button>
                </Popconfirm>
              </Space>
            </Space>
          </Space>
        </div>
      )}

      {/* 文件列表 */}
      {filteredItems.length > 0 ? (
        <List
          loading={loading}
          dataSource={filteredItems}
          renderItem={(item) => (
            <List.Item
              style={{
                padding: '16px 24px',
                cursor: 'pointer',
                background: selectedIds.includes(item.id) ? '#e6f7ff' : 'transparent',
              }}
              onClick={() => toggleSelect(item.id)}
              actions={[
                <Button
                  key="restore"
                  type="link"
                  icon={<RollbackOutlined />}
                  onClick={(e) => {
                    e.stopPropagation()
                    onRestore([item.id])
                    loadDeletedItems()
                  }}
                >
                  恢复
                </Button>,
                <Popconfirm
                  key="delete"
                  title="永久删除"
                  description="确定要永久删除此文件吗？此操作无法撤销！"
                  onConfirm={(e) => {
                    e?.stopPropagation()
                    onPermanentDelete([item.id])
                    loadDeletedItems()
                  }}
                  okText="确认"
                  cancelText="取消"
                  okButtonProps={{ danger: true }}
                >
                  <Button
                    type="link"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={(e) => e.stopPropagation()}
                  >
                    永久删除
                  </Button>
                </Popconfirm>,
              ]}
            >
              <List.Item.Meta
                avatar={
                  <Checkbox
                    checked={selectedIds.includes(item.id)}
                    onClick={(e) => e.stopPropagation()}
                    onChange={() => toggleSelect(item.id)}
                    style={{ marginRight: 8 }}
                  />
                }
                title={
                  <Space>
                    {getFileIcon(item)}
                    <div>
                      <div>
                        <Text strong>{item.title}</Text>
                      </div>
                      <div>
                        <Space size={4}>
                          {item.is_folder ? (
                            <Tag color="gold">文件夹</Tag>
                          ) : item.media_type === 'image' ? (
                            <Tag color="green">图片</Tag>
                          ) : item.media_type === 'video' ? (
                            <Tag color="blue">视频</Tag>
                          ) : (
                            <Tag>文件</Tag>
                          )}
                          {!item.is_folder && (
                            <Text type="secondary" style={{ fontSize: 12 }}>
                              {formatFileSize(item.file_size)}
                            </Text>
                          )}
                        </Space>
                      </div>
                    </div>
                  </Space>
                }
                description={
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    删除时间: {formatDate(item.updated_at || item.created_at)}
                  </Text>
                }
              />
            </List.Item>
          )}
        />
      ) : (
        <div style={{ padding: '100px 24px', textAlign: 'center' }}>
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={
              searchText ? '未找到匹配的文件' : '回收站是空的'
            }
          >
            {!searchText && (
              <Text type="secondary">
                已删除的文件将暂时保存在这里
              </Text>
            )}
          </Empty>
        </div>
      )}
    </Drawer>
  )
}

export default RecycleBin
