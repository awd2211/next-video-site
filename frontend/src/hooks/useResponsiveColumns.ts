/**
 * Responsive Columns Hook
 * Calculates optimal column count based on screen width
 */
import { useState, useEffect } from 'react'

export const useResponsiveColumns = () => {
  const [columns, setColumns] = useState(6)

  useEffect(() => {
    const updateColumns = () => {
      const width = window.innerWidth
      
      if (width < 640) {
        // Mobile
        setColumns(2)
      } else if (width < 768) {
        // Small tablet
        setColumns(3)
      } else if (width < 1024) {
        // Tablet
        setColumns(4)
      } else if (width < 1280) {
        // Small desktop
        setColumns(5)
      } else {
        // Large desktop
        setColumns(6)
      }
    }

    // Initial calculation
    updateColumns()

    // Listen to window resize
    window.addEventListener('resize', updateColumns)
    
    return () => {
      window.removeEventListener('resize', updateColumns)
    }
  }, [])

  return columns
}

export default useResponsiveColumns

