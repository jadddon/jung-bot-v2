'use client'
import { useState, useEffect, useRef } from 'react'
import { Send, Plus } from 'lucide-react'
import { useChatStore } from '@/stores/chatStore'
import { useNotifications } from '@/components/ui/Notification'

export const ChatInterface = () => {
  const [inputValue, setInputValue] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  
  const { 
    messages, 
    isTyping, 
    currentSession, 
    error, 
    sendMessage, 
    createSession, 
  } = useChatStore()

  const { NotificationContainer, error: showError } = useNotifications()

  // Initialize session on component mount
  useEffect(() => {
    const initializeSession = async () => {
      try {
        if (!currentSession) {
          await createSession()
        }
      } catch (error) {
        console.error('Error initializing session:', error)
        showError('Failed to initialize session')
      }
    }

    initializeSession()
  }, [currentSession, createSession, showError])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [inputValue])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim() || isTyping) return

    const messageContent = inputValue.trim()
    setInputValue('')
    
    try {
      await sendMessage(messageContent)
    } catch (error) {
      showError('Failed to send message. Please try again.')
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleNewSession = async () => {
    try {
      await createSession('New Jung Analysis Session')
    } catch (error) {
      console.error('Error creating new session:', error)
      showError('Failed to create new session. Please try again.')
    }
  }

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="simple-header text-center py-4">
        <div className="flex items-center justify-center gap-3">
          <img 
            src="/Carl-Jung.jpeg" 
            alt="Carl Jung" 
            className="w-12 h-12 rounded-full object-cover flex-shrink-0 border border-primary-200 shadow-sm"
            style={{ width: '48px', height: '48px' }}
          />
          <h1 className="text-2xl font-bold text-primary-900">JungBot</h1>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <h2 className="welcome-message .welcome-title">
              Welcome to JungBot
            </h2>
            <p className="welcome-message .welcome-subtitle">
              Please use this Carl Jung chat bot that is enhanced by Retrieval-Augmented Generation which includes Jung's full body of work. You can use this to mimic a formal Jungian session or use it to find and cite relevant sources with page numbers.
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.role === 'user' ? 'message-user' : 'message-assistant'}`}
            >
              <div className="message-content">
                {message.content}
              </div>
            </div>
          ))
        )}

        {/* Typing indicator */}
        {isTyping && (
          <div className="message message-assistant">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="error-message">
            <p>⚠️ {error}</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="chat-input-container">
        <form onSubmit={handleSubmit} className="chat-input-wrapper">
          <textarea
            ref={textareaRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Share your thoughts, dreams, or questions..."
            className="chat-input"
            rows={1}
            disabled={isTyping}
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isTyping}
            className="chat-send-button"
          >
            <Send size={20} />
          </button>
        </form>
      </div>

      {/* Notifications */}
      <NotificationContainer />
    </div>
  )
} 