/**
 * OnlineStatus Component
 * Monitors network connectivity and shows toast notifications
 */

import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'

export const OnlineStatus = () => {
  const [wasOffline, setWasOffline] = useState(false)

  useEffect(() => {
    const handleOffline = () => {
      setWasOffline(true)
      toast.error('You are offline. Some features may not be available.', {
        duration: Infinity,
        id: 'offline-toast',
        icon: '📡',
      })
    }

    const handleOnline = () => {
      // Only show "back online" message if user was actually offline
      if (wasOffline) {
        toast.dismiss('offline-toast')
        toast.success('You are back online!', {
          duration: 3000,
          icon: '✓',
        })
        setWasOffline(false)
      }
    }

    // Set initial state
    if (!navigator.onLine) {
      handleOffline()
    }

    // Add event listeners
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    // Cleanup
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [wasOffline])

  // This component doesn't render anything visible
  return null
}

export default OnlineStatus
