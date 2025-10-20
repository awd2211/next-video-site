/**
 * Performance Monitoring Utilities
 * Tracks Web Vitals and custom performance metrics
 */

interface PerformanceMetric {
  name: string
  value: number
  rating: 'good' | 'needs-improvement' | 'poor'
  delta?: number
  id?: string
}

/**
 * Send metric to analytics service
 */
const sendToAnalytics = (metric: PerformanceMetric) => {
  const body = JSON.stringify({
    ...metric,
    url: window.location.href,
    userAgent: navigator.userAgent,
    timestamp: new Date().toISOString(),
  })

  if (process.env.NODE_ENV === 'production') {
    // Send to backend analytics service
    fetch('/api/v1/analytics/web-vitals', {
      method: 'POST',
      body,
      headers: { 'Content-Type': 'application/json' },
      keepalive: true, // Ensure request completes even if page is closing
    }).catch((err) => {
      console.error('Failed to send analytics:', err)
    })
  } else {
    console.log('📊 Web Vital:', metric.name, metric.value, metric.rating)
  }
}

/**
 * Initialize Web Vitals monitoring
 * Requires: pnpm add web-vitals
 * Note: web-vitals v5 changed the API from get* to on*
 */
export const initWebVitalsMonitoring = async () => {
  try {
    const { onCLS, onINP, onFCP, onLCP, onTTFB } = await import('web-vitals')

    onCLS(sendToAnalytics)
    onINP(sendToAnalytics) // FID was replaced by INP in v5
    onFCP(sendToAnalytics)
    onLCP(sendToAnalytics)
    onTTFB(sendToAnalytics)
  } catch (error) {
    console.warn('Web Vitals library not installed. Run: pnpm add web-vitals')
  }
}

/**
 * Measure page load time
 */
export const measurePageLoad = () => {
  if (typeof window === 'undefined' || !('performance' in window)) {
    return
  }

  window.addEventListener('load', () => {
    // Use Performance Navigation Timing API (modern)
    const perfData = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming

    if (perfData) {
      const metrics = {
        // Page Load Time
        pageLoadTime: perfData.loadEventEnd - perfData.fetchStart,
        
        // DNS Lookup
        dnsTime: perfData.domainLookupEnd - perfData.domainLookupStart,
        
        // TCP Connection
        tcpTime: perfData.connectEnd - perfData.connectStart,
        
        // Request Time
        requestTime: perfData.responseEnd - perfData.requestStart,
        
        // Response Time
        responseTime: perfData.responseEnd - perfData.responseStart,
        
        // DOM Processing
        domProcessing: perfData.domComplete - perfData.domInteractive,
        
        // DOM Content Loaded
        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
      }

      console.log('📈 Page Performance Metrics:', metrics)

      // Send to analytics
      if (process.env.NODE_ENV === 'production') {
        fetch('/api/v1/analytics/page-performance', {
          method: 'POST',
          body: JSON.stringify(metrics),
          headers: { 'Content-Type': 'application/json' },
        }).catch(console.error)
      }
    }
  })
}

/**
 * Measure API call duration
 */
export const measureApiCall = async <T,>(
  name: string,
  apiCall: () => Promise<T>
): Promise<T> => {
  const start = performance.now()

  try {
    const result = await apiCall()
    const duration = performance.now() - start

    console.log(`⏱️ API Call [${name}]: ${duration.toFixed(2)}ms`)

    // Send to analytics if slow
    if (duration > 1000 && process.env.NODE_ENV === 'production') {
      sendToAnalytics({
        name: `api-${name}`,
        value: duration,
        rating: duration > 3000 ? 'poor' : duration > 1000 ? 'needs-improvement' : 'good',
      })
    }

    return result
  } catch (error) {
    const duration = performance.now() - start
    console.error(`❌ API Call Failed [${name}]: ${duration.toFixed(2)}ms`, error)
    throw error
  }
}

/**
 * Measure component render time
 */
export const measureComponentRender = (componentName: string) => {
  const start = performance.now()

  return () => {
    const duration = performance.now() - start
    if (duration > 16) {
      // Slower than 60fps (16.67ms)
      console.warn(`⚠️ Slow Render [${componentName}]: ${duration.toFixed(2)}ms`)
    }
  }
}

/**
 * Memory usage monitoring
 */
export const monitorMemoryUsage = () => {
  if (!('memory' in performance)) {
    console.warn('Memory API not available in this browser')
    return
  }

  const checkMemory = () => {
    const memory = (performance as any).memory
    const usedMB = (memory.usedJSHeapSize / 1048576).toFixed(2)
    const totalMB = (memory.totalJSHeapSize / 1048576).toFixed(2)
    const limitMB = (memory.jsHeapSizeLimit / 1048576).toFixed(2)

    console.log(`💾 Memory: ${usedMB}MB / ${totalMB}MB (Limit: ${limitMB}MB)`)

    // Warn if approaching limit
    if (memory.usedJSHeapSize / memory.jsHeapSizeLimit > 0.9) {
      console.warn('⚠️ Memory usage high! Consider optimizing.')
    }
  }

  // Check every 30 seconds in development
  if (process.env.NODE_ENV === 'development') {
    setInterval(checkMemory, 30000)
  }
}

/**
 * Initialize all performance monitoring
 */
export const initPerformanceMonitoring = () => {
  if (typeof window === 'undefined') return

  // Web Vitals
  initWebVitalsMonitoring()

  // Page Load
  measurePageLoad()

  // Memory (development only)
  if (process.env.NODE_ENV === 'development') {
    monitorMemoryUsage()
  }
}

export default {
  initWebVitalsMonitoring,
  measurePageLoad,
  measureApiCall,
  measureComponentRender,
  monitorMemoryUsage,
  initPerformanceMonitoring,
}

