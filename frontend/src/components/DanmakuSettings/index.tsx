/**
 * 弹幕设置面板
 */
import React from 'react'
import './styles.css'

export interface DanmakuConfig {
  enabled: boolean
  opacity: number
  speed: number
  fontSize: number
  density: number
}

interface DanmakuSettingsProps {
  config: DanmakuConfig
  onChange: (config: DanmakuConfig) => void
  onClose: () => void
}

const DanmakuSettings: React.FC<DanmakuSettingsProps> = ({
  config,
  onChange,
  onClose,
}) => {
  const handleChange = (key: keyof DanmakuConfig, value: any) => {
    onChange({ ...config, [key]: value })
  }

  return (
    <div className="danmaku-settings-overlay" onClick={onClose}>
      <div
        className="danmaku-settings-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="settings-header">
          <h3>弹幕设置</h3>
          <button className="btn-close" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="settings-body">
          {/* 开关 */}
          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={config.enabled}
                onChange={(e) => handleChange('enabled', e.target.checked)}
              />
              <span>显示弹幕</span>
            </label>
          </div>

          {/* 不透明度 */}
          <div className="setting-item">
            <div className="setting-label">
              <span>不透明度</span>
              <span className="setting-value">{Math.round(config.opacity * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={config.opacity}
              onChange={(e) => handleChange('opacity', parseFloat(e.target.value))}
              className="slider"
            />
          </div>

          {/* 速度 */}
          <div className="setting-item">
            <div className="setting-label">
              <span>速度</span>
              <span className="setting-value">{config.speed.toFixed(1)}x</span>
            </div>
            <input
              type="range"
              min="0.5"
              max="2"
              step="0.1"
              value={config.speed}
              onChange={(e) => handleChange('speed', parseFloat(e.target.value))}
              className="slider"
            />
          </div>

          {/* 字号 */}
          <div className="setting-item">
            <div className="setting-label">
              <span>字号</span>
              <span className="setting-value">{config.fontSize.toFixed(1)}x</span>
            </div>
            <input
              type="range"
              min="0.5"
              max="2"
              step="0.1"
              value={config.fontSize}
              onChange={(e) => handleChange('fontSize', parseFloat(e.target.value))}
              className="slider"
            />
          </div>

          {/* 密度 */}
          <div className="setting-item">
            <div className="setting-label">
              <span>密度</span>
              <span className="setting-value">
                {config.density === 0
                  ? '无'
                  : config.density < 0.5
                  ? '稀疏'
                  : config.density < 0.8
                  ? '普通'
                  : '密集'}
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={config.density}
              onChange={(e) => handleChange('density', parseFloat(e.target.value))}
              className="slider"
            />
          </div>

          {/* 重置按钮 */}
          <button
            className="btn-reset"
            onClick={() =>
              onChange({
                enabled: true,
                opacity: 0.8,
                speed: 1,
                fontSize: 1,
                density: 0.6,
              })
            }
          >
            恢复默认设置
          </button>
        </div>
      </div>
    </div>
  )
}

export default DanmakuSettings
