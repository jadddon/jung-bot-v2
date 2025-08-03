'use client'
import { AlertCircle, RefreshCw } from 'lucide-react'

interface ErrorMessageProps {
  message: string
  onRetry?: () => void
}

export const ErrorMessage = ({ message, onRetry }: ErrorMessageProps) => {
  return (
    <div className="max-w-2xl mx-auto animate-slide-up">
      <div className="bg-red-50 border border-red-200 rounded-xl p-4 shadow-soft">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0 w-6 h-6 rounded-full bg-red-100 flex items-center justify-center">
            <AlertCircle size={16} className="text-red-600" />
          </div>
          
          <div className="flex-1">
            <h3 className="text-sm font-medium text-red-800 mb-1">
              Connection Error
            </h3>
            <p className="text-sm text-red-700 leading-relaxed">
              {message}
            </p>
            
            {onRetry && (
              <button
                onClick={onRetry}
                className="mt-3 inline-flex items-center space-x-2 px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors duration-200"
              >
                <RefreshCw size={14} />
                <span>Try Again</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
} 