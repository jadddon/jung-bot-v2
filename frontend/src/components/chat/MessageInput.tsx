'use client'
import { useState, useRef, useEffect } from 'react'
import { Send, Loader2 } from 'lucide-react'

interface MessageInputProps {
  onSend: (message: string) => void
  disabled?: boolean
  placeholder?: string
}

export const MessageInput = ({ 
  onSend, 
  disabled = false, 
  placeholder = "Share your thoughts, dreams, or questions..." 
}: MessageInputProps) => {
  const [message, setMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [message])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!message.trim() || disabled || isSubmitting) return

    const messageToSend = message.trim()
    setMessage('')
    setIsSubmitting(true)

    try {
      await onSend(messageToSend)
    } catch (error) {
      console.error('Error sending message:', error)
      // Restore message if sending failed
      setMessage(messageToSend)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled || isSubmitting}
          className="input-primary resize-none pr-12 min-h-[52px] max-h-32 leading-relaxed"
          rows={1}
        />
        
        {/* Send Button */}
        <button
          type="submit"
          disabled={!message.trim() || disabled || isSubmitting}
          className="absolute right-2 bottom-2 p-2 rounded-lg bg-primary-600 hover:bg-primary-700 disabled:bg-primary-300 disabled:cursor-not-allowed text-white transition-all duration-200 shadow-sm hover:shadow-md"
        >
          {isSubmitting ? (
            <Loader2 size={20} className="animate-spin" />
          ) : (
            <Send size={20} />
          )}
        </button>
      </div>
      
      {/* Helper text */}
      <div className="flex justify-between items-center mt-2 text-xs text-primary-500">
        <span>Press Enter to send, Shift+Enter for new line</span>
        <span className={`transition-opacity duration-200 ${
          message.length > 0 ? 'opacity-100' : 'opacity-0'
        }`}>
          {message.length}/1000
        </span>
      </div>
    </form>
  )
} 