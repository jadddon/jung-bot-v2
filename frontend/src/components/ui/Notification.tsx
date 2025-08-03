'use client'
import { useEffect, useState } from 'react'
import { CheckCircle, XCircle, Info, AlertCircle, X } from 'lucide-react'

interface NotificationProps {
  message: string
  type: 'success' | 'error' | 'info' | 'warning'
  duration?: number
  onClose: () => void
}

export const Notification = ({ message, type, duration = 5000, onClose }: NotificationProps) => {
  const [isVisible, setIsVisible] = useState(true)
  const [isExiting, setIsExiting] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsExiting(true)
      setTimeout(() => {
        onClose()
      }, 300) // Animation duration
    }, duration)

    return () => clearTimeout(timer)
  }, [duration, onClose])

  const handleClose = () => {
    setIsExiting(true)
    setTimeout(() => {
      onClose()
    }, 300)
  }

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-success-500" />
      case 'error':
        return <XCircle className="w-5 h-5 text-error-500" />
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-warning-500" />
      case 'info':
      default:
        return <Info className="w-5 h-5 text-info-500" />
    }
  }

  const getBackgroundClass = () => {
    switch (type) {
      case 'success':
        return 'bg-success-50 border-success-200'
      case 'error':
        return 'bg-error-50 border-error-200'
      case 'warning':
        return 'bg-warning-50 border-warning-200'
      case 'info':
      default:
        return 'bg-info-50 border-info-200'
    }
  }

  const getTextClass = () => {
    switch (type) {
      case 'success':
        return 'text-success-800'
      case 'error':
        return 'text-error-800'
      case 'warning':
        return 'text-warning-800'
      case 'info':
      default:
        return 'text-info-800'
    }
  }

  if (!isVisible) return null

  return (
    <div className="fixed top-4 right-4 z-50 max-w-sm w-full">
      <div
        className={`
          border rounded-lg shadow-lg transition-all duration-300 ease-in-out
          ${getBackgroundClass()}
          ${isExiting ? 'opacity-0 translate-x-2' : 'opacity-100 translate-x-0'}
        `}
      >
        <div className="flex items-start p-4">
          <div className="flex-shrink-0">
            {getIcon()}
          </div>
          <div className="ml-3 flex-1">
            <p className={`text-sm font-medium ${getTextClass()}`}>
              {message}
            </p>
          </div>
          <div className="ml-4 flex-shrink-0">
            <button
              onClick={handleClose}
              className={`
                inline-flex rounded-md p-1.5 transition-colors
                ${type === 'success' ? 'text-success-500 hover:bg-success-100' : ''}
                ${type === 'error' ? 'text-error-500 hover:bg-error-100' : ''}
                ${type === 'warning' ? 'text-warning-500 hover:bg-warning-100' : ''}
                ${type === 'info' ? 'text-info-500 hover:bg-info-100' : ''}
              `}
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Notification Manager Hook
export const useNotifications = () => {
  const [notifications, setNotifications] = useState<Array<{
    id: string
    message: string
    type: 'success' | 'error' | 'info' | 'warning'
    duration?: number
  }>>([])

  const addNotification = (message: string, type: 'success' | 'error' | 'info' | 'warning', duration?: number) => {
    const id = Date.now().toString()
    setNotifications(prev => [...prev, { id, message, type, duration }])
  }

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  const NotificationContainer = () => (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {notifications.map(notification => (
        <Notification
          key={notification.id}
          message={notification.message}
          type={notification.type}
          duration={notification.duration}
          onClose={() => removeNotification(notification.id)}
        />
      ))}
    </div>
  )

  return {
    addNotification,
    NotificationContainer,
    success: (message: string, duration?: number) => addNotification(message, 'success', duration),
    error: (message: string, duration?: number) => addNotification(message, 'error', duration),
    info: (message: string, duration?: number) => addNotification(message, 'info', duration),
    warning: (message: string, duration?: number) => addNotification(message, 'warning', duration),
  }
} 