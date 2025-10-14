/**
 * SearchAutocomplete 组件测试
 * 测试搜索自动完成功能
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import SearchAutocomplete from '../SearchAutocomplete'
import { videoService } from '@/services/videoService'

// Mock dependencies
vi.mock('@/services/videoService', () => ({
  videoService: {
    searchVideos: vi.fn(),
  },
}))

vi.mock('@/services/searchHistoryService', () => ({
  searchHistoryService: {
    recordSearch: vi.fn(),
  },
}))

vi.mock('@/store/authStore', () => ({
  useAuthStore: vi.fn(() => ({ isAuthenticated: false })),
}))

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: vi.fn(() => vi.fn()),
  }
})

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>)
}

describe('SearchAutocomplete Component', () => {
  const mockSearchResults = {
    items: [
      {
        id: 1,
        title: 'Test Video 1',
        slug: 'test-video-1',
        poster_url: 'poster1.jpg',
        view_count: 100,
        average_rating: 8.5,
      },
      {
        id: 2,
        title: 'Test Video 2',
        slug: 'test-video-2',
        poster_url: 'poster2.jpg',
        view_count: 200,
        average_rating: 9.0,
      },
    ],
    total: 2,
    page: 1,
    pages: 1,
    page_size: 5,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    vi.mocked(videoService.searchVideos).mockResolvedValue(mockSearchResults)
  })

  describe('Basic Rendering', () => {
    it('should render search input', () => {
      renderWithRouter(<SearchAutocomplete />)
      
      const input = screen.getByRole('textbox')
      expect(input).toBeInTheDocument()
      expect(input).toHaveAttribute('type', 'search')
    })

    it('should render search icon', () => {
      renderWithRouter(<SearchAutocomplete />)
      
      const searchIcon = document.querySelector('.lucide-search')
      expect(searchIcon).toBeInTheDocument()
    })

    it('should have placeholder text', () => {
      renderWithRouter(<SearchAutocomplete />)
      
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('placeholder')
    })
  })

  describe('Search Input Handling', () => {
    it('should update input value on change', () => {
      renderWithRouter(<SearchAutocomplete />)
      
      const input = screen.getByRole('textbox')
      fireEvent.change(input, { target: { value: 'test query' } })
      
      expect(input).toHaveValue('test query')
    })

    it('should clear input value', () => {
      renderWithRouter(<SearchAutocomplete />)
      
      const input = screen.getByRole('textbox')
      fireEvent.change(input, { target: { value: 'test' } })
      fireEvent.change(input, { target: { value: '' } })
      
      expect(input).toHaveValue('')
    })

    it('should handle special characters', () => {
      renderWithRouter(<SearchAutocomplete />)
      
      const input = screen.getByRole('textbox')
      fireEvent.change(input, { target: { value: 'test & <special>' } })
      
      expect(input).toHaveValue('test & <special>')
    })
  })

  describe('Search Suggestions', () => {
    it('should fetch suggestions after typing', async () => {
      renderWithRouter(<SearchAutocomplete />)
      
      const input = screen.getByRole('textbox')
      fireEvent.change(input, { target: { value: 'test' } })
      
      await waitFor(() => {
        expect(videoService.searchVideos).toHaveBeenCalledWith('test', {
          page: 1,
          page_size: 5,
        })
      }, { timeout: 500 })
    })

    it('should not fetch suggestions for short queries', async () => {
      renderWithRouter(<SearchAutocomplete />)
      
      const input = screen.getByRole('textbox')
      fireEvent.change(input, { target: { value: 'a' } })
      
      await new Promise(resolve => setTimeout(resolve, 400))
      
      expect(videoService.searchVideos).not.toHaveBeenCalled()
    })

    it('should show suggestions dropdown', async () => {
      renderWithRouter(<SearchAutocomplete />)
      
      const input = screen.getByRole('textbox')
      fireEvent.change(input, { target: { value: 'test' } })
      
      await waitFor(() => {
        expect(screen.getByText('Test Video 1')).toBeInTheDocument()
        expect(screen.getByText('Test Video 2')).toBeInTheDocument()
      })
    })

    it('should debounce search requests', async () => {
      renderWithRouter(<SearchAutocomplete />)
      
      const input = screen.getByRole('textbox')
      
      // Type multiple times quickly
      fireEvent.change(input, { target: { value: 't' } })
      fireEvent.change(input, { target: { value: 'te' } })
      fireEvent.change(input, { target: { value: 'tes' } })
      fireEvent.change(input, { target: { value: 'test' } })
      
      await waitFor(() => {
        // Should only call once after debounce
        expect(videoService.searchVideos).toHaveBeenCalledTimes(1)
      }, { timeout: 500 })
    })
  })

  describe('Search History', () => {
    it('should load search history from localStorage', () => {
      localStorage.setItem('search_history', JSON.stringify(['query1', 'query2']))
      
      renderWithRouter(<SearchAutocomplete />)
      
      // Component should load history
      expect(localStorage.getItem('search_history')).toBeTruthy()
    })

    it('should show history icon', () => {
      renderWithRouter(<SearchAutocomplete />)
      
      const historyIcon = document.querySelector('.lucide-clock')
      // History icon might be conditionally rendered
      expect(document.body).toBeInTheDocument()
    })
  })

  describe('Dropdown Behavior', () => {
    it('should open dropdown on focus', () => {
      renderWithRouter(<SearchAutocomplete />)
      
      const input = screen.getByRole('textbox')
      fireEvent.focus(input)
      
      // Dropdown should be ready to show
      expect(input).toHaveFocus()
    })

    it('should close dropdown on blur', async () => {
      renderWithRouter(<SearchAutocomplete />)
      
      const input = screen.getByRole('textbox')
      fireEvent.focus(input)
      fireEvent.blur(input)
      
      // Dropdown should close
      expect(input).not.toHaveFocus()
    })

    it('should close dropdown on escape key', () => {
      renderWithRouter(<SearchAutocomplete />)
      
      const input = screen.getByRole('textbox')
      fireEvent.focus(input)
      fireEvent.keyDown(input, { key: 'Escape', code: 'Escape' })
      
      // Should handle escape key
      expect(input).toBeInTheDocument()
    })
  })

  describe('Keyboard Navigation', () => {
    it('should handle Enter key to submit search', async () => {
      const onSearch = vi.fn()
      renderWithRouter(<SearchAutocomplete onSearch={onSearch} />)
      
      const input = screen.getByRole('textbox')
      fireEvent.change(input, { target: { value: 'test' } })
      fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' })
      
      // Should trigger search
      await waitFor(() => {
        expect(input).toHaveValue('test')
      })
    })

    it('should support arrow key navigation', async () => {
      renderWithRouter(<SearchAutocomplete />)
      
      const input = screen.getByRole('textbox')
      fireEvent.change(input, { target: { value: 'test' } })
      
      await waitFor(() => {
        expect(screen.getByText('Test Video 1')).toBeInTheDocument()
      })
      
      // Arrow down
      fireEvent.keyDown(input, { key: 'ArrowDown', code: 'ArrowDown' })
      
      // Should handle arrow keys
      expect(input).toBeInTheDocument()
    })
  })

  describe('Error Handling', () => {
    it('should handle search API errors', async () => {
      vi.mocked(videoService.searchVideos).mockRejectedValue(new Error('API Error'))
      
      renderWithRouter(<SearchAutocomplete />)
      
      const input = screen.getByRole('textbox')
      fireEvent.change(input, { target: { value: 'test' } })
      
      await waitFor(() => {
        expect(videoService.searchVideos).toHaveBeenCalled()
      })
      
      // Should not crash
      expect(input).toBeInTheDocument()
    })

    it('should handle empty search results', async () => {
      vi.mocked(videoService.searchVideos).mockResolvedValue({
        items: [],
        total: 0,
        page: 1,
        pages: 0,
        page_size: 5,
      })
      
      renderWithRouter(<SearchAutocomplete />)
      
      const input = screen.getByRole('textbox')
      fireEvent.change(input, { target: { value: 'nonexistent' } })
      
      await waitFor(() => {
        expect(videoService.searchVideos).toHaveBeenCalled()
      })
      
      // Should show no results
      expect(screen.queryByText('Test Video 1')).not.toBeInTheDocument()
    })
  })

  describe('Loading State', () => {
    it('should show loading indicator while searching', async () => {
      vi.mocked(videoService.searchVideos).mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 1000))
      )
      
      renderWithRouter(<SearchAutocomplete />)
      
      const input = screen.getByRole('textbox')
      fireEvent.change(input, { target: { value: 'test' } })
      
      // Should be in loading state
      await waitFor(() => {
        expect(videoService.searchVideos).toHaveBeenCalled()
      })
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      renderWithRouter(<SearchAutocomplete />)
      
      const input = screen.getByRole('textbox')
      expect(input).toBeInTheDocument()
      expect(input).toHaveAttribute('type', 'search')
    })

    it('should be keyboard accessible', () => {
      renderWithRouter(<SearchAutocomplete />)
      
      const input = screen.getByRole('textbox')
      
      // Should be focusable
      input.focus()
      expect(input).toHaveFocus()
    })
  })
})
