'use client'
import { useState } from 'react'
import { Book, Menu, User, LogOut, Settings } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'

interface SessionHeaderProps {
  sessionId: string | null
  showSources: boolean
  onToggleSources: () => void
  userName?: string
}

export const SessionHeader = ({ 
  sessionId, 
  showSources, 
  onToggleSources, 
  userName 
}: SessionHeaderProps) => {
  const { signOut, user } = useAuth()
  const [showUserMenu, setShowUserMenu] = useState(false)

  const handleSignOut = async () => {
    try {
      await signOut()
    } catch (error) {
      console.error('Error signing out:', error)
    }
    setShowUserMenu(false)
  }

  return (
    <div className="bg-white/95 backdrop-blur-sm shadow-soft border-b border-primary-200">
      <div className="conversation-container">
        <div className="flex items-center justify-between py-4">
          {/* Left: Session Info */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-full bg-therapeutic-100 flex items-center justify-center">
                <span className="text-therapeutic-600 font-semibold text-sm">J</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-primary-900">Jung AI Analysis</h1>
                <p className="text-sm text-primary-600">
                  {sessionId ? `Session ${sessionId.slice(-8)}` : 'Initializing session...'}
                </p>
              </div>
            </div>
          </div>

          {/* Right: Controls */}
          <div className="flex items-center space-x-3">
            {/* Sources Toggle */}
            <button
              onClick={onToggleSources}
              className={`btn-secondary ${showSources ? 'bg-primary-100 text-primary-700' : ''}`}
            >
              <Book size={16} className="mr-2" />
              {showSources ? 'Hide Sources' : 'Show Sources'}
            </button>

            {/* User Menu */}
            {user ? (
              <div className="relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center space-x-2 btn-secondary"
                >
                  <User size={16} />
                  <span className="hidden sm:inline">
                    {userName || user.email}
                  </span>
                </button>

                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-therapeutic border border-primary-200 py-1 z-50">
                    <div className="px-3 py-2 border-b border-primary-100">
                      <p className="text-sm font-medium text-primary-900">{userName || 'User'}</p>
                      <p className="text-xs text-primary-600">{user.email}</p>
                    </div>
                    
                    <button
                      onClick={() => setShowUserMenu(false)}
                      className="w-full text-left px-3 py-2 text-sm text-primary-700 hover:bg-primary-50 flex items-center space-x-2"
                    >
                      <Settings size={16} />
                      <span>Settings</span>
                    </button>
                    
                    <button
                      onClick={handleSignOut}
                      className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2"
                    >
                      <LogOut size={16} />
                      <span>Sign Out</span>
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <button className="btn-secondary">
                  <User size={16} className="mr-2" />
                  Sign In
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
} 