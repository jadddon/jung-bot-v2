'use client'
import { formatDistanceToNow } from 'date-fns'
import { User, Bot, AlertCircle } from 'lucide-react'

interface JungSource {
  chunk_id: string
  source: string
  concepts: string[]
  quality: number
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  sources?: JungSource[]
  error?: string
}

interface MessageBubbleProps {
  message: Message
}

export const MessageBubble = ({ message }: MessageBubbleProps) => {
  const isUser = message.role === 'user'
  const isError = !!message.error
  
  const formatTime = (timestamp: string) => {
    try {
      return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
    } catch {
      return 'Just now'
    }
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-message-in`}>
      <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'} gap-3`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
          isUser 
            ? 'bg-accent-100 text-accent-600' 
            : isError 
              ? 'bg-red-100 text-red-600'
              : 'bg-therapeutic-100 text-therapeutic-600'
        }`}>
          {isUser ? (
            <User size={20} />
          ) : isError ? (
            <AlertCircle size={20} />
          ) : (
            <Bot size={20} />
          )}
        </div>

        {/* Message Content */}
        <div className={`message-bubble ${
          isUser 
            ? 'message-user' 
            : isError
              ? 'bg-red-50 text-red-900 border border-red-200'
              : 'message-assistant'
        }`}>
          {/* Message Text */}
          <div className="prose prose-sm max-w-none">
            {message.content.split('\n').map((line, index) => (
              <p key={index} className="mb-2 last:mb-0">
                {line}
              </p>
            ))}
          </div>

          {/* Sources Preview */}
          {message.sources && message.sources.length > 0 && (
            <div className="mt-4 pt-3 border-t border-therapeutic-200">
              <p className="text-xs text-therapeutic-600 font-medium mb-2">
                Referenced from Jung's works:
              </p>
              <div className="flex flex-wrap gap-1">
                {message.sources.slice(0, 3).map((source, index) => (
                  <span
                    key={index}
                    className="inline-block px-2 py-1 text-xs bg-therapeutic-100 text-therapeutic-700 rounded-md"
                  >
                    {source.source}
                  </span>
                ))}
                {message.sources.length > 3 && (
                  <span className="inline-block px-2 py-1 text-xs bg-therapeutic-100 text-therapeutic-700 rounded-md">
                    +{message.sources.length - 3} more
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Timestamp */}
          <div className={`mt-2 text-xs ${
            isUser ? 'text-accent-600' : 'text-therapeutic-600'
          }`}>
            {formatTime(message.timestamp)}
          </div>
        </div>
      </div>
    </div>
  )
} 