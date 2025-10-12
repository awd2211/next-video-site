import React, { useState } from 'react'
import { Modal, Tag, Input, Space, message } from 'antd'
import { PlusOutlined, TagsOutlined } from '@ant-design/icons'

interface TagEditorProps {
  visible: boolean
  selectedFiles: number[]
  currentTags: string[]
  allTags: string[]
  onClose: () => void
  onSave: (tags: string[]) => void
}

/**
 * 标签编辑器组件
 */
const TagEditor: React.FC<TagEditorProps> = ({
  visible,
  selectedFiles,
  currentTags,
  allTags,
  onClose,
  onSave,
}) => {
  const [tags, setTags] = useState<string[]>(currentTags)
  const [inputValue, setInputValue] = useState('')
  const [inputVisible, setInputVisible] = useState(false)

  React.useEffect(() => {
    setTags(currentTags)
  }, [currentTags, visible])

  const handleAddTag = () => {
    const trimmedValue = inputValue.trim()
    if (!trimmedValue) {
      return
    }
    if (tags.includes(trimmedValue)) {
      message.warning('标签已存在')
      return
    }
    setTags([...tags, trimmedValue])
    setInputValue('')
    setInputVisible(false)
  }

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter((tag) => tag !== tagToRemove))
  }

  const handleSelectExistingTag = (tag: string) => {
    if (tags.includes(tag)) {
      return
    }
    setTags([...tags, tag])
  }

  const handleSave = () => {
    onSave(tags)
    onClose()
  }

  // 获取建议标签（已存在但未选中的）
  const suggestedTags = allTags.filter((tag) => !tags.includes(tag))

  return (
    <Modal
      title={
        <Space>
          <TagsOutlined style={{ color: '#1890ff' }} />
          <span>编辑标签</span>
          {selectedFiles.length > 0 && (
            <span style={{ fontSize: 14, color: '#8c8c8c', fontWeight: 'normal' }}>
              ({selectedFiles.length} 个文件)
            </span>
          )}
        </Space>
      }
      open={visible}
      onOk={handleSave}
      onCancel={onClose}
      okText="保存"
      cancelText="取消"
      width={600}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* 当前标签 */}
        <div>
          <div style={{ marginBottom: 12, fontSize: 14, fontWeight: 500 }}>
            当前标签:
          </div>
          <div
            style={{
              minHeight: 80,
              padding: 12,
              border: '1px dashed #d9d9d9',
              borderRadius: 4,
              background: '#fafafa',
            }}
          >
            <Space wrap>
              {tags.map((tag) => (
                <Tag
                  key={tag}
                  closable
                  onClose={() => handleRemoveTag(tag)}
                  color="blue"
                  style={{ fontSize: 13, padding: '4px 8px' }}
                  icon={<TagsOutlined />}
                >
                  {tag}
                </Tag>
              ))}

              {inputVisible ? (
                <Input
                  type="text"
                  size="small"
                  style={{ width: 120 }}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onBlur={handleAddTag}
                  onPressEnter={handleAddTag}
                  autoFocus
                  placeholder="输入标签名"
                />
              ) : (
                <Tag
                  onClick={() => setInputVisible(true)}
                  style={{
                    background: '#fff',
                    borderStyle: 'dashed',
                    cursor: 'pointer',
                    fontSize: 13,
                    padding: '4px 8px',
                  }}
                  icon={<PlusOutlined />}
                >
                  新建标签
                </Tag>
              )}
            </Space>

            {tags.length === 0 && !inputVisible && (
              <div style={{ color: '#8c8c8c', fontSize: 13, marginTop: 8 }}>
                点击"新建标签"或从下方选择已有标签
              </div>
            )}
          </div>
        </div>

        {/* 已有标签 */}
        {suggestedTags.length > 0 && (
          <div>
            <div style={{ marginBottom: 12, fontSize: 14, fontWeight: 500 }}>
              选择已有标签:
            </div>
            <Space wrap>
              {suggestedTags.map((tag) => (
                <Tag
                  key={tag}
                  onClick={() => handleSelectExistingTag(tag)}
                  style={{
                    cursor: 'pointer',
                    fontSize: 13,
                    padding: '4px 8px',
                    borderStyle: 'dashed',
                  }}
                  icon={<PlusOutlined style={{ fontSize: 10 }} />}
                >
                  {tag}
                </Tag>
              ))}
            </Space>
          </div>
        )}

        {/* 操作提示 */}
        <div
          style={{
            padding: 12,
            background: '#e6f7ff',
            borderRadius: 4,
            fontSize: 12,
            color: '#0050b3',
          }}
        >
          <div style={{ marginBottom: 4 }}>
            💡 <strong>提示:</strong>
          </div>
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            <li>标签可以帮助您更好地组织和查找文件</li>
            <li>点击已有标签快速添加，点击 × 移除标签</li>
            <li>支持为多个文件批量添加相同标签</li>
          </ul>
        </div>
      </Space>
    </Modal>
  )
}

export default TagEditor
