import React, { useEffect, useState } from 'react'

interface PlaybackRateIndicatorProps {
  rate: number
  show: boolean
}

const PlaybackRateIndicator: React.FC<PlaybackRateIndicatorProps> = ({ rate, show }) => {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (show && rate !== 1) {
      setVisible(true)
      const timer = setTimeout(() => {
        setVisible(false)
      }, 2000)

      return () => clearTimeout(timer)
    } else {
      setVisible(false)
    }
  }, [show, rate])

  if (!visible || rate === 1) return null

  return (
    <div className={`playback-speed-indicator ${visible ? 'active' : ''}`}>
      {rate}x
    </div>
  )
}

export default PlaybackRateIndicator

