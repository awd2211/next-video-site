import { useState, useEffect } from 'react'
import { Sun, Moon } from 'lucide-react'

const ThemeToggle = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark')

  useEffect(() => {
    // 从 localStorage 读取保存的主题
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null
    if (savedTheme) {
      setTheme(savedTheme)
      document.documentElement.classList.toggle('light', savedTheme === 'light')
      document.body.classList.toggle('light', savedTheme === 'light')
    }
  }, [])

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark'
    setTheme(newTheme)
    localStorage.setItem('theme', newTheme)

    // 切换 HTML 和 body 的 light 类
    document.documentElement.classList.toggle('light', newTheme === 'light')
    document.body.classList.toggle('light', newTheme === 'light')
  }

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-lg hover:bg-gray-700 transition-colors"
      aria-label="Toggle theme"
      title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      {theme === 'dark' ? (
        <Sun className="w-5 h-5 text-yellow-400" />
      ) : (
        <Moon className="w-5 h-5 text-gray-700" />
      )}
    </button>
  )
}

export default ThemeToggle
