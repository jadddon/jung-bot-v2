import axios from 'axios'
import { supabase } from './supabase'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (session?.access_token) {
        config.headers.Authorization = `Bearer ${session.access_token}`
      }
    } catch (error) {
      console.error('Error getting session in API interceptor:', error)
      // Don't fail the request if we can't get the session - just proceed without auth
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized errors
      await supabase.auth.signOut()
      window.location.href = '/auth/login'
    }
    return Promise.reject(error)
  }
)

export default api

// Typed API functions
export const apiClient = {
  // Session endpoints
  sessions: {
    create: (data: { title: string; is_anonymous?: boolean }) =>
      api.post('/sessions', data),
    
    get: (sessionId: string) =>
      api.get(`/sessions/${sessionId}`),
    
    list: () =>
      api.get('/sessions'),
    
    update: (sessionId: string, data: { title?: string; is_anonymous?: boolean }) =>
      api.put(`/sessions/${sessionId}`, data),
    
    delete: (sessionId: string) =>
      api.delete(`/sessions/${sessionId}`),
  },
  
  // Chat endpoints
  chat: {
    sendMessage: (data: { content: string; session_id: string }) =>
      api.post('/chat/message', data),
    
    getMessages: (sessionId: string) =>
      api.get(`/chat/sessions/${sessionId}/messages`),
  },
  
  // Auth endpoints
  auth: {
    register: (data: { email: string; password: string; preferred_name?: string }) =>
      api.post('/auth/register', data),
    
    login: (data: { email: string; password: string }) =>
      api.post('/auth/login', data),
  },
  
  // Health check
  health: () => api.get('/health'),
} 