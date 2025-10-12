import React, { useState } from 'react'
import { Modal, Button, Tooltip } from 'antd'
import { QuestionCircleOutlined } from '@ant-design/icons'

const KeyboardHelp: React.FC = () => {
  const [visible, setVisible] = useState(false)

  const shortcuts = [
    { keys: 'Ctrl + A', description: '全选当前页所有文件' },
    { keys: 'Delete', description: '删除选中的文件' },
    { keys: 'Esc', description: '取消选中' },
    { keys: '双击文件夹', description: '进入文件夹' },
    { keys: '双击文件', description: '预览文件' },
    { keys: 'Ctrl + 点击', description: '多选文件' },
    { keys: '右键菜单', description: '更多操作' },
  ]

  return (
    <>
      <Tooltip title="键盘快捷键">
        <Button
          type="text"
          icon={<QuestionCircleOutlined />}
          onClick={() => setVisible(true)}
          style={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            zIndex: 100,
            width: 48,
            height: 48,
            borderRadius: '50%',
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
            background: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 20,
          }}
        />
      </Tooltip>

      <Modal
        title="键盘快捷键"
        open={visible}
        onCancel={() => setVisible(false)}
        footer={null}
        width={500}
      >
        <div style={{ padding: '8px 0' }}>
          {shortcuts.map((shortcut, index) => (
            <div
              key={index}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '12px 0',
                borderBottom: index < shortcuts.length - 1 ? '1px solid #f0f0f0' : 'none',
              }}
            >
              <span style={{ color: '#595959' }}>{shortcut.description}</span>
              <kbd
                style={{
                  padding: '4px 12px',
                  background: '#f5f5f5',
                  border: '1px solid #d9d9d9',
                  borderRadius: 4,
                  fontFamily: 'monospace',
                  fontSize: 13,
                  color: '#262626',
                  boxShadow: '0 2px 0 rgba(0,0,0,0.05)',
                }}
              >
                {shortcut.keys}
              </kbd>
            </div>
          ))}
        </div>

        <div style={{ marginTop: 24, padding: 16, background: '#e6f7ff', borderRadius: 8 }}>
          <p style={{ margin: 0, color: '#0050b3', fontSize: 14 }}>
            💡 提示：在输入框中时快捷键会被禁用，以免干扰正常输入。
          </p>
        </div>
      </Modal>
    </>
  )
}

export default KeyboardHelp
