/**
 * 弹幕输入框组件
 */
import React, { useState, useRef } from 'react'
import { danmakuService, DanmakuType } from '../../services/danmakuService'
import { sanitizeInput } from '@/utils/security'
import { checkDanmakuRateLimit } from '@/utils/rateLimit'
import { VALIDATION_LIMITS } from '@/utils/validationConfig'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import './styles.css'

interface DanmakuInputProps {
  videoId: number
  currentTime: number
  onSent?: () => void
}

const MAX_DANMAKU_LENGTH = VALIDATION_LIMITS.DANMAKU.max

const COLORS = [
  { name: '白色', value: '#FFFFFF' },
  { name: '红色', value: '#FF0000' },
  { name: '橙色', value: '#FF7F00' },
  { name: '黄色', value: '#FFFF00' },
  { name: '绿色', value: '#00FF00' },
  { name: '青色', value: '#00FFFF' },
  { name: '蓝色', value: '#0000FF' },
  { name: '紫色', value: '#8B00FF' },
  { name: '粉色', value: '#FF69B4' },
]

const FONT_SIZES = [
  { name: '小', value: 18 },
  { name: '中', value: 25 },
  { name: '大', value: 36 },
]

const TYPES: { name: string; value: DanmakuType }[] = [
  { name: '滚动', value: 'scroll' },
  { name: '顶部', value: 'top' },
  { name: '底部', value: 'bottom' },
]

const DanmakuInput: React.FC<DanmakuInputProps> = ({
  videoId,
  currentTime,
  onSent,
}) => {
  const { t } = useTranslation()
  const [content, setContent] = useState('')
  const [color, setColor] = useState('#FFFFFF')
  const [fontSize, setFontSize] = useState(25)
  const [type, setType] = useState<DanmakuType>('scroll')
  const [showSettings, setShowSettings] = useState(false)
  const [loading, setLoading] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleSend = async () => {
    // 检查速率限制
    const rateLimit = checkDanmakuRateLimit()
    if (!rateLimit.allowed) {
      toast.error(t('validation.rateLimitExceeded'))
      return
    }

    // 清理输入
    const cleanedContent = sanitizeInput(content, MAX_DANMAKU_LENGTH)

    if (!cleanedContent) {
      toast.error(t('validation.danmakuEmpty'))
      return
    }

    if (cleanedContent.length > MAX_DANMAKU_LENGTH) {
      toast.error(t('validation.danmakuTooLong', { max: MAX_DANMAKU_LENGTH }))
      return
    }

    try {
      setLoading(true)
      await danmakuService.send({
        video_id: videoId,
        content: cleanedContent,
        time: currentTime,
        type,
        color,
        font_size: fontSize,
      })

      setContent('')
      inputRef.current?.focus()
      toast.success(t('common.success'))
      if (onSent) onSent()
    } catch (error: any) {
      if (error.response?.status === 401) {
        toast.error(t('validation.loginRequired'))
      } else {
        toast.error(error.response?.data?.detail || t('common.failed'))
      }
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="danmaku-input-container">
      <div className="danmaku-input-main">
        <input
          ref={inputRef}
          type="text"
          className="danmaku-input"
          placeholder="发个弹幕呗~"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyPress={handleKeyPress}
          maxLength={MAX_DANMAKU_LENGTH}
          disabled={loading}
        />

        <button
          className="danmaku-settings-btn"
          onClick={() => setShowSettings(!showSettings)}
          title="弹幕设置"
        >
          ⚙️
        </button>

        <button
          className="danmaku-send-btn"
          onClick={handleSend}
          disabled={loading || !content.trim()}
        >
          {loading ? '发送中...' : '发送'}
        </button>
      </div>

      {showSettings && (
        <div className="danmaku-settings-panel">
          {/* 颜色选择 */}
          <div className="setting-group">
            <label>颜色:</label>
            <div className="color-picker">
              {COLORS.map((c) => (
                <div
                  key={c.value}
                  className={`color-option ${color === c.value ? 'active' : ''}`}
                  style={{ backgroundColor: c.value }}
                  onClick={() => setColor(c.value)}
                  title={c.name}
                />
              ))}
            </div>
          </div>

          {/* 字号选择 */}
          <div className="setting-group">
            <label>字号:</label>
            <div className="size-picker">
              {FONT_SIZES.map((s) => (
                <button
                  key={s.value}
                  className={`size-option ${fontSize === s.value ? 'active' : ''}`}
                  onClick={() => setFontSize(s.value)}
                >
                  {s.name}
                </button>
              ))}
            </div>
          </div>

          {/* 类型选择 */}
          <div className="setting-group">
            <label>类型:</label>
            <div className="type-picker">
              {TYPES.map((t) => (
                <button
                  key={t.value}
                  className={`type-option ${type === t.value ? 'active' : ''}`}
                  onClick={() => setType(t.value)}
                >
                  {t.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DanmakuInput
