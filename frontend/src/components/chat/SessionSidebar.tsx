'use client'
import { useState, useEffect } from 'react'
import { MessageCircle, Search, Plus, Trash2, Edit2, Clock, Calendar, Filter, X } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { apiClient } from '@/lib/api'
import { useChatStore } from '@/stores/chatStore'

interface Session {
  id: string
  title: string
  created_at: string
  updated_at: string
  last_activity: string
  message_count: number
  context_summary?: string
}

interface SessionSidebarProps {
  isOpen: boolean
  onClose: () => void
  onSessionSelect: (sessionId: string) => void
}

export const SessionSidebar = ({ isOpen, onClose, onSessionSelect }: SessionSidebarProps) => {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState<'recent' | 'oldest' | 'alphabetical'>('recent')
  const [filterPeriod, setFilterPeriod] = useState<'all' | 'today' | 'week' | 'month'>('all')
  const [editingSession, setEditingSession] = useState<string | null>(null)
  const [newTitle, setNewTitle] = useState('')
  const [error, setError] = useState('')

  const { user } = useAuth()
  const { currentSession, createSession } = useChatStore()

  // Load user sessions
  useEffect(() => {
    if (user && isOpen) {
      loadSessions()
    }
  }, [user, isOpen])

  const loadSessions = async () => {
    try {
      setLoading(true)
      const response = await apiClient.sessions.list()
      setSessions(response.data.sessions || [])
    } catch (error) {
      console.error('Error loading sessions:', error)
      setError('Failed to load sessions')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateSession = async () => {
    try {
      const sessionId = await createSession('New Jung Analysis Session')
      onSessionSelect(sessionId)
      onClose()
    } catch (error) {
      console.error('Error creating session:', error)
      setError('Failed to create session')
    }
  }

  const handleDeleteSession = async (sessionId: string) => {
    if (!confirm('Are you sure you want to delete this session? This action cannot be undone.')) {
      return
    }

    try {
      await apiClient.sessions.delete(sessionId)
      setSessions(sessions.filter(s => s.id !== sessionId))
    } catch (error) {
      console.error('Error deleting session:', error)
      setError('Failed to delete session')
    }
  }

  const handleEditSession = async (sessionId: string) => {
    if (!newTitle.trim()) return

    try {
      await apiClient.sessions.update(sessionId, { title: newTitle })
      setSessions(sessions.map(s => 
        s.id === sessionId ? { ...s, title: newTitle } : s
      ))
      setEditingSession(null)
      setNewTitle('')
    } catch (error) {
      console.error('Error updating session:', error)
      setError('Failed to update session')
    }
  }

  const startEdit = (session: Session) => {
    setEditingSession(session.id)
    setNewTitle(session.title)
  }

  const cancelEdit = () => {
    setEditingSession(null)
    setNewTitle('')
  }

  // Filter and sort sessions
  const filteredSessions = sessions
    .filter(session => {
      // Search filter
      const matchesSearch = session.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           session.context_summary?.toLowerCase().includes(searchTerm.toLowerCase())
      
      // Date filter
      const now = new Date()
      const sessionDate = new Date(session.last_activity)
      let matchesDate = true
      
      switch (filterPeriod) {
        case 'today':
          matchesDate = sessionDate.toDateString() === now.toDateString()
          break
        case 'week':
          const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
          matchesDate = sessionDate >= weekAgo
          break
        case 'month':
          const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
          matchesDate = sessionDate >= monthAgo
          break
      }
      
      return matchesSearch && matchesDate
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'recent':
          return new Date(b.last_activity).getTime() - new Date(a.last_activity).getTime()
        case 'oldest':
          return new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        case 'alphabetical':
          return a.title.localeCompare(b.title)
        default:
          return 0
      }
    })

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffMinutes = Math.floor(diffMs / (1000 * 60))

    if (diffMinutes < 60) {
      return `${diffMinutes}m ago`
    } else if (diffHours < 24) {
      return `${diffHours}h ago`
    } else if (diffDays < 7) {
      return `${diffDays}d ago`
    } else {
      return date.toLocaleDateString()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex z-50">
      <div className="bg-white w-80 shadow-2xl flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-primary-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-primary-900">Session History</h2>
            <button
              onClick={onClose}
              className="text-primary-400 hover:text-primary-600 transition-colors"
            >
              <X size={20} />
            </button>
          </div>

          {/* Search */}
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary-400" size={16} />
            <input
              type="text"
              placeholder="Search sessions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-3 py-2 border border-primary-300 rounded-lg focus:ring-2 focus:ring-therapeutic-500 focus:border-transparent text-sm"
            />
          </div>

          {/* Filters */}
          <div className="flex gap-2 mb-4">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
              className="flex-1 px-3 py-2 border border-primary-300 rounded-lg focus:ring-2 focus:ring-therapeutic-500 focus:border-transparent text-sm"
            >
              <option value="recent">Most Recent</option>
              <option value="oldest">Oldest</option>
              <option value="alphabetical">A-Z</option>
            </select>
            <select
              value={filterPeriod}
              onChange={(e) => setFilterPeriod(e.target.value as typeof filterPeriod)}
              className="flex-1 px-3 py-2 border border-primary-300 rounded-lg focus:ring-2 focus:ring-therapeutic-500 focus:border-transparent text-sm"
            >
              <option value="all">All Time</option>
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
            </select>
          </div>

          {/* New Session Button */}
          <button
            onClick={handleCreateSession}
            className="w-full flex items-center justify-center gap-2 py-2 px-4 bg-gradient-to-r from-therapeutic-600 to-therapeutic-700 hover:from-therapeutic-700 hover:to-therapeutic-800 text-white font-medium rounded-lg transition-all duration-200"
          >
            <Plus size={16} />
            New Session
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-3 bg-error-50 border-b border-error-200">
            <p className="text-error-700 text-sm">{error}</p>
          </div>
        )}

        {/* Sessions List */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-therapeutic-600"></div>
            </div>
          ) : filteredSessions.length === 0 ? (
            <div className="text-center py-8 px-4">
              <MessageCircle className="mx-auto h-12 w-12 text-primary-300 mb-4" />
              <p className="text-primary-600 text-sm">
                {searchTerm ? 'No sessions match your search' : 'No sessions yet'}
              </p>
              <p className="text-primary-400 text-xs mt-1">
                {searchTerm ? 'Try adjusting your search terms' : 'Start a new conversation to create your first session'}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-primary-100">
              {filteredSessions.map((session) => (
                <div key={session.id} className="p-4 hover:bg-primary-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      {editingSession === session.id ? (
                        <div className="flex items-center gap-2 mb-2">
                          <input
                            type="text"
                            value={newTitle}
                            onChange={(e) => setNewTitle(e.target.value)}
                            className="flex-1 px-2 py-1 border border-primary-300 rounded text-sm"
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') handleEditSession(session.id)
                              if (e.key === 'Escape') cancelEdit()
                            }}
                            autoFocus
                          />
                          <button
                            onClick={() => handleEditSession(session.id)}
                            className="text-therapeutic-600 hover:text-therapeutic-700"
                          >
                            ✓
                          </button>
                          <button
                            onClick={cancelEdit}
                            className="text-primary-400 hover:text-primary-600"
                          >
                            ✕
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => {
                            onSessionSelect(session.id)
                            onClose()
                          }}
                          className="text-left w-full group"
                        >
                          <h3 className="font-medium text-primary-900 group-hover:text-therapeutic-600 transition-colors truncate">
                            {session.title}
                          </h3>
                        </button>
                      )}

                      <div className="flex items-center gap-4 text-xs text-primary-500 mt-1">
                        <div className="flex items-center gap-1">
                          <Clock size={12} />
                          {formatDate(session.last_activity)}
                        </div>
                        <div className="flex items-center gap-1">
                          <MessageCircle size={12} />
                          {session.message_count} messages
                        </div>
                      </div>

                      {session.context_summary && (
                        <p className="text-xs text-primary-600 mt-2 line-clamp-2">
                          {session.context_summary}
                        </p>
                      )}
                    </div>

                    <div className="flex items-center gap-1 ml-2">
                      <button
                        onClick={() => startEdit(session)}
                        className="text-primary-400 hover:text-primary-600 transition-colors"
                      >
                        <Edit2 size={14} />
                      </button>
                      <button
                        onClick={() => handleDeleteSession(session.id)}
                        className="text-primary-400 hover:text-red-600 transition-colors"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>

                  {currentSession === session.id && (
                    <div className="mt-2 px-2 py-1 bg-therapeutic-100 rounded-lg">
                      <p className="text-xs text-therapeutic-700 font-medium">Current Session</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Backdrop */}
      <div className="flex-1" onClick={onClose} />
    </div>
  )
} 