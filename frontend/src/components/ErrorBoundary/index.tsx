import { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

/**
 * Global Error Boundary Component
 * Catches React errors and prevents the entire app from crashing
 */
class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorInfo: null,
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console (or error reporting service)
    console.error('ErrorBoundary caught an error:', error, errorInfo)

    this.setState({
      error,
      errorInfo,
    })

    // TODO: Send error to error tracking service (e.g., Sentry)
    // Example: Sentry.captureException(error, { extra: errorInfo })
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
  }

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback
      }

      // Default fallback UI
      return (
        <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center px-4">
          <div className="max-w-2xl w-full bg-gray-800 rounded-lg p-8 shadow-xl">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 bg-red-600 rounded-full flex items-center justify-center">
                <svg
                  className="w-8 h-8"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-3xl font-bold">出错了</h1>
                <p className="text-gray-400 mt-1">应用程序遇到了一个错误</p>
              </div>
            </div>

            {this.state.error && (
              <div className="mb-6">
                <h2 className="text-lg font-semibold mb-2 text-red-400">错误详情:</h2>
                <div className="bg-gray-900 rounded p-4 overflow-x-auto">
                  <code className="text-sm text-gray-300">
                    {this.state.error.toString()}
                  </code>
                </div>
              </div>
            )}

            {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
              <details className="mb-6">
                <summary className="cursor-pointer text-gray-400 hover:text-white mb-2">
                  Stack Trace (开发模式)
                </summary>
                <div className="bg-gray-900 rounded p-4 overflow-x-auto">
                  <pre className="text-xs text-gray-400">
                    {this.state.errorInfo.componentStack}
                  </pre>
                </div>
              </details>
            )}

            <div className="flex gap-4">
              <button
                onClick={this.handleReset}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
              >
                重试
              </button>
              <button
                onClick={() => window.location.href = '/'}
                className="flex-1 bg-gray-700 hover:bg-gray-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
              >
                返回首页
              </button>
            </div>

            <div className="mt-6 text-center text-sm text-gray-500">
              <p>如果问题持续存在，请联系技术支持</p>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
