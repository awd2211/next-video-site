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

