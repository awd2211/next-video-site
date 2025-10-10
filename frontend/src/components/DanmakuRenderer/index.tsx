/**
 * 弹幕渲染引擎
 * 使用Canvas绘制弹幕
 */
import React, { useEffect, useRef, useState, useCallback } from 'react'
import { Danmaku } from '../../services/danmakuService'
import './styles.css'

interface DanmakuRendererProps {
  danmakuList: Danmaku[]
  currentTime: number
  isPlaying: boolean
  enabled: boolean
  opacity: number  // 0-1
  speed: number    // 0.5-2
  fontSize: number // 0.5-2 (multiplier)
  density: number  // 0-1 (0=稀疏, 1=密集)
  containerWidth: number
  containerHeight: number
}

interface DanmakuItem extends Danmaku {
  x: number
  y: number
  speed: number
  displayed: boolean
}

const DanmakuRenderer: React.FC<DanmakuRendererProps> = ({
  danmakuList,
  currentTime,
  isPlaying,
  enabled,
  opacity,
  speed,
  fontSize,
  density,
  containerWidth,
  containerHeight,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [activeDanmaku, setActiveDanmaku] = useState<DanmakuItem[]>([])
  const animationRef = useRef<number>()
  const lastTimeRef = useRef<number>(currentTime)

  // 根据密度计算同屏最大弹幕数
  const maxDanmaku = Math.floor(30 * density) || 1

  // 添加弹幕到渲染队列
  const addDanmaku = useCallback((danmaku: Danmaku) => {
    if (!enabled) return

    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // 计算文字宽度
    const actualFontSize = danmaku.font_size * fontSize
    ctx.font = `${actualFontSize}px sans-serif`
    const textWidth = ctx.measureText(danmaku.content).width

    // 根据类型设置初始位置
    let x = containerWidth
    let y = 0

    if (danmaku.type === 'scroll') {
      // 滚动弹幕：从右往左
      x = containerWidth
      y = Math.random() * (containerHeight - actualFontSize) + actualFontSize
    } else if (danmaku.type === 'top') {
      // 顶部弹幕：居中显示
      x = (containerWidth - textWidth) / 2
      y = actualFontSize + Math.random() * 50
    } else if (danmaku.type === 'bottom') {
      // 底部弹幕：居中显示
      x = (containerWidth - textWidth) / 2
      y = containerHeight - actualFontSize - Math.random() * 50
    }

    const item: DanmakuItem = {
      ...danmaku,
      x,
      y,
      speed: danmaku.type === 'scroll' ? (containerWidth + textWidth) / 8 * speed : 0,
      displayed: true,
    }

    setActiveDanmaku((prev) => {
      // 限制同屏弹幕数量
      if (prev.length >= maxDanmaku) {
        return [...prev.slice(1), item]
      }
      return [...prev, item]
    })
  }, [enabled, fontSize, speed, containerWidth, containerHeight, maxDanmaku])

  // 检查并添加新弹幕
  useEffect(() => {
    if (!isPlaying || !enabled) return

    const timeDiff = Math.abs(currentTime - lastTimeRef.current)

    // 时间跳跃时清空弹幕
    if (timeDiff > 1) {
      setActiveDanmaku([])
    }

    lastTimeRef.current = currentTime

    // 查找当前时间点的弹幕 (±0.5秒)
    const newDanmaku = danmakuList.filter(
      (d) =>
        d.time >= currentTime - 0.1 &&
        d.time <= currentTime + 0.1 &&
        !activeDanmaku.some((active) => active.id === d.id)
    )

    newDanmaku.forEach(addDanmaku)
  }, [currentTime, danmakuList, isPlaying, enabled, activeDanmaku, addDanmaku])

  // 渲染弹幕动画
  useEffect(() => {
    if (!enabled || !isPlaying) {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
      return
    }

    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const render = () => {
      // 清空画布
      ctx.clearRect(0, 0, containerWidth, containerHeight)
      ctx.globalAlpha = opacity

      // 更新和绘制弹幕
      setActiveDanmaku((prev) => {
        return prev.filter((item) => {
          const actualFontSize = item.font_size * fontSize

          // 绘制弹幕
          ctx.font = `${actualFontSize}px sans-serif`
          ctx.fillStyle = item.color
          ctx.strokeStyle = '#000'
          ctx.lineWidth = 2

          // 描边文字
          ctx.strokeText(item.content, item.x, item.y)
          // 填充文字
          ctx.fillText(item.content, item.x, item.y)

          // 更新位置 (仅滚动弹幕)
          if (item.type === 'scroll') {
            item.x -= item.speed
            // 移出屏幕则移除
            return item.x > -ctx.measureText(item.content).width
          } else {
            // 固定弹幕：显示3秒后移除
            return Date.now() - new Date(item.created_at).getTime() < 3000
          }
        })
      })

      animationRef.current = requestAnimationFrame(render)
    }

    animationRef.current = requestAnimationFrame(render)

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [enabled, isPlaying, containerWidth, containerHeight, opacity, fontSize, speed])

  // 暂停时停止动画
  useEffect(() => {
    if (!isPlaying && animationRef.current) {
      cancelAnimationFrame(animationRef.current)
    }
  }, [isPlaying])

  if (!enabled) return null

  return (
    <canvas
      ref={canvasRef}
      className="danmaku-canvas"
      width={containerWidth}
      height={containerHeight}
    />
  )
}

export default DanmakuRenderer
