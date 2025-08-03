'use client'
import { Bot } from 'lucide-react'

export const TypingIndicator = () => {
  return (
    <div className="flex justify-start animate-message-in">
      <div className="flex max-w-[80%] gap-3">
        {/* Avatar */}
        <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center bg-therapeutic-100 text-therapeutic-600">
          <Bot size={20} />
        </div>

        {/* Typing Animation */}
        <div className="message-bubble message-assistant">
          <div className="flex items-center space-x-2">
            <span className="text-therapeutic-600">Dr. Jung is reflecting</span>
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-therapeutic-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-therapeutic-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-therapeutic-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 