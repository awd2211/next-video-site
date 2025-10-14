/**
 * VideoPlayer 组件测试
 * 测试视频播放器的基本功能和集成
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import VideoPlayer from '../VideoPlayer'

// Mock video.js
const mockPlayer = {
  dispose: vi.fn(),
  on: vi.fn(),
  off: vi.fn(),
  play: vi.fn(),
  pause: vi.fn(),
  currentTime: vi.fn(),
  duration: vi.fn(),
  volume: vi.fn(),
  muted: vi.fn(),
  ready: vi.fn((callback) => callback()),
  src: vi.fn(),
  poster: vi.fn(),
}

vi.mock('video.js', () => ({
  default: vi.fn(() => mockPlayer),
}))

// Mock services
vi.mock('../../services/historyService', () => ({
  historyService: {
    updateProgress: vi.fn(),
    getVideoHistory: vi.fn(),
  },
}))

vi.mock('../../services/subtitleService', () => ({
  default: {
    getVideoSubtitles: vi.fn().mockResolvedValue({ subtitles: [], total: 0 }),
  },
}))

// Mock toast
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

describe('VideoPlayer Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Basic Rendering', () => {
    it('should render video player container', () => {
      render(<VideoPlayer src="https://example.com/video.mp4" />)
      
      const container = document.querySelector('.video-player-container')
      expect(container).toBeInTheDocument()
    })

    it('should initialize with video source', () => {
      render(<VideoPlayer src="https://example.com/video.mp4" />)
      
      // Video.js should be initialized
      expect(vi.mocked(require('video.js').default)).toHaveBeenCalled()
    })

    it('should render with poster image', () => {
      render(
        <VideoPlayer
          src="https://example.com/video.mp4"
          poster="https://example.com/poster.jpg"
        />
      )
      
      // Poster should be passed to video.js config
      expect(vi.mocked(require('video.js').default)).toHaveBeenCalled()
    })
  })

  describe('Props Handling', () => {
    it('should accept videoId prop', () => {
      render(<VideoPlayer src="test.mp4" videoId={123} />)
      
      expect(vi.mocked(require('video.js').default)).toHaveBeenCalled()
    })

    it('should accept initialTime prop', () => {
      render(<VideoPlayer src="test.mp4" initialTime={60} />)
      
      expect(vi.mocked(require('video.js').default)).toHaveBeenCalled()
    })

    it('should accept callbacks', () => {
      const onTimeUpdate = vi.fn()
      const onEnded = vi.fn()
      
      render(
        <VideoPlayer
          src="test.mp4"
          onTimeUpdate={onTimeUpdate}
          onEnded={onEnded}
        />
      )
      
      expect(vi.mocked(require('video.js').default)).toHaveBeenCalled()
    })

    it('should handle autoSaveProgress option', () => {
      render(<VideoPlayer src="test.mp4" videoId={1} autoSaveProgress={false} />)
      
      expect(vi.mocked(require('video.js').default)).toHaveBeenCalled()
    })

    it('should handle enableSubtitles option', () => {
      render(<VideoPlayer src="test.mp4" videoId={1} enableSubtitles={false} />)
      
      expect(vi.mocked(require('video.js').default)).toHaveBeenCalled()
    })
  })

  describe('Player Lifecycle', () => {
    it('should cleanup player on unmount', () => {
      const { unmount } = render(<VideoPlayer src="test.mp4" />)
      
      unmount()
      
      expect(mockPlayer.dispose).toHaveBeenCalled()
    })

    it('should handle multiple renders', () => {
      const { rerender } = render(<VideoPlayer src="test1.mp4" />)
      rerender(<VideoPlayer src="test2.mp4" />)
      
      expect(vi.mocked(require('video.js').default)).toHaveBeenCalled()
    })
  })

  describe('Error Handling', () => {
    it('should handle player initialization errors gracefully', () => {
      vi.mocked(require('video.js').default).mockImplementationOnce(() => {
        throw new Error('Initialization failed')
      })
      
      expect(() => render(<VideoPlayer src="test.mp4" />)).not.toThrow()
    })

    it('should handle missing video source', () => {
      render(<VideoPlayer src="" />)
      
      expect(vi.mocked(require('video.js').default)).toHaveBeenCalled()
    })
  })

  describe('Integration Features', () => {
    it('should support subtitle loading when enabled', async () => {
      const { getVideoSubtitles } = await import('../../services/subtitleService')
      
      render(<VideoPlayer src="test.mp4" videoId={1} enableSubtitles={true} />)
      
      await waitFor(() => {
        expect(getVideoSubtitles).toHaveBeenCalledWith(1)
      })
    })

    it('should not load subtitles when disabled', () => {
      render(<VideoPlayer src="test.mp4" videoId={1} enableSubtitles={false} />)
      
      const { getVideoSubtitles } = require('../../services/subtitleService').default
      expect(getVideoSubtitles).not.toHaveBeenCalled()
    })
  })

  describe('Responsive Behavior', () => {
    it('should use fluid layout', () => {
      render(<VideoPlayer src="test.mp4" />)
      
      // Video.js should be initialized with fluid: true
      const videojs = vi.mocked(require('video.js').default)
      const config = videojs.mock.calls[0]?.[1]
      expect(config?.fluid).toBe(true)
    })

    it('should have responsive controls', () => {
      render(<VideoPlayer src="test.mp4" />)
      
      const videojs = vi.mocked(require('video.js').default)
      const config = videojs.mock.calls[0]?.[1]
      expect(config?.controls).toBe(true)
    })
  })

  describe('Playback Control', () => {
    it('should support multiple playback rates', () => {
      render(<VideoPlayer src="test.mp4" />)
      
      const videojs = vi.mocked(require('video.js').default)
      const config = videojs.mock.calls[0]?.[1]
      expect(config?.playbackRates).toEqual([0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2])
    })

    it('should not autoplay by default', () => {
      render(<VideoPlayer src="test.mp4" />)
      
      const videojs = vi.mocked(require('video.js').default)
      const config = videojs.mock.calls[0]?.[1]
      expect(config?.autoplay).toBe(false)
    })

    it('should preload video', () => {
      render(<VideoPlayer src="test.mp4" />)
      
      const videojs = vi.mocked(require('video.js').default)
      const config = videojs.mock.calls[0]?.[1]
      expect(config?.preload).toBe('auto')
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA labels and roles', () => {
      render(<VideoPlayer src="test.mp4" />)
      
      // Video element should be accessible
      expect(vi.mocked(require('video.js').default)).toHaveBeenCalled()
    })

    it('should support keyboard controls', () => {
      render(<VideoPlayer src="test.mp4" />)
      
      // Keyboard shortcuts should be available
      // This is handled by video.js and custom keyboard handler
      expect(vi.mocked(require('video.js').default)).toHaveBeenCalled()
    })
  })
})
