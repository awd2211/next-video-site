import React, { Component, ErrorInfo, ReactNode } from 'react'
import { Button, Result } from 'antd'
import { ReloadOutlined, HomeOutlined } from '@ant-design/icons'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

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
    return {
      hasError: true,
      error,
      errorInfo: null,
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console in development
    console.error('Error caught by boundary:', error, errorInfo)

    this.setState({
      error,
      errorInfo,
    })

    // TODO: Log error to error reporting service
    // logErrorToService(error, errorInfo)
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
  }

  handleGoHome = () => {
    window.location.href = '/'
  }

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback
      }

      // Default error UI
      return (
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '100vh',
            padding: '24px',
          }}
        >
          <Result
            status="error"
            title="出错了"
            subTitle={
              <div>
                <p>应用程序遇到了一个错误。我们已经记录了这个问题。</p>
                {process.env.NODE_ENV === 'development' && this.state.error && (
                  <details style={{ marginTop: 16, textAlign: 'left' }}>
                    <summary style={{ cursor: 'pointer', color: '#1890ff' }}>
                      查看错误详情
                    </summary>
                    <pre
                      style={{
                        marginTop: 8,
                        padding: 16,
                        background: '#f5f5f5',
                        borderRadius: 4,
                        fontSize: 12,
                        overflow: 'auto',
                        maxHeight: 300,
                      }}
                    >
                      {this.state.error.toString()}
                      {'\n\n'}
                      {this.state.errorInfo?.componentStack}
                    </pre>
                  </details>
                )}
              </div>
            }
            extra={[
              <Button
                key="retry"
                type="primary"
                icon={<ReloadOutlined />}
                onClick={this.handleReset}
              >
                重试
              </Button>,
              <Button
                key="home"
                icon={<HomeOutlined />}
                onClick={this.handleGoHome}
              >
                返回首页
              </Button>,
            ]}
          />
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary

