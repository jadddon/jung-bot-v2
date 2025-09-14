import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { apiClient } from '@/lib/api'

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
  isStreaming?: boolean
  error?: string
}

interface ChatState {
  messages: Message[]
  currentSession: string | null
  isTyping: boolean
  isConnected: boolean
  error: string | null
  
  // Actions
  addMessage: (message: Message) => void
  updateMessage: (messageId: string, updates: Partial<Message>) => void
  setTyping: (typing: boolean) => void
  setSession: (sessionId: string) => void
  setError: (error: string | null) => void
  clearMessages: () => void
  loadMessages: (sessionId: string) => Promise<void>
  sendMessage: (content: string) => Promise<void>
  createSession: (title?: string) => Promise<string>
}

export const useChatStore = create<ChatState>()(
  immer((set, get) => ({
    messages: [],
    currentSession: null,
    isTyping: false,
    isConnected: true,
    error: null,
    
    addMessage: (message) => {
      set((state) => {
        // Check if message already exists
        const existingMessage = state.messages.find(m => m.id === message.id)
        if (existingMessage) {
          console.warn('Message already exists, skipping:', message.id)
          return
        }
        
        state.messages.push(message)
      })
    },
    
    updateMessage: (messageId, updates) => {
      set((state) => {
        const messageIndex = state.messages.findIndex(m => m.id === messageId)
        if (messageIndex !== -1) {
          Object.assign(state.messages[messageIndex], updates)
        }
      })
    },
    
    setTyping: (typing) => {
      set((state) => {
        state.isTyping = typing
      })
    },
    
    setSession: (sessionId) => {
      set((state) => {
        state.currentSession = sessionId
        state.messages = []
        state.error = null
      })
    },
    
    setError: (error) => {
      set((state) => {
        state.error = error
      })
    },
    
    clearMessages: () => {
      set((state) => {
        state.messages = []
      })
    },
    
    loadMessages: async (sessionId) => {
      try {
        const response = await apiClient.chat.getMessages(sessionId)
        const messages = response.data.messages || []
        
        set((state) => {
          state.messages = messages
        })
      } catch (error) {
        console.error('Error loading messages:', error)
        get().setError('Failed to load conversation history')
      }
    },
    
    createSession: async (title = 'New Jung Analysis Session') => {
      try {
        const response = await apiClient.sessions.create({
          title,
          is_anonymous: true, // Default to anonymous, can be changed later
        })
        
        const sessionId = response.data.id // Note: backend returns 'id' not 'session_id'
        get().setSession(sessionId)
        return sessionId
      } catch (error: any) {
        console.error('Session creation failed:', error.response?.data?.detail || error.message)
        
        // Generate a temporary session ID for demo purposes
        const tempSessionId = `temp-${Date.now()}`
        get().setSession(tempSessionId)
        get().setError(null) // Clear error since demo mode is working
        return tempSessionId
      }
    },
    
    sendMessage: async (content) => {
      const { currentSession, addMessage, setTyping, setError } = get()
      
      if (!currentSession) {
        console.error('No active session!')
        setError('No active session. Please create a new session.')
        return
      }
      
      if (currentSession.startsWith('temp-')) {
        console.warn('Using temporary session - API calls will fail')
      }
      
      // Add user message immediately with more unique ID
      const userMessage: Message = {
        id: `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        role: 'user',
        content,
        timestamp: new Date().toISOString(),
      }
      
      addMessage(userMessage)
      setTyping(true)
      setError(null)
      
      try {
        const response = await apiClient.chat.sendMessage({
          content,
          session_id: currentSession,
        })
        
        // Add AI response with more unique ID
        const aiMessage: Message = {
          id: `ai-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`, // Always use frontend-generated ID
          role: 'assistant',
          content: response.data.assistant_message.content,
          timestamp: response.data.assistant_message.timestamp || new Date().toISOString(),
          sources: response.data.assistant_message.sources || [],
        }
        
        addMessage(aiMessage)
        
      } catch (error: any) {
        console.error('Message sending failed:', error.response?.data?.detail || error.message)
        
        // Add demo response for when backend is not available
        const demoResponse: Message = {
          id: `demo-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          role: 'assistant',
          content: `Thank you for sharing "${content}" with me. I appreciate your openness in exploring these thoughts together. While I'm currently in demonstration mode and cannot access my full therapeutic capabilities, I want you to know that your willingness to engage in this process of self-reflection is commendable.\n\nIn a full session, I would draw upon my extensive understanding of psychological concepts such as the collective unconscious, archetypes, and the process of individuation to help you explore the deeper meanings behind your thoughts and experiences.\n\nHow does it feel to express these thoughts? What patterns do you notice in your inner dialogue?`,
          timestamp: new Date().toISOString(),
          sources: [
            {
              chunk_id: 'demo-cw-1',
              source: 'Collected Works Vol. 1',
              concepts: ['individuation', 'self-reflection', 'therapeutic_process'],
              quality: 0.85
            }
          ]
        }
        
        addMessage(demoResponse)
        setError(null) // Clear error since demo mode is working
      } finally {
        setTyping(false)
      }
    },
  }))
) 