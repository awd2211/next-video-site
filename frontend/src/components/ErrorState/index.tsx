import { AlertCircle, RefreshCw } from 'lucide-react'

interface ErrorStateProps {
  message?: string
  onRetry?: () => void
}

const ErrorState: React.FC<ErrorStateProps> = ({
  message = '加载失败',
  onRetry
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="bg-red-900/20 rounded-full p-6 mb-4">
        <AlertCircle className="w-12 h-12 text-red-500" />
      </div>
      <h3 className="text-xl font-semibold text-red-500 mb-2">出错了</h3>
      <p className="text-gray-400 mb-6">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center space-x-2 bg-red-600 hover:bg-red-700 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
        >
          <RefreshCw className="w-5 h-5" />
          <span>重试</span>
        </button>
      )}
    </div>
  )
}

export default ErrorState
