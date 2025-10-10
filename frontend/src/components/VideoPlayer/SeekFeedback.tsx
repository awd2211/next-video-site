import React, { useEffect, useState } from 'react'
import './SeekFeedback.css'

interface SeekFeedbackProps {
  show: boolean
  direction: 'forward' | 'backward'
  seconds: number
  position: 'left' | 'center' | 'right'
  onAnimationEnd?: () => void
}

const SeekFeedback: React.FC<SeekFeedbackProps> = ({
  show,
  direction,
  seconds,
  position,
  onAnimationEnd,
}) => {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (show) {
      setVisible(true)
      const timer = setTimeout(() => {
        setVisible(false)
        onAnimationEnd?.()
      }, 800)

      return () => clearTimeout(timer)
    }
  }, [show, onAnimationEnd])

  if (!visible && !show) return null

  return (
    <div className={`seek-feedback seek-feedback-${position} ${visible ? 'active' : ''}`}>
      <div className="seek-feedback-content">
        <div className="seek-icon">
          {direction === 'forward' ? (
            // Fast forward icon (双箭头向右)
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M4 18l8.5-6L4 6v12zm9-12v12l8.5-6L13 6z" />
            </svg>
          ) : (
            // Rewind icon (双箭头向左)
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M11 18V6l-8.5 6 8.5 6zm.5-6l8.5 6V6l-8.5 6z" />
            </svg>
          )}
        </div>
        <div className="seek-text">{Math.abs(seconds)} 秒</div>
      </div>
      {/* Ripple effect circles */}
      <div className="seek-ripple seek-ripple-1"></div>
      <div className="seek-ripple seek-ripple-2"></div>
    </div>
  )
}

export default SeekFeedback

