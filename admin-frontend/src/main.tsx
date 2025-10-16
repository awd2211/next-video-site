import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ConfigProvider, theme as antdTheme } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import enUS from 'antd/locale/en_US'
import { LanguageProvider, useLanguage } from './contexts/LanguageContext'
import { ThemeProvider, useTheme } from './contexts/ThemeContext'
import { getAWSThemeConfig } from './styles/awsTheme'
import { initializeSentry } from './utils/sentry'
import './i18n/config' // Initialize i18next
import App from './App.tsx'
import './index.css'

// Initialize Sentry
initializeSentry()

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      retry: 1,
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 0,
    },
  },
})

// Wrapper component to access language and theme context
function AppWithProviders() {
  const { language } = useLanguage();
  const { theme } = useTheme();
  const antdLocale = language === 'zh-CN' ? zhCN : enUS;

  const isDark = theme === 'dark';
  
  return (
    <ConfigProvider
      locale={antdLocale}
      theme={{
        algorithm: isDark ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
        ...getAWSThemeConfig(isDark),
      }}
    >
      <App />
    </ConfigProvider>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <QueryClientProvider client={queryClient}>
    <ThemeProvider>
      <LanguageProvider>
        <AppWithProviders />
      </LanguageProvider>
    </ThemeProvider>
  </QueryClientProvider>
)
