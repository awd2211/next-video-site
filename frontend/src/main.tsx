import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App.tsx'
import './index.css'
import { handleApiError, shouldRetry } from './utils/apiErrorHandler'
import { initPerformanceMonitoring } from './utils/performance'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: (failureCount, error: any) => shouldRetry(error, failureCount),
      staleTime: 5 * 60 * 1000, // 5分钟内数据视为新鲜
      cacheTime: 10 * 60 * 1000, // 缓存保留10分钟
      refetchOnMount: false, // 避免重复获取
      refetchInterval: false, // 禁用轮询
      onError: (error) => {
        // Global error handler for queries
        const errorMessage = handleApiError(error as any)
        console.error('Query Error:', errorMessage)
      },
    },
    mutations: {
      retry: false, // Mutations don't retry by default
      onError: (error) => {
        // Global error handler for mutations
        const errorMessage = handleApiError(error as any)
        console.error('Mutation Error:', errorMessage)
      },
    },
  },
})

// Initialize performance monitoring
initPerformanceMonitoring()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
)
