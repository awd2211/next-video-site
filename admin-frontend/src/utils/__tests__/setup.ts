/**
 * Vitest setup file (Admin Frontend)
 */

import { expect, afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'
import '@testing-library/jest-dom'

// Cleanup after each test
afterEach(() => {
  cleanup()
})

// Mock DOMPurify for tests
global.DOMPurify = {
  sanitize: (dirty: string, config?: any) => {
    // Simple mock implementation
    const allowedTags = config?.ALLOWED_TAGS || []
    if (allowedTags.length === 0) {
      // Remove all HTML tags
      return dirty.replace(/<[^>]*>/g, '')
    }
    // For tests, just return the input
    return dirty
  },
} as any

// Mock window.matchMedia for Ant Design Grid and responsive components
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {}, // deprecated
    removeListener: () => {}, // deprecated
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => true,
  }),
})

// Mock window.getComputedStyle for Ant Design components
Object.defineProperty(window, 'getComputedStyle', {
  writable: true,
  value: () => ({
    getPropertyValue: () => '',
    display: 'none',
    paddingLeft: '0',
    paddingRight: '0',
    paddingTop: '0',
    paddingBottom: '0',
    marginLeft: '0',
    marginRight: '0',
    marginTop: '0',
    marginBottom: '0',
    overflow: 'visible',
  }),
})

