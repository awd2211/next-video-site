import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { HelmetProvider } from 'react-helmet-async'
import App from './App.tsx'
import './index.css'
import { shouldRetry } from './utils/apiErrorHandler'
import { initPerformanceMonitoring } from './utils/performance'
import './i18n/config'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: (failureCount, error: any) => shouldRetry(error, failureCount),
      staleTime: 5 * 60 * 1000, // 5分钟内数据视为新鲜
      gcTime: 10 * 60 * 1000, // 缓存保留10分钟 (React Query v5: cacheTime renamed to gcTime)
      refetchOnMount: false, // 避免重复获取
      refetchInterval: false, // 禁用轮询
    },
    mutations: {
      retry: false, // Mutations don't retry by default
    },
  },
})

// Initialize performance monitoring
initPerformanceMonitoring()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <HelmetProvider>
      <QueryClientProvider client={queryClient}>
        <App />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#1f2937',
              color: '#fff',
              borderRadius: '8px',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.5)',
            },
            success: {
              iconTheme: {
                primary: '#10b981',
                secondary: '#fff',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </QueryClientProvider>
    </HelmetProvider>
  </React.StrictMode>,
)
