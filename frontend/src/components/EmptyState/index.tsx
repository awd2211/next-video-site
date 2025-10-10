import { Film } from 'lucide-react'

interface EmptyStateProps {
  message?: string
  description?: string
}

const EmptyState: React.FC<EmptyStateProps> = ({
  message = '暂无内容',
  description = '这里还没有任何内容'
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="bg-gray-800 rounded-full p-6 mb-4">
        <Film className="w-12 h-12 text-gray-600" />
      </div>
      <h3 className="text-xl font-semibold text-gray-400 mb-2">{message}</h3>
      <p className="text-gray-500">{description}</p>
    </div>
  )
}

export default EmptyState
