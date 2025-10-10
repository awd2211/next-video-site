import React, { useEffect } from 'react'
import './KeyboardShortcuts.css'

interface KeyboardShortcutsProps {
  visible: boolean
  onClose: () => void
}

const KeyboardShortcuts: React.FC<KeyboardShortcutsProps> = ({ visible, onClose }) => {
  useEffect(() => {
    if (!visible) return

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' || e.key === '?') {
        e.preventDefault()
        onClose()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [visible, onClose])

  if (!visible) return null

  const shortcuts = [
    { category: '播放控制', items: [
      { key: 'Space / K', description: '播放/暂停' },
      { key: 'J', description: '快退 10 秒' },
      { key: 'L', description: '快进 10 秒' },
      { key: '← 左箭头', description: '快退 5 秒' },
      { key: '→ 右箭头', description: '快进 5 秒' },
      { key: '0-9', description: '跳转到视频 0%-90%' },
      { key: ', 逗号', description: '逐帧后退（暂停时）' },
      { key: '. 句号', description: '逐帧前进（暂停时）' },
    ]},
    { category: '音量控制', items: [
      { key: '↑ 上箭头', description: '增加音量' },
      { key: '↓ 下箭头', description: '减少音量' },
      { key: 'M', description: '静音/取消静音' },
      { key: '滚轮', description: '调整音量' },
    ]},
    { category: '播放速度', items: [
      { key: '< Shift + ,', description: '减慢播放速度' },
      { key: '> Shift + .', description: '加快播放速度' },
    ]},
    { category: '显示模式', items: [
      { key: 'F', description: '全屏/退出全屏' },
      { key: 'T', description: '剧场模式' },
      { key: 'I', description: '迷你播放器' },
    ]},
    { category: '字幕与设置', items: [
      { key: 'C', description: '切换字幕显示' },
    ]},
    { category: '双击操作', items: [
      { key: '双击左侧', description: '快退 10 秒' },
      { key: '双击中间', description: '播放/暂停' },
      { key: '双击右侧', description: '快进 10 秒' },
    ]},
    { category: '其他', items: [
      { key: '?', description: '显示/隐藏快捷键列表' },
      { key: 'Esc', description: '关闭菜单或退出全屏' },
      { key: '右键', description: '打开上下文菜单' },
    ]},
  ]

  return (
    <div className="keyboard-shortcuts-overlay" onClick={onClose}>
      <div className="keyboard-shortcuts-panel" onClick={(e) => e.stopPropagation()}>
        <div className="shortcuts-header">
          <h3>键盘快捷键</h3>
          <button className="shortcuts-close" onClick={onClose} aria-label="关闭">
            ×
          </button>
        </div>

        <div className="shortcuts-content">
          {shortcuts.map((section) => (
            <div key={section.category} className="shortcuts-section">
              <h4 className="shortcuts-category">{section.category}</h4>
              <div className="shortcuts-list">
                {section.items.map((item, index) => (
                  <div key={index} className="shortcut-item">
                    <kbd className="shortcut-key">{item.key}</kbd>
                    <span className="shortcut-description">{item.description}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="shortcuts-footer">
          <p className="text-sm text-gray-400">按 <kbd>?</kbd> 或 <kbd>Esc</kbd> 关闭此面板</p>
        </div>
      </div>
    </div>
  )
}

export default KeyboardShortcuts

