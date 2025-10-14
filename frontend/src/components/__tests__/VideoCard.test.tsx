/**
 * VideoCard 组件测试
 * 测试视频卡片的渲染、样式和交互
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import VideoCard from '../VideoCard/VideoCard'

// Wrapper for Router context
const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>)
}

describe('VideoCard Component', () => {
  const mockVideoBase = {
    id: 1,
    title: 'Test Video Title',
  }

  describe('Basic Rendering', () => {
    it('should render video card with title', () => {
      renderWithRouter(<VideoCard video={mockVideoBase} />)
      
      expect(screen.getByText('Test Video Title')).toBeInTheDocument()
    })

    it('should render as a link to video detail page', () => {
      renderWithRouter(<VideoCard video={mockVideoBase} />)
      
      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('href', '/video/1')
    })

    it('should render with all video information', () => {
      const fullVideo = {
        ...mockVideoBase,
        poster_url: 'https://example.com/poster.jpg',
        duration: 125, // 2分5秒
        view_count: 1234567,
        average_rating: 8.5,
        release_year: 2024,
      }

      renderWithRouter(<VideoCard video={fullVideo} />)
      
      expect(screen.getByText('Test Video Title')).toBeInTheDocument()
      expect(screen.getByText('2:05')).toBeInTheDocument() // 时长
      expect(screen.getByText('8.5')).toBeInTheDocument() // 评分
      expect(screen.getByText('2024')).toBeInTheDocument() // 年份
      expect(screen.getByText('1,234,567 views')).toBeInTheDocument() // 观看数
    })
  })

  describe('Poster Image', () => {
    it('should render poster image when poster_url exists', () => {
      const videoWithPoster = {
        ...mockVideoBase,
        poster_url: 'https://example.com/poster.jpg',
      }

      renderWithRouter(<VideoCard video={videoWithPoster} />)
      
      const poster = screen.getByAlt('Test Video Title')
      expect(poster).toBeInTheDocument()
      expect(poster).toHaveAttribute('src', 'https://example.com/poster.jpg')
    })

    it('should render placeholder icon when no poster_url', () => {
      renderWithRouter(<VideoCard video={mockVideoBase} />)
      
      // 应该有一个 SVG 图标
      const svg = document.querySelector('svg')
      expect(svg).toBeInTheDocument()
      expect(svg?.parentElement).toHaveTextContent('')
    })
  })

  describe('Duration Display', () => {
    it('should format duration correctly - minutes and seconds', () => {
      const video = { ...mockVideoBase, duration: 125 } // 2:05
      renderWithRouter(<VideoCard video={video} />)
      expect(screen.getByText('2:05')).toBeInTheDocument()
    })

    it('should format duration with zero padding', () => {
      const video = { ...mockVideoBase, duration: 62 } // 1:02
      renderWithRouter(<VideoCard video={video} />)
      expect(screen.getByText('1:02')).toBeInTheDocument()
    })

    it('should handle long durations', () => {
      const video = { ...mockVideoBase, duration: 7200 } // 120:00 (2小时)
      renderWithRouter(<VideoCard video={video} />)
      expect(screen.getByText('120:00')).toBeInTheDocument()
    })

    it('should not render duration badge when duration is missing', () => {
      renderWithRouter(<VideoCard video={mockVideoBase} />)
      expect(screen.queryByText(/:/)).not.toBeInTheDocument()
    })

    it('should not render duration badge when duration is 0', () => {
      const video = { ...mockVideoBase, duration: 0 }
      renderWithRouter(<VideoCard video={video} />)
      expect(screen.queryByText(/:/)).not.toBeInTheDocument()
    })
  })

  describe('Rating Display', () => {
    it('should display rating with star icon', () => {
      const video = { ...mockVideoBase, average_rating: 8.7 }
      renderWithRouter(<VideoCard video={video} />)
      
      expect(screen.getByText('8.7')).toBeInTheDocument()
      // 检查星形图标是否存在
      const starIcon = document.querySelector('.fill-yellow-500')
      expect(starIcon).toBeInTheDocument()
    })

    it('should format rating to 1 decimal place', () => {
      const video = { ...mockVideoBase, average_rating: 7.12345 }
      renderWithRouter(<VideoCard video={video} />)
      expect(screen.getByText('7.1')).toBeInTheDocument()
    })

    it('should not display rating when undefined', () => {
      renderWithRouter(<VideoCard video={mockVideoBase} />)
      // 不应该有 0.0 或其他默认评分
      expect(screen.queryByText(/\d\.\d/)).not.toBeInTheDocument()
    })

    it('should display rating of 0', () => {
      const video = { ...mockVideoBase, average_rating: 0 }
      renderWithRouter(<VideoCard video={video} />)
      expect(screen.getByText('0.0')).toBeInTheDocument()
    })

    it('should display perfect rating', () => {
      const video = { ...mockVideoBase, average_rating: 10.0 }
      renderWithRouter(<VideoCard video={video} />)
      expect(screen.getByText('10.0')).toBeInTheDocument()
    })
  })

  describe('View Count Display', () => {
    it('should format view count with commas', () => {
      const video = { ...mockVideoBase, view_count: 1234567 }
      renderWithRouter(<VideoCard video={video} />)
      expect(screen.getByText('1,234,567 views')).toBeInTheDocument()
    })

    it('should display small view counts', () => {
      const video = { ...mockVideoBase, view_count: 42 }
      renderWithRouter(<VideoCard video={video} />)
      expect(screen.getByText('42 views')).toBeInTheDocument()
    })

    it('should display zero views', () => {
      const video = { ...mockVideoBase, view_count: 0 }
      renderWithRouter(<VideoCard video={video} />)
      expect(screen.getByText('0 views')).toBeInTheDocument()
    })

    it('should not display views when undefined', () => {
      renderWithRouter(<VideoCard video={mockVideoBase} />)
      expect(screen.queryByText(/views/)).not.toBeInTheDocument()
    })
  })

  describe('Release Year Display', () => {
    it('should display release year', () => {
      const video = { ...mockVideoBase, release_year: 2024 }
      renderWithRouter(<VideoCard video={video} />)
      expect(screen.getByText('2024')).toBeInTheDocument()
    })

    it('should display old release year', () => {
      const video = { ...mockVideoBase, release_year: 1990 }
      renderWithRouter(<VideoCard video={video} />)
      expect(screen.getByText('1990')).toBeInTheDocument()
    })

    it('should not display year when missing', () => {
      renderWithRouter(<VideoCard video={mockVideoBase} />)
      // 除了 title 之外不应该有其他文本
      expect(screen.queryByText(/^(19|20)\d{2}$/)).not.toBeInTheDocument()
    })
  })

  describe('Styling and CSS Classes', () => {
    it('should have correct wrapper classes', () => {
      const { container } = renderWithRouter(<VideoCard video={mockVideoBase} />)
      
      const link = container.querySelector('a')
      expect(link).toHaveClass('group')
      expect(link).toHaveClass('bg-gray-800')
      expect(link).toHaveClass('rounded-lg')
    })

    it('should have hover effect classes', () => {
      const { container } = renderWithRouter(<VideoCard video={mockVideoBase} />)
      
      const link = container.querySelector('a')
      expect(link).toHaveClass('hover:ring-2')
      expect(link).toHaveClass('hover:ring-blue-500')
    })

    it('should have correct image container aspect ratio', () => {
      const video = { ...mockVideoBase, poster_url: 'test.jpg' }
      const { container } = renderWithRouter(<VideoCard video={video} />)
      
      const imageContainer = container.querySelector('.aspect-video')
      expect(imageContainer).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('should have accessible alt text for poster image', () => {
      const video = { ...mockVideoBase, poster_url: 'test.jpg' }
      renderWithRouter(<VideoCard video={video} />)
      
      const image = screen.getByAlt('Test Video Title')
      expect(image).toBeInTheDocument()
    })

    it('should be keyboard navigable as a link', () => {
      renderWithRouter(<VideoCard video={mockVideoBase} />)
      
      const link = screen.getByRole('link')
      expect(link).toBeInTheDocument()
      expect(link.tagName).toBe('A')
    })

    it('should have meaningful link text through title', () => {
      renderWithRouter(<VideoCard video={mockVideoBase} />)
      
      const link = screen.getByRole('link')
      expect(within(link).getByText('Test Video Title')).toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    it('should handle very long titles', () => {
      const video = {
        ...mockVideoBase,
        title: 'This is a very long video title that should be truncated with ellipsis because it exceeds the maximum number of characters allowed',
      }
      renderWithRouter(<VideoCard video={video} />)
      
      const title = screen.getByText(/This is a very long video title/)
      expect(title).toBeInTheDocument()
      expect(title).toHaveClass('line-clamp-2')
    })

    it('should handle missing all optional fields', () => {
      const minimalVideo = { id: 999, title: 'Minimal Video' }
      renderWithRouter(<VideoCard video={minimalVideo} />)
      
      expect(screen.getByText('Minimal Video')).toBeInTheDocument()
      expect(screen.getByRole('link')).toHaveAttribute('href', '/video/999')
    })

    it('should handle special characters in title', () => {
      const video = { ...mockVideoBase, title: 'Test & Special <Characters> "Quotes"' }
      renderWithRouter(<VideoCard video={video} />)
      
      expect(screen.getByText('Test & Special <Characters> "Quotes"')).toBeInTheDocument()
    })
  })

  describe('Multiple Cards Rendering', () => {
    it('should render multiple cards independently', () => {
      const videos = [
        { id: 1, title: 'Video 1', average_rating: 8.5 },
        { id: 2, title: 'Video 2', average_rating: 7.2 },
        { id: 3, title: 'Video 3', average_rating: 9.1 },
      ]

      const { container } = render(
        <BrowserRouter>
          <div>
            {videos.map((video) => (
              <VideoCard key={video.id} video={video} />
            ))}
          </div>
        </BrowserRouter>
      )

      expect(screen.getByText('Video 1')).toBeInTheDocument()
      expect(screen.getByText('Video 2')).toBeInTheDocument()
      expect(screen.getByText('Video 3')).toBeInTheDocument()
      expect(screen.getByText('8.5')).toBeInTheDocument()
      expect(screen.getByText('7.2')).toBeInTheDocument()
      expect(screen.getByText('9.1')).toBeInTheDocument()
    })
  })
})
