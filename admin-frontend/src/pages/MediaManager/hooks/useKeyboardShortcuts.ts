import { useEffect } from 'react'

interface KeyboardShortcutsOptions {
  onSelectAll: () => void
  onDelete: () => void
  onEscape: () => void
  enabled?: boolean
}

export function useKeyboardShortcuts({
  onSelectAll,
  onDelete,
  onEscape,
  enabled = true,
}: KeyboardShortcutsOptions) {
  useEffect(() => {
    if (!enabled) return

    const handleKeyDown = (event: KeyboardEvent) => {
      // 忽略在输入框、文本域等元素中的按键
      const target = event.target as HTMLElement
      const tagName = target.tagName.toLowerCase()
      if (tagName === 'input' || tagName === 'textarea' || target.isContentEditable) {
        return
      }

      // Ctrl+A / Cmd+A - 全选
      if ((event.ctrlKey || event.metaKey) && event.key === 'a') {
        event.preventDefault()
        onSelectAll()
      }

      // Delete / Backspace - 删除选中项
      if (event.key === 'Delete' || (event.key === 'Backspace' && event.metaKey)) {
        event.preventDefault()
        onDelete()
      }

      // Esc - 取消选中
      if (event.key === 'Escape') {
        event.preventDefault()
        onEscape()
      }
    }

    window.addEventListener('keydown', handleKeyDown)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [onSelectAll, onDelete, onEscape, enabled])
}
