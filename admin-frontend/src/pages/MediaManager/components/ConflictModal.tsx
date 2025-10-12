import React, { useState } from 'react'
import { Modal, Radio, Input, Alert, Space, Tag } from 'antd'
import { WarningOutlined, FileOutlined } from '@ant-design/icons'

export interface ConflictFile {
  file: File
  existingName: string
  suggestedName: string
}

export type ConflictAction = 'skip' | 'replace' | 'rename'

interface ConflictModalProps {
  visible: boolean
  conflictFile: ConflictFile | null
  onResolve: (action: ConflictAction, newName?: string) => void
  onCancel: () => void
}

/**
 * 文件冲突解决 Modal
 */
const ConflictModal: React.FC<ConflictModalProps> = ({
  visible,
  conflictFile,
  onResolve,
  onCancel,
}) => {
  const [action, setAction] = useState<ConflictAction>('rename')
  const [customName, setCustomName] = useState('')

  React.useEffect(() => {
    if (conflictFile) {
      setCustomName(conflictFile.suggestedName)
      setAction('rename')
    }
  }, [conflictFile])

  const handleOk = () => {
    if (action === 'rename') {
      onResolve(action, customName)
    } else {
      onResolve(action)
    }
  }

  if (!conflictFile) return null

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
  }

  return (
    <Modal
      title={
        <span>
          <WarningOutlined style={{ color: '#faad14', marginRight: 8 }} />
          文件名冲突
        </span>
      }
      open={visible}
      onOk={handleOk}
      onCancel={onCancel}
      okText="确认"
      cancelText="取消"
      width={500}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Alert
          message="检测到同名文件"
          description={`文件夹中已存在名为 "${conflictFile.existingName}" 的文件`}
          type="warning"
          showIcon
        />

        <div>
          <div style={{ marginBottom: 8, fontSize: 14, fontWeight: 500 }}>
            <FileOutlined style={{ marginRight: 4 }} />
            上传文件信息:
          </div>
          <div style={{ padding: 12, background: '#fafafa', borderRadius: 4 }}>
            <div style={{ marginBottom: 4 }}>
              <span style={{ color: '#8c8c8c' }}>文件名: </span>
              <span>{conflictFile.file.name}</span>
            </div>
            <div>
              <span style={{ color: '#8c8c8c' }}>大小: </span>
              <span>{formatFileSize(conflictFile.file.size)}</span>
            </div>
          </div>
        </div>

        <div>
          <div style={{ marginBottom: 12, fontSize: 14, fontWeight: 500 }}>
            请选择处理方式:
          </div>
          <Radio.Group
            value={action}
            onChange={(e) => setAction(e.target.value)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Radio value="rename">
                <span>重命名上传</span>
                <Tag color="green" style={{ marginLeft: 8 }}>推荐</Tag>
              </Radio>
              {action === 'rename' && (
                <div style={{ marginLeft: 24, marginTop: 8 }}>
                  <Input
                    value={customName}
                    onChange={(e) => setCustomName(e.target.value)}
                    placeholder="输入新文件名"
                    suffix={`.${conflictFile.file.name.split('.').pop()}`}
                  />
                  <div style={{ marginTop: 4, fontSize: 12, color: '#8c8c8c' }}>
                    建议名称: {conflictFile.suggestedName}
                  </div>
                </div>
              )}

              <Radio value="replace">
                <span>替换现有文件</span>
                <Tag color="orange" style={{ marginLeft: 8 }}>谨慎</Tag>
              </Radio>

              <Radio value="skip">
                <span>跳过此文件</span>
              </Radio>
            </Space>
          </Radio.Group>
        </div>

        {action === 'replace' && (
          <Alert
            message="警告"
            description="替换操作将覆盖现有文件，此操作不可恢复！"
            type="error"
            showIcon
          />
        )}
      </Space>
    </Modal>
  )
}

export default ConflictModal
